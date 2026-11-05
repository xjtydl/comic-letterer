"""Opt-in Chromium integration; enable with COMIC_LETTERER_RENDER_TEST=1."""

import os
import pytest
from PIL import Image
from comic_letterer.engine import compile_page, find_font
from comic_letterer.render import render_png


@pytest.mark.skipif(
    os.environ.get("COMIC_LETTERER_RENDER_TEST") != "1",
    reason="optional Chromium integration",
)
def test_png_vector_dimensions_and_real_ink(tmp_path):
    job = {
        "version": 1,
        "width": 500,
        "height": 300,
        "panels": [{"id": "p", "box": [0, 0, 500, 300]}],
        "items": [
            {
                "id": "a",
                "panel": "p",
                "order": 1,
                "kind": "caption",
                "text": "中文 Hello",
                "box": [20, 20, 440, 150],
                "font_size": 32,
            }
        ],
    }
    font = find_font()
    svg, report = compile_page(job, font)
    # Font selection can be Latin-only on CI: test English there; missing glyph remains a separate test.
    if any(i["code"] == "missing_glyph" for i in report["issues"]):
        job["items"][0]["text"] = "Hello"
        svg, report = compile_page(job, font)
    assert report["ok"]
    for width in (500, 250):
        path = tmp_path / f"{width}.png"
        render_png(svg, path, width, font)
        with Image.open(path) as im:
            assert im.size == (width, round(width * 0.6))
            # Interior text region contains dark glyph pixels and light fill.
            region = im.convert("RGB").crop(
                (
                    int(width * 0.1),
                    int(width * 0.13),
                    int(width * 0.8),
                    int(width * 0.45),
                )
            )
            pixels = [
                region.getpixel((x, y))
                for y in range(region.height)
                for x in range(region.width)
            ]
            assert sum(max(p) < 100 for p in pixels) > 30
            assert sum(min(p) > 150 for p in pixels) > 100
