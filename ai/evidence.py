"""Gather failure evidence from allure-results into one folder for triage.

Usage (after a pytest run):
    uv run python -m ai.evidence
    uv run python -m ai.evidence --results allure-results --out scratch/triage

Why copy anything? pytest runs with --clean-alluredir, so the next run wipes
allure-results. Copying the evidence out keeps it.
"""

import argparse
import json
import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

FAILED_STATUSES = {"failed", "broken"}

# Things that must never end up in a report that might be pasted into a tool.
_SECRET_PATTERNS = [
    re.compile(r"sk-ant-[A-Za-z0-9_-]+"),
    re.compile(r"(?i)(bearer\s+)[A-Za-z0-9._~+/=-]{12,}"),
    re.compile(r"(?i)(access[_-]?key|secret|token|password)(['\"]?\s*[:=]\s*['\"]?)[^\s'\",}]+"),
]


def redact(text: str) -> str:
    text = _SECRET_PATTERNS[0].sub("[REDACTED]", text)
    text = _SECRET_PATTERNS[1].sub(r"\1[REDACTED]", text)
    return _SECRET_PATTERNS[2].sub(r"\1\2[REDACTED]", text)


@dataclass
class Attachment:
    name: str
    source: str  # file name inside allure-results
    type: str


@dataclass
class Failure:
    name: str
    full_name: str
    status: str
    message: str
    trace: str
    steps: list[str] = field(default_factory=list)
    attachments: list[Attachment] = field(default_factory=list)


def _read_json(path: Path) -> dict[str, Any]:
    with path.open() as f:
        data: dict[str, Any] = json.load(f)
    return data


def _collect_attachments(node: dict[str, Any]) -> list[Attachment]:
    """Walk a result/container/step dict and collect every attachment inside it."""
    found = [
        Attachment(a.get("name", ""), a.get("source", ""), a.get("type", ""))
        for a in node.get("attachments", [])
    ]
    for key in ("steps", "befores", "afters"):
        for child in node.get(key, []):
            found.extend(_collect_attachments(child))
    return found


def _flatten_steps(steps: list[dict[str, Any]], depth: int = 0) -> list[str]:
    lines = []
    for step in steps:
        lines.append(f"{'  ' * depth}[{step.get('status', '?')}] {step.get('name', '')}")
        lines.extend(_flatten_steps(step.get("steps", []), depth + 1))
    return lines


def load_failures(results_dir: Path) -> list[Failure]:
    # Attachments added in fixture teardown (our screenshot + page source) live in
    # the *-container.json files, not in the test's own result file.
    containers = [_read_json(p) for p in results_dir.glob("*-container.json")]
    failures = []
    for path in sorted(results_dir.glob("*-result.json")):
        result = _read_json(path)
        if result.get("status") not in FAILED_STATUSES:
            continue
        details = result.get("statusDetails") or {}
        attachments = _collect_attachments(result)
        for container in containers:
            if result.get("uuid") in container.get("children", []):
                attachments.extend(_collect_attachments(container))
        failures.append(
            Failure(
                name=result.get("name", path.stem),
                full_name=result.get("fullName", ""),
                status=result["status"],
                message=redact(details.get("message", "")),
                trace=redact(details.get("trace", "")),
                steps=_flatten_steps(result.get("steps", [])),
                attachments=attachments,
            )
        )
    return failures


def _safe(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", name).strip("_")


def write_report(failures: list[Failure], results_dir: Path, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    lines = [f"# Failure evidence ({len(failures)} failed)", ""]
    for failure in failures:
        test_dir = out_dir / _safe(failure.name)
        test_dir.mkdir(exist_ok=True)
        copied = []
        for att in failure.attachments:
            src = results_dir / att.source
            if att.source and src.exists():
                suffix = src.suffix or ".bin"
                dest = test_dir / f"{_safe(att.name) or 'attachment'}{suffix}"
                shutil.copy(src, dest)
                copied.append(dest.relative_to(out_dir))
        lines += [
            f"## {failure.name}",
            f"- full name: `{failure.full_name}`",
            f"- status: {failure.status}",
            "",
            "### Error message",
            "```",
            failure.message or "(none)",
            "```",
            "",
            "### Traceback",
            "```",
            failure.trace or "(none)",
            "```",
            "",
            "### Steps (what the test did before it failed)",
            "```",
            *(failure.steps or ["(none recorded)"]),
            "```",
            "",
            "### Evidence files",
            *([f"- `{p}`" for p in copied] or ["- (none captured)"]),
            "",
        ]
    report = out_dir / "REPORT.md"
    report.write_text("\n".join(lines))
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect failure evidence from Allure results.")
    parser.add_argument("--results", type=Path, default=Path("allure-results"))
    parser.add_argument("--out", type=Path, default=Path("scratch/triage"))
    args = parser.parse_args()

    if not args.results.is_dir():
        print(f"No results folder at {args.results}. Run the tests first.")
        return 2
    failures = load_failures(args.results)
    if not failures:
        print("No failed or broken tests found. Nothing to triage.")
        return 0
    if args.out.exists():
        shutil.rmtree(args.out)  # start fresh so old runs don't mix in
    report = write_report(failures, args.results, args.out)
    print(f"{len(failures)} failure(s). Report: {report}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
