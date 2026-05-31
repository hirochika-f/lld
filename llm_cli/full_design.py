from abc import abstractmethod
from collections.abc import Iterator
from dataclasses import dataclass
from enum import StrEnum
from openai import OpenAI
from pathlib import Path
from textwrap import dedent
from typing import Protocol
import asyncio
import json

from llm_cli.tools import ListDir, ToolCall, ToolDispatcher, ToolRegistry, ToolResult, ToolValidator


@dataclass
class TextEvent:
    text: str


@dataclass
class ToolCallsEvent:
    tool_calls: list[ToolCall]


class Role(StrEnum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


@dataclass
class Message:
    role: Role
    content: str
    tool_call_id: str | None = None
    tool_calls: list[ToolCall] | None = None


class ConfigManager:
    def __init__(self, config_path="~/.llm-cli.json"):
        path = Path(config_path).expanduser()
        with open(path, "r") as f:
            config = json.load(f)
            self.api_key = config["apiKey"]
            self.model = config["model"]


class ChatSession:
    def __init__(self, system_message: str):
        self.messages: list[Message] = []
        system_prompt = Message(
            role=Role.SYSTEM,
            content=system_message
        )
        self.messages.append(system_prompt)

    def add_user_message(self, user_message: str):
        prompt = Message(
            role=Role.USER,
            content=user_message
        )
        self.messages.append(prompt)

    def add_assistant_message(self, assistant_message: str):
        prompt = Message(
            role=Role.ASSISTANT,
            content=assistant_message
        )
        self.messages.append(prompt)

    def add_assistant_tool_calls(self, tool_calls: list[ToolCall]):
        message = Message(
            role=Role.ASSISTANT,
            content="",
            tool_calls=tool_calls
        )
        self.messages.append(message)

    def add_tool_result(self, tool_result: ToolResult):
        tool_message = Message(
            role=Role.TOOL,
            content=tool_result.content,
            tool_call_id=tool_result.call_id
        )
        self.messages.append(tool_message)

    def get_messages(self) -> list[Message]:
        return self.messages

    def cutoff(self):
        # TODO: implement cutoff messages to fit context window
        pass


class LlmProvider(Protocol):
    def stream(self, messages: list[Message]) -> Iterator[TextEvent | ToolCallsEvent]:
        ...


class OpenAiClient:
    def __init__(self, config, tool_registry):
        self.config = config
        self.client = OpenAI(api_key=self.config.api_key)
        self.registry = tool_registry

    def _convert_messages(self, messages: list[Message]) -> list[dict[str, str]]:
        dict_messages = []
        for msg in messages:
            item = {
                "role": msg.role.value,
                "content": msg.content,
            }
            if msg.tool_call_id:
                item["tool_call_id"] = msg.tool_call_id
            if msg.tool_calls:
                item["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.name,
                            "arguments": json.dumps(tc.args)
                        }
                    }
                    for tc in msg.tool_calls
                ]
            dict_messages.append(item)
        return dict_messages

    def stream(self, messages: list[Message]) -> Iterator[TextEvent | ToolCallsEvent]:
        messages = self._convert_messages(messages)
        stream_response = self.client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            tools=self.registry.get_tool_definitions(),
            stream=True
        )
        tool_calls = {}
        for chunk in stream_response:
            delta = chunk.choices[0].delta
            if delta.content:
                yield TextEvent(delta.content) 
            elif delta.tool_calls:
                for tc in delta.tool_calls:
                    idx = tc.index
                    if idx not in tool_calls:
                        tool_calls[idx] = {
                            "id": tc.id,
                            "name": tc.function.name,
                            "arguments": ""
                        }
                    entry = tool_calls[idx]
                    if tc.id:
                        entry["id"] = tc.id
                    if tc.function.name:
                        entry["name"] = tc.function.name
                    tool_calls[idx]["arguments"] += tc.function.arguments or ""
        if tool_calls:
            tool_calls_list = []
            for v in tool_calls.values():
                args = json.loads(v["arguments"])
                tool_calls_list.append(ToolCall(id=v["id"], name=v["name"], args=args))
            yield ToolCallsEvent(tool_calls_list)


class CliApp:
    def __init__(self, client, session, dispatcher):
        self.client = client
        self.session = session
        self.dispatcher = dispatcher

    async def start(self):
        while True:
            user_input = input("You: ")

            if user_input == "exit":
                print("BYE!")
                break

            self.session.add_user_message(user_input)
            assistant_response = ""
            tool_calls = None

            for event in self.client.stream(self.session.get_messages()):
                if isinstance(event, TextEvent):
                    print(event.text, end="", flush=True)
                    assistant_response += event.text
                elif isinstance(event, ToolCallsEvent):
                    tool_calls = event.tool_calls

            if tool_calls is None:
                self.session.add_assistant_message(assistant_response)
            else:
                self.session.add_assistant_tool_calls(tool_calls)
                tool_results = await self.dispatcher.dispatch(tool_calls)
                for tool_result in tool_results:
                    self.session.add_tool_result(tool_result)
                for event in self.client.stream(self.session.get_messages()):
                    if isinstance(event, TextEvent):
                        print(event.text, end="", flush=True)
                        assistant_response += event.text
                    else:
                        # only one tool calling round supported
                        raise ValueError("Chained tool callings.")
                self.session.add_assistant_message(assistant_response)
                print()


async def main():
    registry = ToolRegistry()
    registry.register(ListDir())

    validator = ToolValidator()
    dispatcher = ToolDispatcher(registry, validator)

    client = OpenAiClient(ConfigManager(), registry)

    session = ChatSession("You are a CLI assistant.")

    app = CliApp(client, session, dispatcher)
    await app.start()


if __name__ == "__main__":
    asyncio.run(main())

