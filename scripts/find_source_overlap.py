#!/usr/bin/env python3
"""Search PR body corpora for source references, authors and creation dates.

Produced by Nick Petalas. Apache-2.0.
Reuses Douglas Colkitt's credited overlap reader without changing its bytes
or mutating its functions. Results are leads, not a novelty certificate.
"""

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    import find_overlap as legacy
finally:
    sys.path.pop(0)

ROOT = Path(__file__).resolve().parents[1]
REPO = legacy.REPO
now = legacy.now
gh_json = legacy.gh_json


def pull_records(pages):
    rows = legacy.pull_records(pages)
    originals = [pull for page in pages for pull in page]
    for row, pull in zip(rows, originals, strict=True):
        row["author"] = (pull.get("user") or {}).get("login")
        row["created_at"] = pull.get("created_at")
    return rows


def read_snapshot(cache):
    warnings = []
    empty = {"schema_version": 1, "repository": REPO, "sources": {}}
    try:
        snapshot = json.loads(cache.read_text(encoding="utf-8"))
        if (not isinstance(snapshot, dict) or snapshot.get("schema_version") != 1
                or snapshot.get("repository") != REPO or not isinstance(snapshot.get("sources"), dict)):
            raise ValueError("cache schema or repository mismatch")
    except FileNotFoundError:
        snapshot = empty
    except (OSError, ValueError) as exc:
        warnings.append("cache: unusable snapshot: " + legacy.error_summary(exc))
        snapshot = empty
    return snapshot, warnings


def cached_source(snapshot, name, max_age, need_metadata, warnings):
    cached = snapshot["sources"].get(name)
    if cached is None:
        return None, False
    try:
        stamp = legacy.validate_cached_source(cached, name)
        age = (datetime.now(timezone.utc) - stamp).total_seconds()
    except (KeyError, ValueError, TypeError) as exc:
        warnings.append(f"{name}: unusable cached source: {legacy.error_summary(exc)}")
        snapshot["sources"].pop(name, None)
        return None, False
    metadata = all(row.get("author") and row.get("created_at") for row in cached["records"])
    return cached, 0 <= age <= max_age and (metadata or not need_metadata)


def fetch_source(snapshot, name, cache):
    state = "open" if name == "open_prs" else "closed"
    records = pull_records(gh_json([
        "--paginate", "--slurp",
        f"repos/{REPO}/pulls?state={state}&per_page=100&sort=updated&direction=desc"]))
    replacement = {"fetched_at": now(), "records": records, "complete_pagination": True}
    pending = {**snapshot, "sources": {**snapshot["sources"], name: replacement}}
    legacy.atomic_json(cache, pending)
    snapshot["sources"][name] = replacement
    return replacement


def remote_snapshot(cache, offline=False, refresh=False, max_age=300,
                    include_closed=False, need_pr_metadata=False):
    snapshot, warnings = read_snapshot(cache)
    names = ("open_prs", "closed_prs") if include_closed else ("open_prs",)
    for name in names:
        cached, fresh = cached_source(snapshot, name, max_age, need_pr_metadata, warnings)
        if offline:
            warnings.append(f"{name}: offline; cached data may miss current changes")
        elif refresh or not fresh:
            try:
                cached = fetch_source(snapshot, name, cache)
            except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as exc:
                warnings.append(f"{name}: refresh failed; using old data if available: "
                                + legacy.error_summary(exc))
        if cached is None:
            warnings.append(f"{name}: no usable remote snapshot")
            snapshot["sources"].pop(name, None)
    return snapshot, warnings


def reference_number(value):
    if not re.fullmatch(r"[1-9][0-9]{0,9}", value):
        raise argparse.ArgumentTypeError("reference must be a positive ASCII issue/PR number")
    return value


