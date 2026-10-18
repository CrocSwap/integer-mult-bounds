"""Reject incomplete releases and damaged actual outer evidence.

Substantial OpenAI Codex assistance. Apache-2.0.
"""

import copy
import os
import subprocess
import sys
import tempfile
import unittest

import verify as v


class EvidenceControls(unittest.TestCase):
    @unittest.skipUnless(os.name == "posix", "full replay uses POSIX process cleanup")
    def test_cli_refuses_preflight_baseline(self):
        with tempfile.TemporaryDirectory() as directory:
            root = v.Path(directory)
            baseline = root / "baseline"
            baseline.mkdir()
            (baseline / "RESULT.json").write_text(
                v.json.dumps({"status": "PREFLIGHT_ONLY_NOT_A_RELEASE"})
            )
            (baseline / "STAGES.json").write_text("[]")
            output = root / "candidate"
            result = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(v.P / "reproduce.py"),
                    "--baseline-work",
                    str(baseline),
                    "--work",
                    str(output),
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("mandatory completed baseline", result.stderr)
            self.assertFalse(output.exists())

    def test_original_source_derivation(self):
        baseline, candidate = v.expected_adapter_hashes()
        valid = dict(
            reference_sha256=baseline,
            candidate_sha256=candidate,
            replacements=v.read(v.P / "PRECISION-EDITS.json"),
        )
        v.check_derivation(valid)
        for key in ("reference_sha256", "candidate_sha256"):
            with self.subTest(key=key), self.assertRaises(ValueError):
                v.check_derivation(dict(valid, **{key: "0" * 64}))

    def test_incomplete_releases(self):
        valid = dict(
            baseline_complete=True,
            candidate_complete=True,
            status="PASS_T740_SIX_SKIP_PRECISION30_COMPLETE_RELEASE",
        )
        v.completion(valid)
        for key in ("baseline_complete", "candidate_complete"):
            for value in (False, 1, "true"):
                with self.subTest(key=key, value=value):
                    bad = dict(valid, **{key: value})
                    with self.assertRaises(ValueError):
                        v.completion(bad)
        with self.assertRaises(ValueError):
            v.completion(dict(valid, status="PREFLIGHT_ONLY_NOT_A_RELEASE"))

    def test_actual_outer_mutants(self):
        path = v.ROOT / "research/rank7-t740-carrier-skips/evidence/OUTER-LEDGER.json"
        actual = v.read(path)
        point = actual["rows"]["struct_boundary_radix_union"]["kappa"]["rational"]
        v.check_ledger(actual, point)
        with self.assertRaises(ValueError):
            v.check_ledger(actual, v.Q(point) + v.Q(1, 10**30))
        zero = copy.deepcopy(actual)
        checks = zero["rows"]["struct_boundary_radix_union"]["strict_checks"]
        checks[next(iter(checks))]["rational"] = "0"
        with self.assertRaises(ValueError):
            v.check_ledger(zero, point)
        missing = copy.deepcopy(actual)
        missing["rejecting_controls"]["struct_boundary_radix_union"].popitem()
        with self.assertRaises(ValueError):
            v.check_ledger(missing, point)


if __name__ == "__main__":
    unittest.main()
