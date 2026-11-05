import copy
import xml.etree.ElementTree as ET
from pathlib import Path
import pytest
from comic_letterer.engine import compile_page, find_font, tail_geometry
from comic_letterer.render import font_css
from comic_letterer.fitting import fit_item


@pytest.fixture
def job():
    return {
        "version": 1,
        "width": 800,
        "height": 600,
        "panels": [{"id": "p", "box": [0, 0, 800, 600]}],
        "items": [
            {
                "id": "a",
                "kind": "speech",
                "panel": "p",
                "order": 1,
                "speaker": "A",
                "text": "Please bring the little cat inside.",
                "expected_text": "Please bring the little cat inside.",
                "box": [40, 30, 380, 160],
                "font_size": 26,
                "target": [500, 400],
            }
        ],
    }


def italic_font():
    for path in [
        "/System/Library/Fonts/Supplemental/Arial Bold Italic.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-BoldOblique.ttf",
    ]:
        if Path(path).is_file():
            return path
    pytest.skip("actual italic font unavailable")


def test_real_font_runs_have_independent_faces_metrics_and_subset(job):
    role = {"emph": {"path": italic_font()}}
    item = job["items"][0]
    item["emphasis"] = [{"start": 17, "end": 27, "font_role": "emph"}]
    original = copy.deepcopy(job)
    svg, r = compile_page(job, fonts=role)
    assert job == original
    assert r["fonts"]["emph"]["style"] == "italic"
    assert r["fonts"]["emph"]["weight"] >= 600
    ns = {"s": "http://www.w3.org/2000/svg"}
    text = ET.fromstring(svg).find(".//s:text", ns)
    assert "".join(text.itertext()) == item["text"]
    emph = [n for n in text if n.get("data-font-role") == "emph"]
    assert "".join(n.text for n in emph) == "little cat"
    assert all(n.get("font-size") == "26" for n in emph)
    css = font_css(svg, {"body": {"path": find_font()}, **role})
    assert "LocalRender_emph" in css
    with pytest.raises(ValueError, match="every SVG font role"):
        font_css(svg, {"body": {"path": find_font()}})


def test_tracking_and_scale_change_measured_positions(job):
    _, a = compile_page(job)
    job["items"][0].update(tracking=2, horizontal_scale=0.95, breaks=[])
    svg, b = compile_page(job)
    assert 'lengthAdjust="spacingAndGlyphs"' in svg
    assert len(b["items"][0]["glyph_boxes"]) > len(a["items"][0]["glyph_boxes"])
    assert b["items"][0]["text_preserved"]


def test_old_svg_inherits_font_role_from_text_parent(job):
    job["items"][0]["font_role"] = "display"
    svg, _ = compile_page(job, fonts={"display": {"path": find_font()}})
    root = ET.fromstring(svg)
    for node in root.iter():
        if node.tag.endswith("}tspan"):
            node.attrib.pop("data-font-role", None)
    old_svg = ET.tostring(root, encoding="unicode")
    with pytest.raises(ValueError, match="every SVG font role"):
        font_css(old_svg, {"body": {"path": find_font()}})
    assert "LocalRender_display" in font_css(
        old_svg, {"display": {"path": find_font()}}
    )


def test_keep_words_intact_and_reject_conflicting_manual_break(job):
    item = job["items"][0]
    item.update(
        text="一件古怪的事",
        expected_text="一件古怪的事",
        box=[40, 30, 100, 220],
        flow="balanced",
        keep_together=[{"start": 0, "end": 2}],
    )
    _, r = compile_page(job)
    assert r["items"][0]["lines"][0].startswith("一件")
    item["breaks"] = [1]
    with pytest.raises(ValueError, match="keep_together"):
        compile_page(job)


def test_tail_controls_and_protected_gap():
    box = [50, 30, 240, 120]
    target = [450, 350]
    a = tail_geometry(box, target, 0.5, "speech")
    b = tail_geometry(
        box,
        target,
        0.5,
        "speech",
        options={"width": 26, "length": 45, "root_angle": 80, "curve": [210, 190]},
    )
    assert b["boundary"] != a["boundary"] and b["d"] != a["d"]
    import math

    assert math.dist(b["boundary"], b["tip"]) == pytest.approx(45)
    g = tail_geometry(
        box,
        target,
        0.9,
        "speech",
        [[350, 240, 140, 150]],
        options={"length": 999, "gap": 20},
    )
    assert g["tip"][0] < 350 or g["tip"][1] < 240


def test_final_balloon_can_own_attribution(job):
    a = job["items"][0]
    a.update(
        box=[30, 30, 270, 120],
        text="First.",
        expected_text="First.",
        tail={"visible": False},
    )
    b = {
        **a,
        "id": "b",
        "order": 2,
        "box": [390, 30, 250, 120],
        "text": "Then.",
        "expected_text": "Then.",
        "join_to": "a",
        "tail": {"visible": True},
    }
    job["items"].append(b)
    _, r = compile_page(job)
    assert r["items"][0]["tail_tip"] is None and r["items"][1]["tail_tip"] is not None
    assert not any(i["code"] == "missing_attribution" for i in r["issues"])
    b["tail"]["visible"] = False
    _, r = compile_page(job)
    assert any(i["code"] == "missing_attribution" for i in r["issues"])


def test_styles_are_reusable_without_changing_source(job):
    job["styles"] = {
        "narrator": {
            "kind": "caption",
            "caption_type": "inner",
            "font_size": 24,
            "fill": "#EEDDBB",
        }
    }
    item = job["items"][0]
    item["style"] = "narrator"
    del item["kind"]
    del item["font_size"]
    original = copy.deepcopy(job)
    svg, r = compile_page(job)
    assert job == original and r["items"][0]["caption_type"] == "inner"
    assert r["items"][0]["font_size"] == 24 and 'data-caption-type="inner"' in svg
    job["styles"]["narrator"]["text"] = "Illegal override"
    with pytest.raises(ValueError):
        compile_page(job)


@pytest.mark.parametrize("caption", ["inner", "spoken"])
def test_caption_source_requires_speaker(job, caption):
    item = job["items"][0]
    item.update(kind="caption", caption_type=caption)
    item.pop("speaker")
    with pytest.raises(ValueError, match="speaker"):
        compile_page(job)


@pytest.mark.parametrize("voice", ["rough", "breath", "singing", "telepathic"])
def test_explicit_voice_geometry_keeps_frozen_text(job, voice):
    svg0, _ = compile_page(job)
    job["items"][0]["voice"] = voice
    svg, r = compile_page(job)
    assert svg != svg0 and r["items"][0]["text_preserved"]
    assert f'data-voice="{voice}"' in svg


def test_marked_ink_edge_and_short_tail_warnings(job):
    job["ink_edges"] = [{"id": "beam", "points": [[40, 0], [40, 250]]}]
    job["min_tail_length"] = 25
    job["items"][0]["tail"] = {"length": 2}
    _, r = compile_page(job)
    assert {"near_ink_edge", "tail_too_short"} <= {i["code"] for i in r["issues"]}


def test_fit_reflows_contour_without_shrinking_or_rewriting(job):
    item = job["items"][0]
    item["box"] = [40, 30, 170, 55]
    _, before = compile_page(job)
    assert any(i["code"] == "text_overflow" for i in before["issues"])
    fitted = fit_item(job, "a", compile_page)
    assert fitted["items"][0]["text"] == item["text"]
    assert fitted["items"][0]["font_size"] == item["font_size"]
    assert fitted["items"][0]["box"] != item["box"]
    _, r = compile_page(fitted)
    assert not any(i["code"] == "text_overflow" for i in r["issues"])
