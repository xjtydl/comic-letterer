"""Compare authored layouts using intact narrative panels and real lettering."""
import copy
import hashlib
import html
import json
import tempfile
from pathlib import Path
from xml.etree import ElementTree as ET

from PIL import Image
from .engine import compile_page
from .render import render_png
from .validation import fields, ident, number, vector

NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)


def _inside(a, b, tolerance=.1):
    return a[0] >= b[0]-tolerance and a[1] >= b[1]-tolerance and a[0]+a[2] <= b[0]+b[2]+tolerance and a[1]+a[3] <= b[1]+b[3]+tolerance


def _intersects(a, b):
    return min(a[0]+a[2], b[0]+b[2]) > max(a[0], b[0])+.1 and min(a[1]+a[3], b[1]+b[3]) > max(a[1], b[1])+.1


def compile_layouts(page, source_svg, source_report, plan):
    fields(plan, 'version source_sha256 variants', 'layout plan')
    if type(plan.get('version')) is not int or plan['version'] != 1:
        raise ValueError('layout version must be 1')
    if not isinstance(plan.get('variants'), list) or not plan['variants']:
        raise ValueError('layout variants must be a nonempty array')
    panels = {p['id']: p['box'] for p in page['panels']}
    panel_ids = list(panels)
    raw_items = {i['id']: i for i in page['items']}
    variants = []; seen = set()
    for variant in plan['variants']:
        fields(variant, 'id title width height reading_width placements', 'layout variant')
        vid = ident(variant.get('id'))
        if vid in seen: raise ValueError('duplicate layout variant')
        seen.add(vid)
        if not isinstance(variant.get('title'), str) or not variant['title'].strip():
            raise ValueError('layout title required')
        w = number(variant.get('width'), 'layout width', True)
        h = number(variant.get('height'), 'layout height', True)
        rw = number(variant.get('reading_width', w), 'layout reading_width', True)
        if max(w, h) > 50000: raise ValueError('layout dimensions exceed 50000')
        placements = variant.get('placements')
        if not isinstance(placements, list): raise ValueError('placements must be an array')
        for placement in placements:
            fields(placement, 'panel box beat', 'layout placement')
            ident(placement.get('panel'))
            if not isinstance(placement.get('beat'), str) or not placement['beat'].strip():
                raise ValueError('each panel needs its narrative beat')
        if [p['panel'] for p in placements] != panel_ids:
            raise ValueError('placements must contain every source panel exactly once, in narrative order')
        issues = copy.deepcopy(source_report['issues'])
        mapped = []; items = []
        for placement in placements:
            pid = placement['panel']; slot = vector(placement.get('box'), 4, 'layout box', box=True)
            if not _inside(slot, [0, 0, w, h], 0): raise ValueError('layout slot outside canvas')
            sx, sy, sw, sh = panels[pid]
            scale = min(slot[2]/sw, slot[3]/sh)
            box = [slot[0]+(slot[2]-sw*scale)/2, slot[1]+(slot[3]-sh*scale)/2, sw*scale, sh*scale]
            mapped.append({'panel': pid, 'box': box, 'slot': slot, 'scale': scale, 'source_box': panels[pid], 'beat': placement['beat']})
            for item in source_report['items']:
                raw = raw_items[item['id']]
                if raw['panel'] != pid: continue
                # Nothing is silently cropped merely to make a new layout work.
                for field in ['glyph_boxes', 'voice_mark_boxes']:
                    if any(not _inside(b, panels[pid]) for b in item.get(field, [])):
                        issues.append({'code': 'layout_text_clipped', 'severity': 'error', 'panel': pid, 'item': item['id'], 'part': field})
                if not _inside(item['box'], panels[pid]):
                    issues.append({'code': 'layout_shell_clipped', 'severity': 'error', 'panel': pid, 'item': item['id']})
                tip = item.get('tail_tip')
                if tip and not _inside([*tip, 0, 0], panels[pid]):
                    issues.append({'code': 'layout_tail_clipped', 'severity': 'error', 'panel': pid, 'item': item['id']})
                reading_size = item['font_size']*scale*rw/w
                if reading_size < page.get('min_reading_font', 14):
                    issues.append({'code': 'layout_text_small', 'severity': 'warning', 'panel': pid, 'item': item['id'], 'reading_font_size': reading_size})
                items.append({'id': item['id'], 'panel': pid, 'text': raw['text'], 'reading_font_size': reading_size})
        for n, a in enumerate(mapped):
            ax, ay, aw, ah = a['box']
            for b in mapped[n+1:]:
                bx, by, bw, bh = b['box']
                if _intersects(a['box'], b['box']):
                    issues.append({'code': 'layout_panel_overlap', 'severity': 'error', 'panels': [a['panel'], b['panel']]})
                # Conservative LTR/RTL checks, not a general visual-reading model.
                vertical_overlap = min(ay+ah, by+bh) > max(ay, by)+.1
                backwards = bx+bw <= ax+.1 if page.get('direction', 'ltr') == 'ltr' else ax+aw <= bx+.1
                if by+bh <= ay+.1 or (vertical_overlap and backwards):
                    issues.append({'code': 'layout_order_conflict', 'severity': 'error', 'panels': [a['panel'], b['panel']]})
                # Small center-fit differences are not evidence of a staggered group.
                elif vertical_overlap and abs(ay-by) > max(1, min(ah, bh)*.01) and abs(ay+ah-by-bh) > max(1, min(ah, bh)*.01):
                    issues.append({'code': 'layout_grouping_review', 'severity': 'warning', 'panels': [a['panel'], b['panel']]})
        svg = _compose(source_svg, w, h, mapped)
        report = {'version': 1, 'id': vid, 'title': variant['title'], 'ok': not any(i['severity'] == 'error' for i in issues),
                  'issues': issues, 'width': w, 'height': h, 'reading_width': rw, 'panels': mapped, 'items': items,
                  'fonts': source_report['fonts'], 'user_acceptance': 'not_recorded',
                  'scope': 'Intact panel placement, conservative reading/crop/type checks; not generated art or automatic narrative acceptance.'}
        variants.append((svg, report))
    return variants


