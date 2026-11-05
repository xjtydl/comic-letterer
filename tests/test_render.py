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
def test_hollow_reveals_background_and_mask_removes_paint(tmp_path):
    import base64
    import copy
    import io

    buf = io.BytesIO()
    Image.new("RGB", (500, 300), "#409060").save(buf, format="PNG")
    background = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()
    font = find_font()
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
                "kind": "sfx",
                "text": "BOOM",
                "font_size": 100,
                "box": [20, 20, 460, 240],
                "font_role": "display",
                "outlines": [{"color": "#ffffff", "width": 2}],
            }
        ],
    }
    fonts = {"display": {"path": font}}
    images = []
    for hollow in (False, True):
        job["items"][0]["hollow"] = hollow
        svg, report = compile_page(job, font, background=background, fonts=fonts)
        assert report["ok"]
        path = tmp_path / f"hollow-{hollow}.png"
        render_png(svg, path, 500, font, fonts=fonts)
        images.append(Image.open(path).convert("RGB"))
    solid, hollow = images
    revealed = sum(
        max(solid.getpixel((x, y))) < 60 and hollow.getpixel((x, y)) == (64, 144, 96)
        for y in range(50, 250)
        for x in range(20, 480)
    )
    assert revealed > 100
    masked = copy.deepcopy(job)
    masked["occlusions"] = [
        {
            "id": "foreground",
            "polygon": [[0, 0], [250, 0], [250, 300], [0, 300]],
            "items": ["a"],
        }
    ]
    svg, report = compile_page(masked, font, background=background, fonts=fonts)
    assert any(i["code"] == "occluded_text" for i in report["issues"])
    path = tmp_path / "mask.png"
    render_png(svg, path, 500, font, fonts=fonts)
    result = Image.open(path).convert("RGB")
    assert result.crop((0, 0, 249, 300)).getextrema() == (
        (64, 64),
        (144, 144),
        (96, 96),
    )
    from PIL import ImageChops

    difference = ImageChops.difference(
        result.crop((251, 0, 500, 300)), hollow.crop((251, 0, 500, 300))
    )
    # A mask creates a compositing layer; Chromium can round edge antialiasing by one level.
    assert max(hi for lo, hi in difference.getextrema()) <= 1


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
