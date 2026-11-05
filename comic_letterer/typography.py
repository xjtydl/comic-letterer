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


def balanced_lines(text, measure, max_width, max_lines, forbidden=()):
    """Dynamic programming over legal text boundaries, not language inference."""
    if len(text) > 500:
        return None
    ends = [
        i
        for i in range(1, len(text) + 1)
        if legal_break(text, i) and i not in forbidden
    ]
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


def typeset(item, path, font_index, box, pad, lh, wrap_fn, font_bank=None):
    text = item["text"]
    fs = int(item["font_size"])
    base_role = item.get("font_role", "body")
    bank = font_bank or {
        base_role: {"path": path, "index": font_index, "family": "sans-serif"}
    }
    align = item.get("align", "center")
    flow = item.get("flow", "legacy")
    if align not in ("left", "center", "right"):
        raise ValueError("invalid align")
    if flow not in ("legacy", "balanced"):
        raise ValueError("invalid flow")
    tracking = number(item.get("tracking", 0), "tracking")
    if not -fs * 0.2 <= tracking <= fs:
        raise ValueError("tracking must be between -0.2 and 1 em")
    hscale = number(item.get("horizontal_scale", 1), "horizontal_scale", True)
    if not 0.9 <= hscale <= 1.1:
        raise ValueError("horizontal_scale must be 0.9..1.1")
    baseline_effect = item.get("baseline", {})
    fields(baseline_effect, "mode amplitude group", "baseline")
    mode = baseline_effect.get("mode", "straight")
    if mode not in ("straight", "bounce", "wave"):
        raise ValueError("baseline mode must be straight, bounce or wave")
    amplitude = number(baseline_effect.get("amplitude", fs * 0.08), "baseline amplitude")
    group = baseline_effect.get("group", 2)
    if not 0 <= amplitude <= fs * 0.25:
        raise ValueError("baseline amplitude must be 0..0.25 em")
    if type(group) is not int or not 1 <= group <= 12:
        raise ValueError("baseline group must be an integer 1..12")
    if item["kind"] == "sfx" and mode != "straight":
        raise ValueError("SFX uses arc/glyphs, not dialogue baseline")
    shifts = []
    cluster = -1
    for i, char in enumerate(text):
        # Keep combining marks with their base; no bidi/shaping claim is made.
        if not unicodedata.combining(char):
            cluster += 1
        phase = max(0, cluster) // group
        shifts.append(
            amplitude * (-1 if phase % 2 == 0 else 1)
            if mode == "bounce"
            else amplitude * math.sin(math.tau * phase / 6)
            if mode == "wave"
            else 0
        )
    spans = item.get("emphasis", [])
    if not isinstance(spans, list):
        raise ValueError("emphasis must be an array")
    styles = [(fs, None, base_role, shift) for shift in shifts]
    used = set()
    for span in spans:
        fields(span, "start end scale color font_role baseline_shift", "emphasis")
        a, b = span.get("start"), span.get("end")
        if type(a) is not int or type(b) is not int or not 0 <= a < b <= len(text):
            raise ValueError("invalid emphasis range")
        if used.intersection(range(a, b)):
            raise ValueError("overlapping emphasis ranges")
        used.update(range(a, b))
        scale = number(
            span.get("scale", 1 if "font_role" in span or "baseline_shift" in span else 1.2), "emphasis scale", True
        )
        if scale > 3:
            raise ValueError("emphasis scale exceeds 3")
        role = span.get("font_role", base_role)
        if not isinstance(role, str) or role not in bank:
            raise ValueError("emphasis font_role is not configured")
        ink = color(span["color"]) if "color" in span else None
        shift = number(span.get("baseline_shift", 0), "emphasis baseline_shift")
        if abs(shift) > fs:
            raise ValueError("emphasis baseline_shift must be within one em")
        for i in range(a, b):
            styles[i] = (max(1, round(fs * scale)), ink, role, shifts[i] + shift)
    fonts = {
        (size, role): ImageFont.truetype(
            bank[role]["path"], size, index=bank[role].get("index", 0)
        )
        for size, _, role, _ in styles
    }
    forbidden = set()
    keeps = item.get("keep_together", [])
    if not isinstance(keeps, list):
        raise ValueError("keep_together must be an array")
    for keep in keeps:
        fields(keep, "start end", "keep_together")
        a, b = keep.get("start"), keep.get("end")
        if (
            type(a) is not int
            or type(b) is not int
            or not 0 <= a < b <= len(text)
            or "\n" in text[a:b]
        ):
            raise ValueError("invalid keep_together range")
        forbidden.update(range(a + 1, b))

    def runs(start, end):
        out = []
        i = start
        while i < end:
            j = i + 1
            while j < end and styles[j] == styles[i] and not tracking:
                j += 1
            size, ink, role, shift = styles[i]
            seg = text[i:j]
            visible = seg.replace("\n", "")
            f = fonts[size, role]
            l, t, r, b = f.getbbox(visible, anchor="ls")
            advance = f.getlength(visible) * hscale
            out.append((seg, size, ink, role, advance, (l * hscale, t, r * hscale, b), shift))
            i = j
        return out

    @lru_cache(None)
    def measure(a, b):
        return (
            sum(r[4] for r in runs(a, b))
            + max(0, len(text[a:b].replace("\n", "")) - 1) * tracking
        )

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
        if forbidden.intersection(hints):
            raise ValueError("explicit break splits keep_together range")
        points = sorted(
            set(hints + [i + 1 for i, c in enumerate(text) if c == "\n"])
        ) + [len(text)]
        lines = []
        a = 0
        for b in points:
            if b > a:
                lines.append(text[a:b])
                a = b
    elif flow == "legacy" and not keeps and not spans and not tracking and hscale == 1 and mode == "straight":
        lines = wrap_fn(text, fonts[fs, base_role], inner)
    else:
        maxsize = max(size for size, role in fonts)
        maxlines = max(1, int((box[3] - 2 * pad) / (maxsize * lh)))
        lines = (
            balanced_lines(text, measure, inner, maxlines, forbidden)
            if flow == "balanced" and "\n" not in text
            else None
        )
        if lines is None:
            lines = []
            start = 0
            while start < len(text):
                lf = text.find("\n", start)
                limit = lf + 1 if lf >= 0 else len(text)
                ends = [
                    i
                    for i in range(start + 1, limit + 1)
                    if i not in forbidden and (i == limit or legal_break(text, i))
                ]
                fitting = [i for i in ends if measure(start, i) <= inner]
                end = max(fitting) if fitting else ends[0]
                lines.append(text[start:end])
                start = end
    min_shift = min(0, *(s[3] for s in styles))
    max_shift = max(0, *(s[3] for s in styles))
    ascent = max(f.getmetrics()[0] for f in fonts.values()) - min_shift
    descent = max(f.getmetrics()[1] for f in fonts.values()) + max_shift
    step = max(size for size, role in fonts) * lh + max_shift - min_shift
    baseline = (
        box[1] + (box[3] - (ascent + descent + (len(lines) - 1) * step)) / 2 + ascent
    )
    positions = []
    segments = []
    glyphboxes = []
    offset = 0
    for j, line in enumerate(lines):
        rowruns = runs(offset, offset + len(line))
        w = measure(offset, offset + len(line))
        x = (
            box[0] + pad
            if align == "left"
            else box[0] + box[2] - pad - w
            if align == "right"
            else box[0] + (box[2] - w) / 2
        )
        y = baseline + j * step
        positions.append((x, y, line))
        for seg, size, ink, role, advance, (l, t, r, b), shift in rowruns:
            segments.append(
                {
                    "x": x,
                    "y": y + shift,
                    "text": seg,
                    "font_size": size,
                    "color": ink,
                    "font_role": role,
                    "family": bank[role]["family"],
                    "advance": advance,
                    "horizontal_scale": hscale,
                }
            )
            glyphboxes.append(
                [x + min(0, l), y + shift + t, max(advance, r) - min(0, l), b - t]
            )
            x += advance + (tracking if seg != "\n" else 0)
        offset += len(line)
    return {
        "lines": lines,
        "positions": positions,
        "segments": segments,
        "glyphboxes": glyphboxes,
    }
