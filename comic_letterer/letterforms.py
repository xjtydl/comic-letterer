"""Original pressure-stroke glyph sources -> installable TrueType display font.

This is a small authored alphabet tool, not automatic handwriting recognition.
Points use font coordinates (baseline y=0); source JSON remains editable.
"""
import math
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from .validation import fields, number


def stroke_outline(stroke):
    fields(stroke,'points width','stroke')
    raw=stroke.get('points');width=number(stroke.get('width',50),'stroke width',True)
    if not isinstance(raw,list) or not 2<=len(raw)<=2048 or width>300:
        raise ValueError('stroke needs 2..2048 points and width <=300')
    points=[]
    for p in raw:
        if not isinstance(p,list) or len(p) not in (2,3):raise ValueError('stroke points use x,y[,pressure]')
        x,y=[number(v,'stroke coordinate') for v in p[:2]]
        pressure=number(p[2] if len(p)==3 else 1,'pressure',True)
        if not 0.1<=pressure<=2 or not -200<=x<=1400 or not -250<=y<=1100:
            raise ValueError('stroke coordinates/pressure outside font design bounds')
        if points and (x,y)==points[-1][:2]:raise ValueError('duplicate consecutive stroke point')
        points.append((x,y,pressure))
    left=[];right=[]
    for i,(x,y,pressure) in enumerate(points):
        a=points[max(0,i-1)];b=points[min(len(points)-1,i+1)]
        dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy)
        if length<1e-8:raise ValueError('stroke doubles back; split it at the turn')
        w=width*pressure/2
        left.append((x-dy/length*w,y+dx/length*w));right.append((x+dy/length*w,y-dx/length*w))
    return left+right[::-1]


def build_font(source, destination):
    fields(source,'family glyphs kerning alternates license','font source')
    family=source.get('family')
    if not isinstance(family,str) or not family.strip() or len(family)>80:raise ValueError('font family required')
    glyphs=source.get('glyphs')
    if not isinstance(glyphs,dict) or not glyphs or len(glyphs)>4096:raise ValueError('provide 1..4096 original glyphs')
    if not isinstance(source.get('license'),str) or not source['license'].strip():raise ValueError('record glyph source/license')
    order=['.notdef','space'];cmap={32:'space'};metrics={'.notdef':(600,0),'space':(300,0)};drawn={}
    pen=TTGlyphPen(None);drawn['.notdef']=pen.glyph();drawn['space']=pen.glyph()
    names={}
    for char,spec in glyphs.items():
        if len(char)!=1 or char.isspace() or 0xD800<=ord(char)<=0xDFFF:raise ValueError('glyph key must be one printable code point')
        fields(spec,'advance strokes','glyph source');advance=number(spec.get('advance',700),'advance',True)
        if advance>1500 or not isinstance(spec.get('strokes'),list) or not spec['strokes']:raise ValueError('invalid glyph advance/strokes')
        name=f'uni{ord(char):04X}';names[char]=name;order.append(name);cmap[ord(char)]=name
        pen=TTGlyphPen(None);xmin=2000
        for stroke in spec['strokes']:
            pts=stroke_outline(stroke);xmin=min(xmin,*(p[0] for p in pts))
            pen.moveTo(pts[0])
            for p in pts[1:]:pen.lineTo(p)
            pen.closePath()
        drawn[name]=pen.glyph();metrics[name]=(round(advance),round(xmin))
    fb=FontBuilder(1000,isTTF=True);fb.setupGlyphOrder(order);fb.setupCharacterMap(cmap)
    fb.setupGlyf(drawn);fb.setupHorizontalMetrics(metrics);fb.setupHorizontalHeader(ascent=1100,descent=-250)
    fb.setupNameTable({'familyName':family,'styleName':'Regular','uniqueFontIdentifier':family+'-Regular',
                      'fullName':family,'psName':''.join(c for c in family if c.isalnum())+'-Regular',
                      'version':'Version 1.0','licenseDescription':source['license']})
    fb.setupOS2(sTypoAscender=1100,sTypoDescender=-250,usWinAscent=1100,usWinDescent=250)
    fb.setupPost();fb.setupMaxp()
    statements=[]
    for pair,amount in source.get('kerning',{}).items():
        if len(pair)!=2 or any(c not in names for c in pair):raise ValueError('kerning pair must use known glyphs')
        amount=number(amount,'kerning')
        if abs(amount)>300:raise ValueError('kerning exceeds 300 font units')
        statements.append(f'pos {names[pair[0]]} {names[pair[1]]} {round(amount)};')
    features=('feature kern {'+' '.join(statements)+'} kern;') if statements else ''
    # Explicit alternative code points can also supply a stylistic-set substitution.
    for char,alt in source.get('alternates',{}).items():
        if char not in names or alt not in names:raise ValueError('alternate must use known glyphs')
    if source.get('alternates'):
        features+='feature ss01 {'+' '.join(f'sub {names[a]} by {names[b]};' for a,b in source['alternates'].items())+'} ss01;'
    if features:addOpenTypeFeaturesFromString(fb.font,features)
    fb.save(destination)
    return {'family':family,'glyphs':len(glyphs),'source_preserved':True,'features':(['kern'] if statements else [])+(['ss01'] if source.get('alternates') else [])}
