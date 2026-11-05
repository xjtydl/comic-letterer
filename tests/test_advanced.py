import copy
import xml.etree.ElementTree as ET
import pytest
from comic_letterer.engine import compile_page

NS = {"s": "http://www.w3.org/2000/svg"}


@pytest.fixture
def job():
    return {
        "version": 1,
        "width": 800,
        "height": 600,
        "panels": [{"id": "p", "box": [10, 10, 780, 580]}],
        "items": [
            {
                "id": "a",
                "panel": "p",
                "kind": "speech",
                "speaker": "A",
                "order": 1,
                "text": "Wait, the light is still on.",
                "font_size": 24,
                "box": [50, 40, 340, 150],
                "target": [300, 350],
            }
        ],
    }


def test_break_offsets_and_emphasis_preserve_source(job):
    item = job["items"][0]
    item.update(
        breaks=[6, 19], emphasis=[{"start": 10, "end": 15, "scale": 1.25}], shape="tv"
    )
    before = copy.deepcopy(job)
    svg, r = compile_page(job)
    assert job == before
    node = ET.fromstring(svg).find(".//s:text", NS)
    assert "".join(node.itertext()) == item["text"]
    assert r["items"][0]["lines"] == ["Wait, ", "the light is ", "still on."]
    assert any(float(n.get("font-size", "24")) == 30 for n in node.iter())


@pytest.mark.parametrize("breaks", [[0], [100], [8, 3], [3, 3]])
def test_bad_breaks(job, breaks):
    job["items"][0]["breaks"] = breaks
    with pytest.raises(ValueError, match="break"):
        compile_page(job)


def test_balanced_flow_does_not_change_text(job):
    job["items"][0].update(
        flow="balanced", text="听见了吗？门后好像还有声音。", shape="tv"
    )
    _, r = compile_page(job)
    assert "".join(r["items"][0]["lines"]) == job["items"][0]["text"]
    assert len(r["items"][0]["lines"]) >= 2


def test_offpanel_tip_reaches_border(job):
    job["items"][0].update(off_panel=True, target=[900, 250])
    svg, r = compile_page(job)
    assert r["items"][0]["tail_tip"][0] == pytest.approx(790)
    assert not any(i["code"] == "tail_outside_panel" for i in r["issues"])


def test_butt_crops_geometry_not_text(job):
    job["items"][0].update(box=[50, -35, 340, 200], butt=["top"], text="Stop.")
    svg, r = compile_page(job)
    root = ET.fromstring(svg)
    assert root.find(".//s:clipPath", NS) is not None
    assert not any(i["code"] == "outside_panel" for i in r["issues"])
    assert "".join(root.find(".//s:text", NS).itertext()) == "Stop."


def test_butt_does_not_license_other_edges(job):
    job["items"][0].update(box=[-40, -35, 340, 200], butt=["top"])
    _, r = compile_page(job)
    assert any(i["code"] == "outside_panel" for i in r["issues"])


def test_curved_interruption_join_requires_explicit_optin(job):
    a = job["items"][0]
    a.update(box=[40, 40, 200, 110], text="One.")
    b = dict(a, id="b", speaker="B", order=2, box=[300, 100, 200, 110], text="Wait!")
    c = dict(
        a,
        id="c",
        order=3,
        box=[570, 40, 200, 110],
        text="Two.",
        join_to="a",
        join_curve=[400, -10],
    )
    job["items"] += [b, c]
    with pytest.raises(ValueError, match="consecutive"):
        compile_page(job)
    c["allow_interruption"] = True
    svg, r = compile_page(job)
    assert any(i["code"] == "interruption_join" for i in r["issues"])
    assert "join-c" in svg
    assert not any(i["code"] == "join_item_overlap" for i in r["issues"])


