from typing import Any, Protocol
from dataclasses import dataclass
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


class Tool(Protocol):
    name: str
    description: str
    schema: dict[str, Any]

    async def execute(self, args: dict[str, Any]) -> str:
        pass


class GetWeatherTool:
    def __init__(self):
        self.name = "get_weather"
        self.description = "Get the current weather for a given location."
        self.schema = {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state."
                },
                "unit": {
                    "type": "string",
                    "description": "The temperature unit."
                },
            },
            "required": ["location"]
        }

    async def execute(self, args: dict[str, Any]) -> str:
        location = args.get("location", "")
        unit = args.get("unit", "celcius")

        await asyncio.sleep(0.5)

        if "tokyo" == location.lower():
            response = {
                "location": location,
                "temperature": 25,
                "unit": unit,
                "condition": "Sunny"
            }
        elif "london" == location.lower():
             response = {
                "location": location,
                "temperature": 10,
                "unit": unit,
                "condition": "Rainy"
            }
        else:
            raise ValueError(f"Invalid location: {location}")
        return f"{response}"


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


if __name__ == "__main__":
    registry = ToolRegistry()
    registry.register(GetWeatherTool())
    validator = ToolValidator()
    dispatcher = ToolDispatcher(registry, validator)

    llm_calls = [
        ToolCall("call_1", "get_weather", {"location": "tokyo", "unit": "celcius"}),
        ToolCall("call_2", "get_weather", {"location": "london"}),
        ToolCall("call_3", "get_weather", {"location": "unknown"}),
        ToolCall("call_4", "get_weather", {}),
        ToolCall("call_5", "", {})
    ]

    async def main():
        results = await dispatcher.dispatch(llm_calls)
        for r in results:
            print(f"{r.call_id}, {r.success}", end="")
            print(f"{r.content}")
            print("-" * 10)

    asyncio.run(main())

