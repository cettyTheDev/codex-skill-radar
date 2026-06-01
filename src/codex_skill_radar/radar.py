from __future__ import annotations

from datetime import datetime, timedelta, timezone

from .github import GitHubClient
from .models import RankedRepo, RepoCandidate


DEFAULT_QUERIES = (
    '"codex skill" in:name,description,readme',
    '"codex skills" in:name,description,readme',
    '"codex plugin" in:name,description,readme',
    '"codex plugins" in:name,description,readme',
    '"codex cli" skill in:name,description,readme',
    '"codex cli" plugin in:name,description,readme',
    '"OpenAI Codex" skill in:readme',
    '"OpenAI Codex" plugin in:readme',
    '".codex-plugin" in:readme',
    '"SKILL.md" codex in:readme',
)


def discover_candidates(
    client: GitHubClient,
    queries: tuple[str, ...] = DEFAULT_QUERIES,
    per_query: int = 25,
    max_pages: int = 1,
) -> list[RepoCandidate]:
    by_name: dict[str, RepoCandidate] = {}
    for query in queries:
        for item in client.search_repositories(query, per_page=per_query, max_pages=max_pages):
            candidate = RepoCandidate.from_search_item(item, query)
            if not candidate.full_name:
                continue
            existing = by_name.get(candidate.full_name)
            by_name[candidate.full_name] = existing.merge_query(query) if existing else candidate
    return list(by_name.values())


def relevance(candidate: RepoCandidate) -> tuple[int, tuple[str, ...]]:
    text = " ".join(
        [
            candidate.full_name,
            candidate.description,
            candidate.language,
            " ".join(candidate.topics),
            " ".join(candidate.query_matches),
        ]
    ).lower()
    score = 0
    reasons: list[str] = []

    if "codex" in text:
        score += 45
        reasons.append("mentions codex")
    if "openai codex" in text or "codex cli" in text:
        score += 15
        reasons.append("mentions OpenAI Codex/Codex CLI")
    if "skill" in text or "skills" in text or "skill.md" in text:
        score += 25
        reasons.append("mentions skills")
    if "plugin" in text or "plugins" in text or ".codex-plugin" in text:
        score += 25
        reasons.append("mentions plugins")
    if ".codex-plugin" in text:
        score += 20
        reasons.append("mentions .codex-plugin")
    if "skill.md" in text:
        score += 10
        reasons.append("mentions SKILL.md")
    if len(candidate.query_matches) > 1:
        score += min(20, 5 * (len(candidate.query_matches) - 1))
        reasons.append("matched multiple search queries")

    return score, tuple(reasons)


def rank_candidates(
    candidates: list[RepoCandidate],
    stars_by_repo: dict[str, int],
    period_days: int,
    min_relevance: int = 45,
    capped_by_repo: dict[str, bool] | None = None,
) -> list[RankedRepo]:
    capped_by_repo = capped_by_repo or {}
    ranked = []
    for candidate in candidates:
        score, reasons = relevance(candidate)
        if score < min_relevance:
            continue
        ranked.append(
            RankedRepo(
                repo=candidate,
                stars_in_period=int(stars_by_repo.get(candidate.full_name, 0)),
                stars_capped=bool(capped_by_repo.get(candidate.full_name, False)),
                relevance_score=score,
                relevance_reasons=reasons,
                period_days=period_days,
            )
        )
    return sorted(
        ranked,
        key=lambda item: (
            item.stars_in_period,
            item.relevance_score,
            item.repo.stargazers_count,
            item.repo.full_name.lower(),
        ),
        reverse=True,
    )


def scan(
    client: GitHubClient,
    days: int = 7,
    per_query: int = 25,
    max_pages: int = 1,
    max_candidates: int = 80,
    max_star_pages: int = 10,
    min_relevance: int = 45,
    now: datetime | None = None,
) -> tuple[list[RankedRepo], datetime, list[RepoCandidate]]:
    current_time = now or datetime.now(timezone.utc)
    since = current_time - timedelta(days=days)
    candidates = discover_candidates(client, per_query=per_query, max_pages=max_pages)
    scored_candidates = sorted(
        candidates,
        key=lambda item: (relevance(item)[0], item.stargazers_count),
        reverse=True,
    )[:max_candidates]
    stars_by_repo: dict[str, int] = {}
    capped_by_repo: dict[str, bool] = {}
    for candidate in scored_candidates:
        count = client.count_stars_since(
            candidate.full_name,
            candidate.stargazers_count,
            since,
            max_pages=max_star_pages,
        )
        stars_by_repo[candidate.full_name] = count
        capped_by_repo[candidate.full_name] = count >= max_star_pages * 100
    ranked = rank_candidates(
        scored_candidates,
        stars_by_repo,
        days,
        min_relevance,
        capped_by_repo=capped_by_repo,
    )
    return ranked, since, scored_candidates
