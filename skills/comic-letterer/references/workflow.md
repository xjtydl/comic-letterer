# Decisions and execution

## Before geometry

Record each item as: panel, exact words, speaker/source, sequence, narrative purpose, voice kind and protected subject. Use established book style. If only lettering is authorized, keep panel crops and artwork fixed. Work from final page-global coordinates, not uncropped panel coordinates.

Use speech for a normal voice; thought for unspoken thinking; shout only when the performance supports it; whisper and weak describe different situations; electronic points to the transmitting device. Caption is a container, so record whether the source is a location/time note, narrator, internal monologue or editor. The v0.1 schema does not enforce those caption subtypes.

SFX represents an actual sound event. Its placement and size should clarify the event without obscuring its cause. Punctuation and language belong to the approved text; do not import English capitalization or letter-I conventions into Chinese. Preserving silence may be the right decision.

## Rhythm and placement

Lay out actual words before committing the balloon size. Start with stable typography and enough space; let deliberate phrases guide manual source line breaks only when those breaks are authorized. Otherwise retain the original and use automatic soft wrapping.

Join consecutive utterances from the same speaker only when they form an intended sequence. Put the identifying tail on the first balloon. A1 → B1 → A2 needs separate clear attribution in v0.1; complex interruption connectors are unsupported. Check order by reading the whole page without item numbers. `direction` affects a heuristic, not narrative understanding.

Mark heads, hands, key props and important sightlines as protected rectangles. Candidate placement searches a small grid; inspect its result. Fix a distant balloon before lengthening a tail. Source anchors denote mouths, heads for thoughts, or actual devices; tails should leave a readable gap. A fixed fraction alone cannot prove ownership.

## Practical commands

```sh
comic-letterer check page.json --font /path/to/licensed-font.ttf --strict
comic-letterer render page.json --font /path/to/licensed-font.ttf \
  --out /path/to/new-output --background /path/to/unlettered.png --png --strict
```

`render` may write diagnostic outputs on exit 1. Read `report.json`. Resolve `missing_glyph` by choosing an appropriate licensed font, not silently replacing characters. Resolve overflow by reflow, permitted relocation or enlarging the box; do not delete dialogue. If constraints cannot fit, describe the specific conflict and present the necessary creative tradeoff.

## Unsupported techniques

Border-butting, squinks, masks behind characters, telepathy decorations, music baselines, breath marks, perspective signs, decorative titles, mixed emphasis, true hollow SFX, per-glyph distortion and prepress output require another tool or future implementation. Choose those techniques on story grounds, then disclose the implementation gap. Never describe an indexed tutorial as tested software support.

## Delivery record

Record actual font family/index/hash, master and reading sizes, CLI result, image inspection and remaining dependencies. Inspect enlarged joins and the full reading-size page. Check exact source text and unchanged art; font substitution can invalidate SVG appearance. Preserve the editable master before making any downstream print conversion. Obtain actual printer specifications when a print deliverable is requested; screen PNG is not press certification.
