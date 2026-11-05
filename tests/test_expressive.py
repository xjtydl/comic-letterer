"""Expressive lettering must stay measurable, frozen and editable."""
import copy
import math
import re
import xml.etree.ElementTree as ET

import pytest
from comic_letterer.engine import compile_page, contour, tail_geometry
from comic_letterer.narrative import organic_radius


@pytest.fixture
def job():
    return {
        'version': 1, 'width': 800, 'height': 600,
        'panels': [{'id': 'p', 'box': [0, 0, 800, 600]}],
        'items': [{'id': 'a', 'panel': 'p', 'order': 1, 'kind': 'speech',
                   'speaker': 'singer', 'text': 'La la, little one.',
                   'expected_text': 'La la, little one.', 'font_size': 28,
                   'box': [40, 40, 600, 250], 'breaks': [], 'target': [700, 500]}],
    }


def spans(svg):
    return list(ET.fromstring(svg).iter('{http://www.w3.org/2000/svg}tspan'))


@pytest.mark.parametrize('mode', ['bounce', 'wave'])
def test_baseline_uses_actual_y_and_keeps_source(job, mode):
    job['items'][0]['baseline'] = {'mode': mode, 'amplitude': 3, 'group': 2}
    original = copy.deepcopy(job)
    svg, report = compile_page(job)
    rows = spans(svg)
    assert len({n.get('y') for n in rows}) >= 2
    assert ''.join(n.text or '' for n in rows) == job['items'][0]['text']
    assert job == original and report['ok'] and report['items'][0]['text_preserved']
    assert report['items'][0]['resolved_style']['baseline']['mode'] == mode
    assert len(report['items'][0]['glyph_boxes']) == len(rows)
    # Measured ink moves by exactly the rendered offset; widths stay measured.
    for node, box in zip(rows, report['items'][0]['glyph_boxes']):
        assert box[1] < float(node.get('y'))


def test_emphasis_baseline_is_measured_and_detects_overflow(job):
    item = job['items'][0]
    item['emphasis'] = [{'start': 0, 'end': len(item['text']), 'scale': 1,
                         'baseline_shift': -28}]
    svg, moved = compile_page(job)
    item['emphasis'][0]['baseline_shift'] = 0
    svg0, normal = compile_page(job)
    # Centering includes extra ascent, so final visual shift is half the request.
    assert float(spans(svg)[0].get('y')) == pytest.approx(float(spans(svg0)[0].get('y')) - 14)
    assert moved['items'][0]['glyph_boxes'][0][1] == pytest.approx(normal['items'][0]['glyph_boxes'][0][1] - 14)
    item['box'] = [40, 40, 600, 40]
    item['emphasis'][0]['baseline_shift'] = -28
    _, small = compile_page(job)
    assert any(i['code'] == 'text_overflow' for i in small['issues'])


def test_combining_mark_follows_base_in_bouncy_run(job):
    item = job['items'][0]
    item.update(text='a\u0301b\u0301', expected_text='a\u0301b\u0301', baseline={'mode': 'bounce', 'group': 1})
    svg, _ = compile_page(job)
    assert [n.text for n in spans(svg)] == ['a\u0301', 'b\u0301']


@pytest.mark.parametrize('baseline', [
    {'mode': 'bad'}, {'amplitude': -1}, {'amplitude': 100},
    {'group': 0}, {'group': True}, {'group': 1.5}, {'unknown': 1},
])
def test_invalid_baseline_rejected(job, baseline):
    job['items'][0]['baseline'] = baseline
    with pytest.raises(ValueError):
        compile_page(job)


def test_sfx_and_caption_shape_misuse_rejected(job):
    item = job['items'][0]
    item.update(kind='sfx', baseline={'mode': 'bounce'})
    with pytest.raises(ValueError, match='SFX'):
        compile_page(job)
    item.update(kind='speech', baseline={}, shape='tattered')
    with pytest.raises(ValueError, match='caption'):
        compile_page(job)
    item.update(kind='caption', shape='organic')
    with pytest.raises(ValueError, match='speech'):
        compile_page(job)


@pytest.mark.parametrize('shape,kind', [('organic', 'speech'), ('tattered', 'caption')])
def test_contour_bounded_deterministic_and_editable(job, shape, kind):
    item = job['items'][0]
    item.update(shape=shape, kind=kind)
    svg, report = compile_page(job)
    assert report['ok'] and report['items'][0]['text_preserved']
    path = ET.fromstring(svg).find(".//*[@id='fill-a']").get('d')
    assert path == contour(item['box'], kind, shape)
    coords = re.findall(r'(-?[\d.]+),(-?[\d.]+)', path)
    x, y, w, h = item['box']
    assert all(x <= float(a) <= x+w and y <= float(b) <= y+h for a, b in coords)
    assert path != contour(item['box'], kind)
    assert compile_page(job)[0] == svg


def test_organic_tail_starts_at_actual_boundary():
    box = [40, 40, 600, 250]
    tail = tail_geometry(box, [700, 500], .5, 'speech', shape='organic', options={'length': 36})
    bx, by = tail['boundary']
    nx, ny = (bx - 340)/300, (by - 165)/125
    assert math.hypot(nx, ny) == pytest.approx(organic_radius(math.atan2(ny, nx)))
    assert math.dist(tail['tip'], tail['boundary']) == pytest.approx(36)
