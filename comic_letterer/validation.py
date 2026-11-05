"""Input validation shared by the compiler and layout modules."""

import math
import re


def number(value, name, positive=False):
    if (
        isinstance(value, bool)
        or not isinstance(value, (float, int))
        or not math.isfinite(value)
    ):
        raise ValueError(f"{name} must be finite numeric")
    if positive and value <= 0:
        raise ValueError(f"{name} must be positive")
    return float(value)


def vector(value, size, name, box=False):
    if not isinstance(value, list) or len(value) != size:
        raise ValueError(f"{name} must contain {size} numbers")
    out = [number(v, name) for v in value]
    if box and min(out[2:]) <= 0:
        raise ValueError(f"{name} dimensions must be positive")
    return out


def fields(obj, allowed, name):
    if not isinstance(obj, dict):
        raise ValueError(f"{name} must be an object")
    extra = set(obj) - set(allowed.split())
    if extra:
        raise ValueError(f"{name}: unknown fields {sorted(extra)}")


def ident(value):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", value):
        raise ValueError(
            "id must start with a letter and contain ASCII letters, digits, _ or -"
        )
    return value


def color(value):
    if not isinstance(value, str) or not re.fullmatch(r"#[0-9a-fA-F]{6}", value):
        raise ValueError("color must be #RRGGBB")
    return value
