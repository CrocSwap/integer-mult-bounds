#!/usr/bin/env python3
"""Search PR bodies, discussion claims and local package READMEs for possible overlap.

Standard library + optional authenticated gh CLI. Remote snapshots live outside
the checkout. Results are leads, not a novelty certificate. Douglas Colkitt,
with OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from datetime import datetime, timezone
import fnmatch
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tempfile
import time

# Retain direct script execution under -I; the shared helper uses stdlib only.
sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from research_package import git_source_env
finally:
    sys.path.pop(0)

ROOT = Path(__file__).resolve().parents[1]
REPO = "CrocSwap/integer-mult-bounds"


def now():
    return datetime.now(timezone.utc).isoformat()


def gh_json(args, payload=None):
    # --slurp is absent from older gh releases. Normalize it here so callers
    # keep their nested-page contract. @json emits one compact array per page
    # and escapes embedded newlines in PR titles and bodies.
    paginated = "--paginate" in args
    if paginated:
        args = [arg for arg in args if arg != "--slurp"] + ["--jq", "@json"]
    result = subprocess.run(
        ["gh", "api", *args], input=None if payload is None else json.dumps(payload),
        text=True, encoding="utf-8", capture_output=True, timeout=90, check=True,
    )
    if paginated:
        pages = [json.loads(line) for line in result.stdout.split("\n") if line]
        if not pages or not all(isinstance(page, list) for page in pages):
            raise ValueError("expected one JSON array per REST page")
        return pages
    value = json.loads(result.stdout)
    if isinstance(value, dict) and value.get("errors"):
        raise ValueError("GitHub GraphQL errors: " + json.dumps(value["errors"]))
    return value


def graphql(query, variables):
    return gh_json(["graphql", "--input", "-"], {"query": query, "variables": variables})["data"]


def pull_records(pages):
    return [{"kind": "pr", "number": pr["number"], "title": pr["title"],
             "body": pr.get("body") or "", "url": pr["html_url"],
             "head": pr["head"]["sha"], "base": pr.get("base", {}).get("sha"),
             "updated_at": pr["updated_at"],
             "draft": pr.get("draft", False), "state": pr["state"]}
            for page in pages for pr in page]


def pull_file_record(pull):
    """Collect every available path, bound to both endpoints and advertised count."""
    if not pull.get("headRefOid") or not pull.get("baseRefOid"):
        raise ValueError("PR file inventory is missing a head or base OID")
    connection = pull.get("files")
    paths, cursors = set(), set()
    while connection is not None:
        paths.update(node["path"] for node in connection["nodes"] if node)
        if not connection["pageInfo"]["hasNextPage"]:
            break
        cursor = connection["pageInfo"].get("endCursor")
        if not cursor or cursor in cursors:
            raise ValueError("PR file pagination did not advance")
        cursors.add(cursor)
        page = graphql('''query($number:Int!, $cursor:String!) {
          repository(owner:"CrocSwap",name:"integer-mult-bounds") {
            pullRequest(number:$number) {
              headRefOid baseRefOid changedFiles files(first:100,after:$cursor) {
                pageInfo {hasNextPage endCursor} nodes {path}
              }
            }
          }
        }''', {"number": pull["number"], "cursor": cursor})["repository"]["pullRequest"]
        if ((page.get("headRefOid"), page.get("baseRefOid"), page["changedFiles"])
                != (pull["headRefOid"], pull["baseRefOid"], pull["changedFiles"])):
            raise ValueError("PR changed during file pagination")
        connection = page["files"]
        if connection is None:
            raise ValueError("PR file continuation unavailable")
    return {"number": pull["number"], "head": pull["headRefOid"], "base": pull["baseRefOid"],
            "paths": sorted(paths),
            "truncated": connection is None or len(paths) != pull["changedFiles"]}


def fetch_pr_files():
    """Changed file paths per open PR, so overlap can be searched by path.

    Follow 100-file pages; missing lists or count shortfalls remain explicitly
    truncated. This is a file inventory, not a search of diff contents.
    """
    rows = []
    cursor = None
    while True:
        # ponytail: 10 PRs per page (25x100-node pages exceed GitHub's ~10 s
        # gateway limit and 502; 10x100 stays under it). A full index refresh is
        # ~74 pages and only path queries pay it. Each page gets four attempts.
        result = None
        for attempt in range(4):
            try:
                result = graphql('''query($cursor:String) {
          repository(owner:"CrocSwap",name:"integer-mult-bounds") {
            pullRequests(first:10,states:OPEN,after:$cursor) {
              pageInfo {hasNextPage endCursor}
              nodes {number headRefOid baseRefOid changedFiles files(first:100) {
                pageInfo {hasNextPage endCursor}
                nodes {path}
              }}
            }
          }
        }''', {"cursor": cursor})["repository"]["pullRequests"]
                break
            except subprocess.SubprocessError:
                if attempt == 3:
                    raise
                time.sleep(1 + attempt)
        for pull in result["nodes"]:
            # PR 376 (and similar) report no file list; record it as empty and
            # flagged so path search never silently trusts missing data.
            rows.append(pull_file_record(pull))
        if not result["pageInfo"]["hasNextPage"]:
            return sorted(rows, key=lambda row: row["number"])
        cursor = result["pageInfo"]["endCursor"]


def path_report(pr_records, file_rows, patterns):
    """Open-PR entries whose changed files match any pattern (fnmatch or substring)."""
    pulls = {record["number"]: record for record in pr_records if record.get("kind") == "pr"}
    matches = []
    for row in sorted(file_rows, key=lambda item: -item["number"]):
        matched = [path for path in row["paths"]
                   if any(fnmatch.fnmatch(path, pattern) or pattern in path for pattern in patterns)]
        if not matched:
            continue
        pull = pulls.get(row["number"], {})
        matches.append({"kind": "pr", "number": row["number"], "title": pull.get("title", ""),
                        "url": pull.get("url") or f"https://github.com/{REPO}/pull/{row['number']}",
                        "head": row.get("head"), "body_head": pull.get("head"),
                        "head_matches": bool(row.get("head") and row["head"] == pull.get("head")),
                        "base": row.get("base"), "body_base": pull.get("base"),
                        "base_matches": bool(row.get("base") and row["base"] == pull.get("base")),
                        "updated_at": pull.get("updated_at"), "draft": pull.get("draft", False),
                        "matched_paths": matched, "changed_paths": len(row["paths"]),
                        "truncated": row.get("truncated", False)})
    return matches


def fetch_discussions():
    records = []
    cursor = None
    while True:
        result = graphql('''query($cursor:String) {
          repository(owner:"CrocSwap",name:"integer-mult-bounds") {
            discussions(first:10,after:$cursor) {
              pageInfo {hasNextPage endCursor}
              nodes {id number title body url updatedAt comments(first:25) {
                pageInfo {hasNextPage endCursor}
                nodes {id body url updatedAt replies(first:10) {
                  pageInfo {hasNextPage endCursor} nodes {body url updatedAt}
                }}
              }}
            }
          }
        }''', {"cursor": cursor})["repository"]["discussions"]
        for discussion in result["nodes"]:
            common = {"number": discussion["number"], "title": discussion["title"]}
            records.append({**common, "kind": "discussion", "body": discussion["body"],
                            "url": discussion["url"], "updated_at": discussion["updatedAt"]})
            # Batch small first pages without a process/API round trip for
            # every discussion. The worst-case nested node count is only
            # 10 + 10*25 + 10*25*10 = 2760; busy threads still page fully.
            connection = discussion["comments"]
            while True:
                for comment in connection["nodes"]:
                    records.append({**common, "kind": "discussion-comment", "body": comment["body"],
                                    "url": comment["url"], "updated_at": comment["updatedAt"]})
                    replies = comment["replies"]
                    while True:
                        for reply in replies["nodes"]:
                            records.append({**common, "kind": "discussion-reply", "body": reply["body"],
                                            "url": reply["url"], "updated_at": reply["updatedAt"]})
                        if not replies["pageInfo"]["hasNextPage"]:
                            break
                        replies = graphql('''query($id:ID!, $cursor:String) {
                          node(id:$id) { ... on DiscussionComment {
                            replies(first:100,after:$cursor) {
                              pageInfo {hasNextPage endCursor} nodes {body url updatedAt}
                            }
                          }}
                        }''', {"id": comment["id"], "cursor": replies["pageInfo"]["endCursor"]})["node"]["replies"]
                if not connection["pageInfo"]["hasNextPage"]:
                    break
                connection = graphql('''query($id:ID!, $cursor:String) {
                  node(id:$id) { ... on Discussion {
                    comments(first:100,after:$cursor) {
                      pageInfo {hasNextPage endCursor}
                      nodes {id body url updatedAt replies(first:100) {
                        pageInfo {hasNextPage endCursor} nodes {body url updatedAt}
                      }}
                    }
                  }}
                }''', {"id": discussion["id"],
                       "cursor": connection["pageInfo"]["endCursor"]})["node"]["comments"]
        if not result["pageInfo"]["hasNextPage"]:
            return records
        cursor = result["pageInfo"]["endCursor"]


def atomic_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as out:
        tmp = Path(out.name)
        json.dump(data, out)
        out.write("\n")
    try:
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)


def error_summary(exc):
    if isinstance(exc, subprocess.CalledProcessError):
        return (exc.stderr or str(exc))[:700]
    return str(exc)[:700]


def remote_snapshot(cache, offline=False, refresh=False, max_age=300, need_files=False,
                    include_closed=False):
    warnings = []
    try:
        snapshot = json.loads(cache.read_text(encoding="utf-8"))
        if snapshot.get("schema_version") != 1 or snapshot.get("repository") != REPO:
            raise ValueError("cache schema or repository mismatch")
    except (OSError, ValueError):
        snapshot = {"schema_version": 1, "repository": REPO, "sources": {}}
    sources = snapshot.setdefault("sources", {})
    fetches = [("open_prs", lambda: pull_records(gh_json([
        "--paginate", "--slurp", f"repos/{REPO}/pulls?state=open&per_page=100&sort=updated&direction=desc"]))),
        ("discussions", fetch_discussions)]
    if include_closed:
        # Separate coverage and cache identity: an open-only snapshot cannot
        # satisfy a request for closed (including merged) PR bodies.
        fetches.append(("closed_prs", lambda: pull_records(gh_json([
            "--paginate", "--slurp", f"repos/{REPO}/pulls?state=closed&per_page=100&sort=updated&direction=desc"]))))
    if need_files:
        # Only path queries pay for the changed-file index; body searches stay as they were.
        fetches.append(("pr_files", fetch_pr_files))
    for name, fetch in fetches:
        cached = sources.get(name)
        age = None
        if cached:
            try:
                age = (datetime.now(timezone.utc) - datetime.fromisoformat(cached["fetched_at"])).total_seconds()
            except (KeyError, ValueError, TypeError):
                cached = None
        fresh = cached is not None and age is not None and 0 <= age <= max_age
        if need_files and name in ("pr_files", "open_prs") and cached:
            # Old schema-1 caches omitted endpoints. Refresh only affected sources;
            # offline/failed refreshes retain the evidence with explicit warnings.
            fresh = fresh and all(row.get("head") and row.get("base") for row in cached["records"])
        if offline:
            warnings.append(f"{name}: offline; cached data may miss current changes")
        elif refresh or not fresh:
            try:
                # Replace each source only after every page succeeds.
                records = fetch()
                sources[name] = {"fetched_at": now(), "records": records, "complete_pagination": True}
                atomic_json(cache, snapshot)
                cached = sources[name]
            except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as exc:
                warnings.append(f"{name}: refresh failed; using old data if available: {error_summary(exc)}")
        if not cached:
            warnings.append(f"{name}: no usable remote snapshot")
            sources.pop(name, None)
    return snapshot, warnings


def pull_corpus(snapshot, include_closed=False):
    """One body per PR; a state change between snapshots must not double it."""
    pulls = {}
    names = ("open_prs", "closed_prs") if include_closed else ("open_prs",)
    for name in names:
        for row in snapshot["sources"].get(name, {}).get("records", []):
            old = pulls.get(row["number"])
            # GitHub updated_at uses one UTC spelling. Prefer the newer record;
            # an exact tie keeps the open state. Coverage timestamps remain
            # separate: this is not an atomic server snapshot.
            key = lambda item: (item["updated_at"], item["state"] == "open")
            if old is None or key(row) > key(old):
                pulls[row["number"]] = row
    return list(pulls.values())


def local_records(root):
    records = []
    # Deliberately avoid vendored trees and large binary artifacts.
    paths = sorted([*(root / "research").glob("*/README.md"), *(root / "research").glob("*/TASK.json")])
    ledger = root / "docs/research/pr-ledger.md"
    if ledger.is_file():
        paths.append(ledger)
    for path in paths:
        if path.is_symlink():
            continue
        data = path.read_bytes()
        body = data.decode("utf-8", errors="replace")
        name = path.relative_to(root).as_posix()
        kind = {"README.md": "local-readme", "TASK.json": "local-task"}.get(path.name, "local-ledger")
        records.append({"kind": kind,
                        "title": name, "path": name, "body": body,
                        "sha256": hashlib.sha256(data).hexdigest()})
    return records


def local_coverage(root, records):
    """Compare searched working-tree notes with the regular note paths at HEAD."""
    coverage = {"head": None, "records": len(records), "head_records": None,
                "complete_head_inventory": None, "unsearched_head_paths": None}
    try:
        def git(*args):
            return subprocess.run(
                ["git", "--no-replace-objects", *args], cwd=root, check=True,
                capture_output=True, encoding="utf-8", errors="surrogateescape", timeout=15,
                env={**git_source_env(), "GIT_NO_LAZY_FETCH": "1"},
            ).stdout

        # Pin the tree once; only metadata is read, never omitted note blobs.
        coverage["head"] = git("rev-parse", "--verify", "HEAD^{commit}").strip()
        tree = git("ls-tree", "-r", "-z", "--full-tree", coverage["head"], "--",
                   "research", "docs/research/pr-ledger.md")
        expected = set()
        for entry in tree.split("\0"):
            if not entry:
                continue
            metadata, path = entry.split("\t", 1)
            mode, kind, _ = metadata.split()
            parts = PurePosixPath(path).parts
            in_scope = (path == "docs/research/pr-ledger.md"
                        or (len(parts) == 3 and parts[0] == "research"
                            and parts[2] in ("README.md", "TASK.json")))
            if in_scope and kind == "blob" and mode in ("100644", "100755"):
                expected.add(path)
    except (OSError, subprocess.SubprocessError, ValueError) as exc:
        return coverage, ["local: HEAD note inventory unavailable; local coverage is unknown. "
                          + error_summary(exc)]
    missing = sorted(expected - {record["path"] for record in records})
    coverage.update(head_records=len(expected), complete_head_inventory=not missing,
                    unsearched_head_paths=missing)
    warnings = ([f"local: {len(missing)} HEAD note paths were not searched; "
                 "inspect coverage.local.unsearched_head_paths in --json output and materialize relevant notes "
                 "before treating a lack of matches as evidence."] if missing else [])
    return coverage, warnings


def match_position(text, term, pattern):
    if pattern is None:
        return text.find(term)
    match = pattern.search(text)
    return match.start() if match else -1


def search(records, terms, all_terms=False, reference_terms=()):
    terms = list(dict.fromkeys(t.strip().lower() for t in terms if t.strip()))
    if not terms:
        raise ValueError("provide at least one nonempty search term")
    # Numeric card references name predecessors, rather than digits inside a kappa
    # or a source hash. Explicit user terms retain literal substring semantics.
    patterns = {term: re.compile(r"(?<![\w.])(?:pr(?:\s*#)?\s*)?" + re.escape(term)
                                 + r"(?!\w|\.\d)") if term in reference_terms else None
                for term in terms}
    matches = []
    for record in records:
        title, body = record["title"].lower(), record.get("body", "").lower()
        title_positions = {t: match_position(title, t, patterns[t]) for t in terms}
        body_positions = {t: match_position(body, t, patterns[t]) for t in terms}
        found = [t for t in terms if title_positions[t] >= 0 or body_positions[t] >= 0]
        if not found or (all_terms and len(found) != len(terms)):
            continue
        positions = [body_positions[t] for t in found if body_positions[t] >= 0]
        start = max(0, min(positions) - 100) if positions else 0
        matches.append({**{k: v for k, v in record.items() if k != "body"},
                        "matched_terms": found,
                        "score": sum(3 if title_positions[t] >= 0 else 1 for t in found),
                        "excerpt": record.get("body", "")[start:start + 500]})
    return sorted(matches, key=lambda r: (-r["score"], r["kind"], r["title"], r.get("url", "")))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("terms", nargs="*", help="literal case-insensitive terms; quote multiword phrases")
    ap.add_argument("--task", help="add the named catalogue card's overlap terms")
    ap.add_argument("--path", action="append", default=[], metavar="PATTERN",
                    help="match open PRs by changed file path (fnmatch pattern or substring); repeatable")
    ap.add_argument("--offline", action="store_true")
    ap.add_argument("--refresh", action="store_true")
    ap.add_argument("--include-closed", action="store_true",
                    help="also search all paginated closed/merged PR titles and bodies (extra fetch/cache)")
    ap.add_argument("--max-age", type=int, default=300, help="remote cache lifetime in seconds")
    ap.add_argument("--limit", type=int, default=20)
    ap.add_argument("--all-terms", action="store_true")
    ap.add_argument("--json", action="store_true", dest="json_output")
    ap.add_argument("--cache", type=Path, default=Path(os.environ.get("XDG_CACHE_HOME", str(Path.home() / ".cache"))) / "integer-mult-bounds/overlap.json")
    args = ap.parse_args()
    if args.max_age < 0 or args.limit < 1 or (args.offline and args.refresh):
        ap.error("use nonnegative max-age, positive limit, and either offline or refresh")
    if args.include_closed and args.path:
        ap.error("--include-closed searches titles/bodies only; omit --path (its index covers open PRs)")
    if args.cache.resolve().is_relative_to(ROOT.resolve()):
        ap.error("keep the cache outside the repository")
    terms = list(args.terms)
    explicit_terms = {term.strip().lower() for term in args.terms}
    reference_terms = []
    if args.task:
        catalog = json.loads((ROOT / "docs/research/agent-task-catalog.json").read_text(encoding="utf-8"))
        cards = [t for tr in catalog["tracks"] for t in tr["tasks"] if t["id"] == args.task]
        if not cards:
            ap.error("unknown task")
        terms.extend([args.task, *cards[0].get("overlap_terms", [])])
        # A leading-zero digit string can be a word, e.g. census witness
        # 01021323. Restrict reference matching to canonical positive integers.
        reference_terms = list(dict.fromkeys(
            t.strip() for t in cards[0].get("overlap_terms", [])
            if t.strip().isascii() and t.strip().isdecimal() and not t.strip().startswith("0")
            and t.strip() not in explicit_terms))
        # Catalogue paths are repository-relative POSIX paths. Nested sources
        # identify their package, not generic directories such as evidence/code.
        for point in cards[0]["starting_points"]:
            parts = PurePosixPath(point).parts
            if len(parts) >= 3 and parts[0] == "research":
                terms.append(parts[1])
    if not any(t.strip() for t in terms) and not args.path:
        ap.error("provide terms, --task or --path")
    patterns = [p.strip() for p in args.path if p.strip()]
    local = local_records(ROOT)
    local_status, local_warnings = local_coverage(ROOT, local)
    snapshot, warnings = remote_snapshot(args.cache, args.offline, args.refresh, args.max_age,
                                         need_files=bool(patterns), include_closed=args.include_closed)
    warnings = local_warnings + warnings
    records = list(local) + pull_corpus(snapshot, args.include_closed)
    coverage = {"local": local_status}
    corpus_names = ("open_prs", "discussions", "closed_prs") if args.include_closed else ("open_prs", "discussions")
    for name in corpus_names:
        source = snapshot["sources"].get(name)
        coverage[name] = {k: source[k] for k in ("fetched_at", "complete_pagination")} if source else None
        if source:
            if name == "discussions":
                records.extend(source["records"])
            coverage[name]["records"] = len(source["records"])
    path_matches = []
    if patterns:
        source = snapshot["sources"].get("pr_files")
        coverage["pr_files"] = {k: source[k] for k in ("fetched_at", "complete_pagination")} if source else None
        if source:
            coverage["pr_files"]["records"] = len(source["records"])
            truncated = sorted({row["number"] for row in source["records"] if row.get("truncated", False)})
            coverage["pr_files"]["truncated_prs"] = truncated
            if truncated:
                warnings.append(f"pr_files: incomplete file inventories for {len(truncated)} PRs; "
                                "paths may be missing. Check truncated_prs in coverage, even when no path matches.")
            pulls = snapshot["sources"].get("open_prs", {"records": []})["records"]
            heads = {pull["number"]: pull.get("head") for pull in pulls}
            file_heads = {row["number"]: row.get("head") for row in source["records"]}
            unverified = sorted(number for number in heads.keys() | file_heads.keys()
                                if not file_heads.get(number) or file_heads[number] != heads.get(number))
            coverage["pr_files"]["unverified_heads"] = unverified
            if unverified:
                warnings.append(f"pr_files: file-head binding unverified for {len(unverified)} PRs; "
                                "paths may be stale. Refresh and recheck the heads listed in coverage.")
            bases = {pull["number"]: pull.get("base") for pull in pulls}
            file_bases = {row["number"]: row.get("base") for row in source["records"]}
            unverified_bases = sorted(number for number in bases.keys() | file_bases.keys()
                                      if not file_bases.get(number) or file_bases[number] != bases.get(number))
            coverage["pr_files"]["unverified_bases"] = unverified_bases
            if unverified_bases:
                warnings.append(f"pr_files: file-base binding unverified for {len(unverified_bases)} PRs; "
                                "paths may be stale. Refresh and recheck the bases listed in coverage.")
            path_matches = path_report(pulls, source["records"], patterns)
    matches = search(records, terms, args.all_terms, reference_terms) if any(t.strip() for t in terms) else []
    if patterns and matches:
        # With both axes given, a record must match at least one term and one path.
        hits = {m["number"]: m for m in path_matches}
        matches = [dict(m, **{key: hits[m["number"]][key]
                             for key in ("matched_paths", "head", "body_head", "head_matches",
                                         "base", "body_base", "base_matches", "truncated")}) for m in matches
                   if m.get("kind") == "pr" and m.get("number") in hits]
    if patterns and not any(t.strip() for t in terms):
        matches = []
    report = {"status": "POSSIBLE_OVERLAP_NOT_A_NOVELTY_CERTIFICATE", "searched_at": now(),
              "terms": terms, "coverage": coverage, "local_records": len(local), "warnings": warnings,
              "reference_terms": reference_terms,
              "limits": (("Remote PR scope includes open and closed/merged titles and bodies, with separate coverage and timestamps. "
                          "State changes are deduplicated by latest PR update; snapshots are not atomic. "
                          if args.include_closed else
                          "Remote PR scope is open PRs including drafts. Closed work is searched through local READMEs, TASK metadata and ledger only. ")
                         + "Local coverage compares searched working-tree notes with regular note paths at coverage.local.head; "
                         "it does not certify HEAD contents or historical coverage. "
                         "No code diffs or arbitrary package files are searched. Recheck relevant heads before submission."),
              "matches_total": len(matches), "matches": matches[:args.limit]}
    if patterns:
        report["path_patterns"] = patterns
        report["path_limits"] = ("Path matching covers the changed file paths GitHub reports for open PRs, "
                                 "not diff contents; all available file pages are followed. Missing lists or "
                                 "advertised-count shortfalls are flagged truncated and listed in coverage.pr_files.truncated_prs "
                                 "independently of matches or --limit. complete_pagination describes list paging, "
                                 "not completeness of each PR's file inventory. Head/base identify the file "
                                 "snapshot; body_head/body_base identify PR metadata. Both endpoints must match. "
                                 "This is not an atomic server snapshot. Unverified joins are flagged, "
                                 "including inventories with no matching path.")
        report["path_matches_total"] = len(path_matches)
        report["path_matches"] = path_matches[:args.limit]
    if args.json_output:
        print(json.dumps(report, indent=2))
    else:
        # Excerpts quote arbitrary UTF-8; a cp1252 pipe must escape them, not crash.
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(errors="backslashreplace")
        print(report["status"])
        # A sparse checkout can omit thousands of notes. Keep the complete
        # path list in JSON; the text report surfaces the count and warning.
        local_summary = {k: v for k, v in local_status.items() if k != "unsearched_head_paths"}
        omitted = local_status.get("unsearched_head_paths")
        local_summary["unsearched_head_paths_count"] = None if omitted is None else len(omitted)
        print("Coverage: " + json.dumps({**coverage, "local": local_summary}))
        if reference_terms:
            print("Task references (identifier matching): " + ", ".join(reference_terms))
        print(report["limits"])
        if patterns:
            print(report["path_limits"])
        for warning in warnings:
            print("WARNING: " + warning)
        print(f"{len(matches)} possible matches; showing {min(args.limit, len(matches))}")
        for match in matches[:args.limit]:
            flags = " (file list truncated)" if match.get("truncated") else ""
            print(f"\n[{match['kind']}] {match['title']}{flags}\n{match.get('url', match.get('path'))}")
            if match.get("head"):
                print("Head: " + match["head"])
            if match.get("head_matches") is False:
                print("File-head binding unverified; body head: " + str(match.get("body_head")))
            print(match["excerpt"])
        if patterns:
            print(f"\n{len(path_matches)} open PRs match paths {patterns}; "
                  f"showing {min(args.limit, len(path_matches))}")
            for match in path_matches[:args.limit]:
                flags = " (file list truncated)" if match["truncated"] else ""
                print(f"\n[pr {match['number']}] {match['title']}{flags}\n{match['url']}")
                if match.get("head"):
                    print("Head: " + match["head"])
                if not match["head_matches"]:
                    print("File-head binding unverified; body head: " + str(match["body_head"]))
                print("Matched paths: " + ", ".join(match["matched_paths"]))


if __name__ == "__main__":
    main()
