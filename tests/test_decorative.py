import copy
import math
import re
import xml.etree.ElementTree as ET
import pytest
from comic_letterer.engine import compile_page
from comic_letterer.decorative import toothed_path, prepare_decoration


@pytest.fixture
def job():
    return {'version':1,'width':1000,'height':800,
            'panels':[{'id':'p','box':[0,0,1000,800]}],
            'items':[{'id':'a','panel':'p','order':1,'kind':'speech','speaker':'robot',
                      'text':'Wait! The little light is still inside.',
                      'expected_text':'Wait! The little light is still inside.',
                      'box':[60,60,600,260],'font_size':28,'target':[800,500]}]}


@pytest.mark.parametrize('shape',['mechanical','sawtooth','flame'])
def test_real_contours_and_unchanged_words(job,shape):
    job['items'][0]['shape']=shape;original=copy.deepcopy(job)
    svg,r=compile_page(job);assert r['ok'] and job==original
    root=ET.fromstring(svg)
    assert ''.join(root.find(".//*[@id='text-a']").itertext())==job['items'][0]['text']
    d=root.find(".//*[@id='fill-a']").get('d')
    if shape=='mechanical':
        assert root.find(".//*[@id='mechanical-broken-a']").get('stroke-dasharray')
        widths=[float(root.find(f".//*[@id='{name}-a']").get('stroke-width'))
                for name in ('outline','mechanical-broken','mechanical-inner')]
        assert widths[0]>widths[1]>widths[2]
    else:
        assert ('C' in d)==(shape=='flame')
        assert r['items'][0]['decoration']['teeth']>20


def test_teeth_follow_arc_length_and_stay_within_bounds():
    for shape in ['sawtooth','flame']:
        counts=[]
        for factor in [1,2,3]:
            box=[20,30,240*factor,120*factor]
            d,n,spacing=toothed_path(box,shape,{'spacing':24,'depth':9})
            assert abs(spacing-24)<1
            counts.append(n)
            for x,y in re.findall(r'([\d.]+),([\d.]+)',d):
                assert 20<=float(x)<=box[0]+box[2] and 30<=float(y)<=box[1]+box[3]
        assert counts[1]==pytest.approx(counts[0]*2,abs=1)
        assert counts[2]==pytest.approx(counts[0]*3,abs=1)


def test_scroll_reserves_curls_and_dropcap_wraps(job):
    item=job['items'][0]
    item.update(kind='caption',shape='scroll',box=[40,40,500,360],font_size=25,align='left',
                text='Once the lamp went dark, the keeper heard a tiny voice. She opened the hood and carried the light home again.',
                drop_cap={'lines':2,'color':'#71381B'})
    item['expected_text']=item['text']
    svg,r=compile_page(job);assert r['ok']
    report=r['items'][0];cap=report['drop_cap'];assert cap['font_size']>25
    root=ET.fromstring(svg);nodes=list(root.find(".//*[@id='text-a']"))
    assert ''.join(n.text for n in nodes)==item['text']
    assert nodes[0].text=='O'
    # First two body rows clear the initial; subsequent row returns to full width.
    by_y={}
    for n in nodes[1:]:by_y.setdefault(float(n.get('y')),float(n.get('x')))
    xs=list(by_y.values());assert len(xs)>=3 and xs[0]==xs[1] and xs[2]<xs[1]
    assert root.find(".//*[@id='scroll-fold-a-0']") is not None
    safe=report['decoration']['text_box']
    for x,y,w,h in report['glyph_boxes']:
        assert safe[0]<=x and x+w<=safe[0]+safe[2]
        assert safe[1]<=y and y+h<=safe[1]+safe[3]


def test_dropcap_explicit_breaks_and_combining_mark(job):
    item=job['items'][0]
    item.update(kind='caption',align='left',text='A\u0301 star fell. It waited.',expected_text='A\u0301 star fell. It waited.',drop_cap={},breaks=[13])
    svg,r=compile_page(job)
    nodes=list(ET.fromstring(svg).find(".//*[@id='text-a']"))
    assert nodes[0].text=='A\u0301' and ''.join(n.text for n in nodes)==item['text']
    assert r['items'][0]['lines']==[item['text'][:13],item['text'][13:]]


@pytest.mark.parametrize('change',[
    {'shape':'scroll'}, {'shape':'mechanical','mechanical':{'band':100}},
    {'shape':'mechanical','mechanical':{'dash':0}}, {'shape':'mechanical','mechanical':{'notch':1}},
    {'shape':'sawtooth','edge':{'spacing':2}}, {'shape':'flame','edge':{'depth':100}},
    {'shape':'flame','voice':'rough'}, {'shape':'flame','double_outline':4},
    {'edge':{'depth':8}}, {'shape':'flame','edge':False}, {'drop_cap':{}},
    {'kind':'caption','drop_cap':{'lines':1}}, {'kind':'caption','drop_cap':{'count':True}},
    {'kind':'caption','drop_cap':{},'align':'center'},
    {'kind':'caption','drop_cap':{'font_role':'unknown'}},
    {'kind':'caption','shape':'scroll','scroll':{'curl':200}},
])
def test_reject_invalid_or_conflicting_options(job,change):
    job['items'][0].update(change)
    with pytest.raises(ValueError):compile_page(job)


def test_small_caption_overflow_is_not_hidden(job):
    job['items'][0].update(kind='caption',shape='scroll',drop_cap={},box=[30,30,600,75],font_size=28)
    _,r=compile_page(job)
    assert any(i['code']=='text_overflow' for i in r['issues'])


def test_style_options_can_be_disabled_without_rewriting(job):
    job['styles']={'n':{'kind':'caption','shape':'scroll','scroll':{'curl':12},'drop_cap':{'lines':2},'align':'left'}}
    item=job['items'][0];item.pop('kind');item.update(style='n',drop_cap=None,shape=None,scroll=None)
    _,r=compile_page(job);assert r['items'][0]['drop_cap'] is None
