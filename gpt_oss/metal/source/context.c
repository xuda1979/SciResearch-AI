#include <assert.h>
#include <float.h>
#include <inttypes.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#include <gpt-oss.h>

#include "internal/datatype.h"
#include "internal/model.h"
#include "internal/metal.h"
#include "internal/metal-kernels.h"
#include "internal/log.h"
#include "internal/rng.h"


enum gptoss_status GPTOSS_ABI gptoss_context_create(
    gptoss_model_t model,
    size_t context_length,
    gptoss_context_t* context_out)
{
    *context_out = NULL;

    enum gptoss_status status = gptoss_status_success;
    struct gptoss_context* context = NULL;

    if (context_length == 0) {
        context_length = model->context_length;
    } else if (context_length > model->context_length) {
        GPTOSS_LOG_ERROR("requested context length %zu exceeds model context length %" PRIu32,
            context_length, model->context_length);
        status = gptoss_status_invalid_argument;
        goto cleanup;
    }

    context = malloc(sizeof(struct gptoss_context));
    if (context == NULL) {
        GPTOSS_LOG_ERROR("failed to allocate %zu bytes for Context object",
            sizeof(struct gptoss_context));
        status = gptoss_status_insufficient_memory;
        goto cleanup;
    }
    memset(context, 0, sizeof(struct gptoss_context));

    atomic_store_explicit(&context->ref_count, 1, memory_order_relaxed);
    context->max_tokens = context_length;

    status = gptoss_metal_buffer_create(&model->device, context_length * sizeof(uint32_t), NULL, &context->token_buffer);
    if (status != gptoss_status_success) {
        goto cleanup;
    }
    status = gptoss_metal_buffer_create(&model->device, model->max_batch_tokens * model->vocabulary_size * sizeof(float), NULL, &context->score_buffer);
    if (status != gptoss_status_success) {
        goto cleanup;
    }
    status = gptoss_metal_buffer_create(&model->device, model->max_batch_tokens * model->vocabulary_size * sizeof(float), NULL, &context->prob_buffer);
    if (status != gptoss_status_success) {
        goto cleanup;
    }
    status = gptoss_metal_buffer_create(&model->device, model->max_batch_tokens * model->max_threadgroups * sizeof(float), NULL, &context->sum_buffer);
    if (status != gptoss_status_success) {
        goto cleanup;
    }
    status = gptoss_metal_buffer_create(&model->device, model->max_batch_tokens * sizeof(uint64_t), NULL, &context->argmax_buffer);
    if (status != gptoss_status_success) {
        goto cleanup;
    }
    status = gptoss_metal_buffer_create(&model->device, model->num_blocks * context_length * 2 * model->num_kv_heads * model->head_dim * sizeof(float), NULL, &context->kvcache_buffer);
    if (status != gptoss_status_success) {
        goto cleanup;
    }

    context->kvcache_size = context->kvcache_buffer.size;
    context->allocation_size = context->token_buffer.size + context->kvcache_buffer.size + context->score_buffer.size + context->argmax_buffer.size;

    context->model = model;
    gptoss_model_retain(model);
    *context_out = context;
    context = NULL;

cleanup:
    gptoss_context_release(context);
    return status;
}

enum gptoss_status GPTOSS_ABI gptoss_context_get_num_tokens(
    gptoss_context_t context,
    size_t* num_tokens_out)
{
    *num_tokens_out = context->num_tokens;
    return gptoss_status_success;
}

enum gptoss_status GPTOSS_ABI gptoss_context_get_max_tokens(
    gptoss_context_t context,
    size_t* max_tokens_out)
{
    *max_tokens_out = context->max_tokens;
    return gptoss_status_success;
}

enum gptoss_status GPTOSS_ABI gptoss_context_get_tokens(
    gptoss_context_t context,
    uint32_t* tokens_out,
    size_t max_tokens,
    size_t* num_tokens_out)
{
    *num_tokens_out = context->num_tokens;
    if (max_tokens < context->num_tokens) {
        return gptoss_status_insufficient_memory;
    }

    if (context->num_tokens != 0) {
        memcpy(tokens_out, context->token_buffer.ptr, context->num_tokens * sizeof(uint32_t));
    }
    return gptoss_status_success;
}

