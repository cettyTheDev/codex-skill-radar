from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .models import RankedRepo, RepoCandidate


def render_markdown(
    ranked: list[RankedRepo],
    *,
    generated_at: datetime,
    since: datetime,
    candidates_considered: int,
    limit: int = 10,
) -> str:
    lines = [
        "# Codex Skill Radar",
        "",
        f"Generated: `{generated_at.isoformat()}`",
        f"Window start: `{since.isoformat()}`",
        f"Candidates considered: `{candidates_considered}`",
        "",
        "Ranking is based on GitHub stargazer events in the window, then relevance",
        "to Codex skills/plugins, then total stars.",
        "",
        "| Rank | Repository | Stars in window | Total stars | Relevance | Why matched |",
        "| ---: | --- | ---: | ---: | ---: | --- |",
    ]
    for index, item in enumerate(ranked[:limit], start=1):
        reasons = ", ".join(item.relevance_reasons) or "matched search query"
        window_stars = f"{item.stars_in_period}+" if item.stars_capped else str(item.stars_in_period)
        lines.append(
            "| {rank} | [{name}]({url}) | {window_stars} | {total_stars} | {score} | {reasons} |".format(
                rank=index,
                name=item.repo.full_name,
                url=item.repo.html_url,
                window_stars=window_stars,
                total_stars=item.repo.stargazers_count,
                score=item.relevance_score,
                reasons=_escape_table(reasons),
            )
        )
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- GitHub does not expose a native `fastest growing Codex skills` feed.",
            "- This report discovers candidates through repository search queries, then",
            "  counts recent `starred_at` events from the stargazers endpoint.",
            "- Scans can cap stargazer pages per repository to avoid excessive API use;",
            "  capped counts are shown with `+`. Use a higher `--max-star-pages`",
            "  value for more exhaustive large-repo scans.",
            "- Broad agent-skill repositories can appear when they explicitly mention",
            "  Codex compatibility.",
            "",
        ]
    )
    return "\n".join(lines)


def write_snapshot(
    path: Path,
    *,
    ranked: list[RankedRepo],
    candidates: list[RepoCandidate],
    generated_at: datetime,
    since: datetime,
) -> None:
    payload: dict[str, Any] = {
        "generated_at": generated_at.isoformat(),
        "since": since.isoformat(),
        "results": [item.to_dict() for item in ranked],
        "candidates": [candidate.to_dict() for candidate in candidates],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_snapshot(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def ranked_from_snapshot(snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    return list(snapshot.get("results") or [])


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def _escape_table(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")
