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
- To enable web search tools: install `exa_py` and set `EXA_API_KEY`.
- The sandboxed Python tool requires Docker or a compatible container runtime.

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

# Quick check that your OpenAI API key works
python -m sciresearch_ai.main test-openai --model gpt-4o-mini --reasoning-effort none
# (or use a reasoning-capable model and omit `--reasoning-effort`)
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
- **LaTeX compile**: the project writes `.tex`; install a TeX toolchain with `pdflatex` (e.g., `sudo apt-get install texlive-latex-base`, `brew install mactex-no-gui`, or `choco install miktex`) and run `bash scripts/ci_compile_tex.sh` to verify your setup.
- **Proxy errors during pip**: try appending `--proxy=""` to `pip install` to bypass restrictive proxy settings.

---

## Roadmap
- Verifier-driven scoring (unit test pass rate, numerical checks)
- Bandit-of-Thought strategy allocation
- Literature search + BibTeX grounding
- Optional PDF compilation step
 
---

## Fine-tuning the OSS 120B model

The repository ships a lightweight wrapper around the open-source
`openai/oss-120b` model. The upstream implementation is vendored under
[`gpt_oss/`](gpt_oss) for reference. Generated data from different
providers can be normalized with `sciresearch_ai.data.ingestion` and
stored as JSONL. The
 RL training script consumes this file and performs PPO fine-tuning:

### Downloading the weights

Fetch checkpoints from Hugging Face using the helper script (requires
[`git-lfs`](https://git-lfs.com/)):

```bash
python scripts/download_oss_weights.py --repo openai/oss-120b --out ./oss-120b
```

```bash
python scripts/train_rl.py --data data/rl_data.jsonl --output checkpoints/oss-rl
```

Select the device explicitly with `--device` (`cpu`, `cuda`, or `npu`):

```bash
python scripts/train_rl.py --data data/rl_data.jsonl --output checkpoints/oss-rl --device cuda
```

### Generating training data

Use the OSS model itself to create supervised examples:

```bash
python scripts/gen_oss_data.py \
  --prompt "Explain reinforcement learning" \
  --samples 4 \
  --out data/rl_data.jsonl \
  --device cuda \
  --max-new-tokens 200
```

To use the fine-tuned weights during paper generation, supply the path to
`PaperManager`:

```python
from sciresearch_ai.paper.manager import PaperManager
pm = PaperManager(root="projects/my_paper", model_path="checkpoints/oss-rl")
print(pm.generate_text("Summarize the results."))
```

Omit `model_path` to fall back to the base model.

### Quick inference

For a light-weight smoke test of the wrapper, `scripts/infer_oss.py` loads
the base or fine-tuned model and prints a completion for a given prompt:

```bash
python scripts/infer_oss.py "Hello from OSS" --device cpu --max-new-tokens 20
```

Add `--device npu` to execute the model on an Ascend device, or `--device cuda` for GPUs:

```bash
python scripts/infer_oss.py "Hello from OSS" --device npu --max-new-tokens 20
```

### Using the OSS model in the research loop

The main CLI supports the open-source model through the `oss` provider. This
allows local inference and optional tools such as web search (via the
`SimpleBrowser` tool) and a sandboxed Python runtime.

```bash
python -m sciresearch_ai.main run --project ./projects/my_paper \
  --provider oss --enable-browser --enable-python --max-iterations 2
```

`--enable-browser` attaches a lightweight web-search tool (via Exa), and
`--enable-python` exposes a sandboxed Python runtime for quick calculations.
Add `--model` to supply fine-tuned checkpoints; omitting it defaults to the
base `openai/oss-120b` weights.
