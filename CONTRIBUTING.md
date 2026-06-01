# Contributing

Thanks for improving Codex Skill Radar.

## Local Checks

```bash
python -m unittest discover -s tests
PYTHONPATH=src python -m codex_skill_radar.cli scan --help
```

## Branches and Pull Requests

- Create a focused branch for each fix or feature.
- Open an issue first for ranking-method changes that affect report output.
- In pull requests, include the command you ran and a short risk note.
- Keep generated reports small enough to review.

## Style

- Keep code standard-library-only unless a dependency removes real complexity.
- Prefer explicit dataclasses and small functions over hidden global state.
- Format Markdown tables so generated reports remain readable in GitHub.
- When adding new scoring rules, document the reason in `docs/methodology.md`.

## Contribution Guidelines

- Keep ranking heuristics explainable.
- Add tests for any scoring or report-format change.
- Run lint or static checks if you introduce a new tool for them.
- Do not commit API tokens, local snapshots with private data, or generated
  files outside `data/` and `reports/`.
- Prefer small pull requests with one behavioral change.
