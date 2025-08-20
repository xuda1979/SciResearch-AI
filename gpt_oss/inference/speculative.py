import torch

@torch.inference_mode()
def speculative_decode(
    prompt_tokens: list[int],
    main_model: torch.nn.Module,
    draft_model: torch.nn.Module,
    max_tokens: int,
    gamma: int,
    stop_tokens: list[int],
    temperature: float = 1.0,
    return_logprobs: bool = False,
):
    """
    Performs speculative decoding using a main model and a draft model.
    """
    tokens = list(prompt_tokens)
    num_generated_tokens = 0

    while max_tokens == 0 or num_generated_tokens < max_tokens:
        # 1. Draft model generates a sequence of gamma tokens
        draft_tokens = list(tokens)
        for _ in range(gamma):
            logits = draft_model(
                torch.as_tensor(draft_tokens, dtype=torch.int32, device=main_model.embedding.weight.device)
            )[-1]
            if temperature == 0.0:
                next_token = torch.argmax(logits, dim=-1).item()
            else:
                probs = torch.softmax(logits / temperature, dim=-1)
                next_token = torch.multinomial(probs, num_samples=1).item()
            draft_tokens.append(next_token)

        # 2. Main model verifies the draft tokens in parallel
        main_logits = main_model(
            torch.as_tensor(draft_tokens, dtype=torch.int32, device=main_model.embedding.weight.device)
        )

        accepted_tokens = 0
        last_token = -1
        for i in range(gamma):
            main_prob = torch.softmax(main_logits[len(tokens) + i - 1] / temperature, dim=-1)
            draft_prob = torch.softmax(
                draft_model(
                    torch.as_tensor(draft_tokens[:len(tokens) + i], dtype=torch.int32, device=main_model.embedding.weight.device)
                )[-1] / temperature,
                dim=-1,
            )

            p = main_prob[draft_tokens[len(tokens) + i]]
            q = draft_prob[draft_tokens[len(tokens) + i]]

            if torch.rand(1).item() < (p / q):
                # Accept token
                accepted_tokens += 1
            else:
                # Reject token and sample a new one from the corrected distribution
                new_dist = (main_prob - draft_prob).clamp(min=0)
                new_dist /= new_dist.sum()
                last_token = torch.multinomial(new_dist, num_samples=1).item()
                break

        newly_added_tokens = draft_tokens[len(tokens):len(tokens) + accepted_tokens]
        if last_token != -1:
            newly_added_tokens.append(last_token)

        for new_token in newly_added_tokens:
            if max_tokens > 0 and num_generated_tokens >= max_tokens:
                break

            tokens.append(new_token)
            num_generated_tokens += 1

            if return_logprobs:
                logprobs = torch.log_softmax(main_logits[len(tokens) - 2], dim=-1)
                selected_logprobs = logprobs[new_token].item()
                yield new_token, selected_logprobs
            else:
                yield new_token

            if new_token in stop_tokens:
                return
