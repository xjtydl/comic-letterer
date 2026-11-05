import json
from comic_letterer.cli import main


def input_file(tmp_path):
    source = tmp_path / "job.json"
    source.write_text(
        json.dumps(
            {
                "version": 1,
                "width": 500,
                "height": 300,
                "panels": [{"id": "p", "box": [0, 0, 500, 300]}],
                "items": [
                    {
                        "id": "a",
                        "panel": "p",
                        "order": 1,
                        "kind": "caption",
                        "text": "Hello",
                        "font_size": 24,
                        "box": [20, 20, 220, 90],
                    }
                ],
            }
        )
    )
    return source


def test_cli_render_reload_and_overwrite(tmp_path, capsys):
    source = input_file(tmp_path)
    out = tmp_path / "result"
    assert main(["render", str(source), "--out", str(out)]) == 0
    report = json.loads((out / "report.json").read_text())
    assert report["ok"]
    assert json.loads(source.read_text()) == json.loads(
        (out / "source.json").read_text()
    )
    assert main(["check", str(out / "source.json")]) == 0
    assert main(["render", str(source), "--out", str(out)]) == 2
    assert main(["render", str(source), "--out", str(out), "--force"]) == 0


def test_cli_errors_and_warning_exit(tmp_path, capsys):
    source = input_file(tmp_path)
    job = json.loads(source.read_text())
    job["reading_width"] = 100
    source.write_text(json.dumps(job))
    assert main(["check", str(source)]) == 0
    assert main(["check", str(source), "--strict"]) == 1
    job["items"][0]["text"] = "A long sentence " * 40
    source.write_text(json.dumps(job))
    assert main(["check", str(source)]) == 1
    source.write_text("{broken")
    assert main(["check", str(source)]) == 2


def test_prevent_source_overwrite(tmp_path, capsys):
    source = input_file(tmp_path)
    source.rename(tmp_path / "source.json")
    source = tmp_path / "source.json"
    original = source.read_bytes()
    assert main(["render", str(source), "--out", str(tmp_path), "--force"]) == 2
    assert source.read_bytes() == original
