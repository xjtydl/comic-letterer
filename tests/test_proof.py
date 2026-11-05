import copy
import hashlib
import json
import os
from pathlib import Path
import pytest
from PIL import Image
from comic_letterer.letterforms import build_font
from comic_letterer.proof import proof_book


def prepared(tmp_path):
    source=json.loads(Path('examples/last-ticket-hand.json').read_text())
    build_font(source,tmp_path/'a.ttf');source['glyphs']['H']['advance']=750;build_font(source,tmp_path/'b.ttf')
    Image.new('RGB',(800,600),'#dae3e5').save(tmp_path/'art.png')
    page={'version':1,'width':800,'height':600,'reading_width':600,'panels':[{'id':'p','box':[0,0,800,600]}],
          'items':[{'id':'a','panel':'p','kind':'caption','order':1,'text':'HOME','expected_text':'HOME','font_size':28,'box':[40,40,500,150]}]}
    for n in [1,2]:(tmp_path/f'p{n}.json').write_text(json.dumps(page))
    book={'version':1,'pages':[{'id':f'p{n}','path':f'p{n}.json','edition':'en'} for n in [1,2]],
          'rules':[{'id':'body','match':{'kind':'caption'},'expect':{'font_size':28,'features':{}}}]}
    assets={f'p{n}':{'font':'a.ttf','background':'art.png'} for n in [1,2]}
    return book,assets


@pytest.mark.skipif(os.environ.get('COMIC_LETTERER_RENDER_TEST')!='1',reason='optional browser integration')
def test_book_proof_real_renders_source_preservation_and_drift(tmp_path):
    book,assets=prepared(tmp_path);before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in tmp_path.glob('p*.json')}
    result=proof_book(book,tmp_path,assets,tmp_path,tmp_path/'clean')
    assert result['ok'] and result['source_files_unchanged']
    assert all((tmp_path/'clean'/f'p{n}'/'reading.png').stat().st_size>1000 for n in [1,2])
    assert (tmp_path/'clean/index.html').is_file()
    assert before=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in tmp_path.glob('p*.json')}
    with pytest.raises(ValueError,match='already exists'):proof_book(book,tmp_path,assets,tmp_path,tmp_path/'clean')
    assets['p2']['font']='b.ttf'
    page=json.loads((tmp_path/'p2.json').read_text());page['items'][0]['font_size']=30
    (tmp_path/'p2.json').write_text(json.dumps(page))
    bad=proof_book(book,tmp_path,assets,tmp_path,tmp_path/'bad')
    assert not bad['ok']
    assert {i['code'] for i in bad['issues']}=={'style_drift','font_identity_drift'}
    assert bad['source_files_unchanged']


def test_proof_requires_exact_asset_pages_and_matching_art(tmp_path):
    book,assets=prepared(tmp_path)
    with pytest.raises(ValueError,match='exactly match'):proof_book(book,tmp_path,{},tmp_path,tmp_path/'bad')
    Image.new('RGB',(20,20)).save(tmp_path/'art.png')
    with pytest.raises(ValueError,match='matching PNG'):proof_book(book,tmp_path,assets,tmp_path,tmp_path/'bad')
    assert not (tmp_path/'bad').exists()
