# Input contract v1

Coordinates are **page-global pixels**. Rectangles are `[x, y, width, height]`, points `[x, y]`. No pt conversion. Width/height must be positive finite numbers; IDs start with an ASCII letter and contain letters, digits, `-` or `_`. Unknown fields are errors. Source input is never mutated.

```json
{
  "version": 1,
  "width": 800,
  "height": 600,
  "reading_width": 800,
  "direction": "ltr",
  "panels": [{"id": "p1", "box": [0, 0, 800, 600]}],
  "protected": [{"id": "face", "box": [410, 330, 80, 90]}],
  "items": [{
    "id": "a", "panel": "p1", "order": 1,
    "kind": "speech", "speaker": "traveler",
    "text": "雨停了，我们走吧。", "expected_text": "雨停了，我们走吧。",
    "font_size": 32, "box": [40, 30, 400, 160], "target": [450, 370]
  }]
}
```

## Page and panel

| Field | Meaning |
|---|---|
| `version` | Exactly 1 |
| `width`, `height` | Canvas dimensions, at most 50000 each |
| `panels` | Nonempty array of `{id, box}`; boxes inside canvas; input order is panel order |
| `items` | Lettering array; explicit order unique within each panel |
| `protected` | Optional `{id, box}` array: manually marked faces, props, sightlines |
| `direction` | `ltr` default or `rtl`; placement/reading heuristics only, not text bidi support |
| `reading_width` | Target output width; defaults to canvas width |
| `min_reading_font` | Configurable warning threshold in reading pixels, default 14; not an industry standard |

## Item

Required: `id`, `panel`, `order`, `kind`, `text`, plus `box` or `size`.

`kind`: `speech`, `thought`, `shout`, `whisper`, `weak`, `electronic`, `caption`, `sfx`, `floating`.

| Field | Meaning / default |
|---|---|
| `speaker` | Required string for voiced kinds; machine-readable identity |
| `expected_text` | Optional exact freeze; mismatch raises an error |
| `font_size` | Integer pixels, default 28, maximum 1000 |
| `box` | Explicit outer contour bounds, no tail included |
| `size` | `[width,height]` when searching candidate positions |
| `candidates` | Optional nonempty list of `xywh` boxes instead of generated 5×5 grid; requires `size` |
| `target` | Mouth, head (thought), device or explicit source point; required for unjoined voices by layout check |
| `off_panel` | Boolean: source target must lie outside the panel; tail reaches and clips at its border |
| `join_to` | Earlier item ID, same panel/speaker/kind; speech/whisper only. Nonconsecutive requires explicit interruption opt-in. Continuation has no new tail |
| `padding` | Default `font_size × 0.6`; nonnegative |
| `line_height` | Baseline distance as font-size multiplier, default 1.25 |
| `fill`, `stroke`, `text_color` | Hex `#RRGGBB` only; default white (caption cream), dark stroke and text |
| `stroke_width` | Visible exterior stroke, default 2px; bottom contour uses double stroke under fill |
| `tail_fraction` | Open interval (0,1), default 0.5 of boundary-to-source gap, shortened to the first protected rectangle containing the source; an implementation choice |
| `rotation` | SFX only, degrees around box center; default 0 |
| `outlines` | SFX only; array of `{color,width}`, strictly decreasing widths; empty array disables outlines |

Same-speaker joins also require matching fill/stroke/width. Overlapping joined bubbles merge visually through layer fills; separated bubbles have a tapered connector, optionally curved with `join_curve`. Nonconsecutive joins require `allow_interruption: true` and emit an inspection warning. `caption` can carry a narrator in `speaker` but needs no target. SFX `speaker` may identify the object; no speech tail is generated.

## Text layout

UTF-8 JSON, exact Unicode. Spaces and explicit LF newlines are retained. Raw control characters other than LF are rejected. Soft wrapping does not insert or delete source characters. XML entities are escaped. `report.items[].lines` concatenates to the original text. Latin word boundaries are preferred; long words may split without inserted hyphens. Chinese closing punctuation stays off new lines where feasible and opening punctuation stays with following text. The algorithm is not semantic phrase analysis or a complete Unicode line-breaking implementation.

Glyph bounding boxes are checked against padded contours; non-elliptical voice shapes use a conservative inset. Too-small boxes produce `text_overflow`, retaining the selected font size. Missing glyphs are errors even if a browser might find a fallback. Measurement uses the selected font/collection face; font substitution in another application invalidates this measurement.

