# Codex Skill Radar

[![CI](https://github.com/cettyTheDev/codex-skill-radar/actions/workflows/ci.yml/badge.svg)](https://github.com/cettyTheDev/codex-skill-radar/actions/workflows/ci.yml)

Find fast-growing GitHub repositories related to Codex skills and plugins.

The radar discovers candidate repositories with GitHub repository search, then
counts `starred_at` events from the stargazers API for a recent window. This
means it can produce a 7-day ranking without waiting for a local baseline
snapshot to accumulate.

## Project Status

- Latest release: [v0.1.2](https://github.com/cettyTheDev/codex-skill-radar/releases/tag/v0.1.2)
- CI: Python 3.10, 3.11, and 3.12 on GitHub Actions.
- Maintenance surface: issue templates, pull request template, security policy, contribution guide, and code of conduct.
- Latest generated report: [reports/latest.md](reports/latest.md)
- Methodology notes: [docs/methodology.md](docs/methodology.md)

## What It Tracks

- Repositories that mention Codex skills, Codex plugins, `SKILL.md`, or
  `.codex-plugin`.
- Cross-agent skill/plugin libraries when they explicitly mention Codex
  compatibility.
- Recent star velocity, total stars, and a transparent relevance score.

## Quick Start

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e .
export GITHUB_TOKEN="$(gh auth token)"  # optional, but strongly recommended

codex-skill-radar scan \
  --days 7 \
  --limit 10 \
  --per-query 5 \
  --max-candidates 10 \
  --max-star-pages 2 \
  --report reports/latest.md \
  --snapshot data/snapshots/latest.json
```

For a slower but more complete scan, raise `--max-candidates` and
`--max-star-pages`.

You can also run it without installing:

```bash
PYTHONPATH=src python -m codex_skill_radar.cli scan --days 7 --limit 10
```

## Output

- `reports/latest.md` is a readable Top 10 report.
- `data/snapshots/latest.json` keeps the raw ranked results and considered
  candidates.

## Method

1. Search GitHub repositories with targeted queries such as `"codex skill"`,
   `"codex plugin"`, `"SKILL.md" codex`, and `".codex-plugin"`.
2. Deduplicate repositories across search queries.
3. Score relevance from repository name, description, topics, language, and
   matched search queries.
4. Count recent stargazer events through GitHub's stargazers API.
5. Sort by stars in the window, relevance score, and total stars.

## Limitations

- GitHub does not provide an official "fastest-growing Codex skill" category.
- Repository search can include broad agent-skill projects that support many
  tools, not only Codex.
- Star velocity is a signal for attention, not code quality or safety.
- Very large repositories may require more API calls to inspect their recent
  stargazer pages. Use `--max-star-pages` to trade off speed and completeness.

## Development

```bash
python -m unittest discover -s tests
PYTHONPATH=src python -m codex_skill_radar.cli scan --help
```

## Roadmap

- Add allow/deny lists for manually curated sources.
- Add CSV export.
- Add GitHub issue reporting for weekly snapshots.
- Add optional safety metadata checks for detected skill/plugin repos.
