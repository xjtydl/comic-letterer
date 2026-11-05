import copy
import html
import json
from pathlib import Path

import pytest
from comic_letterer.script_handoff import COLUMNS, import_script, parse_script
from comic_letterer.cli import main
from test_proof import prepared


def table(rows):
    return '<table data-comic-script="1"><thead><tr>'+''.join('<th>'+k+'</th>' for k in COLUMNS)+'</tr></thead><tbody>'+''.join(
        '<tr>'+''.join('<td>'+str(value)+'</td>' for value in row)+'</tr>' for row in rows)+'</tbody></table>'


def fixture(tmp_path):
    book, _ = prepared(tmp_path)
    (tmp_path/'book.json').write_text(json.dumps(book))
    rows = [[f'p{n}', 'p', 'a', 1, 'caption', '', 'normal', '<strong>HO</strong>ME', 'The sign &amp; memory.'] for n in [1, 2]]
    path = tmp_path/'script.html'; path.write_text(table(rows))
    return book, rows, path


def test_nested_emphasis_unicode_and_entities_have_exact_offsets():
    row = ['p1', 'p', 'a', 1, 'speech', 'girl', 'normal', '她<strong>说<em>好🙂</em></strong> &amp; 完。', '动作，不是台词。']
    item = parse_script(table([row]))[0]
    assert item['text'] == '她说好🙂 & 完。'
    assert item['emphasis'] == [{'start': 1, 'end': 2, 'font_role': 'bold'}, {'start': 2, 'end': 4, 'font_role': 'bold_italic'}]
    assert item['note'] == row[-1]


@pytest.mark.parametrize('bad', ['missing', 'duplicate', 'extra', 'speaker', 'kind', 'voice', 'text', 'empty_frozen'])
def test_bad_handoff_is_rejected_without_writing_outputs(tmp_path, bad):
    book, rows, path = fixture(tmp_path)
    if bad == 'missing': rows.pop()
    elif bad == 'duplicate': rows.append(copy.deepcopy(rows[0]))
    elif bad == 'extra': rows.append(['extra', 'p', 'a', 1, 'caption', '', 'normal', 'HOME', ''])
    elif bad in ('speaker', 'kind', 'voice'): rows[0][COLUMNS.index(bad)] = 'wrong'
    elif bad == 'text': rows[0][7] = 'HOM'
    else:
        page=json.loads((tmp_path/'p1.json').read_text());page['items'][0]['expected_text']=''
        (tmp_path/'p1.json').write_text(json.dumps(page))
    path.write_text(table(rows));before={p.name:p.read_bytes() for p in tmp_path.iterdir()}
    with pytest.raises(ValueError): import_script(path, tmp_path/'book.json', tmp_path/'out')
    assert before == {p.name:p.read_bytes() for p in tmp_path.iterdir()}


@pytest.mark.parametrize('markup', ['<span style="font-weight:bold">HOME</span>', 'HO<br>ME', '<strong>HOME', '<a href="https://example.com">HOME</a>'])
def test_unsupported_or_unbalanced_formatting_is_not_silently_lost(markup):
    with pytest.raises(ValueError): parse_script(table([['p1', 'p', 'a', 1, 'caption', '', 'normal', markup, '']]))


def test_complete_import_preserves_geometry_words_notes_and_rules(tmp_path):
    book, rows, path = fixture(tmp_path)
    originals = {p.name:p.read_bytes() for p in tmp_path.iterdir()}
    result = import_script(path, tmp_path/'book.json', tmp_path/'out')
    assert result['ok'] and result['source_files_unchanged'] and not result['rendered']
    assert result['required_emphasis_roles'] == ['bold']
    assert result['items'][0]['note'] == 'The sign & memory.'
    old = json.loads((tmp_path/'p1.json').read_text()); new = json.loads((tmp_path/'out/pages/p1.json').read_text())
    assert new['items'][0].pop('emphasis') == [{'start':0,'end':2,'font_role':'bold'}]
    assert new == old
    assert json.loads((tmp_path/'out/book.json').read_text())['rules'] == book['rules']
    assert originals == {name:(tmp_path/name).read_bytes() for name in originals}
    assert (tmp_path/'out/manuscript-source.txt').read_bytes() == path.read_bytes()
    assert '<strong>HO</strong>ME' in (tmp_path/'out/index.html').read_text()
    with pytest.raises(ValueError, match='already exists'): import_script(path, tmp_path/'book.json', tmp_path/'out')


def test_existing_complex_emphasis_is_not_overwritten(tmp_path):
    _, _, path = fixture(tmp_path)
    page=json.loads((tmp_path/'p1.json').read_text());page['items'][0]['emphasis']=[{'start':0,'end':2,'scale':1.2}]
    (tmp_path/'p1.json').write_text(json.dumps(page))
    with pytest.raises(ValueError, match='existing emphasis'): import_script(path, tmp_path/'book.json', tmp_path/'out')


def test_explicit_empty_unfrozen_slot_can_receive_script_and_cli_works(tmp_path, capsys):
    _, _, path = fixture(tmp_path)
    page=json.loads((tmp_path/'p1.json').read_text());page['items'][0].pop('expected_text');page['items'][0]['text']=''
    (tmp_path/'p1.json').write_text(json.dumps(page))
    assert main(['script-import',str(path),'--book',str(tmp_path/'book.json'),'--out',str(tmp_path/'out'),'--strict'])==0
    assert json.loads(capsys.readouterr().out)['items'][0]['text']=='HOME'
