# re-investment-underwriting-agent

Python agent that:
- uses `llama_cpp` with a local GGUF model,
- extracts required underwriting fields from natural language using a YAML-defined schema,
- writes extracted values into named cells in a copied Excel template via `openpyxl`.

Current target fields mirror **`field_schema.yaml`** (including which fields are required—edit that file if you want stricter extraction).

**Required**

- `StreetAddress`
- `YearBuilt`
- `AskingPrice`
- `AssessedValue`
- `Bedrooms`
- `Bathrooms`
- `SquareFootage`
- `RentCastRent`
- `Units`

**Optional**

- `ListingDate`
- `InPlaceRent`
- `PurchasePrice` (contract purchase amount in USD; same currency normalization as `AskingPrice`)
- `SellerConcessions` (seller-paid closing help in USD; same currency rules; minimum 0)
- `CityState` (location as `"City, State"`—when extracted, the default output file name uses this instead of `Charlotte NC`, with the comma omitted from the file name segment)

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

The simplest way for a human to run the script is with **`--gui`**: a window opens, you paste the listing (including **`$` amounts**—no shell quoting issues), then click **Finish**.

<!-- Defaults for optional flags are in "CLI defaults" below; keep examples in sync with parse_args() in main.py. -->

```powershell
# Optional: set once per shell so you can omit --model (see CLI defaults).
# $env:UNDERWRITING_GGUF = "C:\local_models\Qwen2.5-7B-Instruct-Q5_K_M.gguf"

py main.py `
  --model "C:\local_models\Qwen2.5-7B-Instruct-Q5_K_M.gguf" `
  --gui
```

Other ways to supply listing text (for automation, scripts, or non-interactive runs):

- **`--prompt-file listing.txt`** — UTF-8 file (good for long text or CI).
- **`--prompt '...'`** — Inline text; on PowerShell use **single quotes** when the text contains **`$`**, or **`$675k`** may be mangled.

```powershell
py main.py `
  --model "C:\local_models\Qwen2.5-7B-Instruct-Q5_K_M.gguf" `
  --template "TCG Blank Model Template 2026-04-26.xlsx" `
  --output "Output" `
  --schema "field_schema.yaml" `
  --prompt 'Subject property is 123 Main St, Cleveland, OH 44113. Home was built in 1978. Asking price is $ 120,000'
```

### CLI defaults

Arguments that must be supplied (no fallback default in code):

- **Listing text** — Provide exactly one of **`--gui`** (recommended for interactive use), **`--prompt-file`**, or **`--prompt`**. **`--gui`** avoids PowerShell mangling **`$`** and is the least error-prone for hands-on runs. Use **`--prompt-file`** or **`--prompt`** when you need a scripted or non-GUI workflow; use **single quotes** around **`--prompt`** on PowerShell if the text contains **`$`**.

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
3. copy the template workbook to the output path (default directory file name: `{StreetAddress} - {location} - Model {yyyy-mm-dd}.xlsx` under `Output`, where `{location}` is `Charlotte NC` unless `CityState` is present—in which case it is derived from that value with the comma removed, e.g. `Cleveland, OH` → `Cleveland OH`),
4. write values into Excel named cells matching each schema field name (e.g. `StreetAddress`, `AskingPrice`, …).

## Customize output format via YAML

Edit `field_schema.yaml` to add or adjust fields and validation constraints.