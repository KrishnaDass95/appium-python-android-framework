# Sample triage output

A real run, kept in the repo so you can see what the AI-assisted workflow produces without a device.

Scenario: `_sort_button` in `pages/catalog_page.py` was changed from `sortIV` to `sortIV_renamed` (a deliberate break), then `test_sort_by_name[name-asc]` was run on an emulator.

- `REPORT.md`: output of `uv run python -m ai.evidence` (error, traceback, steps, source state).
- `TRIAGE.md`: output of the `/triage` Claude Code command reading that report plus the screenshot and page source.

The screenshot and page source are not committed (size). Generate them yourself by running a failing test, then see `scratch/triage/` (gitignored) or the `failure-evidence` CI artifact.
