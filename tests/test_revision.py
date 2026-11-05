import copy
import hashlib
import json
import os
from pathlib import Path
import pytest

from comic_letterer.revision import book_digest, prepare_revision, revise_book
from test_proof import prepared


def setup(tmp_path):
    book, assets = prepared(tmp_path)
    plan = {'version': 1, 'title': 'Reading revision', 'book_sha256': book_digest(book),
            'page_sha256': {p['id']: hashlib.sha256((tmp_path/p['path']).read_bytes()).hexdigest() for p in book['pages']},
            'changes': [{'page': 'p1', 'item': 'a', 'field': 'font_size', 'before': 28, 'after': 32, 'reason': 'Reading size'}]}
    return book, assets, plan


def test_appearance_revision_retains_inherited_material_and_guards_old_value(tmp_path):
    book, assets, plan = setup(tmp_path)
    page = json.loads((tmp_path/'p1.json').read_text())
    page['styles'] = {'paper': {'appearance': {'paper': .1, 'seed': 37}}}
    page['items'][0]['style'] = 'paper'
    (tmp_path/'p1.json').write_text(json.dumps(page))
    plan['page_sha256']['p1'] = hashlib.sha256((tmp_path/'p1.json').read_bytes()).hexdigest()
    plan['changes'][0].update(field='appearance.paper', before=.1, after=.16)
    original, pages, _, _, _ = prepare_revision(book, tmp_path, plan)
    assert pages['p1']['items'][0]['appearance'] == {'paper': .16, 'seed': 37}
    assert original['p1'] == page
    plan['changes'][0]['before'] = .2
    with pytest.raises(ValueError):
        prepare_revision(book, tmp_path, plan)


@pytest.mark.parametrize('failure', ['stale_page', 'stale_book', 'old_value', 'text', 'duplicate', 'reason', 'unknown_item'])
def test_revision_guards_inputs_before_output(tmp_path, failure):
    book, assets, plan = setup(tmp_path)
    change = plan['changes'][0]
    if failure == 'stale_page': (tmp_path/'p1.json').write_text('{}')
    elif failure == 'stale_book': book['rules'][0]['expect']['font_size'] = 32
    elif failure == 'old_value': change['before'] = 27
    elif failure == 'text': change.update(field='text', before='HOME', after='HOM')
    elif failure == 'duplicate': plan['changes'].append(copy.deepcopy(change))
    elif failure == 'reason': change['reason'] = ''
    else: change['item'] = 'unknown'
    before = {p.name: p.read_bytes() for p in tmp_path.iterdir()}
    with pytest.raises(ValueError): revise_book(book, tmp_path, plan, assets, tmp_path, tmp_path/'out')
    assert before == {p.name: p.read_bytes() for p in tmp_path.iterdir()}


def test_inherited_nested_override_retains_siblings_and_other_items(tmp_path):
    book, assets, plan = setup(tmp_path)
    page = json.loads((tmp_path/'p1.json').read_text())
    page['styles'] = {'wave': {'baseline': {'mode': 'wave', 'amplitude': 2, 'group': 2}}}
    page['items'][0]['style'] = 'wave'
    page['items'].append({**page['items'][0], 'id': 'b'})
    (tmp_path/'p1.json').write_text(json.dumps(page))
    plan['page_sha256']['p1'] = hashlib.sha256((tmp_path/'p1.json').read_bytes()).hexdigest()
    plan['changes'][0].update(field='baseline.amplitude', before=2, after=3)
    original, pages, revised, _, _ = prepare_revision(book, tmp_path, plan)
    assert pages['p1']['items'][0]['baseline'] == {'mode': 'wave', 'amplitude': 3, 'group': 2}
    assert pages['p1']['items'][1] == original['p1']['items'][1]
    assert original['p1'] == page and revised == book


@pytest.mark.skipif(os.environ.get('COMIC_LETTERER_RENDER_TEST') != '1', reason='optional browser integration')
def test_real_revision_renders_and_preserves_exact_exception(tmp_path):
    book, assets, plan = setup(tmp_path)
    book['exceptions'] = [{'page': 'p1', 'item': 'a', 'rule': 'body', 'field': 'font_size', 'value': 32, 'reason': 'Opening emphasis'}]
    page = json.loads((tmp_path/'p1.json').read_text())
    page['items'][0]['font_size'] = 32
    (tmp_path/'p1.json').write_text(json.dumps(page))
    plan['page_sha256']['p1'] = hashlib.sha256((tmp_path/'p1.json').read_bytes()).hexdigest()
    plan['changes'][0].update(page='p2', after=30)
    plan['rule_changes'] = [{'rule': 'body', 'field': 'font_size', 'before': 28, 'after': 30, 'reason': 'New body size; retain opening emphasis'}]
    plan['book_sha256'] = book_digest(book)
    originals = {p.name: p.read_bytes() for p in tmp_path.iterdir()}
    result = revise_book(book, tmp_path, plan, assets, tmp_path, tmp_path/'out')
    assert result['ok'] and result['text_preserved'] and result['source_files_unchanged']
    assert len(result['recorded_exceptions']) == 1 and result['user_acceptance'] == 'not_recorded'
    assert all((tmp_path/'out'/side/'p1/reading.png').stat().st_size > 1000 for side in ('before', 'after'))
    assert (tmp_path/'out/before/p1/reading.png').read_bytes() == (tmp_path/'out/after/p1/reading.png').read_bytes()
    assert (tmp_path/'out/before/p2/reading.png').read_bytes() != (tmp_path/'out/after/p2/reading.png').read_bytes()
    assert originals == {name: (tmp_path/name).read_bytes() for name in originals}
    with pytest.raises(ValueError, match='already exists'):
        revise_book(book, tmp_path, plan, assets, tmp_path, tmp_path/'out')


@pytest.mark.skipif(os.environ.get('COMIC_LETTERER_RENDER_TEST') != '1', reason='optional browser integration')
def test_rule_drift_is_not_silently_fixed_and_rule_changes_are_explicit(tmp_path):
    book, assets, plan = setup(tmp_path)
    bad = revise_book(book, tmp_path, plan, assets, tmp_path, tmp_path/'diagnostic')
    assert not bad['ok'] and any(i['code'] == 'style_drift' for i in bad['issues'])
    plan['changes'].append({**plan['changes'][0], 'page': 'p2'})
    plan['rule_changes'] = [{'rule': 'body', 'field': 'font_size', 'before': 28, 'after': 32, 'reason': 'New reading edition'}]
    good = revise_book(book, tmp_path, plan, assets, tmp_path, tmp_path/'revised')
    assert good['ok']
    revised = json.loads((tmp_path/'revised/book.json').read_text())
    assert revised['rules'][0]['expect']['font_size'] == 32


@pytest.mark.skipif(os.environ.get('COMIC_LETTERER_RENDER_TEST') != '1', reason='optional browser integration')
def test_invalid_render_cleans_staging_directory(tmp_path):
    book, assets, plan = setup(tmp_path)
    plan['changes'][0]['after'] = -1
    with pytest.raises(ValueError): revise_book(book, tmp_path, plan, assets, tmp_path, tmp_path/'out')
    assert not (tmp_path/'out').exists() and not list(tmp_path.glob('.revision-*'))
