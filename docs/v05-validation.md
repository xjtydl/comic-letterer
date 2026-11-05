# v0.5 — requested decorative lettering verified in a narrative

The requested mechanical dashed, sawtooth, flame, scroll and dropped-initial operations are implemented, exposed in the editor, and reviewed on the complete original six-panel **The Lightkeeper / 守灯人** story. This closes these five requested operations at implementation/test/assistant visual-review level; it does not claim user approval or completion of all B modules.

## Sources and original implementation

- [Comicraft: Dashed Iron Man Balloons](https://balloontales.com/dashed-iron-man-balloons/): three overlaid strokes with a broken middle stroke and a notched oval. The program builds its own paths and configurable band/dash/gap/notch parameters; this is different from ordinary whisper dashes.
- [Comicraft: Sawtooth Balloons](https://balloontales.com/sawtooth-balloons/): asymmetric points, curved flame cusps and keeping point density sensible when resizing. The implementation resamples an ellipse by arc length and recomputes tooth count. Straight segments and curved cusps remain distinct constructions.
- [Comicraft: Tattered Captions](https://balloontales.com/tattered-captions/) mentions scroll ends in its book. That book page was not obtained. The bounded roll shapes, seams, shade and safe text rectangle here are an original construction, not a claimed reproduction of paid instructions.
- [Blambot: Drop Caps / Decorative Caps](https://blambot.com/pages/comic-book-grammar-tradition): enlarged/decorated caption initials are a stylistic choice. The program adds actual font metrics and wraparound; Chinese and Latin are separately checked.
- Blambot Better Letterer card 016 informs density checks; the existing OCR-versus-visual-review distinction remains in the source inventory.

## Narrative evidence

See [page plan](v05-page-plan.md). The page moves from a failed lighthouse through a robot's warning, discovery of a trapped flame, the keeper's urgent intervention, silent rescue, and a restored guiding light. Each effect has a source and narrative role:

| Operation | Actual story use | Evidence |
|---|---|---|
| Mechanical multi-stroke contour | Panel 2 robot's warning | Three editable paths; blue-eyed robot remains visible; tail attributed to its speaker |
| Sawtooth contour | Panel 4 urgent “等等！先断电！” | Straight asymmetric teeth, distinct short identifying tail; human face and acting hands unobscured |
| Flame contour | Panel 3 living flame's plea | Curved orange-brown cusps, clear tail toward the trapped flame; not a copied loud-shout outline |
| Scroll | Panel 1 story narration | Curled/shaded sides with text kept out of fold regions |
| Dropped initial | Panel 1 Chinese “那” and English “T” | Real serif fonts; first two lines reserve initial width, English third line returns to full width; every source character retained once |

Both complete 900×1350 reading pages were viewed after correction. The unchanged artwork remains 1024×1536. Silent panel 5 retains its visual action without added words/effects. Final ordinary speech returns to an organic contour, providing a quieter resolution.

The drawings establish rescue and restored light; the lever's precise electrical state is not independently verified by its drawn orientation. This lettering acceptance is not a claim of complete machinery/space-continuity evaluation.

## Corrections retained

1. Chinese “忽然” was split by an authored break; moved the break without editing text.
2. Flame bubble touched the protected lamp cap; moved/resized its shell. A root-angle/curve combination gave a thin or reversing tail; restored a direct, readable source route by changing placement and tail settings.
3. Shout tail was visually lost among teeth; narrowed/increased the shell height and changed the source clearance, preserving font size and wording.
4. English final dialogue had one overly long line; rebalanced its two lines, keeping the source string and size.
5. Browser test originally compared SVG numeric strings `18` and `18.0`; corrected the assertion to numeric comparison. No product failure was hidden by that test change.

NAS version directories retain first/revised/diagnostic outputs. The final deliverables are `v05/story/zh-final` and `v05/story/en-final`. Earlier `story/final` is an intermediate diagnostic directory, not the accepted result; use the explicitly language-named final directories.

## Automated/interaction checks

Geometry tests check density across 1×/2×/3× sizes, bounded paths, distinct cubic versus straight constructions, three mechanical stroke layers and invalid/conflicting parameters. Initial tests check real wraparound, combining marks, exact text, explicit breaks, safe fold regions and small-caption overflow. Browser integration edits every new shape, saves/reloads a scroll with an initial, and exports PNG. Existing tests retain frozen-source and export coverage.

126 tests passed after completing these five operations. After D04 and parameter-validation coverage, the final local suite passed all **135 tests** with Chromium enabled (49.90s). The separately installed 0.5.0 wheel reproduced both Chinese PNG files byte-for-byte, reproduced the two-page book report, and its live editor was inspected at reading size with scroll/initial controls visible. Release CI results are linked from the release and project delivery record.

## Next module started only after these checks: D04

`book-check` compares actual page metadata against explicit house rules. It reports exact field mismatches, documented exceptions with exact values/reasons, unused rules and stale exceptions. It never rewrites a page. The actual two-page Echo Station example checks ordinary dialogue and retains two explicitly documented 25px closing-dialogue exceptions. Those exceptions are not user approval. A separate altered-copy probe verifies that a new 26px override is caught.

This is metadata consistency, not font licensing, optical judgment, drawing continuity or whole-book production. OpenType controls, per-line width, arbitrary hand-edited paths and broader voice/story coverage remain separately tracked.
