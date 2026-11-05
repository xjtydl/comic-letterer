import copy
import xml.etree.ElementTree as ET
import pytest

from comic_letterer.engine import compile_page, find_font, wrap_text, PRESETS


@pytest.fixture
def job():
    return {
        "version": 1,
        "width": 800,
        "height": 600,
        "panels": [{"id": "p1", "box": [0, 0, 800, 600]}],
        "items": [
            {
                "id": "a",
                "panel": "p1",
                "kind": "speech",
                "order": 1,
                "speaker": "one",
                "text": "Hello, friend!",
                "font_size": 24,
                "box": [40, 30, 320, 130],
                "target": [300, 300],
            }
        ],
    }


def test_unknown_kind_rejected(job):
    job["items"][0]["kind"] = "typo-whispr"
    with pytest.raises(ValueError, match="kind"):
        compile_page(job)


def test_original_text_is_escaped_and_preserved(job):
    job["items"][0]["text"] = "<script> & hi"
    svg, report = compile_page(job)
    root = ET.fromstring(svg)
    assert root.find(".//{http://www.w3.org/2000/svg}script") is None
    assert (
        "".join(root.find(".//{http://www.w3.org/2000/svg}text").itertext())
        == "<script> & hi"
    )
    assert report["items"][0]["text_preserved"] is True


def test_frozen_text_mismatch_rejected(job):
    job["items"][0]["expected_text"] = "Changed dialogue"
    with pytest.raises(ValueError, match="frozen"):
        compile_page(job)


def test_geometry_does_not_mutate_input(job):
    original = copy.deepcopy(job)
    compile_page(job)
    assert job == original


def test_overflow_reports_without_shrinking(job):
    job["items"][0]["box"] = [20, 20, 70, 40]
    job["items"][0]["text"] = "A very long sentence that cannot fit."
    _, report = compile_page(job)
    assert any(x["code"] == "text_overflow" for x in report["issues"])
    assert report["items"][0]["font_size"] == 24


def test_face_protection_reports(job):
    job["protected"] = [{"id": "face", "box": [80, 60, 60, 70]}]
    _, report = compile_page(job)
    assert any(x["code"] == "protected_overlap" for x in report["issues"])


def test_auto_position_avoids_exclusion(job):
    del job["items"][0]["box"]
    job["items"][0]["size"] = [260, 120]
    job["protected"] = [{"id": "face", "box": [0, 0, 330, 180]}]
    _, r = compile_page(job)
    assert r["items"][0]["box"][0] >= 330
    assert not any(x["code"] == "protected_overlap" for x in r["issues"])


def test_tail_stops_before_source(job):
    _, r = compile_page(job)
    tip = r["items"][0]["tail_tip"]
    assert 160 < tip[1] < 300


@pytest.mark.parametrize("kind", sorted(PRESETS))
def test_all_presets_are_valid_svg(job, kind):
    job["items"][0]["kind"] = kind
    svg, _ = compile_page(job)
    ET.fromstring(svg)
    assert "NaN" not in svg and "nan" not in svg


def test_chinese_punctuation_and_content():
    from PIL import ImageFont

    font = ImageFont.truetype(find_font(), 20)
    text = "你好，朋友。我们（一起）走吧！"
    lines = wrap_text(text, font, 85)
    assert "".join(lines) == text
    assert all(not line.startswith(tuple("，。！？）")) for line in lines)
    assert all(not line.endswith("（") for line in lines)


def test_join_requires_same_speaker(job):
    b = copy.deepcopy(job["items"][0])
    b.update(id="b", order=2, speaker="two", join_to="a", box=[400, 30, 300, 130])
    job["items"].append(b)
    with pytest.raises(ValueError, match="speaker"):
        compile_page(job)


def test_reading_order_duplicates_rejected(job):
    b = copy.deepcopy(job["items"][0])
    b["id"] = "b"
    job["items"].append(b)
    with pytest.raises(ValueError, match="order"):
        compile_page(job)


def test_nan_rejected(job):
    job["items"][0]["box"][0] = float("nan")
    with pytest.raises(ValueError):
        compile_page(job)


def test_missing_panel_rejected(job):
    job["items"][0]["panel"] = "missing"
    with pytest.raises(ValueError, match="panel"):
        compile_page(job)