static enum gptoss_status process_batch(
    gptoss_context_t context)
{
    enum gptoss_status status = gptoss_status_success;
    const struct gptoss_model* model = context->model;
    struct gptoss_metal_command_buffer command_buffer = {0};

    const size_t attn_qkv_dim = model->head_dim * (model->num_heads + 2 * model->num_kv_heads);

    status = gptoss_metal_command_buffer_create(&model->command_queue, &command_buffer);
    if (status != gptoss_status_success) {
        goto cleanup;
    }
    status = gptoss_metal_command_buffer_encode_launch_bf16_f32_embeddings(
        &command_buffer,
        &model->bf16_f32_embeddings_fn,
        /*threadgroup_size=*/512,
        &context->token_buffer,
        (context->num_tokens - context->num_batch_tokens) * sizeof(uint32_t),
        &model->shared_weight_buffer,
        /*weight_offset=*/0,
        &model->residual_activation_buffer,
        /*output_offset=*/0,
        /*num_tokens=*/context->num_batch_tokens,
        /*num_channels=*/model->embedding_dim);
    if (status != gptoss_status_success) {
        GPTOSS_LOG_ERROR("failed to encode bf16_f32_embeddings kernel launch");
        goto cleanup;
    }
    for (uint32_t n = 0; n < model->num_blocks; n++) {
        const bool last_block = n + 1 == model->num_blocks;
        const size_t num_output_tokens = last_block ? 1 : context->num_batch_tokens;

        status = gptoss_metal_command_buffer_encode_launch_f32_bf16w_rmsnorm(
            &command_buffer,
            &model->f32_bf16w_rmsnorm_fn,
            &model->residual_activation_buffer,
            /*input_offset=*/0,
            &model->shared_weight_buffer,
            /*weight_offset=*/model->attn_rmsnorm_gain_offset + model->per_block_shared_weights_size * n,
            &model->rmsnorm_activation_buffer,
            /*output_offset=*/0,
            /*num_tokens=*/context->num_batch_tokens,
            /*num_channels=*/model->embedding_dim,
            model->rmsnorm_epsilon);
        if (status != gptoss_status_success) {
            GPTOSS_LOG_ERROR("failed to encode f32_bf16w_rmsnorm kernel launch");
            goto cleanup;
        }
        status = gptoss_metal_command_buffer_encode_launch_f32_bf16w_matmul(
            &command_buffer,
            &model->f32_bf16w_matmul_fn,
            /*threadgroup_size=*/256,
            &model->rmsnorm_activation_buffer,
            /*input_offset=*/0,
            &model->shared_weight_buffer,
            /*weight_offset=*/model->attn_qkv_weight_offset + model->per_block_shared_weights_size * n,
            &model->shared_weight_buffer,
            /*bias_offset=*/model->attn_qkv_bias_offset + model->per_block_shared_weights_size * n,
            &model->qkv_activation_buffer,
            /*output_offset=*/0,
            /*num_tokens=*/context->num_batch_tokens,
            /*num_cols=*/model->embedding_dim,
            /*num_rows=*/attn_qkv_dim);
        if (status != gptoss_status_success) {
            GPTOSS_LOG_ERROR("failed to encode f32_bf16w_matmul kernel launch");
            goto cleanup;
        }

        status = gptoss_metal_command_buffer_encode_launch_f32_rope(
            &command_buffer,
            &model->f32_rope_fn,
            /*threadgroup_size=*/32,
            &model->qkv_activation_buffer,
            model->rope_theta,
            model->interpolation_scale,
            model->yarn_offset,
            model->yarn_scale,
            model->yarn_multiplier,
            context->num_batch_tokens,
            model->num_heads,
            model->num_kv_heads,
            model->head_dim,
            /*token_offset=*/context->num_kv_tokens);
        if (status != gptoss_status_success) {
            GPTOSS_LOG_ERROR("failed to encode f32_rope kernel launch");
            goto cleanup;
        }
        for (uint32_t t = 0; t < context->num_batch_tokens; t++) {
            status = gptoss_metal_command_buffer_encode_copy_buffer(
                &command_buffer,
                &model->qkv_activation_buffer,
                /*input_offset=*/(t * attn_qkv_dim + model->num_heads * model->head_dim) * sizeof(float),
                &context->kvcache_buffer,
                /*output_offset=*/(n * context->max_tokens + context->num_kv_tokens + t) * 2 * model->num_kv_heads * model->head_dim * sizeof(float),
                /*size=*/2 * model->num_kv_heads * model->head_dim * sizeof(float));
            if (status != gptoss_status_success) {
                GPTOSS_LOG_ERROR("failed to encode copy of token %" PRIu32 " to KV cache", t);
                goto cleanup;
            }
        }

        status = gptoss_metal_command_buffer_encode_launch_f32_sdpa(
            &command_buffer,
            &model->f32_sdpa_q8_d64_fn,
            &model->qkv_activation_buffer,
            /*q_offset=*/attn_qkv_dim * (context->num_batch_tokens - num_output_tokens) * sizeof(float),
            &context->kvcache_buffer,
            /*k_offset=*/n * context->max_tokens * 2 * model->num_kv_heads * model->head_dim * sizeof(float),
            &context->kvcache_buffer,
            /*v_offset=*/(n * context->max_tokens * 2 + 1) * model->num_kv_heads * model->head_dim * sizeof(float),
            &model->shared_weight_buffer,
            /*s_offset=*/model->attn_sdpa_sink_offset + model->per_block_shared_weights_size * n,
            &model->sdpa_activation_buffer, /*output_offset=*/0,
            /*window=*/n % 2 == 0 ? model->attention_window : UINT32_MAX,
            num_output_tokens, context->num_kv_tokens + (context->num_batch_tokens - num_output_tokens),
            model->num_heads, model->num_kv_heads, model->head_dim);
        if (status != gptoss_status_success) {
            GPTOSS_LOG_ERROR("failed to encode f32_sdpa kernel launch");
            goto cleanup;
        }
        status = gptoss_metal_command_buffer_encode_launch_f32_bf16w_matmul_add(
            &command_buffer,
            &model->f32_bf16w_matmul_fn,
            /*threadgroup_size=*/256,
            &model->sdpa_activation_buffer,
            /*input_offset=*/0,
            &model->shared_weight_buffer,
            /*weight_offset=*/model->attn_out_weight_offset + model->per_block_shared_weights_size * n,
            &model->shared_weight_buffer,
            /*bias_offset=*/model->attn_out_bias_offset + model->per_block_shared_weights_size * n,
            &model->residual_activation_buffer,
            /*output_offset=*/model->embedding_dim * (context->num_batch_tokens - num_output_tokens) * sizeof(float),
            /*num_tokens=*/num_output_tokens,
            /*num_cols=*/model->num_heads * model->head_dim,
            /*num_rows=*/model->embedding_dim);
        if (status != gptoss_status_success) {
            GPTOSS_LOG_ERROR("failed to encode f32_bf16w_matmul_add kernel launch");
            goto cleanup;
        }

        status = gptoss_metal_command_buffer_encode_launch_f32_bf16w_rmsnorm(
            &command_buffer,
            &model->f32_bf16w_rmsnorm_fn,
            &model->residual_activation_buffer,
            /*input_offset=*/model->embedding_dim * (context->num_batch_tokens - num_output_tokens) * sizeof(float),
            &model->shared_weight_buffer,
            /*weight_offset=*/model->mlp_rmsnorm_gain_offset + model->per_block_shared_weights_size * n,
            &model->rmsnorm_activation_buffer,
            /*output_offset=*/0,
            num_output_tokens,
            model->embedding_dim,
            model->rmsnorm_epsilon);
        if (status != gptoss_status_success) {
            GPTOSS_LOG_ERROR("failed to encode f32_bf16w_rmsnorm kernel launch");
            goto cleanup;
        }

        status = gptoss_metal_command_buffer_encode_launch_f32_bf16w_matmul(
            &command_buffer,
            &model->f32_bf16w_matmul_fn,
            /*threadgroup_size=*/256,
            &model->rmsnorm_activation_buffer,
            /*input_offset=*/0,
            &model->shared_weight_buffer,
            /*weight_offset=*/model->mlp_gate_weight_offset + model->per_block_shared_weights_size * n,
            &model->shared_weight_buffer,
            /*bias_offset=*/model->mlp_gate_bias_offset + model->per_block_shared_weights_size * n,
            &model->gate_activation_buffer,
            /*output_offset=*/0,
            /*num_tokens=*/num_output_tokens,
            /*num_cols=*/model->embedding_dim,
            /*num_rows=*/model->num_experts);
        if (status != gptoss_status_success) {
            GPTOSS_LOG_ERROR("failed to encode f32_bf16w_matmul kernel launch");
            goto cleanup;
        }

        const char* kernel_name = NULL;
        switch (model->num_experts) {
            case 32:
                kernel_name = "f32_topk_softmax_e32_k4_fn";
                status = gptoss_metal_command_buffer_encode_launch_f32_topk(
                    &command_buffer,
                    &model->f32_topk_softmax_e32_k4_fn,
                    &model->gate_activation_buffer, /*input_offset=*/0,
                    &model->expert_activation_buffer, /*output_offset=*/0,
                    num_output_tokens,
                    model->num_experts,
                    model->num_active_experts);
                break;
            case 128:
                kernel_name = "f32_topk_softmax_e128_k4_fn";
                status = gptoss_metal_command_buffer_encode_launch_f32_topk(
                    &command_buffer,
                    &model->f32_topk_softmax_e128_k4_fn,
                    &model->gate_activation_buffer, /*input_offset=*/0,
                    &model->expert_activation_buffer, /*output_offset=*/0,
                    num_output_tokens,
                    model->num_experts,
                    model->num_active_experts);
                break;
            default:
                status = gptoss_status_unsupported_argument;
                GPTOSS_LOG_ERROR("missing Top-K kernel for %" PRIu32 " experts", model->num_experts);
                goto cleanup;
        }
        if (status != gptoss_status_success) {
            GPTOSS_LOG_ERROR("failed to encode %s kernel launch", kernel_name);
            goto cleanup;
        }

        status = gptoss_metal_command_buffer_encode_launch_f32_mf4w_moe_matmul_swiglu(
            &command_buffer,
            &model->f32_mf4w_moe_matmul_swiglu_fn,
            /*threadgroup_size=*/512,
            &model->rmsnorm_activation_buffer, /*input_offset=*/0,
            &model->expert_activation_buffer, /*expert_offset=*/0,
            &model->block_weight_buffers[n], /*weight_block_offset=*/0,
            &model->block_weight_buffers[n], /*weight_scale_offset=*/model->mlp_swiglu_scale_offset,
            &model->block_weight_buffers[n], /*bias_offset=*/model->mlp_swiglu_bias_offset,
            &model->swiglu_activation_buffer, /*output_offset=*/0,
            model->swiglu_limit,
            model->per_expert_block_weight_size,
            num_output_tokens,
            model->num_active_experts,
            model->embedding_dim,
            model->mlp_dim);
        if (status != gptoss_status_success) {
            GPTOSS_LOG_ERROR("failed to encode f32_mf4w_moe_matmul_swiglu kernel launch");
            goto cleanup;
        }

        status = gptoss_metal_command_buffer_encode_launch_f32_mf4w_moe_matmul(
            &command_buffer,
            &model->f32_mf4w_moe_matmul_fn,
            /*threadgroup_size=*/512,
            &model->swiglu_activation_buffer, /*input_offset=*/0,
            &model->expert_activation_buffer, /*expert_offset=*/0,
            &model->block_weight_buffers[n], /*weight_block_offset=*/model->mlp_out_block_offset,
            &model->block_weight_buffers[n], /*weight_scale_offset=*/model->mlp_out_scale_offset,
            &model->block_weight_buffers[n], /*bias_offset=*/model->mlp_out_bias_offset,
            &model->moe_activation_buffer, /*output_offset=*/0,
            model->per_expert_block_weight_size,
            num_output_tokens,
            model->num_active_experts,
            model->mlp_dim,
            model->embedding_dim);
        if (status != gptoss_status_success) {
            GPTOSS_LOG_ERROR("failed to encode f32_mf4w_moe_matmul kernel launch");
            goto cleanup;
        }

        status = gptoss_metal_command_buffer_encode_launch_f32_accumulate(
            &command_buffer,
            &model->f32_accumulate_e4_fn,
            /*threadgroup_size=*/256,
            model->max_threadgroups,
            &model->moe_activation_buffer,
            /*input_offset=*/0,
            &model->expert_activation_buffer,
            /*expert_offset=*/0,
            &model->residual_activation_buffer,
            /*output_offset=*/model->embedding_dim * (context->num_batch_tokens - num_output_tokens) * sizeof(float),
            model->embedding_dim,
            num_output_tokens,
            model->num_active_experts);
        if (status != gptoss_status_success) {
            GPTOSS_LOG_ERROR("failed to encode f32_accumulate kernel launch");
            goto cleanup;
        }
    }

    const size_t num_output_tokens = 1;
    status = gptoss_metal_command_buffer_encode_launch_f32_bf16w_rmsnorm(
        &command_buffer,
        &model->f32_bf16w_rmsnorm_fn,
        &model->residual_activation_buffer,
        /*input_offset=*/model->embedding_dim * (context->num_batch_tokens - num_output_tokens) * sizeof(float),
        &model->shared_weight_buffer,
        /*weight_offset=*/model->rmsnorm_weight_offset,
        &model->rmsnorm_activation_buffer,
        /*output_offset=*/0,
        /*num_tokens=*/num_output_tokens,
        /*num_channels=*/model->embedding_dim,
        model->rmsnorm_epsilon);
    if (status != gptoss_status_success) {
        GPTOSS_LOG_ERROR("failed to encode f32_bf16w_rmsnorm kernel launch");
        goto cleanup;
    }

    status = gptoss_metal_command_buffer_encode_fill_buffer(
        &command_buffer,
        &context->argmax_buffer,
        /*offset=*/0,
        /*size=*/sizeof(uint64_t) * num_output_tokens,
        /*fill_value=*/0xFF);
    if (status != gptoss_status_success) {
        GPTOSS_LOG_ERROR("failed to encode fill buffer command");
        goto cleanup;
    }
    status = gptoss_metal_command_buffer_encode_launch_f32_bf16w_unembedding(
        &command_buffer,
        &model->f32_bf16w_unembedding_fn,
        /*threadgroup_size=*/256,
        model->max_threadgroups,
        &model->rmsnorm_activation_buffer,
        /*input_offset=*/0,
        &model->shared_weight_buffer,
        /*weight_offset=*/model->unembedding_weight_offset,
        &context->score_buffer,
        /*output_offset=*/0,
        &context->argmax_buffer,
        /*argmax_offset=*/0,
        /*num_tokens=*/num_output_tokens,
        /*num_cols=*/model->embedding_dim,
        /*num_rows=*/model->vocabulary_size);
    if (status != gptoss_status_success) {
        GPTOSS_LOG_ERROR("failed to encode f32_bf16w_unembedding kernel launch");
        goto cleanup;
    }

    gptoss_metal_command_buffer_commit(&command_buffer);
    gptoss_metal_command_buffer_wait_completion(&command_buffer, NULL);

    context->num_kv_tokens = context->num_tokens;
    context->num_processed_tokens = num_output_tokens;
    context->num_batch_tokens = 0;

cleanup:
    gptoss_metal_command_buffer_release(&command_buffer);
    return status;
}