def _compose(source_svg, width, height, panels):
    def element(tag, attrs, parent): return ET.SubElement(parent, f'{{{NS}}}{tag}', {k: str(v) for k, v in attrs.items()})
    root = ET.Element(f'{{{NS}}}svg', {'width': str(width), 'height': str(height), 'viewBox': f'0 0 {width} {height}'})
    defs = element('defs', {}, root)
    source = ET.fromstring(source_svg)
    # Prefix source IDs/references once; every use retains editable Unicode.
    ids = {e.get('id'): 'source-'+e.get('id') for e in source.iter() if e.get('id')}
    for node in source.iter():
        for key, val in list(node.attrib.items()):
            if key == 'id': node.set(key, ids[val])
            elif val.startswith('#') and val[1:] in ids: node.set(key, '#'+ids[val[1:]])
            elif val.startswith('url(#') and val.endswith(')') and val[5:-1] in ids: node.set(key, 'url(#'+ids[val[5:-1]]+')')
    group = element('g', {'id': 'layout-source'}, defs)
    group.extend(list(source))
    element('rect', {'width': width, 'height': height, 'fill': '#F5EFE3'}, root)
    for n, panel in enumerate(panels):
        x, y, _, _ = panel['box']; sx, sy, sw, sh = panel['source_box']; scale = panel['scale']
        clip = element('clipPath', {'id': f'layout-clip-{n}', 'clipPathUnits': 'userSpaceOnUse'}, defs)
        element('rect', {'x': sx, 'y': sy, 'width': sw, 'height': sh}, clip)
        outer = element('g', {'data-panel': panel['panel'], 'transform': f'translate({x} {y}) scale({scale}) translate({-sx} {-sy})'}, root)
        cropped = element('g', {'clip-path': f'url(#layout-clip-{n})'}, outer)
        element('use', {'href': '#layout-source'}, cropped)
    return ET.tostring(root, encoding='unicode')


def layout_proof(source_path, plan, font, index, fonts, background, output):
    import base64
    source_path = Path(source_path); background = Path(background); output = Path(output)
    if output.exists(): raise ValueError('layout output already exists; choose a new directory')
    raw = source_path.read_bytes()
    if plan.get('source_sha256') != hashlib.sha256(raw).hexdigest(): raise ValueError('stale layout source hash')
    page = json.loads(raw); art = background.read_bytes()
    with Image.open(background) as im:
        if im.format not in ('PNG', 'JPEG') or list(im.size) != [page['width'], page['height']]:
            raise ValueError('layout artwork must be a matching PNG/JPEG')
        mime = 'png' if im.format == 'PNG' else 'jpeg'; im.verify()
    svg, source_report = compile_page(page, font, index, 'data:image/'+mime+';base64,'+base64.b64encode(art).decode(), fonts)
    variants = compile_layouts(page, svg, source_report, plan)
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.layout-', dir=output.parent) as temp:
        work = Path(temp); (work/'source.json').write_bytes(raw)
        (work/'source.svg').write_text(svg, encoding='utf-8')
        (work/'plan.json').write_text(json.dumps(plan, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
        cards = []
        for composed, report in variants:
            target = work/report['id']; target.mkdir()
            (target/'page.svg').write_text(composed, encoding='utf-8')
            (target/'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
            render_png(composed, target/'reading.png', round(report['reading_width']), font, index, fonts)
            cards.append(f'<article><h2>{html.escape(report["title"])}</h2><p>{len(report["issues"])} findings · '
                         f'<a href="{report["id"]}/report.json">报告</a> · <a href="{report["id"]}/page.svg">SVG</a></p>'
                         f'<img src="{report["id"]}/reading.png" alt="{html.escape(report["title"])}"></article>')
        issues = [{**i, 'variant': r['id']} for _, r in variants for i in r['issues']]
        unchanged = raw == source_path.read_bytes() and art == background.read_bytes()
        if not unchanged: issues.append({'code': 'layout_source_changed', 'severity': 'error'})
        result = {'version': 1, 'ok': not any(i['severity'] == 'error' for i in issues), 'issues': issues,
                  'source_sha256': hashlib.sha256(raw).hexdigest(), 'art_sha256': hashlib.sha256(art).hexdigest(),
                  'sources_unchanged': unchanged, 'variants': [r for _, r in variants], 'user_acceptance': 'not_recorded'}
        (work/'layout.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
        (work/'index.html').write_text('<!doctype html><html lang="zh"><meta charset="utf-8"><title>实际漫画布局对照</title>'
            '<style>body{background:#18202b;color:#eee;font:16px system-ui;margin:24px}a{color:#9ee3ef}.variants{display:flex;align-items:start;gap:24px;overflow:auto}'
            'article{flex:0 0 600px}img{width:100%;height:auto}header{position:sticky;top:0;background:#18202b;padding:10px}</style>'
            '<header><h1>实际漫画布局对照</h1><p>画稿与文字一起等比置入；固定600px对照仅是预览，检查以各方案配置阅读宽度为准。'
            '声音、构图与用户验收仍需实看。</p></header><main class="variants">'+''.join(cards)+'</main></html>', encoding='utf-8')
        if output.exists(): raise ValueError('layout output appeared during render')
        work.rename(output)
    return result
