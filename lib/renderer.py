"""Template rendering: input coercion → computed fields → str.format."""
import json
from typing import Any

_SAFE_BUILTINS = {
    "round": round, "abs": abs, "sum": sum, "len": len,
    "min": min, "max": max, "int": int, "float": float,
    "str": str, "bool": bool, "list": list, "dict": dict,
    "sorted": sorted, "enumerate": enumerate, "zip": zip,
    "range": range, "isinstance": isinstance,
}


def _eval_expr(expr: str, ctx: dict) -> Any:
    try:
        return eval(expr, {"__builtins__": _SAFE_BUILTINS}, ctx)  # noqa: S307
    except Exception:
        return None


def coerce_inputs(prompt_def: dict, raw: dict) -> dict:
    """Cast user-supplied values to the declared types from the inputs list."""
    result: dict = {}
    for inp in prompt_def.get("inputs", []):
        key = inp["key"]
        val = raw.get(key)
        if val is None or val == "":
            result[key] = 0.0 if inp.get("type") == "number" else ""
            continue
        if inp.get("type") == "number":
            try:
                fval = float(val)
                result[key] = int(fval) if fval == int(fval) else fval
            except (TypeError, ValueError):
                result[key] = val
        else:
            result[key] = val
    return result


def resolve_computed(prompt_def: dict, values: dict) -> dict:
    """Evaluate computed_fields in dependency order (up to 10 passes)."""
    ctx = dict(values)
    for field, expr in (prompt_def.get("computed_fields") or {}).items():
        ctx[field] = None  # ensure keys exist so dependent fields can reference them

    for _ in range(10):
        changed = False
        for field, expr in (prompt_def.get("computed_fields") or {}).items():
            val = _eval_expr(expr, ctx)
            if val is not None and val != ctx.get(field):
                ctx[field] = val
                changed = True
        if not changed:
            break
    return ctx


def _parse_json_if_array(val: Any) -> Any:
    """Parse a string value as JSON if it looks like an array."""
    if isinstance(val, str):
        stripped = val.strip()
        if stripped.startswith("["):
            try:
                return json.loads(stripped)
            except json.JSONDecodeError:
                pass
    return val


def _format_array(val: list) -> str:
    """Render a list to a human-readable string for template substitution."""
    if not val:
        return ""
    if isinstance(val[0], dict):
        headers = list(val[0].keys())
        # Filter out empty/None values from headers for cleaner output
        rows = []
        for item in val:
            rows.append(" | ".join(str(item.get(h, "")) for h in headers))
        header_row = " | ".join(h for h in headers)
        sep = " | ".join("---" for _ in headers)
        return "\n".join([header_row, sep] + rows)
    # list of strings → bullet list
    return "\n".join(f"- {item}" for item in val if item)


def _to_display(val: Any) -> Any:
    """Convert a value to its template-ready form."""
    val = _parse_json_if_array(val)
    if isinstance(val, list):
        return _format_array(val)
    if val is None:
        return ""
    return val


class _DefaultDict(dict):
    """str.format_map helper: missing keys return {key} unchanged."""
    def __missing__(self, key: str) -> str:
        return f"{{{key}}}"


def render_template(prompt_def: dict, resolved: dict) -> str:
    """Render the user_prompt_template with resolved values."""
    template: str = prompt_def.get("user_prompt_template", "")
    display = {k: _to_display(v) for k, v in resolved.items()}
    try:
        return template.format_map(_DefaultDict(display))
    except (ValueError, KeyError):
        # Fallback: manual substitution without format specs
        result = template
        for k, v in display.items():
            result = result.replace(f"{{{k}}}", str(v))
        return result
