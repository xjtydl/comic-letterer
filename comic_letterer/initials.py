"""Measured dropped initials with real wraparound, retaining exact Unicode."""
import unicodedata
from PIL import ImageFont
from .validation import fields, number, color


def layout_initial(item, box, pad, lh, bank, styles, fonts, runs, measure, forbidden, legal_break):
    spec=item['drop_cap']
    fields(spec,'lines count font_role gap color','drop_cap')
    rows=spec.get('lines',2);count=spec.get('count',1)
    if type(rows) is not int or not 2<=rows<=4:
        raise ValueError('drop_cap lines must be an integer 2..4')
    if type(count) is not int or not 1<=count<=4:
        raise ValueError('drop_cap count must be an integer 1..4')
    if item['kind'] not in ('caption','floating'):
        raise ValueError('drop_cap requires caption or floating text')
    if item.get('align','left')!='left':
        raise ValueError('drop_cap requires left alignment')
    text=item['text'];end=count
    while end<len(text) and unicodedata.combining(text[end]):end+=1
    if end>=len(text) or any(c.isspace() for c in text[:end]) or not text[end:].strip():
        raise ValueError('drop_cap requires an initial followed by body text')
    if end in forbidden:
        raise ValueError('drop_cap splits a protected phrase')
    if any(s['start']<end for s in item.get('emphasis',[])):
        raise ValueError('drop_cap initial uses its own font/color, not emphasis')
    hints=item.get('breaks')
    if hints is not None and (
        not isinstance(hints,list) or any(type(i) is not int or not end<i<len(text) for i in hints)
        or hints!=sorted(set(hints)) or forbidden.intersection(hints)
    ):
        raise ValueError('drop_cap breaks must follow the initial and preserve phrases')
    role=spec.get('font_role',item.get('font_role','body'))
    if not isinstance(role,str) or role not in bank:
        raise ValueError('drop_cap font_role is not configured')
    ink=color(spec['color']) if 'color' in spec else None
    fs=item['font_size'];gap=number(spec.get('gap',fs*.3),'drop_cap gap')
    if not 0<=gap<=fs*2:raise ValueError('drop_cap gap must be 0..2 em')
    bodyruns=runs(end,len(text))
    top=min(r[5][1]+r[6] for r in bodyruns)
    bottom=max(r[5][3]+r[6] for r in bodyruns)
    shift_range=max(s[3] for s in styles[end:])-min(s[3] for s in styles[end:])
    step=max(s[0] for s in styles[end:])*lh+shift_range
    desired=bottom-top+(rows-1)*step
    initial=text[:end]
    def font(size):return ImageFont.truetype(bank[role]['path'],size,index=bank[role].get('index',0))
    lo,hi=1,1000
    while lo<hi:
        mid=(lo+hi+1)//2;bounds=font(mid).getbbox(initial,anchor='ls')
        if bounds[3]-bounds[1]<=desired:lo=mid
        else:hi=mid-1
    f=font(lo);l,t,r,b=f.getbbox(initial,anchor='ls');adv=f.getlength(initial)
    capwidth=max(adv,r)-min(0,l)
    capheight=b-t
    if capheight<=0:raise ValueError('drop_cap initial has no visible ink')
    reserved=capwidth+gap
    inner=box[2]-pad*2
    if inner-reserved<fs:
        raise ValueError('drop_cap leaves no room for body text; enlarge caption')
    forced=sorted(set((hints or [])+[i+1 for i,c in enumerate(text) if c=='\n']+[len(text)]))
    ranges=[];start=end
    while start<len(text):
        row=len(ranges);width=inner-(reserved if row<rows else 0)
        limit=next(i for i in forced if i>start)
        if hints is not None:
            stop=limit
        else:
            ends=[i for i in range(start+1,limit+1) if i not in forbidden and (i==limit or legal_break(text,i))]
            fitting=[i for i in ends if measure(start,i)<=width]
            stop=max(fitting) if fitting else ends[0]
        ranges.append((start,stop));start=stop
    height=max(capheight,bottom-top+(len(ranges)-1)*step)
    ytop=box[1]+(box[3]-height)/2
    left=box[0]+pad
    segments=[{'x':left-min(0,l),'y':ytop-t,'text':initial,'font_size':lo,'color':ink,
               'font_role':role,'family':bank[role]['family'],'advance':adv,'horizontal_scale':1}]
    glyphboxes=[[left,ytop,capwidth,capheight]]
    positions=[];lines=[]
    for row,(a,z) in enumerate(ranges):
        line=text[a:z];x=left+(reserved if row<rows else 0);y=ytop-top+row*step
        lines.append((initial if row==0 else '')+line)
        positions.append((left if row==0 else x,y,lines[-1]))
        for seg,size,ink,srole,advance,(l,t,r,b),shift in runs(a,z):
            segments.append({'x':x,'y':y+shift,'text':seg,'font_size':size,'color':ink,
                             'font_role':srole,'family':bank[srole]['family'],
                             'advance':advance,'horizontal_scale':item.get('horizontal_scale',1)})
            glyphboxes.append([x+min(0,l),y+shift+t,max(advance,r)-min(0,l),b-t])
            x+=advance+(item.get('tracking',0) if seg!='\n' else 0)
    return {'lines':lines,'positions':positions,'segments':segments,'glyphboxes':glyphboxes,
            'initial':{'count':end,'lines':rows,'font_size':lo,'font_role':role,
                       'reserved_width':reserved,'box':glyphboxes[0]}}
