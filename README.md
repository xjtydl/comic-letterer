# Comic Letterer

An independent, CPU-based comic lettering library and CLI. Exact Unicode text + explicit panel/speaker coordinates → editable SVG + explainable checks + optional PNG.

独立原创漫画排字工具。保留真实中文和审定原文，把字体度量、气泡、尾巴、连泡、拟声字、图层和检查做成程序；把叙事与视觉判断交给配套 Skill。当前为 **v0.1**，不是全功能图形编辑器，也不宣称覆盖全部漫画知识。

[Download v0.1.0](https://github.com/xjtydl/comic-letterer/releases/tag/v0.1.0)

![Original Chinese lettering specimen](https://github.com/xjtydl/comic-letterer/releases/download/v0.1.0/specimen-reading.png)

## Install

Python 3.10 or newer:

```sh
python -m pip install '.[test,png]'
python -m playwright install chromium
```

Supply a locally licensed font with all needed glyphs (TTF, OTF or TTC, with `--font-index` for collections). Fonts and comic art are not bundled. `COMIC_LETTERER_FONT` can set a default; automatic font discovery is only a convenience.

## Run

```sh
comic-letterer check examples/specimen.json --font /path/to/font.ttf --strict
python examples/make_specimen.py /path/to/output --font /path/to/font.ttf
comic-letterer render examples/specimen.json \
  --font /path/to/font.ttf --out /path/to/output \
  --background /path/to/output/plate.png --png --strict
```

Equivalent source checkout entry point: `python -m comic_letterer`.

Outputs: `page.svg`, `source.json`, `report.json`, optionally `master.png` and `reading.png`. Both PNGs are rendered directly from the vector master. Existing output files require `--force`. Original input files cannot be overwritten by output flags. A supplied PNG/JPEG background must match the canvas dimensions; it is embedded unchanged in the SVG.

Exit codes: **0** no errors; **1** layout errors (or any warning with `--strict`); **2** invalid input or ordinary file/dependency errors. A diagnostic SVG may still be written on exit 1. Rendering failures may leave partial outputs: inspect the exit status and report, then rerun into a fresh directory.

## Implemented

- Measured text wrapping, CJK punctuation boundary handling, explicit newline preservation, missing-glyph checks and optional frozen-text verification. No automatic text rewriting or font shrinking.
- Speech, thought, shout, whisper, weak, electronic, caption and SFX presets. These are starting styles, not an exhaustive voice taxonomy.
- Curved speech tails, thought dots, angular electronic tails; same-speaker consecutive speech/whisper joins.
- Explicit placement or deterministic candidate search; declared reading order, protected rectangles, text fit, overlap and reading-size checks.
- Editable Unicode SVG groups for art, balloons, connectors, text and SFX. Multi-outline rotated SFX retains one text source.
- Optional offline Chromium rendering using the selected font locally. SVG references the font family and records its hash; it does **not** embed or redistribute font bytes.

```python
from comic_letterer.engine import compile_page
svg, report = compile_page(job, font_path='/path/to/font.ttf')
if not report['ok']:
    print(report['issues'])
```

See [input contract](docs/contract.md), [tutorial coverage](docs/coverage.md), [verification record](docs/verification.md) and [release notes](CHANGELOG.md).

## Companion Skill

Copy `skills/comic-letterer` into your agent's skill directory. The [Skill](skills/comic-letterer/SKILL.md) selects methods from actual story facts, prepares JSON and interprets reports. It is portable and does not depend on a private comic project. Install the Python program separately. See its [workflow reference](skills/comic-letterer/references/workflow.md).

## Limits

No GUI, image understanding, face detection, automatic story inference, per-word emphasis, arbitrary path editing, text-to-path export, PDF/CMYK/prepress certification, true hollow SFX, border-butting, squinks, perspective lettering or advanced typography shaping. Horizontal CJK and simple Latin are the tested text domains; bidirectional/complex scripts, emoji clusters and vertical typesetting need further work.

Bounding-envelope checks are conservative. They can report false positives and cannot establish visual acceptance. Candidate placement is greedy, does not optimize the entire page and does not infer character identities. A clean report still requires inspection at reading size. SVG text may reflow visually if the receiving application substitutes fonts.

## Development

```sh
python -m pytest
COMIC_LETTERER_RENDER_TEST=1 python -m pytest
```

The optional second command requires Chromium and exercises real PNG output. Use `TMPDIR` and pytest `--basetemp` if your project requires generated files on a separate volume.

Implementation and synthetic examples are original. Public teaching references are acknowledged in the coverage document; no third-party application code, tutorial illustrations, commercial fonts or production comic artwork are included. MIT license applies to this repository's original code and examples; it grants no rights to external fonts or artwork.
