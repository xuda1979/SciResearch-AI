import os
from typing import List


class WriteProjectFileTool:
    """A tool for writing to project files."""

    def __init__(self, base_dir: str = "project_files"):
        self.base_dir = base_dir
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)

    @property
    def name(self) -> str:
        return "write_project_file"

    @property
    def description(self) -> str:
        return "Writes content to a file in the project directory."

    async def __call__(self, filepath: str, content: str) -> str:
        """Write content to the given filepath."""
        if ".." in filepath:
            return "Error: Filepath cannot contain '..'"

        full_path = os.path.join(self.base_dir, filepath)
        try:
            with open(full_path, "w") as f:
                f.write(content)
            return f"Successfully wrote to {filepath}"
        except Exception as e:
            return f"Error writing to file: {e}"


class ListProjectFilesTool:
    """A tool for listing project files."""

    def __init__(self, base_dir: str = "project_files"):
        self.base_dir = base_dir
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)

    @property
    def name(self) -> str:
        return "list_project_files"

    @property
    def description(self) -> str:
        return "Lists all files in the project directory."

    async def __call__(self) -> List[str]:
        """List all files in the project directory."""
        try:
            files = []
            for dirpath, _, filenames in os.walk(self.base_dir):
                for filename in filenames:
                    relative_path = os.path.relpath(
                        os.path.join(dirpath, filename), self.base_dir
                    )
                    files.append(relative_path)
            return files
        except Exception as e:
            return [f"Error listing files: {e}"]