enum gptoss_status GPTOSS_ABI gptoss_context_append_chars(
    gptoss_context_t context,
    const char* text,
    size_t text_length,
    size_t* num_tokens_out)
{
    enum gptoss_status status = gptoss_status_success;
    const struct gptoss_model* model = context->model;
    const struct gptoss_tokenizer* tokenizer = model->tokenizer;
    size_t num_appended_tokens = 0;
    while (text_length != 0) {
        if (context->num_tokens == context->max_tokens) {
            status = gptoss_status_context_overflow;
            break;
        }
        const char* tokens = tokenizer->tokens_ptr;
        uint32_t best_token = UINT32_MAX;
        uint32_t best_token_length = 0;
        for (size_t t = 0; t < tokenizer->num_text_tokens; t++) {
            uint16_t token_length;
            memcpy(&token_length, tokens, sizeof(uint16_t));
            tokens += sizeof(uint16_t);
            if (token_length <= text_length && token_length > best_token_length) {
                if (memcmp(text, tokens, token_length) == 0) {
                    if (token_length > best_token_length) {
                        best_token = (uint32_t) t;
                        best_token_length = token_length;
                    }
                }
            }
            tokens += token_length;
        }

        if (best_token == UINT32_MAX) {
            GPTOSS_LOG_ERROR("failed to tokenize text \"%.*s\"", (int) text_length, text);
            return gptoss_status_invalid_argument;
        }

        uint32_t* input_tokens = (uint32_t*) context->token_buffer.ptr;
        input_tokens[context->num_tokens] = best_token;
        context->num_tokens++;
        num_appended_tokens++;
        if (++context->num_batch_tokens == model->max_batch_tokens) {
            status = process_batch(context);
            if (status != gptoss_status_success) {
                break;
            }
            assert(context->num_batch_tokens == 0);
        }
        assert(context->num_batch_tokens < model->max_batch_tokens);
        text += best_token_length;
        text_length -= best_token_length;
    }
    if (num_tokens_out != NULL) {
        *num_tokens_out = num_appended_tokens;
    }
    return status;
}

