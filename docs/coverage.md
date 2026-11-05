> v0.7增量：全书显式批量修订与前后完整漫画对照已实现，实际四页600px中英文剧情验证，175项测试通过；见 [v07验证](v07-validation.md)。后文保留早期能力节点。

# Latest v0.6 narrative pass

[The Last Ticket actual-page evidence](v06-validation.md) covers the remaining type/path/voice operations, projective materials and authored handwriting. Independent stacking and border crossing were added and visually checked before extending D04 to real book proofs. Earlier tables remain historical; consult WORK_INDEX for present limits.

# Latest v0.5 increment

Mechanical three-stroke contours, arc-length sawtooth/flame density, scroll captions and measured Chinese/Latin dropped initials are implemented, editable and checked in a complete narrative. [Actual evidence](v05-validation.md). After these five operations passed, D04 gained `book-check` for explicit read-only style rules. Remaining broader gaps are kept in [the work index](WORK_INDEX.md).

# Latest v0.4 increment

Measured dialogue bounce/wave and emphasis baseline shifts, organic speech and tattered captions are implemented. See [actual page evidence](research/IMPLEMENTATION_LEDGER.md) and [complete scope](WORK_INDEX.md). This supersedes older “unsupported” rows for these specific operations; other gaps remain.

# Tutorial coverage and implementation boundaries

> 2026-11-05 expanded scope: [two-site discovery inventory and 45-module comic-creation roadmap](research/TWO_SITE_MASTER_SCOPE_20261105.md) now includes composition, drawing/color workflow, design, production and AI learning/evaluation. The roadmap distinguishes source discovery, reading, implementation and actual-page evidence; it does not change the v0.3 implementation claims below.

**Current v0.3:** real-font runs, tracking/scaling, manual phrase protection, text-first box fit, independent tails/later attribution, caption types and reusable styles are implemented and tested on continuous Chinese pages plus an English treatment. Rough telephone speech has actual-page evidence; breath/music/telepathy marks and double outlines are only executable/unit-tested. Wavy singing baselines remain missing. See [v0.3 evidence](v03-validation.md). Earlier tables are historical snapshots.


**v0.2 update:** see the current implementation and visual evidence table immediately below. The v0.1 ledger farther down is historical and documents what was absent at that release.

## Current v0.2 evidence

| Tutorial method | Executable implementation | Actual validation | Remaining boundary |
|---|---|---|---|
| Word Arrangement | Independent break offsets, balanced flow, alignment, measured size emphasis | Echo Station final reassurance; private page semantic breaks; source-preservation tests | No language-model phrase inference or real bold/italic runs |
| Making Word Balloons / Butting Balloons | TV contour, edge clipping, text-safe border placement | Echo Station panel 2 off-panel speech; edge/overflow tests | No automatic crop choice |
| Creating Tails and Joins / Blambot grammar | Curved joins, explicit interruption opt-in, edge tails, hidden-source squink | Full interruption treatment, same-speaker bridge and behind-door kitten; collision regression | Human reading order required; first balloon owns the identifying tail |
| Layer Method / Floating Text | Separate layers, floating caption, polygon foreground masks | Roof beam over balloon shell in alternate story; raster mask test | Masks are manually specified; no image segmentation |
| Multiple Outline SFX / Fighting Words / Curved Type | Hollow fill, depth offsets, arced baseline, per-character scale/rotation, display font | Door impact in the real story; hollow raster exposes original background | No perspective warp, weathering, font design or 3D lighting |
| Preparing Files for Output | Editable SVG, source/report, two direct vector PNG sizes, local editor export | Drag → undo/redo → save → reload → export browser test | No CMYK, PDF, font outlines or printer certification |

