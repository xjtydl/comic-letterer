"""Original panel-edge and curved-ribbon constructions."""

import math
from .validation import vector, number, fields, color


def edge_target(box, target, panel):
    cx = box[0] + box[2] / 2
    cy = box[1] + box[3] / 2
    dx = target[0] - cx
    dy = target[1] - cy
    values = []
    if dx > 0:
        values.append((panel[0] + panel[2] - cx) / dx)
    if dx < 0:
        values.append((panel[0] - cx) / dx)
    if dy > 0:
        values.append((panel[1] + panel[3] - cy) / dy)
    if dy < 0:
        values.append((panel[1] - cy) / dy)
    t = min(v for v in values if v >= 0)
    return [cx + dx * t, cy + dy * t]


def intersection(a, b):
    x = max(a[0], b[0])
    y = max(a[1], b[1])
    return [
        x,
        y,
        max(0, min(a[0] + a[2], b[0] + b[2]) - x),
        max(0, min(a[1] + a[3], b[1] + b[3]) - y),
    ]


def polygon_box_overlap(points, box):
    """Clip a simple polygon to an axis-aligned box and test positive area."""
    poly = [tuple(p) for p in points]
    for axis, boundary, sign in [
        (0, box[0], 1),
        (0, box[0] + box[2], -1),
        (1, box[1], 1),
        (1, box[1] + box[3], -1),
    ]:
        if not poly:
            return False
        output = []
        previous = poly[-1]
        for current in poly:
            a = sign * (previous[axis] - boundary) >= 0
            b = sign * (current[axis] - boundary) >= 0
            if a != b:
                t = (boundary - previous[axis]) / (current[axis] - previous[axis])
                output.append(
                    tuple(previous[k] + t * (current[k] - previous[k]) for k in (0, 1))
                )
            if b:
                output.append(current)
            previous = current
        poly = output
    return (
        bool(poly)
        and abs(
            sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(poly, poly[1:] + poly[:1]))
        )
        > 1e-6
    )


def polygons_overlap(a, b):
    """Intersection of simple sampled polygons, including boundary contact."""

    def cross(p, q, r):
        return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])

    def on(p, q, r):
        return abs(cross(p, q, r)) < 1e-8 and all(
            min(p[k], q[k]) - 1e-8 <= r[k] <= max(p[k], q[k]) + 1e-8 for k in (0, 1)
        )

    def inside(p, poly):
        result = False
        for u, v in zip(poly, poly[1:] + poly[:1]):
            if on(u, v, p):
                return True
            if (u[1] > p[1]) != (v[1] > p[1]) and p[0] < (v[0] - u[0]) * (
                p[1] - u[1]
            ) / (v[1] - u[1]) + u[0]:
                result = not result
        return result

    for p, q in zip(a, a[1:] + a[:1]):
        for r, s in zip(b, b[1:] + b[:1]):
            if (
                cross(p, q, r) * cross(p, q, s) < 0
                and cross(r, s, p) * cross(r, s, q) < 0
            ):
                return True
            if on(p, q, r) or on(p, q, s) or on(r, s, p) or on(r, s, q):
                return True
    return inside(a[0], b) or inside(b[0], a)


def ribbon(a, b, control, half):
    """Quadratic centerline with tapered, sampled perpendicular offsets."""
    if a == b:
        raise ValueError("joined centers must differ")
    c = control or [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2]
    c = vector(list(c), 2, "join_curve")
    left = []
    right = []
    cells = []
    for j in range(65):
        t = j / 64
        u = 1 - t
        x = u * u * a[0] + 2 * u * t * c[0] + t * t * b[0]
        y = u * u * a[1] + 2 * u * t * c[1] + t * t * b[1]
        dx = 2 * u * (c[0] - a[0]) + 2 * t * (b[0] - c[0])
        dy = 2 * u * (c[1] - a[1]) + 2 * t * (b[1] - c[1])
        length = math.hypot(dx, dy)
        if length < 1e-8:
            raise ValueError("join_curve creates a cusp; move its control point")
        w = half * (1 - 0.3 * t)
        nx = -dy / length
        ny = dx / length
        left.append((x + nx * w, y + ny * w))
        right.append((x - nx * w, y - ny * w))
        if j:
            pts = [left[-2], left[-1], right[-2], right[-1]]
            xs, ys = zip(*pts)
            cells.append([min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)])
    pts = left + right[::-1]
    return "M" + " L".join(f"{x:.4f},{y:.4f}" for x, y in pts) + " Z", cells


def sfx_glyph_layout(item, font_path, index):
    """Per-character controls preserve one Unicode text source; no outline conversion."""
    from PIL import ImageFont

    text = item["text"]
    fs = item["font_size"]
    box = item["box"]
    pad = item["padding"]
    if "\n" in text:
        raise ValueError("per-glyph SFX requires a single-line source")
    controls = item.get("glyphs", [])
    if not isinstance(controls, list):
        raise ValueError("glyphs must be an array")
    specs = {}
    for g in controls:
        fields(g, "index dx dy scale rotate", "glyph")
        i = g.get("index")
        if type(i) is not int or not 0 <= i < len(text) or i in specs:
            raise ValueError("invalid or duplicate glyph index")
        vals = {
            k: number(g.get(k, 1 if k == "scale" else 0), "glyph " + k, k == "scale")
            for k in ("dx", "dy", "scale", "rotate")
        }
        if vals["scale"] > 4:
            raise ValueError("glyph scale exceeds 4")
        specs[i] = vals
    arc = number(item.get("arc", 0), "arc")
    fonts = []
    widths = []
    for i, c in enumerate(text):
        size = max(1, round(fs * specs.get(i, {}).get("scale", 1)))
        f = ImageFont.truetype(font_path, size, index=index)
        fonts.append(f)
        widths.append(f.getlength(c))
    total = sum(widths)
    x = box[0] + (box[2] - total) / 2
    maxa = max(f.getmetrics()[0] for f in fonts)
    maxd = max(f.getmetrics()[1] for f in fonts)
    base = box[1] + (box[3] - maxa - maxd) / 2 + maxa
    segments = []
    rects = []
    for i, c in enumerate(text):
        g = specs.get(i, {})
        f = fonts[i]
        t = (i + 0.5) / len(text)
        gx = x + g.get("dx", 0)
        gy = base - 4 * arc * t * (1 - t) + g.get("dy", 0)
        angle = g.get("rotate", 0)
        segments.append(
            {
                "text": c,
                "x": gx,
                "y": gy,
                "font_size": f.size,
                "rotate": angle,
                "color": None,
            }
        )
        l, top, r, b = f.getbbox(c, anchor="ls")
        a = math.radians(angle)
        pts = [
            (
                gx + xx * math.cos(a) - yy * math.sin(a),
                gy + xx * math.sin(a) + yy * math.cos(a),
            )
            for xx in (l, r)
            for yy in (top, b)
        ]
        xs, ys = zip(*pts)
        rects.append([min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)])
        x += widths[i]
    return {
        "lines": [text],
        "positions": [(box[0] + pad, base, text)],
        "segments": segments,
        "glyphboxes": rects,
    }


def shadow_spec(value):
    if value is None:
        return None
    fields(value, "dx dy steps color", "shadow")
    out = {
        "dx": number(value.get("dx", 5), "shadow dx"),
        "dy": number(value.get("dy", 5), "shadow dy"),
        "color": color(value.get("color", "#20202A")),
        "steps": value.get("steps", 5),
    }
    if type(out["steps"]) is not int or not 1 <= out["steps"] <= 32:
        raise ValueError("shadow steps must be 1..32")
    return out
