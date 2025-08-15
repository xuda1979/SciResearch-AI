from __future__ import annotations
import argparse
from .project import Project
from .config import RunConfig

def build_provider(args, project_root: str):
    if args.provider == "mock":
        from .providers.mock_provider import MockProvider
        return MockProvider()
    elif args.provider == "openai":
        from .providers.openai_provider import OpenAIProvider
        return OpenAIProvider(
            model=args.model,
            temperature=args.temperature,
            top_p=args.top_p,
            max_output_tokens=args.max_output_tokens,
            reasoning_effort=args.reasoning_effort,
            enable_code_interpreter=args.enable_code_interpreter,
            project_root=project_root,
        )
    elif args.provider == "oss":
        from .providers.oss_provider import OssProvider
        # If --model is not provided, the provider will use its default "openai/oss-120b"
        return OssProvider(
            checkpoint=args.model,
            reasoning_effort=args.reasoning_effort,
            enable_browser=args.enable_browser,
            enable_python=args.enable_python,
        )
    else:
        raise SystemExit(f"Unknown provider: {args.provider}")

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
    from .orchestrator import Orchestrator
    orch = Orchestrator(prj, provider, cfg)
    orch.run()
    print("Run finished. See state.json and logs folder for details.")

def cmd_test_openai(args):
    from .providers.openai_provider import OpenAIProvider
    reasoning = None if args.reasoning_effort in (None, "none") else args.reasoning_effort
    provider = OpenAIProvider(
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
    p = argparse.ArgumentParser(prog="sciresearch-ai", description="Automated scientific research CLI")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_new = sub.add_parser("new", help="Create a new project folder")
    p_new.add_argument("--name", required=True)
    p_new.add_argument("--root", default=".")
    p_new.set_defaults(func=cmd_new)

    p_run = sub.add_parser("run", help="Run the research loop on an existing project")
    p_run.add_argument("--project", required=True, help="Path to project folder")
    p_run.add_argument("--provider", choices=["mock", "openai", "oss"], default="mock")
    p_run.add_argument("--model", default=None, help="For OpenAI, a model ID like 'gpt-5-chat-latest'. For OSS, a local path or Hugging Face model ID.")
    p_run.add_argument("--max-iterations", type=int, default=5)
    p_run.add_argument("--samples-per-query", type=int, default=5)
    p_run.add_argument("--time-budget-sec", type=int, default=1800)
    p_run.add_argument("--parallel-workers", type=int, default=2)
    p_run.add_argument("--devices", default="")
    p_run.add_argument("--reasoning-effort", choices=["low","medium","high"], default="high")
    p_run.add_argument("--temperature", type=float, default=0.2)
    p_run.add_argument("--top_p", type=float, default=0.9)
    p_run.add_argument("--max-output-tokens", type=int, default=2000)
    p_run.add_argument("--budget-usd", type=float, default=None)
    p_run.add_argument("--no-interactive", action="store_true", help="Disable human-in-the-loop prompts")
    p_run.add_argument("--enable-code-interpreter", action="store_true", help="Enable server-side code interpreter tool")
    p_run.add_argument("--enable-browser", action="store_true", help="Enable web search tool for OSS provider")
    p_run.add_argument("--enable-python", action="store_true", help="Enable Python tool for OSS provider")
    p_run.set_defaults(func=cmd_run)

    p_test = sub.add_parser("test-openai", help="Send a test prompt to OpenAI and print the response")
    p_test.add_argument("--model", default="gpt-4o-mini")
    p_test.add_argument("--reasoning-effort", choices=["low","medium","high","none"], default=None)
    p_test.set_defaults(func=cmd_test_openai)

    args = p.parse_args(argv)
    return args.func(args)

if __name__ == "__main__":
    main()