## Reports and checks

`ok` means no error-severity issue; warnings remain visible. `--strict` also fails warnings. Issues carry `code`, `item`, `severity`, `message`. Checks include text overflow, missing glyphs, box/protected overlap, target inside balloon, missing target, conservative tail/join conflicts, rotated SFX bounds, repeated/reversed reading order and small reading text. Duplicate numeric order is structural; suspicious geometric order is a warning.

Protect full hair/hat/face bounds, not just the mouth target. Curved speech-tail checks use sampled polygons; tail crossings use polygon intersections and joins use sampled local envelopes. Thought/electronic checks remain conservative. They do not detect arbitrary pixels, tangencies to unmarked art, narrative misattribution, actual font visual weight, or every possible occlusion. Stroke envelopes and SFX checks are conservative, not pixel-perfect clearance guarantees.

SVG group IDs: `art`, `balloons`, `balloon-outlines`, `tails-and-joins`, `balloon-fills`, `text`, `sfx`. Item groups store `data-panel`, `data-order`, `data-speaker`, `data-kind`; metadata retains the JSON and font hash. These are standard SVG groups, not an assurance of native layer UI in every editor. Recompile JSON to change content and recompute geometry. Manual SVG edits do not round-trip back to JSON.

The CLI only embeds explicitly supplied local PNG/JPEG art. It accepts no raw SVG fragments or remote image/font URL. PNG rendering blocks network requests. Use trusted input file paths; this CLI is not an upload service or sandbox for untrusted font parsers.

## v0.2 additions (schema version remains 1)

| Field | Meaning |
|---|---|
| `breaks` | Sorted distinct internal **Unicode code-point** offsets; source text stays unchanged. `[]` forces one line unless the source contains LF. Explicit LF remains preserved. |
| `flow` | `legacy` (default) or `balanced`; legal-boundary line-length optimization, not semantic Chinese segmentation |
| `align` | `left`, `center` (default), `right` |
| `emphasis` | Nonoverlapping `{start,end,scale,color?}` ranges; actual resized font metrics, scale ≤3. This is size emphasis, not faux or real bold. |
| `font_role` | `body` (default), or a configured role such as `display`; unknown roles fail. CLI `--display-font` and `--display-font-index` configure display. Python `fonts={"display":{"path":path,"index":0}}`. Paths stay outside source JSON. |
| `shape` | `ellipse` or `tv`, only speech/whisper; TV uses a fourth-power superellipse |
| `butt` | Distinct edges from `top`, `bottom`, `left`, `right`; permits cropping the balloon only at those panel edges. Text must remain within panel. |
| `join_curve` | Quadratic centerline control point; same page coordinate system |
| `allow_interruption` | Boolean explicit opt-in for nonconsecutive joins; never suppresses collision errors |
| `source_mark` | `squink`; hidden source burst at the tip, tail reaches the supplied source |
| `hollow` | SFX only, `fill=none` with editable outline layers; choose a suitably heavy display font |
| `arc` | SFX only, baseline arch height in pixels; positive arches upward |
| `glyphs` | SFX-only list of `{index,dx?,dy?,scale?,rotate?}`; code-point indices, unique, scale ≤4 |
| `shadow` | SFX-only `{dx,dy,steps,color}`; defaults 5,5,5,#20202A; 1–32 depth steps |

Per-glyph/arc SFX is single-line and cannot also carry range emphasis; use glyph scale instead. It is controlled placement of characters, not arbitrary glyph deformation. Whitespace/combining/complex-script limitations still apply. Depth is stepped flat extrusion, not a 3D lighting model.

Page `occlusions` is an array of `{id, polygon:[[x,y],...], items:[itemID,...]}`. Simple polygons mask only listed items, exposing unchanged original art; they do not segment the artwork automatically. Glyph-region intersection reports possible hidden text. Protected-region and some overlap checks remain conservative even when masks are present. Do not use masks to conceal essential words.

Python `compile_page(..., fonts=...)` and `render_png(..., fonts=...)` must receive the same font configuration. Reports and SVG metadata record every configured font hash. PNG/preview use in-memory WOFF subsets; exported SVG contains no font bytes. Install the same fonts when opening it elsewhere.

## Editor persistence

