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
pip install -r requirements-dev.txt
```

Run tests from the project root (uses `pytest.ini`):

```bash
pytest
```

> Note: this project is currently configured for CPU-only `llama-cpp-python` installation. If you later want GPU-enabled `llama-cpp-python` on Windows, you should verify that a C/C++ compiler toolchain is installed and configured.

## Run

<!-- Defaults for each flag are documented in "CLI defaults" below; keep this example in sync with parse_args() in main.py. -->

```powershell
# Optional: set once per shell so you can omit --model (see CLI defaults).
# $env:UNDERWRITING_GGUF = "C:\local_models\Qwen2.5-7B-Instruct-Q5_K_M.gguf"

# Use single quotes for --prompt when the text contains $ — double quotes cause PowerShell to eat `$675k`.
py main.py `
  --model "C:\local_models\Qwen2.5-7B-Instruct-Q5_K_M.gguf" `
  --template "TCG Blank Model Template 2026-04-26.xlsx" `
  --output "Output" `
  --schema "field_schema.yaml" `
  --prompt 'Subject property is 123 Main St, Cleveland, OH 44113. Home was built in 1978. Asking price is $ 120,000'

# Or use a UTF-8 file: --prompt-file listing.txt
# Or paste in a window (best on Windows; preserves $): --gui
```

### CLI defaults

Arguments that must be supplied (no fallback default in code):

- **`--prompt`**, **`--prompt-file`**, or **`--gui`** — Exactly one way to supply listing text. Prefer **`--gui`** on Windows to paste into a small dialog so **`$` amounts are never mangled by PowerShell**. **`--prompt-file`** is good for automation or very long text. Inline **`--prompt`** works if you use **single quotes** around the value when it contains `$`.

Arguments that are optional on the CLI but still need a model path before the run succeeds:

- **`--model`** — Optional flag; default value is whatever is in the **`UNDERWRITING_GGUF`** environment variable (often unset). If you omit `--model` and `UNDERWRITING_GGUF` is missing or empty, the program raises an error—there is no bundled GGUF path.

Optional arguments with built-in defaults (see `parse_args()` in `main.py`):

- **`--template`** — `TCG Blank Model Template 2026-04-26.xlsx`
- **`--output`** — `Output` (treated as a directory unless the path ends with `.xlsx`)
- **`--schema`** — `field_schema.yaml`
- **`--n-ctx`** — `4096`
- **`--n-gpu-layers`** — `0` (CPU-only)

The script will:
1. call the model to extract fields from the prompt,
2. validate/coerce output according to `field_schema.yaml`,
3. copy the template workbook to the output path (default file name: `{StreetAddress} - Charlotte NC - Model {yyyy-mm-dd}.xlsx` under `Output`),
4. write values into named cells (`StreetAddress`, `YearBuilt`).

## Customize output format via YAML

Edit `field_schema.yaml` to add or adjust fields and validation constraints.