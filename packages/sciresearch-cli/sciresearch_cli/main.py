from __future__ import annotations

import argparse

# Provider registries - we will load these via entry points later
from sciresearch_providers_openai.registry import PROVIDERS as OPENAI_PROVIDERS

from sciresearch_ai.config import RunConfig
from sciresearch_ai.orchestrator import Orchestrator

# Core components from the main application
from sciresearch_ai.project import Project
from sciresearch_ai.providers.mock_provider import MockProvider

# from sciresearch_ai.providers.oss_provider import OssProvider # TODO: migrate to its own package

# For now, we'll manually assemble the providers.
# TODO: Replace with an entry-point-based discovery mechanism.
ALL_PROVIDERS = {p.name: p for p in OPENAI_PROVIDERS}
ALL_PROVIDERS[MockProvider.name] = MockProvider
# if OssProvider:
#     ALL_PROVIDERS[OssProvider.name] = OssProvider


def build_provider(args, project_root: str):
    provider_class = ALL_PROVIDERS.get(args.provider)
    if not provider_class:
        raise SystemExit(f"Unknown provider: {args.provider}")

    if args.provider == "mock":
        return MockProvider()
    elif args.provider == "openai":
        return provider_class(
            model=args.model,
            temperature=args.temperature,
            top_p=args.top_p,
            max_output_tokens=args.max_output_tokens,
            reasoning_effort=args.reasoning_effort,
            enable_code_interpreter=args.enable_code_interpreter,
            project_root=project_root,
        )
    # elif args.provider == "oss":
    #     return provider_class(
    #         checkpoint=args.model,
    #         reasoning_effort=args.reasoning_effort,
    #         enable_browser=args.enable_browser,
    #         enable_python=args.enable_python,
    #     )
    else:
        # This path should not be reached if argparse choices are set correctly.
        raise SystemExit(f"Provider '{args.provider}' not fully configured in CLI.")


def cmd_new(args):
    prj = Project.create(args.root, args.name)
    print(f"Created project at: {prj.root}")


def cmd_run(args):
    prj = Project(args.project)
    provider = build_provider(args, prj.root)
    cfg = RunConfig(
        model=args.model,
        max_iterations=args.max_iterations,
        samples_per_query=args.samples_per_query,
        time_budget_sec=args.time_budget_sec,
        parallel_workers=args.parallel_workers,
        devices=args.devices.split(",") if args.devices else [],
        reasoning_effort=args.reasoning_effort,
        temperature=args.temperature,
        top_p=args.top_p,
        max_output_tokens=args.max_output_tokens,
        budget_usd=args.budget_usd,
        interactive=not args.no_interactive,
        enable_code_interpreter=args.enable_code_interpreter,
    )
    orch = Orchestrator(prj, provider, cfg)
    orch.run()
    print("Run finished. See state.json and logs folder for details.")


def cmd_test_openai(args):
    provider_class = ALL_PROVIDERS.get("openai")
    if not provider_class:
        raise SystemExit("OpenAI provider not found.")

    reasoning = (
        None if args.reasoning_effort in (None, "none") else args.reasoning_effort
    )
    provider = provider_class(
        model=args.model,
        temperature=0.2,
        top_p=1.0,
        max_output_tokens=100,
        reasoning_effort=reasoning,
        enable_code_interpreter=False,
    )
    try:
        resp = provider.generate("Respond with 'OpenAI connection successful.'", n=1)[0]
        print("OpenAI response:", resp)
    except Exception as e:
        print("OpenAI test failed:", e)


def main(argv=None):
    p = argparse.ArgumentParser(
        prog="sciresearch-ai", description="Automated scientific research CLI"
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    p_new = sub.add_parser("new", help="Create a new project folder")
    p_new.add_argument("--name", required=True)
    p_new.add_argument("--root", default=".")
    p_new.set_defaults(func=cmd_new)

    p_run = sub.add_parser("run", help="Run the research loop on an existing project")
    p_run.add_argument("--project", required=True, help="Path to project folder")
    p_run.add_argument(
        "--provider", choices=sorted(ALL_PROVIDERS.keys()), default="mock"
    )
    p_run.add_argument(
        "--model",
        default=None,
        help="For OpenAI, a model ID like 'gpt-4o-mini'. For OSS, a local path or Hugging Face model ID.",
    )
    p_run.add_argument("--max-iterations", type=int, default=5)
    p_run.add_argument("--samples-per-query", type=int, default=5)
    p_run.add_argument("--time-budget-sec", type=int, default=1800)
    p_run.add_argument("--parallel-workers", type=int, default=2)
    p_run.add_argument("--devices", default="")
    p_run.add_argument(
        "--reasoning-effort", choices=["low", "medium", "high"], default="high"
    )
    p_run.add_argument("--temperature", type=float, default=0.2)
    p_run.add_argument("--top_p", type=float, default=0.9)
    p_run.add_argument("--max-output-tokens", type=int, default=2000)
    p_run.add_argument("--budget-usd", type=float, default=None)
    p_run.add_argument(
        "--no-interactive",
        action="store_true",
        help="Disable human-in-the-loop prompts",
    )
    p_run.add_argument(
        "--enable-code-interpreter",
        action="store_true",
        help="Enable server-side code interpreter tool",
    )
    p_run.add_argument(
        "--enable-browser",
        action="store_true",
        help="Enable web search tool for OSS provider",
    )
    p_run.add_argument(
        "--enable-python",
        action="store_true",
        help="Enable Python tool for OSS provider",
    )
    p_run.set_defaults(func=cmd_run)

    p_test = sub.add_parser(
        "test-openai", help="Send a test prompt to OpenAI and print the response"
    )
    p_test.add_argument("--model", default="gpt-4o-mini")
    p_test.add_argument(
        "--reasoning-effort", choices=["low", "medium", "high", "none"], default=None
    )
    p_test.set_defaults(func=cmd_test_openai)

    args = p.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
