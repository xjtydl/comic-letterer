"""Read-only book style audit. Explicit house rules, no inferred rewriting."""
import json
from pathlib import Path
from .narrative import resolve_item
from .decorative import prepare_decoration
from .validation import fields, ident, number
from .balloon_finish import DEFAULTS as APPEARANCE_DEFAULTS, resolve as resolve_appearance

MATCH = 'speaker kind style voice caption_type edition language'
EXPECT = set(('font_size font_role fill stroke text_color stroke_width shape voice caption_type features language '
              'line_height padding tracking horizontal_scale reading_font_size '
              'tail.width tail.gap baseline.mode baseline.amplitude '
              'edge.spacing edge.depth mechanical.band mechanical.dash mechanical.gap mechanical.notch '
              'scroll.curl drop_cap.lines drop_cap.font_role').split())
EXPECT.update('appearance.' + k for k in APPEARANCE_DEFAULTS)
EXPECT.add('appearance')


def value(item, page, key):
    fs=item.get('font_size',28)
    defaults={'font_size':28,'font_role':'body','stroke_width':2,'shape':None,'voice':'normal',
              'caption_type':None,'line_height':1.25,'padding':fs*.6,'tracking':0,
              'horizontal_scale':1,'stroke':'#20202A','text_color':'#20202A',
              'fill':'#FFF4D8' if item.get('kind')=='caption' else '#FFFFFF',
              'baseline.mode':'straight','tail.gap':0,'features':{},'language':None}
    if key=='reading_font_size':
        width=number(page['width'],'page width',True)
        return number(fs,'font size',True)*number(page.get('reading_width',width),'reading_width',True)/width
    prefix, _, leaf = key.partition('.')
    if prefix == 'appearance':
        spec = resolve_appearance(item)
        return spec if not leaf else spec.get(leaf)
    if prefix in ('edge','mechanical','scroll') and item.get('box'):
        decoration = prepare_decoration(item, item['box'])
        if decoration and leaf in decoration['spec']:
            return decoration['spec'][leaf]
    if prefix == 'drop_cap' and item.get('drop_cap') is not None:
        return item['drop_cap'].get(leaf, 2 if leaf == 'lines' else item.get('font_role','body'))
    if key == 'baseline.amplitude':
        return item.get('baseline',{}).get('amplitude',fs*.08)
    if key == 'tail.width' and item.get('box'):
        return item.get('tail',{}).get('width',min(item['box'][2:])*.13)
    result=item
    for part in key.split('.'):
        if not isinstance(result,dict) or part not in result:return defaults.get(key)
        result=result[part]
    return result


def audit_book(book, base_dir):
    fields(book,'version pages rules exceptions','book')
    if type(book.get('version')) is not int or book['version']!=1:raise ValueError('book version must be 1')
    for key in ('pages','rules','exceptions'):
        if not isinstance(book.get(key,[]),list):raise ValueError(key+' must be an array')
    if not book.get('pages') or not book.get('rules'):raise ValueError('book needs pages and rules')
    rules={};hits={}
    for rule in book['rules']:
        fields(rule,'id match expect','book rule');rid=ident(rule.get('id'))
        if rid in rules:raise ValueError('duplicate book rule')
        fields(rule.get('match',{}),MATCH,'rule match')
        expect=rule.get('expect')
        if not isinstance(expect,dict) or not expect or set(expect)-EXPECT:raise ValueError('unknown or empty rule expectation')
        rules[rid]=rule;hits[rid]=0
    exceptions={}
    for exc in book.get('exceptions',[]):
        fields(exc,'page item rule field value reason','book exception')
        if not isinstance(exc.get('reason'),str) or not exc['reason'].strip() or 'value' not in exc:
            raise ValueError('exception needs an exact value and reason')
        key=(ident(exc.get('page')),ident(exc.get('item')),ident(exc.get('rule')),exc.get('field'))
        if key[2] not in rules or key[3] not in rules[key[2]]['expect'] or key in exceptions:
            raise ValueError('unknown or duplicate exception target')
        exceptions[key]=exc
    seen=set();issues=[];recorded=[];used=set();pages=[]
    for entry in book['pages']:
        fields(entry,'id path edition','book page');pid=ident(entry.get('id'))
        if pid in seen:raise ValueError('duplicate book page id')
        seen.add(pid)
        if not isinstance(entry.get('path'),str) or not entry['path']:raise ValueError('page path required')
        page=json.loads((Path(base_dir)/entry['path']).read_text(encoding='utf-8'))
        if page.get('version')!=1 or not isinstance(page.get('items'),list):raise ValueError('invalid page document')
        items=set();checked=0
        for raw in page['items']:
            item=resolve_item(raw,page.get('styles',{}));iid=ident(item.get('id'))
            if iid in items:raise ValueError('duplicate item id in book page')
            items.add(iid)
            if 'expected_text' in item and item.get('text')!=item['expected_text']:
                issues.append({'page':pid,'item':iid,'code':'frozen_text_mismatch','severity':'error'})
            selector={**item,'voice':item.get('voice','normal'),'edition':entry.get('edition')}
            for rid,rule in rules.items():
                if any(selector.get(k)!=v for k,v in rule.get('match',{}).items()):continue
                hits[rid]+=1;checked+=1
                for field,expected in rule['expect'].items():
                    actual=value(item,page,field)
                    equal=(abs(actual-expected)<1e-6 if type(actual) in (int,float) and type(expected) in (int,float) else actual==expected)
                    if equal:continue
                    issue={'page':pid,'item':iid,'rule':rid,'field':field,'expected':expected,'actual':actual,'code':'style_drift','severity':'error'}
                    key=(pid,iid,rid,field);exc=exceptions.get(key)
                    if exc is not None and actual==exc['value']:
                        used.add(key);recorded.append({**issue,'severity':'recorded_exception','reason':exc['reason']})
                    else:issues.append(issue)
        pages.append({'id':pid,'path':entry['path'],'items':len(items),'rule_matches':checked})
    for rid,n in hits.items():
        if not n:issues.append({'rule':rid,'code':'unmatched_rule','severity':'warning'})
    for key in exceptions.keys()-used:
        issues.append({'page':key[0],'item':key[1],'rule':key[2],'field':key[3],'code':'stale_exception','severity':'warning'})
    return {'version':1,'ok':not any(i['severity']=='error' for i in issues),'pages':pages,
            'rule_matches':hits,'issues':issues,'recorded_exceptions':recorded,
            'scope':'Explicit metadata rules only; not a layout, font, drawing or narrative acceptance check.'}
