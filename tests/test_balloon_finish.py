import base64
import copy
import io
import json
import os
from xml.etree import ElementTree as ET

import pytest
from PIL import Image, ImageChops

from comic_letterer.engine import compile_page, find_font
from comic_letterer.render import render_png
from comic_letterer.book import value


@pytest.fixture
def job():
    return dict(version=1, width=600, height=400,
                panels=[dict(id='p', box=[0, 0, 600, 400])],
                items=[dict(id='a', panel='p', order=1, kind='speech', speaker='A',
                            text='I remember.', expected_text='I remember.',
                            box=[50, 40, 300, 150], font_size=26, target=[420, 300],
                            fill='#E6D3B6', stroke='#604F43')])


def test_style_roundtrip_and_text_preservation(job):
    job['styles'] = {'paper': {'appearance': {'paper': .2, 'glow': 3}}}
    job['items'][0]['style'] = 'paper'
    original = copy.deepcopy(job)
    svg, report = compile_page(job)
    root = ET.fromstring(svg)
    assert report['ok'] and original == job
    assert ''.join(root.find(".//*[@id='text-a']").itertext()) == 'I remember.'
    assert root.find(".//*[@id='fill-a']").get('fill') == root.find(".//*[@id='tail-a']").get('fill')
    assert not any(n.get('filter') for n in root.find(".//*[@id='text']").iter())
    metadata = json.loads(root.find('{http://www.w3.org/2000/svg}metadata').text)
    assert compile_page(metadata['source'])[0] == svg
    job['items'][0]['appearance'] = None
    disabled = compile_page(job)[0]
    assert '<pattern' not in disabled and 'edge-glow-' not in disabled


@pytest.mark.parametrize('appearance', [False, {'grain': 1}, {'paper': True},
    {'paper': -.1}, {'paper': .31}, {'grain_scale': 0}, {'seed': 1.2},
    {'seed': 65536}, {'glow': float('nan')}, {'glow': 13},
    {'glow_color': 'red'}, {'glow_opacity': 2}, {'whisper_border': 'inside'},
    {'whisper_border': 'center'}])
def test_invalid_effects_fail_before_rendering(job, appearance):
    job['items'][0]['appearance'] = appearance
    with pytest.raises(ValueError):
        compile_page(job)


def test_appearance_is_not_sfx_material(job):
    job['items'][0].update(kind='sfx', appearance={'paper': .1})
    with pytest.raises(ValueError, match='shell'):
        compile_page(job)


def test_shared_join_grain_and_center_border_root_masks(job):
    a = job['items'][0]
    a.update(kind='whisper', box=[30, 25, 220, 120],
             appearance={'paper': .18, 'whisper_border': 'center'})
    b = {**copy.deepcopy(a), 'id': 'b', 'order': 2, 'box': [320, 25, 220, 120], 'join_to': 'a'}
    job['items'].append(b)
    svg, _ = compile_page(job)
    root = ET.fromstring(svg)
    paint = root.find(".//*[@id='fill-a']").get('fill')
    for ident in ('fill-b', 'tail-a', 'join-b'):
        assert root.find(f".//*[@id='{ident}']").get('fill') == paint
    for ident in ('a', 'b'):
        mask = root.find(f".//*[@id='whisper-root-mask-{ident}']")
        assert root.find(".//*[@id='join-b']").get('d') in [n.get('d') for n in mask]
    b['appearance']['paper'] = .1
    with pytest.raises(ValueError, match='joined appearance'):
        compile_page(job)


def test_book_default_effect_values_and_invalid_input(job):
    item = job['items'][0]
    assert value(item, job, 'appearance.paper') == 0
    assert value(item, job, 'appearance.whisper_border') == 'outside'
    item['appearance'] = {'paper': .16}
    assert value(item, job, 'appearance.paper') == .16
    item['appearance']['paper'] = 99
    with pytest.raises(ValueError):
        value(item, job, 'appearance.paper')