def creation_cutoff(value):
    try:
        if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
            raise ValueError("expected YYYY-MM-DD")
        return datetime.strptime(value, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("creation cutoff must be a valid YYYY-MM-DD UTC date") from exc


def filter_pulls(records, author=None, created_since=None):
    """Reject unknown filter metadata rather than silently omit a possible lead."""
    selected, unknown = [], []
    for row in records:
        login, stamp = row.get("author"), row.get("created_at")
        created = None
        if created_since is not None and isinstance(stamp, str):
            try:
                created = datetime.fromisoformat(stamp)
            except ValueError:
                pass
        if ((author is not None and (not isinstance(login, str) or not login))
                or (created_since is not None and (created is None or created.tzinfo is None))):
            unknown.append(row["number"])
            continue
        if author is not None and login.lower() != author.lower():
            continue
        if created_since is not None and created < created_since:
            continue
        selected.append(row)
    if unknown:
        examples = ", ".join(str(number) for number in sorted(unknown)[:20])
        raise ValueError(f"PR filter metadata unavailable for {len(unknown)} records ({examples}); "
                         "refresh the cache or inspect an unfiltered report; unknown is not no overlap")
    return selected


def parse_arguments():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("terms", nargs="*", help="literal case-insensitive PR title/body terms")
    parser.add_argument("--reference", action="append", type=reference_number, default=[], metavar="NUMBER")
    parser.add_argument("--pr-author", metavar="LOGIN")
    parser.add_argument("--created-since", type=creation_cutoff, metavar="YYYY-MM-DD")
    parser.add_argument("--include-closed", action="store_true", help="also fetch/search closed and merged PRs")
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument("--max-age", type=int, default=300)
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--all-terms", action="store_true")
    parser.add_argument("--json", action="store_true", dest="json_output")
    cache_root = Path(os.environ.get("XDG_CACHE_HOME", str(Path.home() / ".cache")))
    parser.add_argument("--cache", type=Path, default=cache_root / "integer-mult-bounds/source-overlap.json")
    args = parser.parse_args()
    if args.max_age < 0 or args.limit < 1 or (args.offline and args.refresh):
        parser.error("use nonnegative max-age, positive limit, and either offline or refresh")
    if args.pr_author is not None and not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9-]{0,38}", args.pr_author):
        parser.error("--pr-author requires a GitHub login, not @me or a search expression")
    if args.cache.resolve().is_relative_to(ROOT.resolve()):
        parser.error("keep the cache outside the repository")
    if not args.reference and not any(term.strip() for term in args.terms):
        parser.error("provide terms or --reference")
    return parser, args


def write_report(report, args):
    if args.json_output:
        print(json.dumps(report, indent=2))
        return
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="backslashreplace")
    print(report["status"])
    print("Coverage: " + json.dumps(report["coverage"]))
    print("PR filters: " + json.dumps(report["pr_filters"]))
    print(report["limits"])
    for warning in report["warnings"]:
        print("WARNING: " + warning)
    print(f"{report['matches_total']} possible matches; showing {len(report['matches'])}")
    for match in report["matches"]:
        print(f"\n[pr {match['number']}] {match['title']}\n{match.get('url', '')}")
        print(match["excerpt"])


def main():
    parser, args = parse_arguments()
    filtered = args.pr_author is not None or args.created_since is not None
    snapshot, warnings = remote_snapshot(args.cache, args.offline, args.refresh, args.max_age,
                                         args.include_closed, filtered)
    try:
        records = filter_pulls(legacy.pull_corpus(snapshot, args.include_closed),
                               args.pr_author, args.created_since)
    except ValueError as exc:
        parser.error(str(exc))
    references = list(dict.fromkeys(args.reference))
    terms = [*args.terms, *references]
    matches = legacy.search(records, terms, args.all_terms, references)
    names = ("open_prs", "closed_prs") if args.include_closed else ("open_prs",)
    coverage = {}
    for name in names:
        source = snapshot["sources"].get(name)
        coverage[name] = ({"fetched_at": source["fetched_at"], "records": len(source["records"]),
                           "complete_pagination": source["complete_pagination"]} if source else None)
    report = {"status": "POSSIBLE_OVERLAP_NOT_A_NOVELTY_CERTIFICATE", "searched_at": now(),
              "terms": terms, "reference_terms": references, "coverage": coverage, "warnings": warnings,
              "pr_filters": {"author": args.pr_author,
                             "created_since": args.created_since.isoformat() if args.created_since else None,
                             "scope": "PR titles and bodies only; local notes and Discussions excluded",
                             "records_after_filter": len(records)},
              "limits": ("PR titles/bodies only; local notes and Discussions are excluded. "
                         + ("Closed/merged PRs are included with separate timestamps. " if args.include_closed
                            else "Closed/merged PRs are excluded; use --include-closed. ")
                         + "Creation dates are not update dates. Unknown filter metadata is an error. "
                         "Snapshots are not atomic; no diffs or semantic equivalence are checked. "
                         "Matches are overlap leads, not a novelty certificate."),
              "matches_total": len(matches), "matches": matches[:args.limit]}
    write_report(report, args)


if __name__ == "__main__":
    main()
