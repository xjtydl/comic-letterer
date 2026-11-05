import copy
import json
import os
import threading
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from comic_letterer.editor import EditorSession, create_server


@pytest.fixture
def session(tmp_path):
    job = {
        "version": 1,
        "width": 600,
        "height": 400,
        "reading_width": 600,
        "panels": [{"id": "p", "box": [0, 0, 600, 400]}],
        "items": [
            {
                "id": "a",
                "panel": "p",
                "order": 1,
                "kind": "speech",
                "speaker": "A",
                "text": "The door is open.",
                "expected_text": "The door is open.",
                "font_size": 24,
                "box": [40, 30, 300, 130],
                "target": [400, 250],
            }
        ],
    }
    return EditorSession(job, tmp_path)


@pytest.mark.parametrize("change", ["text", "expected_text", "remove", "remove_lock"])
def test_frozen_source_cannot_be_bypassed(session, change):
    job = copy.deepcopy(session.job)
    if change == "remove":
        job["items"].clear()
    elif change == "remove_lock":
        del job["items"][0]["expected_text"]
    else:
        job["items"][0][change] = "Changed"
    with pytest.raises(ValueError, match="frozen"):
        session.save(job)
    assert not list(session.out.iterdir())


def test_saves_are_distinct_and_original_untouched(session):
    original = copy.deepcopy(session.job)
    job = copy.deepcopy(original)
    job["items"][0]["box"][0] += 10
    a, b = session.save(job), session.save(job)
    assert a["path"] != b["path"]
    assert json.loads(open(a["path"]).read()) == job
    assert original["items"][0]["box"][0] == 40
    assert session.snapshot()["job"] == job


@pytest.fixture
def server(session):
    server = create_server(session)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_port}"
    server.shutdown()
    server.server_close()
    thread.join()


def test_loopback_token_origin_and_traversal(session, server):
    for headers in (
        {},
        {"X-Editor-Token": session.token, "Origin": "https://example.com"},
    ):
        req = Request(
            server + "/save",
            data=json.dumps({"job": session.job}).encode(),
            headers={"Content-Type": "application/json", **headers},
        )
        with pytest.raises(HTTPError) as error:
            urlopen(req)
        assert error.value.code == 403
    req = Request(server, headers={"Host": "example.com"})
    with pytest.raises(HTTPError) as error:
        urlopen(req)
    assert error.value.code == 403
    with pytest.raises(HTTPError) as error:
        urlopen(server + "/files/%2e%2e/secret")
    assert error.value.code == 404


@pytest.mark.skipif(
    os.environ.get("COMIC_LETTERER_RENDER_TEST") != "1",
    reason="optional browser integration",
)
def test_real_editor_drag_undo_save_reload_and_export(session, server, tmp_path):
    from playwright.sync_api import sync_playwright

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={"width": 1400, "height": 1000})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto(server)
        page.wait_for_function("() => window.editorReady")
        page.locator("#zoom").select_option("reading")
        assert page.locator("#source-text").get_attribute("readonly") is not None
        box = page.locator('[data-item="a"]').bounding_box()
        page.mouse.move(box["x"] + 40, box["y"] + 40)
        page.mouse.down()
        page.mouse.move(box["x"] + 70, box["y"] + 55, steps=5)
        page.mouse.up()
        page.wait_for_function('() => document.getElementById("x").value === "70"')
        page.wait_for_function(
            '() => document.getElementById("status").textContent.includes("检查通过")'
        )
        page.locator("#undo").click()
        page.wait_for_function('() => document.getElementById("x").value === "40"')
        page.locator("#redo").click()
        page.wait_for_function('() => document.getElementById("x").value === "70"')
        page.locator("#lines").fill("The door\n is open.")
        page.locator("#apply-lines").click()
        page.wait_for_function(
            '() => document.getElementById("advanced").value.includes("breaks")'
        )
        page.locator("#save").click()
        page.wait_for_function(
            '() => document.getElementById("status").textContent.includes("drafts")'
        )
        page.reload()
        page.wait_for_function("() => window.editorReady")
        assert page.locator("#x").input_value() == "70"
        assert page.locator("#lines").input_value() == "The door\n is open."
        page.locator("#export-png").click()
        page.locator("#files a", has_text="reading.png").wait_for(timeout=60000)
        assert len(list(tmp_path.glob("exports/*/master.png"))) == 1
        page.screenshot(path=str(tmp_path / "editor.png"))
        assert not errors
        browser.close()
