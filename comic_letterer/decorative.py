"""Original editable contour constructions; no third-party brushes or paths."""
import bisect
import math
from .validation import fields, number


def inset(box, x, y=None):
    y = x if y is None else y
    return [box[0] + x, box[1] + y, box[2] - 2*x, box[3] - 2*y]


def edge_spec(item, box):
    spec = item.get('edge')
    if spec is None:
        spec = {}
    fields(spec, 'spacing depth', 'edge')
    spacing = number(spec.get('spacing', 24), 'edge spacing', True)
    depth = number(spec.get('depth', min(10, min(box[2:]) * .08)), 'edge depth', True)
    if not 8 <= spacing <= 128:
        raise ValueError('edge spacing must be 8..128 pixels')
    if not 1 <= depth <= min(box[2:]) * .16:
        raise ValueError('edge depth must be 1..16% of the smaller dimension')
    return {'spacing': spacing, 'depth': depth}


def mechanical_spec(item, box):
    spec = item.get('mechanical')
    if spec is None:
        spec = {}
    fields(spec, 'band dash gap notch', 'mechanical')
    out = {k: number(spec.get(k, default), 'mechanical '+k, True)
           for k, default in [('band', 7), ('dash', 7), ('gap', 5), ('notch', .09)]}
    if not 2 <= out['band'] <= min(24, min(box[2:]) * .12):
        raise ValueError('mechanical band must fit the contour (2..24px, at most 12%)')
    if not all(1 <= out[k] <= 80 for k in ('dash', 'gap')):
        raise ValueError('mechanical dash/gap must be 1..80 pixels')
    if not .02 <= out['notch'] <= .16:
        raise ValueError('mechanical notch must be .02.. .16')
    return out


def scroll_spec(item, box):
    spec = item.get('scroll')
    if spec is None:
        spec = {}
    fields(spec, 'curl', 'scroll')
    curl = number(spec.get('curl', min(18, box[3] * .2)), 'scroll curl', True)
    if not 4 <= curl <= min(box[2] * .16, box[3] * .3):
        raise ValueError('scroll curl must fit within the caption')
    return {'curl': curl}


def mechanical_radius(angle, notch):
    # Four shallow bites centered on the diagonal corners of an oval.
    phase = ((angle - math.pi/4 + math.pi/4) % (math.pi/2)) - math.pi/4
    return 1 - notch * max(0, 1 - abs(phase)/.16)


def mechanical_path(box, spec):
    x, y, w, h = inset(box, spec['band'])
    points = []
    for j in range(320):
        a = math.tau*j/320
        r = mechanical_radius(a, spec['notch'])
        points.append((x+w/2+w/2*r*math.cos(a), y+h/2+h/2*r*math.sin(a)))
    return 'M'+' L'.join(f'{x:.4f},{y:.4f}' for x,y in points)+' Z'


def toothed_path(box, shape, spec):
    """Equal arc-length tooth spacing, with curved asymmetric flame cusps."""
    x,y,w,h = box
    cx,cy,a,b = x+w/2,y+h/2,w/2,h/2
    points = [(cx+a*math.cos(math.tau*j/1024), cy+b*math.sin(math.tau*j/1024)) for j in range(1025)]
    lengths = [0.0]
    for p,q in zip(points,points[1:]):
        lengths.append(lengths[-1]+math.dist(p,q))
    perimeter = lengths[-1]
    count = max(8, round(perimeter/spec['spacing']))
    if count > 512:
        raise ValueError('edge spacing requires more than 512 teeth; increase spacing')
    step = perimeter/count
    def point(s, depth=0):
        s %= perimeter
        i = max(1, bisect.bisect_left(lengths,s))
        t = (s-lengths[i-1])/(lengths[i]-lengths[i-1])
        px,py = [points[i-1][k]*(1-t)+points[i][k]*t for k in (0,1)]
        nx,ny = (px-cx)/a**2,(py-cy)/b**2
        norm=math.hypot(nx,ny);nx/=norm;ny/=norm
        return (px-depth*nx,py-depth*ny),(-ny,nx),(nx,ny)
    def fmt(p):
        # Keep all Bezier controls in the declared envelope too.
        return f'{max(x,min(x+w,p[0])):.4f},{max(y,min(y+h,p[1])):.4f}'
    depth=spec['depth'];parts=[]
    for i in range(count):
        v,t,n=point(i*step,depth)
        tip,tt,nt=point((i+.72)*step)
        end,te,ne=point((i+1)*step,depth)
        if i==0:parts.append('M'+fmt(v))
        if shape=='sawtooth':
            parts.extend(['L'+fmt(tip),'L'+fmt(end)])
        else:
            c1=(v[0]+t[0]*step*.38,v[1]+t[1]*step*.38)
            c2=(tip[0]-tt[0]*step*.38-nt[0]*depth*.7,tip[1]-tt[1]*step*.38-nt[1]*depth*.7)
            c3=(tip[0]-nt[0]*depth*.8,tip[1]-nt[1]*depth*.8)
            c4=(end[0]-te[0]*step*.14,end[1]-te[1]*step*.14)
            parts.extend(['C'+fmt(c1)+' '+fmt(c2)+' '+fmt(tip),
                          'C'+fmt(c3)+' '+fmt(c4)+' '+fmt(end)])
    return ' '.join(parts)+' Z',count,perimeter/count


