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
from .validation import number, vector, fields, ident, color
from .typography import typeset
from .narrative import resolve_item, rough_contour, rough_tail, near_ink_edges
from .geometry import (
    edge_target,
    intersection,
    ribbon,
    sfx_glyph_layout,
    shadow_spec,
    polygon_box_overlap,
    polygons_overlap,
)

PRESETS = {
    "speech": "ellipse",
    "thought": "cloud",
    "shout": "burst",
    "whisper": "dashed",
    "weak": "wave",
    "electronic": "electric",
    "caption": "rect",
    "sfx": "text",
    "floating": "text",
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


def contour(box, kind, shape=None):
    x, y, w, h = box
    cx, cy = center(box)
    if kind == "caption":
        return f"M{x},{y} h{w} v{h} h{-w} Z"
    if shape == "tv":
        pts = []
        for j in range(160):
            a = 2 * math.pi * j / 160
            co = math.cos(a)
            si = math.sin(a)
            pts.append(
                (
                    cx + w / 2 * math.copysign(abs(co) ** 0.5, co),
                    cy + h / 2 * math.copysign(abs(si) ** 0.5, si),
                )
            )
        return "M" + " L".join(f"{a:.4f},{b:.4f}" for a, b in pts) + " Z"
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


def tail_geometry(
    box, target, fraction, kind, source_regions=(), shape=None, options=None
):
    options = options or {}
    cx, cy = center(box)
    tx, ty = target
    dx, dy = tx - cx, ty - cy
    power = 4 if shape == "tv" else 2
    q = (abs(dx / (box[2] / 2)) ** power + abs(dy / (box[3] / 2)) ** power) ** (
        1 / power
    )
    if q <= 1:
        return None
    if "root_angle" in options:
        a = math.radians(options["root_angle"])
        dx, dy = math.cos(a), math.sin(a)
        q = (abs(dx / (box[2] / 2)) ** power + abs(dy / (box[3] / 2)) ** power) ** (
            1 / power
        )
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
    distance = math.hypot(tx - bx, ty - by)
    requested = options.get("length", distance * fraction * available)
    permitted = max(0, distance * available - options.get("gap", 0))
    fraction = min(requested, permitted) / max(distance, 1e-8)
    tip = (bx + (tx - bx) * fraction, by + (ty - by) * fraction)
    length = math.hypot(dx, dy)
    nx, ny = -dy / length, dx / length
    half = options.get("width", min(box[2], box[3]) * 0.13) / 2
    root = (cx + dx / q * 0.70, cy + dy / q * 0.70)
    a = (root[0] + nx * half, root[1] + ny * half)
    b = (root[0] - nx * half, root[1] - ny * half)
    control = ((bx + tip[0]) / 2 + nx * half * 0.5, (by + tip[1]) / 2 + ny * half * 0.5)
    right_control = (bx, by)
    if "curve" in options:
        c = options["curve"]
        control = (c[0] + nx * half * 0.2, c[1] + ny * half * 0.2)
        right_control = (c[0] - nx * half * 0.2, c[1] - ny * half * 0.2)
    if kind == "electronic":
        mid = ((bx + tip[0]) / 2, (by + tip[1]) / 2)
        p = (mid[0] + nx * half, mid[1] + ny * half)
        d = f"M{a[0]},{a[1]} L{p[0]},{p[1]} L{mid[0]},{mid[1]} L{tip[0]},{tip[1]} L{b[0]},{b[1]} Z"
        polygon = [a, p, mid, tip, b]
        cells = [bounds(polygon, 2)]
    else:
        d = f"M{a[0]},{a[1]} Q{control[0]},{control[1]} {tip[0]},{tip[1]} Q{right_control[0]},{right_control[1]} {b[0]},{b[1]} Z"
        left, right, cells = [], [], []
        for j in range(33):
            t = j / 32
            u = 1 - t
            left.append(
                tuple(
                    u * u * a[k] + 2 * u * t * control[k] + t * t * tip[k]
                    for k in (0, 1)
                )
            )
            right.append(
                tuple(
                    u * u * b[k] + 2 * u * t * right_control[k] + t * t * tip[k]
                    for k in (0, 1)
                )
            )
            if j:
                cells.append(bounds([left[-2], left[-1], right[-2], right[-1]], 2))
        polygon = left + right[::-1]
    return {
        "d": d,
        "tip": tip,
        "box": bounds(polygon, 2),
        "boundary": (bx, by),
        "polygon": polygon,
        "cells": cells,
    }


def compile_page(job, font_path=None, font_index=0, background=None, fonts=None):
    """Return (editable SVG, JSON-serializable report). Never alter input.

    Structural errors raise ValueError. Layout problems produce report issues and
    a diagnostic SVG; callers must inspect report.ok before treating it as final.
    background may be a prevalidated PNG/JPEG data URL supplied by the CLI.
    """
    fields(
        job,
        "version width height panels items protected reading_width min_reading_font direction occlusions styles ink_edges tangent_distance min_tail_length",
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
    for key in ("panels", "items", "protected", "occlusions"):
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
        weight = face["OS/2"].usWeightClass if "OS/2" in face else 400
        style = "italic" if "post" in face and face["post"].italicAngle else "normal"
    report = {
        "version": 1,
        "ok": True,
        "font": {
            "family": family,
            "weight": weight,
            "style": style,
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

    font_bank = {
        "body": {
            "path": path,
            "index": font_index,
            "family": family,
            "cmap": cmap,
            "metadata": report["font"],
        }
    }
    for role, spec in (fonts or {}).items():
        ident(role)
        if role == "body":
            raise ValueError("body font is configured with font_path")
        fields(spec, "path index", "font configuration")
        fp = str(spec["path"])
        fi = spec.get("index", 0)
        if type(fi) is not int or fi < 0:
            raise ValueError("font index must be nonnegative integer")
        with TTFont(fp, fontNumber=fi) as face:
            ff = face["name"].getDebugName(1) or "sans-serif"
            cm = face.getBestCmap() or {}
            fw = face["OS/2"].usWeightClass if "OS/2" in face else 400
            fst = "italic" if "post" in face and face["post"].italicAngle else "normal"
        meta = {
            "family": ff,
            "weight": fw,
            "style": fst,
            "index": fi,
            "sha256": hashlib.sha256(Path(fp).read_bytes()).hexdigest(),
            "embedded": False,
        }
        font_bank[role] = {
            "path": fp,
            "index": fi,
            "family": ff,
            "cmap": cm,
            "metadata": meta,
        }
    report["fonts"] = {role: spec["metadata"] for role, spec in font_bank.items()}
    placed = []
    ids = set()
    orders = set()
    for raw in job.get("items", []):
        fields(
            raw,
            "id panel kind order speaker text expected_text font_size box size candidates target off_panel join_to padding line_height fill stroke text_color stroke_width tail_fraction rotation outlines breaks emphasis flow align shape butt join_curve allow_interruption hollow arc glyphs shadow source_mark font_role tracking horizontal_scale keep_together style caption_type voice double_outline tail",
            "item",
        )
        item = resolve_item(raw, job.get("styles", {}))
        role = item.get("font_role", "body")
        if not isinstance(role, str) or role not in font_bank:
            raise ValueError("font_role is not configured")
        selected_font = font_bank[role]
        path = selected_font["path"]
        font_index = selected_font["index"]
        cmap = selected_font["cmap"]
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
        if kind not in ("caption", "sfx", "floating") and (
            not isinstance(item.get("speaker"), str) or not item["speaker"].strip()
        ):
            raise ValueError("speaker required for voiced items")
        for flag in ("off_panel",):
            if flag in item and not isinstance(item[flag], bool):
                raise ValueError(f"{flag} must be boolean")
        for flag in ("hollow", "allow_interruption"):
            if flag in item and not isinstance(item[flag], bool):
                raise ValueError(f"{flag} must be boolean")
        if item.get("shape") not in (None, "ellipse", "tv"):
            raise ValueError("shape must be ellipse or tv")
        if item.get("shape") and kind not in ("speech", "whisper"):
            raise ValueError("shape override supports speech and whisper")
        butt = item.get("butt", [])
        if (
            not isinstance(butt, list)
            or len(set(butt)) != len(butt)
            or any(e not in ("top", "bottom", "left", "right") for e in butt)
        ):
            raise ValueError("butt must list distinct panel edges")
        if butt and kind in ("sfx", "floating"):
            raise ValueError("butt requires a balloon")
        if item.get("source_mark") not in (None, "squink"):
            raise ValueError("unknown source_mark")
        if kind != "sfx" and any(
            k in item for k in ("hollow", "arc", "glyphs", "shadow")
        ):
            raise ValueError("SFX options require sfx kind")
        shadow = shadow_spec(item.get("shadow"))
        if (
            kind == "sfx"
            and ("glyphs" in item or "arc" in item)
            and item.get("emphasis")
        ):
            raise ValueError("use glyph scale instead of emphasis with per-glyph SFX")
        if "join_curve" in item:
            vector(item["join_curve"], 2, "join_curve")
        if ("join_curve" in item or item.get("allow_interruption")) and not item.get(
            "join_to"
        ):
            raise ValueError("join options require join_to")
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
        visible_box = intersection(box, panels[pid]) if butt else box
        clipped_edges = {
            e
            for e, yes in zip(
                ("left", "top", "right", "bottom"),
                (
                    box[0] < panels[pid][0],
                    box[1] < panels[pid][1],
                    box[0] + box[2] > panels[pid][0] + panels[pid][2],
                    box[1] + box[3] > panels[pid][1] + panels[pid][3],
                ),
            )
            if yes
        }
        if not clipped_edges.issubset(set(butt)):
            issue("outside_panel", iid, "Balloon box exceeds its panel.")
        for name, pbox in protected:
            if overlap(visible_box, pbox):
                issue(
                    "protected_overlap", iid, f"Box overlaps protected region {name}."
                )
        layout_item = dict(item, font_size=fs, box=box, padding=pad)
        layout = typeset(
            layout_item, path, font_index, box, pad, lh, wrap_text, font_bank
        )
        if kind == "sfx" and ("glyphs" in item or "arc" in item):
            layout = sfx_glyph_layout(layout_item, path, font_index)
        for seg in layout["segments"]:
            sr = seg.get("font_role", role)
            missing = sorted(
                {
                    c
                    for c in seg["text"]
                    if c != "\n" and ord(c) not in font_bank[sr]["cmap"]
                }
            )
            if missing:
                issue(
                    "missing_glyph",
                    iid,
                    "Font "
                    + sr
                    + " lacks "
                    + ", ".join(f"U+{ord(c):04X}" for c in missing),
                )
        lines = layout["lines"]
        positions = layout["positions"]
        overflow = False
        for glyphbox in layout["glyphboxes"]:
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
            if butt and not contains(panels[pid], glyphbox):
                overflow = True
            if kind not in ("caption", "sfx", "floating"):
                inset = (
                    0.79
                    if kind == "shout"
                    else 0.91
                    if kind in ("thought", "weak", "electronic")
                    else 1
                )
                rx = (box[2] / 2 - pad) * inset
                ry = (box[3] / 2 - pad) * inset
                cx, cy = center(box)
                power = 4 if item.get("shape") == "tv" else 2
                if min(rx, ry) <= 0 or any(
                    abs((xx - cx) / max(rx, 1)) ** power
                    + abs((yy - cy) / max(ry, 1)) ** power
                    > 1
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
        if kind not in ("caption", "sfx", "floating") and item.get("tail", {}).get(
            "visible", not bool(item.get("join_to"))
        ):
            if target is None:
                issue(
                    "missing_target", iid, "Supply the mouth/head/device source point."
                )
            else:
                actual_target = (
                    edge_target(box, target, panels[pid])
                    if item.get("off_panel")
                    else target
                )
                actual_fraction = (
                    1 if item.get("off_panel") or item.get("source_mark") else fraction
                )
                tail = tail_geometry(
                    box,
                    actual_target,
                    actual_fraction,
                    kind,
                    []
                    if item.get("off_panel") or item.get("source_mark")
                    else [pb for _, pb in protected if contains(pb, [*target, 0, 0])],
                    item.get("shape"),
                    item.get("tail"),
                )
                if tail and item.get("voice") == "rough":
                    rough_tail(tail)
                if tail is None:
                    issue(
                        "target_inside_balloon",
                        iid,
                        "Source is inside balloon; reposition balloon.",
                    )
                else:
                    visible_length = (
                        math.dist(tail["boundary"], tail["tip"]) * rw / width
                    )
                    if visible_length < number(
                        job.get("min_tail_length", 0), "min_tail_length"
                    ):
                        issue(
                            "tail_too_short",
                            iid,
                            f"Tail is only {visible_length:.1f}px at reading size; move balloon or adjust root.",
                            "warning",
                        )
                    for name, pbox in protected:
                        if polygon_box_overlap(
                            tail["polygon"],
                            [
                                pbox[0] - sw,
                                pbox[1] - sw,
                                pbox[2] + 2 * sw,
                                pbox[3] + 2 * sw,
                            ],
                        ):
                            issue(
                                "tail_protected_overlap",
                                iid,
                                f"Tail envelope overlaps {name}; inspect actual curve.",
                            )
                    if not item.get("off_panel") and not contains(
                        panels[pid], tail["box"]
                    ):
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
            _segments=layout["segments"],
            _glyphboxes=layout["glyphboxes"],
            _visible=visible_box,
            _shadow=shadow,
            _family=selected_font["family"],
        )
        if item.get("double_outline"):
            g = item["double_outline"]
            outer = [box[0] - g, box[1] - g, box[2] + 2 * g, box[3] + 2 * g]
            if not contains(panels[pid], outer):
                issue("decoration_outside_panel", iid, "Double outline exceeds panel.")
            for name, pb in protected:
                if overlap(outer, pb):
                    issue(
                        "decoration_protected_overlap",
                        iid,
                        "Double outline overlaps " + name,
                    )
        for name in near_ink_edges(
            item,
            job.get("ink_edges", []),
            number(job.get("tangent_distance", 3), "tangent_distance"),
        ):
            issue(
                "near_ink_edge",
                iid,
                "Lettering approaches marked ink edge "
                + name
                + "; inspect tangent/overlap.",
                "warning",
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
            if other["order"] >= p["order"]:
                raise ValueError("join_to must precede current item")
            if idx == 0 or seq[idx - 1]["id"] != jid:
                if not p.get("allow_interruption"):
                    raise ValueError(
                        "join requires consecutive order or explicit allow_interruption"
                    )
                issue(
                    "interruption_join",
                    p["id"],
                    "Intentional interruption connector; inspect whole-page reading order.",
                    "warning",
                )
            if any(p[k] != other[k] for k in ("fill", "stroke", "stroke_width")):
                raise ValueError("joined styles must match")
    for p in placed:
        if (
            p["kind"] in ("caption", "floating", "sfx")
            or p["_tail"]
            or p.get("off_panel")
        ):
            continue
        component = {p["id"]}
        changed = True
        while changed:
            changed = False
            for q in placed:
                if q.get("join_to") and (
                    q["id"] in component or q["join_to"] in component
                ):
                    old = len(component)
                    component.update((q["id"], q["join_to"]))
                    changed |= len(component) > old
        if not any(by_id[i]["_tail"] for i in component):
            issue(
                "missing_attribution",
                p["id"],
                "Connected voice group needs an identifying tail.",
            )
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
            if overlap(a["_visible"], b["_visible"]) and not linked:
                issue("item_overlap", b["id"], f"Box overlaps {a['id']}.")
            if linked:
                for first, second in ((a, b), (b, a)):
                    if any(overlap(gb, second["box"]) for gb in first["_glyphboxes"]):
                        issue(
                            "join_text_overlap",
                            first["id"],
                            "Joined balloon overlaps neighbouring text.",
                        )
            for p, q in ((a, b), (b, a)):
                if p["_tail"] and polygon_box_overlap(p["_tail"]["polygon"], q["box"]):
                    issue(
                        "tail_item_overlap",
                        p["id"],
                        f"Tail envelope overlaps {q['id']}.",
                    )
            if (
                a["_tail"]
                and b["_tail"]
                and overlap(a["_tail"]["box"], b["_tail"]["box"])
                and polygons_overlap(a["_tail"]["polygon"], b["_tail"]["polygon"])
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
            {
                "version": 1,
                "font": report["font"],
                "fonts": report["fonts"],
                "source": job,
            },
            ensure_ascii=False,
        ),
    )
    defs = elem("defs", parent=root)
    masks = {i["id"]: [] for i in placed}
    seen_masks = set()
    for oc in job.get("occlusions", []):
        fields(oc, "id polygon items", "occlusion")
        oid = ident(oc.get("id"))
        if oid in seen_masks:
            raise ValueError("duplicate occlusion id")
        seen_masks.add(oid)
        if not isinstance(oc.get("polygon"), list) or len(oc["polygon"]) < 3:
            raise ValueError("occlusion polygon requires 3 points")
        points = [vector(p, 2, "occlusion point") for p in oc["polygon"]]
        if not isinstance(oc.get("items"), list) or not oc["items"]:
            raise ValueError("occlusion items required")
        for iid in oc["items"]:
            if iid not in masks:
                raise ValueError("occlusion references unknown item")
            masks[iid].append(points)
    for p in placed:
        iid = p["id"]
        panel = panels[p["panel"]]
        if p.get("butt") or p.get("off_panel"):
            clip = elem("clipPath", {"id": f"clip-{iid}"}, defs)
            elem("rect", dict(zip(("x", "y", "width", "height"), panel)), clip)
        if masks[iid]:
            mask = elem(
                "mask",
                {
                    "id": f"mask-{iid}",
                    "maskUnits": "userSpaceOnUse",
                    "x": 0,
                    "y": 0,
                    "width": width,
                    "height": height,
                    "style": "mask-type:luminance",
                },
                defs,
            )
            elem("rect", {"width": width, "height": height, "fill": "white"}, mask)
            for pts in masks[iid]:
                elem(
                    "polygon",
                    {"points": " ".join(f"{x},{y}" for x, y in pts), "fill": "black"},
                    mask,
                )
                hidden = any(polygon_box_overlap(pts, gb) for gb in p["_glyphboxes"])
                if p["kind"] == "sfx" and p["rotation"]:
                    angle = math.radians(p["rotation"])
                    cx, cy = center(p["box"])
                    glyph_polygons = []
                    for x, y, w, h in p["_glyphboxes"]:
                        glyph_polygons.append(
                            [
                                (
                                    cx
                                    + (gx - cx) * math.cos(angle)
                                    - (gy - cy) * math.sin(angle),
                                    cy
                                    + (gx - cx) * math.sin(angle)
                                    + (gy - cy) * math.cos(angle),
                                )
                                for gx, gy in [
                                    (x, y),
                                    (x + w, y),
                                    (x + w, y + h),
                                    (x, y + h),
                                ]
                            ]
                        )
                    hidden = any(
                        polygons_overlap(pts, polygon) for polygon in glyph_polygons
                    )
                if hidden:
                    issue(
                        "occluded_text",
                        iid,
                        "Foreground mask may hide source text; move the lettering.",
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
        attrs = {}
        if p.get("butt") or p.get("off_panel"):
            attrs["clip-path"] = f"url(#clip-{iid})"
        if masks[iid]:
            attrs["mask"] = f"url(#mask-{iid})"
        item_bottom = elem("g", attrs, bottom)
        item_connectors = elem("g", attrs, connectors)
        item_fills = elem("g", attrs, fills)
        if kind not in ("sfx", "floating"):
            if p.get("double_outline"):
                g = p["double_outline"]
                outer = [box[0] - g, box[1] - g, box[2] + 2 * g, box[3] + 2 * g]
                elem(
                    "path",
                    {
                        "d": contour(outer, kind, p.get("shape")),
                        "fill": p["fill"],
                        "stroke": p["stroke"],
                        "stroke-width": sw,
                    },
                    item_bottom,
                )
            d = (
                rough_contour(box)
                if p.get("voice") == "rough"
                else contour(
                    box,
                    "thought" if p.get("voice") == "telepathic" else kind,
                    p.get("shape"),
                )
            )
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
                item_bottom,
            )
            elem("path", {"id": f"fill-{iid}", "d": d, "fill": p["fill"]}, item_fills)
        voice = p.get("voice", "normal")
        if voice in ("breath", "telepathic", "singing"):
            x, y, w, h = box
            ink = p["stroke"]
            # Place marks in a reserved corner; exact glyph intersection is reported below.
            decoration = [x + 3, y + 3, 24, 22]
            if any(overlap(decoration, gb) for gb in p["_glyphboxes"]):
                issue(
                    "decoration_text_overlap",
                    iid,
                    "Voice marks overlap text; enlarge padding or move text.",
                )
            if voice == "singing":
                elem(
                    "path",
                    {
                        "d": f"M{x + 19},{y + 7} v15 M{x + 19},{y + 7} q9,1 8,8",
                        "fill": "none",
                        "stroke": ink,
                        "stroke-width": 2,
                    },
                    item_fills,
                )
                elem(
                    "ellipse",
                    {"cx": x + 15, "cy": y + 22, "rx": 5, "ry": 3, "fill": ink},
                    item_fills,
                )
            else:
                for side in (0, 1) if voice == "telepathic" else (0,):
                    mx = x + 8 if side == 0 else x + w - 24
                    my = y + 8 if side == 0 else y + h - 24
                    elem(
                        "path",
                        {
                            "d": f"M{mx},{my + 11} q4,-7 3,-11 M{mx + 8},{my + 13} q5,-6 5,-10",
                            "fill": "none",
                            "stroke": ink,
                            "stroke-width": 2,
                            "stroke-linecap": "round",
                        },
                        item_fills,
                    )
                    if side and any(
                        overlap([mx, my, 20, 20], gb) for gb in p["_glyphboxes"]
                    ):
                        issue(
                            "decoration_text_overlap",
                            iid,
                            "Telepathy marks overlap text.",
                        )
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
                        item_connectors,
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
                    item_connectors,
                )
        if p.get("source_mark") and tail:
            tip = tail["tip"]
            d = contour([tip[0] - 7, tip[1] - 7, 14, 14], "shout")
            elem(
                "path",
                {"d": d, "fill": p["fill"], "stroke": p["stroke"], "stroke-width": sw},
                item_connectors,
            )
        if p.get("join_to"):
            other = by_id[p["join_to"]]
            a = center(other["box"])
            b = center(box)
            half = min(box[2], box[3], other["box"][2], other["box"][3]) * 0.065
            jd, cells = ribbon(a, b, p.get("join_curve"), half)
            for name, pb in protected:
                if any(overlap(cell, pb) for cell in cells):
                    issue("join_protected_overlap", iid, f"Join crosses {name}.")
            for q in placed:
                if q["id"] not in (iid, other["id"]) and any(
                    overlap(cell, q["box"]) for cell in cells
                ):
                    issue("join_item_overlap", iid, f"Join crosses {q['id']}.")
            if any(not contains(panels[p["panel"]], cell) for cell in cells):
                issue("join_outside_panel", iid, "Connector exceeds its panel.")
            elem(
                "path",
                {
                    "id": f"join-{iid}",
                    "d": jd,
                    "fill": p["fill"],
                    "stroke": p["stroke"],
                    "stroke-width": sw,
                    "stroke-linejoin": "round",
                    **dash,
                },
                item_connectors,
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
                "data-caption-type": p.get("caption_type", ""),
                "data-voice": p.get("voice", "normal"),
                "color": p["text_color"],
                **attrs,
            },
            layer,
        )
        if kind == "sfx":
            group = elem("g", parent=group)
            cx, cy = center(box)
            group.set("transform", f"rotate({p['rotation']} {cx} {cy})")
            angle = math.radians(p["rotation"])
            corners = []
            envelope = box
            if "glyphs" in p or "arc" in p:
                pts = [
                    (gb[0] + dx * gb[2], gb[1] + dy * gb[3])
                    for gb in p["_glyphboxes"]
                    for dx in (0, 1)
                    for dy in (0, 1)
                ]
                if p["_shadow"]:
                    pts += [
                        (x + p["_shadow"]["dx"], y + p["_shadow"]["dy"])
                        for x, y in list(pts)
                    ]
                envelope = bounds(pts)
            for x in (envelope[0], envelope[0] + envelope[2]):
                for y in (envelope[1], envelope[1] + envelope[3]):
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
                "font-family": p["_family"],
                "data-font-role": p.get("font_role", "body"),
                "font-size": p["font_size"],
                "fill": "none" if p.get("hollow") else "currentColor",
                "xml:space": "preserve",
                "style": "white-space:pre",
                "font-kerning": "normal",
            },
            group,
        )
        for seg in p["_segments"]:
            sr = seg.get("font_role", p.get("font_role", "body"))
            fm = font_bank[sr]["metadata"]
            sa = {
                "x": seg["x"],
                "y": seg["y"],
                "font-size": seg["font_size"],
                "data-font-role": sr,
                "font-family": font_bank[sr]["family"],
                "font-weight": fm.get("weight", 400),
                "font-style": fm.get("style", "normal"),
            }
            if seg.get("horizontal_scale", 1) != 1 and seg.get("advance", 0) > 0:
                sa.update(textLength=seg["advance"], lengthAdjust="spacingAndGlyphs")
            if seg.get("color"):
                sa["fill"] = seg["color"]
            if "rotate" in seg:
                sa["rotate"] = seg["rotate"]
            elem("tspan", sa, node, text=seg["text"])
        if kind == "sfx":
            # Reuse one Unicode text source; outlines remain independently editable.
            group.remove(node)
            if p["_shadow"]:
                sh = p["_shadow"]
                for j in range(sh["steps"], 0, -1):
                    t = j / sh["steps"]
                    elem(
                        "use",
                        {
                            "href": f"#text-{iid}",
                            "transform": f"translate({sh['dx'] * t} {sh['dy'] * t})",
                            "color": sh["color"],
                            "stroke": sh["color"],
                            "stroke-width": max(
                                [o["width"] for o in p["outlines"]] or [1]
                            ),
                            "stroke-linejoin": "round",
                            "aria-hidden": "true",
                        },
                        group,
                    )
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
                "glyph_boxes": p["_glyphboxes"],
                "tail_tip": list(tail["tip"]) if tail else None,
                "tail_length": math.dist(tail["boundary"], tail["tip"])
                if tail
                else None,
                "caption_type": p.get("caption_type"),
                "voice": p.get("voice", "normal"),
                "resolved_style": {
                    k: p[k]
                    for k in (
                        "font_size",
                        "font_role",
                        "kind",
                        "fill",
                        "stroke",
                        "text_color",
                        "shape",
                        "voice",
                        "caption_type",
                    )
                    if k in p
                },
                "text_preserved": "".join(p["_lines"]) == p["text"],
            }
        )
    report["ok"] = not any(i["severity"] == "error" for i in report["issues"])
    return ET.tostring(root, encoding="unicode"), report
