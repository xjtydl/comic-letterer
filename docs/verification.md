# v0.1 verification record

2026-11-05. Tested locally on macOS arm64, Python 3.14, Pillow/fontTools, Playwright Chromium. This records observed checks, not universal compatibility or visual acceptance of production pages.

## Automated checks

- **44 tests passed**, including the opt-in Chromium integration test. No skipped rendering test in this run.
- Original baseline first failed because the engine was absent. New boundary/geometry tests were also observed failing before their fixes.
- Coverage includes frozen text, XML escaping, Unicode/whitespace preservation, punctuation wrapping, invalid fields/numbers, missing glyphs, protected areas, candidate selection, source-head tail clearance, joins and interruption rejection, preset construction differences, SFX outlines, reading-size warnings, CLI exit codes, reload and overwrite protection.
- Real PNG test checks vector-to-raster output dimensions at two sizes and visible interior text pixels. It is not OCR or a pixel-perfect cross-platform golden comparison.
- Ruff undefined/unused-import checks passed; companion Skill frontmatter validator passed. Skill content was exercised while preparing the specimen; no independent agent behavioral evaluation is claimed.

## Original specimen

`examples/specimen.json` + `examples/make_specimen.py` create a synthetic style plate. No production comic art, character references or third-party tutorial graphics were used. The geometry and Chinese wording are original examples.

Methods applied: two columns for independent voice comparisons, then a continuous-utterance row; fixed 32px dialogue (21.3px at 800px reading width); explicit source dots; standard speech, thinking, shout, whisper, weakness and device voice tied to their example wording; same-speaker connector with first-balloon attribution; door-creak SFX with two outline layers. This is a specimen, not a story page or an approved production style.

Rendered at **1200×1580** and directly from SVG at **800×1053**, using locally supplied Heiti TC collection face 0. Font bytes are absent from saved SVG/repository. Initial SFX padding caused an overflow and unwanted two-line break; reduced item padding fixed it without changing wording or font size. Final specimen strict report has zero issues.

Actual reading PNG was viewed: Chinese characters and punctuation are visible, voice outlines differ, thought dots taper, whisper dashes remain legible, connector roots do not show internal seams, and the final door-creak text reads on one line. This is a local visual inspection, not an external user acceptance or guarantee across editors/fonts.

## Private diagnostic regression

A separate existing page was adapted outside the repository without modifying its artwork or text. Background SHA-256 matched its declared original; all source text checks passed. The new program reported overflow and protected-area conflicts rather than silently accepting the inherited placement. Its report and images remain private. This regression is not an accepted replacement page and contributes no private assets to this release.

## Packaging and publication checks

A wheel was built on the designated output volume, installed to an isolated target directory, and invoked from outside the source checkout. The installed CLI passed the specimen strict check. Public source files were scanned for private paths, project names, credential patterns and bundled image/font files; no findings. Generated release assets are limited to the wheel, portable Skill archive and original specimen PNG.

## Remaining validation

The initial [GitHub Actions run](https://github.com/xjtydl/comic-letterer/actions/runs/41962367029) passed on Ubuntu with Python 3.10, 3.12 and 3.14, including Chromium rendering. Consult the current run for subsequent commit status. Other SVG editors, Windows, complex scripts, full Unicode line breaking, print profiles and graphical editing workflows have not been certified. README and coverage ledger delimit unsupported features.
