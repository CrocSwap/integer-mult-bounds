"""REST pagination controls for overlap checks on GitHub CLI without --slurp."""
import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import find_overlap as overlap
sys.path.pop(0)


def pull(number, body="A claim", draft=False):
    return {"number": number, "title": "A modest change", "body": body,
            "html_url": f"https://example.invalid/pull/{number}",
            "head": {"sha": f"{number:040x}"}, "updated_at": "2026-10-14T00:00:00Z",
            "state": "open", "draft": draft}


def legacy_cli(pages):
    """Model gh's output contract, including old versions' unsupported flag."""
    def run(argv, **kwargs):
        if "--slurp" in argv:
            raise subprocess.CalledProcessError(1, argv, stderr="unknown flag: --slurp")
        selected = pages if "--paginate" in argv else pages[:1]
        if "--jq" in argv and argv[argv.index("--jq") + 1] == "@json":
            text = "\n".join(json.dumps(page, ensure_ascii=False) for page in selected)
        else:
            text = "\n".join(json.dumps(page, indent=2) for page in selected)
        return subprocess.CompletedProcess(argv, 0, stdout=text + "\n", stderr="")
    return run


class OverlapPaginationTests(unittest.TestCase):
    def test_legacy_slurp_arguments_keep_all_pages(self):
        pages = [[pull(1)], [pull(2, draft=True)]]
        with patch.object(overlap.subprocess, "run", side_effect=legacy_cli(pages)):
            result = overlap.gh_json(["--paginate", "--slurp", "repos/example/pulls"])
        self.assertEqual(result, pages)

    def test_cli_finds_later_page_draft_without_slurp(self):
        # JSON permits these Unicode line separators inside a string. Only LF
        # separates compact @json pages; str.splitlines() would corrupt this body.
        pages = [[pull(1)], [pull(2, "Exact κ claim\nwith a dirty decoder\u0085\u2028\u2029", draft=True)]]
        with tempfile.TemporaryDirectory() as tmp:
            root, cache = Path(tmp) / "repo", Path(tmp) / "cache.json"
            output = io.StringIO()
            argv = ["find_overlap.py", "dirty decoder", "--json", "--cache", str(cache)]
            with (patch.object(overlap, "ROOT", root), patch.object(sys, "argv", argv),
                  patch.object(overlap.subprocess, "run", side_effect=legacy_cli(pages)),
                  patch.object(overlap, "fetch_discussions", return_value=[]),
                  contextlib.redirect_stdout(output)):
                overlap.main()
            report = json.loads(output.getvalue())
            self.assertEqual(report["warnings"], [])
            self.assertEqual(report["coverage"]["open_prs"]["records"], 2)
            self.assertTrue(report["coverage"]["open_prs"]["complete_pagination"])
            self.assertEqual(report["matches_total"], 1)
            match = report["matches"][0]
            self.assertEqual(match["number"], 2)
            self.assertEqual(match["head"], "0000000000000000000000000000000000000002")
            self.assertTrue(match["draft"])
            self.assertEqual(match["excerpt"], "Exact κ claim\nwith a dirty decoder\u0085\u2028\u2029")
            stored = json.loads(cache.read_text(encoding="utf-8"))
            self.assertEqual([r["number"] for r in stored["sources"]["open_prs"]["records"]], [1, 2])

    def test_empty_repository_is_complete_not_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            with (patch.object(overlap.subprocess, "run", side_effect=legacy_cli([[]])),
                  patch.object(overlap, "fetch_discussions", return_value=[])):
                snapshot, warnings = overlap.remote_snapshot(Path(tmp) / "cache.json")
            self.assertEqual(warnings, [])
            source = snapshot["sources"]["open_prs"]
            self.assertEqual(source["records"], [])
            self.assertTrue(source["complete_pagination"])

    def test_single_response_and_graphql_errors_keep_their_contract(self):
        for response in ({"data": {"value": "κ"}}, {"errors": [{"message": "denied"}]}):
            with self.subTest(response=response):
                result = subprocess.CompletedProcess([], 0, stdout=json.dumps(response), stderr="")
                with patch.object(overlap.subprocess, "run", return_value=result):
                    if "errors" in response:
                        with self.assertRaisesRegex(ValueError, "GitHub GraphQL errors.*denied"):
                            overlap.graphql("query", {})
                    else:
                        self.assertEqual(overlap.graphql("query", {}), {"value": "κ"})

    def test_invalid_or_failed_refresh_preserves_previous_complete_pages(self):
        first_page = json.dumps([pull(99)])
        bad_outputs = ("", first_page + "\n[", first_page + '\n{"message":"denied"}',
                       first_page + "\n{}", first_page + "\nnull", first_page + "\n42")
        failures = [subprocess.CompletedProcess([], 0, stdout=text, stderr="") for text in bad_outputs]
        failures.append(subprocess.CalledProcessError(1, ["gh", "api"],
                                                      output=first_page, stderr="later page failed"))
        with tempfile.TemporaryDirectory() as tmp:
            cache = Path(tmp) / "cache.json"
            with (patch.object(overlap.subprocess, "run", side_effect=legacy_cli([[pull(1)], [pull(2)]])),
                  patch.object(overlap, "fetch_discussions", return_value=[])):
                original, warnings = overlap.remote_snapshot(cache)
            self.assertEqual(warnings, [])
            for failure in failures:
                with self.subTest(failure=failure):
                    mock = {"side_effect": failure} if isinstance(failure, Exception) else {"return_value": failure}
                    with (patch.object(overlap.subprocess, "run", **mock),
                          patch.object(overlap, "fetch_discussions", return_value=[])):
                        snapshot, warnings = overlap.remote_snapshot(cache, refresh=True)
                    self.assertTrue(any("open_prs: refresh failed" in warning for warning in warnings), warnings)
                    self.assertEqual(snapshot["sources"]["open_prs"], original["sources"]["open_prs"])
                    stored = json.loads(cache.read_text(encoding="utf-8"))
                    self.assertEqual(stored["sources"]["open_prs"], original["sources"]["open_prs"])
                    self.assertEqual([r["number"] for r in stored["sources"]["open_prs"]["records"]], [1, 2])

    def test_failed_first_fetch_does_not_claim_complete_coverage(self):
        failure = subprocess.CalledProcessError(1, ["gh", "api"],
                                                output=json.dumps([pull(99)]), stderr="later page failed")
        with tempfile.TemporaryDirectory() as tmp:
            with (patch.object(overlap.subprocess, "run", side_effect=failure),
                  patch.object(overlap, "fetch_discussions", return_value=[])):
                snapshot, warnings = overlap.remote_snapshot(Path(tmp) / "cache.json")
            self.assertNotIn("open_prs", snapshot["sources"])
            self.assertTrue(any("open_prs: no usable remote snapshot" in warning for warning in warnings))
            self.assertEqual(snapshot["sources"]["discussions"]["records"], [])
            self.assertTrue(snapshot["sources"]["discussions"]["complete_pagination"])

    def test_cached_multi_page_snapshot_needs_no_network(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = Path(tmp) / "cache.json"
            with (patch.object(overlap.subprocess, "run", side_effect=legacy_cli([[pull(1)], [pull(2)]])),
                  patch.object(overlap, "fetch_discussions", return_value=[])):
                overlap.remote_snapshot(cache)
            with patch.object(overlap.subprocess, "run", side_effect=AssertionError("unexpected network")):
                fresh, warnings = overlap.remote_snapshot(cache)
                self.assertEqual(warnings, [])
                offline, warnings = overlap.remote_snapshot(cache, offline=True)
                self.assertEqual(len(warnings), 2)
            self.assertEqual([r["number"] for r in fresh["sources"]["open_prs"]["records"]], [1, 2])
            self.assertEqual(offline["sources"]["open_prs"], fresh["sources"]["open_prs"])


if __name__ == "__main__":
    unittest.main()
