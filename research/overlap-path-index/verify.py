#!/usr/bin/env python3
"""Verify the find_overlap changed-file path index without network access.

Checks, in order: exact source pins (identity), the Overlap unit tests against
the pinned tool, a hermetic CLI fixture with a positive path match, term/path
AND semantics, a rejection control, a mutated-fixture control that must lose
the match, and a missing-index control that must warn instead of reporting
"no overlap" silently.

Aaron Wang / navinor, with help from opencode. Apache-2.0.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
PYTHON = sys.executable


def check_sources():
    pins = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    for entry in pins["files"]:
        if entry["usage"] != "input":
            continue
        data = (ROOT / entry["path"]).read_bytes()
        assert hashlib.sha256(data).hexdigest() == entry["sha256"], "pin mismatch: " + entry["path"]
    return sum(1 for entry in pins["files"] if entry["usage"] == "input")


def run_overlap_tests():
    result = subprocess.run(
        [PYTHON, "-B", "-m", "unittest", "discover", "-s", "tests", "-p", "test_research_onboarding.py",
         "-k", "Overlap"],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8", timeout=300)
    assert result.returncode == 0, "overlap unit tests failed:\n" + result.stderr[-2000:]
    assert "OK" in result.stderr, "unexpected unittest output:\n" + result.stderr[-2000:]
    ran = [line for line in result.stderr.splitlines() if line.startswith("Ran ")]
    return ran[-1] if ran else "?"


def fixture_cache(path, mutated=False, drop_index=False):
    hit_path = "docs/research/current-status.md"
    if mutated:
        hit_path = "docs/research/unrelated.md"
    sources = {
        "open_prs": {"fetched_at": "2026-10-14T00:00:00+00:00", "complete_pagination": True, "records": [
            {"kind": "pr", "number": 4242, "title": "Fixture: status rewrite", "body": "touches the status doc",
             "url": "https://github.com/CrocSwap/integer-mult-bounds/pull/4242", "head": "a" * 40,
             "updated_at": "2026-10-14T00:00:00Z", "draft": False, "state": "open"},
            {"kind": "pr", "number": 4243, "title": "Fixture: other", "body": "unrelated",
             "url": "https://github.com/CrocSwap/integer-mult-bounds/pull/4243", "head": "b" * 40,
             "updated_at": "2026-10-14T00:00:00Z", "draft": False, "state": "open"}]},
        "discussions": {"fetched_at": "2026-10-14T00:00:00+00:00", "complete_pagination": True, "records": []},
    }
    if not drop_index:
        sources["pr_files"] = {"fetched_at": "2026-10-14T00:00:00+00:00", "complete_pagination": True, "records": [
            {"number": 4242, "paths": [hit_path, "README.md"], "truncated": False},
            {"number": 4243, "paths": ["research/other/README.md"], "truncated": False}]}
    path.write_text(json.dumps({"schema_version": 1, "repository": "CrocSwap/integer-mult-bounds",
                                "sources": sources}), encoding="utf-8")


def run_cli(cache, extra):
    result = subprocess.run(
        [PYTHON, "-B", str(ROOT / "scripts" / "find_overlap.py"), "--offline",
         "--cache", str(cache), "--json", *extra],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8", timeout=300)
    assert result.returncode == 0, "CLI failed:\n" + result.stderr[-2000:]
    return json.loads(result.stdout)


def main():
    pinned = check_sources()
    tests = run_overlap_tests()
    with tempfile.TemporaryDirectory() as tmp:
        cache = Path(tmp) / "fixture-cache.json"

        fixture_cache(cache)
        report = run_cli(cache, ["--path", "docs/research/current-status.md", "--limit", "5"])
        numbers = [m["number"] for m in report["path_matches"]]
        assert numbers == [4242], "positive fixture failed: " + repr(numbers)
        assert report["path_matches"][0]["matched_paths"] == ["docs/research/current-status.md"]

        # Substring and fnmatch pattern forms both match the same fixture.
        assert [m["number"] for m in run_cli(cache, ["--path", "current-status.md"])["path_matches"]] == [4242]
        assert [m["number"] for m in run_cli(cache, ["--path", "docs/*"])["path_matches"]] == [4242]

        # Rejection control: a pattern no PR touches matches nothing.
        rejected = run_cli(cache, ["--path", "no-such-path-xyz"])
        assert rejected["path_matches_total"] == 0, "rejection control failed"

        # Term/path AND semantics: the path hit alone never enters matches ...
        both = run_cli(cache, ["--path", "docs/research/current-status.md", "status rewrite"])
        assert [m["number"] for m in both["path_matches"]] == [4242]
        assert [m["number"] for m in both["matches"]] == [4242]
        # ... while path_matches stays the superset of all path hits (no false negative).
        neither = run_cli(cache, ["--path", "docs/research/current-status.md", "no-such-term-xyz"])
        assert neither["matches"] == [] and neither["path_matches_total"] == 1

        # Mutated fixture: once the changed file is different, the match is gone.
        fixture_cache(cache, mutated=True)
        assert run_cli(cache, ["--path", "docs/research/current-status.md"])["path_matches_total"] == 0

        # Missing index warns and reports zero, never a silent "no overlap".
        fixture_cache(cache, drop_index=True)
        missing = run_cli(cache, ["--path", "docs/research/current-status.md"])
        assert missing["path_matches_total"] == 0
        assert any("pr_files" in w for w in missing["warnings"]), "missing-index warning absent"

    print(json.dumps({
        "status": "PASS_OVERLAP_PATH_INDEX",
        "pinned_inputs": pinned,
        "unit_tests": tests,
        "controls": ["positive", "substring", "glob", "rejection", "term-and-path", "mutation", "missing-index"],
    }, indent=2))


if __name__ == "__main__":
    main()
