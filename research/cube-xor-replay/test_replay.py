#!/usr/bin/env python3
"""Independent permutation checks, mathematical controls, package guards."""
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import replay
from cached_xor import CachedXorPermuter


def bit_loop(bits, index, n):
    # Deliberately avoid block masks and shifts of entire blocks.
    return sum(1 << (j ^ index) for j in range(n) if bits >> j & 1)


class PermutationTests(unittest.TestCase):
    def test_exhaustive_small_rows(self):
        fast = CachedXorPermuter()
        for n in (1, 2, 4, 8):
            for bits in range(1 << n):
                for index in range(n):
                    self.assertEqual(fast(bits, index, n), bit_loop(bits, index, n))

    def test_every_basis_and_index(self):
        fast = CachedXorPermuter()
        for n in (16, 32, 64, 128):
            for bit in range(n):
                for index in range(n):
                    self.assertEqual(fast(1 << bit, index, n), 1 << (bit ^ index))

    def test_seeded_dense_rows_and_group_law(self):
        rng = random.Random(94)
        fast = CachedXorPermuter()
        for n in (16, 32, 64, 128, 256, 512, 1024, 2048):
            for _ in range(12):
                bits, i, j = rng.getrandbits(n), rng.randrange(n), rng.randrange(n)
                self.assertEqual(fast(bits, i, n), bit_loop(bits, i, n))
                self.assertEqual(fast(fast(bits, i, n), j, n), fast(bits, i ^ j, n))
                self.assertEqual(fast(fast(bits, i, n), i, n), bits)

    def test_high_coordinates_and_mixed_width_cache_keys(self):
        fast = CachedXorPermuter()
        for n in (1 << 21, 8, 1 << 15, 1 << 21):
            for b in range(n.bit_length() - 1):
                for j in (0, n // 2 - 1, n // 2, n - 1):
                    self.assertEqual(fast(1 << j, 1 << b, n), 1 << (j ^ (1 << b)))
        # A changed input row at an already used shift must be recomputed.
        self.assertEqual(fast(1, 1, 8), 2)
        self.assertEqual(fast(128, 1, 8), 64)

    def test_reject_invalid_inputs_on_cold_and_warm_calls(self):
        _, core = replay.load_original()
        bad = [(0, 0, 0), (0, 0, 3), (0, 0, -2), (0, 0, True),
               (0, 0, 8.0), (0, -1, 8), (0, 8, 8), (0, True, 8),
               (0, 1.0, 8), (-1, 0, 8), (256, 0, 8), (True, 0, 8),
               (1.0, 0, 8)]
        for args in bad:
            for warmed in (False, True):
                fast = CachedXorPermuter()
                if warmed:
                    fast(93, 7, 8)
                for fn in (core.xor_permute, fast):
                    with self.assertRaisesRegex(ValueError, "Invalid packed row"):
                        fn(*args)

    def test_mutated_mask_detected_even_when_rank_is_preserved(self):
        fast = CachedXorPermuter()
        fast(1, 1, 8)
        fast._masks[(8, 1)] ^= 1
        self.assertNotEqual(fast(1, 1, 8), bit_loop(1, 1, 8))
        # Dropping an index bit is still a permutation, hence preserves rank.
        _, core = replay.load_original()
        row = core.quadratic_code_base(3)["base"]
        self.assertNotEqual(core.xor_permute(row, 1, 64), row)

    def test_no_input_results_are_cached(self):
        fast = CachedXorPermuter()
        for bits in range(256):
            fast(bits, 7, 8)
        self.assertEqual(set(fast._masks), {(8, 1), (8, 2), (8, 4)})


class ReplayTests(unittest.TestCase):
    def test_complete_historical_receipt_and_row_coverage(self):
        coverage = {"rows": 0, "coefficients": 0}
        expected = (replay.ROOT / "certificates/cube-core-family.json").read_bytes()
        self.assertEqual(replay.run("historical", "original"), expected)
        self.assertEqual(replay.run("historical", "cached"), expected)
        self.assertEqual(replay.run("historical", "differential", coverage), expected)
        self.assertEqual(coverage, {"rows": 228, "coefficients": 6993024})

    def test_zero_budget_and_incomplete_screen_preserved(self):
        _, core = replay.load_original()
        with replay.backend(core, "cached"):
            with self.assertRaisesRegex(ValueError, "Positive row budget"):
                core.quadratic_rank_screen(3, maximum_rows=0)
            limited = core.quadratic_rank_screen(5, maximum_rows=1)
        self.assertEqual(limited["rows_checked"], 1)
        self.assertFalse(limited["specified_core_positive_deficit_excluded"])

    def test_adapter_restores_original_after_failure(self):
        _, core = replay.load_original()
        original = core.xor_permute
        with self.assertRaisesRegex(RuntimeError, "test failure"):
            with replay.backend(core, "cached"):
                raise RuntimeError("test failure")
        self.assertIs(core.xor_permute, original)

    def test_omitted_shift_is_detected_by_full_replay(self):
        # Using j -> j xor (index xor 1) retains every rank by a common
        # invertible column permutation, but changes the witness stream.
        original = CachedXorPermuter.__call__
        def shifted(self, bits, index, n):
            return original(self, bits, index ^ 1, n)
        _, core = replay.load_original()
        baseline = {t: core.quadratic_rank_screen(t) for t in (3, 4, 5)}
        with patch.object(CachedXorPermuter, "__call__", shifted):
            with replay.backend(core, "cached"):
                for t, before in baseline.items():
                    after = core.quadratic_rank_screen(t)
                    for field in ("binary_rank_lower_bound", "independent_row_indices",
                                  "rows_checked", "specified_core_positive_deficit_excluded"):
                        self.assertEqual(after[field], before[field])
                    self.assertNotEqual(after["independent_row_sha256"],
                                        before["independent_row_sha256"])
            with self.assertRaisesRegex(ValueError, "Complete receipt mismatch"):
                replay.run("historical", "cached")

    def test_no_row_can_be_skipped(self):
        original = CachedXorPermuter.__call__
        def missing(self, bits, index, n):
            return 0 if index == 0 else original(self, bits, index, n)
        with patch.object(CachedXorPermuter, "__call__", missing):
            with self.assertRaises(ValueError):
                replay.run("historical", "cached")


class PackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix="cube xor minimal ")
        cls.root = Path(cls.temporary.name)
        manifest = replay.check_sources()
        for relative in manifest["files"]:
            target = cls.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(replay.ROOT / relative, target)
        cls.package = cls.root / "research/cube-xor-replay"
        cls.package.mkdir(parents=True, exist_ok=True)
        for path in HERE.iterdir():
            if path.is_file():
                shutil.copyfile(path, cls.package / path.name)

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def launch(self, *extra):
        return subprocess.run([sys.executable, "-I", "-O", "-B",
                               str(self.package / "replay.py"), *extra],
                              cwd=self.root.parent, capture_output=True, text=True)

    def test_offline_relocated_optimized_replay(self):
        result = self.launch()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PASS_CUBE_XOR_REPLAY", result.stdout)

    def test_changed_source_and_expected_certificate_rejected(self):
        for relative in ("scripts/experiments/cube_core_family.py",
                         "scripts/audit_fused_block.py",
                         "scripts/exclusion_circuit.py",
                         "scripts/shared_point_circuit.py",
                         "certificates/cube-core-family.json", "upstream/README.md"):
            path = self.root / relative
            original = path.read_bytes()
            try:
                path.write_bytes(original + b"\n")
                result = self.launch()
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("Source pin mismatch", result.stderr)
                self.assertNotIn("PASS_CUBE_XOR_REPLAY", result.stdout)
            finally:
                path.write_bytes(original)

    def test_existing_output_is_not_overwritten(self):
        output = self.root / "already exists.json"
        output.write_bytes(b"keep me")
        result = self.launch("--output", str(output))
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(output.read_bytes(), b"keep me")

    def test_unknown_backend_rejected(self):
        result = self.launch("--backend", "guess")
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("PASS_CUBE_XOR_REPLAY", result.stdout)

    def test_manifest_and_t6_fixture_changes_rejected(self):
        for name, message in (("SOURCES.json", "Source manifest mismatch"),
                              ("COMPATIBILITY.json", "Compatibility manifest mismatch"),
                              ("EXPECTED-T6.json", "Fixture pin mismatch")):
            path = self.package / name
            original = path.read_bytes()
            try:
                path.write_bytes(original + b"\n")
                result = self.launch()
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(message, result.stderr)
                self.assertNotIn("PASS_CUBE_XOR_REPLAY", result.stdout)
            finally:
                path.write_bytes(original)


if __name__ == "__main__":
    unittest.main()
