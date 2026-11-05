"""Read-only book proof: actual renders, style audit, font identity, source hashes."""
import base64
import hashlib
import html
import json
from pathlib import Path
from PIL import Image
from .book import audit_book
from .engine import compile_page, find_font
from .fonts import read_font_map
from .narrative import resolve_item
from .render import render_png
from .validation import fields


def proof_book(book, base_dir, assets, asset_dir, output):
    output=Path(output);base_dir=Path(base_dir);asset_dir=Path(asset_dir)
    if output.exists():raise ValueError('proof output already exists; choose a new directory')
    if not isinstance(assets,dict):raise ValueError('assets must map page IDs to local font/background settings')
    ids={p['id'] for p in book.get('pages',[])}
    if set(assets)!=ids:raise ValueError('asset page IDs must exactly match the book')
    audit=audit_book(book,base_dir);issues=list(audit['issues']);prepared=[];font_seen={};hashes=[]
    for entry in book['pages']:
        pid=entry['id'];spec=assets[pid]
        fields(spec,'font font_index font_map background','proof assets')
        def local(key):
            value=spec.get(key)
            if not isinstance(value,str) or not value:raise ValueError('asset '+key+' must be a local path')
            return (asset_dir/value).resolve()
        source_path=(base_dir/entry['path']).resolve();raw=source_path.read_bytes();page=json.loads(raw)
        font=str(local('font')) if spec.get('font') else find_font();index=spec.get('font_index',0)
        fonts=read_font_map(local('font_map')) if spec.get('font_map') else {}
        background=local('background');art=background.read_bytes()
        with Image.open(background) as im:
            if im.format not in ('PNG','JPEG') or list(im.size)!=[page['width'],page['height']]:
                raise ValueError('proof artwork must be a matching PNG/JPEG')
            mime='png' if im.format=='PNG' else 'jpeg';im.verify()
        svg,report=compile_page(page,font,index,f'data:image/{mime};base64,'+base64.b64encode(art).decode(),fonts)
        issues += [{**issue,'page':pid} for issue in report['issues']]
        roles=set()
        for raw_item in page['items']:
            item=resolve_item(raw_item,page.get('styles',{}));roles.add(item.get('font_role','body'))
            roles.update(e.get('font_role',item.get('font_role','body')) for e in item.get('emphasis',[]))
            if item.get('drop_cap'):roles.add(item['drop_cap'].get('font_role',item.get('font_role','body')))
        for role in roles:
            info=report['fonts'][role];key=(entry.get('edition'),role);prior=font_seen.get(key)
            fingerprint=(info['sha256'],info['index'])
            if prior and prior['fingerprint']!=fingerprint:
                issues.append({'code':'font_identity_drift','severity':'error','page':pid,'role':role,'edition':entry.get('edition'),
                               'compared_to':prior['page'],'expected':list(prior['fingerprint']),'actual':list(fingerprint)})
            else:font_seen[key]={'fingerprint':fingerprint,'page':pid}
        digest=hashlib.sha256(raw).hexdigest()
        hashes.append((source_path,digest))
        prepared.append((entry,page,svg,report,font,index,fonts,{'page':pid,'source_sha256':digest,'art_sha256':hashlib.sha256(art).hexdigest()}))
    # A proof is always a new artifact; inputs are never rewritten, even on errors.
    output.mkdir(parents=True)
    cards=[];results=[]
    for entry,page,svg,report,font,index,fonts,provenance in prepared:
        pid=entry['id'];dest=output/pid;dest.mkdir()
        (dest/'page.svg').write_text(svg,encoding='utf-8')
        (dest/'source.json').write_text(json.dumps(page,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        (dest/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        render_png(svg,dest/'reading.png',round(report['reading_width']),font,index,fonts)
        results.append({**provenance,'edition':entry.get('edition'),'items':len(report['items']),'issues':len(report['issues']),
                        'fonts':report['fonts'],'reading_width':report['reading_width']})
        cards.append(f'<article><h2>{html.escape(pid)} · {html.escape(str(entry.get("edition", "")))}</h2>'
                     f'<p>{len(report["issues"])} layout findings · <a href="{pid}/report.json">report</a> · <a href="{pid}/page.svg">SVG</a></p>'
                     f'<a href="{pid}/reading.png"><img src="{pid}/reading.png" alt="{html.escape(pid)} narrative proof"></a></article>')
    unchanged=all(hashlib.sha256(path.read_bytes()).hexdigest()==digest for path,digest in hashes)
    if not unchanged:issues.append({'code':'source_changed_during_proof','severity':'error'})
    result={'version':1,'ok':not any(i['severity']=='error' for i in issues),'issues':issues,'pages':results,
            'recorded_exceptions':audit['recorded_exceptions'],'source_files_unchanged':unchanged,
            'scope':'Rendered layout and explicit house rules; editorial/visual/user acceptance remains separate.'}
    (output/'proof.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    style='body{margin:24px;background:#18202b;color:#eee;font:16px system-ui}a{color:#9ee3ef}.pages{display:flex;flex-wrap:wrap;gap:24px}article{width:min(900px,100%)}img{width:100%;height:auto}h1{font-size:24px}pre{white-space:pre-wrap}'
    detail=html.escape(json.dumps(issues,ensure_ascii=False,indent=2))
    (output/'index.html').write_text(f'<!doctype html><meta charset="utf-8"><title>Comic book proof</title><style>{style}</style>'
                                   f'<h1>Continuous narrative proof</h1><p>{len(results)} pages · {len(issues)} findings. '
                                   'Source files preserved. Visual/user acceptance remains separate.</p>'
                                   f'<details><summary>Audit findings</summary><pre>{detail}</pre></details><main class="pages">'+''.join(cards)+'</main>',encoding='utf-8')
    return result
