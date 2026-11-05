"""Optional, offline Chromium raster output from the vector master."""

import base64
import io
from pathlib import Path
from xml.etree import ElementTree as ET

from fontTools import subset
from fontTools.ttLib import TTFont


def render_png(svg, output, width, font_path, font_index=0):
    from playwright.sync_api import sync_playwright

    root = ET.fromstring(svg)
    source_w, source_h = map(float, (root.get("width"), root.get("height")))
    height = round(source_h * width / source_w)
    if (
        width < 1
        or height < 1
        or width > 16000
        or height > 16000
        or width * height > 64_000_000
    ):
        raise ValueError(
            "PNG dimensions must be 1..16000 and at most 64 million pixels"
        )
    # Local render only. No font bytes are persisted in the editable SVG.
    chars = "".join(n.text or "" for n in root.iter() if n.tag.endswith("}tspan"))
    with TTFont(font_path, fontNumber=font_index) as font:
        options = subset.Options()
        sub = subset.Subsetter(options=options)
        sub.populate(text=chars)
        sub.subset(font)
        font.flavor = "woff"
        buf = io.BytesIO()
        font.save(buf)
    data = base64.b64encode(buf.getvalue()).decode("ascii")
    css = f"@font-face{{font-family:LocalRender;src:url(data:font/woff;base64,{data})}} html,body{{margin:0;background:white}} svg{{display:block;width:{width}px;height:{height}px}} text{{font-family:LocalRender!important}}"
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        try:
            page = browser.new_page(
                viewport={"width": width, "height": height}, device_scale_factor=1
            )
            page.route("**/*", lambda route: route.abort())
            page.set_content(f"<style>{css}</style>{svg}")
            page.evaluate("document.fonts.ready")
            if not page.evaluate("document.fonts.check('20px LocalRender')"):
                raise ValueError("Render font failed to load")
            page.screenshot(path=str(Path(output)), omit_background=False)
        finally:
            browser.close()