enum gptoss_status GPTOSS_ABI gptoss_context_append_tokens(
    gptoss_context_t context,
    size_t num_tokens,
    const uint32_t* tokens)
{
    const struct gptoss_model* model = context->model;

    // Validate all tokens
    for (size_t t = 0; t < num_tokens; t++) {
        const uint32_t token = tokens[t];
        if (token >= model->vocabulary_size) {
            GPTOSS_LOG_ERROR("token %" PRIu32 " at index %zu is out of bounds for vocabulary size %" PRIu32,
                token, t, context->model->vocabulary_size);
            return gptoss_status_invalid_argument;
        }
    }

    enum gptoss_status status = gptoss_status_success;
    uint32_t* input_tokens = (uint32_t*) context->token_buffer.ptr;
    while (num_tokens != 0) {
        assert(context->num_batch_tokens < model->max_batch_tokens);
        if (context->num_tokens == context->max_tokens) {
            status = gptoss_status_context_overflow;
            break;
        }

        const size_t num_tokens_to_copy =
            math_min(context->max_tokens - context->num_tokens,
                math_min(num_tokens, model->max_batch_tokens - context->num_batch_tokens));
        memcpy(input_tokens + context->num_tokens, tokens, num_tokens_to_copy * sizeof(uint32_t));
        context->num_tokens += num_tokens_to_copy;
        context->num_batch_tokens += num_tokens_to_copy;
        if (context->num_batch_tokens == model->max_batch_tokens) {
            status = process_batch(context);
            if (status != gptoss_status_success) {
                break;
            }
            assert(context->num_batch_tokens == 0);
        }
        tokens += num_tokens_to_copy;
        num_tokens -= num_tokens_to_copy;
    }

    return status;
}

