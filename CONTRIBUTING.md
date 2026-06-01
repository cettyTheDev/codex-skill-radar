# Contributing

Thanks for improving Codex Skill Radar.

## Local Checks

```bash
python -m unittest discover -s tests
PYTHONPATH=src python -m codex_skill_radar.cli scan --help
```

## Contribution Guidelines

- Keep ranking heuristics explainable.
- Add tests for any scoring or report-format change.
- Do not commit API tokens, local snapshots with private data, or generated
  files outside `data/` and `reports/`.
- Prefer small pull requests with one behavioral change.

