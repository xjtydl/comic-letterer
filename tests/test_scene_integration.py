import base64
import copy
import io
import json
import os
from xml.etree import ElementTree as ET

import pytest
from PIL import Image, ImageChops

from comic_letterer.engine import compile_page, find_font, contour
from comic_letterer.organic import prepare
from comic_letterer.custom_path import inside, ray_boundary
from comic_letterer.render import render_png
from comic_letterer.book import value, audit_book


@pytest.fixture
def job():
    return dict(version=1, width=600, height=400, panels=[dict(id='p', box=[0, 0, 600, 400])],
                items=[dict(id='a', panel='p', order=1, kind='speech', speaker='A',
                            text='Stay here.', expected_text='Stay here.', font_size=26,
                            box=[45, 40, 290, 150], target=[420, 300],
                            fill='#E6D3B6', stroke='#604F43', shape='organic',
                            organic=dict(variation=.6, roundness=2.4, seed=17))])


@pytest.mark.parametrize('kind', ['speech', 'whisper', 'thought', 'weak'])
def test_actual_profile_bounds_voice_and_tail_attachment(job, kind):
    a = job['items'][0]; a['kind'] = kind
    if kind == 'thought': a['voice'] = 'telepathic'
    original = copy.deepcopy(job)
    svg, report = compile_page(job)
    assert report['ok'] and job == original
    geometry = prepare(a, a['box'])
    x, y, w, h = a['box']
    assert all(x <= px <= x+w and y <= py <= y+h for px, py in geometry['polygon'])
    assert inside((x+w/2, y+h/2), geometry['polygon'])
    root = ET.fromstring(svg)
    assert root.find(".//*[@id='fill-a']").get('d') == geometry['path']
    assert ''.join(root.find(".//*[@id='text-a']").itertext()) == a['text']
    if kind == 'thought':
        assert len(list(root.find(".//*[@id='tails-and-joins']").iter('{http://www.w3.org/2000/svg}circle'))) == 3
    else:
        from comic_letterer.engine import tail_geometry
        tail = tail_geometry(a['box'], a['target'], .5, kind, shape='organic',
                             options={'_polygon': geometry['polygon']})
        center = (x+w/2, y+h/2)
        assert tail['boundary'] == ray_boundary(center, [a['target'][i]-center[i] for i in (0, 1)], geometry['polygon'])


def test_legacy_profile_roundtrip_and_real_shape_fit(job):
    a = job['items'][0]
    first, report = compile_page(job)
    a['organic']['seed'] = 32
    assert ET.fromstring(first).find(".//*[@id='fill-a']").get('d') != ET.fromstring(compile_page(job)[0]).find(".//*[@id='fill-a']").get('d')
    metadata = json.loads(ET.fromstring(first).find('{http://www.w3.org/2000/svg}metadata').text)
    assert compile_page(metadata['source'])[0] == first
    a['organic'] = None
    assert ET.fromstring(compile_page(job)[0]).find(".//*[@id='fill-a']").get('d') == contour(a['box'], 'speech', 'organic')
    a.update(text='Keep this exact wording intact.', expected_text='Keep this exact wording intact.', box=[45, 40, 130, 90])
    a['organic'] = {'variation': 1, 'roundness': 2}
    assert any(i['code'] == 'text_overflow' for i in compile_page(job)[1]['issues'])


@pytest.mark.parametrize('profile', [False, {'variation': True}, {'variation': 1.01},
    {'roundness': 1.9}, {'seed': -1}, {'seed': .5}, {'noise': 1}])
def test_invalid_organic_profile_rejected(job, profile):
    job['items'][0]['organic'] = profile
    with pytest.raises(ValueError): compile_page(job)


@pytest.mark.parametrize('appearance', [{'wash_opacity': True}, {'wash_opacity': .36},
    {'wash_angle': float('nan')}, {'wash_angle': 181}, {'wash_color': 'red'}])
def test_invalid_wash_rejected(job, appearance):
    job['items'][0]['appearance'] = appearance
    with pytest.raises(ValueError): compile_page(job)


def test_joined_wash_and_book_parameters(job):
    a = job['items'][0]
    a.update(box=[25, 30, 220, 125], appearance={'wash_color': '#705440', 'wash_opacity': .2, 'wash_angle': 25})
    job['items'].append({**copy.deepcopy(a), 'id': 'b', 'box': [320, 30, 220, 125], 'order': 2, 'join_to': 'a'})
    root = ET.fromstring(compile_page(job)[0])
    paint = root.find(".//*[@id='fill-a']").get('fill')
    for ident in ('fill-b', 'tail-a', 'join-b'):
        assert root.find(f".//*[@id='{ident}']").get('fill') == paint
    assert len(list(root.iter('{http://www.w3.org/2000/svg}linearGradient'))) == 1
    assert value(a, job, 'appearance.wash_opacity') == .2
    assert value(a, job, 'organic.roundness') == 2.4
    job['items'][1]['appearance']['wash_angle'] = 90
    with pytest.raises(ValueError, match='joined appearance'): compile_page(job)


