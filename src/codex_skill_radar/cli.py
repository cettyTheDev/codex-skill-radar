from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

from .github import GitHubClient
from .radar import scan
from .report import render_markdown, utc_now, write_snapshot


def cmd_scan(args: argparse.Namespace) -> None:
    client = GitHubClient()
    generated_at = utc_now()
    ranked, since, candidates = scan(
        client,
        days=args.days,
        per_query=args.per_query,
        max_pages=args.max_pages,
        max_candidates=args.max_candidates,
        max_star_pages=args.max_star_pages,
        min_relevance=args.min_relevance,
        now=generated_at,
    )
    report = render_markdown(
        ranked,
        generated_at=generated_at,
        since=since,
        candidates_considered=len(candidates),
        limit=args.limit,
    )
    if args.report:
        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(report, encoding="utf-8")
    else:
        print(report)
    if args.snapshot:
        write_snapshot(
            Path(args.snapshot),
            ranked=ranked,
            candidates=candidates,
            generated_at=generated_at,
            since=since,
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="codex-skill-radar",
        description="Rank fast-growing GitHub repositories related to Codex skills/plugins.",
    )
    subparsers = parser.add_subparsers(required=True)

    scan_parser = subparsers.add_parser("scan", help="discover and rank repositories")
    scan_parser.add_argument("--days", type=int, default=7, help="growth window in days")
    scan_parser.add_argument("--limit", type=int, default=10, help="rows to render")
    scan_parser.add_argument("--per-query", type=int, default=20, help="search results per query")
    scan_parser.add_argument("--max-pages", type=int, default=1, help="GitHub search pages per query")
    scan_parser.add_argument("--max-candidates", type=int, default=80, help="repos to inspect for stars")
    scan_parser.add_argument(
        "--max-star-pages",
        type=int,
        default=10,
        help="max stargazer GraphQL pages per repo; each page is 100 stars",
    )
    scan_parser.add_argument("--min-relevance", type=int, default=45, help="minimum relevance score")
    scan_parser.add_argument("--report", help="write Markdown report to this path")
    scan_parser.add_argument("--snapshot", help="write JSON snapshot to this path")
    scan_parser.set_defaults(func=cmd_scan)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if hasattr(args, "days") and args.days <= 0:
        parser.error("--days must be positive")
    if hasattr(args, "max_star_pages") and args.max_star_pages <= 0:
        parser.error("--max-star-pages must be positive")
    args.func(args)


if __name__ == "__main__":
    main()
