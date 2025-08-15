from typing import NamedTuple, Type, List
from .tool import Tool
from .python_exec_tool import PythonExecTool
from .sym_eq_tool import SymEqTool
from .proj_file_tools import WriteProjectFileTool, ListProjectFilesTool

class ToolSpec(NamedTuple):
    """A specification for a tool."""
    name: str
    description: str
    tool_class: Type[Tool]

ALL_TOOLS: List[ToolSpec] = [
    ToolSpec(
        name="python_exec",
        description="Executes Python code in a sandboxed Docker container.",
        tool_class=PythonExecTool,
    ),
    ToolSpec(
        name="symbolic_equality",
        description="Checks if two mathematical expressions are symbolically equal.",
        tool_class=SymEqTool,
    ),
    ToolSpec(
        name="write_project_file",
        description="Writes content to a file in the project directory.",
        tool_class=WriteProjectFileTool,
    ),
    ToolSpec(
        name="list_project_files",
        description="Lists all files in the project directory.",
        tool_class=ListProjectFilesTool,
    ),
]

def get_tool_spec(name: str) -> ToolSpec | None:
    """Get a tool spec by name."""
    for spec in ALL_TOOLS:
        if spec.name == name:
            return spec
    return None