`edit INPUT --out DIRECTORY --background ART --font FONT [--display-font FONT] [--port PORT]` launches a loopback server. No source overwrite endpoint exists. Save creates `drafts/TIMESTAMP-ID/source.json`; export creates `exports/TIMESTAMP-ID/` with SVG/source/report and optional PNGs. A draft can contain layout errors, but the UI labels it diagnostic. Structural/frozen-text violations fail the operation. A failed PNG export can leave a partial export folder; success is reported only after all requested files are written.

## v0.3 typography, source geometry and narrative semantics

`emphasis` ranges now accept `font_role`. When a role is present, default `scale` is 1, so a true bold or italic face can be selected without resizing. The role must be configured; measurement, missing-glyph checks and browser subsets all use that face. SVG spans retain actual family/weight/style. Roles are aliases: the configured file determines actual weight/slant, never the role's name. The renderer disables synthetic weight/slant for its embedded local subsets.

CLI `--font-map fonts.json` accepts `{ "bold": {"path":"fonts/bold.ttf", "index":0}, "italic": {"path":"fonts/italic.ttf"} }`. Relative paths resolve against the map file, not the current directory. `body` remains `--font`; `--display-font` overrides a map's display role. Fonts are never bundled automatically.

| Field | Meaning |
|---|---|
| `tracking` | Extra spacing in source pixels; -0.2 to 1 em. Nonzero tracking uses explicit character positioning; complex shaping is not promised. |
| `horizontal_scale` | 0.9–1.1, measured and rendered consistently; explicit only, never an automatic fix for overflow |
| `keep_together` | `{start,end}` ranges of Unicode code-point offsets; automatic wrapping cannot split them. Conflicting explicit breaks fail. This is manual phrase protection, not NLP segmentation. |
| `tail` | Optional `{visible,width,length,gap,root_angle,curve}`; sizes in pixels, angle in degrees clockwise from page-right, curve is a global quadratic control point |
| `caption_type` | `location`, `time`, `inner`, `spoken`, `editorial`; caption/floating only. Inner/spoken require a speaker. Does not rewrite punctuation or apply English conventions. |
| `voice` | `normal`, `rough`, `breath`, `singing`, `telepathic`; explicitly selected for voiced balloons. Rough modifies contour and tail, breath/telepathy add marks, singing adds a music-note mark. Wavy sung baselines remain unimplemented. |
| `double_outline` | Outer contour offset 0–24px; 0 disables. Not for caption/floating/SFX. |
| `style` | Named page style; raw item fields override inherited appearance. No text/source IDs can be supplied by a style. |

Tail `length` is an upper bound: it is shortened before protected source regions, accounting for `gap`. `root_angle` chooses the attachment direction; a poor angle or control point can bend back through the balloon and still needs visual review. Width is full root width. Curved overrides are for smooth tails; thought/electronic curve overrides fail. `visible` defaults to true on the first balloon and false on continuations. You can explicitly suppress the first and enable a later tail; a connected voice group without attribution is reported. Explicit off-panel tailless speech is allowed.

Page `min_tail_length` enables a reading-pixel warning (default 0 for compatibility). It is a configurable diagnostic, not a universal comic rule. `ink_edges:[{id,points:[[x,y],...]}]` with `tangent_distance` (default 3 source pixels) warns when sampled lettering boundaries approach a manually marked ink line. It cannot identify artwork edges on its own or distinguish every intentional overlap.

Page `styles` maps IDs to appearance/semantic definitions: kind, font role/size, padding, line height, fill/stroke/text color, stroke width, shape, tracking, horizontal scale, flow, alignment, voice, caption type and double outline. Styles can be copied between pages; there is no central book manager yet. Metadata preserves original style references, reports expose resolved values.

Editor additions: choose an actual face for a selected emphasis range; protect a selected phrase; adjust tracking/scale; choose caption/voice types; control tail width/length/gap/root angle and drag its orange curve handle; edit shared styles and marked ink edges. Fit searches bounded box dimensions at the current origin with frozen words and the same font size, accepting only candidates without item errors. It may fail and ask for repositioning; it is not whole-page optimization.

## v0.4 expressive lettering

