# v0.2 actual comic and editor validation

2026-11-05. This release was developed from actual lettering on a five-panel narrative page, plus a private unchanged-art regression. This records the developer's visual inspection, not user acceptance or print certification.

## Echo Station / 回声站

Original story and original generated artwork, 1086×1448. A woman and station caretaker investigate a sound, cut the power, open a steel door and find a kitten by a bell. Art SHA-256: `43cd2feadbabf4ec5c363d4d997b738fa6bc370649a62d040db57b8228b9fc40`. The image tool did not expose a backend model ID; no specific GPT Image 2.5 identity is claimed.

`examples/echo-station.json` applies a left-to-right five-panel sequence: floating narration, ordinary TV-shaped speech, dashed whisper, panel-butted off-panel reply, same-speaker join, a hollow metallic door impact, and a quiet final reassurance. Faces, hands, door latch, kitten and bell are protected. Words are frozen exactly. The radio visible in the drawing has no invented transmission. Body: locally supplied Heiti TC face 0. Display: separately supplied [Noto Sans CJK SC Black](https://github.com/notofonts/noto-cjk/blob/main/Sans/OTF/SimplifiedChinese/NotoSansCJKsc-Black.otf); fonts are not included in this release.

Master and 900×1200 reading PNGs were rendered directly from SVG and viewed. Findings corrected during production: a source tail too close to a head, an oversized conservative SFX collision envelope, an awkward final phrase break, and a thin body font whose thick outlines visually closed the hollow sound. The final main page has **zero report issues**. The final words “回家” remain together and slightly enlarged. Door-impact glyphs use different sizes/rotations with a modest arch and depth; artwork remains visible inside their stems.

[Reading page](https://github.com/xjtydl/comic-letterer/releases/download/v0.2.0/echo-station-reading.png)

## Interruption and foreground treatment

`examples/echo-station-interruption.json` is a separate authored treatment of the same unchanged artwork, not a rewrite of frozen production dialogue. A hidden kitten call ends at a squink on the closed door. The caretaker begins “我已断电——”, the off-panel woman interrupts “等等！”, and he continues “——先听。”. A curved same-speaker bridge runs over the interruption. A polygon following a roof beam reveals that foreground edge across the upper-left balloon shell without hiding its words.

Full 900px reading output was viewed. Initial attempts exposed actual box/tail conflicts and a conservative false positive from whole-tail envelopes. Moving the interruption and shortening the identifying tail resolved the layout; sampled tail polygons resolved the false collision. Final output has **no errors** and one deliberate `interruption_join` warning. The warning remains because a numerical check cannot certify interrupted reading order. In the inspected image, sequence reads left → middle → right, the first small tail points toward the caretaker, the interruption tail exits left, and the bridge clears the middle balloon.

[Alternate reading page](https://github.com/xjtydl/comic-letterer/releases/download/v0.2.0/echo-station-interruption.png)

## Private regression

The earlier existing-book page was rerendered privately without changing source artwork or any of its five frozen text strings. TV contours and independent phrase breaks resolve the question's overflow. Relocating the final balloon clears the protected head. A narrow caption now breaks between complete short phrases instead of splitting 门环 or 多年来; 一件 remains together in the final balloon. Final diagnostic report has zero issues. This remains a diagnostic comparison, not an authorized replacement of an accepted book page, and none of its images or strings are published here.

## Editor and executable evidence

The local editor was inspected with the actual Echo Station page and exact configured fonts. Browser automation exercised real pointer dragging, undo, redo, unchanged frozen text, manual line breaks, save-copy, reload and SVG/master/reading PNG export. Server tests reject modified or deleted frozen words, removed freeze metadata, foreign Host/Origin, missing write token and file traversal. The original JSON is not overwritten.

Raster checks compare actual pixels: hollow strokes reveal the background where solid type previously painted; a foreground mask removes only the chosen region. Chromium can round antialiased edges by one intensity level after adding a mask layer, so the test permits exactly that numerical tolerance outside the mask. Font-role omissions are errors instead of browser fallback. Polygon tests distinguish crossing tails from nearby curves with overlapping bounding rectangles.

[Editor screenshot](https://github.com/xjtydl/comic-letterer/releases/download/v0.2.0/editor.png)

## Practical boundaries

This is an existing-job lettering editor. Page creation, arbitrary script import, automated scene segmentation, true bold/italic runs, complex-script shaping, perspective signs and CMYK/prepress remain outside this release. Masks and protected regions are supplied in source JSON; advanced item parameters are editable in the GUI. SVG is editable Unicode and references the supplied fonts; opening it with replacement fonts invalidates the measured layout. A clean check does not replace reading-size visual inspection.