def test_old_whole_appearance_rule_does_not_drift_when_defaults_expand(job, tmp_path):
    job['items'][0]['appearance'] = {'paper': .12}
    (tmp_path/'page.json').write_text(json.dumps(job))
    old = dict(paper=.12, grain_scale=1, seed=17, glow=0,
               glow_color='#DDC9A0', glow_opacity=.45, whisper_border='outside')
    book = dict(version=1, pages=[dict(id='p', path='page.json')],
                rules=[dict(id='style', match={}, expect={'appearance': old, 'organic': {'variation': .6, 'roundness': 2.4}})])
    assert audit_book(book, tmp_path)['ok']
    job['items'][0]['appearance']['wash_opacity'] = .2
    (tmp_path/'page.json').write_text(json.dumps(job))
    result = audit_book(book, tmp_path)
    assert not result['ok'] and result['issues'][0]['field'] == 'appearance'
    # A requested profile on a plain ellipse must report drift, not None==None.
    job['items'][0].update(shape='ellipse', organic=None, appearance={'paper': .12})
    (tmp_path/'page.json').write_text(json.dumps(job))
    result = audit_book(book, tmp_path)
    assert not result['ok'] and result['issues'][0]['field'] == 'organic'


def test_organic_cannot_silently_swallow_foreign_shape_parameters(job):
    job['items'][0]['mechanical'] = {'band': 7}
    with pytest.raises(ValueError, match='matching shape'): compile_page(job)


@pytest.mark.skipif(os.environ.get('COMIC_LETTERER_RENDER_TEST') != '1', reason='Chromium integration')
def test_real_opaque_wash_grain_no_tile_restart_and_untouched_ink_art(job, tmp_path):
    a = job['items'][0]
    a.update(box=[35, 25, 500, 220], tail={'width': 38, 'length': 80}, target=[480, 350])
    buf = io.BytesIO(); Image.new('RGB', (600, 400), '#252226').save(buf, format='PNG')
    art = 'data:image/png;base64,'+base64.b64encode(buf.getvalue()).decode()
    font = find_font(); images = []
    for enabled in (False, True):
        a['appearance'] = dict(wash_opacity=.3, wash_color='#705440', wash_angle=0, paper=.12) if enabled else None
        svg, report = compile_page(job, font, background=art)
        assert report['ok']
        path = tmp_path/f'wash-{enabled}.png'
        render_png(svg, path, 600, font)
        images.append(Image.open(path).convert('RGB'))
    plain, finished = images
    assert ImageChops.difference(plain.crop((0, 360, 600, 400)), finished.crop((0, 360, 600, 400))).getbbox() is None
    ink = [(x, y) for y in range(80, 180) for x in range(180, 400) if plain.getpixel((x, y)) == (32, 32, 42)]
    assert len(ink) > 100 and all(finished.getpixel(p) == plain.getpixel(p) for p in ink)
    # Equal positions in adjacent 128px tiles must continue darkening.
    means = [sum(finished.getpixel((x+dx, y))[0] for dx in range(12) for y in range(78, 88))/120 for x in (130, 258, 386)]
    assert means[0] > means[1]+5 > means[2]+10
    # Compare solid coverage against one uninterrupted material sheet.
    root = ET.fromstring(svg); ns = '{http://www.w3.org/2000/svg}'
    sheet = ET.Element(ns+'svg', {'width': '600', 'height': '400'})
    sheet.append(copy.deepcopy(root.find(ns+'defs')))
    ET.SubElement(sheet, ns+'rect', {'width': '600', 'height': '400', 'fill': root.find(".//*[@id='fill-a']").get('fill')})
    path = tmp_path/'sheet.png'; render_png(ET.tostring(sheet, encoding='unicode'), path, 600, font)
    reference = Image.open(path).convert('RGB')
    covered = [(x, y) for y in range(25, 350) for x in range(35, 540) if plain.getpixel((x, y)) == (230, 211, 182)]
    assert len(covered) > 60000
    assert max(max(abs(a-b) for a, b in zip(finished.getpixel(p), reference.getpixel(p))) for p in covered) <= 1
