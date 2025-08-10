<<<<<<< HEAD
# SciResearch-AI (Reasoning CLI for Scientific Papers)

SciResearch-AI automates a **human-like research loop** with **test-time compute (TTC)**, **multi-agent debate**, and **reflection**. It writes and revises a LaTeX paper in a project folder, saving **atomic autosaves** and **timestamped checkpoints** after every edit. You can pause any time to steer or stop.

## Why this matters
Recent systems (e.g., OpenAI's reasoning models and Google's 'deep thinking' results) highlight that **longer, structured inference** at runtime (not just bigger models) significantly improves reliability. This project exposes those **TTC dials** (samples, strategies, consensus) and bakes in verification hooks. It also supports **function/tool calls** the GPT‑5 family can use, and can optionally enable the **server‑side Code Interpreter** tool.

---

## Features at a glance
- **End-to-end project layout per paper**
  - `paper/` (LaTeX), `figures/`, `code/`, `data/`, `notes/`, `logs/`, `revisions/`
- **Autosave + Checkpoints** on every change
- **SOTA inference-time strategies:**
  - Self-consistency (Best-of-N) voting
  - **Budgeted Adaptive Deliberation (BAD)**: *new* margin-based early stop for TTC
  - Multi-agent **Debate → Consensus**
  - **Critique → Revise** reflection loop
- **Human-in-the-loop:** inject guidance or stop after each iteration
- **OpenAI Responses API** integration with:
  - Optional GPT‑5 **Code Interpreter** tool (`--enable-code-interpreter`)
  - **Function tools** the model can call:
    - `run_python(code)` — quick local execution (no network)
    - `check_symbolic_equality(expr1, expr2)` — SymPy-backed check
    - `write_project_file(relative_path, content)` — create/edit files
    - `list_project_files(relative_path)` — list files in a subfolder
- **Configurable budgets:** iterations, TTC samples, time budget, parallelism
- **Offline** Mock provider for tests

---

## Installation (Windows PowerShell)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Environment
- To use OpenAI: set `OPENAI_API_KEY` and choose an available GPT‑5‑family model ID.
  ```powershell
  $env:OPENAI_API_KEY="sk-..."
  ```

---

## Quick Start
```powershell
# Create a project
python -m sciresearch_ai.main new --name "my_paper" --root .

# Offline smoke run (mock LLM)
python -m sciresearch_ai.main run --project .\projects\my_paper --provider mock --max-iterations 2

# Real run (OpenAI)
python -m sciresearch_ai.main run --project .\projects\my_paper `
  --provider openai `
  --model gpt-5-chat-latest `
  --max-iterations 5 `
  --samples-per-query 6 `
  --time-budget-sec 1800 `
  --reasoning-effort high `
  --temperature 0.2 --top_p 0.9 --max-output-tokens 2000 `
  --enable-code-interpreter   # optional tool
```

**Human control:** after each iteration, press **Enter** to continue, type text to guide, or type **stop** to end.

---

## Project layout
```text
projects/<name>/
  paper/draft.tex
  figures/
  code/
  data/
  notes/
  logs/run-YYYYmmdd-HHMMSS.log
  revisions/draft-YYYYmmdd-HHMMSS.tex
  state.json
```

---

## How it works (algorithmic loop)
1. **Plan** — propose a concise objective and milestones
2. **TTC** — expand into an experiment protocol with pseudocode using:
   - Self-consistency or **BAD** (samples per query = TTC)
3. **Debate** — multi-agent critique and consensus
4. **Reflection** — critique → revise a draft Methods block
5. **Write** — merge into LaTeX and autosave + checkpoint

**BAD (Budgeted Adaptive Deliberation):**
- Allocate samples in batches; compute a score per candidate (can be verifier-based)
- Stop early when a candidate clears a margin over the running average → saves tokens while keeping accuracy

---

## Tools that GPT‑5 models can call
The OpenAI provider enables **Responses API** tools:
- `--enable-code-interpreter` adds OpenAI’s server-side Code Interpreter.
- Built-in **function tools** (executed locally):
  - `run_python(code: str) -> str`
  - `check_symbolic_equality(expr1: str, expr2: str) -> {"equal": bool}`
  - `write_project_file(relative_path: str, content: str) -> {"written": str}`
  - `list_project_files(relative_path: str) -> {"files": [..]}`

### Security considerations
- `run_python` is intended for **trusted, local** exploration; it has no network and runs in the current process. Review before enabling on shared machines.

---

## Configuration reference
| Flag | Meaning |
|------|---------|
| `--max-iterations` | Upper bound on loop iterations |
| `--samples-per-query` | Test-time compute budget per critical step |
| `--time-budget-sec` | Soft wall-clock limit |
| `--reasoning-effort` | Reasoning effort hint to the model (low/medium/high) |
| `--enable-code-interpreter` | Allow server-side code interpreter tool |
| `--temperature`, `--top_p` | Sampling controls |
| `--max-output-tokens` | Cap output length per call |
| `--parallel-workers` | Parallel sampling (for future expansion) |
| `--devices` | Labels for local tools (placeholders, e.g., `cuda:0`) |

---

## Testing
- **Offline smoke test**: `scripts/run_demo.py` creates a throwaway project and a zip for inspection.
- **Unit tests (no network)** using the Mock provider:
  ```powershell
  python sciresearch_ai\testing\test_mock_flow.py
  python sciresearch_ai\testing\test_more.py
  ```
  These validate project creation, autosaves, checkpoints, and the BAD early-stop contract.

---

## Troubleshooting
- **`Set OPENAI_API_KEY`**: required for the OpenAI provider.
- **Model not found**: ensure your account has access to the selected GPT‑5 model ID.
- **LaTeX compile**: this project writes `.tex`; PDF compilation is not included. Use your local TeX toolchain (TeX Live/MiKTeX).

---

## Roadmap
- Verifier-driven scoring (unit test pass rate, numerical checks)
- Bandit-of-Thought strategy allocation
- Literature search + BibTeX grounding
- Optional PDF compilation step
=======
# SciResearch-AI
>>>>>>> 1621e5aef8c6a1ef61bf3c5174af077a2a0ceac4
