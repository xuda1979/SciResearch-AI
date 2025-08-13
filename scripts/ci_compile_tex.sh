#!/usr/bin/env bash
set -euo pipefail
pdflatex -interaction=nonstopmode paper/draft.tex >/tmp/pdflatex.log || { cat /tmp/pdflatex.log; exit 1; }
tail -n 20 /tmp/pdflatex.log
