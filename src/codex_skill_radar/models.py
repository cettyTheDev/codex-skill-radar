from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class RepoCandidate:
    full_name: str
    html_url: str
    description: str
    stargazers_count: int
    forks_count: int
    open_issues_count: int
    language: str
    pushed_at: str
    updated_at: str
    topics: tuple[str, ...]
    query_matches: tuple[str, ...]

    @classmethod
    def from_search_item(cls, item: dict[str, Any], query: str) -> "RepoCandidate":
        return cls(
            full_name=item.get("full_name", ""),
            html_url=item.get("html_url", ""),
            description=item.get("description") or "",
            stargazers_count=int(item.get("stargazers_count") or 0),
            forks_count=int(item.get("forks_count") or 0),
            open_issues_count=int(item.get("open_issues_count") or 0),
            language=item.get("language") or "",
            pushed_at=item.get("pushed_at") or "",
            updated_at=item.get("updated_at") or "",
            topics=tuple(item.get("topics") or ()),
            query_matches=(query,),
        )

    def merge_query(self, query: str) -> "RepoCandidate":
        if query in self.query_matches:
            return self
        return RepoCandidate(
            full_name=self.full_name,
            html_url=self.html_url,
            description=self.description,
            stargazers_count=self.stargazers_count,
            forks_count=self.forks_count,
            open_issues_count=self.open_issues_count,
            language=self.language,
            pushed_at=self.pushed_at,
            updated_at=self.updated_at,
            topics=self.topics,
            query_matches=tuple((*self.query_matches, query)),
        )

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["topics"] = list(self.topics)
        data["query_matches"] = list(self.query_matches)
        return data


@dataclass(frozen=True)
class RankedRepo:
    repo: RepoCandidate
    stars_in_period: int
    stars_capped: bool
    relevance_score: int
    relevance_reasons: tuple[str, ...]
    period_days: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "full_name": self.repo.full_name,
            "html_url": self.repo.html_url,
            "description": self.repo.description,
            "language": self.repo.language,
            "total_stars": self.repo.stargazers_count,
            "forks": self.repo.forks_count,
            "open_issues": self.repo.open_issues_count,
            "stars_in_period": self.stars_in_period,
            "stars_capped": self.stars_capped,
            "period_days": self.period_days,
            "relevance_score": self.relevance_score,
            "relevance_reasons": list(self.relevance_reasons),
            "topics": list(self.repo.topics),
            "pushed_at": self.repo.pushed_at,
            "updated_at": self.repo.updated_at,
            "query_matches": list(self.repo.query_matches),
        }
