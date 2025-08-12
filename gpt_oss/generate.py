# Model parallel inference
# Note: This script is for demonstration purposes only. It is not designed for production use.
#       See gpt_oss.chat for a more complete example with the Harmony parser.
# torchrun --nproc-per-node=4 -m gpt_oss.generate -p "why did the chicken cross the road?" model/

import argparse

from gpt_oss.tokenizer import get_tokenizer


def main(args):
    match args.backend:
        case "torch":
            from gpt_oss.torch.utils import init_distributed
            from gpt_oss.torch.model import TokenGenerator as TorchGenerator
            device = init_distributed()
            generator = TorchGenerator(args.checkpoint, device=device)
        case "triton":
            from gpt_oss.torch.utils import init_distributed
            from gpt_oss.triton.model import TokenGenerator as TritonGenerator
            device = init_distributed()
            generator = TritonGenerator(args.checkpoint, context=4096, device=device)
        case "vllm":
            from gpt_oss.vllm.token_generator import TokenGenerator as VLLMGenerator
            generator = VLLMGenerator(args.checkpoint, tensor_parallel_size=2)
        case _:
            raise ValueError(f"Invalid backend: {args.backend}")

    tokenizer = get_tokenizer()
    tokens = tokenizer.encode(args.prompt)
    for token, logprob in generator.generate(tokens, stop_tokens=[tokenizer.eot_token], temperature=args.temperature, max_tokens=args.limit, return_logprobs=True):
        tokens.append(token)
        decoded_token = tokenizer.decode([token])
        print(
            f"Generated token: {repr(decoded_token)}, logprob: {logprob}"
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Text generation example")
    parser.add_argument(
        "checkpoint",
        metavar="FILE",
        type=str,
        help="Path to the SafeTensors checkpoint",
    )
    parser.add_argument(
        "-p",
        "--prompt",
        metavar="PROMPT",
        type=str,
        default="How are you?",
        help="LLM prompt",
    )
    parser.add_argument(
        "-t",
        "--temperature",
        metavar="TEMP",
        type=float,
        default=0.0,
        help="Sampling temperature",
    )
    parser.add_argument(
        "-l",
        "--limit",
        metavar="LIMIT",
        type=int,
        default=0,
        help="Limit on the number of tokens (0 to disable)",
    )
    parser.add_argument(
        "-b",
        "--backend",
        metavar="BACKEND",
        type=str,
        default="torch",
        choices=["triton", "torch", "vllm"],
        help="Inference backend",
    )
    args = parser.parse_args()

    main(args)
