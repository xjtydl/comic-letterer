# v0.2 development and narrative validation

User requested continued implementation with actual comic results, not a preset sheet. Keep the existing independent implementation and frozen production pages unchanged.

## Implement and test (completed v0.2; see v02-validation.md)

1. Typography module: lossless explicit break offsets; balanced line lengths with punctuation boundary costs; word-range emphasis with measured scaling; left/center/right alignment; editable text retained.
2. Geometry: rounded TV contour, panel-butt clipping with safe text, off-panel tails terminating at the panel edge, curved joins with explicit interruption opt-in, hidden-source squink; polygon foreground masks with explicit item targets.
3. SFX: real transparent/hollow fill, stepped depth shadow, per-character position/size/rotation and arced baseline. Inspect glyph counters and original source text.
4. Local editor: actual art + SVG preview, selectable draggable items/targets, editable layout and immutable frozen wording, undo/redo, save a new JSON, SVG/PNG export and reading-width preview. Loopback only; do not modify shared services.
5. Real outputs: original short story `Echo Station`, plus private legacy page diagnostic. Publish only original story, code and examples. Expand tests and Skill from actual findings. Release after local and remote checks.

## Original validation page: Echo Station / 回声站

Create an independent unlettered five-panel page first. Not related to the private book or approved cast. Hand-inked color suspense comic, cool rain/night tones and warm utility lights. Two original adults: young short-haired woman in red rain jacket; older gray-bearded caretaker in ochre coat. They investigate a noise at a closed railway station and find a kitten caught beside a loose signal bell.

Layout: full-width establishing panel; two middle panels; two bottom panels. Each beat adds information: unexpected sound → listen at shut door → power off/check radio → door opens with a clang → kitten reveal and relieved exchange. Preserve usable negative space for actual dialogue. No pre-rendered balloons, letters, numbers, signage or SFX in the artwork.

Apply comic-production-entry → american-comic-layout / comic-visual-language / comic-lettering: actual wording before geometry; voices tied to sound source; protect faces, hand action, latch and kitten; do not assign sound to a pictured radio without a script event, a large hollow metallic clang only at visible door impact, no impact effect in the listening panel. Last panel uses normal dialogue and a silent kitten reveal; the alternative treatment adds a justified hidden kitten call. Check order without numbered guides at 900px width and inspect roots/joins enlarged.

Use the gpt-image-2-prompting visual-brief method for original art: medium, subject, layout, tone, material and explicit blank-text requirement. Font and lettering remain program-generated. Source image and panel boxes will be recorded after inspecting the actual generated art.
