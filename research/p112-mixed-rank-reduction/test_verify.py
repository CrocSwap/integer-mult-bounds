"""Behavioral controls for the mathematical boundary and published replay."""

import copy
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import geometry
import survivors
import verify


class BoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix="p112-controls-")
        cls.work = Path(cls.temporary.name)
        cls.binary = verify.build(cls.work)
        cls.text = geometry.fixture(
            verify.ROOT / "research/one-sided-six-multisets/data/data.txt",
            verify.ROOT / "research/one-sided-six-multisets/data/gens.txt",
        )
        cls.data = cls.work / "fixture.txt"
        cls.data.write_text(cls.text)
        cls.result = json.loads((verify.PACKAGE / "RESULT.json").read_text())

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def native(self, arguments, data=None):
        return subprocess.run(
            [str(self.binary), str(data or self.data), *arguments],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )

    def test_literal_deletion_oracle(self):
        result = self.native(["--self-test"])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "PASS_ORACLE 36864 subsets 4096 budgets 9\n")

    def test_reject_budget_limit_and_malformed_integer(self):
        for arguments in (["9"], ["4junk"], ["4", "0"], ["4", "160"], ["4", "1junk"]):
            with self.subTest(arguments=arguments):
                self.assertEqual(self.native(arguments).returncode, 2)

    def test_reject_native_fixture_corruption(self):
        for index, replacement in ((0, "0"), (112, "0"), (113, "0"), (352, "112")):
            tokens = self.text.split()
            tokens[index] = replacement
            data = self.work / f"bad-{index}.txt"
            data.write_text(" ".join(tokens))
            with self.subTest(index=index):
                self.assertEqual(self.native(["--self-test"], data).returncode, 2)
        data = self.work / "trailing.txt"
        data.write_text(self.text + "unexpected\n")
        self.assertEqual(self.native(["--self-test"], data).returncode, 2)

    def test_prefix_is_not_a_complete_census(self):
        result = self.native(["4", "1"])
        self.assertEqual(result.returncode, 0, result.stderr)
        with self.assertRaisesRegex(ValueError, "incomplete orbit"):
            verify.parse_census(result.stdout, 4)

    def test_receipt_rows_and_totals(self):
        receipt = self.result["censuses"][1]
        self.assertEqual(len(receipt["rows"]), 159)
        for mutator in (
            lambda s: s.replace("rep 1 ", "rep 0 ", 1),
            lambda s: s.replace("positive_pairs 71726", "positive_pairs 71727"),
            lambda s: s.replace("flats 776805", "flats 776804"),
        ):
            text = self.receipt_text(receipt)
            with self.assertRaises(ValueError):
                verify.parse_census(mutator(text), 8)

    @staticmethod
    def receipt_text(receipt):
        lines = [f"flats 776805 reps 159 budget {receipt['budget']}"]
        for row in receipt["rows"]:
            lines.append(
                "rep {} flat {} lines {} active {} maxdirs {} positive_pairs {}".format(
                    *row
                )
            )
        if receipt["witness"] is not None:
            lines.insert(1, "WITNESS " + " ".join(map(str, receipt["witness"])))
        total = receipt["total"]
        lines.append(
            f"TOTAL maxdirs {total['max_directions']} "
            f"positive_pairs {total['positive_pairs']} "
            f"oracle_calls {total['oracle_calls']}"
        )
        return "\n".join(lines) + "\n"

    def test_three_independent_directions_and_separate_cuts(self):
        control = verify.witness_check(self.result["censuses"][1]["witness"])
        self.assertEqual(control["gram_determinant"], 256)
        self.assertEqual(control["cut_sizes"], [8, 8, 8])
        self.assertEqual(control["cut_union_size"], 12)

    def test_reject_wrong_witness_direction_or_cut(self):
        for index, value in ((5, 0), (6, 0), (7, 0), (0, 0), (4, 4)):
            witness = copy.deepcopy(self.result["censuses"][1]["witness"])
            witness[index] = value
            with self.subTest(index=index), self.assertRaises(ValueError):
                verify.witness_check(witness)

    def test_four_shapes_and_alternate_quotient_basis(self):
        result = survivors.remaining_shapes()
        self.assertEqual(result["examined"], 2793)
        self.assertEqual(result["new_survivors"], 0)
        self.assertEqual(result["old_survivors"][-1]["quotient_basis"], (4, 6, 6))
        self.assertEqual(result["old_survivors"][-1]["extra_lines"], 8)
        self.assertEqual(
            [x["direction_bound"] for x in result["old_survivors"]], [3, 4, 3, 3]
        )

    def test_reject_stronger_unproved_direction_bound(self):
        text = self.receipt_text(self.result["censuses"][1]).replace(
            "maxdirs 3", "maxdirs 2"
        )
        with self.assertRaises(ValueError):
            verify.parse_census(text, 8)

    def test_reject_nonautomorphism_permutation(self):
        roots = geometry.root_lines()
        points = tuple(row for row in roots if row not in geometry.frame_lines())
        labels = tuple(geometry.exact_label(row) for row in points)
        supports = tuple(
            sum(
                1 << i
                for i, row in enumerate(points)
                if sum(x * y for x, y in zip(row, h, strict=True))
            )
            for h in roots
        )
        generators = [
            [int(x) for x in line.split()] for line in self.text.splitlines()[121:]
        ]
        generators[0][0], generators[0][1] = generators[0][1], generators[0][0]
        with self.assertRaises(ValueError):
            geometry.validate_generators(labels, supports, generators)

    def test_reject_changed_source_before_native_execution(self):
        root = self.work / "changed-source"
        name = "research/one-sided-six-multisets/data/data.txt"
        target = root / name
        target.parent.mkdir(parents=True)
        target.write_bytes((verify.ROOT / name).read_bytes() + b"\n")
        with (
            patch.object(verify, "ROOT", root),
            self.assertRaisesRegex(ValueError, "changed source"),
        ):
            verify.bound_sources()

    def test_reject_source_capacity_exhaustion(self):
        root = self.work / "oversized-source"
        target = root / "research/one-sided-six-multisets/data/data.txt"
        target.parent.mkdir(parents=True)
        target.write_bytes(b"x" * 2_000_001)
        with patch.object(verify, "ROOT", root):
            with self.assertRaisesRegex(ValueError, "source capacity"):
                verify.bound_sources()

    def test_reject_changed_predecessor_excerpt(self):
        package = self.work / "changed-vendor"
        shutil.copytree(verify.PACKAGE, package)
        (package / "vendor/CONJECTURES.md").write_text("changed")
        with (
            patch.object(verify, "PACKAGE", package),
            self.assertRaisesRegex(ValueError, "changed predecessor"),
        ):
            verify.bound_sources()

    def test_git_free_read_only_cli_and_receipt_rejection(self):
        exported = self.work / "export"
        package = exported / "research/p112-mixed-rank-reduction"
        shutil.copytree(verify.PACKAGE, package)
        for row in json.loads((package / "SOURCES.json").read_text())["files"]:
            if row["usage"] == "input":
                destination = exported / row["path"]
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(verify.ROOT / row["path"], destination)
        environment = dict(
            os.environ, PYTHONPYCACHEPREFIX=str(self.work / "export-bytecode")
        )
        result_path = package / "RESULT.json"
        original = result_path.read_bytes()
        result = json.loads(original)
        result["new_kappa"] = True
        result_path.write_text(json.dumps(result))
        bad = subprocess.run(
            [sys.executable, "-O", "-W", "error", "-B", str(package / "verify.py")],
            env=environment,
            capture_output=True,
            text=True,
            timeout=90,
            check=False,
        )
        self.assertEqual(bad.returncode, 2)
        self.assertIn("committed receipt differs", bad.stderr)
        result_path.write_bytes(original)
        paths = list(exported.rglob("*"))
        self.assertLessEqual(len(paths), 64)
        for path in paths:
            path.chmod(0o555 if path.is_dir() else 0o444)
        exported.chmod(0o555)
        try:
            good = subprocess.run(
                [sys.executable, "-O", "-W", "error", "-B", str(package / "verify.py")],
                env=environment,
                capture_output=True,
                text=True,
                timeout=90,
                check=False,
            )
        finally:
            exported.chmod(0o755)
            for path in paths:
                if path.is_dir():
                    path.chmod(0o755)

        self.assertEqual(good.returncode, 0, good.stderr)
        self.assertIn("PASS_P112_MIXED_RANK_REDUCTION", good.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
