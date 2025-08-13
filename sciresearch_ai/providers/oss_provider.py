from __future__ import annotations
import datetime
import asyncio
from typing import List, Optional

from openai_harmony import (
    Author,
    Conversation,
    DeveloperContent,
    HarmonyEncodingName,
    Message,
    Role,
    SystemContent,
    TextContent,
    StreamableParser,
    load_harmony_encoding,
    ReasoningEffort,
)

from gpt_oss.tools.simple_browser import SimpleBrowserTool
from gpt_oss.tools.simple_browser.backend import ExaBackend
from gpt_oss.tools.python_docker.docker_tool import PythonTool
from gpt_oss.responses_api.inference.transformers import setup_model as _setup_transformers


REASONING_EFFORT = {
    "high": ReasoningEffort.HIGH,
    "medium": ReasoningEffort.MEDIUM,
    "low": ReasoningEffort.LOW,
}


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
        # transformers-based incremental generator
        self._infer_next_token = _setup_transformers(self.checkpoint, device=device)
        self.encoding = load_harmony_encoding(HarmonyEncodingName.HARMONY_GPT_OSS)
        self.reasoning_effort = reasoning_effort
        self.enable_browser = enable_browser
        self.enable_python = enable_python
        self.browser_tool: Optional[SimpleBrowserTool] = None
        self.python_tool: Optional[PythonTool] = None
        if enable_browser:
            backend = ExaBackend(source="web")
            self.browser_tool = SimpleBrowserTool(backend=backend)
        if enable_python:
            self.python_tool = PythonTool()

    # ---- helpers -----------------------------------------------------
    def _system_message(self) -> Message:
        content = (
            SystemContent.new()
            .with_reasoning_effort(REASONING_EFFORT.get(self.reasoning_effort, ReasoningEffort.LOW))
            .with_conversation_start_date(datetime.datetime.now().strftime("%Y-%m-%d"))
        )
        if self.browser_tool:
            content = content.with_tools(self.browser_tool.tool_config)
        if self.python_tool:
            content = content.with_tools(self.python_tool.tool_config)
        return Message.from_role_and_content(Role.SYSTEM, content)

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
        error = Message(
            author=Author.new(Role.TOOL, msg.recipient or ""),
            content=[TextContent(text="Tool not available")],
        ).with_recipient("assistant")
        return [error]

    def _token_generator(self, tokens: List[int], stop: List[int], max_new_tokens: Optional[int]):
        new_request = True
        produced = 0
        while True:
            if max_new_tokens is not None and produced >= max_new_tokens:
                break
            next_tok = self._infer_next_token(tokens, temperature=0.0, new_request=new_request)
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
        outputs: List[str] = []
        for _ in range(n):
            messages: List[Message] = [
                self._system_message(),
                Message.from_role_and_content(Role.DEVELOPER, DeveloperContent.new()),
                Message.from_role_and_content(Role.USER, prompt),
            ]
            remaining = max_new_tokens
            while True:
                conversation = Conversation.from_messages(messages)
                tokens = self.encoding.render_conversation_for_completion(conversation, Role.ASSISTANT)
                parser = StreamableParser(self.encoding, role=Role.ASSISTANT)
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
                if last.recipient is None or (remaining is not None and remaining - produced <= 0):
                    outputs.append(last.content[0].text)
                    break
                remaining = None if remaining is None else remaining - produced
                tool_msgs = self._dispatch_tool(last)
                messages.extend(tool_msgs)
        return outputs
