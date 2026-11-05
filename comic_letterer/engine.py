"""Original, deterministic lettering compiler. All coordinates are page-global pixels."""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
from pathlib import Path
from xml.etree import ElementTree as ET

from fontTools.ttLib import TTFont
from PIL import ImageFont

PRESETS = {
    "speech": "ellipse",
    "thought": "cloud",
    "shout": "burst",
    "whisper": "dashed",
    "weak": "wave",
    "electronic": "electric",
    "caption": "rect",
    "sfx": "text",
}
NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", NS)
OPEN = set("（【《「『〔〈([{“‘")
CLOSE = set("，。！？；：、）》」』】〕〉,.;:!?)]}”’")


def elem(tag, attrs=None, parent=None, text=None):
    node = ET.Element(f"{{{NS}}}{tag}", {k: str(v) for k, v in (attrs or {}).items()})
    node.text = text
    if parent is not None:
        parent.append(node)
    return node


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


def find_font():
    """Convenience only; production jobs should pass an explicit font."""
    candidates = [
        os.environ.get("COMIC_LETTERER_FONT", ""),
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "C:/Windows/Fonts/msyh.ttc",
    ]
    for path in candidates:
        if path and Path(path).is_file():
            return path
    raise ValueError("No font found; supply --font or COMIC_LETTERER_FONT")


def wrap_text(text, font, width):
    """Lossless greedy wrap, preferring Latin spaces and CJK punctuation boundaries.

    An indivisible punctuation unit may exceed width; compiler reports overflow.
    Explicit newlines remain in line strings so joining lines recovers the source.
    """
    number(width, "wrap width", positive=True)
    lines = []
    for paragraph in text.splitlines(keepends=True) or [""]:
        rest = paragraph
        while rest:
            end = 0
            while (
                end < len(rest)
                and rest[end] != "\n"
                and font.getlength(rest[: end + 1]) <= width
            ):
                end += 1
            if end == len(rest):
                lines.append(rest)
                break
            if rest[end : end + 1] == "\n":
                lines.append(rest[: end + 1])
                rest = rest[end + 1 :]
                continue
            end = max(1, end)
            # Prefer a word boundary when splitting a Latin word.
            if (
                end < len(rest)
                and rest[end - 1].isascii()
                and rest[end].isascii()
                and rest[end - 1].isalnum()
                and rest[end].isalnum()
            ):
                space = rest.rfind(" ", 0, end)
                if space >= 0:
                    end = space + 1
            while end > 1 and rest[end - 1] in OPEN:
                end -= 1
            while end < len(rest) and rest[end] in CLOSE:
                end += 1
            # A leading opener and its first glyph stay together even in tiny boxes.
            if end == 1 and rest[0] in OPEN and len(rest) > 1:
                end = 2
                while end < len(rest) and rest[end] in CLOSE:
                    end += 1
            lines.append(rest[:end])
            rest = rest[end:]
    return lines or [""]


def overlap(a, b):
    return max(0, min(a[0] + a[2], b[0] + b[2]) - max(a[0], b[0])) * max(
        0, min(a[1] + a[3], b[1] + b[3]) - max(a[1], b[1])
    )


def contains(a, b):
    return (
        a[0] <= b[0]
        and a[1] <= b[1]
        and a[0] + a[2] >= b[0] + b[2]
        and a[1] + a[3] >= b[1] + b[3]
    )


def bounds(points, pad=0):
    xs, ys = zip(*points)
    return [
        min(xs) - pad,
        min(ys) - pad,
        max(xs) - min(xs) + 2 * pad,
        max(ys) - min(ys) + 2 * pad,
    ]


def center(box):
    x, y, w, h = box
    return x + w / 2, y + h / 2


