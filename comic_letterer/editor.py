"""Loopback editor. Frozen words are enforced independently of client metadata."""

import base64
import copy
import json
import mimetypes
import secrets
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

from PIL import Image

from .engine import compile_page, find_font
from .render import font_css, render_png
from .fitting import fit_item


class EditorSession:
    def __init__(self, job, out, font=None, font_index=0, fonts=None, background=None):
        self.job = copy.deepcopy(job)
        self.frozen = {
            i["id"]: i["expected_text"] for i in job["items"] if "expected_text" in i
        }
        self.out = Path(out).resolve()
        self.font = str(font or find_font())
        self.font_index = font_index
        self.fonts = fonts or {}
        self.bank = {"body": {"path": self.font, "index": font_index}, **self.fonts}
        self.background = Path(background).resolve() if background else None
        self.background_data = None
        if self.background:
            with Image.open(self.background) as im:
                if im.format not in ("PNG", "JPEG") or list(im.size) != [
                    job["width"],
                    job["height"],
                ]:
                    raise ValueError(
                        "background must be PNG/JPEG matching page dimensions"
                    )
                mime = Image.MIME[im.format]
                im.verify()
            self.background_data = f"data:{mime};base64," + base64.b64encode(
                self.background.read_bytes()
            ).decode("ascii")
        self.lock = threading.RLock()
        self.token = secrets.token_urlsafe(32)
        self.preview(job)

    def validate(self, job):
        items = {item["id"]: item for item in job["items"]}
        for iid, text in self.frozen.items():
            if (
                iid not in items
                or items[iid].get("text") != text
                or items[iid].get("expected_text") != text
            ):
                raise ValueError(f"frozen wording cannot change or be removed: {iid}")
        if self.background and (job["width"], job["height"]) != (
            self.job["width"],
            self.job["height"],
        ):
            raise ValueError("page dimensions must match the original artwork")

    def compile(self, job, background=False):
        self.validate(job)
        return compile_page(
            job,
            self.font,
            self.font_index,
            self.background_data if background else None,
            self.fonts,
        )

    def preview(self, job):
        svg, report = self.compile(job)
        return {"svg": svg, "report": report, "css": font_css(svg, self.bank)}

    def snapshot(self):
        return {
            "job": copy.deepcopy(self.job),
            "frozen": list(self.frozen),
            "has_art": bool(self.background),
            "font_roles": list(self.bank),
            **self.preview(self.job),
        }

    def new_dir(self, category):
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
        destination = self.out / category / f"{stamp}-{secrets.token_hex(4)}"
        destination.mkdir(parents=True, exist_ok=False)
        return destination

    def save(self, job):
        _, report = self.compile(job)
        destination = self.new_dir("drafts") / "source.json"
        destination.write_text(
            json.dumps(job, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        self.job = copy.deepcopy(job)
        return {"path": str(destination), "report": report}

    def export(self, job, png=False):
        svg, report = self.compile(job, background=True)
        destination = self.new_dir("exports")
        (destination / "page.svg").write_text(svg, encoding="utf-8")
        (destination / "source.json").write_text(
            json.dumps(job, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        names = ["page.svg", "source.json", "report.json"]
        if png:
            for name, width in [
                ("master.png", job["width"]),
                ("reading.png", report["reading_width"]),
            ]:
                render_png(
                    svg,
                    destination / name,
                    round(width),
                    self.font,
                    self.font_index,
                    self.fonts,
                )
                names.append(name)
        (destination / "report.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        return {
            "path": str(destination),
            "report": report,
            "files": {
                name: "/files/" + str((destination / name).relative_to(self.out))
                for name in names
            },
        }


def create_server(session, port=0):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_args):
            pass

        def send(self, status, data, mime="application/json; charset=utf-8"):
            if isinstance(data, dict):
                data = json.dumps(data, ensure_ascii=False).encode("utf-8")
            elif isinstance(data, str):
                data = data.encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", mime)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header(
                "Content-Security-Policy",
                "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src data:; frame-ancestors 'none'; base-uri 'none'; form-action 'none'",
            )
            self.end_headers()
            self.wfile.write(data)

        def allowed(self, mutate=False):
            host = f"127.0.0.1:{self.server.server_port}"
            if self.headers.get("Host") != host:
                self.send(403, {"error": "loopback Host required"})
                return False
            origin = self.headers.get("Origin")
            if origin and origin != f"http://{host}":
                self.send(403, {"error": "cross-origin request rejected"})
                return False
            if mutate and not secrets.compare_digest(
                self.headers.get("X-Editor-Token", ""), session.token
            ):
                self.send(403, {"error": "editor token required"})
                return False
            return True

        def do_GET(self):
            if not self.allowed():
                return
            path = unquote(urlsplit(self.path).path)
            try:
                if path == "/":
                    html = (Path(__file__).parent / "web" / "editor.html").read_text(
                        encoding="utf-8"
                    )
                    self.send(
                        200,
                        html.replace("__TOKEN__", session.token),
                        "text/html; charset=utf-8",
                    )
                elif path == "/session":
                    with session.lock:
                        self.send(200, session.snapshot())
                elif path == "/art" and session.background:
                    self.send(
                        200,
                        session.background.read_bytes(),
                        mimetypes.guess_type(session.background)[0],
                    )
                elif path.startswith("/files/"):
                    target = (session.out / path.removeprefix("/files/")).resolve()
                    if not target.is_relative_to(session.out) or not target.is_file():
                        raise ValueError("file not found")
                    self.send(
                        200,
                        target.read_bytes(),
                        mimetypes.guess_type(target)[0] or "application/octet-stream",
                    )
                else:
                    self.send(404, {"error": "not found"})
            except (OSError, ValueError) as exc:
                self.send(404, {"error": str(exc)})

        def do_POST(self):
            if not self.allowed(mutate=True):
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if (
                    not 0 < length <= 2_000_000
                    or self.headers.get_content_type() != "application/json"
                ):
                    raise ValueError("JSON request required, maximum 2 MB")
                data = json.loads(self.rfile.read(length))
                with session.lock:
                    if self.path == "/preview":
                        result = session.preview(data["job"])
                    elif self.path == "/fit":
                        fitted = fit_item(data["job"], data["item"], session.compile)
                        result = {"job": fitted, **session.preview(fitted)}
                    elif self.path == "/save":
                        result = session.save(data["job"])
                    elif self.path == "/export":
                        result = session.export(data["job"], data.get("png") is True)
                    else:
                        self.send(404, {"error": "not found"})
                        return
                self.send(200, result)
            except Exception as exc:
                self.send(400, {"error": str(exc)})

    return ThreadingHTTPServer(("127.0.0.1", port), Handler)


def serve(job, out, font=None, font_index=0, fonts=None, background=None, port=0):
    session = EditorSession(job, out, font, font_index, fonts, background)
    server = create_server(session, port)
    print(f"Comic Letterer editor: http://127.0.0.1:{server.server_port}", flush=True)
    print(
        "Ctrl-C to stop. Save writes new drafts; your input remains unchanged.",
        flush=True,
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
