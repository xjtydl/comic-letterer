"""Bounded editable cubic shells. Coordinates are normalized to the balloon box."""
import math
from .validation import fields, vector, number


def inside(point, polygon):
    x,y=point; hit=False
    for a,b in zip(polygon,polygon[1:]+polygon[:1]):
        if (a[1]>y)!=(b[1]>y) and x < (b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:hit=not hit
    return hit


def prepare_path(item, box):
    shape=item.get('shape')
    if shape=='flat':
        r=number(item.get('corner',.18),'corner',True)
        if not .02<=r<=.5:raise ValueError('corner must be .02..0.5')
        k=.55228475
        start=[r,0]
        curves=[[1-r,0,1-r,0,1-r,0],[1-r+k*r,0,1,r-k*r,1,r],
                [1,1-r,1,1-r,1,1-r],[1,1-r+k*r,1-r+k*r,1,1-r,1],
                [r,1,r,1,r,1],[r-k*r,1,0,1-r+k*r,0,1-r],
                [0,r,0,r,0,r],[0,r-k*r,r-k*r,0,r,0]]
    else:
        spec=item.get('contour')
        fields(spec,'start curves','contour');start=vector(spec.get('start'),2,'contour start')
        curves=spec.get('curves')
        if not isinstance(curves,list) or not 2<=len(curves)<=32:
            raise ValueError('contour requires 2..32 cubic segments')
        curves=[vector(c,6,'contour cubic') for c in curves]
        if curves[-1][-2:]!=start:raise ValueError('contour must close explicitly')
        if any(not 0<=n<=1 for n in start+[v for c in curves for v in c]):
            raise ValueError('contour coordinates must stay within 0..1')
    def actual(p):return (box[0]+box[2]*p[0],box[1]+box[3]*p[1])
    def fmt(p):return ','.join(f'{v:.4f}' for v in actual(p))
    d='M'+fmt(start);points=[];a=start
    for raw in curves:
        b,c,z=raw[:2],raw[2:4],raw[4:]
        d+=' C'+' '.join(fmt(p) for p in [b,c,z])
        for j in range(24):
            t=j/24;u=1-t
            points.append(actual([u**3*a[k]+3*u*u*t*b[k]+3*u*t*t*c[k]+t**3*z[k] for k in (0,1)]))
        a=z
    # A self-crossing shell has no safe interpretation for text or tail roots.
    def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
    edges=list(zip(points,points[1:]+points[:1]))
    for i,(a,b) in enumerate(edges):
        for j in range(i+2,len(edges)):
            c,z=edges[j]
            if cross(a,b,c)*cross(a,b,z)<-1e-8 and cross(c,z,a)*cross(c,z,b)<-1e-8:
                raise ValueError('contour self-intersects')
    if not inside((box[0]+box[2]/2,box[1]+box[3]/2),points):
        raise ValueError('contour must contain its center for tail attachment')
    return {'path':d+' Z','spec':{'corner':r} if shape=='flat' else {},'polygon':points}


def ray_boundary(center, direction, polygon):
    dx,dy=direction;hits=[]
    for a,b in zip(polygon,polygon[1:]+polygon[:1]):
        ex,ey=b[0]-a[0],b[1]-a[1];den=dx*ey-dy*ex
        if abs(den)<1e-10:continue
        ax,ay=a[0]-center[0],a[1]-center[1]
        t=(ax*ey-ay*ex)/den;u=(ax*dy-ay*dx)/den
        if t>0 and 0<=u<=1:hits.append(t)
    if not hits:raise ValueError('contour has no valid tail intersection')
    t=min(hits);return center[0]+dx*t,center[1]+dy*t


def box_inside(box, polygon, padding):
    x,y,w,h=box
    # Sample edges as well as corners: concave notches cannot be skipped.
    points=[(x+w*i/16,y+h*j) for i in range(17) for j in (0,1)]
    points += [(x+w*j,y+h*i/16) for i in range(17) for j in (0,1)]
    for p in points:
        if not inside(p,polygon):return False
        for a,b in zip(polygon,polygon[1:]+polygon[:1]):
            dx,dy=b[0]-a[0],b[1]-a[1];den=dx*dx+dy*dy
            t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/den)) if den else 0
            if math.dist(p,(a[0]+t*dx,a[1]+t*dy)) < padding:return False
    return True
