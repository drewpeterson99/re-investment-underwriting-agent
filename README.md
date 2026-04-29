# re-investment-underwriting-agent

Python agent that:
- uses `llama_cpp` with a local GGUF model,
- extracts required underwriting fields from natural language using a YAML-defined schema,
- writes extracted values into named cells in a copied Excel template via `openpyxl`.

Current target fields:
- `StreetAddress`
- `YearBuilt`

## Suggested GGUF model

For structured extraction, a strong local option is:
- [`Qwen2.5-7B-Instruct-Q4_K_M.gguf`](https://huggingface.co/bartowski/Qwen2.5-7B-Instruct-GGUF)

If you have limited RAM/CPU, you can also use a smaller 3B Instruct GGUF from the same family.

## Setup

```bash
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

> Note: this project is currently configured for CPU-only `llama-cpp-python` installation. If you later want GPU-enabled `llama-cpp-python` on Windows, you should verify that a C/C++ compiler toolchain is installed and configured.

## Run

```bash
py main.py `
  --model "C:\local_models\Qwen2.5-7B-Instruct-Q5_K_M.gguf" `
  --template "TCG Blank Model Template 2026-04-26.xlsx" `
  --output "Output" `
  --schema "field_schema.yaml" `
  --prompt "Subject property is 123 Main St, Cleveland, OH 44113. Home was built in 1978. Asking price is $ 120,000"
```

The script will:
1. call the model to extract fields from the prompt,
2. validate/coerce output according to `field_schema.yaml`,
3. copy the template workbook to the output path (default file name: `{StreetAddress} - Charlotte NC - Model {yyyy-mm-dd}.xlsx` under `Output`),
4. write values into named cells (`StreetAddress`, `YearBuilt`).

## Customize output format via YAML

Edit `field_schema.yaml` to add or adjust fields and validation constraints.