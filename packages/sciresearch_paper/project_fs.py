from __future__ import annotations
import os
from pathlib import Path
from typing import List

class ProjectFS:
    def __init__(self, project_name: str, projects_dir: Path = Path("./projects")):
        self.project_name = project_name
        self.root = projects_dir / project_name
        self.root.mkdir(parents=True, exist_ok=True)

        self.paper_dir = self.root / "paper"
        self.fig_dir = self.root / "figures"
        self.code_dir = self.root / "code"
        self.data_dir = self.root / "data"
        self.notes_dir = self.root / "notes"
        self.logs_dir = self.root / "logs"
        self.rev_dir = self.root / "revisions"

        for d in [self.paper_dir, self.fig_dir, self.code_dir, self.data_dir, self.notes_dir, self.logs_dir, self.rev_dir]:
            d.mkdir(exist_ok=True)

    def read(self, file_path: str) -> str:
        """Reads a file from the project."""
        full_path = self.root / file_path
        if not full_path.is_file():
            raise FileNotFoundError(f"File not found: {full_path}")
        return full_path.read_text(encoding="utf-8")

    def write(self, file_path: str, content: str) -> None:
        """Writes content to a file in the project."""
        full_path = self.root / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content, encoding="utf-8")

    def list_files(self, sub_dir: str = ".") -> List[str]:
        """Lists files in a subdirectory of the project."""
        target_dir = self.root / sub_dir
        if not target_dir.is_dir():
            return []

        files: List[str] = []
        for item in target_dir.iterdir():
            files.append(item.name)
        return files

    def get_path(self, file_path: str) -> Path:
        """Gets the full path for a file in the project."""
        return self.root / file_path
