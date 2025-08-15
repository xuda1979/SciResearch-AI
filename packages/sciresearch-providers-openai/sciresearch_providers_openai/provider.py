from __future__ import annotations
import os, httpx, json, time
from typing import List, Dict, Any, Callable, Optional
from openai import OpenAI, APIError, APITimeoutError

# Local function tools that the model can call through the Responses API.
# We expose simple capabilities that are safe and useful during research.
from .tools.python_exec import run_user_code
from .tools.sympy_tools import check_symbolic_equality

def _build_client() -> OpenAI:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Set OPENAI_API_KEY environment variable.")
    proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("HTTP_PROXY")
    if proxy:
        transport = httpx.HTTPTransport(proxy=proxy)
        http_client = httpx.Client(transport=transport, timeout=httpx.Timeout(120, connect=10))
        return OpenAI(api_key=api_key, http_client=http_client)
    return OpenAI(api_key=api_key)

class OpenAIProvider:
    name = "openai"
    def __init__(
        self,
        model: str,
        temperature: float,
        top_p: float,
        max_output_tokens: int,
        reasoning_effort: Optional[str] = None,
        enable_code_interpreter: bool = False,
        project_root: Optional[str] = None,
    ):
        self.client = _build_client()
        self.model = model
        self.temperature = temperature
        self.top_p = top_p
        self.max_output_tokens = max_output_tokens
        self.reasoning_effort = reasoning_effort
        self.enable_code_interpreter = enable_code_interpreter
        self.project_root = project_root

    def _model_supports_reasoning(self) -> bool:
        """Return True if the selected model supports the reasoning param."""
        reasoning_models = {
            "o1-preview",
            "o1-mini",
            "gpt-o1-mini",
            "gpt-o1-preview",
            "o3-mini",
            "gpt-o3-mini",
        }
        return any(m in self.model for m in reasoning_models)

    # ---- Tool registry
    def _function_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "type": "function",
                "name": "run_python",
                "description": "Execute short Python snippets and return stdout/stderr text (no network).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "description": "Python code to run"}
                    },
                    "required": ["code"]
                },
            },
            {
                "type": "function",
                "name": "check_symbolic_equality",
                "description": "Check if two mathematical expressions are symbolically equal.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expr1": {"type": "string"},
                        "expr2": {"type": "string"}
                    },
                    "required": ["expr1","expr2"]
                },
            },
            {
                "type": "function",
                "name": "write_project_file",
                "description": "Write a text file under the project folder (e.g., code/, notes/).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "relative_path": {"type": "string", "description": "Relative path inside project, e.g., 'code/exp.py'"},
                        "content": {"type": "string"}
                    },
                    "required": ["relative_path","content"]
                },
            },
            {
                "type": "function",
                "name": "list_project_files",
                "description": "List files under a relative path inside the project.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "relative_path": {"type": "string", "description": "Directory path, e.g., 'code/'"},
                    },
                    "required": ["relative_path"]
                },
            },
        ]

    def _dispatch_tool(self, name: str, arguments: Dict[str, Any]) -> str:
        try:
            if name == "run_python":
                return run_user_code(arguments.get("code",""))
            elif name == "check_symbolic_equality":
                ok = check_symbolic_equality(arguments.get("expr1",""), arguments.get("expr2",""))
                return json.dumps({"equal": bool(ok)})
            elif name == "write_project_file":
                rel = arguments.get("relative_path","")
                content = arguments.get("content","")
                if not self.project_root:
                    return json.dumps({"error": "project_root not set"})
                import os
                dest = os.path.abspath(os.path.join(self.project_root, rel))
                if not dest.startswith(os.path.abspath(self.project_root)):
                    return json.dumps({"error": "path escapes project_root"})
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                with open(dest, "w", encoding="utf-8") as f:
                    f.write(content)
                return json.dumps({"written": rel})
            elif name == "list_project_files":
                rel = arguments.get("relative_path","")
                if not self.project_root:
                    return json.dumps({"error": "project_root not set"})
                import os
                base = os.path.abspath(os.path.join(self.project_root, rel))
                if not os.path.isdir(base):
                    return json.dumps({"files": [], "error": "not a directory"})
                files = []
                for root, _, fs in os.walk(base):
                    for fn in fs:
                        full = os.path.join(root, fn)
                        files.append(os.path.relpath(full, self.project_root))
                return json.dumps({"files": files})
            else:
                return json.dumps({"error": f"unknown tool {name}"})
        except Exception as e:
            return json.dumps({"error": str(e)})

    def generate(self, prompt: str, n: int = 1, **gen_kwargs) -> List[str]:
        # Tool-enabled Responses API with function tools and optional code_interpreter
        outputs: List[str] = []
        try:
            tools = self._function_tools()
            if self.enable_code_interpreter:
                tools = [{"type": "code_interpreter", "name": "code_interpreter"}] + tools
            # We keep it simple: single prompt per call; if n>1, loop.
            if n > 1:
                for _ in range(n):
                    outputs.extend(self.generate(prompt, n=1, **gen_kwargs))
                return outputs

            reasoning_effort = gen_kwargs.get("reasoning_effort", self.reasoning_effort)

            params = dict(
                model=self.model,
                input=prompt,
                temperature=self.temperature,
                top_p=self.top_p,
                max_output_tokens=self.max_output_tokens,
                tools=tools,

                include_reasoning = (
                    reasoning_effort is not None or self._model_supports_reasoning()
                )

            )
            if reasoning_effort is not None:
                params["reasoning"] = {"effort": reasoning_effort}

            def _create(include_reasoning_param: bool):
                req = {
                    "model": self.model,
                    "input": prompt,
                    "temperature": self.temperature,
                    "top_p": self.top_p,
                    "max_output_tokens": self.max_output_tokens,
                    "tools": tools,
                }
                if include_reasoning_param:
                    reasoning: Dict[str, Any] = {}
                    if reasoning_effort is not None:
                        reasoning["effort"] = reasoning_effort
                    req["reasoning"] = reasoning
                return self.client.responses.create(**req)

            try:
                include_reasoning = (
                    reasoning_effort is not None or self._model_supports_reasoning()
                )
                resp = _create(include_reasoning)
            except APIError as e:
                if (
                    include_reasoning
                    and getattr(e, "code", "") == "unsupported_parameter"
                    and "reasoning.effort" in str(e)
                ):
                    resp = _create(False)
                else:
                    raise

            # Handle tool calling loop (function tools)
            while True:
                # collect text
                txts = []
                tool_calls = []
                for item in getattr(resp, "output", []) or []:
                    if getattr(item, "type", None) == "output_text":
                        txts.append(getattr(item, "text", ""))
                    elif getattr(item, "type", None) == "tool_call":
                        tool_calls.append(item)
                if txts and not tool_calls:
                    outputs.append("".join(txts))
                    break
                if tool_calls:
                    tool_outputs = []
                    for call in tool_calls:
                        fn = getattr(call, "name", "")
                        args_json = getattr(call, "arguments", "{}")
                        try:
                            args = json.loads(args_json) if isinstance(args_json, str) else args_json
                        except Exception:
                            args = {}
                        result = self._dispatch_tool(fn, args if isinstance(args, dict) else {})
                        tool_outputs.append({
                            "tool_call_id": getattr(call, "id", ""),
                            "output": result[:100000],  # avoid oversized payloads
                        })
                    resp = self.client.responses.submit_tool_outputs(
                        response_id=resp.id,
                        tool_outputs=tool_outputs
                    )
                    # loop again to read new outputs
                    continue
                # if we got here with no text and no tools, append raw
                outputs.append(str(resp))
                break
        except (APIError, APITimeoutError) as e:
            outputs.append(f"API error: {e}")
        except Exception as e:
            outputs.append(f"Provider exception: {e}")
        return outputs
