"""Behavioral controls for the mixed-rank theorem's public replay surface."""

import copy
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import verify as v


class ReplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(
            prefix="p112-anchor-tests-", dir=os.environ.get("TMPDIR")
        )
        cls.work = Path(cls.temporary.name)
        cls.fixture, _ = v.fixture(*(v.ROOT / name for name in v.INPUTS))
        cls.data = v.parse_fixture(cls.fixture)
        cls.path = cls.work / "fixture.txt"
        cls.path.write_text(cls.fixture)
        cls.binary = v.build(cls.work)
        cls.raw = v.run([str(cls.binary), str(cls.path)], cls.work, "census.txt")
        cls.result = json.loads((v.PACKAGE / "RESULT.json").read_text())

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def rejects_native(self, args, text):
        result = subprocess.run(
            [str(self.binary), *args], capture_output=True, text=True, timeout=10
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn(text, result.stderr)

    def test_complete_replay_and_literal_theorem(self):
        actual = v.audit_census(self.raw, self.data)
        self.assertEqual(json.loads(json.dumps(actual)), self.result["census"])
        self.assertEqual(
            actual["total"],
            {
                "pairs": 123511995,
                "anchor_tests": 987,
                "positive_pairs": 832,
                "rank_six_oracle_calls": 2146,
                "max_span": 3,
            },
        )

    def test_native_invalid_modes(self):
        self.rejects_native([], "usage:")
        self.rejects_native([str(self.path), "--unknown"], "unknown mode")
        self.rejects_native([str(self.work / "absent")], "cannot read fixture")

    def test_native_duplicate_even_trailing_and_truncated_inputs(self):
        lines = self.fixture.splitlines()
        labels = lines[0].split()
        cases = [
            (labels[:1] + labels[:-1], "invalid label"),
            (["2", *labels[1:]], "labels must be odd"),
        ]
        for index, (changed, expected) in enumerate(cases):
            mutant = self.work / f"labels-{index}.txt"
            mutant.write_text(" ".join(changed) + "\n" + "\n".join(lines[1:]) + "\n")
            self.rejects_native([str(mutant)], expected)
        for index, (text, expected) in enumerate(
            (
                (self.fixture + "extra\n", "trailing"),
                (lines[0] + "\n", "invalid coordinate"),
            )
        ):
            mutant = self.work / f"boundary-{index}.txt"
            mutant.write_text(text)
            self.rejects_native([str(mutant)], expected)

    def test_cut_budget_membership_and_rank(self):
        labels = self.data[0]
        rest = (1 << 20) - 1
        with self.assertRaisesRegex(ValueError, "deletion cut"):
            v.check_cut(rest, (1 << 13) - 1, 4, labels)
        with self.assertRaisesRegex(ValueError, "deletion cut"):
            v.check_cut(rest, 1 << 50, 4, labels)
        with self.assertRaisesRegex(ValueError, "residual rank"):
            v.check_cut(rest, 0, 4, labels)
        v.check_cut(15, 0, 4, labels)
        self.assertEqual(v.binary_rank(v.values(15, labels)), 3)

    def test_binary_and_characteristic_zero_rank_are_distinct(self):
        rows = [
            [1, 1, 0, 0, 0, 0, 0, 0],
            [1, 0, 1, 0, 0, 0, 0, 0],
            [0, 1, 1, 0, 0, 0, 0, 0],
        ]
        self.assertEqual(v.rational_rank(rows), 3)
        self.assertEqual(v.binary_rank([3, 5, 6]), 2)
        rows[-1] = [2, 1, 1, 0, 0, 0, 0, 0]
        self.assertEqual(v.rational_rank(rows), 2)

    def test_anchor_oracle_positive_negative_and_capacity(self):
        labels = self.data[0]
        self.assertTrue(v.anchor_oracle(15, labels, 0))
        self.assertFalse(v.anchor_oracle((1 << 20) - 1, labels, 0))
        with self.assertRaisesRegex(ValueError, "capacity"):
            v.anchor_oracle((1 << 21) - 1, labels)
        self.assertEqual(len(v.binary_span([1, 3, 5, 9])), 16)

    def test_missing_row_and_inconsistent_total(self):
        lines = self.raw.splitlines()
        removed = (
            "\n".join(line for line in lines if not line.startswith("ROW 42 ")) + "\n"
        )
        with self.assertRaises(ValueError):
            v.audit_census(removed, self.data)
        mutant = self.raw.replace(
            "TOTAL 123511995 987 832 2146 3", "TOTAL 123511994 987 832 2146 3"
        )
        with self.assertRaisesRegex(ValueError, "coverage total"):
            v.audit_census(mutant, self.data)
        with self.assertRaisesRegex(ValueError, "line capacity"):
            v.audit_census("", self.data)

    def test_missing_direction_and_mutated_cut(self):
        lines = self.raw.splitlines()
        position = next(i for i, line in enumerate(lines) if line.startswith("POS "))
        parts = lines[position].split()
        parts[1] = str(int(parts[1]) + 1)
        lines[position] = " ".join(parts)
        with self.assertRaisesRegex(ValueError, "positive list capacity"):
            v.audit_census("\n".join(lines), self.data)
        parts = self.raw.splitlines()[position].split()
        parts[3] = str((1 << 64) - 1)
        lines[position] = " ".join(parts)
        with self.assertRaisesRegex(ValueError, "deletion cut"):
            v.audit_census("\n".join(lines), self.data)

    def test_unanchored_rank_five_control(self):
        actual = v.unanchored_control(self.data)
        self.assertEqual(actual["rank"], 5)
        self.assertEqual(
            json.loads(json.dumps(actual)), self.result["unanchored_control"]
        )

    def test_fourteen_anchor_extension_is_false(self):
        actual = v.fourteen_control(self.data)
        self.assertEqual(actual["rank"], 5)
        self.assertGreater(actual["cut_union_size"], 14)
        mutant = self.work / "fourteen-mutant.json"
        control = copy.deepcopy(actual["witness"])
        control["anchor"]["cut"] = [0, 0]
        mutant.write_text(json.dumps(control))
        with self.assertRaisesRegex(ValueError, "residual rank"):
            v.fourteen_control(self.data, mutant)

    def test_new_beta_shape_and_remaining_shape(self):
        actual = v.beta_application()
        self.assertEqual(actual["nonbasis_weights"], [4, 6, 6, 6, 6])
        self.assertEqual(actual["support_cap"], 52)
        self.assertEqual(actual["remaining_from_PR3162"], [2, 5, 5, 5, 6, 6, 6, 6, 6])
        self.assertEqual(
            actual["forced_direction_rank"] - actual["finite_upper_bound"], 2
        )

    def test_source_binding_and_exact_inventory(self):
        root = self.work / "source-control"
        package = root / "research/p112-mixed-rank-anchor"
        package.mkdir(parents=True)
        shutil.copytree(v.PACKAGE / "vendor", package / "vendor")
        shutil.copyfile(v.PACKAGE / "SOURCES.json", package / "SOURCES.json")
        for name in v.INPUTS:
            target = root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((v.ROOT / name).read_bytes())
        self.assertEqual(v.bound_sources(root, package), self.result["sources"])
        path = package / "vendor/geometry.py"
        path.write_bytes(path.read_bytes() + b"\n")
        with self.assertRaisesRegex(ValueError, "changed source"):
            v.bound_sources(root, package)
        path.write_bytes((v.PACKAGE / "vendor/geometry.py").read_bytes())
        target = root / v.INPUTS[0]
        target.write_bytes(target.read_bytes() + b"\n")
        with self.assertRaisesRegex(ValueError, "changed source"):
            v.bound_sources(root, package)

    def test_receipt_mismatch_fails_cli(self):
        package = self.work / "receipt-control/research/p112-mixed-rank-anchor"
        shutil.copytree(v.PACKAGE, package)
        for name in v.INPUTS:
            target = package.parent.parent / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((v.ROOT / name).read_bytes())
        receipt = copy.deepcopy(self.result)
        receipt["census"]["total"]["max_span"] = 4
        (package / "RESULT.json").write_text(json.dumps(receipt))
        env = os.environ | {"PYTHONDONTWRITEBYTECODE": "1"}
        result = subprocess.run(
            [os.sys.executable, "-B", str(package / "verify.py")],
            env=env,
            capture_output=True,
            text=True,
            timeout=180,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("receipt mismatch", result.stderr)

    def test_compiled_anchor_and_coverage_mutants(self):
        source = (v.PACKAGE / "scan.cpp").read_text()
        mutants = (
            ("size <= budget + 4", "size <= budget + 5", "--self-test"),
            ("ri < reps.size()", "ri + 1 < reps.size()", None),
        )
        for index, (before, after, mode) in enumerate(mutants):
            package = self.work / f"native-mutant-{index}"
            package.mkdir()
            (package / "vendor").mkdir()
            shutil.copyfile(
                v.PACKAGE / "vendor/census.cpp", package / "vendor/census.cpp"
            )
            self.assertEqual(source.count(before), 1)
            (package / "scan.cpp").write_text(source.replace(before, after))
            binary = v.build(package, package)
            args = [str(binary), str(self.path)] + ([mode] if mode else [])
            result = subprocess.run(args, capture_output=True, text=True, timeout=180)
            if mode:
                self.assertEqual(result.returncode, 2)
                self.assertIn("oracle disagrees", result.stderr)
            else:
                self.assertEqual(result.returncode, 0)
                with self.assertRaises(ValueError):
                    v.audit_census(result.stdout, self.data)


if __name__ == "__main__":
    unittest.main()
