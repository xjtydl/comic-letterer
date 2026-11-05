# Decisions and execution

## Before geometry

Record each item as: panel, exact words, speaker/source, sequence, narrative purpose, voice kind and protected subject. Use established book style. If only lettering is authorized, keep panel crops and artwork fixed. Work from final page-global coordinates, not uncropped panel coordinates.

Use speech for a normal voice; thought for unspoken thinking; shout only when the performance supports it; whisper and weak describe different situations; electronic points to the transmitting device. Caption is a container, so record whether the source is a location/time note, narrator, internal monologue or editor. Use explicit caption_type for the supported semantic subtypes; inner/spoken captions require a speaker.

SFX represents an actual sound event. Its placement and size should clarify the event without obscuring its cause. Punctuation and language belong to the approved text; do not import English capitalization or letter-I conventions into Chinese. Preserving silence may be the right decision.

## Rhythm and placement

Lay out actual words before committing the balloon size. Start with stable typography and enough space. Set `breaks` to character offsets at phrase boundaries; this changes layout without changing the original string. Balanced flow optimizes lengths and punctuation costs but cannot know that a Chinese noun should stay together. Inspect and correct those boundaries.

Join consecutive utterances from the same speaker only when they form an intended sequence. Usually identify the voice on the first balloon; v0.3 can put it on a later connected balloon with explicit `tail.visible` settings if that better fits the actual source. For A1 → B1 → A2, `allow_interruption: true` and `join_curve` can route a bridge above the interruption. The compiler retains an inspection warning. Keep the interruption tail clear of both the first tail and the bridge; revise placement if needed. Check order by reading the whole page without item numbers. `direction` affects a heuristic, not narrative understanding.

Mark heads, hands, key props and important sightlines as protected rectangles. Candidate placement searches a small grid; inspect its result. Fix a distant balloon before lengthening a tail. Source anchors denote mouths, heads for thoughts, or actual devices; tails should leave a readable gap. A fixed fraction alone cannot prove ownership.

## Practical commands

```sh
comic-letterer check page.json --font /path/to/licensed-font.ttf --strict
comic-letterer render page.json --font /path/to/licensed-font.ttf \
  --out /path/to/new-output --background /path/to/unlettered.png --png --strict
```

`render` may write diagnostic outputs on exit 1. Read `report.json`. Resolve `missing_glyph` by choosing an appropriate licensed font, not silently replacing characters. Resolve overflow by reflow, permitted relocation or enlarging the box; do not delete dialogue. If constraints cannot fit, describe the specific conflict and present the necessary creative tradeoff.

## Extended techniques

Use `butt` only for named panel edges; text must remain inside the frame. `off_panel` requires an external source and sends the tail to the border. `source_mark: squink` marks a known hidden source such as a closed door. Do not point a hidden-source mark at an unrelated visible character.

Foreground masks are explicit page polygons targeted to item IDs. Follow a visible foreground edge and keep every glyph clear. The Echo Station alternative follows a roof beam over a balloon shell; the source art is unchanged.

For loud metallic impact, use a heavy display font with `hollow`, multiple outlines, small depth offsets and restrained per-glyph size/rotation. Thin body fonts with thick outlines can visually close the hollow interior. Inspect the actual door impact and reading PNG. Arc/glyph transforms are separate from range emphasis; use glyph scale for that SFX mode.

## Unsupported techniques

Telepathy/music/breath decorations exist, but still need their own narrative validation. Dialogue bounce/wave baselines and organic/tattered contours exist in v0.4. Perspective signs, a dedicated decorative-title workflow, arbitrary glyph distortion and prepress output remain future implementation. Choose those techniques on story grounds, then disclose the implementation gap. Never describe an indexed tutorial as tested software support.

## Local editor

```sh
comic-letterer edit page.json --font /path/to/dialogue.ttf \
  --display-font /path/to/display.otf --background /path/to/art.png \
  --out /path/to/new-output
```

Open the printed loopback URL. Drag the selected box, blue resize point, green source point or purple join control. Original text with `expected_text` is locked on the client and server. Use the separate line arrangement and emphasis controls. Advanced item JSON exposes style parameters. Save creates a new draft; export creates a new folder. Reload resumes the last save in that session; restarting requires the saved JSON. Do not present a diagnostic export as an accepted page.

## Delivery record

Record actual font family/index/hash, master and reading sizes, CLI result, image inspection and remaining dependencies. Inspect enlarged joins and the full reading-size page. Check exact source text and unchanged art; font substitution can invalidate SVG appearance. Preserve the editable master before making any downstream print conversion. Obtain actual printer specifications when a print deliverable is requested; screen PNG is not press certification.

## v0.3 decisions from real pages

Configure real font files with `--font-map` before choosing emphasis roles. Chinese validation uses Heiti body, Noto Black for stronger words, and Songti Regular for captions; English uses Arial regular/bold/italic/bold-italic. These are local choices, not compulsory style or bundled fonts. Do not mechanically italicize Chinese text. Explicit phrase ranges preserve words during reflow; ambiguous semantic breaks still require editorial judgment.

The continuous station-office page distinguishes time caption, inner caption, a caretaker speaking, and distorted speech from a telephone receiver. The first page now gives the later connected balloon the identifying tail. Check the whole sequence at reading width. In the English version, the telephone sentence needed three lines; keep the words and font size, then correct the breaks.

## v0.4 expressive lettering decisions

Use small bounce/wave baseline offsets only for an intended vocal effect. The verified station-office revision uses a 2.5px wave on the distorted receiver, a -2px emphasis shift on the reassurance, subtly organic speech and a tattered inner-caption frame. It preserves every word and the original art. Enlarging the final organic balloon solved a measured overflow without reducing type size.

The editor exposes mode, amplitude, group size and emphasis baseline shift. These are measured effects with glyph bounds; a clean report still needs a reading-size inspection. Wave on this telephone scene is visually reviewed; bounce, song, breath and telepathy are not thereby narratively accepted. The tattered frame is not a scroll or decorative initial.

## v0.5 decorative lettering and book audit

The Lightkeeper story deliberately separates the robot's three-layer mechanical contour, the living flame's curved cusp contour, and the engineer's straight sawtooth shout. The narrator uses rolled parchment with a measured initial; the final reassurance returns to ordinary speech. Do not apply all effects to a quiet scene simply because they are available.

Set `edge.spacing` rather than scaling a fixed small tooth pattern across unrelated sizes. Use the actual caption text before sizing scrolls; curl regions are excluded from text layout. A dropped initial is a separate real-font run, with body rows reserving its width and later rows returning to full width. Count Unicode code points, retain punctuation and spaces, and review Chinese and Latin independently. Read `docs/v05-validation.md` for actual corrections and limits.

Once the requested lettering operations pass their actual pages, use `book-check` for explicit cross-page style rules. Keep legitimate exceptions visible with an exact value and reason; do not erase differences or rewrite source pages to manufacture a clean report. No matching items and obsolete exceptions are warnings. Layout, font-file identity, narrative and visual continuity still need their own checks.

## v0.6 actual-page completion pass

The Last Ticket two-page Chinese/English story verifies authored phrase/row controls, custom/flat paths, cough/telepathy/thought/whisper/weak/singing, original HOME font on the physical sign, restrained projective piano SFX, independent overlapping shells and an intentional border-crossing caption. Lightkeeper supplies a separate full-page double-outline treatment. Read `docs/v06-validation.md`; sources and 45-module states are in `docs/WORK_INDEX.md`. `book-proof` then renders these four pages together and detects both metadata size drift and actual font drift without rewriting them.
