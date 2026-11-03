"""Source-reference intake must retain exact PR metadata and expose unknowns."""

import contextlib
from datetime import datetime, timezone
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import find_source_overlap as overlap
sys.path.pop(0)


def pull(number, body="Builds on PR6537.", author="petalas", created="2026-11-03T00:00:00Z"):
    return {"kind": "pr", "number": number, "title": "A follow-up", "body": body,
            "url": f"https://example.invalid/pull/{number}", "author": author,
            "created_at": created, "updated_at": "2026-11-03T12:00:00Z",
            "state": "open", "head": "a" * 40, "base": "b" * 40}


class IntakeTests(unittest.TestCase):
    def run_report(self, rows, arguments=(), closed=()):
        with tempfile.TemporaryDirectory() as tmp:
            cache = Path(tmp) / "cache.json"
            sources = {name: {"fetched_at": overlap.now(), "complete_pagination": True,
                              "records": records}
                       for name, records in (("open_prs", rows), ("discussions", []),
                                             ("closed_prs", list(closed)))}
            raw = json.dumps({"schema_version": 1, "repository": overlap.REPO, "sources": sources})
            cache.write_text(raw, encoding="utf-8")
            output = io.StringIO()
            with (patch.object(overlap, "ROOT", Path(tmp) / "empty-repo"),
                  patch.object(overlap, "gh_json", side_effect=AssertionError("network")),
                  patch.object(sys, "argv", ["find_source_overlap.py", "--offline", "--json",
                                             "--cache", str(cache), *arguments]),
                  contextlib.redirect_stdout(output)):
                overlap.main()
            self.assertEqual(cache.read_text(encoding="utf-8"), raw)
            return json.loads(output.getvalue())

    def test_reference_bypasses_hash_and_decimal_noise(self):
        noise = [pull(i, "Commit a6537b, saving 0.006537 and parameter 6537.5.") for i in range(21)]
        result = self.run_report([*noise, pull(99)], ["--reference", "6537"])
        self.assertEqual(result["matches_total"], 1)
        self.assertEqual([row["number"] for row in result["matches"]], [99])
        self.assertEqual(result["reference_terms"], ["6537"])

    def test_reference_forms_and_literal_query_semantics(self):
        forms = ["#6537", "PR6537", "pr #6537", "PR 6537",
                 "https://github.com/CrocSwap/integer-mult-bounds/pull/6537"]
        rows = [pull(i, body) for i, body in enumerate(forms)]
        result = self.run_report(rows, ["--reference", "6537", "--reference", "6537"])
        self.assertEqual(result["matches_total"], len(forms))
        self.assertEqual(result["reference_terms"], ["6537"])
        result = self.run_report([pull(1, "a6537b")], ["6537"])
        self.assertEqual(result["matches_total"], 1)

    def test_author_and_creation_cutoff_are_inclusive_and_case_insensitive(self):
        rows = [pull(1, created="2026-10-27T00:00:00Z"),
                pull(2, created="2026-10-26T23:59:59Z"), pull(3, author="someone-else")]
        result = self.run_report(rows, ["--reference", "6537", "--pr-author", "PeTaLaS",
                                        "--created-since", "2026-10-27"])
        self.assertEqual([row["number"] for row in result["matches"]], [1])
        self.assertEqual(result["pr_filters"]["records_after_filter"], 1)
        self.assertEqual(result["pr_filters"]["created_since"], "2026-10-27T00:00:00+00:00")
        self.assertIn("Discussions excluded", result["pr_filters"]["scope"])

    def test_closed_body_is_only_included_when_requested(self):
        row = dict(pull(9), state="closed")
        args = ["--reference", "6537", "--pr-author", "petalas"]
        self.assertEqual(self.run_report([], args, [row])["matches_total"], 0)
        result = self.run_report([], [*args, "--include-closed"], [row])
        self.assertEqual([match["number"] for match in result["matches"]], [9])
        self.assertTrue(result["coverage"]["closed_prs"]["complete_pagination"])

    def test_legacy_offline_metadata_is_an_error_not_an_empty_result(self):
        row = pull(1)
        del row["author"]
        with contextlib.redirect_stderr(io.StringIO()) as errors, self.assertRaises(SystemExit) as exc:
            self.run_report([row], ["--reference", "6537", "--pr-author", "petalas"])
        self.assertEqual(exc.exception.code, 2)
        self.assertIn("unknown is not no overlap", errors.getvalue())
        # Unfiltered offline reports remain compatible with legacy metadata.
        self.assertEqual(self.run_report([row], ["--reference", "6537"])["matches_total"], 1)

    def test_missing_or_bad_creation_times_cannot_be_silently_filtered_out(self):
        cutoff = datetime(2026, 10, 27, tzinfo=timezone.utc)
        for stamp in (None, 123, "yesterday", "2026-11-03T00:00:00"):
            with self.subTest(stamp=stamp), self.assertRaisesRegex(ValueError, "metadata unavailable"):
                overlap.filter_pulls([pull(1, created=stamp)], created_since=cutoff)

    def test_normalized_rest_metadata_retains_creation_not_update(self):
        raw = {"number": 7, "title": "A lead", "body": None, "html_url": "url",
               "head": {"sha": "a" * 40}, "state": "closed", "user": {"login": "petalas"},
               "created_at": "2026-10-01T00:00:00Z", "updated_at": "2026-11-03T00:00:00Z"}
        normalized = overlap.pull_records([[raw]])[0]
        self.assertEqual(normalized["author"], "petalas")
        self.assertEqual(normalized["created_at"], raw["created_at"])
        cutoff = datetime(2026, 10, 27, tzinfo=timezone.utc)
        self.assertEqual(overlap.filter_pulls([normalized], "petalas", cutoff), [])
        self.assertIsNone(overlap.pull_records([[dict(raw, user=None)]])[0]["author"])

    def test_new_cli_does_not_mutate_the_legacy_reader(self):
        names = ("pull_records", "remote_snapshot", "search", "atomic_json")
        functions = [getattr(overlap.legacy, name) for name in names]
        self.run_report([pull(1)], ["--reference", "6537", "--pr-author", "petalas"])
        self.assertEqual(functions, [getattr(overlap.legacy, name) for name in names])
        raw = {"number": 7, "title": "A lead", "html_url": "url", "head": {"sha": "a" * 40},
               "state": "open", "updated_at": overlap.now(), "user": {"login": "petalas"},
               "created_at": overlap.now()}
        self.assertNotIn("author", overlap.legacy.pull_records([[raw]])[0])
        self.assertNotIn("created_at", overlap.legacy.pull_records([[raw]])[0])

    def test_refresh_failure_preserves_cached_bytes_and_in_memory_evidence(self):
        for failure in ("fetch", "publication"):
            with self.subTest(failure=failure), tempfile.TemporaryDirectory() as tmp:
                cache = Path(tmp) / "cache.json"
                old = {"fetched_at": overlap.now(), "complete_pagination": True, "records": [pull(1)]}
                raw = json.dumps({"schema_version": 1, "repository": overlap.REPO,
                                  "sources": {"open_prs": old}})
                cache.write_text(raw, encoding="utf-8")
                new = {"number": 2, "title": "New", "html_url": "url", "head": {"sha": "c" * 40},
                       "state": "open", "updated_at": overlap.now()}
                fetch_error = overlap.subprocess.CalledProcessError(1, ["gh"], stderr="later page failed")
                with (patch.object(overlap, "gh_json", side_effect=fetch_error if failure == "fetch" else None,
                                   return_value=[[new]]),
                      patch.object(overlap.legacy, "atomic_json", side_effect=OSError("write failed"))):
                    snapshot, warnings = overlap.remote_snapshot(cache, refresh=True)
                self.assertEqual(cache.read_text(encoding="utf-8"), raw)
                self.assertEqual(snapshot["sources"]["open_prs"], old)
                self.assertTrue(any("refresh failed" in warning for warning in warnings))

    def test_fresh_legacy_cache_refreshes_pr_metadata_without_refetching_discussions(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = Path(tmp) / "cache.json"
            old = pull(1)
            del old["author"]
            section = lambda rows: {"fetched_at": overlap.now(), "complete_pagination": True, "records": rows}
            cache.write_text(json.dumps({"schema_version": 1, "repository": overlap.REPO,
                                         "sources": {"open_prs": section([old]),
                                                     "discussions": section([])}}), encoding="utf-8")
            raw = {"number": 1, "title": "A lead", "html_url": "url", "head": {"sha": "a" * 40},
                   "state": "open", "updated_at": overlap.now(), "created_at": overlap.now(),
                   "user": {"login": "petalas"}}
            with (patch.object(overlap, "gh_json", return_value=[[raw]]) as fetch,
                  patch.object(overlap.legacy, "fetch_discussions", side_effect=AssertionError("discussion refetch"))):
                snapshot, warnings = overlap.remote_snapshot(cache, need_pr_metadata=True)
            self.assertEqual(fetch.call_count, 1)
            self.assertEqual(warnings, [])
            self.assertEqual(snapshot["sources"]["open_prs"]["records"][0]["author"], "petalas")

    def test_invalid_query_values_stop_before_network(self):
        for arguments in (["--reference", "0"], ["--reference", "06537"],
                          ["--reference", "６５３７"], ["--reference", "-1"],
                          ["--reference", "6537", "--created-since", "2026-02-30"],
                          ["--reference", "6537", "--created-since", "2026-1-1"],
                          ["--reference", "6537", "--pr-author", "@me"],
                          ["--reference", "6537", "--pr-author", "petalas", "--path", "research/*"]):
            with self.subTest(arguments=arguments), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as exc:
                    self.run_report([], arguments)
                self.assertEqual(exc.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
