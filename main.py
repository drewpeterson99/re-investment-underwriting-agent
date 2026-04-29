import argparse
import json
import math
import re
import shutil
from datetime import date
from pathlib import Path
from typing import Any, Dict, Iterable, Tuple

import yaml
from llama_cpp import Llama
from openpyxl import load_workbook


def load_schema(schema_path: Path) -> Dict[str, Any]:
    with schema_path.open("r", encoding="utf-8") as f:
        schema = yaml.safe_load(f)
    if not isinstance(schema, dict) or "fields" not in schema:
        raise ValueError("Schema must be a YAML mapping with a top-level 'fields' key.")
    if not isinstance(schema["fields"], dict) or not schema["fields"]:
        raise ValueError("'fields' must be a non-empty mapping in schema.")
    return schema


def schema_to_instruction_block(schema: Dict[str, Any]) -> str:
    lines = []
    for field_name, field_spec in schema["fields"].items():
        field_type = field_spec.get("type", "string")
        required = field_spec.get("required", False)
        description = field_spec.get("description", "")
        bounds = []
        if "min" in field_spec:
            bounds.append(f"min={field_spec['min']}")
        if "max" in field_spec:
            bounds.append(f"max={field_spec['max']}")
        bounds_text = f" ({', '.join(bounds)})" if bounds else ""
        req_text = "required" if required else "optional"
        normalization = field_spec.get("normalization", {})
        norm_text = ""
        if isinstance(normalization, dict) and normalization.get("rule"):
            norm_text = f" Normalization: {normalization['rule']}."
        lines.append(f"- {field_name}: {field_type}{bounds_text}, {req_text}. {description}{norm_text}")
    return "\n".join(lines)


def normalize_currency_text_to_int(raw_value: Any) -> int:
    text = str(raw_value).strip()

    # Remove currency symbols/codes/punctuation and keep numeric characters.
    text = re.sub(r"[^0-9.\-]", "", text)
    if not text:
        raise ValueError(f"Could not parse integer value from input: {raw_value!r}")
    return int(math.ceil(float(text)))


def build_messages(schema: Dict[str, Any], user_input: str) -> Iterable[Dict[str, str]]:
    instructions = schema_to_instruction_block(schema)
    system_prompt = (
        "You extract structured real-estate underwriting data from free text.\n"
        "Return ONLY valid JSON with exactly the schema keys.\n"
        "If a required field is missing, return null for that field.\n"
        "Do not add commentary."
    )
    user_prompt = (
        "Extract the following fields and normalize values where appropriate.\n"
        f"{instructions}\n\n"
        "Return JSON object with keys exactly as listed above.\n\n"
        f"Input text:\n{user_input}"
    )
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


def extract_json_from_response(text: str) -> Dict[str, Any]:
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if "\n" in text:
            text = text.split("\n", 1)[1]
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError(f"Could not locate JSON object in model output: {text}")
    return json.loads(text[start : end + 1])


