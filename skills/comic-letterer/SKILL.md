---
name: comic-letterer
description: Use the independent Comic Letterer Python CLI to letter existing comic artwork or create editable lettering specimens from exact Unicode text, explicit sound sources and panel coordinates. Prepare JSON, select supported voice styles, resolve layout reports and inspect reading-size output.
---

# Comic Letterer

Use the program for repeatable geometry and checks. Make story, reading and style decisions from the actual script and artwork. This skill is for lettering, not generating or changing characters, backgrounds or dialogue.

Locate the installed `comic-letterer` command or its source checkout. Read [workflow and decisions](references/workflow.md) when preparing a page; read the repository's `docs/contract.md` for exact fields and `docs/coverage.md` before promising an unfamiliar technique. The bundled skill does not install the Python package or fonts automatically.

Preserve approved text byte-for-byte, including punctuation; set `expected_text` when a freeze is available. Obtain final crop, reading direction/width, font, panel IDs, speakers, mouth/head/device anchors and protected regions. Mark unknown source positions as unresolved rather than guessing from character names. Keep local project storage requirements and original art intact.

Choose `kind` from the sound in the story. Ordinary speech remains speech; a dramatic image alone does not justify a shout, monster voice or invented SFX. Separate caption sources and keep thoughts distinct from spoken dialogue. Do not silently substitute a supported shape for an unsupported requested effect.

Run `check`, inspect issues, adjust position/box/padding or explicit candidates, and render. Keep text and font size fixed while solving space where possible. Confirm both exit status and report. A report with layout errors is diagnostic output, not finished work; a clean report still needs visual inspection at the requested reading size.

Inspect speaker ownership, reading order, protected faces/props, contour fit, tail roots, connector joins and SFX legibility. Retain JSON, editable SVG, report and master/reading PNGs. Record what was actually viewed, remaining issues and external font dependence. Never equate automated checks with narrative or user acceptance.
