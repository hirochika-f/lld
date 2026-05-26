from dataclasses import dataclass
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


class Tool(Protocol):
    name: str
    description: str
    schema: dict[str, Any]

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