- `baseline`: `{mode, amplitude, group}`. `mode` is `straight` (default), `bounce` or `wave`. `amplitude` is page pixels, default `0.08 × font_size`, bounded to `0..0.25 × font_size`; `group` is an integer `1..12` (default 2). Bounce alternates groups, wave follows a six-group cycle. Use on dialogue/captions; SFX retains its separate `arc`/`glyphs` system. Combining marks follow their base. This is not complex-script shaping or an OpenType replacement; splitting runs can change kerning across a group boundary, and the compiler measures those same runs.
- `emphasis[].baseline_shift`: explicit pixel offset; negative moves up, positive down, within ±one base em. When present without `scale`, size stays unchanged. Shifted glyph bounds and extra line spacing are measured and checked. Centering includes the added ascent/descent, so the final block also recenters inside the balloon.
- `shape: organic`: speech/whisper only. Subtle deterministic asymmetry within the specified bounds. Tail length starts at the actual radial contour; text uses a conservative inner envelope.
- `shape: tattered`: caption only. Small inward roughness and divots, bounded by the declared rectangle. Text checks include edge wear. This does not implement scroll ends or drop caps.
- `baseline` may be inherited from a page style. The editor exposes baseline mode/amplitude/group, emphasis shift and both contours. Saving/reloading retains these fields and frozen words.

These effects are choices, not automatic voice classification. The actual Echo Station page uses a small wave for the distorted receiver, organic speech and a worn inner-caption frame. Bounce has automated coverage; song/drunkenness/telepathy narrative treatments are still separately pending.

## v0.5 decorative contours and initials

| Field | Contract |
|---|---|
| `shape: mechanical` | Speech/shout/electronic. Four notches, three stroke layers, broken middle stroke. |
| `mechanical` | `{band:7, dash:7, gap:5, notch:0.09}` defaults. Band 2–24px and ≤12% of smaller box dimension; dash/gap 1–80px; notch .02–.16. |
| `shape: sawtooth` / `flame` | Speech/shout/electronic. Straight leaning teeth versus curved asymmetric cusps. |
| `edge` | `{spacing:24, depth:min(10, min_dimension*0.08)}`. Spacing 8–128px; depth 1px to 16% of smaller dimension. Arc-length sampling recomputes count (minimum 8, maximum 512; excessive requested count errors). Report includes count and actual spacing. |
| `shape: scroll` | Caption only; curled sides, seams/shade and reserved central text area. |
| `scroll` | `{curl:min(18,height*0.2)}`; at least 4px and no larger than 16% of width/30% of height. |
| `drop_cap` | Caption/floating only, left aligned. `{lines:2, count:1, font_role?, gap?, color?}`. Lines 2–4; initial prefix count 1–4 Unicode code points, extended through following combining marks. Gap defaults .3em, bounded 0–2em. Actual font size is measured to span the specified body rows. Following rows use full width. |

The initial and body are separate measured runs, but one exact Unicode source. Body emphasis remains supported; emphasis intersecting the initial is rejected because its face/color are controlled by `drop_cap`. A protected phrase cannot be split by the initial. Explicit breaks use original source offsets and must follow the initial. Automatic drop-cap wrapping is left-aligned per available row width; it does not run the uniform-width balanced-line optimizer.

`edge`, `mechanical`, `scroll` and `drop_cap` may be inherited from styles; explicit `null` disables inherited settings. A parameter object on the wrong shape is rejected. New voiced contours cannot combine with rough/telepathic contour replacements or double_outline. These restrictions avoid silently ignoring either requested construction. Scroll/initial glyph bounds participate in normal overflow and occlusion checks.

## Book style audit (first D04 operation)

`comic-letterer book-check book.json [--strict]` reads page JSON paths relative to the book manifest. It writes no source or output files; JSON report goes to stdout. The manifest has `version:1`, nonempty `pages:[{id,path,edition?}]`, `rules:[{id,match,expect}]`, and optional `exceptions`.

`match` may specify `speaker`, resolved `kind`, `style`, `voice`, `caption_type`, or the page entry's `edition`. `expect` checks explicitly chosen metadata fields (see `book.py` EXPECT), including resolved defaults and optional `reading_font_size`. Numeric comparison tolerance is 1e-6; this is not an optical tolerance. Font roles are labels, not a proof that the same actual font file is installed.

An exception is `{page,item,rule,field,value,reason}`. It only applies to that exact mismatch value and remains visible in `recorded_exceptions`. Unmatched rules or stale exceptions warn; `--strict` fails warnings too. Frozen-text mismatches are errors. `ok` means no unexplained metadata errors, not that all pages look good or every style decision is approved. The command neither compiles pages nor verifies layout; run ordinary page checks/rendering separately.
