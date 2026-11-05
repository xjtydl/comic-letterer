# Comic Letterer

An independent, CPU-based comic lettering library, CLI and local visual editor. Exact Unicode text + explicit panel/speaker coordinates → editable SVG + explainable checks + optional PNG.

独立原创漫画排字工具。保留真实中文和审定原文，把字体度量、气泡、尾巴、连泡、拟声字、图层和检查做成程序；把叙事与视觉判断交给配套 Skill。**v0.7** 新增带来源保护的全书批量修订和前后漫画对照，已用四页中英文600px阅读版验证。v0.6补入 OpenType、逐行字宽、手修曲线、叠放/跨边、透视字形、材质与原创笔触字体，使用两页《最后一张票》中英文完整剧情验证；随后增加真实全书校样和字体漂移检查。完整目标与能力边界见 [45模块工作入口](docs/WORK_INDEX.md)，不宣称全部漫画/字体能力已经完成。

[Download v0.7.0](https://github.com/xjtydl/comic-letterer/releases/tag/v0.7.0)

![The Last Ticket — original narrative page](https://github.com/xjtydl/comic-letterer/releases/download/v0.7.0/theatre-600-p1-zh.png)

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

## Visual editor

```sh
comic-letterer edit examples/echo-station.json \
  --font /path/to/dialogue-font.ttf --display-font /path/to/display-font.otf \
  --background /path/to/echo-station-art.png --out /path/to/new-output
```

Use `--font-map /path/to/fonts.json` for additional roles such as bold, italic and narrator. See the contract for map format.

Open the printed `http://127.0.0.1:PORT` URL. Drag boxes, resize with the blue handle, move sources with green handles and join curves with purple handles. Orange handles adjust tail curves. Phrase protection, face-based emphasis, tail refinement, caption types and bounded contour fit are available in the sidebar. Change line breaks without rewriting frozen words, select words to emphasize, undo/redo, save a new JSON draft, and export SVG or SVG plus two PNG sizes. Reading-size view displays the configured pixel width. Advanced item JSON exposes the remaining style controls. This is an editor for existing lettering jobs; it does not yet draw panels or import arbitrary scripts.

The server binds to loopback only and rejects foreign Host/Origin and unauthenticated writes. Frozen wording is checked on the server against the initial document. Saves are versioned copies; reload returns the last saved draft within that session. Restart with the saved JSON to resume. Browser previews use local font subsets in memory; exports remain dependent on the named fonts.

[Editor screenshot](https://github.com/xjtydl/comic-letterer/releases/download/v0.6.0/editor.png) · [600px before/after](https://github.com/xjtydl/comic-letterer/releases/download/v0.7.0/comparison-p1-zh.png) · [Actual narrative validation](docs/v07-validation.md)

## Implemented

- Independent break offsets, manually protected phrases, balanced line lengths, real-font mixed emphasis, tracking, controlled horizontal scale and alignment. `--font-map` supplies actual bold/italic faces.
- Independent tail width/length/gap/root/curve controls; attribution may live on a continuation. Optional short-tail and marked-ink-edge warnings.
- Reusable page styles, explicit caption source types, rough/double contours and breath/music/telepathy marks. Special marks beyond the telephone example are unit-tested, not yet validated as story treatments.
- Measured text wrapping, CJK punctuation boundary handling, explicit newline preservation, missing-glyph checks and optional frozen-text verification. No automatic text rewriting or font shrinking.
- Speech, thought, shout, whisper, weak, electronic, caption and SFX presets. These are starting styles, not an exhaustive voice taxonomy.
- Curved speech tails, thought dots, angular electronic tails; TV contours, clipped border-butting, off-panel edge tails and hidden-source squinks. Same-speaker curved joins allow explicit interruption sequences with an inspection warning.
- Polygon foreground masks with hidden-text checks; floating captions. Hollow SFX, stepped depth, arced baselines and per-character scale/position/rotation retain editable text.
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

No image understanding, face detection, automatic story inference, arbitrary path editing, text-to-path export, PDF/CMYK/prepress certification, perspective lettering or advanced typography shaping. Horizontal CJK and simple Latin are the tested text domains; bidirectional/complex scripts, emoji clusters and vertical typesetting need further work.

Bounding-envelope checks are conservative. They can report false positives and cannot establish visual acceptance. Candidate placement is greedy, does not optimize the entire page and does not infer character identities. A clean report still requires inspection at reading size. SVG text may reflow visually if the receiving application substitutes fonts.

## Development

```sh
python -m pytest
COMIC_LETTERER_RENDER_TEST=1 python -m pytest
```

The optional second command requires Chromium and exercises real PNG output. Use `TMPDIR` and pytest `--basetemp` if your project requires generated files on a separate volume.

Implementation, synthetic examples and the Echo Station story are original. Echo Station art was generated with an image tool; no exact backend model identity is claimed. Public teaching references are acknowledged in the coverage document; no third-party application code, tutorial illustrations, commercial fonts or production comic artwork are included. MIT license applies to this repository's original code and examples; it grants no rights to external fonts or artwork.

### v0.7 全书修订与600px剧情阅读

`book-revise` 将带来源哈希、旧值和理由的计划落实为新副本，同时生成修订前后完整漫画对照。四页中英文《最后一张票》实际改为600px阅读版，保留原文/原画并修复重排后的溢出和声源问题。见 [实际验证](docs/v07-validation.md) 与 [修订契约](docs/contract.md#book-revisions)。
