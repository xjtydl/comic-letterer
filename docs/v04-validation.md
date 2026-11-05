# v0.4 validation — expressive text inside a narrative page

This increment addresses B02, B04 and B08 within the [45-module scope](research/TWO_SITE_MASTER_SCOPE_20261105.md). It does not close the lettering phase or the full comic-production roadmap.

## Methods and page intent

Sources: [Comicraft Bouncy Text](https://balloontales.com/bouncy-text/), [Tattered Captions](https://balloontales.com/tattered-captions/), and Blambot [Better Letterer](https://blambot.com/pages/lettering-tips), especially cards 019 and 014. Public texts/OCR were reviewed; GIF examples could not be fetched by the research tool, and are not marked visually reviewed. The deterministic paths and waveform are original implementation choices.

Consulted comic-production-entry, american-comic-layout, comic-visual-language, comic-lettering and comic-letterer. Layout and artwork remain the approved independent Echo Station page. Actual choices:

- Preserve the four-panel sequence: arrive with rescued cat → ask for a box by telephone → reassure cat → caretaker brings shelter.
- Keep time note separate from the woman's inner caption.
- Small 2.5px wave belongs to the distorted voice **from the receiver**, not the caretaker's normal speech.
- Gentle organic speech suits reassurance and the closing invitation. A -2px emphasis shift remains restrained.
- Tattered inner-caption frame echoes the old station's paper/wood material. The time note stays plain to distinguish its role.
- Do not add singing, telepathy, screaming, new SFX or invented words to force more features into this quiet story.

## Observed issue and correction

The first expressive export flagged `home` as text overflow: the organic contour's safe envelope was smaller than the old TV shape. Its box changed from `[460,1040,175,98]` to `[450,1036,190,112]`. Text, font size and sound-source point were retained. The final report has zero issues.

The complete 900×1200 page was viewed before and after correction. Dialogue remains readable, faces/cat/phone remain unobscured, the distorted reply points to the receiver, and the final balloon points toward the caretaker. The natural contour is subtle; it does not become a monster-voice shape. The paper edge remains secondary to the narrator's text.

All seven item IDs/text/expected_text strings exactly match the original page. The embedded art bytes match SHA-256 `6c9ee6186ee0e2530e8d3aae993b9d8a86ef254342b7b5a3a4001838a7466cdf`.

## Automated and interactive checks

102 tests passed locally with Chromium enabled. Added tests cover actual SVG baseline positions, measured shifted ink bounds, frozen text/input preservation, combining marks, invalid parameter rejection, bounded deterministic paths and organic tail boundary/length. The browser integration test changes the natural contour and wave baseline, saves, reloads and verifies retained settings alongside phrase/tail controls. Existing drag, undo/redo and PNG export tests continue to pass.

Portable Skill and production-entry Skill passed quick validation. Wheel installation, CI and release evidence are recorded in the release and local delivery log after completion.

## Limits

Wave has this actual narrative-page review; bounce has automated coverage, not a singing/drunkenness story acceptance. Other special voices still need appropriate full narratives. Complex-script shaping/OpenType controls, line-specific width, mechanical multilayer balloons, sawtooth/flame density, scrolls/drop caps, full-book consistency and print delivery remain open. No user visual approval or AI training is inferred from self-review.
