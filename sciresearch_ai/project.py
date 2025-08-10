from __future__ import annotations
import os, datetime, json
from typing import Dict, Any

from .paper.manager import PaperManager

class Project:
    def __init__(self, root: str):
        self.root = os.path.abspath(root)
        os.makedirs(self.root, exist_ok=True)
        self.pm = PaperManager(self.root)

    @staticmethod
    def create(root: str, name: str) -> "Project":
        base = os.path.join(root, "projects", name)
        os.makedirs(base, exist_ok=True)
        return Project(base)
