Welcome to the gpt-oss series, [OpenAI's open-weight models](https://openai.com/open-models/) designed for powerful reasoning, agentic tasks, and versatile developer use cases.

We're releasing two flavors of these open models:

- `gpt-oss-120b` — for production, general purpose, high reasoning use cases that fit into a single H100 GPU (117B parameters with 5.1B active parameters)
- `gpt-oss-20b` — for lower latency, and local or specialized use cases (21B parameters with 3.6B active parameters)

Both models were trained using our [harmony response format][harmony] and should only be used with this format; otherwise, they will not work correctly.

### Highlights

- **Permissive Apache 2.0 license:** Build freely without copyleft restrictions or patent risk—ideal for experimentation, customization, and commercial deployment.
- **Configurable reasoning effort:** Easily adjust the reasoning effort (low, medium, high) based on your specific use case and latency needs.
- **Full chain-of-thought:** Provides complete access to the model's reasoning process, facilitating easier debugging and greater trust in outputs. This information is not intended to be shown to end users.
- **Fine-tunable:** Fully customize models to your specific use case through parameter fine-tuning.
- **Agentic capabilities:** Use the models' native capabilities for function calling, [web browsing](#browser), [Python code execution](#python), and Structured Outputs.
- **Native MXFP4 quantization:** The models are trained with native MXFP4 precision for the MoE layer, allowing `gpt-oss-120b` to run on a single H100 GPU and `gpt-oss-20b` to run within 16GB of memory..

### Inference examples

#### Transformers

You can use `gpt-oss-120b` and `gpt-oss-20b` with Transformers. If you use Transformers's chat template it will automatically apply the [harmony response format][harmony]. If you use `model.generate` directly, you need to apply the harmony format manually using the chat template or use our [`openai-harmony`][harmony] package.

```python
from transformers import pipeline
import torch

model_id = "openai/gpt-oss-120b"

pipe = pipeline(
    "text-generation",
    model=model_id,
    torch_dtype="auto",
    device_map="auto",
)

messages = [
    {"role": "user", "content": "Explain quantum mechanics clearly and concisely."},
]

outputs = pipe(
    messages,
    max_new_tokens=256,
)
print(outputs[0]["generated_text"][-1])
```

[Learn more about how to use gpt-oss with Transformers.](https://cookbook.openai.com/articles/gpt-oss/run-transformers)

#### vLLM

vLLM recommends using [`uv`](https://docs.astral.sh/uv/) for Python dependency management. You can use vLLM to spin up an OpenAI-compatible webserver. The following command will automatically download the model and start the server.

```bash
uv pip install --pre vllm==0.10.1+gptoss \
    --extra-index-url https://wheels.vllm.ai/gpt-oss/ \
    --extra-index-url https://download.pytorch.org/whl/nightly/cu128 \
    --index-strategy unsafe-best-match

vllm serve openai/gpt-oss-20b
```

[Learn more about how to use gpt-oss with vLLM.](https://cookbook.openai.com/articles/gpt-oss/run-vllm)

#### PyTorch / Triton / Metal

These implementations are largely reference implementations for educational purposes and are not expected to be run in production.

[Learn more below.](#reference-pytorch-implementation)

#### Ollama

If you are trying to run `gpt-oss` on consumer hardware, you can use Ollama by running the following commands after [installing Ollama](https://ollama.com/download).

```bash
# gpt-oss-20b
ollama pull gpt-oss:20b
ollama run gpt-oss:20b

# gpt-oss-120b
ollama pull gpt-oss:120b
ollama run gpt-oss:120b
```

[Learn more about how to use gpt-oss with Ollama.](https://cookbook.openai.com/articles/gpt-oss/run-locally-ollama)

#### LM Studio

If you are using [LM Studio](https://lmstudio.ai/) you can use the following commands to download.

```bash
# gpt-oss-20b
lms get openai/gpt-oss-20b
# gpt-oss-120b
lms get openai/gpt-oss-120b
```

## About this repository

This repository provides a collection of reference implementations:

- **Inference:**
  - [`torch`](#reference-pytorch-implementation) — a non-optimized [PyTorch](https://pytorch.org/) implementation for educational purposes only. Requires at least 4x H100s because it's not optimized
  - [`triton`](#reference-triton-implementation-single-gpu) — a more optimized implementation using [PyTorch](https://pytorch.org/) & [Triton](https://github.com/triton-lang/triton) incl. using CUDA graphs and basic caching
  - [`metal`](#reference-metal-implementation) — a Metal-specific implementation for running the models on Apple Silicon hardware
- **Tools:**
  - [`browser`](#browser) — a reference implementation of the browser tool the models got trained on
  - [`python`](#python) — a stateless reference implementation of the python tool the model got trained on
- **Client examples:**
  - [`chat`](#terminal-chat) — a basic terminal chat application that uses the PyTorch or Triton implementations for inference along with the python and browser tools
  - [`responses_api`](#responses-api) — an example Responses API compatible server that implements the browser tool along with other Responses-compatible functionality

## Setup

### Requirements

- python 3.12
- On macOS: Install the Xcode CLI tools --> `xcode-select --install`
- On Linux: These reference implementations require CUDA
- On Windows: These reference implementations have not been tested on Windows. Try using solutions like Ollama if you are trying to run the model locally.

### Installation

If you want to modify the code, you can install the project from the local source:

```shell
pip install -e ".[metal]"
```

## Download the model

You can download the model weights from the [Hugging Face Hub](https://huggingface.co/collections/openai/gpt-oss-68911959590a1634ba11c7a4) directly from Hugging Face CLI:

```shell
# gpt-oss-120b
huggingface-cli download openai/gpt-oss-120b --include "original/*" --local-dir gpt-oss-120b/

# gpt-oss-20b
huggingface-cli download openai/gpt-oss-20b --include "original/*" --local-dir gpt-oss-20b/
```

## Reference PyTorch implementation

We include an inefficient reference PyTorch implementation in [gpt_oss/torch/model.py](./gpt_oss/torch/model.py). This code uses basic PyTorch operators to show the exact model architecture, with a small addition of supporting tensor parallelism in MoE so that the larger model can run with this code (e.g., on 4xH100 or 2xH200). In this implementation, we upcast all weights to BF16 and run the model in BF16.

To run the reference implementation. Install dependencies:

```shell
pip install -e .[torch]
```

And then run:

```shell
# On 4xH100:
torchrun --nproc-per-node=4 -m gpt_oss.generate gpt-oss-120b/original/
```

## Reference Triton implementation (single GPU)

We also include an optimized reference implementation that uses [an optimized triton MoE kernel](https://github.com/triton-lang/triton/tree/main/python/triton_kernels/triton_kernels) that supports MXFP4. It also has some optimization on the attention code to reduce the memory cost. To run this implementation, the nightly version of triton and torch will be installed. This version can be run on a single 80GB GPU for `gpt-oss-120b`.

To install the reference Triton implementation run

```shell
# You need to install triton from source to use the triton implementation
git clone https://github.com/triton-lang/triton
cd triton/
pip install -r python/requirements.txt
pip install -e . --verbose --no-build-isolation

# Install the gpt-oss triton implementation
pip install -e .[triton]
```

And then run:

```shell
# On 1xH100
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
python -m gpt_oss.generate --backend triton gpt-oss-120b/original/
```

If you encounter `torch.OutOfMemoryError` make sure to turn on the expandable allocator to avoid crashes when loading weights from the checkpoint.

## Reference Metal implementation

Additionally we are providing a reference implementation for Metal to run on Apple Silicon. This implementation is not production-ready but is accurate to the PyTorch implementation.

The implementation will get automatically compiled when running the `.[metal]` installation on an Apple Silicon device:

```shell
pip install -e .[metal]
```

To perform inference you'll need to first convert the SafeTensor weights from Hugging Face into the right format using:

```shell
python gpt_oss/metal/scripts/create-local-model.py -s <model_dir> -d <output_file>
```

Or downloaded the pre-converted weight:
```shell
huggingface-cli download openai/gpt-oss-120b --include "metal/*" --local-dir gpt-oss-120b/metal/
huggingface-cli download openai/gpt-oss-20b --include "metal/*" --local-dir gpt-oss-20b/metal/
```

To test it you can run:

```shell
python gpt_oss/metal/examples/generate.py gpt-oss-20b/metal/model.bin -p "why did the chicken cross the road?"
```

## Harmony format & tools

Along with the model, we are also releasing a new chat format library `harmony` to interact with the model. Check [this guide](https://cookbook.openai.com/articles/openai-harmony) for more info about harmony.

We also include two system tools for the model: browsing and python container. Check [gpt_oss/tools](gpt_oss/tools) for the tool implementation.

## Clients

### Terminal Chat

The terminal chat application is a basic example on how to use the harmony format together with the PyTorch, Triton, and vLLM implementations. It also exposes both the python and browser tool as optional tools that can be used.

```bash
usage: python -m gpt_oss.chat [-h] [-r REASONING_EFFORT] [-a] [-b] [--show-browser-results] [-p] [--developer-message DEVELOPER_MESSAGE] [-c CONTEXT] [--raw] [--backend {triton,torch,vllm}] FILE

Chat example

positional arguments:
  FILE                  Path to the SafeTensors checkpoint

options:
  -h, --help            show this help message and exit
  -r REASONING_EFFORT, --reasoning-effort REASONING_EFFORT
                        Reasoning effort (default: low)
  -a, --apply-patch     Make apply_patch tool available to the model (default: False)
  -b, --browser         Use browser tool (default: False)
  --show-browser-results
                        Show browser results (default: False)
  -p, --python          Use python tool (default: False)
  --developer-message DEVELOPER_MESSAGE
                        Developer message (default: )
  -c CONTEXT, --context CONTEXT
                        Max context length (default: 8192)
  --raw                 Raw mode (does not render Harmony encoding) (default: False)
  --backend {triton,torch,vllm}
                        Inference backend (default: triton)
```

> [!NOTE]
> The torch and triton implementation requires original checkpoint under `gpt-oss-120b/original/` and `gpt-oss-20b/original/` respectively. While vLLM uses the Hugging Face converted checkpoint under `gpt-oss-120b/` and `gpt-oss-20b/` root directory respectively.

### Responses API

We also include an example Responses API server. This server does not implement every feature and event of the Responses API but should be compatible with most of the basic use cases and serve as inspiration for anyone building their own server. Some of our inference partners are also offering their own Responses API.

You can start this server with the following inference backends:

- `triton` — uses the triton implementation
- `metal` — uses the metal implementation on Apple Silicon only
- `ollama` — uses the Ollama /api/generate API as a inference solution
- `vllm` — uses your installed vllm version to perform inference
- `transformers` — uses your installed transformers version to perform local inference

```bash
usage: python -m gpt_oss.responses_api.serve [-h] [--checkpoint FILE] [--port PORT] [--inference-backend BACKEND]

Responses API server

options:
  -h, --help                    show this help message and exit
  --checkpoint FILE             Path to the SafeTensors checkpoint
  --port PORT                   Port to run the server on
  --inference-backend BACKEND   Inference backend to use
```

### Codex

We support [codex](https://github.com/openai/codex) as a client for gpt-oss. To run the 20b version, set this to `~/.codex/config.toml`:

```
disable_response_storage = true
show_reasoning_content = true

[model_providers.local]
name = "local"
base_url = "http://localhost:11434/v1"

[profiles.oss]
model = "gpt-oss:20b"
model_provider = "local"
```

This will work with any chat completions-API compatible server listening on port 11434, like ollama. Start the server and point codex to the oss model:

```
ollama run gpt-oss:20b
codex -p oss
```

## Tools

### Browser

> [!WARNING]
> This implementation is purely for educational purposes and should not be used in production. You should implement your own equivalent of the [`ExaBackend`](./gpt_oss/tools/simple_browser/backend.py) class with your own browsing environment.

Both gpt-oss models were trained with the capability to browse using the `browser` tool that exposes the following three methods:

- `search` to search for key phrases
- `open` to open a particular page
- `find` to look for contents on a page

#### Usage

To enable the browser tool, you'll have to place the definition into the `system` message of your harmony formatted prompt. You can either use the `with_browser()` method if your tool implements the full interface or modify the definition using `with_tools()`. For example:

```python
import datetime
from gpt_oss.tools.simple_browser import SimpleBrowserTool
from gpt_oss.tools.simple_browser.backend import ExaBackend
from openai_harmony import SystemContent, Message, Conversation, Role, load_harmony_encoding, HarmonyEncodingName

encoding = load_harmony_encoding(HarmonyEncodingName.HARMONY_GPT_OSS)

# Exa backend requires you to have set the EXA_API_KEY environment variable
backend = ExaBackend(
    source="web",
)
browser_tool = SimpleBrowserTool(backend=backend)

# create a basic system prompt
system_message_content = SystemContent.new().with_conversation_start_date(
    datetime.datetime.now().strftime("%Y-%m-%d")
)

# if you want to use the browser tool
if use_browser_tool:
    # enables the tool
    system_message_content = system_message_content.with_tools(browser_tool.tool_config)
    # alternatively you could use the following if your tool is not stateless
    system_message_content = system_message_content.with_browser()

# construct the system message
system_message = Message.from_role_and_content(Role.SYSTEM, system_message_content)

# create the overall prompt
messages = [system_message, Message.from_role_and_content(Role.USER, "What's the weather in SF?")]
conversation = Conversation.from_messages(messages)

# convert to tokens
token_ids = encoding.render_conversation_for_completion(conversation, Role.ASSISTANT)

# perform inference
# ...

# parse the output
messages = encoding.parse_messages_from_completion_tokens(output_tokens, Role.ASSISTANT)
last_message = messages[-1]
if last_message.recipient.startswith("browser"):
  # perform browser call
  response_messages = await browser_tool.process(last_message)

  # extend the current messages and run inference again
  messages.extend(response_messages)
```

#### Details

To control the context window size this tool use a scrollable window of text that the model can interact with. So it might fetch the first 50 lines of a page and then scroll to the next 20 lines after that. The model has also been trained to then use citations from this tool in its answers.

To improve performance the tool caches requests so that the model can revisit a different part of a page without having to reload the page. For that reason you should create a new browser instance for every request.

### Python

The model was trained to use a python tool to perform calculations and other actions as part of its chain-of-thought. During the training the model used a stateful tool which makes running tools between CoT loops easier. This reference implementation, however, uses a stateless mode. As a result the PythonTool defines its own tool description to override the definition in `openai-harmony`.

> [!WARNING]
> This implementation runs in a permissive Docker container which could be problematic in cases like prompt injections. It's serving as an example and you should consider implementing your own container restrictions in production.

#### Usage

To enable the python tool, you'll have to place the definition into the `system` message of your harmony formatted prompt. You can either use the `with_python()` method if your tool implements the full interface or modify the definition using `with_tools()`. For example:

```python
import datetime
from gpt_oss.tools.python_docker.docker_tool import PythonTool
from openai_harmony import SystemContent, Message, Conversation, Role, load_harmony_encoding, HarmonyEncodingName

encoding = load_harmony_encoding(HarmonyEncodingName.HARMONY_GPT_OSS)

python_tool = PythonTool()

# create a basic system prompt
system_message_content = SystemContent.new().with_conversation_start_date(
    datetime.datetime.now().strftime("%Y-%m-%d")
)

# if you want to use the python tool
if use_python_tool:
    # enables the tool making sure that the prompt gets set with the stateless tool description
    system_message_content = system_message_content.with_tools(python_tool.tool_config)
    # alternatively you could use the following if your tool is not stateless
    system_message_content = system_message_content.with_python()

# construct the system message
system_message = Message.from_role_and_content(Role.SYSTEM, system_message_content)

# create the overall prompt
messages = [system_message, Message.from_role_and_content(Role.USER, "What's the square root of 9001?")]
conversation = Conversation.from_messages(messages)

# convert to tokens
token_ids = encoding.render_conversation_for_completion(conversation, Role.ASSISTANT)

# perform inference
# ...

# parse the output
messages = encoding.parse_messages_from_completion_tokens(output_tokens, Role.ASSISTANT)
last_message = messages[-1]
if last_message.recipient == "python":
  # perform python call
  response_messages = await python_tool.process(last_message)

  # extend the current messages and run inference again
  messages.extend(response_messages)
```

### Apply Patch

`apply_patch` can be used to create, update or delete files locally.

## Other details

### Precision format

We released the models with native quantization support. Specifically, we use [MXFP4](https://www.opencompute.org/documents/ocp-microscaling-formats-mx-v1-0-spec-final-pdf) for the linear projection weights in the MoE layer. We store the MoE tensor in two parts:

- `tensor.blocks` stores the actual fp4 values. We pack every two value in one `uint8` value.
- `tensor.scales` stores the block scale. The block scaling is done among the last dimension for all MXFP4 tensors.

All other tensors will be in BF16. We also recommend use BF16 as the activation precision for the model.

### Recommended Sampling Parameters

We recommend sampling with `temperature=1.0` and `top_p=1.0`.

## Contributing

The reference implementations in this repository are meant as a starting point and inspiration. Outside of bug fixes we do not intend to accept new feature contributions.

## SciResearch-AI

This repository also includes `sciresearch_ai`, a reasoning CLI for scientific papers that automates a human-like research loop. For more details on this application, please see the [`sciresearch_ai/README.md`](./sciresearch_ai/README.md) file.

## Research Papers

This repository contains research papers that explore various ideas and concepts. Below is a summary of each paper's objective.

### Proof-Carrying Answers and Property-Based Self-Fuzzing

Proof-Carrying Answers (PCA) require each model output to include a machine-checkable proof or verification script. Property-based self-fuzzing complements PCA by stress-testing claims with generated counterexamples. Together they increase the reliability and verifiability of large language model responses.

### Causal Audit Trails for Transparent LLM Reasoning

Causal Audit Trails (CAT) improve transparency and trust in language model outputs by recording a directed acyclic graph of the sources, tools, prompts, and code paths that influence each claim.

### Field-Programmable Attention for Efficient Long Contexts

This paper introduces Field-Programmable Attention (FPA), a technique to program sparse attention patterns based on task-specific signals to improve long-context utilization and reduce computational cost.

### Semantic-Hash Lattice Memory (SHL-Mem)

Semantic-Hash Lattice Memory (SHL-Mem) is a proposed long-context memory architecture that uses multiple locality-sensitive semantic hashes to organize and retrieve information from very long sequences. By mapping spans of the input into hash buckets along several semantic dimensions (e.g., entities, relations, time), SHL-Mem allows efficient retrieval via lattice joins.

### Global-then-Local Decoding (GLD)

Global-then-Local Decoding (GLD) decomposes generation into two phases: first a global plan is produced that outlines goals and constraints, then local sections are filled under the plan using constrained decoding. This approach reduces contradictions and improves coherence across long documents.

### Counterparty Models with Verifiable Non-Collusion

Counterparty Models with Verifiable Non-Collusion (CNCM) are a radical approach to reduce hallucinations and biases in language models by running multiple specialised models as adversarial partners: an Advocate, a Skeptic, and a Judge. Each model plays a role in producing, challenging and aggregating answers, while cryptographic transcripts prevent collusion.

### Deterministic Shadow-OS for Agents (DSOS)

Deterministic Shadow-OS for Agents (DSOS) is a method to make AI agents safer and more reliable when interacting with operating systems and web interfaces. DSOS forces the agent to produce a deterministic intention log of actions to be executed in a sandbox, enabling human review and rollback before committing changes.

### Answer Futures Market (AFM)

The Answer Futures Market (AFM) is a novel mechanism for routing computational budget in a mixture-of-experts or agents system. Specialists bid their confidence and associated cost to answer a question; a router allocates resources to those with the highest expected value of improvement.

### Entropy-Thermostat Decoding (ETD)

Entropy-Thermostat Decoding (ETD) is a decoding strategy for language models that regulates the entropy of output tokens, aiming to reduce verbosity and stabilize reasoning depth. It dynamically adjusts the sampling temperature based on a target entropy schedule.

### Knowledge Fossilization via Micro-Theorems

Large language models are prone to forgetting or misrepresenting established facts when updated or fine-tuned. To counteract this drift, we propose knowledge fossilization via micro-theorems. Each important domain fact is formalized as a small theorem with an accompanying test or proof. During generation, these micro-theorems can be referenced or imported, ensuring that critical relationships remain consistent across model updates.

### KV Sketching for Long Contexts

Large language models (LLMs) equipped with extremely long context windows suffer from high memory bandwidth requirements and prohibitive VRAM usage because key and value (K/V) states must be stored for every token. “KV-Sketching” is a family of techniques that learns to compress K/V state tensors into compact sketches that can be rehydrated on demand. By combining low-rank approximations, count-sketch hashing and quantization, one can achieve multi-million-token contexts without a linear growth in memory footprint.

### Differentially-Private Ephemeral Memory with Revocation

Long-lived conversational agents risk accumulating sensitive or malicious information in their internal caches. Differentially-Private Ephemeral Memory (DPEM) aims to enforce the “right to be forgotten” and limit prompt‑injection persistence by associating each memory with a privacy budget and a revocation token. When the budget is exhausted or a valid revocation request is received, the memory is purged from the model's context.
