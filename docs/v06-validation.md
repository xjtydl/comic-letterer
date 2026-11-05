# v0.6 — narrative lettering completion pass

This pass follows the user's order: address outstanding balloon/type operations, inspect actual narrative pages, update the 45-module ledger, and only then extend book checking. “Implemented and visually reviewed” is not user acceptance or completion of all possible font/drawing software.

## Actual pages, not specimens

**The Last Ticket / 最后一张票** is an original two-page story. A courier enters an old theatre, coughs in the dust, hears a ghost's mental voice, recognizes a song, sings its ending, and leaves a ticket at dawn. Four panels per page; Chinese and English editions have independently frozen source strings. Both editions use the same unchanged artwork. Layout and methods are in [the page plan](v06-page-plan.md).

| Outstanding operation | Implementation | Actual narrative evidence |
|---|---|---|
| Phrase-safe arrangement | Authored semantic phrase ranges, punctuation boundary suggestions, explicit row widths and 0.9–1.1 row scales | P1 thought initially split 妈妈; corrected break and protected the phrase. P2 weak speech uses two individual row settings. |
| OpenType | Font-supported feature tags are validated and used for Pillow/libraqm measurement and SVG; raster subsets retain alternate glyphs | English P1 title uses actual Arial `liga`/`kern`. Original HOME font exports and tests `kern` and `ss01`; alternate rendering is separately tested, not claimed in projected sign. |
| Language advice | Opt-in zh/en punctuation, first-person I and quote-balance advice; source never rewritten | Chinese ellipsis and English edition retained independently; advisory failures tested on copies. Full semantic interpretation stays with the AI/letterer. |
| Flat/custom contours | Bounded editable cubic segments, control-point handles, actual-boundary tail roots, sampled interior checks | P1 title uses a hand-adjusted shell; whisper and final caption use flat-sided rounded shells. |
| Unverified voice variants | Breath/singing/telepathy marks positioned from actual glyph boxes; thought/whisper/weak use distinct source treatment | P1 cough, ghost voice, thought and whisper; P2 weak speech and singing. Old corner placement made black marks nearly invisible; corrected and added safe-shell checks. |
| Double outline | Existing construction now checked in a full scene, not just a unit fixture | Lightkeeper alternate preserves every word and art pixel. 4px gap was visually weak at reading size; 8px final gap is visibly separate around the urgent shout. |
| Surface lettering / SFX perspective | Convex four-point homography; sampled font outlines, exact hidden Unicode master, transformed ink checks | HOME follows the wooden theatre sign; the final piano note uses a restrained perspective treatment. Complex-script outline shaping is explicitly unsupported. |
| SFX material / event design | Two-color ink gradient, bounded seeded wear; source/event/material/intensity/duration metadata | The final piano note was initially too heavy. Replaced its display face with a thinner narrator face, reduced size and outline; golden sustained note now supports the quiet release. |
| Font creation / handwriting | Original pressure trajectories → glyph contours → TrueType export, kerning pairs and stylistic-set alternate | Five-glyph HOME/h alphabet is used on the real theatre sign. Editable original strokes and generated font are delivered; no commercial font outlines copied. This is a small display alphabet, not a completed general text font family or handwriting recognizer. |

Explicit front/back stacking was also added after the first 160-test checkpoint: P1 whisper overlaps the prior thought shell without merging voices or hiding words. P2 closing narration intentionally crosses the left panel border while every glyph remains within its assigned panel. These are rendered shell/word checks, not disabled collision checks.

Existing Echo Station and Lightkeeper pages remain the evidence for joins, interruptions, border-butting, foreground masking, rough device voices, ordinary tail/source editing, scroll/drop caps, mechanical layers and sawtooth/flame density. They are not reset to “unverified”, nor are unrelated effects forced into the theatre story.

## Corrections and failures retained

- Projected outlines retain hidden live source text. Raster validation initially treated its unused font as a failed font load; hidden sources are now excluded from raster font loading, with a dedicated regression.
- The projective simple-script guard initially rejected the Chinese long dash; the supported punctuation set now includes it.
- Breath/music marks had landed outside the white shell and disappeared against dark art. Positions now derive from measured text; opposing cough marks are mirrored. Text overlap and safe-shell bounds are checked.
- The first thought break split 妈妈; fixed offsets without changing text. The piano SFX used an overly heavy face; the final quieter face better fits the sound.
- The new UI test exposed a real race: a delayed preview response could reset a language value while the user edited another field. Preview refresh now preserves in-progress type fields; explicit commits still refresh them.
- The first custom-control browser test also needed to expand its details section before filling hidden inputs. This test-only correction is distinct from the real UI race above.
- A temporary variable named `bottom` shadowed the SVG bottom-layer object when adding the second voice item. It was renamed; a multiple-item voice regression now covers that state.

## Output and acceptance boundaries

Production files are under the verified NAS `comic-letterer/v06/` output root. Final directories are `story/p1-zh-complete`, `p2-zh-complete`, `p1-en-complete-r2`, `p2-en-complete`, plus `double-outline-r2`. The earlier drafts retain the failures. All four theatre page reports have zero issues; each SVG's exact text and embedded artwork bytes were compared to source. Reading size is 900×1350.

The girl's piano hand and the boy's ticket support the story; this does not certify a complete 3D reconstruction or all continuity dimensions. Chinese/English horizontal text is the tested production scope. Bidi, vertical layout, automatic image segmentation, arbitrary font hinting/family production, broad learned semantic inference and printer certification are not secretly included.

## Source use

- [Blambot grammar](https://blambot.com/pages/comic-book-grammar-tradition): voice, typography and narration choices are conventions with contextual exceptions. New voice scenes check their application; not every tutorial diagram has been visually reviewed.
- [Comicraft font and character usage](https://balloontales.com/font-and-character-usage/): alternate characters and modest width adjustments informed explicit controls. Its old OS shortcuts are not copied as current instructions.
- [Pillow ImageFont](https://pillow.readthedocs.io/en/stable/reference/ImageFont.html): feature-aware metrics require libraqm. The installed fontTools FontBuilder/pen APIs were checked in code; the web FontBuilder page was inaccessible and is not claimed as read.

Numerical bounds, projection, font-building code and Chinese advice are original local engineering decisions, not quotations of an industry standard.

## D04, after the lettering checkpoint

162 tests passed after the lettering/stacking/border work (Chromium enabled, 58.87s). Only then `book-proof` was implemented. Its real four-page bilingual Last Ticket proof covers 20 items, 14 edition/kind rules and actual font hashes, with zero unexplained findings. The generated continuous-reading HTML was opened and visually inspected. A separate copy changes P2 English weak speech to 27px and substitutes the actual body font; it produces exactly `style_drift` and `font_identity_drift`. Originals retain their hashes.

The final complete local suite passes **164 tests** with Chromium (52.41s), including new proof/raster/source-preservation regressions. Release CI and installed-package checks are recorded in the project delivery log. No batch rewrite or automatic editorial acceptance was added.
