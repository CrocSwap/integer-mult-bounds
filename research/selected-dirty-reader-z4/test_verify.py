#!/usr/bin/env python3
"""Meaningful controls for the selected-reader boundary and exact obstruction."""
import copy
import importlib.util
from pathlib import Path
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location("reader_audit", Path(__file__).with_name("verify.py"))
v = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(v)


class Controls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = v.load()
        cls.gates, _ = v.typed_segment(cls.data)
        cls.A = v.reader(cls.gates)
        full = cls.data["LOCAL-PROGRAMS.json.gz"]["forward"]
        cls.segment = full[full.index(["phase", "entry_adapters"]):full.index(["phase", "centers"])]

    def test_live_source_byte_drift(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = root / v.ARCHIVE
            path.parent.mkdir(parents=True)
            path.write_bytes((v.ROOT / v.ARCHIVE).read_bytes() + b"drift")
            with self.assertRaisesRegex(ValueError, "live source hash"):
                v.load(root)

    def test_frame_mismatch_and_missing_helper_entry(self):
        events = copy.deepcopy(self.segment)
        gate = next(e for e in events if e[0] == "scalar")
        gate[2] = -1
        with self.assertRaisesRegex(ValueError, "scalar target frame"):
            v.typed_segment(self.data, events)
        events = [e for e in self.segment if not (e[0] in ("adapter", "residual_adapter") and e[2] == 224)]
        with self.assertRaisesRegex(ValueError, "complete entry inventory"):
            v.typed_segment(self.data, events)

    def test_wrong_climb_and_residual_wrapper(self):
        events = copy.deepcopy(self.segment)
        next(e for e in events if e[0] == "climb")[3] = -1
        with self.assertRaisesRegex(ValueError, "climb source frame"):
            v.typed_segment(self.data, events)
        events = copy.deepcopy(self.segment)
        e = next(e for e in events if e[0] == "residual_adapter")
        e[0], e[1] = "adapter", "old_to_new"
        with self.assertRaisesRegex(ValueError, "actual entry wrapper kind"):
            v.typed_segment(self.data, events)

    def test_nonbijective_native_monomial(self):
        recipe = copy.deepcopy(self.data["CLIFFORD-RECIPES.json"]["children"][0]["left"])
        recipe["matrix_rows"][0] = 0
        with self.assertRaisesRegex(ValueError, "invertible monomial"):
            v.monomial(recipe)

    def test_data_only_positive_is_insufficient(self):
        R = [row[:112] for row in self.A]
        self.assertEqual(v.gram(R), [[v.F(56 if i == j else 0) for j in range(8)] for i in range(8)])
        with self.assertRaisesRegex(ValueError, "paired cycle survives"):
            v.rejects_every_paired_cycle([56]*8)
        self.assertEqual(len(v.rejects_every_paired_cycle(v.NORMS)), 1260)

    def test_drop_negative_signs_breaks_data_intertwiner(self):
        columns = list(zip(*(row[:112] for row in self.A)))
        index = {c: j for j, c in enumerate(columns)}
        P = []
        for c in columns:
            target = tuple(c[i] for i in v.Q_ROWS)
            sign = 1 if target in index else -1
            P.append((index[tuple(sign*x for x in target)], sign))
        v.check_signed_intertwiner(columns, P)
        with self.assertRaisesRegex(ValueError, "RP equals QR"):
            v.check_signed_intertwiner(columns, [(j, 1) for j, _ in P])

    def test_actual_helper_witness_and_paid_escape(self):
        h = [r[224] for r in self.A]
        self.assertEqual(h, [0, 2, 2, 0, 0, 0, 0, 0])
        qh = tuple(h[i] for i in v.Q_ROWS)
        self.assertNotIn(qh, set(zip(*self.A)))
        self.assertNotIn(tuple(-x for x in qh), set(zip(*self.A)))
        R = [row[:112] for row in self.A]
        delta = [sum(R[k][j]*(qh[k]-h[k])/56 for k in range(8)) for j in range(112)]
        self.assertEqual(1 + sum(x*x for x in delta), v.F(8, 7))


if __name__ == "__main__":
    unittest.main(verbosity=2)
