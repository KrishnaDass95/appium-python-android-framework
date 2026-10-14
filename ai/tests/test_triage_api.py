"""Unit tests for ai.triage_api. A fake client stands in for the API: no key, no network.

Run with: uv run pytest -o addopts="" ai/tests
"""

from pathlib import Path
from types import SimpleNamespace

import pytest

from ai import triage_api
from ai.triage_api import TriageError, TriageItem, TriageResult, build_prompt, triage


class FakeMessages:
    def __init__(self, response: SimpleNamespace) -> None:
        self.response = response
        self.calls: list[dict] = []

    def parse(self, **kwargs: object) -> SimpleNamespace:
        self.calls.append(kwargs)
        return self.response


def _client(parsed: TriageResult | None, stop_reason: str = "end_turn") -> SimpleNamespace:
    response = SimpleNamespace(parsed_output=parsed, stop_reason=stop_reason)
    return SimpleNamespace(messages=FakeMessages(response))


def _report_dir(tmp_path: Path) -> Path:
    (tmp_path / "test_x").mkdir()
    (tmp_path / "REPORT.md").write_text("NoSuchElementError at tap_sort password=hunter2")
    (tmp_path / "test_x" / "page-source-test_x.xml").write_text('<node resource-id="sortIV"/>')
    return tmp_path


def _item(quote: str) -> TriageItem:
    return TriageItem(
        test="test_x",
        verdict="locator broken",
        evidence_quote=quote,
        explanation="why",
        suggested_fix="fix",
        confidence="high",
    )


def test_prompt_is_redacted_and_includes_page_source(tmp_path: Path) -> None:
    prompt = build_prompt(_report_dir(tmp_path))
    assert "hunter2" not in prompt
    assert '<page_source test="test_x">' in prompt
    assert 'resource-id="sortIV"' in prompt


def test_triage_sends_schema_and_renders_result(tmp_path: Path) -> None:
    client = _client(TriageResult(items=[_item("NoSuchElementError")]))
    markdown, _ = triage(_report_dir(tmp_path), client=client, model="test-model")
    call = client.messages.calls[0]
    assert call["model"] == "test-model"
    assert call["output_format"] is TriageResult
    assert "locator broken" in markdown
    assert "WARNING" not in markdown


def test_invented_quote_is_flagged(tmp_path: Path) -> None:
    client = _client(TriageResult(items=[_item("this text is not in the evidence")]))
    markdown, _ = triage(_report_dir(tmp_path), client=client)
    assert "WARNING" in markdown


def test_refusal_and_schema_mismatch_raise(tmp_path: Path) -> None:
    report_dir = _report_dir(tmp_path)
    with pytest.raises(TriageError):
        triage(report_dir, client=_client(None, stop_reason="refusal"))
    with pytest.raises(TriageError):
        triage(report_dir, client=_client(None))


def test_main_skips_without_key(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_AUTH_TOKEN", raising=False)
    monkeypatch.setattr("sys.argv", ["triage_api", "--dir", str(tmp_path)])
    assert triage_api.main() == 0
    assert "skipping" in capsys.readouterr().out
