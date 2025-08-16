from __future__ import annotations

import asyncio
import datetime
import os
from typing import Any, List, Optional

# Imports for the heavy OSS model are deferred so that the lightweight stub
# can run without triggering network downloads of Harmony vocabularies.
_setup_transformers = None


class OssProvider:
    """Local provider for the open-source OSS 120B model with tool support."""

    name = "oss"

    def __init__(
        self,
        checkpoint: Optional[str] = None,
        *,
        device: Optional[str] = None,
        reasoning_effort: str = "low",
        enable_browser: bool = False,
        enable_python: bool = False,
    ) -> None:
        self.checkpoint = checkpoint or "openai/oss-120b"
        backend = os.environ.get("OSS_PROVIDER_BACKEND", "transformers")
        self._backend = backend
        if backend == "stub":
            # The stub backend returns a fixed string and avoids any heavy
            # initialization or network access.
            self._infer_next_token = None
            self.encoding = None
        else:
            from openai_harmony import (
                Author,
                Conversation,
                DeveloperContent,
                HarmonyEncodingName,
                Message,
                ReasoningEffort,
                Role,
                StreamableParser,
                SystemContent,
                TextContent,
                load_harmony_encoding,
            )

            from gpt_oss.responses_api.inference.transformers import (
                setup_model as _setup_transformers,
            )

            self.Author = Author
            self.Conversation = Conversation
            self.DeveloperContent = DeveloperContent
            self.HarmonyEncodingName = HarmonyEncodingName
            self.Message = Message
            self.ReasoningEffort = ReasoningEffort
            self.Role = Role
            self.StreamableParser = StreamableParser
            self.SystemContent = SystemContent
            self.TextContent = TextContent
            self.load_harmony_encoding = load_harmony_encoding
            self.REASONING_EFFORT = {
                "high": ReasoningEffort.HIGH,
                "medium": ReasoningEffort.MEDIUM,
                "low": ReasoningEffort.LOW,
            }

            # transformers-based incremental generator
            self._infer_next_token = _setup_transformers(self.checkpoint, device=device)
            self.encoding = load_harmony_encoding(HarmonyEncodingName.HARMONY_GPT_OSS)
        self.reasoning_effort = reasoning_effort
        self.enable_browser = enable_browser
        self.enable_python = enable_python
        self.browser_tool = None
        self.python_tool = None
        if enable_browser:
            from gpt_oss.tools.simple_browser import SimpleBrowserTool
            from gpt_oss.tools.simple_browser.backend import ExaBackend

            backend = ExaBackend(source="web")
            self.browser_tool = SimpleBrowserTool(backend=backend)
        if enable_python:
            from gpt_oss.tools.python_docker.docker_tool import PythonTool

            self.python_tool = PythonTool()

    # ---- helpers -----------------------------------------------------
    def _system_message(self):
        content = (
            self.SystemContent.new()
            .with_reasoning_effort(
                self.REASONING_EFFORT.get(
                    self.reasoning_effort, self.ReasoningEffort.LOW
                )
            )
            .with_conversation_start_date(datetime.datetime.now().strftime("%Y-%m-%d"))
        )
        if self.browser_tool:
            content = content.with_tools(self.browser_tool.tool_config)
        if self.python_tool:
            content = content.with_tools(self.python_tool.tool_config)
        return self.Message.from_role_and_content(self.Role.SYSTEM, content)

    async def _run_browser(self, msg: Message) -> List[Message]:
        assert self.browser_tool is not None
        results: List[Message] = []
        async for out in self.browser_tool.process(msg):
            results.append(out)
        return results

    async def _run_python(self, msg: Message) -> List[Message]:
        assert self.python_tool is not None
        results: List[Message] = []
        async for out in self.python_tool.process(msg):
            results.append(out)
        return results

    def _dispatch_tool(self, msg: Message) -> List[Message]:
        if msg.recipient and msg.recipient.startswith("browser.") and self.browser_tool:
            return asyncio.run(self._run_browser(msg))
        if msg.recipient and msg.recipient.startswith("python") and self.python_tool:
            return asyncio.run(self._run_python(msg))
        # Tool not enabled - send error back to assistant
        error = self.Message(
            author=self.Author.new(self.Role.TOOL, msg.recipient or ""),
            content=[self.TextContent(text="Tool not available")],
        ).with_recipient("assistant")
        return [error]

    def _token_generator(
        self, tokens: List[int], stop: List[int], max_new_tokens: Optional[int]
    ):
        new_request = True
        produced = 0
        while True:
            if max_new_tokens is not None and produced >= max_new_tokens:
                break
            next_tok = self._infer_next_token(
                tokens, temperature=0.0, new_request=new_request
            )
            new_request = False
            tokens.append(next_tok)
            yield next_tok
            produced += 1
            if next_tok in stop:
                break

    # ---- public API --------------------------------------------------
    def generate(
        self,
        prompt: str,
        n: int = 1,
        *,
        max_new_tokens: Optional[int] = None,
        **gen_kwargs,
    ) -> List[str]:
        # When running with the stub backend there is no tokenization or
        # streaming. Return a deterministic placeholder so higher-level
        # logic can be exercised without the full model stack.
        if self.encoding is None:
            return ["This is a demo response from the OSS provider stub."] * n

        outputs: List[str] = []
        for _ in range(n):
            messages: List[Any] = [
                self._system_message(),
                self.Message.from_role_and_content(
                    self.Role.DEVELOPER, self.DeveloperContent.new()
                ),
                self.Message.from_role_and_content(self.Role.USER, prompt),
            ]
            remaining = max_new_tokens
            while True:
                conversation = self.Conversation.from_messages(messages)
                tokens = self.encoding.render_conversation_for_completion(
                    conversation, self.Role.ASSISTANT
                )
                parser = self.StreamableParser(self.encoding, role=self.Role.ASSISTANT)
                produced = 0
                for tok in self._token_generator(
                    tokens,
                    self.encoding.stop_tokens_for_assistant_actions(),
                    remaining,
                ):
                    parser.process(tok)
                    produced += 1
                messages.extend(parser.messages)
                last = messages[-1]
                if last.recipient is None or (
                    remaining is not None and remaining - produced <= 0
                ):
                    outputs.append(last.content[0].text)
                    break
                remaining = None if remaining is None else remaining - produced
                tool_msgs = self._dispatch_tool(last)
                messages.extend(tool_msgs)
        return outputs