@pytest.mark.skipif(os.environ.get('COMIC_LETTERER_RENDER_TEST') != '1', reason='Chromium integration')
def test_real_grain_is_continuous_and_does_not_touch_ink_or_art(job, tmp_path):
    buf = io.BytesIO()
    Image.new('RGB', (600, 400), '#252226').save(buf, format='PNG')
    art = 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()
    font = find_font()
    images = []
    for enabled in (False, True):
        job['items'][0]['appearance'] = {'paper': .22, 'glow': 3} if enabled else None
        svg, _ = compile_page(job, font, background=art)
        path = tmp_path / f'paper-{enabled}.png'
        render_png(svg, path, 600, font)
        images.append(Image.open(path).convert('RGB'))
    plain, finished = images
    # Genuine texture variation inside a text-free part of the balloon.
    samples = [finished.getpixel((x, y)) for y in range(65, 80) for x in range(160, 240)]
    assert len(set(samples)) > 10
    assert ImageChops.difference(plain.crop((0, 330, 600, 400)), finished.crop((0, 330, 600, 400))).getbbox() is None
    # Fully covered ink stays unchanged even with paper/glow behind it.
    ink = [p for p in [(x, y) for y in range(80, 150) for x in range(80, 300)] if plain.getpixel(p) == (32, 32, 42)]
    assert len(ink) > 100
    assert all(finished.getpixel(p) == plain.getpixel(p) for p in ink)
    # Compare every fully covered body/tail pixel to one unbroken paper sheet
    # at the same page coordinates. Joins must not restart/compound the grain.
    root = ET.fromstring(svg)
    ns = '{http://www.w3.org/2000/svg}'
    sheet = ET.Element(ns+'svg', {'width': '600', 'height': '400'})
    sheet.append(copy.deepcopy(root.find(ns+'defs')))
    ET.SubElement(sheet, ns+'rect', {'width': '600', 'height': '400',
        'fill': root.find(".//*[@id='fill-a']").get('fill')})
    path = tmp_path / 'paper-sheet.png'
    render_png(ET.tostring(sheet, encoding='unicode'), path, 600, font)
    reference = Image.open(path).convert('RGB')
    covered = [(x, y) for y in range(40, 310) for x in range(40, 430)
               if plain.getpixel((x, y)) == (230, 211, 182)]
    assert len(covered) > 20000
    assert max(max(abs(a-b) for a,b in zip(finished.getpixel(p),reference.getpixel(p))) for p in covered) <= 1
    # A semantic thought chain receives the same material as its body.
    job['items'][0]['kind'] = 'thought'
    svg, _ = compile_page(job, font, background=art)
    root = ET.fromstring(svg)
    dots = list(root.find(".//*[@id='tails-and-joins']").iter('{http://www.w3.org/2000/svg}circle'))
    assert len(dots) == 3 and all(n.get('fill') == root.find(".//*[@id='fill-a']").get('fill') for n in dots)


@pytest.mark.skipif(os.environ.get('COMIC_LETTERER_RENDER_TEST') != '1', reason='Chromium integration')
def test_whisper_center_edge_has_visible_ink_over_light_paper(job, tmp_path):
    item = job['items'][0]
    item.update(kind='whisper', stroke='#252226', stroke_width=4)
    font = find_font()
    results = []
    for position in ('outside', 'center'):
        item['appearance'] = {'whisper_border': position}
        svg, _ = compile_page(job, font)
        path = tmp_path / f'{position}.png'
        render_png(svg, path, 600, font)
        results.append(Image.open(path).convert('RGB'))
    outside, center = results
    # Just inside the top of the shell: dark dashes survive the fill layer.
    pixels = [(x, y) for y in range(41, 45) for x in range(180, 221)]
    assert sum(max(center.getpixel(p)) < 100 and min(outside.getpixel(p)) > 150 for p in pixels) > 10
