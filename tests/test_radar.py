import unittest

from codex_skill_radar.models import RepoCandidate
from codex_skill_radar.radar import rank_candidates, relevance


def candidate(
    full_name: str,
    description: str,
    stars: int = 10,
    queries: tuple[str, ...] = ('"codex skill" in:name,description,readme',),
) -> RepoCandidate:
    return RepoCandidate(
        full_name=full_name,
        html_url=f"https://github.com/{full_name}",
        description=description,
        stargazers_count=stars,
        forks_count=1,
        open_issues_count=0,
        language="Python",
        pushed_at="2026-06-01T00:00:00Z",
        updated_at="2026-06-01T00:00:00Z",
        topics=("codex", "skills"),
        query_matches=queries,
    )


class RelevanceTests(unittest.TestCase):
    def test_codex_skill_repo_scores_as_relevant(self) -> None:
        score, reasons = relevance(
            candidate("example/codex-skills", "Reusable skills for Codex CLI")
        )
        self.assertGreaterEqual(score, 70)
        self.assertIn("mentions codex", reasons)
        self.assertIn("mentions skills", reasons)

    def test_rank_prefers_window_growth_before_total_stars(self) -> None:
        slow_large = candidate("example/large", "Codex skill library", stars=5000)
        fast_small = candidate("example/fast", "Codex skill library", stars=100)
        ranked = rank_candidates(
            [slow_large, fast_small],
            {"example/large": 2, "example/fast": 12},
            period_days=7,
        )
        self.assertEqual(ranked[0].repo.full_name, "example/fast")
        self.assertEqual(ranked[0].stars_in_period, 12)
        self.assertFalse(ranked[0].stars_capped)


if __name__ == "__main__":
    unittest.main()
