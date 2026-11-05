import copy
import json
import pytest
from comic_letterer.book import audit_book
from comic_letterer.cli import main


@pytest.fixture
def fixture(tmp_path):
    page={'version':1,'width':1000,'reading_width':500,'styles':{'body':{'kind':'speech','font_size':24}},
          'items':[{'id':'a','style':'body','text':'Stay.','expected_text':'Stay.','speaker':'A'}]}
    (tmp_path/'page.json').write_text(json.dumps(page))
    book={'version':1,'pages':[{'id':'p','path':'page.json'}],
          'rules':[{'id':'body','match':{'kind':'speech'},'expect':{'font_size':24,'reading_font_size':12,'font_role':'body'}}]}
    return tmp_path,page,book


def test_inheritance_defaults_and_read_only(fixture):
    root,page,book=fixture;before=(root/'page.json').read_bytes();original=copy.deepcopy(book)
    r=audit_book(book,root)
    assert r['ok'] and r['issues']==[] and r['rule_matches']['body']==1
    assert book==original and (root/'page.json').read_bytes()==before


def test_actual_override_and_exact_exception(fixture):
    root,page,book=fixture;page['items'][0]['font_size']=26
    (root/'page.json').write_text(json.dumps(page))
    r=audit_book(book,root);assert not r['ok'] and len(r['issues'])==2
    book['exceptions']=[{'page':'p','item':'a','rule':'body','field':'font_size','value':26,'reason':'An intentional louder voice.'},
                        {'page':'p','item':'a','rule':'body','field':'reading_font_size','value':13,'reason':'Same documented exception.'}]
    r=audit_book(book,root);assert r['ok'] and len(r['recorded_exceptions'])==2
    page['items'][0]['font_size']=28;(root/'page.json').write_text(json.dumps(page))
    r=audit_book(book,root);assert not r['ok'] and any(i['code']=='stale_exception' for i in r['issues'])


def test_no_match_warns_and_frozen_text_is_checked(fixture):
    root,page,book=fixture;book['rules'][0]['match']={'speaker':'missing'}
    page['items'][0]['text']='Changed.';(root/'page.json').write_text(json.dumps(page))
    r=audit_book(book,root)
    assert {i['code'] for i in r['issues']}=={'unmatched_rule','frozen_text_mismatch'}


@pytest.mark.parametrize('change',['unknown','duplicate','no_reason'])
def test_malformed_rules_are_not_silently_ignored(fixture,change):
    root,page,book=fixture
    if change=='unknown':book['rules'][0]['expect']={'font_sze':24}
    elif change=='duplicate':book['pages'].append(book['pages'][0])
    else:book['exceptions']=[{'page':'p','item':'a','rule':'body','field':'font_size','value':25,'reason':''}]
    with pytest.raises(ValueError):audit_book(book,root)


def test_cli_strict_and_no_output_files(fixture,capsys):
    root,page,book=fixture;path=root/'book.json';path.write_text(json.dumps(book))
    before=set(root.iterdir());assert main(['book-check',str(path),'--strict'])==0
    assert json.loads(capsys.readouterr().out)['ok']
    book['rules'][0]['match']={'speaker':'missing'};path.write_text(json.dumps(book))
    assert main(['book-check',str(path),'--strict'])==1 and set(root.iterdir())==before


def test_decorative_defaults_follow_renderer(fixture):
    root,page,book=fixture
    page['items'][0].update(shape='flame',box=[20,20,300,100])
    book['rules'][0]['expect'].update({'edge.spacing':24,'edge.depth':8})
    (root/'page.json').write_text(json.dumps(page))
    assert audit_book(book,root)['issues']==[]
