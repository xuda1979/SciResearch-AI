import torch

from gpt_oss.inference.speculative import speculative_decode
from gpt_oss.torch.model import Transformer


class SpeculativeTokenGenerator:
    @torch.inference_mode()
    def __init__(self, main_checkpoint: str, draft_checkpoint: str, device: torch.device):
        self.device = device
        self.main_model = Transformer.from_checkpoint(main_checkpoint, device=self.device)
        self.draft_model = Transformer.from_checkpoint(draft_checkpoint, device=self.device)

    @torch.inference_mode()
    def generate(
        self,
        prompt_tokens: list[int],
        stop_tokens: list[int],
        temperature: float = 1.0,
        max_tokens: int = 0,
        gamma: int = 4,
        return_logprobs: bool = False,
    ):
        yield from speculative_decode(
            prompt_tokens=prompt_tokens,
            main_model=self.main_model,
            draft_model=self.draft_model,
            max_tokens=max_tokens,
            gamma=gamma,
            stop_tokens=stop_tokens,
            temperature=temperature,
            return_logprobs=return_logprobs,
        )