def scroll_geometry(box, spec):
    """Rolled parchment sides inside an explicit outer box and reserved text area."""
    x,y,w,h=box;c=spec['curl'];r=c*.5
    d=(f'M{x+c},{y} H{x+w-c} Q{x+w},{y} {x+w},{y+c} '
       f'V{y+h-c} Q{x+w},{y+h} {x+w-c},{y+h} H{x+c} '
       f'Q{x},{y+h} {x},{y+h-c} V{y+c} Q{x},{y} {x+c},{y} Z')
    folds=[]
    for side in (0,1):
        # Mirrored curls remain behind a safe central text rectangle.
        sx=x if side==0 else x+w;sgn=1 if side==0 else -1
        ix=sx+sgn*c
        folds.append(f'M{ix},{y} C{sx+sgn*c*.1},{y} {sx+sgn*c*.1},{y+c} {ix},{y+c} '
                     f'C{sx+sgn*c*1.6},{y+c} {sx+sgn*c*1.6},{y+r} {ix},{y+r} '
                     f'M{ix},{y+c} V{y+h-c} '
                     f'C{sx+sgn*c*.1},{y+h-c} {sx+sgn*c*.1},{y+h} {ix},{y+h} '
                     f'C{sx+sgn*c*1.6},{y+h} {sx+sgn*c*1.6},{y+h-r} {ix},{y+h-r}')
    rolls=[
        f'M{x+c},{y} Q{x},{y} {x},{y+c} V{y+h-c} Q{x},{y+h} {x+c},{y+h} Z',
        f'M{x+w-c},{y} Q{x+w},{y} {x+w},{y+c} V{y+h-c} Q{x+w},{y+h} {x+w-c},{y+h} Z',
    ]
    return d,folds,rolls,inset(box,c*1.65,c*.45)


def prepare_decoration(item, box):
    shape=item.get('shape')
    from .organic import prepare
    organic = prepare(item, box)
    if organic:
        for key in ('edge', 'mechanical', 'scroll'):
            if item.get(key) is not None:
                raise ValueError(key+' parameters require their matching shape')
        return organic
    if shape in ("flat", "custom"):
        from .custom_path import prepare_path
        if item.get("voice") in ("rough","telepathic") or item.get("double_outline"):
            raise ValueError("custom/flat contour conflicts with voice or double outline")
        return prepare_path(item, box)
    for key,valid in [('edge',('sawtooth','flame')),('mechanical',('mechanical',)),('scroll',('scroll',))]:
        if item.get(key) is not None and shape not in valid:
            raise ValueError(key+' parameters require their matching shape')
    if shape in ('sawtooth','flame','mechanical') and item.get('voice','normal') in ('rough','telepathic'):
        raise ValueError('decorative contour conflicts with rough/telepathic contour')
    if shape in ('sawtooth','flame'):
        spec=edge_spec(item,box);d,n,spacing=toothed_path(box,shape,spec)
        return {'path':d,'spec':spec,'teeth':n,'actual_spacing':spacing}
    if shape=='mechanical':
        spec=mechanical_spec(item,box)
        return {'path':mechanical_path(box,spec),'spec':spec}
    if shape=='scroll':
        spec=scroll_spec(item,box);d,folds,rolls,text_box=scroll_geometry(box,spec)
        return {'path':d,'spec':spec,'folds':folds,'rolls':rolls,'text_box':text_box}
    return None
