# Structured Output

This submodule demonstrates techniques for generating structured JSON outputs from Large Language Models (LLMs), ensuring they conform to predefined schemas.

We explore three different implementation strategies to control and constrain the output format:

## Methods

### 1. VLLM with OpenAI Function Call Interface
Uses the `vllm` engine to enforce JSON schema constraints via the OpenAI-style function calling mechanism. This allows the model to fill in structured outputs with type-safe validation during generation.

### 2. SGLANG (Structured Generation Language)
Leverages `sglang`, a declarative interface for defining structured output templates. It tightly constrains the decoding space to valid outputs using grammar-based decoding.

### 3. Logit Processor
Implements a custom `LogitProcessor` in HuggingFace Transformers to restrict token generation dynamically based on the current state of the JSON template. This allows for real-time control over output structure without relying on external grammar engines.

## Use Cases

These implementations are useful for:
- Task routing
- Parameter extraction
- Function calling where strict adherence to output structure is required

## Running

Each implementation is contained in a standalone script:
- `vllmtest.py`
- `sglangtest.py`
- `logit_test.py`

Make sure to install the corresponding dependencies before running.

```bash
pip install vllm sglang transformers

