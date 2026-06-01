import unittest
from datetime import datetime, timezone

from codex_skill_radar.models import RankedRepo, RepoCandidate
from codex_skill_radar.report import render_markdown


class ReportTests(unittest.TestCase):
    def test_markdown_contains_repository_and_growth(self) -> None:
        repo = RepoCandidate(
            full_name="example/codex-plugin",
            html_url="https://github.com/example/codex-plugin",
            description="Codex plugin",
            stargazers_count=42,
            forks_count=3,
            open_issues_count=1,
            language="TypeScript",
            pushed_at="2026-06-01T00:00:00Z",
            updated_at="2026-06-01T00:00:00Z",
            topics=("codex", "plugin"),
            query_matches=('"codex plugin" in:name,description,readme',),
        )
        ranked = [
            RankedRepo(
                repo=repo,
                stars_in_period=9,
                stars_capped=False,
                relevance_score=95,
                relevance_reasons=("mentions codex", "mentions plugins"),
                period_days=7,
            )
        ]
        rendered = render_markdown(
            ranked,
            generated_at=datetime(2026, 6, 1, tzinfo=timezone.utc),
            since=datetime(2026, 5, 25, tzinfo=timezone.utc),
            candidates_considered=1,
        )
        self.assertIn("example/codex-plugin", rendered)
        self.assertIn("| 1 |", rendered)
        self.assertIn("| 9 |", rendered)


if __name__ == "__main__":
    unittest.main()
