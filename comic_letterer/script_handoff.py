"""Strict rich-text script handoff into existing, explicitly mapped page geometry."""
import copy
import hashlib
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import tempfile

from .book import audit_book
from .narrative import resolve_item
from .validation import ident

COLUMNS = ['page', 'panel', 'id', 'order', 'kind', 'speaker', 'voice', 'text', 'note']
INLINE = {'strong', 'b', 'em', 'i'}


class ScriptTable(HTMLParser):
    """One marked table. Unsupported formatting is rejected, never guessed."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []; self.rows = []; self.row = None; self.cell = None
        self.tables = 0

    def handle_starttag(self, tag, attrs):
        if not self.stack:
            if tag != 'table' or dict(attrs).get('data-comic-script') != '1': return
            self.tables += 1
            if self.tables > 1: raise ValueError('exactly one script table is allowed')
            self.stack.append(tag); return
        parent = self.stack[-1]
        if attrs: raise ValueError('attributes inside the script table are unsupported')
        if tag in ('thead', 'tbody') and parent == 'table': pass
        elif tag == 'tr' and parent in ('table', 'thead', 'tbody'): self.row = []
        elif tag in ('td', 'th') and parent == 'tr':
            self.cell = {'tag': tag, 'text': '', 'runs': []}
        elif tag in INLINE and parent in {'td', 'th', *INLINE}: pass
        else: raise ValueError('unsupported or misplaced script tag: '+tag)
        self.stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        if self.stack: raise ValueError('self-closing tags are not supported in script cells')

    def handle_endtag(self, tag):
        if not self.stack: return
        if tag != self.stack[-1]: raise ValueError('unbalanced script markup: '+tag)
        if tag in ('td', 'th'):
            self.row.append(self.cell); self.cell = None
        elif tag == 'tr': self.rows.append(self.row); self.row = None
        self.stack.pop()

    def handle_data(self, data):
        if not self.stack: return
        if self.cell is None:
            if data.strip(): raise ValueError('text outside a script cell')
            return
        start = len(self.cell['text']); self.cell['text'] += data
        bold = any(t in self.stack for t in ('b', 'strong'))
        italic = any(t in self.stack for t in ('i', 'em'))
        role = 'bold_italic' if bold and italic else 'bold' if bold else 'italic' if italic else None
        if role and data:
            runs = self.cell['runs']; end = start+len(data)
            if runs and runs[-1]['end'] == start and runs[-1]['font_role'] == role: runs[-1]['end'] = end
            else: runs.append({'start': start, 'end': end, 'font_role': role})

    def handle_comment(self, data):
        if self.stack: raise ValueError('comments inside the script table are unsupported')


def parse_script(source):
    parser = ScriptTable(); parser.feed(source); parser.close()
    if parser.tables != 1 or parser.stack: raise ValueError('missing or unclosed script table')
    if not parser.rows or [c['text'].strip() for c in parser.rows[0]] != COLUMNS or any(c['tag'] != 'th' for c in parser.rows[0]):
        raise ValueError('script header must be: '+', '.join(COLUMNS))
    entries = {}; rows = []
    for row in parser.rows[1:]:
        if len(row) != len(COLUMNS) or any(c['tag'] != 'td' for c in row): raise ValueError('script row needs nine data cells')
        if any(c['runs'] for n, c in enumerate(row) if COLUMNS[n] != 'text'):
            raise ValueError('rich text is only supported in the text cell')
        entry = {key: c['text'] if key in ('text', 'note') else c['text'].strip() for key, c in zip(COLUMNS, row)}
        for key in ('page', 'panel', 'id'): ident(entry[key])
        if not entry['order'].isascii() or not entry['order'].isdigit() or int(entry['order']) < 1:
            raise ValueError('script order must be a positive integer')
        entry['order'] = int(entry['order'])
        if not entry['text']: raise ValueError('script text must not be empty')
        if any(ord(ch) < 32 for ch in entry['text']):
            raise ValueError('literal line breaks/control characters in text are unsupported; keep layout breaks in the page')
        entry['emphasis'] = row[COLUMNS.index('text')]['runs']
        key = (entry['page'], entry['id'])
        if key in entries: raise ValueError('duplicate script item: '+str(key))
        entries[key] = entry; rows.append(entry)
    if not rows: raise ValueError('script has no items')
    return rows


def _rich_text(row):
    out = []; offset = 0
    for span in row['emphasis']:
        out.append(html.escape(row['text'][offset:span['start']]))
        text = html.escape(row['text'][span['start']:span['end']])
        role = span['font_role']
        if role in ('italic', 'bold_italic'): text = '<em>'+text+'</em>'
        if role in ('bold', 'bold_italic'): text = '<strong>'+text+'</strong>'
        out.append(text); offset = span['end']
    out.append(html.escape(row['text'][offset:]))
    return ''.join(out)


def import_script(script_path, book_path, output):
    script_path = Path(script_path); book_path = Path(book_path); output = Path(output)
    if output.exists(): raise ValueError('script output already exists; choose a new directory')
    script_bytes = script_path.read_bytes(); rows = parse_script(script_bytes.decode('utf-8-sig'))
    book_bytes = book_path.read_bytes(); book = json.loads(book_bytes)
    audit_book(book, book_path.parent)
    entries = {(r['page'], r['id']): r for r in rows}
    originals = {}; pages = {}; expected = set(); effects = []
    for entry in book['pages']:
        pid = entry['id']; path = (book_path.parent/entry['path']).resolve()
        raw = path.read_bytes(); originals[pid] = (path, raw); page = json.loads(raw)
        for item in page['items']:
            key = (pid, item['id']); expected.add(key)
            if key not in entries: raise ValueError('missing script item: '+str(key))
            row = entries[key]; resolved = resolve_item(item, page.get('styles', {}))
            for field in ('panel', 'order', 'kind', 'speaker', 'voice'):
                actual = resolved.get(field, 'normal' if field == 'voice' else '')
                if actual != row[field]: raise ValueError('script metadata mismatch: '+str(key)+'/'+field)
            if 'expected_text' in resolved and resolved['expected_text'] != row['text']:
                raise ValueError('frozen text mismatch: '+str(key))
            if resolved.get('text') and resolved['text'] != row['text']: raise ValueError('existing text mismatch: '+str(key))
            # Existing complex emphasis must not be silently flattened by HTML.
            if item.get('emphasis') and item['emphasis'] != row['emphasis']:
                raise ValueError('existing emphasis differs: '+str(key))
            item['text'] = row['text']; item['expected_text'] = row['text']
            if row['emphasis']: item['emphasis'] = copy.deepcopy(row['emphasis'])
            effects.append({'page': pid, 'item': item['id'], 'note': row['note'], 'text': row['text'],
                            'emphasis': row['emphasis'], 'source_target': item.get('target'),
                            'source_mark': item.get('source_mark'), 'frozen_on_import': True})
        pages[pid] = page
    if set(entries) != expected: raise ValueError('unexpected script items: '+str(sorted(set(entries)-expected)))
    # Only after the entire handoff is reconciled do we create an output version.
    revised = copy.deepcopy(book)
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.script-', dir=output.parent) as temp:
        work = Path(temp); (work/'pages').mkdir()
        (work/'manuscript-source.txt').write_bytes(script_bytes)
        for entry in revised['pages']:
            entry['path'] = 'pages/'+entry['id']+'.json'
            (work/entry['path']).write_text(json.dumps(pages[entry['id']], ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
        (work/'book.json').write_text(json.dumps(revised, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
        audit = audit_book(revised, work)
        preserved = script_bytes == script_path.read_bytes() and book_bytes == book_path.read_bytes() and all(path.read_bytes() == raw for path, raw in originals.values())
        if not preserved: raise ValueError('source changed during script import')
        report = {'version': 1, 'ok': audit['ok'], 'issues': audit['issues'], 'items': effects,
                  'source_files_unchanged': preserved, 'script_sha256': hashlib.sha256(script_bytes).hexdigest(),
                  'book_sha256': hashlib.sha256(book_bytes).hexdigest(),
                  'page_sha256': {pid: hashlib.sha256(raw).hexdigest() for pid, (_, raw) in originals.items()},
                  'required_emphasis_roles': sorted({span['font_role'] for row in rows for span in row['emphasis']}),
                  'rendered': False, 'user_acceptance': 'not_recorded',
                  'scope': 'Structured semantic HTML into explicit existing geometry; run book-proof with actual fonts and art next.'}
        (work/'handoff.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
        cells = ''.join('<tr>'+''.join('<td>'+(_rich_text(row) if k == 'text' else html.escape(str(row[k])))+'</td>' for k in COLUMNS)+'</tr>' for row in rows)
        (work/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>剧本交接核对</title>'
            '<style>body{font:16px system-ui;margin:24px}td,th{border:1px solid #aaa;padding:10px;white-space:pre-wrap}table{border-collapse:collapse}</style>'
            '<h1>剧本交接核对</h1><p>原文与说明分别保留。强调范围见handoff.json；本页不是最终排字校样。</p><table><tr>'
            +''.join('<th>'+k+'</th>' for k in COLUMNS)+'</tr>'+cells+'</table>', encoding='utf-8')
        if output.exists(): raise ValueError('script output appeared during import')
        work.rename(output)
    return report
