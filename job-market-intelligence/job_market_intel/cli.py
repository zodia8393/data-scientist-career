from __future__ import annotations

import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv

from .errors import JobMarketIntelError, MissingCredentialError
from .models import utc_now_iso
from .normalize import normalize_raw_wrappers
from .profile import load_profile
from .providers import FixtureProvider, SaraminProvider
from .providers.specs import PROVIDER_SPECS
from .report import write_report
from .scoring import score_jobs
from .storage import (
    Workspace,
    fetch_normalized_jobs,
    fetch_scored_jobs,
    load_latest_raw_results,
    replace_normalized_jobs,
    replace_scored_jobs,
    row_counts,
    write_raw_result,
)


def main(argv: list[str] | None = None) -> int:
    load_dotenv()
    parser = build_parser()
    args = parser.parse_args(argv)
    workspace = Workspace(args.workspace)
    try:
        if args.command == "collect":
            return command_collect(args, workspace)
        if args.command == "normalize":
            return command_normalize(args, workspace)
        if args.command == "score":
            return command_score(args, workspace)
        if args.command == "report":
            return command_report(args, workspace)
        if args.command == "providers":
            return command_providers()
        if args.command == "demo":
            return command_demo(args, workspace)
    except JobMarketIntelError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    parser.print_help()
    return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Korean job market intelligence CLI")
    parser.add_argument("--workspace", default=".", help="Project workspace root")
    subparsers = parser.add_subparsers(dest="command")

    collect = subparsers.add_parser("collect", help="Collect raw postings")
    collect.add_argument("--provider", default="saramin", choices=["saramin", "fixture"])
    collect.add_argument("--limit", type=int, default=100)
    collect.add_argument("--query", default=None)
    collect.add_argument("--no-fixture-fallback", action="store_true")

    subparsers.add_parser("normalize", help="Normalize latest raw responses")

    score = subparsers.add_parser("score", help="Score normalized jobs")
    score.add_argument("--profile", default="profile.yaml")

    subparsers.add_parser("report", help="Write Markdown and HTML report")
    subparsers.add_parser("providers", help="List provider implementation and credential status")

    demo = subparsers.add_parser("demo", help="Run fixture end-to-end pipeline")
    demo.add_argument("--limit", type=int, default=100)
    demo.add_argument("--profile", default="profile.example.yaml")
    return parser


def command_collect(args: argparse.Namespace, workspace: Workspace) -> int:
    result = collect_provider(
        provider=args.provider,
        limit=args.limit,
        query=args.query,
        fixture_fallback=not args.no_fixture_fallback,
    )
    raw_path = write_raw_result(workspace, result)
    print(f"collected provider={result.provider} mode={result.mode} raw_path={raw_path}")
    return 0


def command_normalize(args: argparse.Namespace, workspace: Workspace) -> int:
    result = normalize_raw_wrappers(load_latest_raw_results(workspace))
    replace_normalized_jobs(workspace, result.jobs)
    print(
        "normalized "
        f"raw_items={result.raw_items} filtered={result.filtered_items} "
        f"deduped={result.deduped_items} duplicates={result.duplicate_items}"
    )
    return 0


def command_score(args: argparse.Namespace, workspace: Workspace) -> int:
    profile = load_profile(Path(args.profile), project_root=workspace.root)
    jobs = fetch_normalized_jobs(workspace)
    results = score_jobs(jobs, profile)
    replace_scored_jobs(workspace, results, scored_at=utc_now_iso())
    print(f"scored jobs={len(results)}")
    return 0


def command_report(args: argparse.Namespace, workspace: Workspace) -> int:
    jobs = fetch_normalized_jobs(workspace)
    records = fetch_scored_jobs(workspace)
    md_path, html_path = write_report(workspace.reports_dir, jobs, records, row_counts(workspace))
    print(f"report markdown={md_path}")
    print(f"report html={html_path}")
    return 0


def command_providers() -> int:
    for spec in PROVIDER_SPECS.values():
        env_names = ", ".join(spec.credential_env)
        print(f"{spec.name}\t{spec.status}\t{spec.response_format}\t{env_names}\t{spec.docs_url}")
    return 0


def command_demo(args: argparse.Namespace, workspace: Workspace) -> int:
    result = FixtureProvider().collect(limit=args.limit, query="demo fixture")
    raw_path = write_raw_result(workspace, result)
    normalized = normalize_raw_wrappers(load_latest_raw_results(workspace, provider="fixture"))
    replace_normalized_jobs(workspace, normalized.jobs)
    profile = load_profile(Path(args.profile), project_root=workspace.root)
    scored = score_jobs(normalized.jobs, profile)
    replace_scored_jobs(workspace, scored, scored_at=utc_now_iso())
    counts = row_counts(workspace)
    counts.update(
        {
            "raw_latest_items": normalized.raw_items,
            "normalized_jobs": len(normalized.jobs),
            "scored_jobs": len(scored),
        }
    )
    md_path, html_path = write_report(workspace.reports_dir, normalized.jobs, [item.as_dict() for item in scored], counts)
    print(f"demo raw_path={raw_path}")
    print(
        "demo counts "
        f"raw_items={normalized.raw_items} filtered={normalized.filtered_items} "
        f"deduped={normalized.deduped_items} scored={len(scored)}"
    )
    print(f"demo report={md_path}")
    print(f"demo html={html_path}")
    return 0


def collect_provider(
    provider: str,
    limit: int,
    query: str | None,
    fixture_fallback: bool,
):
    if provider == "fixture":
        return FixtureProvider().collect(limit=limit, query=query)
    if provider == "saramin":
        try:
            return SaraminProvider().collect(limit=limit, query=query)
        except MissingCredentialError:
            if not fixture_fallback:
                raise
            return FixtureProvider(provider_name="saramin").collect(limit=limit, query=query or "saramin fixture fallback")
    raise JobMarketIntelError(f"unsupported provider: {provider}")


if __name__ == "__main__":
    raise SystemExit(main())
