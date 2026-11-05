"""Explicit narrative semantics and reusable appearance. Never rewrite dialogue."""

import math
from .validation import fields, ident, number, vector

STYLE_FIELDS = "kind font_role font_size padding line_height fill stroke text_color stroke_width shape tracking horizontal_scale flow align voice caption_type double_outline baseline edge mechanical scroll drop_cap"
CAPTIONS = ("location", "time", "inner", "spoken", "editorial")
VOICES = ("normal", "rough", "breath", "singing", "telepathic")


def resolve_item(raw, styles):
    if not isinstance(styles, dict):
        raise ValueError("styles must be an object")
    for key, value in styles.items():
        ident(key)
        fields(value, STYLE_FIELDS, "style")
    key = raw.get("style")
    if key is not None and (not isinstance(key, str) or key not in styles):
        raise ValueError("unknown style")
    item = {**styles.get(key, {}), **raw}
    caption = item.get("caption_type")
    if caption is not None:
        if caption not in CAPTIONS or item.get("kind") not in ("caption", "floating"):
            raise ValueError(
                "caption_type requires a caption/floating item and known source type"
            )
        if caption in ("inner", "spoken") and not item.get("speaker"):
            raise ValueError("inner/spoken caption requires speaker")
    voice = item.get("voice", "normal")
    if voice not in VOICES:
        raise ValueError("unknown voice")
    if voice != "normal" and item.get("kind") in ("caption", "floating", "sfx"):
        raise ValueError("voice decorations require a voiced balloon")
    double = item.get("double_outline", 0)
    number(double, "double_outline")
    if not 0 <= double <= 24:
        raise ValueError("double_outline must be 0..24 pixels")
    if double and item.get("kind") in ("caption", "floating", "sfx"):
        raise ValueError("double_outline requires a voiced balloon")
    tail = item.get("tail", {})
    fields(tail, "visible width length gap root_angle curve", "tail")
    if "visible" in tail and type(tail["visible"]) is not bool:
        raise ValueError("tail visible must be boolean")
    for key in ("width", "length", "gap", "root_angle"):
        if key in tail:
            n = number(tail[key], "tail " + key)
            if key != "root_angle" and n < 0:
                raise ValueError("tail dimensions must be nonnegative")
    if "width" in tail and tail["width"] == 0:
        raise ValueError("tail width must be positive")
    if "curve" in tail:
        vector(tail["curve"], 2, "tail curve")
        if item.get("kind") in ("thought", "electronic"):
            raise ValueError("tail curve supports smooth voice tails")
    return item


def rough_contour(box):
    x, y, w, h = box
    pts = []
    for i in range(192):
        a = math.tau * i / 192
        # Deterministic multiscale edge, independent of font and process RNG.
        r = 0.95 + 0.025 * math.sin(29 * a) + 0.018 * math.sin(47 * a + 1.1)
        pts.append(
            (x + w / 2 + w / 2 * r * math.cos(a), y + h / 2 + h / 2 * r * math.sin(a))
        )
    return "M" + " L".join(f"{x:.4f},{y:.4f}" for x, y in pts) + " Z"


def organic_radius(angle):
    """Subtle deterministic asymmetry, entirely inside the declared ellipse."""
    return 0.97 + 0.018 * math.sin(3 * angle + 0.7) + 0.012 * math.sin(5 * angle)


def tattered_depth(box):
    return min(4, min(box[2:]) * 0.06)


def tattered_contour(box):
    """Small inward wear and occasional divots; never expands the outer box."""
    x, y, w, h = box
    corners = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
    inward = [(0, 1), (-1, 0), (0, -1), (1, 0)]
    pts = []
    depth = tattered_depth(box)
    for side, (a, b) in enumerate(zip(corners, corners[1:] + corners[:1])):
        length = math.dist(a, b)
        count = max(3, math.ceil(length / 7))
        nx, ny = inward[side]
        for i in range(count):
            t = i / count
            wear = 0 if i == 0 else depth * (
                1 if (i + side * 3) % 13 == 5
                else 0.18 + 0.3 * (0.5 + 0.5 * math.sin(i * 2.39 + side))
            )
            pts.append((a[0] + (b[0] - a[0]) * t + nx * wear,
                        a[1] + (b[1] - a[1]) * t + ny * wear))
    return "M" + " L".join(f"{x:.4f},{y:.4f}" for x, y in pts) + " Z"


def rough_tail(tail):
    points = tail["polygon"]
    out = []
    n = len(points)
    for i, (x, y) in enumerate(points):
        before = points[max(0, i - 1)]
        after = points[min(n - 1, i + 1)]
        dx, dy = after[0] - before[0], after[1] - before[1]
        length = max(math.hypot(dx, dy), 1e-8)
        noise = 1.5 * math.sin(i * 2.7) * abs(math.sin(math.tau * i / max(1, n - 1)))
        out.append((x - dy / length * noise, y + dx / length * noise))
    tail["polygon"] = out
    tail["d"] = "M" + " L".join(f"{x:.4f},{y:.4f}" for x, y in out) + " Z"
    xs, ys = zip(*out)
    tail["box"] = [
        min(xs) - 2,
        min(ys) - 2,
        max(xs) - min(xs) + 4,
        max(ys) - min(ys) + 4,
    ]


def edge_distance(point, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    den = dx * dx + dy * dy
    t = (
        max(0, min(1, ((point[0] - a[0]) * dx + (point[1] - a[1]) * dy) / den))
        if den
        else 0
    )
    return math.hypot(point[0] - a[0] - t * dx, point[1] - a[1] - t * dy)


def near_ink_edges(item, edges, tolerance):
    if not isinstance(edges, list):
        raise ValueError("ink_edges must be an array")
    x, y, w, h = item["box"]
    kind = item["kind"]
    power = 4 if item.get("shape") == "tv" else 2
    if kind in ("caption", "floating", "sfx"):
        points = [(x + i * w / 24, y + j * h) for i in range(25) for j in (0, 1)] + [
            (x + j * w, y + i * h / 24) for i in range(25) for j in (0, 1)
        ]
    else:
        points = [
            (
                x
                + w / 2
                + w / 2 * math.copysign(abs(math.cos(a)) ** (2 / power), math.cos(a)),
                y
                + h / 2
                + h / 2 * math.copysign(abs(math.sin(a)) ** (2 / power), math.sin(a)),
            )
            for a in (math.tau * i / 128 for i in range(128))
        ]
    if item["_tail"]:
        points += item["_tail"]["polygon"]
    near = []
    for edge in edges:
        fields(edge, "id points", "ink edge")
        name = ident(edge.get("id"))
        raw = edge.get("points")
        if not isinstance(raw, list) or len(raw) < 2:
            raise ValueError("ink edge requires at least two points")
        line = [vector(p, 2, "ink edge point") for p in raw]
        if any(
            edge_distance(p, a, b) <= tolerance
            for p in points
            for a, b in zip(line, line[1:])
        ):
            near.append(name)
    return near