enum gptoss_status GPTOSS_ABI gptoss_context_process(
    gptoss_context_t context)
{
    if (context->num_batch_tokens != 0) {
        process_batch(context);
    }

    return gptoss_status_success;
}

enum gptoss_status GPTOSS_ABI gptoss_context_sample(
    gptoss_context_t context,
    float temperature,
    uint64_t seed,
    uint32_t* token_out)
{
    enum gptoss_status status = gptoss_status_success;
    const struct gptoss_model* model = context->model;
    struct gptoss_metal_command_buffer command_buffer = {0};

    *token_out = UINT32_MAX;
    if (context->num_batch_tokens != 0) {
        status = process_batch(context);
        if (status != gptoss_status_success) {
            return status;
        }
    }

    if (temperature == 0.0f) {
        const uint64_t argmax_bits = ((const uint64_t*) context->argmax_buffer.ptr)[0];
        *token_out = (uint32_t) argmax_bits;
    } else {
        assert(context->num_processed_tokens != 0);
        status = gptoss_metal_command_buffer_create(&context->model->command_queue, &command_buffer);
        if (status != gptoss_status_success) {
            goto cleanup;
        }

        uint32_t num_threadgroups = 0;
        uint32_t num_dims_per_threadgroup = 0;
        status = gptoss_metal_command_buffer_encode_launch_f32_softmax(
            &command_buffer,
            &model->f32_softmax_fn,
            /*threadgroup_size=*/256,
            model->max_threadgroups,
            &context->score_buffer,
            /*score_offset=*/0,
            &context->argmax_buffer,
            /*argmax_offset=*/0,
            &context->prob_buffer,
            /*prob_offset=*/0,
            &context->sum_buffer,
            /*sum_offset=*/0,
            model->vocabulary_size,
            /*num_tokens=*/1,
            temperature,
            &num_threadgroups,
            &num_dims_per_threadgroup);
        if (status != gptoss_status_success) {
            GPTOSS_LOG_ERROR("failed to encode f32_softmax kernel launch");
        }

        gptoss_metal_command_buffer_commit(&command_buffer);
        gptoss_metal_command_buffer_wait_completion(&command_buffer, NULL);

        const uint32_t sample_word = rng_squares32(context->num_tokens, seed + UINT64_C(0x123456789ABCDEF));
        float sample_cdf = (float) ((int32_t) sample_word & INT32_C(0x00FFFFFF)) * 0x1.0p-24f;

        const float* sum_ptr = (const float*) context->sum_buffer.ptr;
        float sum = 0.0f;
        for (uint32_t i = 0; i < num_threadgroups; i++) {
            sum += sum_ptr[i];
        }
        sample_cdf *= sum;

        uint32_t block_idx = 0, token_idx = 0;
        if (sample_cdf == 0.0f) {
            // Make sure we choose the first token with non-zero probability rather than just the first token
            sample_cdf = FLT_TRUE_MIN;
        }

        // Step 1: find block
        float cumsum = 0.0f;
        for (; block_idx < num_threadgroups; block_idx++) {
            const float new_cumsum = cumsum + sum_ptr[block_idx];
            if (new_cumsum >= sample_cdf) {
                break;
            }
            cumsum = new_cumsum;
        }
        if (block_idx == num_threadgroups) {
            block_idx -= 1;
        }

        // Step 2: find token
        const float* prob_ptr = (const float*) context->prob_buffer.ptr + block_idx * num_dims_per_threadgroup;
        assert(model->vocabulary_size > num_dims_per_threadgroup * block_idx);
        uint32_t num_dims_per_block = math_min(num_dims_per_threadgroup, model->vocabulary_size - num_dims_per_threadgroup * block_idx);
        for (; token_idx < num_dims_per_block; token_idx++) {
            const float new_cumsum = cumsum + prob_ptr[token_idx];
            if (new_cumsum >= sample_cdf) {
                break;
            }
            cumsum = new_cumsum;
        }
        if (token_idx == num_dims_per_block) {
            token_idx -= 1;
        }

        token_idx += block_idx * num_dims_per_threadgroup;

        *token_out = token_idx;

cleanup:
        gptoss_metal_command_buffer_release(&command_buffer);
        return status;
    }

    return gptoss_status_success;
}

