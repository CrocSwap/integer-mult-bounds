#!/usr/bin/env python3
"""Opt-in live comparison on a fixed Discussion roster and exact record hash.

Arham Garg, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def load(name, source):
    module = types.ModuleType(name)
    module.__file__ = str(ROOT / "scripts/find_overlap.py")
    exec(compile(source, module.__file__, "exec"), module.__dict__)
    return module


def discussion_fields(query):
    """Retain the fetcher's exact node selection, changing only the roster."""
    start = query.index("nodes {") + len("nodes {")
    depth = 1
    for end in range(start, len(query)):
        depth += (query[end] == "{") - (query[end] == "}")
        if depth == 0:
            return query[start:end]
    raise ValueError("unterminated Discussion field selection")


def measure(module, fixture):
    real = module.graphql
    requests = 0
    roster = [row["id"] for row in fixture["discussions"]]

    def fixed_roster(query, variables):
        nonlocal requests
        requests += 1
        if "repository(owner:" in query:
            if variables["cursor"] is not None:
                raise ValueError("fixed-roster benchmark received a second listing page")
            fields = discussion_fields(query)
            response = real("query($ids:[ID!]!) { nodes(ids:$ids) { ... on Discussion {"
                            + fields + "} } }", {"ids": roster})
            nodes = response["nodes"]
            if [node["id"] for node in nodes] != roster:
                raise ValueError("live Discussion roster changed")
            return {"repository": {"discussions": {
                "nodes": nodes, "pageInfo": {"hasNextPage": False, "endCursor": None}}}}
        return real(query, variables)

    module.graphql = fixed_roster
    try:
        start = time.perf_counter()
        records = module.fetch_discussions()
        elapsed = time.perf_counter() - start
    finally:
        module.graphql = real
    encoded = json.dumps(records, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
    if len(records) != fixture["records"] or digest(encoded) != fixture["records_sha256"]:
        raise ValueError("live records differ from the fixed fixture; no timing comparison is accepted")
    return {"seconds": elapsed, "requests": requests, "records": len(records),
            "records_sha256": digest(encoded)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="authorize read-only GitHub API measurements")
    args = parser.parse_args()
    if not args.live:
        parser.error("live GitHub checks require --live; ordinary package replay is offline")
    fixture_bytes = (HERE / "FIXTURE.json").read_bytes()
    fixture = json.loads(fixture_bytes)
    sources = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
    old = subprocess.check_output(["git", "show", sources["base_commit"] + ":scripts/find_overlap.py"], cwd=ROOT)
    expected = next(row["sha256"] for row in sources["files"] if row["path"] == "scripts/find_overlap.py")
    if digest(old) != expected:
        raise ValueError("baseline source differs from its pin")
    new = (ROOT / "scripts/find_overlap.py").read_bytes()
    modules = {"before": load("before", old), "after": load("after", new)}
    samples = {name: [] for name in modules}
    order = []
    for pair in range(3):
        for name in (("before", "after") if pair % 2 == 0 else ("after", "before")):
            sample = measure(modules[name], fixture)
            samples[name].append(sample)
            order.append(name)
            print(f"{name}: {sample['seconds']:.3f}s, {sample['requests']} requests, exact records match",
                  file=sys.stderr, flush=True)
    summary = {name: {"median_seconds": statistics.median(s["seconds"] for s in rows),
                      "min_seconds": min(s["seconds"] for s in rows),
                      "max_seconds": max(s["seconds"] for s in rows)} for name, rows in samples.items()}
    print(json.dumps({"checked_at_utc": datetime.now(timezone.utc).isoformat(),
                      "environment": {"python": sys.version, "platform": platform.platform(),
                                      "gh": subprocess.check_output(["gh", "--version"], text=True).splitlines()[0]},
                      "scope": "Three alternating pairs on twenty fixed Discussions and all descendants; fresh API reads, no overlap cache. Listing is replaced by nodes(ids:) with unchanged field selections. Timings include network, GitHub processing and local gh startup.",
                      "base_commit": sources["base_commit"], "before_sha256": digest(old),
                      "after_sha256": digest(new), "fixture_sha256": digest(fixture_bytes),
                      "order": order, "samples": samples, "summary": summary,
                      "median_ratio": summary["before"]["median_seconds"] / summary["after"]["median_seconds"]}, indent=2))


if __name__ == "__main__":
    main()
