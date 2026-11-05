import copy
import json
import os
from pathlib import Path
from xml.etree import ElementTree as ET
import pytest
from PIL import ImageFont
from fontTools.ttLib import TTFont
from comic_letterer.engine import compile_page
from comic_letterer.custom_path import prepare_path, ray_boundary, box_inside
from comic_letterer.surface import projection
from comic_letterer.letterforms import build_font, stroke_outline
from comic_letterer.type_options import language_advice


@pytest.fixture
def job():
    return {'version':1,'width':800,'height':600,'panels':[{'id':'p','box':[0,0,800,600]}],
            'items':[{'id':'a','panel':'p','kind':'speech','speaker':'A','order':1,'font_size':24,
                      'text':'Please wait. I remember the final song.',
                      'expected_text':'Please wait. I remember the final song.',
                      'box':[40,30,430,230],'target':[650,440]}]}


@pytest.fixture
def font(tmp_path):
    source=json.loads(Path('examples/last-ticket-hand.json').read_text())
    path=tmp_path/'original.ttf';build_font(source,path)
    return str(path)


def test_font_strokes_kerning_alternate_and_roundtrip(font):
    with TTFont(font) as f:
        assert set('HOMEh') <= {chr(n) for n in f.getBestCmap()}
        assert 'GSUB' in f and 'GPOS' in f
    face=ImageFont.truetype(font,100)
    assert face.getlength('HOME',features=['kern=1']) < face.getlength('HOME',features=['kern=0'])
    assert bytes(face.getmask('HOME',features=['ss01=1'])) != bytes(face.getmask('HOME',features=['ss01=0']))


def test_opentype_changes_measured_advance_and_retains_source(job,font):
    a=job['items'][0];a.update(text='HOME',expected_text='HOME',features={'kern':1,'ss01':1})
    original=copy.deepcopy(job);svg,r=compile_page(job,font)
    assert r['ok'] and job==original
    node=ET.fromstring(svg).find(".//*[@id='text-a']")
    assert ''.join(node.itertext())=='HOME' and "'ss01' 1" in node.get('font-feature-settings')
    a['features']['kern']=0
    _,other=compile_page(job,font)
    assert r['items'][0]['glyph_boxes'][0][2]<other['items'][0]['glyph_boxes'][0][2]
    a['features']={'zzzz':1}
    with pytest.raises(ValueError,match='does not provide'):compile_page(job,font)


@pytest.mark.parametrize('value',[{'bad':1},{'kern':-1},{'kern':100},[],{'kern':'on'}])
def test_bad_features_rejected(job,value):
    job['items'][0]['features']=value
    with pytest.raises(ValueError):compile_page(job)


def test_rows_preserve_wording_and_scale_only_requested_line(job):
    a=job['items'][0];a.update(breaks=[13],line_scales=[.92,1.05],line_widths=[270,300],kind='caption',align='left')
    svg,r=compile_page(job)
    assert r['items'][0]['text_preserved']
    spans=list(ET.fromstring(svg).find(".//*[@id='text-a']"))
    assert all(s.get('lengthAdjust')=='spacingAndGlyphs' for s in spans)
    assert spans[0].get('x')!=spans[1].get('x')
    a['line_scales']=[.8]
    with pytest.raises(ValueError,match='line_scales'):compile_page(job)


def test_variable_row_wrapping_and_unused_rows(job):
    a=job['items'][0];a.update(line_widths=[100,280],kind='caption')
    _,r=compile_page(job)
    assert len(r['items'][0]['lines'][0])<len(r['items'][0]['lines'][1])
    a['line_widths']=[200]*100
    with pytest.raises(ValueError,match='actual line count'):compile_page(job)


def test_language_advice_is_language_specific_and_read_only():
    a={'text':'等等...我来了','language':'zh-CN'};before=copy.deepcopy(a)
    assert language_advice(a)['findings'][0]['code']=='zh_ellipsis' and a==before
    assert not language_advice({**a,'language':'en'})['findings']
    assert language_advice({'text':'i remember.','language':'en'})['findings'][0]['start']==0


def test_flat_contour_and_tail_use_same_boundary(job):
    a=job['items'][0];a.update(shape='flat',corner=.15)
    svg,r=compile_page(job);assert r['ok']
    poly=prepare_path(a,a['box'])['polygon']
    x,y=ray_boundary((255,145),(1,0),poly)
    assert x==pytest.approx(470) and y==pytest.approx(145)
    assert 'C' in ET.fromstring(svg).find(".//*[@id='fill-a']").get('d')


def test_custom_path_text_notch_and_bad_shapes(job):
    a=job['items'][0];a.update(shape='custom',contour={'start':[.5,0],'curves':[[1,0,1,1,.5,1],[0,1,0,0,.5,0]]})
    svg,r=compile_page(job);assert 'C' in svg and r['items'][0]['text_preserved']
    assert not box_inside([40,30,20,20],prepare_path(a,a['box'])['polygon'],2)
    a['contour']['curves'][0][0]=1.1
    with pytest.raises(ValueError,match='0..1'):compile_page(job)


