# Native artwork and editable lettering

Update, v0.10: this tool now has core `appearance` controls for continuous paper, edge glow and centered whisper dashes, including the editor and book audit/revision. See [the contract](../../../docs/contract.md) and [actual-story verification](../../../docs/v010-validation.md). The r02 discussion below records its historical branch-only state. Two routes here mean **balloons plus text**: program-rendered or directly image-generated; choosing one does not authorize regenerating approved artwork.

The program is one production tool. A new comic may generate art, balloons and lettering together; preserve successful native lettering after checking every word, speaker and reading order at delivery size. Choose editable lettering for exact changes, localization or layered delivery. Do not use program geometry as the visual ceiling for native image generation.

When using the program, choose fill, ink and outline from the artwork's palette and narrative role. White is available, not an aesthetic requirement. A warm paper fill alone does not solve a pasted-on appearance: inspect the contour, source distance, tail root, texture continuity and negative space. Preserve the approved artwork and text; do not regenerate characters to fix a lettering issue.

## Last Ticket evidence, 2026-11-06

The complete native eight-panel strip r01 integrates warm paper variation, organic edges, ghost light, a floating title and the closing caption. The complete program r02 uses the fixed v0.7 engine with separate SVG styling. Both were inspected. They use different art/composition and do not constitute a controlled same-art benchmark. The user viewed r02 and found it improved, while still finding the light balloons insufficiently integrated; the user prefers considering direct native generation for future comics. This is not full-module approval.

Useful branch methods: deterministic fill grain, restrained ghost/thought edge light, and whisper dashes partially visible over light paper against dark art. At the r02 review these were **production-local**, not core v0.9 parameters. The script styles only the body fill, leaving tails/dots flat, and chooses glowing items by story-specific IDs. v0.10 implements the reusable operations through explicit styles, continuous material and root-safe borders; it does not paste story IDs into the core.

Core `fill`, `stroke`, `text_color` and existing shape controls make palette/contour choices; v0.10 adds documented `appearance` parameters. Use that schema rather than branch-only filter names. Never insert invented fields into a job or describe a postprocessed SVG as raw engine output.

Native raster words are not editable Unicode; keep a text source separately. A local image edit may change pixels outside its requested region; inspect the returned image instead of promising pixel locking. Record the actual model metadata if exposed; an unspecified image backend does not prove a named model was used. Native letters, artwork continuity and desired panel pacing all need actual review.

Full audit and module mapping: [branch review](../../../docs/last-ticket-branch-review-20261106.md). That review alone did not establish model training or a new engine release; v0.10 implementation and verification are recorded separately.
