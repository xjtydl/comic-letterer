"""Optional balloon surface and edge treatments; never filter text or artwork."""
import copy
import hashlib
import json

from .validation import fields, number, color

DEFAULTS = dict(paper=0, grain_scale=1, seed=17, glow=0,
                glow_color='#DDC9A0', glow_opacity=.45, whisper_border='outside')


def resolve(item):
    raw = item.get('appearance')
    if raw is None:
        return dict(DEFAULTS)
    fields(raw, ' '.join(DEFAULTS), 'appearance')
    if item.get('kind') in ('sfx', 'floating'):
        raise ValueError('appearance requires a balloon or caption shell')
    spec = {**DEFAULTS, **raw}
    for key, low, high in [('paper', 0, .3), ('grain_scale', .5, 4),
                           ('glow', 0, 12), ('glow_opacity', 0, 1)]:
        if not low <= number(spec[key], 'appearance ' + key) <= high:
            raise ValueError(f'appearance {key} must be {low}..{high}')
    if type(spec['seed']) is not int or not 0 <= spec['seed'] <= 65535:
        raise ValueError('appearance seed must be an integer 0..65535')
    color(spec['glow_color'])
    if spec['whisper_border'] not in ('outside', 'center'):
        raise ValueError('appearance whisper_border must be outside or center')
    if spec['whisper_border'] == 'center' and item.get('kind') != 'whisper':
        raise ValueError('center whisper_border requires whisper')
    return spec


def _paper(fill, spec, defs, elem, cache):
    key = (fill, spec['paper'], spec['grain_scale'], spec['seed'])
    if key in cache:
        return cache[key]
    suffix = hashlib.sha256(json.dumps(key).encode()).hexdigest()[:16]
    pid, fid = 'paper-' + suffix, 'grain-' + suffix
    scale = spec['grain_scale']
    tile = 128 * scale
    filt = elem('filter', {'id': fid, 'x': 0, 'y': 0, 'width': '100%', 'height': '100%',
                          'color-interpolation-filters': 'sRGB'}, defs)
    elem('feTurbulence', {'type': 'fractalNoise', 'baseFrequency': .18 / scale,
                         'numOctaves': 3, 'seed': spec['seed'], 'stitchTiles': 'stitch',
                         'result': 'noise'}, filt)
    elem('feColorMatrix', {'in': 'noise', 'type': 'saturate', 'values': 0}, filt)
    transfer = elem('feComponentTransfer', parent=filt)
    for channel in 'RGB':
        elem('feFunc' + channel, {'type': 'linear', 'slope': spec['paper'],
                                 'intercept': 1 - spec['paper']}, transfer)
    elem('feBlend', {'in2': 'SourceGraphic', 'mode': 'multiply'}, filt)
    elem('feComposite', {'in2': 'SourceGraphic', 'operator': 'in'}, filt)
    pattern = elem('pattern', {'id': pid, 'patternUnits': 'userSpaceOnUse',
                               'x': 0, 'y': 0, 'width': tile, 'height': tile}, defs)
    elem('rect', {'width': tile, 'height': tile, 'fill': fill,
                  'filter': f'url(#{fid})'}, pattern)
    cache[key] = f'url(#{pid})'
    return cache[key]


def _silhouette(node):
    result = copy.deepcopy(node)
    for key in ('id', 'filter', 'mask', 'stroke-dasharray', 'fill-opacity'):
        result.attrib.pop(key, None)
    result.set('fill', '#FFFFFF')
    result.set('stroke', '#FFFFFF')
    return result


def apply_all(placed, groups, defs, elem, width, height):
    """Apply after geometry exists, so incoming joins can clear inset borders."""
    paper_cache = {}
    joins = {}
    for p in placed:
        if p.get('join_to'):
            path = next(n for n in groups[p['id']][1] if n.get('id') == 'join-' + p['id'])
            joins.setdefault(p['id'], []).append(path)
            joins.setdefault(p['join_to'], []).append(path)
    for p in placed:
        spec = resolve(p)
        if not (spec['paper'] or spec['glow'] or spec['whisper_border'] == 'center'):
            continue
        iid = p['id']
        bottom, connectors, fills = groups[iid]
        outline = next(n for n in bottom if n.get('id') == 'outline-' + iid)
        body = next(n for n in fills if n.get('id') == 'fill-' + iid)
        # All solid components use one page-space pattern. Overlap at a tail root
        # samples the same pixels instead of starting a new grain field.
        shells = [n for n in list(bottom) + list(connectors) + [body]
                  if n.get('fill') == p['fill']]
        if spec['paper']:
            paint = _paper(p['fill'], spec, defs, elem, paper_cache)
            for n in shells:
                n.set('fill', paint)
            for n in bottom:
                if n.get('id') == 'mechanical-broken-' + iid:
                    n.set('stroke', paint)
        if spec['glow'] and spec['glow_opacity']:
            pad = spec['glow'] * 4 + p['stroke_width'] * 2 + p.get('double_outline', 0)
            boxes = [p['box']] + ([p['_tail']['box']] if p['_tail'] else []) + p.get('_join_cells', [])
            x, y = min(b[0] for b in boxes) - pad, min(b[1] for b in boxes) - pad
            right = max(b[0] + b[2] for b in boxes) + pad
            lower = max(b[1] + b[3] for b in boxes) + pad
            fid = 'edge-glow-' + iid
            filt = elem('filter', {'id': fid, 'filterUnits': 'userSpaceOnUse',
                                  'x': x, 'y': y, 'width': right-x, 'height': lower-y,
                                  'color-interpolation-filters': 'sRGB'}, defs)
            elem('feGaussianBlur', {'in': 'SourceAlpha', 'stdDeviation': spec['glow'], 'result': 'halo'}, filt)
            elem('feFlood', {'flood-color': spec['glow_color'], 'flood-opacity': spec['glow_opacity']}, filt)
            elem('feComposite', {'in2': 'halo', 'operator': 'in'}, filt)
            glow = elem('g', {'id': 'glow-' + iid, 'filter': f'url(#{fid})', 'aria-hidden': 'true'})
            for node in shells:
                glow.append(_silhouette(node))
            bottom.insert(0, glow)
        if spec['whisper_border'] == 'center':
            # Half the dashed edge remains over light paper. Remove that edge
            # where a tail or either end of a join passes through the shell.
            outline.set('stroke-width', str(p['stroke_width']))
            mid = 'whisper-root-mask-' + iid
            mask = elem('mask', {'id': mid, 'maskUnits': 'userSpaceOnUse', 'x': 0, 'y': 0,
                                 'width': width, 'height': height, 'style': 'mask-type:luminance'}, defs)
            elem('rect', {'width': width, 'height': height, 'fill': '#FFFFFF'}, mask)
            cutouts = [n for n in connectors if n.get('id') == 'tail-' + iid] + joins.get(iid, [])
            for node in cutouts:
                cut = _silhouette(node)
                cut.set('fill', '#000000')
                cut.set('stroke', '#000000')
                mask.append(cut)
            attrs = {**outline.attrib, 'id': 'whisper-border-' + iid,
                     'fill': 'none', 'mask': f'url(#{mid})'}
            elem('path', attrs, fills)