def test_projective_corners_exact_and_invalid_quad():
    q=[[20,40],[400,10],[350,200],[10,260]];fn=projection(q)
    for uv,p in zip([(0,0),(1,0),(1,1),(0,1)],q):assert fn(*uv)==pytest.approx(p)
    with pytest.raises(ValueError):projection([q[0],q[2],q[1],q[3]])


def test_surface_exact_text_paths_bounds_and_material(job,font):
    a=job['items'][0];a.update(kind='floating',text='HOME',expected_text='HOME',surface=[[70,50],[450,30],[430,220],[50,250]],material={'gradient':['#FFFFFF','#AA8844'],'wear':.03,'seed':7})
    svg,r=compile_page(job,font);assert r['ok']
    root=ET.fromstring(svg);assert root.find(".//*[@id='projected-a']") is not None
    assert ''.join(root.find(".//*[@id='text-a']").itertext())=='HOME'
    assert root.find(".//*[@id='text-a']").get('display')=='none'
    assert root.find(".//*[@id='ink-wear-a']") is not None
    assert compile_page(job,font)[0]==svg
    job['protected']=[{'id':'sign','box':[50,30,400,220]}]
    assert any(i['code']=='surface_protected_overlap' for i in compile_page(job,font)[1]['issues'])


@pytest.mark.parametrize('patch',[{'material':{'wear':.9}},{'corner':.9,'shape':'flat'},{'surface':[[0,0]]},{'language':'en";bad'},{'sound':{'intensity':'loud'}}])
def test_new_options_reject_invalid_input(job,patch):
    job['items'][0].update(patch)
    with pytest.raises(ValueError):compile_page(job)


def test_strokes_pressure_affects_outline_and_rejects_turnback():
    narrow=stroke_outline({'points':[[0,0,.5],[0,500,.5]],'width':50})
    broad=stroke_outline({'points':[[0,0,1.5],[0,500,1.5]],'width':50})
    assert abs(broad[0][0])==3*abs(narrow[0][0])
    with pytest.raises(ValueError):stroke_outline({'points':[[0,0],[0,500],[0,0]]})

@pytest.mark.parametrize('voice',['breath','telepathic','singing'])
def test_voice_marks_stay_visible_inside_shell_and_avoid_words(job,voice):
    a=job['items'][0];a.update(text='Wait.',expected_text='Wait.',voice=voice)
    other=copy.deepcopy(a);other.update(id='b',order=2,voice='normal',box=[40,350,430,170],target=[650,550])
    job['items'].append(other)  # Catch variable/layer state leaking between items.
    svg,r=compile_page(job)
    assert r['ok'],r['issues']
    marks=r['items'][0]['voice_mark_boxes'];assert len(marks)==(1 if voice=='singing' else 2)
    assert r['items'][1]['voice_mark_boxes']==[]
    assert ET.fromstring(svg).find(".//*[@id='voice-mark-a-0']") is not None


@pytest.mark.skipif(os.environ.get('COMIC_LETTERER_RENDER_TEST')!='1',reason='optional browser integration')
def test_projected_source_font_is_not_required_by_raster(job,font,tmp_path):
    from comic_letterer.render import render_png,font_css
    a=job['items'][0];a.update(kind='floating',text='HOME',expected_text='HOME',surface=[[50,50],[450,40],[440,230],[40,240]])
    svg,r=compile_page(job,font)
    assert '@font-face' not in font_css(svg,{'body':{'path':font}})
    render_png(svg,tmp_path/'surface.png',800,font)
    assert (tmp_path/'surface.png').stat().st_size>1000


def test_explicit_stack_keeps_independent_shells_and_rejects_hidden_words(job):
    a=job['items'][0];a.update(text='Wait.',expected_text='Wait.',box=[40,30,300,160])
    b=copy.deepcopy(a);b.update(id='b',order=2,kind='whisper',text='Quiet.',expected_text='Quiet.',box=[300,170,220,140],target=[680,490],overlap_with=['a'])
    job['items'].append(b)
    svg,r=compile_page(job)
    assert not any(i['code']=='item_overlap' for i in r['issues'])
    root=ET.fromstring(svg);stack=root.find(".//*[@id='intentional-stacks']")
    assert [n.get('id') for n in stack]==['stack-a','stack-b']
    b['box']=[150,70,220,140]
    assert any(i['code']=='join_text_overlap' for i in compile_page(job)[1]['issues'])


def test_cross_border_is_explicit_and_does_not_allow_words_outside_panel(job):
    job['panels'][0]['box']=[100,100,600,400]
    a=job['items'][0];a.update(kind='caption',text='Wait.',expected_text='Wait.',box=[80,130,400,100],cross_border=['left'])
    _,r=compile_page(job);assert r['ok']
    a.pop('cross_border');assert not compile_page(job)[1]['ok']
    a['cross_border']=['left'];a['box']=[80,130,35,100]
    assert any(i['code']=='text_overflow' for i in compile_page(job)[1]['issues'])
