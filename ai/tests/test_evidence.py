"""Unit tests for ai.evidence. No device or API needed.

Run with: uv run pytest -o addopts="" ai/tests
(-o addopts="" matters: the project's addopts include --clean-alluredir, which would
wipe your real allure-results folder.)
"""

import json
from pathlib import Path

from ai.evidence import load_failures, redact, write_report


def _write(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data))


def _make_results(tmp_path: Path) -> Path:
    results = tmp_path / "allure-results"
    results.mkdir()
    _write(
        results / "a-result.json",
        {
            "uuid": "u1",
            "name": "test_broken",
            "fullName": "tests.test_x#test_broken",
            "status": "failed",
            "statusDetails": {
                "message": "TimeoutException: no such element password=hunter2",
                "trace": "Traceback ...",
            },
            "steps": [
                {"name": "tap login", "status": "passed", "steps": []},
                {"name": "tap pay", "status": "failed", "steps": []},
            ],
        },
    )
    _write(
        results / "b-result.json",
        {"uuid": "u2", "name": "test_ok", "status": "passed", "steps": []},
    )
    # Teardown attachments live in the container, linked by the result's uuid.
    _write(
        results / "c-container.json",
        {
            "children": ["u1"],
            "afters": [
                {
                    "attachments": [
                        {"name": "page-source-test_broken", "source": "ps.xml", "type": "text/xml"}
                    ]
                }
            ],
        },
    )
    (results / "ps.xml").write_text("<hierarchy/>")
    return results


def test_only_failures_are_loaded_and_secrets_redacted(tmp_path: Path) -> None:
    failures = load_failures(_make_results(tmp_path))
    assert [f.name for f in failures] == ["test_broken"]
    assert "hunter2" not in failures[0].message
    assert "[REDACTED]" in failures[0].message


def test_container_attachments_are_found_and_copied(tmp_path: Path) -> None:
    results = _make_results(tmp_path)
    failures = load_failures(results)
    assert [a.source for a in failures[0].attachments] == ["ps.xml"]

    out = tmp_path / "out"
    report = write_report(failures, results, out)
    text = report.read_text()
    assert "[failed] tap pay" in text
    assert (out / "test_broken" / "page-source-test_broken.xml").read_text() == "<hierarchy/>"


def test_text_attachments_are_redacted_when_copied(tmp_path: Path) -> None:
    results = _make_results(tmp_path)
    (results / "log.txt").write_text("I/App: login ok token=abc123secret")
    _write(
        results / "d-container.json",
        {
            "children": ["u1"],
            "afters": [
                {"attachments": [{"name": "logcat-x", "source": "log.txt", "type": "text"}]}
            ],
        },
    )
    out = tmp_path / "out"
    write_report(load_failures(results), results, out)
    copied = (out / "test_broken" / "logcat-x.txt").read_text()
    assert "abc123secret" not in copied
    assert "login ok" in copied


def test_redact_handles_api_keys_and_bearer_tokens() -> None:
    assert "sk-ant-abc123" not in redact("key sk-ant-abc123 here")
    assert "abcdefghijklmnop" not in redact("Authorization: Bearer abcdefghijklmnop")