enum gptoss_status GPTOSS_ABI gptoss_context_reset(
    gptoss_context_t context)
{
    context->num_tokens = 0;
    context->num_kv_tokens = 0;
    context->num_batch_tokens = 0;
    context->num_processed_tokens = 0;
    return gptoss_status_success;
}

enum gptoss_status GPTOSS_ABI gptoss_context_retain(
    gptoss_context_t context)
{
    atomic_fetch_add_explicit(&context->ref_count, 1, memory_order_relaxed);
    return gptoss_status_success;
}

enum gptoss_status GPTOSS_ABI gptoss_context_release(
    gptoss_context_t context)
{
    if (context != NULL) {
        if (atomic_fetch_sub_explicit(&context->ref_count, 1, memory_order_acq_rel) == 1) {
            gptoss_metal_buffer_release(&context->token_buffer);
            gptoss_metal_buffer_release(&context->score_buffer);
            gptoss_metal_buffer_release(&context->prob_buffer);
            gptoss_metal_buffer_release(&context->sum_buffer);
            gptoss_metal_buffer_release(&context->argmax_buffer);
            gptoss_metal_buffer_release(&context->kvcache_buffer);

            gptoss_model_release(context->model);

            memset(context, 0, sizeof(struct gptoss_context));
            free(context);
        }
    }
    return gptoss_status_success;
}
