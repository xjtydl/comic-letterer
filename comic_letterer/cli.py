"""Small CLI; exit 0 clean, 1 layout errors (or strict warnings), 2 invalid input."""

import argparse
import base64
import json
import sys
from pathlib import Path

from PIL import Image
from .engine import compile_page, find_font


def main(argv=None):
    parser = argparse.ArgumentParser(prog="comic-letterer")
    parser.add_argument("--version", action="version", version="comic-letterer 0.9.0")
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("check", "render", "edit", "layout-proof"):
        p = sub.add_parser(command)
        p.add_argument("input", type=Path)
        p.add_argument("--font", type=Path)
        p.add_argument("--font-index", type=int, default=0)
        p.add_argument("--font-map", type=Path, help="JSON role-to-font map")
        p.add_argument("--display-font", type=Path)
        p.add_argument("--display-font-index", type=int, default=0)
        p.add_argument(
            "--strict", action="store_true", help="Fail on warnings as well as errors"
        )
        if command == "layout-proof":
            p.add_argument("--layouts", type=Path, required=True)
        if command in ("render", "edit", "layout-proof"):
            p.add_argument("--out", type=Path, required=True, help="Output directory")
            p.add_argument(
                "--background",
                type=Path,
                help="Local PNG/JPEG matching canvas dimensions",
            )
        if command == "edit":
            p.add_argument(
                "--port",
                type=int,
                default=0,
                help="Loopback port; 0 chooses an available port",
            )
        if command == "render":
            p.add_argument(
                "--png", action="store_true", help="Render master.png and reading.png"
            )
            p.add_argument(
                "--force", action="store_true", help="Replace known output files"
            )
    p = sub.add_parser("book-check", help="Read-only audit against explicit book style rules")
    p.add_argument("input", type=Path)
    p.add_argument("--strict", action="store_true")
    p = sub.add_parser("book-proof", help="Render a new continuous book proof without rewriting sources")
    p.add_argument("input", type=Path)
    p.add_argument("--assets", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--strict", action="store_true")
    p = sub.add_parser("book-revise", help="Apply an explicit revision to new copies and render before/after proofs")
    p.add_argument("input", type=Path)
    p.add_argument("--plan", type=Path, required=True)
    p.add_argument("--assets", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--strict", action="store_true")
    p = sub.add_parser("font-build", help="Build an authored pressure-stroke display alphabet")
    p.add_argument("input", type=Path)
    p.add_argument("--out", type=Path, required=True)
    p = sub.add_parser("script-import", help="Reconcile a semantic rich-text script with existing page geometry")
    p.add_argument("input", type=Path)
    p.add_argument("--book", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--strict", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.command == "script-import":
            from .script_handoff import import_script
            report = import_script(args.input, args.book, args.out)
            print(json.dumps(report, ensure_ascii=False, indent=2))
            return 0 if report["ok"] and not (args.strict and report["issues"]) else 1
        job = json.loads(args.input.read_text(encoding="utf-8"))
        if args.command == "book-revise":
            from .revision import revise_book
            report = revise_book(job, args.input.resolve().parent, json.loads(args.plan.read_text()),
                                 json.loads(args.assets.read_text()), args.assets.resolve().parent, args.out)
            print(json.dumps(report, ensure_ascii=False, indent=2))
            return 0 if report["ok"] and not (args.strict and report["issues"]) else 1
        if args.command == "book-proof":
            from .proof import proof_book
            report = proof_book(job, args.input.resolve().parent, json.loads(args.assets.read_text()), args.assets.resolve().parent, args.out)
            print(json.dumps(report, ensure_ascii=False, indent=2))
            return 0 if report["ok"] and not (args.strict and report["issues"]) else 1
        if args.command == "font-build":
            from .letterforms import build_font
            if args.out.exists(): raise ValueError("font output exists; choose a new file")
            args.out.parent.mkdir(parents=True, exist_ok=True)
            print(json.dumps(build_font(job, args.out), ensure_ascii=False, indent=2))
            return 0
        if args.command == "book-check":
            from .book import audit_book
            report = audit_book(job, args.input.resolve().parent)
            print(json.dumps(report, ensure_ascii=False, indent=2))
            return 0 if report["ok"] and not (args.strict and report["issues"]) else 1
        font = str(args.font or find_font())
        fonts = (
            {
                "display": {
                    "path": str(args.display_font),
                    "index": args.display_font_index,
                }
            }
            if args.display_font
            else None
        )
        from .fonts import read_font_map

        fonts = {**read_font_map(args.font_map), **(fonts or {})}
        if args.command == "layout-proof":
            from .layout import layout_proof
            if args.background is None: raise ValueError("layout-proof requires a background")
            report = layout_proof(args.input, json.loads(args.layouts.read_text()), font,
                                  args.font_index, fonts, args.background, args.out)
            print(json.dumps(report, ensure_ascii=False, indent=2))
            return 0 if report["ok"] and not (args.strict and report["issues"]) else 1
        if args.command == "edit":
            from .editor import serve

            serve(
                job, args.out, font, args.font_index, fonts, args.background, args.port
            )
            return 0
        background = None
        if args.command == "render" and args.background:
            with Image.open(args.background) as im:
                if im.format not in ("PNG", "JPEG"):
                    raise ValueError("background must be PNG/JPEG")
                if list(im.size) != [job["width"], job["height"]]:
                    raise ValueError("background dimensions must match page")
                im.verify()
                mime = "png" if im.format == "PNG" else "jpeg"
            background = f"data:image/{mime};base64," + base64.b64encode(
                args.background.read_bytes()
            ).decode("ascii")
        svg, report = compile_page(job, font, args.font_index, background, fonts)
        if args.command == "render":
            names = ["page.svg", "report.json", "source.json"] + (
                ["master.png", "reading.png"] if args.png else []
            )
            if not args.force and any((args.out / n).exists() for n in names):
                raise ValueError(
                    "output exists; choose another directory or use --force"
                )
            # Prevent output flags from overwriting the source image or JSON.
            inputs = {args.input.resolve(), Path(font).resolve()}
            if args.background:
                inputs.add(args.background.resolve())
            if args.font:
                inputs.add(args.font.resolve())
            if args.font_map:
                inputs.add(args.font_map.resolve())
            inputs.update(Path(spec["path"]).resolve() for spec in fonts.values())
            if args.display_font:
                inputs.add(args.display_font.resolve())
            if any((args.out / n).resolve() in inputs for n in names):
                raise ValueError("output would overwrite an input")
            args.out.mkdir(parents=True, exist_ok=True)
            (args.out / "page.svg").write_text(svg, encoding="utf-8")
            (args.out / "source.json").write_text(
                json.dumps(job, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
            if args.png:
                from .render import render_png

                render_png(
                    svg,
                    args.out / "master.png",
                    round(job["width"]),
                    font,
                    args.font_index,
                    fonts,
                )
                render_png(
                    svg,
                    args.out / "reading.png",
                    round(report["reading_width"]),
                    font,
                    args.font_index,
                    fonts,
                )
                report["raster"] = {
                    "master": "master.png",
                    "reading": "reading.png",
                    "rendered_from_vector": True,
                }
            (args.out / "report.json").write_text(
                json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if report["ok"] and not (args.strict and report["issues"]) else 1
    except (ValueError, OSError, KeyError, TypeError, ImportError) as exc:
        print(f"comic-letterer: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