def test_hollow_arc_shadow_and_glyphs_are_real_svg(job):
    job["items"][0].update(
        kind="sfx",
        text="CLANG",
        font_size=50,
        box=[60, 50, 500, 200],
        padding=8,
        hollow=True,
        arc=24,
        shadow={"dx": 5, "dy": 7, "steps": 4, "color": "#333333"},
        glyphs=[
            {"index": 0, "scale": 1.2, "rotate": -12},
            {"index": 4, "dy": 12, "rotate": 8},
        ],
    )
    svg, r = compile_page(job)
    root = ET.fromstring(svg)
    text = root.find(".//s:text", NS)
    assert text.get("fill") == "none"
    assert "".join(text.itertext()) == "CLANG"
    assert len(root.findall(".//s:use", NS)) >= 6
    assert any(n.get("rotate") == "-12.0" for n in text.iter())
    assert r["items"][0]["text_preserved"]


def test_occlusion_is_mask_and_hidden_text_reported(job):
    job["occlusions"] = [
        {
            "id": "hand",
            "polygon": [[50, 40], [390, 40], [390, 190], [50, 190]],
            "items": ["a"],
        }
    ]
    svg, r = compile_page(job)
    assert ET.fromstring(svg).find(".//s:mask", NS) is not None
    assert any(i["code"] == "occluded_text" for i in r["issues"])


def test_bad_emphasis_and_bad_glyph_index(job):
    job["items"][0]["emphasis"] = [{"start": 0, "end": 500, "scale": 1.2}]
    with pytest.raises(ValueError):
        compile_page(job)
    job["items"][0].pop("emphasis")
    job["items"][0].update(kind="sfx", glyphs=[{"index": 500}])
    with pytest.raises(ValueError):
        compile_page(job)


def test_mask_diagonal_bounding_box_is_not_a_false_positive():
    from comic_letterer.geometry import polygon_box_overlap

    polygon = [[0, 0], [100, 100], [110, 100], [10, 0]]
    assert not polygon_box_overlap(polygon, [70, 10, 20, 20])
    assert polygon_box_overlap(polygon, [45, 45, 10, 10])


def test_font_role_requires_explicit_configuration(job):
    from comic_letterer.engine import find_font

    job["items"][0]["font_role"] = "display"
    with pytest.raises(ValueError, match="font_role"):
        compile_page(job)
    _, report = compile_page(job, fonts={"display": {"path": find_font()}})
    assert set(report["fonts"]) == {"body", "display"}


def test_sampled_tail_polygons_distinguish_gap_from_crossing():
    from comic_letterer.engine import tail_geometry
    from comic_letterer.geometry import polygons_overlap

    a = tail_geometry(
        [575, 483, 190, 78], [879, 704], 0.14, "speech", [[800, 565, 245, 230]], "tv"
    )
    b = tail_geometry([785, 500, 105, 60], [556, 672], 1, "speech")
    assert not polygons_overlap(a["polygon"], b["polygon"])
    assert polygons_overlap(a["polygon"], a["polygon"])


def test_missing_display_renderer_font_is_not_silent_fallback(job):
    from comic_letterer.engine import find_font
    from comic_letterer.render import font_css

    job["items"][0]["font_role"] = "display"
    svg, _ = compile_page(job, fonts={"display": {"path": find_font()}})
    with pytest.raises(ValueError, match="every SVG font role"):
        font_css(svg, {"body": {"path": find_font()}})


def test_mask_checks_rotated_sfx_in_page_coordinates(job):
    item = job["items"][0]
    item.update(
        kind="sfx", text="MMMM", font_size=42, box=[150, 100, 300, 140], rotation=90
    )
    _, r = compile_page(job)
    x, y, w, h = r["items"][0]["glyph_boxes"][0]
    # Rotate the left end of the measured word 90 degrees about the item center.
    gx, gy = x + 3, y + h / 2
    mx, my = 300 - (gy - 170), 170 + (gx - 300)
    job["occlusions"] = [
        {
            "id": "foreground",
            "polygon": [
                [mx - 2, my - 2],
                [mx + 2, my - 2],
                [mx + 2, my + 2],
                [mx - 2, my + 2],
            ],
            "items": ["a"],
        }
    ]
    _, r = compile_page(job)
    assert any(i["code"] == "occluded_text" for i in r["issues"])
