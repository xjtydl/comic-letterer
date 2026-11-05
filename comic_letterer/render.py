"""Optional, offline Chromium raster output from the vector master."""

import base64
import io
from functools import lru_cache
from pathlib import Path
from xml.etree import ElementTree as ET

from fontTools import subset
from fontTools.ttLib import TTFont


def render_png(svg, output, width, font_path, font_index=0, fonts=None):
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
    font_bank = {"body": {"path": str(font_path), "index": font_index}, **(fonts or {})}
    css = (
        font_css(svg, font_bank)
        + f"html,body{{margin:0;background:white}} svg{{display:block;width:{width}px;height:{height}px}}"
    )
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        try:
            page = browser.new_page(
                viewport={"width": width, "height": height}, device_scale_factor=1
            )
            page.route("**/*", lambda route: route.abort())
            page.set_content(f"<style>{css}</style>{svg}")
            page.evaluate("document.fonts.ready")
            if not page.evaluate(
                "[...document.fonts].every(font => font.status === 'loaded')"
            ):
                raise ValueError("Render font failed to load")
            page.screenshot(path=str(Path(output)), omit_background=False)
        finally:
            browser.close()


def font_css(svg, font_bank):
    root = ET.fromstring(svg)
    css = ""
    leaves = []

    def collect(node, role="body"):
        role = node.get("data-font-role", role)
        if node.tag.endswith("}tspan"):
            leaves.append((node, role))
        for child in node:
            collect(child, role)

    collect(root)
    roles = {role for node, role in leaves}
    if not roles.issubset(font_bank):
        raise ValueError("render font configuration must include every SVG font role")
    for role, spec in font_bank.items():
        chars = "".join(
            node.text or "" for node, inherited in leaves if inherited == role
        )
        if not chars:
            continue
        data = subset_font(
            str(spec["path"]), spec.get("index", 0), "".join(sorted(set(chars)))
        )
        css += f"@font-face{{font-family:LocalRender_{role};src:url(data:font/woff;base64,{data})}} [data-font-role='{role}']{{font-family:LocalRender_{role}!important;font-weight:normal!important;font-style:normal!important;font-synthesis:none}}"
    return css


@lru_cache(maxsize=8)
def subset_font(path, index, chars):
    with TTFont(path, fontNumber=index) as font:
        sub = subset.Subsetter(options=subset.Options())
        sub.populate(text=chars)
        sub.subset(font)
        font.flavor = "woff"
        buf = io.BytesIO()
        font.save(buf)
    return base64.b64encode(buf.getvalue()).decode("ascii")
