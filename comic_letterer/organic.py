"""Bounded, reproducible soft shells. Variation never changes voice semantics."""
import hashlib
import math

from .validation import fields, number

DEFAULTS = dict(variation=.55, roundness=2.3, seed=17)


def resolve(item):
    raw = item.get('organic')
    if raw is not None and item.get('shape') != 'organic':
        raise ValueError('organic parameters require organic shape')
    if raw is None:
        return dict(DEFAULTS)
    fields(raw, ' '.join(DEFAULTS), 'organic')
    spec = {**DEFAULTS, **raw}
    for key, low, high in [('variation', 0, 1), ('roundness', 2, 3)]:
        if not low <= number(spec[key], 'organic ' + key) <= high:
            raise ValueError(f'organic {key} must be {low}..{high}')
    if type(spec['seed']) is not int or not 0 <= spec['seed'] <= 65535:
        raise ValueError('organic seed must be an integer 0..65535')
    return spec


def prepare(item, box):
    spec = resolve(item)
    if item.get('shape') != 'organic':
        return None
    # Preserve v0.4 ordinary organic geometry when no profile was requested.
    if item.get('organic') is None and item['kind'] in ('speech', 'whisper'):
        return None
    if item.get('voice') == 'rough' or item.get('double_outline'):
        raise ValueError('organic profile conflicts with rough voice or double outline')
    x, y, w, h = box
    seed = hashlib.sha256(str(spec['seed']).encode()).digest()
    phases = [n / 255 * math.tau for n in seed[:4]]
    amount, power = spec['variation'], spec['roundness']
    kind = 'thought' if item.get('voice') == 'telepathic' else item['kind']
    points = []
    for j in range(256):
        a = math.tau * j / 256
        co, si = math.cos(a), math.sin(a)
        r = 1 - .08 * amount + amount * (
            .045 * math.sin(3*a + phases[0]) + .025 * math.sin(2*a + phases[1])
            + .01 * math.sin(5*a + phases[2]))
        # Cloud/weak edges remain distinct, with unequally spaced soft lobes.
        if kind in ('thought', 'weak'):
            depth = .055 if kind == 'thought' else .026
            r *= 1 - depth * (1 - math.cos((9 if kind == 'thought' else 11)*a
                                          + .65*math.sin(3*a+phases[3])))
        radius = r / (abs(co)**power + abs(si)**power)**(1/power)
        points.append((x+w/2 + w/2*radius*co, y+h/2 + h/2*radius*si))
    return dict(path='M'+' L'.join(f'{px:.4f},{py:.4f}' for px, py in points)+' Z',
                polygon=points, spec=spec)
