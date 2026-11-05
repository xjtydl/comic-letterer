"""Project authored text outlines onto a convex four-corner surface."""
import math
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen
from .validation import vector


def projection(quad):
    if not isinstance(quad,list) or len(quad)!=4:raise ValueError('surface requires TL,TR,BR,BL points')
    q=[vector(p,2,'surface point') for p in quad]
    crosses=[]
    for i in range(4):
        a,b,c=q[i],q[(i+1)%4],q[(i+2)%4]
        crosses.append((b[0]-a[0])*(c[1]-b[1])-(b[1]-a[1])*(c[0]-b[0]))
    if min(crosses)<=1e-6:raise ValueError('surface must be clockwise convex TL,TR,BR,BL in page coordinates')
    matrix=[]
    for (u,v),(x,y) in zip([(0,0),(1,0),(1,1),(0,1)],q):
        matrix += [[u,v,1,0,0,0,-x*u,-x*v,x],[0,0,0,u,v,1,-y*u,-y*v,y]]
    for col in range(8):
        pivot=max(range(col,8),key=lambda row:abs(matrix[row][col]));matrix[col],matrix[pivot]=matrix[pivot],matrix[col]
        n=matrix[col][col]
        if abs(n)<1e-10:raise ValueError('degenerate surface')
        matrix[col]=[v/n for v in matrix[col]]
        for row in range(8):
            if row!=col:
                n=matrix[row][col];matrix[row]=[a-n*b for a,b in zip(matrix[row],matrix[col])]
    h=[row[-1] for row in matrix]
    # Prevent an internal horizon in the glyph area.
    if min(1,1+h[6],1+h[7],1+h[6]+h[7])<=.001:raise ValueError('surface crosses projective horizon')
    def transform(u,v):
        den=h[6]*u+h[7]*v+1
        return ((h[0]*u+h[1]*v+h[2])/den,(h[3]*u+h[4]*v+h[5])/den)
    return transform


class OutlinePen(BasePen):
    def __init__(self,glyphset,transform):super().__init__(glyphset);self.transform=transform;self.paths=[];self.current=[]
    def _moveTo(self,p):self.current=[self.transform(*p)]
    def _lineTo(self,p):self.current.append(self.transform(*p))
    def _curveToOne(self,b,c,d):
        a=self._getCurrentPoint()
        for i in range(1,25):
            t=i/24;u=1-t
            self.current.append(self.transform(*(u**3*a[k]+3*u*u*t*b[k]+3*u*t*t*c[k]+t**3*d[k] for k in (0,1))))
    def _qCurveToOne(self,b,c):
        a=self._getCurrentPoint()
        for i in range(1,25):
            t=i/24;u=1-t
            self.current.append(self.transform(*(u*u*a[k]+2*u*t*b[k]+t*t*c[k] for k in (0,1))))
    def _closePath(self):self.paths.append(self.current);self.current=[]
    def _endPath(self):self._closePath()


def projected_text(item,layout,bank):
    if item['kind'] not in ('sfx','floating'):raise ValueError('surface supports SFX or in-world floating text')
    if item.get('features') or item.get('rotation') or item.get('arc') or item.get('glyphs') or item.get('tracking'):
        raise ValueError('surface uses plain horizontal glyph outlines; omit OpenType/rotation/arc/tracking')
    if any(not (c.isspace() or c in '—–…“”‘’' or 0x20<=ord(c)<0x300 or 0x3000<=ord(c)<=0x9fff) for c in item['text']):
        raise ValueError('surface currently supports simple Latin/CJK, not complex-script shaping')
    warp=projection(item['surface']);box=item['box'];paths=[];boxes=[]
    for seg in layout['segments']:
        role=seg.get('font_role',item.get('font_role','body'));spec=bank[role]
        with TTFont(spec['path'],fontNumber=spec.get('index',0)) as font:
            gs=font.getGlyphSet();cmap=font.getBestCmap();scale=seg['font_size']/font['head'].unitsPerEm
            # Outline delivery has explicit advances; no hidden browser kerning.
            glyphnames=[cmap.get(ord(c),'.notdef') for c in seg['text'] if c!='\n']
            native=sum(gs[n].width*scale for n in glyphnames)
            stretch=seg.get('advance',native)/native if native else 1
            x=seg['x'];y=seg['y']
            for name in glyphnames:
                def transform(gx,gy):return warp((x+gx*scale*stretch-box[0])/box[2],(y-gy*scale-box[1])/box[3])
                pen=OutlinePen(gs,transform);gs[name].draw(pen)
                if pen.paths:
                    pts=[p for path in pen.paths for p in path];xs,ys=zip(*pts)
                    boxes.append([min(xs),min(ys),max(xs)-min(xs),max(ys)-min(ys)])
                    paths.append(' '.join('M'+' L'.join(f'{a:.4f},{b:.4f}' for a,b in path)+' Z' for path in pen.paths))
                x+=gs[name].width*scale*stretch
    return paths,boxes