def contour(box, kind):
    x, y, w, h = box
    cx, cy = center(box)
    if kind == "caption":
        return f"M{x},{y} h{w} v{h} h{-w} Z"
    if kind in ("speech", "whisper"):
        return f"M{x},{cy} a{w / 2},{h / 2} 0 1 0 {w},0 a{w / 2},{h / 2} 0 1 0 {-w},0 Z"
    pts = []
    n = 160 if kind in ("thought", "weak") else 48
    for j in range(n):
        a = 2 * math.pi * j / n
        if kind == "thought":
            r = 0.94 + 0.06 * math.cos(12 * a)
        elif kind == "weak":
            r = 0.96 + 0.025 * math.sin(11 * a) + 0.015 * math.cos(7 * a)
        elif kind == "shout":
            r = 1 if j % 2 == 0 else 0.82 + 0.035 * math.sin(j * 2.7)
        else:
            r = 1 if j % 2 == 0 else 0.90
        pts.append((cx + w / 2 * r * math.cos(a), cy + h / 2 * r * math.sin(a)))
    return "M" + " L".join(f"{a:.4f},{b:.4f}" for a, b in pts) + " Z"


def tail_geometry(box, target, fraction, kind, source_regions=()):
    cx, cy = center(box)
    tx, ty = target
    dx, dy = tx - cx, ty - cy
    q = math.hypot(dx / (box[2] / 2), dy / (box[3] / 2))
    if q <= 1:
        return None
    bx, by = cx + dx / q, cy + dy / q
    # Shorten against the first enclosing source-region boundary, preserving the
    # source direction. Unrelated obstacles remain reported rather than hidden.
    available = 1.0
    for region in source_regions:
        entry, leave = 0.0, 1.0
        for start, delta, low, high in (
            (bx, tx - bx, region[0], region[0] + region[2]),
            (by, ty - by, region[1], region[1] + region[3]),
        ):
            if abs(delta) > 1e-9:
                t0, t1 = sorted(((low - start) / delta, (high - start) / delta))
                entry, leave = max(entry, t0), min(leave, t1)
        if entry <= leave:
            available = min(available, max(0.0, entry))
    fraction *= available
    tip = (bx + (tx - bx) * fraction, by + (ty - by) * fraction)
    length = math.hypot(dx, dy)
    nx, ny = -dy / length, dx / length
    half = min(box[2], box[3]) * 0.065
    root = (cx + dx / q * 0.70, cy + dy / q * 0.70)
    a = (root[0] + nx * half, root[1] + ny * half)
    b = (root[0] - nx * half, root[1] - ny * half)
    control = ((bx + tip[0]) / 2 + nx * half * 0.5, (by + tip[1]) / 2 + ny * half * 0.5)
    if kind == "electronic":
        mid = ((bx + tip[0]) / 2, (by + tip[1]) / 2)
        p = (mid[0] + nx * half, mid[1] + ny * half)
        d = f"M{a[0]},{a[1]} L{p[0]},{p[1]} L{mid[0]},{mid[1]} L{tip[0]},{tip[1]} L{b[0]},{b[1]} Z"
    else:
        d = f"M{a[0]},{a[1]} Q{control[0]},{control[1]} {tip[0]},{tip[1]} Q{bx},{by} {b[0]},{b[1]} Z"
    return {
        "d": d,
        "tip": tip,
        "box": bounds([a, b, tip, control], 2),
        "boundary": (bx, by),
    }


