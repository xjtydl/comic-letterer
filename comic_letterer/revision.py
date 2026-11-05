"""Explicit book revisions with stale-input guards and complete reading proofs."""
import copy
import hashlib
import html
import json
import tempfile
from pathlib import Path

from .book import EXPECT, audit_book, value
from .narrative import resolve_item
from .proof import proof_book
from .validation import fields, ident

# No words, speakers, voice kinds, sources, art, panels or protected regions.
ITEM_FIELDS = set(('font_size font_role fill stroke text_color stroke_width padding '
                   'tracking horizontal_scale line_height features box breaks '
                   'line_widths line_scales keep_together tail.width tail.gap '
                   'baseline.amplitude').split())
PAGE_FIELDS = {'reading_width'}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def book_digest(book):
    """Canonical metadata hash; page bytes are guarded separately."""
    return digest(json.dumps(book, ensure_ascii=False, sort_keys=True,
                             separators=(',', ':'), allow_nan=False).encode())


def write_json(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')


def _same(a, b):
    # Booleans must not match numeric preconditions.
    return json.dumps(a, sort_keys=True, allow_nan=False) == json.dumps(b, sort_keys=True, allow_nan=False) or (
        type(a) in (int, float) and type(b) in (int, float) and a == b)


def _set_field(raw, effective, field, after):
    parts = field.split('.')
    if len(parts) == 1:
        raw[field] = copy.deepcopy(after)
    else:
        # Styles are shallow-merged by the renderer; retain inherited siblings.
        raw[parts[0]] = copy.deepcopy(effective.get(parts[0], {}))
        raw[parts[0]][parts[1]] = copy.deepcopy(after)


def prepare_revision(book, base_dir, plan):
    """Validate all preconditions in memory; never modify an input object/file."""
    fields(plan, 'version title book_sha256 page_sha256 changes rule_changes', 'revision plan')
    if type(plan.get('version')) is not int or plan['version'] != 1:
        raise ValueError('revision version must be 1')
    if not isinstance(plan.get('title'), str) or not plan['title'].strip():
        raise ValueError('revision needs a title')
    if plan.get('book_sha256') != book_digest(book):
        raise ValueError('stale book: revision metadata hash differs')
    audit_book(book, base_dir)  # Validate manifest, IDs, rules and exceptions.
    ids = {p['id'] for p in book['pages']}
    if not isinstance(plan.get('page_sha256'), dict) or set(plan['page_sha256']) != ids:
        raise ValueError('page_sha256 must cover exactly all book pages')
    original = {}; paths = {}; raw_bytes = {}
    for entry in book['pages']:
        pid = entry['id']; path = (Path(base_dir)/entry['path']).resolve()
        raw = path.read_bytes()
        if plan['page_sha256'][pid] != digest(raw):
            raise ValueError('stale page: '+pid)
        original[pid] = json.loads(raw); paths[pid] = path; raw_bytes[pid] = raw
    pages = copy.deepcopy(original); revised = copy.deepcopy(book)
    changes = plan.get('changes', []); rules = plan.get('rule_changes', [])
    if not isinstance(changes, list) or not isinstance(rules, list) or not (changes or rules):
        raise ValueError('revision needs nonempty change arrays')
    seen = set()
    for change in changes:
        fields(change, 'page item field before after reason', 'revision change')
        pid = ident(change.get('page')); iid = change.get('item'); field = change.get('field')
        if pid not in pages: raise ValueError('unknown revision page')
        if iid is not None: ident(iid)
        allowed = ITEM_FIELDS if iid is not None else PAGE_FIELDS
        if not isinstance(field, str) or field not in allowed:
            raise ValueError('unsupported revision field; frozen text and narrative are not editable')
        key = (pid, iid, field)
        _check_change(change, key, seen)
        page = pages[pid]
        if iid is None:
            actual = original[pid].get(field, original[pid].get('width'))
            raw = page; effective = page
        else:
            old = next((i for i in original[pid]['items'] if i['id'] == iid), None)
            if old is None: raise ValueError('unknown revision item')
            old_effective = resolve_item(old, original[pid].get('styles', {}))
            actual = value(old_effective, original[pid], field) if field in EXPECT else old_effective.get(field)
            raw = next(i for i in page['items'] if i['id'] == iid)
            effective = resolve_item(raw, page.get('styles', {}))
        if not _same(actual, change['before']):
            raise ValueError(f'previous value mismatch: {pid}/{iid or "page"}/{field}')
        _set_field(raw, effective, field, change['after'])
    by_rule = {r['id']: r for r in revised['rules']}
    for change in rules:
        fields(change, 'rule field before after reason', 'revision rule change')
        rid = ident(change.get('rule')); field = change.get('field')
        if rid not in by_rule or not isinstance(field, str) or field not in by_rule[rid]['expect']:
            raise ValueError('rule changes must target an existing expectation')
        _check_change(change, ('rule', rid, field), seen)
        if not _same(by_rule[rid]['expect'][field], change['before']):
            raise ValueError('previous rule value mismatch')
        by_rule[rid]['expect'][field] = copy.deepcopy(change['after'])
    return original, pages, revised, paths, raw_bytes


def _check_change(change, key, seen):
    if key in seen: raise ValueError('duplicate revision target')
    seen.add(key)
    if not {'before', 'after', 'reason'} <= change.keys():
        raise ValueError('each revision needs before, after and reason')
    if not isinstance(change['reason'], str) or not change['reason'].strip():
        raise ValueError('each revision needs a reason')
    if _same(change['before'], change['after']):
        raise ValueError('revision must change the value')


def revise_book(book, base_dir, plan, assets, asset_dir, output):
    output = Path(output)
    if output.exists(): raise ValueError('revision output already exists; choose a new directory')
    original, pages, revised, paths, raw_bytes = prepare_revision(book, base_dir, plan)
    output.parent.mkdir(parents=True, exist_ok=True)
    # Failed input/render operations leave no misleading half-complete delivery.
    with tempfile.TemporaryDirectory(prefix='.revision-', dir=output.parent) as temp:
        work = Path(temp); before_book = copy.deepcopy(book)
        (work/'before-pages').mkdir(); (work/'pages').mkdir()
        for entry in before_book['pages']:
            pid = entry['id']; entry['path'] = f'before-pages/{pid}.json'
            (work/entry['path']).write_bytes(raw_bytes[pid])
        for entry in revised['pages']:
            pid = entry['id']; entry['path'] = f'pages/{pid}.json'
            write_json(work/entry['path'], pages[pid])
        write_json(work/'before-book.json', before_book)
        write_json(work/'book.json', revised); write_json(work/'plan.json', plan)
        before = proof_book(before_book, work, assets, asset_dir, work/'before')
        after = proof_book(revised, work, assets, asset_dir, work/'after')
        issues = list(after['issues'])
        preserved = all(paths[pid].read_bytes() == raw for pid, raw in raw_bytes.items())
        if not preserved: issues.append({'code': 'source_changed_during_revision', 'severity': 'error'})
        for old, new in zip(before['pages'], after['pages']):
            if old['art_sha256'] != new['art_sha256'] or old['fonts'] != new['fonts']:
                issues.append({'code': 'assets_changed_during_revision', 'severity': 'error', 'page': old['page']})
        result = {'version': 1, 'title': plan['title'], 'ok': not any(i['severity'] == 'error' for i in issues),
                  'issues': issues, 'before_issues': before['issues'], 'source_files_unchanged': preserved,
                  'text_preserved': all([i.get('text') for i in original[p]['items']] ==
                                        [i.get('text') for i in pages[p]['items']] for p in pages),
                  'changes': plan.get('changes', []), 'rule_changes': plan.get('rule_changes', []),
                  'recorded_exceptions': after['recorded_exceptions'],
                  'pages': [{'id': p, 'before_sha256': digest(raw_bytes[p]),
                             'after_sha256': digest((work/f'pages/{p}.json').read_bytes())} for p in pages],
                  'user_acceptance': 'not_recorded',
                  'scope': 'Explicit revision and rendered comparison; not automatic visual or editorial acceptance.'}
        write_json(work/'revision.json', result)
        _comparison(work, book, plan, result)
        if output.exists(): raise ValueError('revision output appeared during render')
        work.rename(output)
    return result


def _comparison(work, book, plan, result):
    cards = []
    for entry in book['pages']:
        pid = entry['id']
        edits = [c for c in plan.get('changes', []) if c['page'] == pid]
        rows = ''.join('<li>'+html.escape(f'{c.get("item", "page")} · {c["field"]}: '
                                         f'{c["before"]} → {c["after"]} — {c["reason"]}')+'</li>' for c in edits)
        cards.append(f'<section><h2>{html.escape(pid)}</h2><ul>{rows}</ul><div class="pair">'+''.join(
            f'<figure><figcaption>{label} · <a href="{side}/{pid}/page.svg">SVG</a></figcaption>'
            f'<a href="{side}/{pid}/reading.png"><img src="{side}/{pid}/reading.png" alt="{pid} {side}"></a></figure>'
            for side, label in [('before', '修订前 / Before'), ('after', '修订后 / After')])+'</div></section>')
    style = ('body{margin:24px;background:#18202b;color:#eee;font:16px system-ui}a{color:#9ee3ef}'
             '.pair{display:flex;gap:20px;overflow:auto}figure{margin:0;flex:0 0 var(--reading,600px)}'
             'img{width:100%;height:auto}li{margin:6px 0}section{margin:32px 0}figcaption{margin:10px 0}'
             'button,select{font:inherit}header{position:sticky;top:0;background:#18202b;padding:12px 0}')
    text = html.escape(plan['title'])
    (work/'index.html').write_text(f'<!doctype html><html lang="zh"><meta charset="utf-8"><title>{text}</title>'
        f'<style>{style}</style><header><h1>{text}</h1><p>{len(result["issues"])} findings · '
        '<a href="revision.json">修订记录</a> · <a href="before/index.html">原版连续阅读</a> · '
        '<a href="after/index.html">新版连续阅读</a></p>'
        '<label>对照显示宽度 <select aria-label="Reading width" onchange="document.documentElement.style.setProperty(\'--reading\',this.value+\'px\')">'
        '<option>600</option><option>900</option><option>450</option></select> px</label>'
        '<p>完整页面同宽对照；缩览不代表该尺寸已通过字号检查。用户验收未记录。</p></header>'
        +''.join(cards)+'</html>', encoding='utf-8')
