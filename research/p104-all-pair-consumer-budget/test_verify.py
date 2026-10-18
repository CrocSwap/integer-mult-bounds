#!/usr/bin/env python3
"""Behavioral and mathematical controls for the all-p P104 budget theorem."""

import gzip
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from collections import Counter
from fractions import Fraction as Q
from math import isqrt
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("p104_budget", PACKAGE / "verify.py")
VERIFY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFY)


class MathematicalControls(unittest.TestCase):
    """Literal fixtures and failures at the actual arithmetic boundaries."""

    def test_source_profiles_and_p4_predecessor(self):
        VERIFY.authenticate()
        forward, dual = VERIFY.source_profiles()
        self.assertEqual(VERIFY.mass(forward), 3070)
        self.assertEqual(VERIFY.mass(dual), 3542)
        relaxed = VERIFY.discounted(dual)
        self.assertEqual(
            {r: 5 * forward[r] + 4 * relaxed[r] for r in forward},
            {1: 10408, 2: 610, 3: 726, 4: 888, 5: 472, 6: 434, 7: 708, 8: 72},
        )
        self.assertEqual(72 * 832 - 9 * VERIFY.PROGRESS, 32778)
        self.assertEqual(VERIFY.mass(relaxed), 3126)

    def test_independent_span_census(self):
        def span(frame):
            values = {0}
            for vector in frame:
                values |= {value ^ vector for value in values}
            return values

        core, _ = VERIFY.load_json(
            VERIFY.ROOT / "research/p104-native-channel/inputs/LOWRANK-WITNESS.json"
        )
        correction, _ = VERIFY.load_json(
            PACKAGE / "inputs/PR2458-CIRCUIT.json.gz", compressed=True
        )
        dual, _ = VERIFY.load_json(
            PACKAGE / "inputs/PR2712-WORD.json.gz", compressed=True
        )
        forward_events = core["program"] + [
            event for cut in correction["insertions"] for event in cut["events"]
        ]
        for events, expected in [
            (forward_events, VERIFY.FORWARD),
            (dual["program"], VERIFY.DUAL),
        ]:
            census = Counter()
            for event in events:
                if event[0] == "transport":
                    before, after = span(event[2]), span(event[3])
                    self.assertTrue(before <= after or after <= before)
                    rank = abs(len(after).bit_length() - len(before).bit_length())
                    self.assertEqual(rank, event[4])
                    census[rank] += 1
            self.assertEqual(dict(census), expected)

    def test_all_p_certificate(self):
        proof = VERIFY.prove(VERIFY.FORWARD, VERIFY.DUAL)
        self.assertEqual(proof["p1_mass_excess"], 4066)
        self.assertEqual([r["pairs"] for r in proof["finite"]], [2, 3, 4, 5, 6, 7])
        self.assertTrue(
            all(Q(r["excess_numerator_lower"]) > 46 for r in proof["finite"])
        )
        self.assertEqual(proof["tail_from_pairs"], 8)
        self.assertGreater(Q(proof["tail_slope_lower"]), Q(2, 3))
        self.assertGreater(Q(proof["tail_intercept_lower"]), 76)

    def test_paid_bank_clamping_boundary(self):
        proof = VERIFY.prove(VERIFY.FORWARD, VERIFY.DUAL)
        self.assertEqual(proof["p1_any_paid_banks_mass_excess_lower"], 16)
        for banks, expected_excess in [
            (0, 4066),
            (161, 41),
            (162, 16),
            (163, 16),
            (10**12, 16),
        ]:
            idle = max(0, -4050 + 25 * banks)
            self.assertEqual(9266 + idle - 25 * (208 + banks), expected_excess)
        for pairs in range(2, 8):
            width, roles = 16 * pairs + 9, 208 * pairs
            for banks in (0, 1, 1000):
                idle = (width - 1) * roles + width * banks - (2 * pairs + 1) * 3014
                paid = (pairs + 1) * 3070 + pairs * 3126
                self.assertEqual(paid + idle - width * (roles + banks), 56 - 40 * pairs)

    def test_exact_log_and_discount_fixtures(self):
        self.assertEqual(VERIFY.log_lower(Q(1)), 0)
        self.assertEqual(VERIFY.log_lower(Q(2)), Q(693147, 1_000_000))
        self.assertEqual(VERIFY.log_lower(Q(137)), Q(614347, 125000))
        # Independently enclose every integer-rank deletion at saving 1/2.
        # The README proves all savings; this is a finite fixture of that lemma.
        scale = 1_000_000
        for rank in range(1, 9):
            root_floor = isqrt(rank * scale * scale)
            root_ceil = root_floor + (root_floor * root_floor != rank * scale * scale)
            for delta in range(1, rank + 1):
                rest_floor = isqrt((rank - delta) * scale * scale)
                self.assertLessEqual(Q(root_ceil - rest_floor, scale), delta)
        with self.assertRaisesRegex(ValueError, "discount bound"):
            VERIFY.discounted(VERIFY.DUAL, 2000)
        with self.assertRaisesRegex(ValueError, "log domain"):
            VERIFY.log_lower(Q(138))

    def test_semantic_rejections(self):
        understated = dict(VERIFY.DUAL)
        understated[1] -= 1
        with self.assertRaisesRegex(ValueError, "source masses"):
            VERIFY.prove(VERIFY.FORWARD, understated)
        base_slope, base_intercept = VERIFY.coefficients(
            VERIFY.FORWARD, VERIFY.discounted(VERIFY.DUAL), 41
        )
        self.assertLess(-24 + Q(1, 10000) * (2 * base_slope + base_intercept), 0)
        with self.assertRaisesRegex(ValueError, "finite p=2"):
            VERIFY.prove(VERIFY.FORWARD, VERIFY.DUAL, Q(1, 10000))
        with self.assertRaisesRegex(ValueError, "saving domain"):
            VERIFY.prove(VERIFY.FORWARD, VERIFY.DUAL, Q(0))
        with self.assertRaisesRegex(ValueError, "transport rank"):
            VERIFY.transport_profile([["transport", "r", [], [1, 2], 1]])
        with self.assertRaisesRegex(ValueError, "nonnested"):
            VERIFY.transport_profile([["transport", "r", [1], [2], 1]])
        slope, _ = VERIFY.coefficients(
            VERIFY.FORWARD, VERIFY.discounted(VERIFY.DUAL), 73
        )
        self.assertLess(VERIFY.KAPPA * slope - 40, 0)
        self.assertEqual(
            VERIFY.transport_profile([["transport", "r", [3, 1], [2, 1, 4], 1]]),
            {1: 1},
        )


