import xml.etree.ElementTree as ET
import pytest
from comic_letterer.engine import compile_page


@pytest.fixture
def page():
    return {
        "version": 1,
        "width": 600,
        "height": 500,
        "panels": [{"id": "p", "box": [0, 0, 600, 500]}],
        "items": [
            {
                "id": "a",
                "panel": "p",
                "kind": "speech",
                "speaker": "A",
                "order": 1,
                "text": "We go now.",
                "box": [20, 20, 250, 120],
                "target": [200, 300],
                "font_size": 24,
            }
        ],
    }


def test_missing_glyph_reported(page):
    page["items"][0]["text"] = "\U0010ffff"
    _, report = compile_page(page)
    assert "missing_glyph" in {i["code"] for i in report["issues"]}


def test_newlines_and_spaces_preserved(page):
    page["items"][0]["text"] = " A  B\nC "
    svg, report = compile_page(page)
    root = ET.fromstring(svg)
    node = root.find(".//{http://www.w3.org/2000/svg}text")
    assert "".join(node.itertext()) == " A  B\nC "
    assert report["items"][0]["text_preserved"]


def test_tail_obstacle_reported(page):
    page["protected"] = [{"id": "prop", "box": [160, 150, 70, 70]}]
    _, report = compile_page(page)
    assert any(i["code"] == "tail_protected_overlap" for i in report["issues"])


def test_nonfinite_font_size_rejected(page):
    page["items"][0]["font_size"] = float("inf")
    with pytest.raises(ValueError):
        compile_page(page)


def test_bad_color_cannot_inject_svg(page):
    page["items"][0]["fill"] = "url(https://example.com/a)"
    with pytest.raises(ValueError):
        compile_page(page)


def test_unknown_field_rejected(page):
    page["items"][0]["font_szie"] = 42
    with pytest.raises(ValueError, match="unknown"):
        compile_page(page)


def test_join_cannot_jump_interruption(page):
    b = dict(page["items"][0], id="b", speaker="B", order=2, box=[300, 20, 250, 120])
    c = dict(page["items"][0], id="c", order=3, join_to="a", box=[20, 200, 250, 120])
    page["items"] += [b, c]
    with pytest.raises(ValueError, match="consecutive"):
        compile_page(page)


def test_join_and_sfx_layers(page):
    page["items"].append(
        dict(page["items"][0], id="b", order=2, join_to="a", box=[300, 20, 250, 120])
    )
    page["items"].append(
        {
            "id": "s",
            "panel": "p",
            "order": 3,
            "kind": "sfx",
            "text": "BAM",
            "box": [300, 280, 220, 120],
            "font_size": 44,
            "rotation": -12,
        }
    )
    svg, report = compile_page(page)
    root = ET.fromstring(svg)
    ids = {x.get("id") for x in root.iter()}
    assert {"art", "balloons", "text", "sfx", "join-b"} <= ids
    assert next(i for i in report["items"] if i["id"] == "b")["tail_tip"] is None


def test_reading_size_report(page):
    page["reading_width"] = 150
    _, r = compile_page(page)
    assert any(i["code"] == "reading_text_small" for i in r["issues"])


def test_target_inside_balloon_reported(page):
    page["items"][0]["target"] = [100, 70]
    _, r = compile_page(page)
    assert any(i["code"] == "target_inside_balloon" for i in r["issues"])


def test_reversed_order_warning(page):
    page["items"][0]["box"] = [320, 20, 250, 120]
    page["items"].append(
        dict(page["items"][0], id="b", order=2, box=[20, 20, 250, 120])
    )
    _, r = compile_page(page)
    assert any(i["code"] == "reading_order" for i in r["issues"])


@pytest.mark.parametrize("field", ["panels", "items", "protected"])
def test_invalid_collection_is_value_error(page, field):
    page[field] = None
    with pytest.raises(ValueError):
        compile_page(page)


def test_offpanel_requires_external_source(page):
    page["items"][0].update(off_panel=True, target=[200, 300])
    with pytest.raises(ValueError, match="outside"):
        compile_page(page)


def test_sfx_only_fields_rejected_on_speech(page):
    page["items"][0]["outlines"] = []
    with pytest.raises(ValueError, match="sfx"):
        compile_page(page)


def test_sfx_stroke_protection_without_rotation(page):
    page["items"][0].update(
        kind="sfx",
        box=[100, 100, 250, 120],
        outlines=[{"color": "#000000", "width": 30}],
    )
    page["protected"] = [{"id": "edge", "box": [85, 110, 10, 80]}]
    _, r = compile_page(page)
    assert any(i["code"] == "sfx_protected_overlap" for i in r["issues"])


def test_preset_visual_constructions_differ(page):
    outputs = {}
    for kind in ("speech", "thought", "whisper", "weak", "electronic", "shout"):
        page["items"][0]["kind"] = kind
        svg, _ = compile_page(page)
        root = ET.fromstring(svg)
        outputs[kind] = next(
            n.get("d") for n in root.iter() if n.get("id") == "outline-a"
        )
        if kind == "thought":
            assert len(root.findall(".//{http://www.w3.org/2000/svg}circle")) == 3
        if kind == "whisper":
            assert any(n.get("stroke-dasharray") for n in root.iter())
    assert len(set(outputs.values())) == 5


def test_tail_stays_out_of_source_head(page):
    page["items"][0]["target"] = [400, 300]
    page["protected"] = [{"id": "head", "box": [280, 180, 180, 180]}]
    _, report = compile_page(page)
    item = report["items"][0]
    assert item["tail_tip"][0] < 280
    assert not any(i["code"] == "tail_protected_overlap" for i in report["issues"])
