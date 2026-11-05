"""Lossless layout hints and measured mixed-size runs for horizontal text."""

from functools import lru_cache
import math
import unicodedata
from PIL import ImageFont
from .validation import fields, number, color

OPEN = set("（【《「『〔〈([{“‘")
CLOSE = set("，。！？；：、）》」』】〕〉,.;:!?)]}”’")


def legal_break(text, index):
    if index == 0 or index == len(text):
        return True
    a, b = text[index - 1], text[index]
    if a in OPEN or b in CLOSE or unicodedata.combining(b):
        return False
    if a == b and a in "…—":
        return False
    if a.isascii() and b.isascii() and a.isalnum() and b.isalnum():
        return False
    return True


def balanced_lines(text, measure, max_width, max_lines):
    """Dynamic programming over legal text boundaries, not language inference."""
    if len(text) > 500:
        return None
    ends = [i for i in range(1, len(text) + 1) if legal_break(text, i)]
    best = None
    minimum = max(1, math.ceil(measure(0, len(text)) / max_width))
    for count in range(minimum, min(max_lines, minimum + 3) + 1):

        @lru_cache(None)
        def solve(start, row):
            if row == count:
                return (0, []) if start == len(text) else (math.inf, [])
            choice = (math.inf, [])
            target = max_width * (1 - 0.16 * abs(2 * (row + 0.5) / count - 1))
            for end in ends:
                if end <= start:
                    continue
                w = measure(start, end)
                if w > max_width:
                    break
                if row == count - 1 and end != len(text):
                    continue
                cost = ((w - target) / max_width) ** 2
                if end < len(text):
                    cost += 0 if text[end - 1] in "，。！？；：、,.;:!? " else 0.08
                    if end - start == 1:
                        cost += 0.35
                future, tail = solve(end, row + 1)
                if cost + future < choice[0]:
                    choice = (cost + future, [end] + tail)
            return choice

        score, breaks = solve(0, 0)
        score = score / count + 0.025 * count
        if best is None or score < best[0]:
            best = (score, breaks)
    if best is None or not math.isfinite(best[0]):
        return None
    out = []
    start = 0
    for end in best[1]:
        out.append(text[start:end])
        start = end
    return out


def typeset(item, path, font_index, box, pad, lh, wrap_fn):
    text = item["text"]
    fs = item["font_size"]
    align = item.get("align", "center")
    if align not in ("left", "center", "right"):
        raise ValueError("align must be left, center or right")
    flow = item.get("flow", "legacy")
    if flow not in ("legacy", "balanced"):
        raise ValueError("flow must be legacy or balanced")
    spans = item.get("emphasis", [])
    if not isinstance(spans, list):
        raise ValueError("emphasis must be an array")
    styles = [(int(fs), None)] * len(text)
    used = set()
    for span in spans:
        fields(span, "start end scale color", "emphasis")
        a, b = span.get("start"), span.get("end")
        if type(a) is not int or type(b) is not int or not 0 <= a < b <= len(text):
            raise ValueError("invalid emphasis range")
        if used.intersection(range(a, b)):
            raise ValueError("overlapping emphasis ranges")
        used.update(range(a, b))
        scale = number(span.get("scale", 1.2), "emphasis scale", True)
        if scale > 3:
            raise ValueError("emphasis scale exceeds 3")
        ink = color(span["color"]) if "color" in span else None
        for i in range(a, b):
            styles[i] = (max(1, round(fs * scale)), ink)
    fonts = {
        size: ImageFont.truetype(path, size, index=font_index) for size, _ in styles
    }

    def runs(start, end):
        out = []
        i = start
        while i < end:
            j = i + 1
            while j < end and styles[j] == styles[i]:
                j += 1
            size, ink = styles[i]
            seg = text[i:j]
            visible = seg.replace("\n", "")
            out.append(
                (
                    seg,
                    size,
                    ink,
                    fonts[size].getlength(visible),
                    fonts[size].getbbox(visible, anchor="ls"),
                )
            )
            i = j
        return out

    @lru_cache(None)
    def measure(a, b):
        return sum(r[3] for r in runs(a, b))

    inner = max(1, box[2] - 2 * pad)
    if item["kind"] not in ("caption", "sfx", "floating"):
        inner *= 0.9 if item.get("shape") == "tv" else 0.78
    hints = item.get("breaks")
    if hints is not None:
        if (
            not isinstance(hints, list)
            or any(type(i) is not int or not 0 < i < len(text) for i in hints)
            or hints != sorted(set(hints))
        ):
            raise ValueError(
                "breaks must be strictly increasing internal character offsets"
            )
        points = sorted(
            set(hints + [i + 1 for i, c in enumerate(text) if c == "\n"])
        ) + [len(text)]
        lines = []
        a = 0
        for b in points:
            if b > a:
                lines.append(text[a:b])
                a = b
    elif flow == "balanced" and "\n" not in text:
        maxlines = max(1, int((box[3] - 2 * pad) / (max(fonts) * lh)))
        lines = balanced_lines(text, measure, inner, maxlines)
        if lines is None:
            lines = wrap_fn(text, fonts[max(fonts)], inner)
    else:
        lines = wrap_fn(text, fonts[max(fonts)], inner)
    ascent = max(f.getmetrics()[0] for f in fonts.values())
    descent = max(f.getmetrics()[1] for f in fonts.values())
    step = max(fonts) * lh
    block_h = ascent + descent + (len(lines) - 1) * step
    baseline = box[1] + (box[3] - block_h) / 2 + ascent
    positions = []
    segments = []
    glyphboxes = []
    offset = 0
    for j, line in enumerate(lines):
        rowruns = runs(offset, offset + len(line))
        w = sum(r[3] for r in rowruns)
        x = (
            box[0] + pad
            if align == "left"
            else box[0] + box[2] - pad - w
            if align == "right"
            else box[0] + (box[2] - w) / 2
        )
        y = baseline + j * step
        positions.append((x, y, line))
        for seg, size, ink, advance, (l, t, r, b) in rowruns:
            segments.append(
                {"x": x, "y": y, "text": seg, "font_size": size, "color": ink}
            )
            glyphboxes.append(
                [x + min(0, l), y + t, max(advance, r) - min(0, l), b - t]
            )
            x += advance
        offset += len(line)
    return {
        "lines": lines,
        "positions": positions,
        "segments": segments,
        "glyphboxes": glyphboxes,
    }
