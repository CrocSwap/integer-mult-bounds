"""Focused controls for production DisjointTensor.frame_data union propagation."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from experiments.disjoint_tensor import DisjointTensor  # noqa: E402


def load_baseline():
    path = ROOT / "research/disjoint-tensor-frame-unions/baseline.py"
    spec = importlib.util.spec_from_file_location("dt_frame_baseline", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class DisjointTensorFrameUnions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline = load_baseline()

    def test_frame_maps_and_receipts_match_baseline(self):
        for h in (8, 10, 12, 16):
            circuit = DisjointTensor(h)
            self.assertEqual(
                self.baseline.DisjointTensor.frame_data(circuit),
                circuit.frame_data(),
            )
            self.assertEqual(
                self.baseline.DisjointTensor.verify_frames(circuit),
                circuit.verify_frames(),
            )

    def test_h26_receipt_fields(self):
        frames = DisjointTensor(26).verify_frames()
        self.assertTrue(frames["all_physical_transitions_checked"])
        self.assertEqual(frames["distinct_nontrivial_transitions"], 195345)
        self.assertEqual(
            frames["frame_types"],
            {"line": 27430, "coordinate": 65884, "complement": 27430},
        )

    def test_corrupted_rectangle_rejected(self):
        circuit = DisjointTensor(10)
        leaf = min(n for n in circuit.active if circuit.args[n] is None)
        circuit.inputs[leaf - 1] = (1 << circuit.h) - 1
        with self.assertRaises(ValueError):
            circuit.frame_data()


if __name__ == "__main__":
    unittest.main()
