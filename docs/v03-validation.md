# v0.3 actual-page validation

2026-11-05. Scope: priorities 1–3 from the tutorial gap review — measured typography, source geometry and narrative semantics. This is developer inspection, not user acceptance of a production book.

## Continuous Chinese story

Echo Station page 1 retains all ten original strings and exact artwork. Improved source tails are visible at 900px reading width; the caretaker's second connected balloon now owns its identifying tail. Words use an actual emphasis face at the same size.

New page 2 continues the original woman, caretaker and kitten into the station office: arrival, phone request, reassurance, then a box for the night. Four panels. Art SHA-256: `6c9ee6186ee0e2530e8d3aae993b9d8a86ef254342b7b5a3a4001838a7466cdf`. The image tool did not expose its backend model identity. Time and inner captions have explicit types; the distorted phone voice has a rough contour/tail pointing at the receiver. Faces, hands, receiver and kitten are protected.

Final local fonts: Heiti TC Light body face 0; existing Noto Sans CJK SC Black (weight 900) for stronger words; Songti SC Regular face 6 for captions. A Heiti Medium trial was inspected and its metadata showed weight 400, so final strong emphasis uses Noto Black. The initial Songti Black caption was too heavy and was changed to Regular. Font roles are aliases; the supplied file determines the real face. No font files are redistributed.

Both pages have zero report issues. Source-image bytes in SVG and frozen strings match their inputs. No private book asset or accepted production page was changed.

- [Page 1](https://github.com/xjtydl/comic-letterer/releases/download/v0.3.0/echo-station-page1.png)
- [Page 2](https://github.com/xjtydl/comic-letterer/releases/download/v0.3.0/echo-station-page2.png)

## Real italic / bold-italic edition

The separately authored English page 2 uses actual Arial regular/bold/italic/bold-italic files. Telephone reply and inner caption use italic; cardboard box uses bold; tonight uses bold-italic without resizing. Initial phone text touched its contour and failed overflow checks. Three-line phrasing plus a larger balloon resolved it without removing words or shrinking type. Final report has zero issues, and actual reading PNG was inspected.

[English page](https://github.com/xjtydl/comic-letterer/releases/download/v0.3.0/echo-station-page2-en.png)

## Editor and tests

87 local tests passed with Chromium enabled. New tests cover real font metadata and per-role subsets, spacing/scale, phrase boundaries, source gaps, independent tails, later-balloon attribution, style resolution, caption identities, voice paths, ink-edge/short-tail warnings and fixed-word/fixed-size contour fitting. Existing raster and frozen-word checks remain enabled. A compatibility test verifies inherited font roles in older SVG files. The built wheel was installed separately and compiled page 2 outside the source checkout with zero issues; bundled editor HTML was present.

Browser interactions exercise selected-phrase protection, tail width/curve, fit, save and reload, in addition to drag/undo/redo/export. An early screenshot captured the artwork still loading; readiness now waits for image decode and fonts. The corrected screenshot verifies natural artwork width 1086. [Editor](https://github.com/xjtydl/comic-letterer/releases/download/v0.3.0/editor.png).

## Source alignment and limits

[Word Arrangement](https://balloontales.com/word-arrangement/) informs deliberate breaks, real emphasis faces and text-first fitting. [Blambot grammar](https://blambot.com/pages/comic-book-grammar-tradition) informs source/caption distinctions. [Rough Balloons](https://balloontales.com/rough-balloons/) informs matching roughness on contour and tail. Algorithms are original.

Rough telephone speech has narrative evidence. Breath/music/telepathy marks and double outlines have executable/unit coverage but no complete narrative acceptance claim. Singing adds a music-note mark; wavy singing baselines remain missing. Phrase protection is authored, not NLP segmentation. Ink-edge checks require manual polylines; fitting is a bounded local search. Styles can be reused between pages, but a central book manager is not present.

Title/perspective effects, full script/page creation, complex Unicode shaping and print output remain later work. This release does not claim full coverage of either website.
