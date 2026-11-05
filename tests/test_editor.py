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


@pytest.mark.skipif(
    os.environ.get("COMIC_LETTERER_RENDER_TEST") != "1",
    reason="optional browser integration",
)
def test_editor_phrase_tail_and_contour_controls(session, server):
    from playwright.sync_api import sync_playwright

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={"width": 1400, "height": 1000})
        page.goto(server)
        page.wait_for_function("() => window.editorReady")
        page.locator("#shape").select_option("organic")
        page.wait_for_function("()=>document.querySelector('#fill-a').getAttribute('d').includes(' L')")
        page.locator("#baseline-mode").select_option("wave")
        page.wait_for_function(
            "()=>new Set([...document.querySelectorAll('#lettering tspan')].map(n=>n.getAttribute('y'))).size>1"
        )
        page.locator("#source-text").evaluate(
            "(el)=>{el.focus();el.setSelectionRange(4,8)}"
        )
        page.locator("#keep-phrase").click()
        page.wait_for_function(
            '()=>document.getElementById("advanced").value.includes("keep_together")'
        )
        page.locator("#tail-width").fill("24")
        page.locator("#tail-width").press("Tab")
        page.wait_for_function(
            '()=>JSON.parse(document.getElementById("advanced").value).tail.width===24'
        )
        page.locator("#tail-curve").click()
        page.locator('[data-handle="tailcurve"]').wait_for()
        page.locator("#fit").click()
        page.wait_for_function('()=>!document.getElementById("fit").disabled')
        page.locator("#save").click()
        page.wait_for_function(
            '()=>document.getElementById("status").textContent.includes("drafts")'
        )
        page.reload()
        page.wait_for_function("()=>window.editorReady")
        value = json.loads(page.locator("#advanced").input_value())
        assert value["keep_together"] == [{"start": 4, "end": 8}]
        assert value["shape"] == "organic"
        assert value["baseline"]["mode"] == "wave"
        assert value["tail"]["width"] == 24 and "curve" in value["tail"]
        assert value["text"] == session.frozen["a"]
        browser.close()


@pytest.mark.skipif(
    os.environ.get('COMIC_LETTERER_RENDER_TEST') != '1',
    reason='optional browser integration',
)
def test_decorative_controls_roundtrip_and_export(session, server, tmp_path):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        browser=pw.chromium.launch()
        page=browser.new_page(viewport={'width':1400,'height':1100})
        errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto(server);page.wait_for_function('()=>window.editorReady')
        page.locator('#shape').select_option('mechanical')
        page.locator('#mechanical-broken-a').wait_for(state='attached')
        page.locator('#mechanical-band').fill('9');page.locator('#mechanical-band').press('Tab')
        page.wait_for_function("()=>Number(document.querySelector('#outline-a').getAttribute('stroke-width'))===18")
        page.locator('#shape').select_option('sawtooth')
        page.locator('#edge-spacing').fill('18');page.locator('#edge-spacing').press('Tab')
        page.wait_for_function("()=>JSON.parse(document.querySelector('#advanced').value).edge.spacing===18")
        page.locator('#shape').select_option('flame')
        page.wait_for_function("()=>document.querySelector('#fill-a').getAttribute('d').includes('C')")
        page.locator('#kind').select_option('caption')
        page.locator('#shape').select_option('scroll')
        page.locator('#scroll-fold-a-0').wait_for(state='attached')
        page.locator('#drop-enabled').check()
        page.wait_for_function("()=>Number(document.querySelector('#text-a tspan').getAttribute('font-size'))>24")
        page.locator('#save').click()
        page.wait_for_function("()=>document.querySelector('#status').textContent.includes('drafts')")
        page.reload();page.wait_for_function('()=>window.editorReady')
        assert page.locator('#drop-enabled').is_checked()
        value=json.loads(page.locator('#advanced').input_value())
        assert value['shape']=='scroll' and value['drop_cap']['lines']==2
        assert value['text']==session.frozen['a']
        page.locator('#export-png').click()
        page.locator('#files a',has_text='reading.png').wait_for(timeout=60000)
        assert len(list(tmp_path.glob('exports/*/reading.png')))==1
        assert not errors
        browser.close()

@pytest.mark.skipif(os.environ.get('COMIC_LETTERER_RENDER_TEST') != '1',reason='optional browser integration')
def test_row_controls_and_editable_contour_handles(session, server, tmp_path):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        browser=pw.chromium.launch();page=browser.new_page(viewport={'width':1450,'height':1200})
        errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto(server);page.wait_for_function('()=>window.editorReady')
        page.locator('#shape').select_option('custom')
        assert not page.locator('#scroll-controls').is_visible()
        handle=page.locator('[data-handle="contour-0-0"]');handle.wait_for()
        before=json.loads(page.locator('#advanced').input_value())['contour']['curves'][0][0]
        box=handle.bounding_box();page.mouse.move(box['x']+box['width']/2,box['y']+box['height']/2)
        page.mouse.down();page.mouse.move(box['x']-12,box['y']+box['height']/2);page.mouse.up()
        page.wait_for_function('()=>!document.querySelector("#status").textContent.includes("正在")')
        after=json.loads(page.locator('#advanced').input_value())
        assert after['contour']['curves'][0][0]!=before
        page.locator('summary',has_text='字体特性与逐行宽度').click()
        page.locator('#type-language').fill('en')
        page.locator('#type-scales').fill('[0.97]');page.locator('#apply-type').click()
        page.wait_for_function('()=>JSON.parse(document.querySelector("#advanced").value).line_scales?.[0]===0.97')
        page.locator('#save').click();page.wait_for_function('()=>document.querySelector("#status").textContent.includes("drafts")')
        page.reload();page.wait_for_function('()=>window.editorReady')
        value=json.loads(page.locator('#advanced').input_value())
        assert value['line_scales']==[.97] and value['language']=='en'
        assert value['contour']==after['contour'] and value['text']==session.frozen['a']
        assert not errors
        browser.close()
