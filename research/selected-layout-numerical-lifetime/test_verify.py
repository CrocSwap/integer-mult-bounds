"""Defect and boundary controls for the actual frozen Layout entry points."""

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "layout_audit", Path(__file__).with_name("verify.py")
)
v = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(v)


class LayoutControls(unittest.TestCase):
    def setUp(self):
        self.m = v.load()

    def case(self, shape=(2, 1, 3), embedded=True):
        case = v.setup(self.m, *shape, 3, 1, embedded, 3)
        return case, v.check_constructor(case)

    def test_literal_gap_and_zero_exponent_outputs(self):
        for shape, positions, expected, peaks in (
            ((1, 1, 1), (0, 1), [2, 3, 5], [0, 4]),
            ((2, 1, 3), (1, 2), [6, 27, 15], [6, 4]),
        ):
            case, layout = self.case(shape)
            record = v.extents_case(case, layout, *positions)
            self.assertEqual(record["peaks"], peaks)
            case.index.base = None
            a, b = (case.index.literal(x) for x in positions)
            values = layout.extents(a, b)
            self.assertEqual([v.natural_value(x) for x in values], expected)

    def test_constructor_one_word_underbudget(self):
        case = v.setup(self.m, 2, 1, 3, 3, 1, True, 3)
        with self.assertRaisesRegex(ValueError, "numerical allowance"):
            v.check_constructor(case, limit=3)

    def test_unary_and_binary_one_index_underbudget(self):
        for second, limit in ((None, 2), (2, 3)):
            case, layout = self.case()
            with self.assertRaisesRegex(ValueError, "numerical allowance"):
                v.extents_case(case, layout, 0, second, limits=(6, limit))

    def test_residue_one_word_underbudget(self):
        case, layout = self.case()
        with self.assertRaisesRegex(ValueError, "numerical allowance"):
            v.extents_case(case, layout, 0, 2, limits=(5, 4))

    def test_omitted_power_is_detected(self):
        case, layout = self.case()
        self.m.layout.multiply_atom_power = lambda *_args: None
        with self.assertRaisesRegex(ValueError, "exact extent cardinalities"):
            v.extents_case(case, layout, 0, 2)

    def test_unfreed_index_is_detected(self):
        case, layout = self.case((1, 1, 1))
        original = case.index.free_many
        case.index.free_many = lambda *_args: None
        with self.assertRaisesRegex(ValueError, "entry slots"):
            v.extents_case(case, layout, 0, 1, limits=(6, 64))
        case.index.free_many = original

    def test_reversed_atoms_reject_without_rollback_guarantee(self):
        case, layout = self.case()
        case.index.base = None
        first, second = case.index.literal(2), case.index.literal(0)
        baseline = len(case.index.live)
        with self.assertRaisesRegex(ValueError, "ordered physical"):
            layout.extents(first, second)
        # This source rejects after allocating a and b; successful cleanup is
        # not an exception rollback contract.
        self.assertEqual(len(case.index.live) - baseline, 2)

    def test_snapshot_and_source_corruption_reject(self):
        for name in ("SNAPSHOT.json", "vendor/layout.py", "vendor/numeric.py"):
            with tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary) / "package"
                shutil.copytree(
                    v.ROOT, root, ignore=shutil.ignore_patterns("__pycache__")
                )
                target = root / name
                target.write_bytes(target.read_bytes() + b"\n")
                with self.assertRaisesRegex(
                    ValueError, "snapshot identity|source hash"
                ):
                    v.load(root)

    def test_boolean_cannot_replace_integer_in_receipt(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "package"
            shutil.copytree(v.ROOT, root, ignore=shutil.ignore_patterns("__pycache__"))
            receipt = json.loads((root / "RESULT.json").read_text())
            self.assertEqual(receipt["fixtures"][0]["parameters"][0], 1)
            receipt["fixtures"][0]["parameters"][0] = True
            (root / "RESULT.json").write_text(json.dumps(receipt))
            # Fixed interpreter and a verifier copied from this package; no shell.
            result = subprocess.run(  # noqa: S603
                [sys.executable, "-I", "-O", "-Werror", "-B", str(root / "verify.py")],
                capture_output=True,
                text=True,
                check=False,
                timeout=180,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("complete typed receipt", result.stderr)


if __name__ == "__main__":
    unittest.main()
