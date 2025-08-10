from __future__ import annotations
import os, json, shutil, time, datetime
from typing import Dict, Any

class PaperManager:
    def __init__(self, root: str):
        self.root = os.path.abspath(root)
        self.paper_dir = os.path.join(self.root, "paper")
        self.fig_dir = os.path.join(self.root, "figures")
        self.code_dir = os.path.join(self.root, "code")
        self.data_dir = os.path.join(self.root, "data")
        self.notes_dir = os.path.join(self.root, "notes")
        self.logs_dir = os.path.join(self.root, "logs")
        self.rev_dir = os.path.join(self.root, "revisions")
        os.makedirs(self.paper_dir, exist_ok=True)
        for d in [self.fig_dir, self.code_dir, self.data_dir, self.notes_dir, self.logs_dir, self.rev_dir]:
            os.makedirs(d, exist_ok=True)
        self.state_path = os.path.join(self.root, "state.json")
        self.draft_path = os.path.join(self.paper_dir, "draft.tex")
        if not os.path.exists(self.draft_path):
            with open(self.draft_path, "w", encoding="utf-8") as f:
                f.write(DEFAULT_TEX)

    def autosave(self, content: str) -> None:
        # atomic write
        tmp = self.draft_path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(content)
        os.replace(tmp, self.draft_path)
        # checkpoint snapshot
        now = datetime.datetime.now(); ts = now.strftime("%Y%m%d-%H%M%S") + f"-{int(now.microsecond/1000):03d}"
        snap = os.path.join(self.rev_dir, f"draft-{ts}.tex")
        shutil.copy2(self.draft_path, snap)

    def log(self, text: str) -> None:
        ts = time.strftime("%Y%m%d-%H%M%S")
        path = os.path.join(self.logs_dir, f"run-{ts}.log")
        with open(path, "a", encoding="utf-8") as f:
            f.write(text + "\n")

    def save_state(self, state: Dict[str, Any]) -> None:
        tmp = self.state_path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
        os.replace(tmp, self.state_path)

DEFAULT_TEX = r"""\documentclass{article}
\usepackage{graphicx}
\usepackage{amsmath, amssymb}
\title{Automated Research Draft}
\author{SciResearch-AI}
\date{\today}
\begin{document}
\maketitle

\begin{abstract}
This is an auto-generated abstract. Replace with your research summary.
\end{abstract}

\section{Introduction}
This is a placeholder introduction.

\section{Methods}
TBD.

\section{Experiments}
TBD.

\section{Results}
TBD.

\section{Discussion}
TBD.

\bibliographystyle{plain}
\bibliography{refs}
\end{document}
"""
