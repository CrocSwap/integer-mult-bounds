#!/usr/bin/env python3
"""Observable endpoint, arithmetic, source-binding and fault controls."""

import copy
import itertools
import json
import shutil
import tempfile
import types
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
V = types.ModuleType("helper_certificate")
V.__file__ = str(HERE / "verify.py")
exec(compile((HERE / "verify.py").read_bytes(), V.__file__, "exec"), V.__dict__)
W = types.ModuleType("helper_fixed_grid")
W.__file__ = str(HERE / "independent.py")
exec(compile((HERE / "independent.py").read_bytes(), W.__file__, "exec"), W.__dict__)


class EndpointTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = V.authenticated_source()
        cls.data = cls.source.load()

    def test_nonconstant_and_constant_are_different_contracts(self):
        native = self.source.N
        delta = native.vector([1] + [0] * 511)
        endpoint = V.execute(self.source, self.data, delta)
        self.assertNotEqual(endpoint, delta)
        self.assertEqual(endpoint, W.walsh_expected([1] + [0] * 511))
        self.assertEqual(V.execute(self.source, self.data, native.ONE), native.ONE)
        self.assertEqual(V.product(native, endpoint, -1), delta)

    def test_literal_scalar_fault_rejects(self):
        events = copy.deepcopy(self.data[0])
        site = 19241
        self.assertEqual(
            events[site], ["scalar", ["add", ["L", 7], ["L", 224], -1, 1], 1]
        )
        events[site][1][3] *= 2
        changed = (events, *self.data[1:])
        native = self.source.N
        delta = native.vector([1] + [0] * 511)
        try:
            result = V.execute(self.source, changed, delta)
        except ValueError as error:
            self.assertIn("leakage", str(error))
        else:
            self.assertNotEqual(result, V.product(native, delta))

    def test_wrong_direction_and_missing_axis_fail(self):
        native = self.source.N
        delta = native.vector([1] + [0] * 511)
        endpoint = V.execute(self.source, self.data, delta)
        self.assertNotEqual(endpoint, V.product(native, delta, -1))
        partial = delta
        for j in range(8):
            partial = native.line(partial, 1 << j)
        self.assertNotEqual(endpoint, partial)

    def test_every_walsh_eigenvector_and_fixed_space(self):
        counts = [0] * 4
        for label in range(512):
            row = [1 if (label & x).bit_count() % 2 == 0 else -1 for x in range(512)]
            got = W.walsh_expected(row)
            phase = label.bit_count() % 4
            expected_rows = (
                (row, [0] * 512),
                ([0] * 512, row),
                ([-x for x in row], [0] * 512),
                ([0] * 512, [-x for x in row]),
            )[phase]
            self.assertEqual(got, (tuple(expected_rows[0]), tuple(expected_rows[1]), 0))
            counts[phase] += 1
        self.assertEqual(counts, [136, 136, 120, 120])

    def test_packed_injectivity_and_small_radix_collision(self):
        values = {
            sum(c * 8**j for j, c in enumerate(coefficients))
            for coefficients in itertools.product(range(-2, 3), repeat=3)
        }
        self.assertEqual(len(values), 125)
        too_small = {
            sum(c * 2**j for j, c in enumerate(coefficients))
            for coefficients in itertools.product(range(-2, 3), repeat=3)
        }
        self.assertLess(len(too_small), len(values))
        peak, guard, bits = V.coefficient_bound(self.source, self.data)
        self.assertLess((peak + 1) * 2**guard, 2 ** (bits - 2))
        self.assertEqual((guard, bits), (66, 106))

    def test_fixed_grid_rejects_inexact_division(self):
        engine = W.FixedGrid([1] + [0] * 511, 0)
        with self.assertRaisesRegex(ValueError, "scalar division"):
            engine.scalar(engine.entry, 1, 2, "control")
        with self.assertRaisesRegex(ValueError, "line division"):
            engine.line(engine.entry, 1)

    def test_each_live_source_corruption_rejects_before_execution(self):
        original_root = V.ROOT
        with tempfile.TemporaryDirectory(prefix="qq16-helper-source-") as temporary:
            root = Path(temporary)
            for name in V.INPUTS:
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(original_root / name, target)
            V.ROOT = root
            try:
                for name in sorted(V.INPUTS):
                    target = root / name
                    target.write_bytes(b"corrupt source control\n")
                    with self.assertRaisesRegex(ValueError, "Source hash: " + name):
                        V.authenticated_source()
                    shutil.copyfile(original_root / name, target)
            finally:
                V.ROOT = original_root

    def test_reclassified_live_source_rejects(self):
        original_here = V.HERE
        sources = json.loads((HERE / "SOURCES.json").read_text())
        row = next(pin for pin in sources["files"] if pin["usage"] == "input")
        row["usage"] = "provenance"
        with tempfile.TemporaryDirectory(prefix="qq16-helper-inventory-") as temporary:
            V.HERE = Path(temporary)
            try:
                (V.HERE / "SOURCES.json").write_text(json.dumps(sources))
                with self.assertRaisesRegex(
                    ValueError, "Complete live source inventory"
                ):
                    V.authenticated_source()
            finally:
                V.HERE = original_here


if __name__ == "__main__":
    unittest.main(verbosity=2)
