from collections.abc import Iterator
from enum import StrEnum
from dataclasses import dataclass
from openai import OpenAI
from pathlib import Path
from typing import Protocol
import json


class ConfigManager:
    def __init__(self, config_path="~/.llm-cli.json"):
        path = Path(config_path).expanduser()
        with open(path, "r") as f:
            config = json.load(f)
            self.api_key = config["apiKey"]
            self.model = config["model"]


class Role(StrEnum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class Message:
    role: Role
    content: str


class ChatSession:
    def __init__(self, system_prompt: str) -> None:
        self.messages: list[Message] = []
        system_message = Message(
            role=Role.SYSTEM,
            content=system_prompt
        )
        self.messages.append(system_message)

    def add_message(self, role: Role, content: str) -> None:
        message = Message(
            role=role,
            content=content
        )
        self.messages.append(message)

    def get_messages(self) -> list[Message]:
        return self.messages

    def convert_messages(self) -> list[dict[str, str]]:
        raw_messages = []
        for message in self.messages:
            dict_message = {
                "role": message.role.value,
                "content": message.content
            }
            raw_messages.append(dict_message)
        return raw_messages


class LlmProvider(Protocol):
    def stream(self):
        pass


class OpenAiClient:
    def __init__(self, config: ConfigManager):
        self.config = config
        self.client = OpenAI(api_key=self.config.api_key)

    def stream(self, raw_messages: list[dict[str, str]]) -> Iterator[str]:
        stream_response = self.client.chat.completions.create(
            model = self.config.model,
            messages=raw_messages,
            stream=True
        )
        for chunk in stream_response:
            content = chunk.choices[0].delta.content
            if content is not None:
                yield content


class CliApp:
    def __init__(self, client: LlmProvider, session: ChatSession):
        self.client = client
        self.session = session

    def run(self):
        while True:
            user_input = input("You: ")
            if user_input == "Bye":
                print("BYE!")
                break

            assistant_message = ""
            self.session.add_message(Role.USER, user_input)
            for event in self.client.stream(self.session.convert_messages()):
                print(event, end="", flush=True)
                assistant_message += event
            self.session.add_message(Role.ASSISTANT, assistant_message)
            print()


if __name__ == "__main__":
    config = ConfigManager()
    client = OpenAiClient(config)
    session = ChatSession("You are a CLI assistant.")
    app = CliApp(client, session)
    app.run()
