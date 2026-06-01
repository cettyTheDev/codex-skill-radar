# Methodology

Codex Skill Radar is intentionally transparent and conservative.

## Candidate Discovery

The default query set searches repository name, description, and README text for:

- `codex skill`
- `codex skills`
- `codex plugin`
- `codex plugins`
- `codex cli` with `skill` or `plugin`
- `OpenAI Codex` with `skill` or `plugin`
- `.codex-plugin`
- `SKILL.md` with `codex`

The search results are deduplicated by repository full name.

## Relevance Score

The score is a simple heuristic:

- Codex mention: strong positive signal.
- Codex CLI or OpenAI Codex mention: additional positive signal.
- Skill or `SKILL.md` mention: skill signal.
- Plugin or `.codex-plugin` mention: plugin signal.
- Multiple query matches: confidence signal.

This is not a quality score. It only explains why a repository belongs in the
candidate set.

## Growth Score

The ranking uses GitHub stargazer events:

1. Compute the time window start, such as seven days before generation.
2. Fetch stargazer pages from newest toward older pages.
3. Count `starred_at` timestamps inside the window.
4. Stop once a page contains stars older than the window.

This avoids waiting for a week of local snapshots while keeping the method
auditable.

## Interpretation

A fast-growing repository deserves manual review before use. Star growth can be
driven by announcements, social traffic, or naming overlap, and does not imply
that a skill/plugin is safe or production-ready.

