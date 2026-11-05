import copy
import hashlib
import json
import os
from pathlib import Path
from xml.etree import ElementTree as ET

import pytest
from PIL import Image
from comic_letterer.engine import compile_page
from comic_letterer.layout import compile_layouts, layout_proof
from comic_letterer.letterforms import build_font


def prepared(tmp_path):
    build_font(json.loads(Path('examples/last-ticket-hand.json').read_text()), tmp_path/'font.ttf')
    page = {'version': 1, 'width': 600, 'height': 400, 'reading_width': 600,
            'panels': [{'id': 'a', 'box': [0, 0, 295, 400]}, {'id': 'b', 'box': [305, 0, 295, 400]}],
            'items': [{'id': 'one', 'panel': 'a', 'kind': 'caption', 'order': 1, 'text': 'HOME', 'expected_text': 'HOME', 'font_size': 28, 'box': [20, 20, 230, 100]},
                      {'id': 'two', 'panel': 'b', 'kind': 'caption', 'order': 1, 'text': 'HOME', 'expected_text': 'HOME', 'font_size': 28, 'box': [330, 20, 230, 100]}]}
    raw = json.dumps(page).encode(); (tmp_path/'page.json').write_bytes(raw)
    plan = {'version': 1, 'source_sha256': hashlib.sha256(raw).hexdigest(), 'variants': [
        {'id': 'columns', 'title': 'Side by side', 'width': 600, 'height': 400, 'placements': [
            {'panel': 'a', 'box': [0, 0, 295, 400], 'beat': 'Arrival'},
            {'panel': 'b', 'box': [305, 0, 295, 400], 'beat': 'Recognition'}]}]}
    return page, plan, str(tmp_path/'font.ttf')


def test_layout_preserves_text_aspect_and_measured_size(tmp_path):
    page, plan, font = prepared(tmp_path); before = copy.deepcopy(page)
    svg, report = compile_page(page, font)
    result, r = compile_layouts(page, svg, report, plan)[0]
    assert not r['issues'] and page == before
    assert [i['text'] for i in r['items']] == ['HOME', 'HOME']
    assert r['items'][0]['reading_font_size'] == 28
    assert all(p['scale'] == 1 for p in r['panels'])
    tree = ET.fromstring(result)
    assert len(tree.findall('.//{http://www.w3.org/2000/svg}use')) == 2


@pytest.mark.parametrize('bad', ['missing', 'duplicate', 'order', 'outside', 'beat'])
def test_layout_plan_rejects_ambiguous_or_incomplete_mapping(tmp_path, bad):
    page, plan, font = prepared(tmp_path); v = plan['variants'][0]
    if bad == 'missing': v['placements'].pop()
    elif bad == 'duplicate': v['placements'][1]['panel'] = 'a'
    elif bad == 'order': v['placements'].reverse()
    elif bad == 'outside': v['placements'][0]['box'][0] = -1
    else: v['placements'][0]['beat'] = ''
    svg, report = compile_page(page, font)
    with pytest.raises(ValueError): compile_layouts(page, svg, report, plan)


def test_geometry_conflicts_and_reading_size_are_reported(tmp_path):
    page, plan, font = prepared(tmp_path); v = plan['variants'][0]
    v['placements'][0]['box'], v['placements'][1]['box'] = v['placements'][1]['box'], v['placements'][0]['box']
    v['reading_width'] = 200
    svg, report = compile_page(page, font)
    _, r = compile_layouts(page, svg, report, plan)[0]
    assert {'layout_order_conflict', 'layout_text_small'} <= {i['code'] for i in r['issues']}
    v['placements'][0]['box'] = v['placements'][1]['box']
    _, r = compile_layouts(page, svg, report, plan)[0]
    assert any(i['code'] == 'layout_panel_overlap' for i in r['issues'])


def test_cross_border_shell_and_glyphs_cannot_be_silently_cropped(tmp_path):
    page, plan, font = prepared(tmp_path)
    svg, report = compile_page(page, font)
    report['items'][0]['box'] = [-10, 20, 230, 100]
    report['items'][0]['glyph_boxes'] = [[-1, 30, 20, 20]]
    _, r = compile_layouts(page, svg, report, plan)[0]
    assert {'layout_shell_clipped', 'layout_text_clipped'} <= {i['code'] for i in r['issues']}


def test_center_fit_rounding_does_not_invent_ambiguous_rows(tmp_path):
    page, plan, font = prepared(tmp_path)
    page['panels'][1]['box'][2] = 294
    svg, report = compile_page(page, font)
    _, r = compile_layouts(page, svg, report, plan)[0]
    assert not any(i['code'] == 'layout_grouping_review' for i in r['issues'])


@pytest.mark.skipif(os.environ.get('COMIC_LETTERER_RENDER_TEST') != '1', reason='optional browser integration')
def test_actual_raster_keeps_panels_and_source_untouched(tmp_path):
    page, plan, font = prepared(tmp_path)
    art = Image.new('RGB', (600, 400), '#ef2222'); art.paste('#2255ee', (305, 0, 600, 400)); art.save(tmp_path/'art.png')
    raw = (tmp_path/'page.json').read_bytes(); art_raw = (tmp_path/'art.png').read_bytes()
    result = layout_proof(tmp_path/'page.json', plan, font, 0, {}, tmp_path/'art.png', tmp_path/'out')
    assert result['ok'] and result['sources_unchanged']
    with Image.open(tmp_path/'out/columns/reading.png') as im:
        assert im.getpixel((100, 300))[:3] == (239, 34, 34)
        assert im.getpixel((400, 300))[:3] == (34, 85, 238)
        # Glyph pixels must render from the reused source, not just colored panels.
        assert any(max(im.getpixel((x, y))[:3]) < 100 for x in range(50, 220) for y in range(30, 100))
    assert raw == (tmp_path/'page.json').read_bytes() and art_raw == (tmp_path/'art.png').read_bytes()
    with pytest.raises(ValueError, match='already exists'):
        layout_proof(tmp_path/'page.json', plan, font, 0, {}, tmp_path/'art.png', tmp_path/'out')
    plan['source_sha256'] = 'stale'
    with pytest.raises(ValueError, match='stale'):
        layout_proof(tmp_path/'page.json', plan, font, 0, {}, tmp_path/'art.png', tmp_path/'new')
    assert not (tmp_path/'new').exists()