def compile_page(job, font_path=None, font_index=0, background=None):
    """Return (editable SVG, JSON-serializable report). Never alter input.

    Structural errors raise ValueError. Layout problems produce report issues and
    a diagnostic SVG; callers must inspect report.ok before treating it as final.
    background may be a prevalidated PNG/JPEG data URL supplied by the CLI.
    """
    fields(
        job,
        "version width height panels items protected reading_width min_reading_font direction",
        "page",
    )
    if type(job.get("version")) is not int or job["version"] != 1:
        raise ValueError("version must be 1")
    width = number(job.get("width"), "width", True)
    height = number(job.get("height"), "height", True)
    if max(width, height) > 50000:
        raise ValueError("page dimensions exceed 50000px")
    direction = job.get("direction", "ltr")
    if direction not in ("ltr", "rtl"):
        raise ValueError("direction must be ltr or rtl")
    rw = number(job.get("reading_width", width), "reading_width", True)
    min_reading = number(job.get("min_reading_font", 14), "min_reading_font", True)
    for key in ("panels", "items", "protected"):
        if not isinstance(job.get(key, []), list):
            raise ValueError(f"{key} must be an array")
    if "items" not in job:
        raise ValueError("items required")
    panels = {}
    for p in job.get("panels", []):
        fields(p, "id box", "panel")
        pid = ident(p.get("id"))
        if pid in panels:
            raise ValueError("duplicate panel id")
        panels[pid] = vector(p.get("box"), 4, "panel box", True)
        if not contains([0, 0, width, height], panels[pid]):
            raise ValueError("panel outside page")
    if not panels:
        raise ValueError("panels required")
    protected = []
    for p in job.get("protected", []):
        fields(p, "id box", "protected")
        protected.append(
            (ident(p.get("id")), vector(p.get("box"), 4, "protected box", True))
        )
    path = str(font_path or find_font())
    if (
        isinstance(font_index, bool)
        or not isinstance(font_index, int)
        or font_index < 0
    ):
        raise ValueError("font_index must be a nonnegative integer")
    with TTFont(path, fontNumber=font_index) as face:
        cmap = face.getBestCmap() or {}
        family = face["name"].getDebugName(1) or "sans-serif"
    report = {
        "version": 1,
        "ok": True,
        "font": {
            "family": family,
            "index": font_index,
            "sha256": hashlib.sha256(Path(path).read_bytes()).hexdigest(),
            "embedded": False,
        },
        "reading_width": rw,
        "issues": [],
        "items": [],
    }

    def issue(code, item, message, severity="error"):
        report["issues"].append(
            {"code": code, "item": item, "severity": severity, "message": message}
        )

    placed = []
    ids = set()
    orders = set()
    for raw in job.get("items", []):
        fields(
            raw,
            "id panel kind order speaker text expected_text font_size box size candidates target off_panel join_to padding line_height fill stroke text_color stroke_width tail_fraction rotation outlines",
            "item",
        )
        item = dict(raw)
        iid = ident(item.get("id"))
        if iid in ids:
            raise ValueError("duplicate item id")
        ids.add(iid)
        kind = item.get("kind")
        if not isinstance(kind, str) or kind not in PRESETS:
            raise ValueError(f"unknown kind: {kind}")
        pid = item.get("panel")
        if not isinstance(pid, str) or pid not in panels:
            raise ValueError("unknown panel")
        order = number(item.get("order"), "order")
        if (pid, order) in orders:
            raise ValueError("duplicate order in panel")
        orders.add((pid, order))
        text = item.get("text")
        if not isinstance(text, str) or not text:
            raise ValueError("text must be nonempty string")
        if any(
            (ord(c) < 32 and c != "\n")
            or 0xD800 <= ord(c) <= 0xDFFF
            or ord(c) in (0xFFFE, 0xFFFF)
            for c in text
        ):
            raise ValueError(
                "text contains unsupported control or invalid XML characters"
            )
        if "expected_text" in item and text != item["expected_text"]:
            raise ValueError(f"frozen text mismatch: {iid}")
        if kind not in ("caption", "sfx") and (
            not isinstance(item.get("speaker"), str) or not item["speaker"].strip()
        ):
            raise ValueError("speaker required for voiced items")
        for flag in ("off_panel",):
            if flag in item and not isinstance(item[flag], bool):
                raise ValueError(f"{flag} must be boolean")
        if item.get("off_panel"):
            raise ValueError("off-panel border tails are not supported in v0.1")
        if kind != "sfx" and "outlines" in item:
            raise ValueError("outlines is supported only for sfx")
        fs = number(item.get("font_size", 28), "font_size", True)
        if fs > 1000:
            raise ValueError("font_size exceeds 1000px")
        # Pillow uses integer pixels. Reject fractional values to avoid silent rounding.
        if fs != int(fs):
            raise ValueError("font_size must be integer pixels")
        pad = number(item.get("padding", fs * 0.6), "padding")
        if pad < 0:
            raise ValueError("padding must be nonnegative")
        lh = number(item.get("line_height", 1.25), "line_height", True)
        sw = number(item.get("stroke_width", 2), "stroke_width", True)
        fraction = number(item.get("tail_fraction", 0.5), "tail_fraction", True)
        if fraction >= 1:
            raise ValueError("tail_fraction must be below 1")
        rotation = number(item.get("rotation", 0), "rotation")
        if rotation and kind != "sfx":
            raise ValueError("rotation is supported only for sfx")
        fill = color(item.get("fill", "#FFFFFF" if kind != "caption" else "#FFF4D8"))
        stroke = color(item.get("stroke", "#20202A"))
        ink = color(item.get("text_color", "#20202A"))
        target = vector(item["target"], 2, "target") if "target" in item else None
        if item.get("off_panel") and target and contains(panels[pid], [*target, 0, 0]):
            raise ValueError("off_panel target must be outside its panel")
        outlines = (
            item.get(
                "outlines",
                [{"color": "#20202A", "width": 8}, {"color": "#FFFFFF", "width": 4}],
            )
            if kind == "sfx"
            else []
        )
        if not isinstance(outlines, list):
            raise ValueError("outlines must be an array")
        prev = math.inf
        for outline in outlines:
            fields(outline, "color width", "outline")
            color(outline.get("color"))
            ow = number(outline.get("width"), "outline width", True)
            if ow >= prev:
                raise ValueError("outline widths must decrease back to front")
            prev = ow
        font = ImageFont.truetype(path, int(fs), index=font_index)
        if "box" in item:
            if "size" in item or "candidates" in item:
                raise ValueError("box and auto placement are exclusive")
            box = vector(item["box"], 4, "box", True)
        else:
            size = vector(item.get("size"), 2, "size")
            if min(size) <= 0:
                raise ValueError("size must be positive")
            px, py, pw, ph = panels[pid]
            bw, bh = size
            candidates = item.get("candidates")
            if candidates is None:
                xs = [px + 12 + (pw - bw - 24) * j / 4 for j in range(5)]
                if direction == "rtl":
                    xs.reverse()
                candidates = [
                    [x, py + 12 + (ph - bh - 24) * k / 4, bw, bh]
                    for k in range(5)
                    for x in xs
                ]
            if not isinstance(candidates, list):
                raise ValueError("candidates must be an array")
            candidates = [vector(c, 4, "candidate", True) for c in candidates]
            if not candidates:
                raise ValueError("candidates must be nonempty")

            def score(b):
                return (
                    (0 if contains(panels[pid], b) else width * height * 100)
                    + sum(overlap(b, p) for _, p in protected)
                    + sum(overlap(b, p["box"]) for p in placed)
                )

            box = min(candidates, key=score)
        if not contains(panels[pid], box):
            issue("outside_panel", iid, "Balloon box exceeds its panel.")
        for name, pbox in protected:
            if overlap(box, pbox):
                issue(
                    "protected_overlap", iid, f"Box overlaps protected region {name}."
                )
        missing = sorted({c for c in text if c != "\n" and ord(c) not in cmap})
        if missing:
            issue(
                "missing_glyph",
                iid,
                "Font lacks " + ", ".join(f"U+{ord(c):04X}" for c in missing),
            )
        inner_w = max(1, box[2] - 2 * pad)
        if kind not in ("caption", "sfx"):
            inner_w *= 0.78
        lines = wrap_text(text, font, inner_w)
        ascent, descent = font.getmetrics()
        step = fs * lh
        block_h = ascent + descent + (len(lines) - 1) * step
        baseline = box[1] + (box[3] - block_h) / 2 + ascent
        overflow = False
        positions = []
        for j, line in enumerate(lines):
            visible = line.removesuffix("\n")
            advance = font.getlength(visible)
            x = box[0] + (box[2] - advance) / 2
            y = baseline + j * step
            positions.append((x, y, line))
            left, top, right, bottom = font.getbbox(visible, anchor="ls")
            glyphbox = [
                x + min(0, left),
                y + top,
                max(advance, right) - min(0, left),
                bottom - top,
            ]
            if not contains(
                [
                    box[0] + pad,
                    box[1] + pad,
                    max(0, box[2] - 2 * pad),
                    max(0, box[3] - 2 * pad),
                ],
                glyphbox,
            ):
                overflow = True
            if kind not in ("caption", "sfx"):
                rx = (box[2] / 2 - pad) * (
                    0.79
                    if kind == "shout"
                    else 0.91
                    if kind in ("thought", "weak", "electronic")
                    else 1
                )
                ry = (box[3] / 2 - pad) * (
                    0.79
                    if kind == "shout"
                    else 0.91
                    if kind in ("thought", "weak", "electronic")
                    else 1
                )
                cx, cy = center(box)
                if min(rx, ry) <= 0 or any(
                    ((xx - cx) / max(rx, 1)) ** 2 + ((yy - cy) / max(ry, 1)) ** 2 > 1
                    for xx in (glyphbox[0], glyphbox[0] + glyphbox[2])
                    for yy in (glyphbox[1], glyphbox[1] + glyphbox[3])
                ):
                    overflow = True
        if overflow:
            issue(
                "text_overflow",
                iid,
                "Measured text exceeds padded contour; move or enlarge box. Font unchanged.",
            )
        if fs * rw / width < min_reading:
            issue(
                "reading_text_small",
                iid,
                f"Reading size is {fs * rw / width:.1f}px; threshold is {min_reading:g}px.",
                "warning",
            )
        tail = None
        if kind not in ("caption", "sfx") and not item.get("join_to"):
            if target is None:
                issue(
                    "missing_target", iid, "Supply the mouth/head/device source point."
                )
            else:
                tail = tail_geometry(
                    box,
                    target,
                    fraction,
                    kind,
                    [pb for _, pb in protected if contains(pb, [*target, 0, 0])],
                )
                if tail is None:
                    issue(
                        "target_inside_balloon",
                        iid,
                        "Source is inside balloon; reposition balloon.",
                    )
                else:
                    for name, pbox in protected:
                        if overlap(tail["box"], pbox):
                            issue(
                                "tail_protected_overlap",
                                iid,
                                f"Tail envelope overlaps {name}; inspect actual curve.",
                            )
                    if not contains(panels[pid], tail["box"]):
                        issue("tail_outside_panel", iid, "Tail envelope exceeds panel.")
        item.update(
            box=box,
            font_size=fs,
            padding=pad,
            fill=fill,
            stroke=stroke,
            text_color=ink,
            stroke_width=sw,
            rotation=rotation,
            outlines=outlines,
            _positions=positions,
            _tail=tail,
            _lines=lines,
        )
        placed.append(item)
    by_id = {i["id"]: i for i in placed}
    for p in placed:
        jid = p.get("join_to")
        if jid is not None:
            if not isinstance(jid, str) or jid not in by_id:
                raise ValueError("join_to references unknown item")
            other = by_id[jid]
            if not p.get("speaker") or p.get("speaker") != other.get("speaker"):
                raise ValueError("join requires same speaker")
            if (
                p["panel"] != other["panel"]
                or p["kind"] != other["kind"]
                or p["kind"] not in ("speech", "whisper")
            ):
                raise ValueError(
                    "joins require speech/whisper of same kind in same panel"
                )
            seq = sorted(
                [i for i in placed if i["panel"] == p["panel"]],
                key=lambda i: i["order"],
            )
            idx = seq.index(p)
            if idx == 0 or seq[idx - 1]["id"] != jid:
                raise ValueError("join requires consecutive order")
            if any(p[k] != other[k] for k in ("fill", "stroke", "stroke_width")):
                raise ValueError("joined styles must match")
    for pid in panels:
        seq = sorted([p for p in placed if p["panel"] == pid], key=lambda i: i["order"])
        for a, b in zip(seq, seq[1:]):
            ac, bc = center(a["box"]), center(b["box"])
            if bc[1] < ac[1] - max(a["box"][3], b["box"][3]) * 0.5 or (
                abs(bc[1] - ac[1]) < min(a["box"][3], b["box"][3]) * 0.5
                and (bc[0] < ac[0] if direction == "ltr" else bc[0] > ac[0])
            ):
                issue(
                    "reading_order",
                    b["id"],
                    "Placement may contradict declared reading order.",
                    "warning",
                )
    for j, a in enumerate(placed):
        for b in placed[j + 1 :]:
            linked = a.get("join_to") == b["id"] or b.get("join_to") == a["id"]
            if overlap(a["box"], b["box"]) and not linked:
                issue("item_overlap", b["id"], f"Box overlaps {a['id']}.")
            if linked:
                for ax, ay, line in a["_positions"]:
                    # Conservative line box; joined contours may overlap but text must not.
                    if overlap(
                        [
                            ax,
                            ay - a["font_size"],
                            len(line) * a["font_size"],
                            a["font_size"],
                        ],
                        b["box"],
                    ):
                        issue(
                            "join_text_overlap",
                            a["id"],
                            "Joined balloon may cover neighbouring text.",
                        )
                        break
            for p, q in ((a, b), (b, a)):
                if p["_tail"] and overlap(p["_tail"]["box"], q["box"]):
                    issue(
                        "tail_item_overlap",
                        p["id"],
                        f"Tail envelope overlaps {q['id']}.",
                    )
            if (
                a["_tail"]
                and b["_tail"]
                and overlap(a["_tail"]["box"], b["_tail"]["box"])
            ):
                issue(
                    "tail_crossing",
                    b["id"],
                    f"Tail envelopes intersect {a['id']}; inspect curves.",
                    "warning",
                )
    root = elem(
        "svg",
        {
            "width": width,
            "height": height,
            "viewBox": f"0 0 {width} {height}",
            "role": "img",
        },
    )
    elem("title", parent=root, text="Editable comic lettering")
    elem(
        "metadata",
        parent=root,
        text=json.dumps(
            {"version": 1, "font": report["font"], "source": job}, ensure_ascii=False
        ),
    )
    art = elem("g", {"id": "art"}, root)
    if background:
        if not re.fullmatch(
            r"data:image/(?:png|jpeg);base64,[A-Za-z0-9+/=]+", background
        ):
            raise ValueError("background must be a PNG/JPEG data URL")
        elem(
            "image",
            {
                "href": background,
                "width": width,
                "height": height,
                "preserveAspectRatio": "none",
            },
            art,
        )
    balloons = elem("g", {"id": "balloons"}, root)
    bottom = elem("g", {"id": "balloon-outlines"}, balloons)
    connectors = elem("g", {"id": "tails-and-joins"}, balloons)
    fills = elem("g", {"id": "balloon-fills"}, balloons)
    text_layer = elem("g", {"id": "text"}, root)
    sfx_layer = elem("g", {"id": "sfx"}, root)
    for p in placed:
        iid = p["id"]
        kind = p["kind"]
        box = p["box"]
        sw = p["stroke_width"]
        dash = {"stroke-dasharray": f"{sw * 3} {sw * 2}"} if kind == "whisper" else {}
        if kind != "sfx":
            d = contour(box, kind)
            elem(
                "path",
                {
                    "id": f"outline-{iid}",
                    "d": d,
                    "fill": p["fill"],
                    "stroke": p["stroke"],
                    "stroke-width": sw * 2,
                    "stroke-linejoin": "round",
                    **dash,
                },
                bottom,
            )
            elem("path", {"id": f"fill-{iid}", "d": d, "fill": p["fill"]}, fills)
        tail = p["_tail"]
        if tail:
            if kind == "thought":
                bx, by = tail["boundary"]
                tx, ty = tail["tip"]
                for j, t in enumerate((0.20, 0.55, 1.0)):
                    elem(
                        "circle",
                        {
                            "cx": bx + (tx - bx) * t,
                            "cy": by + (ty - by) * t,
                            "r": max(2, min(box[2:]) * 0.045 * (1 - j * 0.28)),
                            "fill": p["fill"],
                            "stroke": p["stroke"],
                            "stroke-width": sw,
                        },
                        connectors,
                    )
            else:
                elem(
                    "path",
                    {
                        "id": f"tail-{iid}",
                        "d": tail["d"],
                        "fill": p["fill"],
                        "stroke": p["stroke"],
                        "stroke-width": sw,
                        "stroke-linejoin": "round",
                        **dash,
                    },
                    connectors,
                )
        if p.get("join_to"):
            other = by_id[p["join_to"]]
            a = center(other["box"])
            b = center(box)
            dx, dy = b[0] - a[0], b[1] - a[1]
            length = math.hypot(dx, dy)
            if length == 0:
                raise ValueError("joined centers must differ")
            nx, ny = -dy / length, dx / length
            half = min(box[2], box[3], other["box"][2], other["box"][3]) * 0.065
            points = [
                (a[0] + nx * half, a[1] + ny * half),
                (b[0] + nx * half * 0.7, b[1] + ny * half * 0.7),
                (b[0] - nx * half * 0.7, b[1] - ny * half * 0.7),
                (a[0] - nx * half, a[1] - ny * half),
            ]
            jb = bounds(points, sw)
            for name, pb in protected:
                if overlap(jb, pb):
                    issue(
                        "join_protected_overlap", iid, f"Join envelope overlaps {name}."
                    )
            for q in placed:
                if q["id"] not in (iid, other["id"]) and overlap(jb, q["box"]):
                    issue(
                        "join_item_overlap", iid, f"Join envelope overlaps {q['id']}."
                    )
            elem(
                "path",
                {
                    "id": f"join-{iid}",
                    "d": "M" + " L".join(f"{x},{y}" for x, y in points) + " Z",
                    "fill": p["fill"],
                    "stroke": p["stroke"],
                    "stroke-width": sw,
                    "stroke-linejoin": "round",
                    **dash,
                },
                connectors,
            )
        layer = sfx_layer if kind == "sfx" else text_layer
        group = elem(
            "g",
            {
                "id": f"item-{iid}",
                "data-panel": p["panel"],
                "data-order": p["order"],
                "data-speaker": p.get("speaker", ""),
                "data-kind": kind,
            },
            layer,
        )
        if kind == "sfx":
            cx, cy = center(box)
            group.set("transform", f"rotate({p['rotation']} {cx} {cy})")
            angle = math.radians(p["rotation"])
            corners = []
            for x in (box[0], box[0] + box[2]):
                for y in (box[1], box[1] + box[3]):
                    corners.append(
                        (
                            cx
                            + (x - cx) * math.cos(angle)
                            - (y - cy) * math.sin(angle),
                            cy
                            + (x - cx) * math.sin(angle)
                            + (y - cy) * math.cos(angle),
                        )
                    )
            rb = bounds(corners, max([o["width"] / 2 for o in p["outlines"]] or [0]))
            if not contains(panels[p["panel"]], rb):
                issue("sfx_outside_panel", iid, "Rotated SFX envelope exceeds panel.")
            for name, pb in protected:
                if overlap(rb, pb):
                    issue(
                        "sfx_protected_overlap",
                        iid,
                        f"Rotated SFX envelope overlaps {name}.",
                    )
        node = elem(
            "text",
            {
                "id": f"text-{iid}",
                "font-family": family,
                "font-size": p["font_size"],
                "fill": p["text_color"],
                "xml:space": "preserve",
                "style": "white-space:pre",
                "font-kerning": "normal",
            },
            group,
        )
        for x, y, line in p["_positions"]:
            elem("tspan", {"x": x, "y": y}, node, text=line)
        if kind == "sfx":
            # Reuse one Unicode text source; outlines remain independently editable.
            group.remove(node)
            for o in p["outlines"]:
                elem(
                    "use",
                    {
                        "href": f"#text-{iid}",
                        "stroke": o["color"],
                        "stroke-width": o["width"],
                        "stroke-linejoin": "round",
                        "aria-hidden": "true",
                    },
                    group,
                )
            group.append(node)
        report["items"].append(
            {
                "id": iid,
                "kind": kind,
                "box": box,
                "font_size": p["font_size"],
                "reading_font_size": p["font_size"] * rw / width,
                "lines": p["_lines"],
                "tail_tip": list(tail["tip"]) if tail else None,
                "text_preserved": "".join(p["_lines"]) == p["text"],
            }
        )
    report["ok"] = not any(i["severity"] == "error" for i in report["issues"])
    return ET.tostring(root, encoding="unicode"), report
