from abc import abstractmethod
from collections.abc import Iterator
from enum import StrEnum
from openai import OpenAI
from pathlib import Path
from textwrap import dedent
from typing import Protocol
import json

from llm_cli.tools import ListDir, ToolCall, ToolRegistry, ToolResult

SYSTEM_PROMPT = """
You are an CLI assistant.
You can use a tool as below
  1. ListDir tool: to list the files and folders in the directory user passed.
"""

class Role(StrEnum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class ConfigManager:
    def __init__(self, config_path="~/.llm-cli.json"):
        path = Path(config_path).expanduser()
        with open(path, "r") as f:
            config = json.load(f)
            self.api_key = config["apiKey"]
            self.model = config["model"]


class ChatSession:
    def __init__(self, system_message: str):
        self.messages: list[dict[str, str]] = []
        system_prompt = {
            "role": Role.SYSTEM,
            "content": system_message
        }
        self.messages.append(system_prompt)

    def add_user_message(self, user_message: str):
        prompt = {
            "role": Role.USER,
            "content": user_message
        }
        self.messages.append(prompt)

    def add_assistant_message(self, assistant_message: str):
        prompt = {
            "role": Role.ASSISTANT,
            "content": assistant_message
        }
        self.messages.append(prompt)

    def get_messages(self) -> list:
        return self.messages

    def cutoff(self):
        # TODO: implement cutoff messages to fit context window
        pass


class LlmProvider(Protocol):
    def stream(self, messages: list[dict[str, str]]) -> Iterator[str]:
        ...


class OpenAiClient:
    def __init__(self, config, tool_registry):
        self.config = config
        self.client = OpenAI(api_key=self.config.api_key)
        self.registry = tool_registry

    def stream(self, messages: list[dict[str, str]]) -> Iterator[str]:
        stream_response = self.client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            tools=self.registry.get_tool_definitions(),
            stream=True
        )
        for chunk in stream_response:
            content = chunk.choices[0].delta.content
            if content:
                yield content


class CliApp:
    def __init__(self, client, session):
        self.client = client
        self.session = session

    def start(self):
        while True:
            user_input = input("You: ")

            if user_input == "exit":
                break
            self.session.add_user_message(user_input)
            assistant_response = self._construct_assistant_message(
                self.client.stream(self.session.get_messages())
            )
            self.session.add_assistant_message(assistant_response)

    def _construct_assistant_message(self, content: Iterator[str]):
        assistant_response = ""
        for token in content:
            print(token, end="", flush=True)
            assistant_response += token
        print()
        return assistant_response
 

if __name__ == "__main__":
    tool_registry = ToolRegistry()
    tool_registry.register(ListDir())
    client = OpenAiClient(ConfigManager(), tool_registry)
    session = ChatSession(SYSTEM_PROMPT)
    app = CliApp(client, session)
    app.start()

