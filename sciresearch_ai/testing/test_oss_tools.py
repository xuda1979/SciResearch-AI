from __future__ import annotations

import sys
import types

import pytest

# Stub heavy optional deps before importing the provider
class _Role:
    SYSTEM = "system"
    DEVELOPER = "developer"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class _Author:
    @staticmethod
    def new(role, name=""):
        return types.SimpleNamespace(role=role, name=name)


class _TextContent:
    def __init__(self, text: str):
        self.text = text


class _Message:
    def __init__(self, author, content, recipient=None):
        self.author = author
        self.content = content if isinstance(content, list) else [content]
        self.recipient = recipient

    @classmethod
    def from_role_and_content(cls, role, content):
        if isinstance(content, str):
            content = [_TextContent(content)]
        return cls(_Author.new(role), content)

    def with_recipient(self, recipient):
        self.recipient = recipient
        return self


class _SystemContent:
    @classmethod
    def new(cls):
        return cls()

    def with_reasoning_effort(self, effort):
        return self

    def with_conversation_start_date(self, date):
        return self

    def with_tools(self, tool_config):
        return self


class _DeveloperContent:
    @classmethod
    def new(cls):
        return cls()


class _Conversation:
    @staticmethod
    def from_messages(msgs):
        return msgs


class _HarmonyEncodingName:
    HARMONY_GPT_OSS = "harmony_gpt_oss"


def _load_harmony_encoding(name):  # pragma: no cover - replaced in tests
    return None


class _StreamableParser:  # pragma: no cover - replaced in tests
    def __init__(self, encoding, role):
        self.messages = []

    def process(self, tok):
        pass


class _ReasoningEffort:
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


sys.modules.setdefault(
    "openai_harmony",
    types.SimpleNamespace(
        Author=_Author,
        Message=_Message,
        Role=_Role,
        TextContent=_TextContent,
        SystemContent=_SystemContent,
        DeveloperContent=_DeveloperContent,
        Conversation=_Conversation,
        HarmonyEncodingName=_HarmonyEncodingName,
        load_harmony_encoding=_load_harmony_encoding,
        StreamableParser=_StreamableParser,
        ReasoningEffort=_ReasoningEffort,
    ),
)

sys.modules.setdefault(
    "gpt_oss.tools.simple_browser",
    types.SimpleNamespace(SimpleBrowserTool=object),
)
sys.modules.setdefault(
    "gpt_oss.tools.simple_browser.backend",
    types.SimpleNamespace(ExaBackend=object),
)
sys.modules.setdefault(
    "gpt_oss.tools.python_docker.docker_tool",
    types.SimpleNamespace(PythonTool=object),
)
sys.modules.setdefault(
    "gpt_oss.responses_api.inference.transformers",
    types.SimpleNamespace(
        setup_model=lambda checkpoint, device=None: (lambda tokens, temperature, new_request: 0)
    ),
)

import sciresearch_ai.providers.oss_provider as op
from sciresearch_ai.providers.oss_provider import OssProvider
from openai_harmony import Author, Message, Role, TextContent


class DummyTool:
    def __init__(self, reply: str):
        self.reply = reply
        self.tool_config = types.SimpleNamespace(name="dummy")

    async def process(self, msg: Message):
        yield Message(
            author=Author.new(Role.TOOL, msg.recipient or ""),
            content=[TextContent(text=self.reply)],
        ).with_recipient("assistant")


def setup_fake_model(monkeypatch, messages_seq):
    class FakeEncoding:
        def render_conversation_for_completion(self, conversation, role):
            return [0]

        def stop_tokens_for_assistant_actions(self):
            return [0]

    class FakeParser:
        def __init__(self, encoding, role):
            self.messages = []

        def process(self, tok):
            self.messages = messages_seq.pop(0)

    monkeypatch.setattr(op, "load_harmony_encoding", lambda _: FakeEncoding())
    monkeypatch.setattr(op, "StreamableParser", FakeParser)
    monkeypatch.setattr(
        op,
        "_setup_transformers",
        lambda checkpoint, device=None: (lambda tokens, temperature, new_request: 0),
    )


def test_browser_tool_routing(monkeypatch):
    msgs = [
        [
            Message.from_role_and_content(Role.ASSISTANT, TextContent(text="q"))
            .with_recipient("browser.search")
        ],
        [Message.from_role_and_content(Role.ASSISTANT, "tool result")],
    ]
    setup_fake_model(monkeypatch, msgs)
    prov = OssProvider()
    prov.browser_tool = DummyTool("tool result")
    out = prov.generate("hi")[0]
    assert out == "tool result"


def test_python_tool_routing(monkeypatch):
    msgs = [
        [
            Message.from_role_and_content(Role.ASSISTANT, TextContent(text="code"))
            .with_recipient("python")
        ],
        [Message.from_role_and_content(Role.ASSISTANT, "py result")],
    ]
    setup_fake_model(monkeypatch, msgs)
    prov = OssProvider()
    prov.python_tool = DummyTool("py result")
    out = prov.generate("hi")[0]
    assert out == "py result"
