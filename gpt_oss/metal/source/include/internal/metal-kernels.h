#pragma once

#include <stddef.h>
#include <stdint.h>

#include <internal/metal.h>

#ifdef __cplusplus
extern "C" {
#endif

#include <stddef.h>
#include <stdint.h>

#include <internal/kernel-args.h>
#include <internal/math.h>
#include <internal/metal.h>


enum gptoss_status gptoss_metal_command_buffer_encode_launch_u32_fill_random(
    const struct gptoss_metal_command_buffer* command_buffer,
    const struct gptoss_metal_function* u32_fill_random_fn,
    size_t threadgroup_size,
    size_t max_threadgroups,
    const struct gptoss_metal_buffer* output_buffer,
    size_t output_offset,
    uint64_t num_elements,
    uint64_t rng_seed,
    uint64_t rng_offset);

enum gptoss_status gptoss_metal_command_buffer_encode_launch_f32_fill_random(
    const struct gptoss_metal_command_buffer* command_buffer,
    const struct gptoss_metal_function* f32_fill_random_fn,
    size_t threadgroup_size,
    size_t max_threadgroups,
    const struct gptoss_metal_buffer* output_buffer,
    size_t output_offset,
    uint64_t num_elements,
    uint64_t rng_seed,
    uint64_t rng_offset,
    float rng_min,
    float rng_max);

enum gptoss_status gptoss_metal_command_buffer_encode_launch_bf16_fill_random(
    const struct gptoss_metal_command_buffer* command_buffer,
    const struct gptoss_metal_function* bf16_fill_random_fn,
    size_t threadgroup_size,
    size_t max_threadgroups,
    const struct gptoss_metal_buffer* output_buffer,
    size_t output_offset,
    uint64_t num_elements,
    uint64_t rng_seed,
    uint64_t rng_offset,
    float rng_min,
    float rng_max);

enum gptoss_status gptoss_metal_command_buffer_encode_launch_mf4_f32_convert(
    const struct gptoss_metal_command_buffer* command_buffer,
    const struct gptoss_metal_function* mf4_f32_convert_fn,
    size_t threadgroup_size,
    size_t max_threadgroups,
    const struct gptoss_metal_buffer* block_buffer,
    const struct gptoss_metal_buffer* scale_buffer,
    const struct gptoss_metal_buffer* output_buffer,
    uint64_t num_elements);

enum gptoss_status gptoss_metal_command_buffer_encode_launch_bf16_f32_embeddings(
    const struct gptoss_metal_command_buffer* command_buffer,
    const struct gptoss_metal_function* bf16_f32_embeddings_fn,
    size_t threadgroup_size,
    const struct gptoss_metal_buffer* token_buffer,
    size_t token_offset,
    const struct gptoss_metal_buffer* weight_buffer,
    size_t weight_offset,
    const struct gptoss_metal_buffer* output_buffer,
    size_t output_offset,
    uint32_t num_tokens,
    uint32_t num_channels);

enum gptoss_status gptoss_metal_command_buffer_encode_launch_f32_bf16w_rmsnorm(
    const struct gptoss_metal_command_buffer* command_buffer,
    const struct gptoss_metal_function* f32_bf16w_rmsnorm_fn,
    const struct gptoss_metal_buffer* input_buffer,
    size_t input_offset,
    const struct gptoss_metal_buffer* weight_buffer,
    size_t weight_offset,
    const struct gptoss_metal_buffer* output_buffer,
    size_t output_offset,
    uint32_t num_tokens,
    uint32_t num_channels,
    float epsilon);

enum gptoss_status gptoss_metal_command_buffer_encode_launch_f32_bf16w_matmul(
    const struct gptoss_metal_command_buffer* command_buffer,
    const struct gptoss_metal_function* f32_bf16w_matmul_fn,
    size_t threadgroup_size,
    const struct gptoss_metal_buffer* input_buffer,
    size_t input_offset,
    const struct gptoss_metal_buffer* weight_buffer,
    size_t weight_offset,
    const struct gptoss_metal_buffer* bias_buffer,
    size_t bias_offset,
    const struct gptoss_metal_buffer* output_buffer,
    size_t output_offset,
    uint32_t num_tokens,
    uint32_t num_cols,
    uint32_t num_rows);

enum gptoss_status gptoss_metal_command_buffer_encode_launch_f32_bf16w_matmul_add(
    const struct gptoss_metal_command_buffer* command_buffer,
    const struct gptoss_metal_function* f32_bf16w_matmul_fn,
    size_t threadgroup_size,
    const struct gptoss_metal_buffer* input_buffer,
    size_t input_offset,
    const struct gptoss_metal_buffer* weight_buffer,
    size_t weight_offset,
    const struct gptoss_metal_buffer* bias_buffer,
    size_t bias_offset,
    const struct gptoss_metal_buffer* output_buffer,
    size_t output_offset,
    uint32_t num_tokens,
    uint32_t num_cols,
    uint32_t num_rows);

enum gptoss_status gptoss_metal_command_buffer_encode_launch_f32_bf16w_unembedding(
    const struct gptoss_metal_command_buffer* command_buffer,
    const struct gptoss_metal_function* f32_bf16w_matmul_fn,
    size_t threadgroup_size,
    size_t max_threadgroups,
    const struct gptoss_metal_buffer* input_buffer,
    size_t input_offset,
    const struct gptoss_metal_buffer* weight_buffer,
    size_t weight_offset,
    const struct gptoss_metal_buffer* output_buffer,
    size_t output_offset,
    const struct gptoss_metal_buffer* argmax_buffer,
    size_t argmax_offset,
    uint32_t num_tokens,
    uint32_t num_cols,
    uint32_t num_rows);

enum gptoss_status gptoss_metal_command_buffer_encode_launch_f32_mf4w_moe_matmul_swiglu(
    const struct gptoss_metal_command_buffer* command_buffer,
    const struct gptoss_metal_function* f32_mf4w_moe_matmul_swiglu_fn,
    size_t threadgroup_size,
    const struct gptoss_metal_buffer* input_buffer,
    size_t input_offset,
    const struct gptoss_metal_buffer* expert_buffer,
    size_t expert_offset,
    const struct gptoss_metal_buffer* weight_block_buffer,
    size_t weight_block_offset,
    const struct gptoss_metal_buffer* weight_scale_buffer,
    size_t weight_scale_offset,
    const struct gptoss_metal_buffer* bias_buffer,
    size_t bias_offset,
    const struct gptoss_metal_buffer* output_buffer,
    size_t output_offset,
    float swiglu_limit,
    uint32_t expert_stride,
    uint32_t num_tokens,
    uint32_t num_active_experts,
    uint32_t num_cols,
    uint32_t num_rows);

enum gptoss_status gptoss_metal_command_buffer_encode_launch_f32_mf4w_moe_matmul(
    const struct gptoss_metal_command_buffer* command_buffer,
    const struct gptoss_metal_function* f32_mf4w_moe_matmul_fn,
    size_t threadgroup_size,
    const struct gptoss_metal_buffer* input_buffer,
    size_t input_offset,
    const struct gptoss_metal_buffer* expert_buffer,
    size_t expert_offset,
    const struct gptoss_metal_buffer* weight_block_buffer,
    size_t weight_block_offset,
    const struct gptoss_metal_buffer* weight_scale_buffer,
    size_t weight_scale_offset,
    const struct gptoss_metal_buffer* bias_buffer,
    size_t bias_offset,
    const struct gptoss_metal_buffer* output_buffer,
    size_t output_offset,
    uint32_t expert_stride,
    uint32_t num_tokens,
    uint32_t num_active_experts,
    uint32_t num_cols,
    uint32_t num_rows);

enum gptoss_status gptoss_metal_command_buffer_encode_launch_f32_rope(
    const struct gptoss_metal_command_buffer* command_buffer,
    const struct gptoss_metal_function* f32_rope_fn,
    size_t threadgroup_size,
    const struct gptoss_metal_buffer* activations_buffer,
    float rope_base,
    float interpolation_scale,
    float yarn_offset,
    float yarn_scale,
    float yarn_multiplier,
    uint32_t num_tokens,
    uint32_t num_q_heads,
    uint32_t num_kv_heads,
    uint32_t attn_head_dim,
    uint32_t token_offset);

enum gptoss_status gptoss_metal_command_buffer_encode_launch_f32_accumulate(
    const struct gptoss_metal_command_buffer* command_buffer,
    const struct gptoss_metal_function* f32_accumulate_fn,
    size_t threadgroup_size,
    size_t max_threadgroups,
    const struct gptoss_metal_buffer* input_buffer,
    size_t input_offset,
    const struct gptoss_metal_buffer* expert_buffer,
    size_t expert_offset,
    const struct gptoss_metal_buffer* output_buffer,
    size_t output_offset,
    uint32_t num_channels,
    uint32_t num_tokens,
    uint32_t num_experts);

enum gptoss_status gptoss_metal_command_buffer_encode_launch_f32_topk(
    const struct gptoss_metal_command_buffer* command_buffer,
    const struct gptoss_metal_function* f32_topk_fn,
    const struct gptoss_metal_buffer* input_buffer,
    size_t input_offset,
    const struct gptoss_metal_buffer* output_buffer,
    size_t output_offset,
    uint32_t num_tokens,
    uint32_t num_experts,
    uint32_t num_active_experts);

enum gptoss_status gptoss_metal_command_buffer_encode_launch_f32_sdpa(
    const struct gptoss_metal_command_buffer* command_buffer,
    const struct gptoss_metal_function* f32_sdpa_fn,
    const struct gptoss_metal_buffer* q_buffer,
    size_t q_offset,
    const struct gptoss_metal_buffer* k_buffer,
    size_t k_offset,
    const struct gptoss_metal_buffer* v_buffer,
    size_t v_offset,
    const struct gptoss_metal_buffer* s_buffer,
    size_t s_offset,
    const struct gptoss_metal_buffer* output_buffer,
    size_t output_offset,
    uint32_t window,
    uint32_t num_q_tokens,
    uint32_t num_kv_tokens,
    uint32_t num_q_heads,
    uint32_t num_kv_heads,
    uint32_t head_dim);

enum gptoss_status gptoss_metal_command_buffer_encode_launch_f32_softmax(
    const struct gptoss_metal_command_buffer* command_buffer,
    const struct gptoss_metal_function* f32_softmax_fn,
    size_t threadgroup_size,
    size_t max_threadgroups,
    const struct gptoss_metal_buffer* score_buffer,
    size_t score_offset,
    const struct gptoss_metal_buffer* argmax_buffer,
    size_t argmax_offset,
    const struct gptoss_metal_buffer* prob_buffer,
    size_t prob_offset,
    const struct gptoss_metal_buffer* sum_buffer,
    size_t sum_offset,
    uint32_t num_channels,
    uint32_t num_tokens,
    float temperature,
    uint32_t* num_threadgroups_out,
    uint32_t* num_channels_per_threadgroup_out);

#ifdef __cplusplus
}  // extern "C"
#endif
