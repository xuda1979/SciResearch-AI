from __future__ import annotations
import datetime
import os
import shutil
from pathlib import Path

from .project_fs import ProjectFS

class PaperWriter:
    def __init__(self, fs: ProjectFS):
        self.fs = fs
        self.draft_path = self.fs.get_path("paper/draft.tex")
        if not self.draft_path.exists():
            self.fs.write("paper/draft.tex", DEFAULT_TEX)

    def autosave(self, content: str) -> Path:
        """Atomically writes content to the draft and creates a checkpoint."""
        # Atomic write
        tmp_path = self.draft_path.with_suffix(".tex.tmp")
        tmp_path.write_text(content, encoding="utf-8")
        os.replace(tmp_path, self.draft_path)

        # Checkpoint snapshot
        now = datetime.datetime.now(datetime.timezone.utc)
        ts = now.strftime("%Y%m%d-%H%M%S") + f"-{int(now.microsecond/1000):03d}"
        snap_name = f"draft-{ts}.tex"
        snap_path = self.fs.rev_dir / snap_name
        shutil.copy2(self.draft_path, snap_path)
        return snap_path

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