class ArtifactControls(unittest.TestCase):
    """Run the public optimized CLI from a Git-free export, including faults."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.package = self.root / "research/p104-all-pair-consumer-budget"
        shutil.copytree(
            PACKAGE, self.package, ignore=shutil.ignore_patterns("__pycache__")
        )
        sources = json.loads((PACKAGE / "SOURCES.json").read_text())
        for row in sources["files"]:
            if row["usage"] == "input":
                destination = self.root / row["path"]
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(VERIFY.ROOT / row["path"], destination)

    def cli(self):
        return subprocess.run(
            [sys.executable, "-I", "-O", "-B", str(self.package / "verify.py")],
            cwd=self.root,
            text=True,
            capture_output=True,
            timeout=30,
            check=False,
        )

    def test_git_free_positive_and_recompression(self):
        result = self.cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PASS_P104_ALL_PAIR_CONSUMER_BUDGET", result.stdout)
        path = self.package / "inputs/PR2712-WORD.json.gz"
        raw = gzip.decompress(path.read_bytes())
        path.write_bytes(gzip.compress(raw, compresslevel=1, mtime=123456789))
        result = self.cli()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_changed_source_rejects(self):
        path = self.package / "inputs/PR2458-CIRCUIT.json.gz"
        data = json.loads(gzip.decompress(path.read_bytes()))
        data["source_witness_sha256"] = "0" * 64
        path.write_bytes(gzip.compress(json.dumps(data).encode()))
        result = self.cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("PR2458-CIRCUIT", result.stderr)

    def test_changed_receipt_rejects(self):
        path = self.package / "RESULT.json"
        data = json.loads(path.read_text())
        data["proof"]["tail_from_pairs"] = 9
        path.write_text(json.dumps(data))
        result = self.cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("receipt mismatch", result.stderr)

    def test_typed_receipt_rejects(self):
        path = self.package / "RESULT.json"
        data = json.loads(path.read_text())
        data["schema_version"] = True
        path.write_text(json.dumps(data))
        result = self.cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("receipt mismatch", result.stderr)

    def test_duplicate_key_rejects(self):
        path = self.package / "RESULT.json"
        path.write_text('{"schema_version":1,"schema_version":2}')
        result = self.cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("duplicate key", result.stderr)


if __name__ == "__main__":
    unittest.main()
