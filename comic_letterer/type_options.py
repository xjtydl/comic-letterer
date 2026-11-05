"""Explicit OpenType controls and read-only language advice, never copy editing."""
import re
from functools import lru_cache
from fontTools.ttLib import TTFont
from PIL import features as pillow_features
from .validation import number


@lru_cache(maxsize=32)
def font_features(path, index=0):
    with TTFont(path, fontNumber=index) as f:
        tags = set()
        for table in ('GSUB', 'GPOS'):
            if table in f and f[table].table.FeatureList:
                tags.update(r.FeatureTag for r in f[table].table.FeatureList.FeatureRecord)
        if 'kern' in f:
            tags.add('kern')
    return frozenset(tags)


def options(item, bank, roles):
    features = item.get('features', {})
    if not isinstance(features, dict) or any(
        not isinstance(k, str) or not re.fullmatch(r'[A-Za-z0-9]{4}', k)
        or type(v) not in (int, bool) or not 0 <= v <= 99
        for k, v in features.items()
    ):
        raise ValueError('features must map four-character OpenType tags to 0..99')
    language = item.get('language')
    if language is not None and (not isinstance(language, str) or not re.fullmatch(r'[A-Za-z]{2,8}(?:-[A-Za-z0-9]{1,8})*', language)):
        raise ValueError('language must be a BCP47-style tag')
    if features and not pillow_features.check('raqm'):
        raise ValueError('OpenType measurement requires Pillow with libraqm')
    for role in roles:
        available = font_features(bank[role]['path'], bank[role].get('index', 0))
        missing = features.keys() - available
        if missing:
            raise ValueError(f'font {role} does not provide features: {sorted(missing)}')
    kwargs = {}
    if features:
        kwargs['features'] = [f'{k}={int(v)}' for k, v in features.items()]
    if language and pillow_features.check('raqm'):
        kwargs['language'] = language
    return kwargs


def row_options(item, inner):
    result = []
    for key, low, high in [('line_widths', 1, inner), ('line_scales', .9, 1.1)]:
        values = item.get(key, [])
        if not isinstance(values, list) or len(values) > 128:
            raise ValueError(key + ' must be an array of at most 128 values')
        values = [number(v, key, True) for v in values]
        if any(not low <= v <= high for v in values):
            raise ValueError(f'{key} must be within {low}..{high}')
        result.append(values)
    return result


def language_advice(item):
    """Opt-in language conventions. All findings are suggestions with offsets."""
    text = item['text']; lang = item.get('language', '').lower(); out = []
    def add(code, start, end, message):
        out.append({'code': code, 'start': start, 'end': end, 'message': message})
    if lang.startswith('zh'):
        for m in re.finditer(r'(?<!\.)\.{3}(?!\.)|(?<!…)…(?!…)', text):
            add('zh_ellipsis', *m.span(), '中文省略号通常用六点；核对本书约定，原文不自动改写。')
        for m in re.finditer(r'(?<=[\u3400-\u9fff])[,;:](?=[\u3400-\u9fff])', text):
            add('zh_punctuation', *m.span(), '中文句内出现半角标点；核对是否有意。')
    if lang.startswith('en'):
        for m in re.finditer(r'\bi\b', text):
            add('en_pronoun_i', *m.span(), 'Check first-person I capitalization; crossbar choice depends on the font/book.')
    for opening, closing in [('“','”'),('‘','’'),('「','」'),('『','』'),('（','）')]:
        if text.count(opening) != text.count(closing):
            add('unpaired_quote', 0, len(text), '引号/括号未配对；可能跨气泡，需结合上下文检查。')
    # Break candidates are offsets, never replacement strings or inferred translations.
    return {'findings': out, 'break_candidates': [i+1 for i,c in enumerate(text[:-1]) if c in '，。！？；：,.;:!?'],
            'scope': 'Opt-in conventions and punctuation boundaries; semantic phrases remain authored.'}
