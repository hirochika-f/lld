from dataclasses import dataclass
from typing import Any, Protocol
from pathlib import Path
import asyncio

@dataclass
class ToolCall:
    id: str
    name: str
    args: dict[str, Any]


@dataclass
class ToolResult:
    call_id: str
    success: bool
    content: str


@dataclass
class ToolCallsEvent:
    tool_calls: list[ToolCall]


class Tool(Protocol):
    name: str
    description: str
    schema: dict[str, Any]
    definition: dict[str, str]

    async def execute(self, args: dict[str, Any]) -> str:
        pass


class ListDir:
    def __init__(self):
        self.name = "list_dir"
        self.description = "Get the files in the directory."
        self.schema = {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Absolute path."
                }
            },
            "required": ["path"]
        }
        self.definition = {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.schema
            }
        }

    async def execute(self, args: dict[str, Any]) -> str:
        path = args.get("path", "")

        await asyncio.sleep(0.5)

        if path is None:
            raise ValueError(f"Invalid location: {location}")

        path = Path(path)
        file_list = [str(p) for p in path.iterdir()]
        response = {
            "files": ' '.join(file_list)
        }
        return f"{response}"

    def get_definition(self) -> dict[str, str]:
        return self.definition


class ToolRegistry:
    def __init__(self):
        self.tools = {}

    def register(self, tool: Tool) -> bool:
        name = tool.name
        if name in self.tools:
            raise ValueError(f"Tool {name} is already resistered.")
        self.tools[name] = tool

    def get_tool(self, name: str) -> Tool:
        if name not in self.tools:
            raise ValueError(f"Not found tool: {name}")
        return self.tools[name]

    def get_tool_definitions(self) -> dict[str, Any]:
        return [
            t.get_definition() for t in self.tools.values()
        ]


class ToolValidator:
    def validate(self, tool: Tool, call: ToolCall) -> dict[str, Any]:
        self._validate_tool_exists(tool)
        self._validate_required_fields(tool, call.args)
        self._validate_types(tool, call.args)
        return call.args

    def _validate_tool_exists(self, tool):
        if tool is None:
            raise ValueError(f"Tool not found: {call.name}")

    def _validate_required_fields(self, tool, args):
        required = tool.schema.get("required", [])
        missing = [key for key in required if key not in args]
        if missing:
            raise ValueError(f"Missing fields: {missing}")

    def _validate_types(self, tool, args):
        props = tool.schema.get("properties", {})
        for k, v in args.items():
            if k not in props:
                continue
            expected_type = props[k].get("type")
            if expected_type == "string" and not isinstance(v, str):
                raise ValueError(f"{k} must be string")


class ToolDispatcher:
    def __init__(self, registry: ToolRegistry, validator: ToolValidator):
        self.registry = registry
        self.validator = validator

    async def dispatch(self, calls: list[ToolCall]) -> list[ToolResult]:
        tasks = [
            asyncio.create_task(self._execute(call)) for call in calls
        ]
        return await asyncio.gather(*tasks)

    async def _execute(self, call: ToolCall) -> ToolResult:
        try:
            tool = self.registry.get_tool(call.name)
            args = self.validator.validate(tool, call)
            result = await tool.execute(args)
            return ToolResult(
                call_id=call.id,
                success=True,
                content=result
            )
        except Exception as e:
            return ToolResult(
                call_id=call.id,
                success=False,
                content=f"Execution Error: {str(e)}"
            )

