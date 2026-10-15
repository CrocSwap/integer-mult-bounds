"""Task queries must derive package names, not generic nested directories."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


def pull(number, title, body=""):
    return {"kind": "pr", "number": number, "title": title, "body": body,
            "url": f"https://example.invalid/pull/{number}", "head": "a" * 40,
            "draft": True, "updated_at": "2026-10-14T00:00:00Z"}


class OverlapTaskTermsTests(unittest.TestCase):
    def report(self, card, records, *args):
        """Exercise the public CLI with an isolated, immutable offline cache."""
        with tempfile.TemporaryDirectory() as tmp:
            root, cache = Path(tmp) / "repo", Path(tmp) / "cache.json"
            script = root / "scripts/find_overlap.py"
            script.parent.mkdir(parents=True)
            script.write_bytes((ROOT / "scripts/find_overlap.py").read_bytes())
            catalog = root / "docs/research/agent-task-catalog.json"
            catalog.parent.mkdir(parents=True)
            catalog.write_text(json.dumps({"tracks": [{"tasks": [card]}]}), encoding="utf-8")
            sources = {name: {"fetched_at": "2026-10-14T00:00:00+00:00",
                              "complete_pagination": True, "records": rows}
                       for name, rows in (("open_prs", records), ("discussions", []))}
            raw = json.dumps({"schema_version": 1, "repository": "CrocSwap/integer-mult-bounds",
                              "sources": sources}).encode("utf-8")
            cache.write_bytes(raw)
            result = subprocess.run(
                [sys.executable, "-I", "-B", str(script), "--task", card["id"],
                 "--offline", "--json", "--cache", str(cache), *args],
                cwd=root, capture_output=True, text=True, encoding="utf-8", timeout=15)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(cache.read_bytes(), raw)
        report = json.loads(result.stdout)
        self.assertEqual(report["coverage"]["open_prs"],
                         {"fetched_at": sources["open_prs"]["fetched_at"],
                          "complete_pagination": True, "records": len(records)})
        self.assertEqual(report["status"], "POSSIBLE_OVERLAP_NOT_A_NOVELTY_CERTIFICATE")
        self.assertEqual(len(report["warnings"]), 2)
        return report

    def test_nested_evidence_does_not_hide_a_lead_below_the_default_limit(self):
        # The revision-4 QQ16 paths used to add "evidence" as an OR term.
        # Title hits then outranked a genuine package mention in a PR body.
        card = {"id": "joint-query-controller", "overlap_terms": ["QQ16", "joint-query"],
                "starting_points": ["research/joint-query/README.md",
                                    "research/joint-query/evidence/QQ16-SELECTED-WITNESS.md",
                                    "research/joint-query/evidence/JOINT-QUERY-TRANSFER.md"]}
        records = [pull(i, "Evidence for an unrelated construction") for i in range(21)]
        records.append(pull(99, "Reader extension", "Adds a joint-query observation."))
        report = self.report(card, records)
        self.assertNotIn("evidence", report["terms"])
        self.assertEqual(report["matches_total"], 1)
        self.assertEqual([row["number"] for row in report["matches"]], [99])
        self.assertEqual(report["matches"][0]["head"], "a" * 40)
        self.assertTrue(report["matches"][0]["draft"])

    def test_exclusively_nested_sources_find_their_packages(self):
        card = {"id": "fixture", "starting_points": ["research/alpha/proofs/note.md",
                "research/beta/code/build.py", "research/gamma/README.md",
                "docs/research/guide.md", "research/README.md"]}
        records = [pull(i, "A continuation", name)
                   for i, name in enumerate(("alpha", "beta", "gamma", "proofs", "code", "research"))]
        report = self.report(card, records)
        self.assertEqual(set(report["terms"]), {"fixture", "alpha", "beta", "gamma"})
        self.assertEqual({row["number"] for row in report["matches"]}, {0, 1, 2})

    def test_explicit_generic_terms_and_all_terms_are_preserved(self):
        card = {"id": "fixture", "starting_points": ["research/alpha/proofs/note.md"]}
        records = [pull(1, "Evidence", "fixture alpha"), pull(2, "Evidence only"),
                   pull(3, "Package only", "fixture alpha")]
        report = self.report(card, records, "EVIDENCE")
        self.assertEqual({row["number"] for row in report["matches"]}, {1, 2, 3})
        report = self.report(card, records, "EVIDENCE", "--all-terms")
        self.assertEqual([row["number"] for row in report["matches"]], [1])

    def test_catalogue_terms_and_literal_package_names_are_not_stopwords(self):
        cards = [
            {"id": "fixture", "overlap_terms": ["evidence"],
             "starting_points": ["research/alpha/proofs/note.md"]},
            {"id": "fixture", "starting_points": ["research/evidence/code/check.py"]},
        ]
        for card in cards:
            with self.subTest(card=card):
                report = self.report(card, [pull(1, "Evidence")])
                self.assertEqual([row["number"] for row in report["matches"]], [1])


if __name__ == "__main__":
    unittest.main()
