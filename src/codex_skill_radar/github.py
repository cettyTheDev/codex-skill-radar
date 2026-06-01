from __future__ import annotations

import json
import math
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from typing import Any


DEFAULT_API_BASE = "https://api.github.com"
DEFAULT_TIMEOUT = 30


class GitHubApiError(RuntimeError):
    """Raised when the GitHub API returns an error response."""


class GitHubClient:
    def __init__(
        self,
        token: str | None = None,
        api_base: str = DEFAULT_API_BASE,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        self.token = token or os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
        self.api_base = api_base.rstrip("/")
        self.timeout = timeout

    def request(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        accept: str = "application/vnd.github+json",
    ) -> Any:
        query = urllib.parse.urlencode(params or {})
        url = f"{self.api_base}/{path.lstrip('/')}"
        if query:
            url = f"{url}?{query}"
        headers = {
            "Accept": accept,
            "User-Agent": "codex-skill-radar",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        request = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                if response.status == 204:
                    return None
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise GitHubApiError(f"GitHub API {exc.code} for {url}: {detail}") from exc
        except urllib.error.URLError as exc:
            raise GitHubApiError(f"GitHub API request failed for {url}: {exc}") from exc

    def graphql(self, query: str, variables: dict[str, Any]) -> dict[str, Any]:
        if not self.token:
            raise GitHubApiError("GraphQL requests require GITHUB_TOKEN or GH_TOKEN")
        url = f"{self.api_base}/graphql"
        payload = json.dumps({"query": query, "variables": variables}).encode("utf-8")
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "User-Agent": "codex-skill-radar",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        request = urllib.request.Request(url, data=payload, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                body = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise GitHubApiError(f"GitHub GraphQL {exc.code}: {detail}") from exc
        except urllib.error.URLError as exc:
            raise GitHubApiError(f"GitHub GraphQL request failed: {exc}") from exc
        if body.get("errors"):
            raise GitHubApiError(f"GitHub GraphQL errors: {body['errors']}")
        return body["data"]

    def search_repositories(
        self,
        query: str,
        per_page: int = 30,
        max_pages: int = 1,
        sort: str = "stars",
        order: str = "desc",
    ) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        for page in range(1, max_pages + 1):
            data = self.request(
                "/search/repositories",
                {
                    "q": query,
                    "sort": sort,
                    "order": order,
                    "per_page": per_page,
                    "page": page,
                },
            )
            page_items = data.get("items", [])
            items.extend(page_items)
            if len(page_items) < per_page:
                break
            # The Search API has stricter secondary limits; a tiny pause helps.
            time.sleep(0.2)
        return items

    def count_stars_since(
        self,
        full_name: str,
        total_stars: int,
        since: datetime,
        per_page: int = 100,
        max_pages: int = 10,
    ) -> int:
        if self.token:
            return self.count_stars_since_graphql(
                full_name,
                since,
                per_page=per_page,
                max_pages=max_pages,
            )
        if total_stars <= 0:
            return 0
        page = max(1, math.ceil(total_stars / per_page))
        count = 0
        while page >= 1:
            data = self.request(
                f"/repos/{full_name}/stargazers",
                {"per_page": per_page, "page": page},
                accept="application/vnd.github.star+json",
            )
            if not data:
                break
            page_dates = []
            for event in data:
                starred_at = event.get("starred_at")
                if not starred_at:
                    continue
                timestamp = parse_github_datetime(starred_at)
                page_dates.append(timestamp)
                if timestamp >= since:
                    count += 1
            if page_dates and min(page_dates) < since:
                break
            page -= 1
            time.sleep(0.1)
        return count

    def count_stars_since_graphql(
        self,
        full_name: str,
        since: datetime,
        per_page: int = 100,
        max_pages: int = 10,
    ) -> int:
        owner, name = full_name.split("/", 1)
        query = """
        query($owner: String!, $name: String!, $first: Int!, $cursor: String) {
          repository(owner: $owner, name: $name) {
            stargazers(
              first: $first,
              after: $cursor,
              orderBy: {field: STARRED_AT, direction: DESC}
            ) {
              pageInfo {
                hasNextPage
                endCursor
              }
              edges {
                starredAt
              }
            }
          }
        }
        """
        cursor = None
        count = 0
        for _ in range(max_pages):
            data = self.graphql(
                query,
                {"owner": owner, "name": name, "first": per_page, "cursor": cursor},
            )
            repo = data.get("repository")
            if not repo:
                return count
            stargazers = repo["stargazers"]
            edges = stargazers.get("edges") or []
            if not edges:
                return count
            saw_older = False
            for edge in edges:
                timestamp = parse_github_datetime(edge["starredAt"])
                if timestamp >= since:
                    count += 1
                else:
                    saw_older = True
            if saw_older or not stargazers["pageInfo"]["hasNextPage"]:
                return count
            cursor = stargazers["pageInfo"]["endCursor"]
            time.sleep(0.05)
        return count


def parse_github_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))
