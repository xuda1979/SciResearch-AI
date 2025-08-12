# OpenAI OSS 120B

This directory contains a lightweight wrapper to interface with the
open-source **OpenAI OSS 120B** language model. The full upstream model
source code is now vendored in this repository under the top-level
[`gpt_oss/`](../../../gpt_oss) directory, which carries its own
[Apache&nbsp;2.0 license](../../../gpt_oss/LICENSE).

The actual model weights are not distributed with this repository. Use
the helper function `load_model` to fetch the model and tokenizer from a
local path or from Hugging Face Hub:

```python
from sciresearch_ai.models.oss_120b import load_model
model, tokenizer = load_model()  # downloads openai/oss-120b by default
```

Refer to the upstream project for full details and licensing.
