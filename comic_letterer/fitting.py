"""Bounded contour search with exact compiler checks and unchanged wording/size."""

import copy
import math


def fit_item(job, item_id, compile_fn):
    item = next((i for i in job["items"] if i["id"] == item_id), None)
    if item is None or "box" not in item:
        raise ValueError("fit requires a placed item")
    resolved = {**job.get("styles", {}).get(item.get("style"), {}), **item}
    if resolved["kind"] in ("sfx", "floating"):
        raise ValueError("fit requires a balloon or caption")
    panel = next(p["box"] for p in job["panels"] if p["id"] == item["panel"])
    x, y, w, h = item["box"]
    fs = resolved.get("font_size", 28)
    pad = resolved.get("padding", fs * 0.6)
    candidates = []
    for factor in (0.75, 1, 1.25, 1.5, 1.8):
        nw = min(w * factor, panel[0] + panel[2] - x - 3)
        if nw <= 2 * pad:
            continue
        count = max(
            1, math.ceil(len(item["text"]) * fs / max(1, (nw - 2 * pad) * 0.75))
        )
        start = max(
            fs * 1.4 + 2 * pad, count * fs * resolved.get("line_height", 1.25) + 2 * pad
        )
        for scale in (1, 1.25, 1.6):
            nh = round(start * scale)
            if y + nh > panel[1] + panel[3] - 3:
                continue
            candidates.append([x, y, round(nw), nh])
    for box in sorted(candidates, key=lambda b: b[2] * b[3]):
        candidate = copy.deepcopy(job)
        next(i for i in candidate["items"] if i["id"] == item_id)["box"] = box
        _, report = compile_fn(candidate)
        if not any(
            i["severity"] == "error" and i["item"] == item_id for i in report["issues"]
        ):
            return candidate
    raise ValueError(
        "No clear fit at this origin and font size; reposition the balloon first"
    )