Newly consulted public texts on 2026-11-05: [Butting Balloons](https://balloontales.com/butting-balloons/), [Curved Type](https://balloontales.com/curved-type/) and [Fighting Words](https://balloontales.com/articles/tutorial/part2.html). Their practical principles were applied: crop at panel boundaries with safe words, use deformation for rhythm while preserving legibility, build sound character from varied glyph skeletons and outlines. These are original implementations, not copied Illustrator procedures or code. No blanket claim that every site technique is complete.

See [v0.2 actual-page evidence](v02-validation.md) and [contract](contract.md).

## Historical v0.1 scope


Research date: 2026-11-05. This is a bounded, expanding ledger, not a claim to have read either entire site, bought their books, inspected every illustration, or implemented all comic knowledge. “Read” below means the public article text was inspected in this development session. Illustration-only details are not claimed as verified.

The program's algorithms, JSON contract, geometry and synthetic examples are original. Tutorials are teaching references, not code sources. Historical Illustrator menus, point sizes and print recipes are not current universal specifications. Chinese line-breaking rules and numerical defaults are this project's adaptations.

## Research ledger

| ID | Official public source | Research | Program / Skill outcome | Test status and remaining gap |
|---|---|---|---|---|
| B01 | [Comic Book Grammar & Tradition](https://blambot.com/pages/comic-book-grammar-tradition) | Voice, tail, join, caption, SFX and text convention sections read | Eight initial presets; semantic selection in Skill | Preset geometry, source gaps and reading checks tested; many variants below remain absent |
| B02 | [Comic Script Basics](https://blambot.com/pages/comic-script-basics) | Text read | Explicit panel/item/order/speaker; freeze check; distinguish script from art directions | Structural and text tests; no Word importer or emphasis runs |
| B03 | [Original Art Dimensions](https://blambot.com/pages/original-art-dimensions-for-american-standard-comics) | Definitions read; diagram measurements not extracted | Skill separates canvas, reading and print specs | Screen dimensions tested; trim/bleed/prepress unimplemented |
| C01 | [Making Word Balloons](https://balloontales.com/making-word-balloons/) | Text read | Measured text before contours, independent art | Fit and layering tests; no TV contour or border-butting |
| C02 | [Creating Tails and Joins](https://balloontales.com/creating-tails-and-joins/) | Text read | Curved tapered tails and explicit same-speaker joins; protected regions | Attribution metadata, source gap, connector tests; curved joins and interruption connectors absent |
| C03 | [The Layer Method](https://balloontales.com/the-layer-method/) | Text read | Separate outline, connector and fill geometry | SVG structure and rendered specimen inspected; no cross-editor native-layer certification |
| C04 | [Glossary of Lettering Terms](https://balloontales.com/the-comicraft-glossary-of-lettering-terms/) | Core terms and linked technique vocabulary read | Voice versus geometry distinction; Skill decisions | Scope inventory; no blanket “glossary implemented” claim |
| C05 | [Multiple Outline SFX](https://balloontales.com/multiple-outline-sfx/) | Text read | Ordered outline layers with one editable text source | Rotated specimen and outline/protection tests; no 3D offsets, per-glyph transforms or print trapping |
| C06 | [Word Arrangement](https://balloontales.com/word-arrangement/) | Text read | Centered measured lines and retained manual LF; font-size stability | Wrapping and overflow tests; semantic line balancing and inline emphasis absent |
| C07 | [Preparing Lettering Files for Output](https://balloontales.com/preparing-lettering-files-for-output/) | Text read; historical EPS workflow identified | Preserve editable master; separate render outputs | JSON reload, SVG parse and real PNG tests; EPS/outline/CMYK unsupported |
| C08 | [Floating Text & Captions](https://balloontales.com/floating-text-captions/) | Text read | Skill recognizes negative-space composition | No dedicated floating-caption kind or masking; unimplemented |
| C09 | [Rough Balloons](https://balloontales.com/rough-balloons/) | Text read | Layer construction informs seam inspection | Weak preset is a deterministic wave, not full roughening; random rough tail workflow unimplemented |

## Technique inventory

This inventory intentionally includes work beyond balloons. A named tutorial or concept is not an implementation claim.

| Technique family | Current executable support | Human/Skill decision | Still to build / research |
|---|---|---|---|
| Ordinary voice / thought / shout / whisper / weak / device | Presets, tails/dots, font metrics | Select from script sound | Wider stylistic range, independent shape override |
| Monologue, time/place, editorial, spoken caption | One caption rectangle; source metadata | Identify narrator and voice | Caption subtypes, loose text, drop caps |
| Burst variants, rough/icy/telepathic voices | None beyond initial shout/weak | Establish book vocabulary | Dedicated geometry; no inferred supernatural voice |
| Off-panel and behind-door sound | Explicit rejection of off-panel mode | Identify actual hidden source | Edge tails, curved off-panel tails, squinks |
| Same-speaker sequence and interruption | Consecutive speech/whisper join only | Rhythm and first attribution | Curved connectors, interruption paths, multiple speakers |
| Overlap, border-butting, breaking border, masks | Simple joined overlap; out-of-panel checks | Intentional composition versus tangent | Clipping, crop-safe text, art masks, shared edges |
| Cough/breath/singing/whistling | Exact text can be supplied | Decide whether sound occurs | Breath marks, music symbols as decorations, wavy baselines |
| Emphasis and textual conventions | Exact text, no editorial rewriting | Language-specific punctuation and emphasis | Mixed font runs, bold/italic actual-font measurement |
| SFX outline/solid/rotation | Multi-outline live Unicode + rotation | Event, loudness, duration, placement | Hollow/3D/weathered/curved/per-glyph effects |
| Titles, credits, logos, decorative lettering | Not a dedicated subsystem | Hierarchy and narrative tone | [Title Deeds](https://balloontales.com/articles/tutorial/part3.html) indexed, not re-read/tested here |
| Action-driven sound design | Basic SFX | Sound source and story beat | [Fighting Words](https://balloontales.com/articles/tutorial/part2.html) indexed, not re-read/tested here |
| Signs, letters and other in-world text | None | Accurate text tied to its physical surface | Perspective text and surface anchors |
| Panel sequence, page turns, silent beats | Explicit panel/order input; crude warning | Full sequential-story judgment | No automatic plot/layout inference |
| Halftone, aging, speed/impact lines | None | Art direction; sound separate from motion | [Comic Book Look](https://balloontales.com/giving-artwork-the-comic-book-look/) indexed; drawing effects outside core v0.1 |
| Font design and crossbar-I tradition | Local font loading/cmap checks | Language and licensing | Font creation unimplemented; no copied font packages |
| Source import, editability and delivery | JSON, editable SVG, RGB PNG | Inspect actual output and dependencies | GUI, rich script import, path conversion, PDF, printer profiles |
| Advanced type / internationalization | Horizontal Chinese/simple Latin tests | Choose appropriate language conventions | Grapheme-aware UAX line breaks, bidi, vertical type, complex shaping |
| General tutorials, careers, font installation, videos | None | Consult as relevant | Full site discovery and illustrated-tip review remain open |

## Release stages

- **v0.1:** independent engine/CLI, synthetic specimen, tests, contract and companion Skill. Capability claims limited to the tables above.
- **Next geometry stage:** border/hidden-source semantics, safe masks, configurable curved joins and more exact collision checks. Add regression cases before claiming support.
- **Next type stage:** inline emphasis, semantic/manual break hints without changing frozen strings, richer SFX and display lettering.
- **Later integration:** GUI or thin node adapter, broader text shaping and printer-specific export. No shared production service changes are prerequisites.

For every added method: record source and actual reading scope, implement an independently designed operation when it can be deterministic, test observable behavior, render a representative example and update the ledger. Keep narrative decisions in the Skill; do not encode one project's look as universal comic grammar.
