"""Bounded optional ink treatments; source text remains unchanged."""
import random
from .validation import fields, color, number, vector


def validate(item):
    material=item.get('material')
    if material is not None:
        fields(material,'gradient wear seed','material')
        if item['kind'] not in ('sfx','floating'):raise ValueError('ink material requires SFX or floating text')
        if item.get('shadow') or item.get('hollow'):raise ValueError('material cannot combine shadow/hollow')
        if 'gradient' in material:
            g=material['gradient']
            if not isinstance(g,list) or len(g)!=2:raise ValueError('gradient needs two colors')
            for c in g:color(c)
        wear=number(material.get('wear',0),'wear')
        if not 0<=wear<=.12:raise ValueError('wear must be 0..0.12')
        if type(material.get('seed',0)) is not int:raise ValueError('material seed must be an integer')
    sound=item.get('sound')
    if sound is not None:
        fields(sound,'event source material intensity duration direction','sound')
        if item['kind']!='sfx':raise ValueError('sound design metadata requires SFX')
        for k in ('event','material','duration'):
            if not isinstance(sound.get(k),str) or not sound[k].strip():raise ValueError('sound needs event/material/duration')
        vector(sound.get('source'),2,'sound source')
        if sound.get('intensity') not in ('quiet','moderate','loud'):raise ValueError('sound intensity must be quiet/moderate/loud')
        if 'direction' in sound:vector(sound['direction'],2,'sound direction')


def apply(item,node,group,defs,elem,boxes):
    spec=item.get('material')
    if not spec:return
    iid=item['id']
    if 'gradient' in spec:
        grad=elem('linearGradient',{'id':f'ink-gradient-{iid}','x1':'0%','y1':'0%','x2':'100%','y2':'100%'},defs)
        for offset,c in zip(('0%','100%'),spec['gradient']):elem('stop',{'offset':offset,'stop-color':c},grad)
        node.set('fill',f'url(#ink-gradient-{iid})')
    wear=spec.get('wear',0)
    if wear and boxes:
        rng=random.Random(spec.get('seed',0));mask=elem('mask',{'id':f'ink-wear-{iid}','maskUnits':'userSpaceOnUse','x':-10000,'y':-10000,'width':20000,'height':20000},defs)
        elem('rect',{'x':-10000,'y':-10000,'width':20000,'height':20000,'fill':'white'},mask)
        for x,y,w,h in boxes:
            # Small deterministic chips; density is intentionally limited.
            count=min(200,max(1,int(w*h*wear/6)))
            for _ in range(count):
                elem('ellipse',{'cx':x+rng.random()*w,'cy':y+rng.random()*h,'rx':.4+rng.random()*1.2,'ry':.3+rng.random()*.5,'fill':'black'},mask)
        group.set('mask',f'url(#ink-wear-{iid})')
