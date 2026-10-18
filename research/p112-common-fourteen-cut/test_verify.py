#!/usr/bin/env python3
"""Behavioral and semantic-mutation controls for the scoped P112 census."""

import copy
import itertools
import subprocess
import sys
import tempfile
import unittest
from math import gcd
from pathlib import Path

import geometry
import verify


def xor_span(values):
    span = {0}
    for value in values:
        span |= {x ^ value for x in span}
        if len(span) > 512:
            raise ValueError("binary span capacity")
    return span


def triangular_label(row):
    c = [0] * 8
    c[0] = row[7]
    c[7] = (row[6] + c[0]) // 2
    for j in range(6, 2, -1):
        c[j] = (row[j - 1] + c[0]) // 2 + c[j + 1]
    c[1] = (row[0] + row[1] + 2 * c[3]) // 4
    c[2] = (-row[0] + row[1] + 2 * c[0] + 2 * c[3]) // 4
    return 1 | sum((x % 2) << (i + 1) for i, x in enumerate(c))


def short_lattice_normals():
    """Direct E8 norm-two/norm-four projective list, without Weyl closure."""

    def primitive(row):
        divisor = gcd(*row)
        row = tuple(x // divisor for x in row)
        return max(row, tuple(-x for x in row))

    result = {primitive(row) for row in geometry.root_lines()}
    for i in range(8):
        row = [0] * 8
        row[i] = 4
        result.add(primitive(row))
    for support in itertools.combinations(range(8), 4):
        for signs in itertools.product((-2, 2), repeat=4):
            row = [0] * 8
            for i, sign in zip(support, signs, strict=True):
                row[i] = sign
            result.add(primitive(row))
    for exceptional in range(8):
        for signs in itertools.product((-1, 1), repeat=8):
            row = tuple(signs[i] * (3 if i == exceptional else 1) for i in range(8))
            if sum(row) % 4 == 0:
                result.add(primitive(row))
    return result


class CensusControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix="p112-common-controls-")
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.output = Path(cls.temporary.name)
        cls.fixture, cls.coverage, _ = verify.prepare_fixture(cls.output)
        cls.executable = verify.compile_census(cls.output)
        cls.directions, _ = geometry.direction_catalogue()

    def test_root_and_label_reconstruction(self):
        roots = geometry.root_lines()
        self.assertEqual(len(roots), 120)
        self.assertEqual(geometry.validate_root_system(roots), 960)
        self.assertEqual(
            [geometry.exact_label(r) for r in roots],
            [triangular_label(r) for r in roots],
        )
        self.assertEqual(len(set(map(triangular_label, roots))), 120)

    def test_root_mutation_rejected(self):
        roots = list(geometry.root_lines())
        roots[0] = (9,) + roots[0][1:]
        with self.assertRaises(ValueError):
            geometry.validate_root_system(roots)

    def test_complete_direction_cutoff(self):
        points = [r for r in geometry.root_lines() if r not in geometry.frame_lines()]
        sizes = [
            sum(bool(sum(x * y for x, y in zip(h, p, strict=True))) for p in points)
            for h in self.directions
        ]
        self.assertEqual(sorted(sizes), [53] * 112 + [56] * 8 + [70] * 128 + [73] * 896)
        self.assertEqual(max(self.coverage["rank_six_parabolic_counts"]), 36)
        self.assertEqual(
            self.coverage["chamber_zero_counts"], [42, 28, 22, 14, 16, 23, 37, 63]
        )

    def test_independent_short_lattice_inventory(self):
        all_normals = short_lattice_normals()
        self.assertEqual(len(all_normals), 1200)
        points = [r for r in geometry.root_lines() if r not in geometry.frame_lines()]
        selected = {
            h
            for h in all_normals
            if sum(bool(sum(x * y for x, y in zip(h, p, strict=True))) for p in points)
            <= 74
        }
        self.assertEqual(selected, set(self.directions))

    def test_binary_rank_by_literal_xor_closure(self):
        labels = [triangular_label(r) for r in geometry.root_lines()]
        self.assertEqual(len(xor_span(labels)), 512)
        for n in range(1, 10):
            self.assertEqual(len(xor_span([1 << i for i in range(n)])), 1 << n)
        # All independent-character deletion minima in dimensions seven to nine.
        for n in range(7, 10):
            minima = [cut for cut in range(1 << n) if cut.bit_count() == n - 6]
            self.assertEqual(
                len(minima), len(list(itertools.combinations(range(n), n - 6)))
            )
            self.assertTrue(
                all(
                    len(xor_span([1 << i for i in range(n) if not cut >> i & 1])) == 64
                    for cut in minima
                )
            )

    def test_actual_native_ranks_match_fraction(self):
        text = verify.run_command(
            [str(self.executable), "--rank-controls", str(self.fixture)],
            15,
            self.output,
            "rank-crosscheck",
        )
        verify.check_rank_controls(text, self.directions)
        bad = text.replace("RANK 1 1 ", "RANK 1 0 ", 1)
        with self.assertRaises(ValueError):
            verify.check_rank_controls(bad, self.directions)
        with self.assertRaises(ValueError):
            verify.check_rank_controls(
                "\n".join(text.splitlines()[:-1]), self.directions
            )

    def test_literal_original_caller(self):
        result = verify.application_check()
        self.assertEqual(result["required_span"], 6)
        self.assertEqual(result["common_cut_cap"], 14)
        self.assertEqual(result["profile"], (2, 3, 4) + (6,) * 8)

    def test_input_hash_mutation(self):
        root = self.output / "source-mutant"
        for row in verify.read_json(verify.PACKAGE / "SOURCES.json")["files"]:
            if row["usage"] == "input":
                target = root / row["path"]
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((verify.ROOT / row["path"]).read_bytes())
        verify.check_sources(root=root)
        path = root / "research/one-sided-six-multisets/data/gens.txt"
        path.write_bytes(path.read_bytes() + b"\n")
        with self.assertRaisesRegex(ValueError, "changed live input"):
            verify.check_sources(root=root)

    def test_vendor_hash_mutation(self):
        package = self.output / "vendor-mutant"
        package.mkdir()
        source_manifest = verify.PACKAGE / "SOURCES.json"
        (package / "SOURCES.json").write_bytes(source_manifest.read_bytes())
        for row in verify.read_json(source_manifest)["upstream"]:
            target = package / row["local_path"]
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((verify.PACKAGE / row["local_path"]).read_bytes())
        verify.check_sources(package=package)
        target = package / "vendor/PR3185-PROOF.md"
        target.write_bytes(target.read_bytes() + b"\n")
        with self.assertRaisesRegex(ValueError, "changed retained source"):
            verify.check_sources(package=package)

    def test_completion_and_range_controls(self):
        good = "ROW 0 0 0 32 1 0 0 0 0 0\nPASS_COMMON_FOURTEEN 0 1\n"
        self.assertEqual(len(verify.parse_rows(good, 0, 1)), 1)
        for bad in (
            good.splitlines()[0],
            good.replace("ROW 0", "ROW 1"),
            good.replace(" 32 ", " 33 "),
            good + "extra\n",
        ):
            with self.assertRaises(ValueError):
                verify.parse_rows(bad, 0, 1)

    def test_receipt_missing_half_or_wrong_counter(self):
        expected = verify.read_json(verify.PACKAGE / "RESULT.json")
        actual = copy.deepcopy(expected)
        actual["rows"] = actual["rows"][:80]
        verify.check_receipt(actual, expected, 0, 80)
        broken = copy.deepcopy(expected)
        broken["rows"].pop()
        with self.assertRaises(ValueError):
            verify.check_receipt(actual, broken, 0, 80)
        actual["rows"][0][-1] += 1
        with self.assertRaises(ValueError):
            verify.check_receipt(actual, expected, 0, 80)

    def test_native_input_and_range_rejections(self):
        for args in (
            [str(self.fixture), "-1", "1"],
            [str(self.fixture), "0", "161"],
            [str(self.fixture), "2147483647", "2147483647"],
            [str(self.fixture), "1", "2147483647"],
            [str(self.fixture), "0", "1", "extra"],
        ):
            result = subprocess.run(
                [str(self.executable), *args],
                capture_output=True,
                text=True,
                timeout=15,
                check=False,
            )
            self.assertEqual(result.returncode, 2)
            expected = "invalid orbit range" if len(args) == 3 else "usage:"
            self.assertIn(expected, result.stderr)
        bad = self.output / "bad-fixture.txt"
        bad.write_text("0\n")
        result = subprocess.run(
            [str(self.executable), str(bad), "0", "1"],
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("invalid label", result.stderr)

    def test_child_failure_and_timeout(self):
        with self.assertRaises(ValueError):
            verify.run_command(
                [sys.executable, "-c", "raise SystemExit(7)"],
                5,
                self.output,
                "failed-child",
            )
        with self.assertRaises(subprocess.TimeoutExpired):
            verify.run_command(
                [sys.executable, "-c", "import time; time.sleep(2)"],
                0.05,
                self.output,
                "timed-child",
            )

    def test_semantic_mutants_rejected(self):
        source = (verify.PACKAGE / "census.cpp").read_text()
        changes = (
            ("dependent-character", "!(words[c] == (words[a] ^ words[b]))", "true", 2),
            (
                "separate-cuts",
                "weight(next) <= budget",
                "weight(next) <= 2 * budget",
                1,
            ),
            (
                "truncated-rank",
                "if (rank >= 6) return rank;",
                "if (rank >= 5) return rank;",
                1,
            ),
        )
        for name, old, new, count in changes:
            with self.subTest(name=name):
                self.assertEqual(source.count(old), count)
                path = self.output / f"{name}.cpp"
                executable = self.output / name
                path.write_text(source.replace(old, new))
                result = subprocess.run(
                    ["g++", *verify.FLAGS, str(path), "-o", str(executable)],
                    capture_output=True,
                    text=True,
                    timeout=60,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                result = subprocess.run(
                    [str(executable), "--self-test"],
                    capture_output=True,
                    text=True,
                    timeout=45,
                    check=False,
                )
                self.assertNotEqual(result.returncode, 0, name)
                self.assertIn("FAIL:", result.stderr)


if __name__ == "__main__":
    unittest.main()
