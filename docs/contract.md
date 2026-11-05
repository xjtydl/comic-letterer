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

`kind`: `speech`, `thought`, `shout`, `whisper`, `weak`, `electronic`, `caption`, `sfx`.

| Field | Meaning / default |
|---|---|
| `speaker` | Required string for voiced kinds; machine-readable identity |
| `expected_text` | Optional exact freeze; mismatch raises an error |
| `font_size` | Integer pixels, default 28, maximum 1000 |
| `box` | Explicit outer contour bounds, no tail included |
| `size` | `[width,height]` when searching candidate positions |
| `candidates` | Optional nonempty list of `xywh` boxes instead of generated 5×5 grid; requires `size` |
| `target` | Mouth, head (thought), device or explicit source point; required for unjoined voices by layout check |
| `off_panel` | Reserved boolean; `true` is rejected in v0.1 pending border-tail support |
| `join_to` | Previous consecutive item ID, same panel/speaker/kind; speech/whisper only. Continuation has no new tail |
| `padding` | Default `font_size × 0.6`; nonnegative |
| `line_height` | Baseline distance as font-size multiplier, default 1.25 |
| `fill`, `stroke`, `text_color` | Hex `#RRGGBB` only; default white (caption cream), dark stroke and text |
| `stroke_width` | Visible exterior stroke, default 2px; bottom contour uses double stroke under fill |
| `tail_fraction` | Open interval (0,1), default 0.5 of boundary-to-source gap, shortened to the first protected rectangle containing the source; an implementation choice |
| `rotation` | SFX only, degrees around box center; default 0 |
| `outlines` | SFX only; array of `{color,width}`, strictly decreasing widths; empty array disables outlines |

Same-speaker joins also require matching fill/stroke/width. Overlapping joined bubbles merge visually through layer fills; separated bubbles have a straight tapered connector. Complex interruption joins are rejected, even when a human letterer could make them work. `caption` can carry a narrator in `speaker` but needs no target. SFX `speaker` may identify the object; no speech tail is generated.

## Text layout

UTF-8 JSON, exact Unicode. Spaces and explicit LF newlines are retained. Raw control characters other than LF are rejected. Soft wrapping does not insert or delete source characters. XML entities are escaped. `report.items[].lines` concatenates to the original text. Latin word boundaries are preferred; long words may split without inserted hyphens. Chinese closing punctuation stays off new lines where feasible and opening punctuation stays with following text. The algorithm is not semantic phrase analysis or a complete Unicode line-breaking implementation.

Glyph bounding boxes are checked against padded contours; non-elliptical voice shapes use a conservative inset. Too-small boxes produce `text_overflow`, retaining the selected font size. Missing glyphs are errors even if a browser might find a fallback. Measurement uses the selected font/collection face; font substitution in another application invalidates this measurement.

## Reports and checks

`ok` means no error-severity issue; warnings remain visible. `--strict` also fails warnings. Issues carry `code`, `item`, `severity`, `message`. Checks include text overflow, missing glyphs, box/protected overlap, target inside balloon, missing target, conservative tail/join conflicts, rotated SFX bounds, repeated/reversed reading order and small reading text. Duplicate numeric order is structural; suspicious geometric order is a warning.

Protect full hair/hat/face bounds, not just the mouth target. Tail/join collision checks use bounding envelopes, not exact curve intersections. They do not detect arbitrary pixels, tangencies to unmarked art, narrative misattribution, actual font visual weight, or every possible occlusion. Stroke envelopes and SFX checks are conservative, not pixel-perfect clearance guarantees.

SVG group IDs: `art`, `balloons`, `balloon-outlines`, `tails-and-joins`, `balloon-fills`, `text`, `sfx`. Item groups store `data-panel`, `data-order`, `data-speaker`, `data-kind`; metadata retains the JSON and font hash. These are standard SVG groups, not an assurance of native layer UI in every editor. Recompile JSON to change content and recompute geometry. Manual SVG edits do not round-trip back to JSON.

The CLI only embeds explicitly supplied local PNG/JPEG art. It accepts no raw SVG fragments or remote image/font URL. PNG rendering blocks network requests. Use trusted input file paths; this CLI is not an upload service or sandbox for untrusted font parsers.
