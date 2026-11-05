# Decisions and execution

## Before geometry

Record each item as: panel, exact words, speaker/source, sequence, narrative purpose, voice kind and protected subject. Use established book style. If only lettering is authorized, keep panel crops and artwork fixed. Work from final page-global coordinates, not uncropped panel coordinates.

Use speech for a normal voice; thought for unspoken thinking; shout only when the performance supports it; whisper and weak describe different situations; electronic points to the transmitting device. Caption is a container, so record whether the source is a location/time note, narrator, internal monologue or editor. The schema does not enforce those caption subtypes.

SFX represents an actual sound event. Its placement and size should clarify the event without obscuring its cause. Punctuation and language belong to the approved text; do not import English capitalization or letter-I conventions into Chinese. Preserving silence may be the right decision.

## Rhythm and placement

Lay out actual words before committing the balloon size. Start with stable typography and enough space. Set `breaks` to character offsets at phrase boundaries; this changes layout without changing the original string. Balanced flow optimizes lengths and punctuation costs but cannot know that a Chinese noun should stay together. Inspect and correct those boundaries.

Join consecutive utterances from the same speaker only when they form an intended sequence. Put the identifying tail on the first balloon. For A1 → B1 → A2, `allow_interruption: true` and `join_curve` can route a bridge above the interruption. The compiler retains an inspection warning. Keep the interruption tail clear of both the first tail and the bridge; revise placement if needed. Check order by reading the whole page without item numbers. `direction` affects a heuristic, not narrative understanding.

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

Telepathy decorations, music baselines, breath marks, perspective signs, a dedicated decorative-title workflow, true bold/italic font runs, arbitrary glyph distortion and prepress output require another tool or future implementation. Choose those techniques on story grounds, then disclose the implementation gap. Never describe an indexed tutorial as tested software support.

## Local editor

```sh
comic-letterer edit page.json --font /path/to/dialogue.ttf \
  --display-font /path/to/display.otf --background /path/to/art.png \
  --out /path/to/new-output
```

Open the printed loopback URL. Drag the selected box, blue resize point, green source point or purple join control. Original text with `expected_text` is locked on the client and server. Use the separate line arrangement and emphasis controls. Advanced item JSON exposes style parameters. Save creates a new draft; export creates a new folder. Reload resumes the last save in that session; restarting requires the saved JSON. Do not present a diagnostic export as an accepted page.

## Delivery record

Record actual font family/index/hash, master and reading sizes, CLI result, image inspection and remaining dependencies. Inspect enlarged joins and the full reading-size page. Check exact source text and unchanged art; font substitution can invalidate SVG appearance. Preserve the editable master before making any downstream print conversion. Obtain actual printer specifications when a print deliverable is requested; screen PNG is not press certification.