def coerce_and_validate(parsed: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for field_name, field_spec in schema["fields"].items():
        raw_value = parsed.get(field_name)
        field_type = field_spec.get("type", "string")

        if raw_value is None:
            if field_spec.get("required", False):
                raise ValueError(f"Required field '{field_name}' is missing/null.")
            result[field_name] = None
            continue

        if field_type == "integer":
            normalization = field_spec.get("normalization", {})
            try:
                if isinstance(normalization, dict) and normalization.get("rule"):
                    value = normalize_currency_text_to_int(raw_value)
                else:
                    value = int(raw_value)
            except (TypeError, ValueError) as e:
                raise ValueError(f"Field '{field_name}' must be an integer. Got: {raw_value!r}") from e
            if "min" in field_spec and value < int(field_spec["min"]):
                raise ValueError(f"Field '{field_name}' below min {field_spec['min']}: {value}")
            if "max" in field_spec and value > int(field_spec["max"]):
                raise ValueError(f"Field '{field_name}' above max {field_spec['max']}: {value}")
            result[field_name] = value
        else:
            result[field_name] = str(raw_value).strip()

    return result


def run_extraction(
    model_path: Path,
    schema: Dict[str, Any],
    user_input: str,
    n_ctx: int = 4096,
    n_gpu_layers: int = 0,
) -> Dict[str, Any]:
    llm = Llama(
        model_path=str(model_path),
        n_ctx=n_ctx,
        n_gpu_layers=n_gpu_layers,
        verbose=False,
    )
    messages = list(build_messages(schema, user_input))
    completion = llm.create_chat_completion(
        messages=messages,
        temperature=0.0,
        top_p=0.95,
        response_format={"type": "json_object"},
    )
    content = completion["choices"][0]["message"]["content"]
    parsed = extract_json_from_response(content)
    return coerce_and_validate(parsed, schema)


def resolve_named_cell(workbook, name: str) -> Tuple[Any, str]:
    defined_name = workbook.defined_names.get(name)
    if defined_name is None:
        raise KeyError(f"Named cell/range '{name}' not found in workbook.")

    destinations = list(defined_name.destinations)
    if not destinations:
        raise ValueError(f"Named cell/range '{name}' has no destinations.")

    sheet_name, coord = destinations[0]
    ws = workbook[sheet_name]
    return ws, coord


def write_named_cells(output_workbook_path: Path, values: Dict[str, Any]) -> None:
    wb = load_workbook(output_workbook_path)
    for field_name, value in values.items():
        if value is None:
            continue
        ws, coord = resolve_named_cell(wb, field_name)
        ws[coord] = value
    wb.save(output_workbook_path)


def ensure_output_copy(template_path: Path, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(template_path, output_path)


_WIN_INVALID_FILENAME = set('<>:"/\\|?*')


def sanitize_filename_component(text: str) -> str:
    """Make a string safe for use as a single Windows filename segment."""
    out = "".join("_" if c in _WIN_INVALID_FILENAME else c for c in text.strip())
    out = re.sub(r"\s+", " ", out).strip(" .")
    return out or "Unknown_Address"


def resolve_output_workbook_path(output_arg: Path, street_address: str, today: date) -> Path:
    """
    If output_arg ends with .xlsx, use it as the exact file path.
    Otherwise treat output_arg as the output directory and build:
    ``{street} - Charlotte NC - Model {yyyy-mm-dd}.xlsx``
    """
    if output_arg.suffix.lower() == ".xlsx":
        return output_arg
    date_str = today.isoformat()
    x = sanitize_filename_component(street_address)
    filename = f"{x} - Charlotte NC - Model {date_str}.xlsx"
    return output_arg / filename


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract underwriting fields with llama.cpp and write to named Excel cells."
    )
    parser.add_argument("--model", required=True, help="Path to a GGUF model file.")
    parser.add_argument(
        "--template",
        default="TCG Blank Model Template 2026-04-26.xlsx",
        help="Path to source template workbook.",
    )
    parser.add_argument(
        "--output",
        default="Output",
        help=(
            "Path to the output .xlsx file, or a directory. "
            "If a directory (default: Output), the file name is "
            '"{StreetAddress} - Charlotte NC - Model {yyyy-mm-dd}.xlsx".'
        ),
    )
    parser.add_argument(
        "--schema",
        default="field_schema.yaml",
        help="Path to YAML schema defining extraction fields.",
    )
    parser.add_argument("--prompt", required=True, help="Natural-language user input to triage.")
    parser.add_argument("--n-ctx", type=int, default=4096, help="Context window.")
    parser.add_argument(
        "--n-gpu-layers",
        type=int,
        default=0,
        help="Number of model layers to offload to GPU (0 for CPU-only).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    model_path = Path(args.model)
    template_path = Path(args.template)
    output_arg = Path(args.output)
    schema_path = Path(args.schema)

    if not model_path.exists():
        raise FileNotFoundError(f"Model file not found: {model_path}")
    if not template_path.exists():
        raise FileNotFoundError(f"Template workbook not found: {template_path}")
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")

    schema = load_schema(schema_path)
    structured_values = run_extraction(
        model_path=model_path,
        schema=schema,
        user_input=args.prompt,
        n_ctx=args.n_ctx,
        n_gpu_layers=args.n_gpu_layers,
    )

    street = structured_values.get("StreetAddress")
    if not street:
        raise ValueError("StreetAddress is required to build the output filename.")

    output_path = resolve_output_workbook_path(output_arg, str(street), date.today())

    ensure_output_copy(template_path, output_path)
    write_named_cells(output_path, structured_values)

    print("Extracted fields:")
    print(json.dumps(structured_values, indent=2))
    print(f"\nWorkbook written: {output_path}")


if __name__ == "__main__":
    main()
