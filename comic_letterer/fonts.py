"""Local font maps; paths are resolved relative to their configuration file."""

import json
from pathlib import Path
from .validation import ident, fields


def read_font_map(path):
    if not path:
        return {}
    path = Path(path)
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("font map must be an object")
    result = {}
    for role, spec in value.items():
        ident(role)
        if role == "body":
            raise ValueError("configure body using --font")
        fields(spec, "path index", "font map")
        p = Path(spec["path"]).expanduser()
        result[role] = {
            "path": str((path.parent / p).resolve()),
            "index": spec.get("index", 0),
        }
    return result
