#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Mathematical failure controls; also run under isolated optimized Python."""
from dataclasses import replace
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("star_floor_verifier", HERE / "verify.py")
v = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = v
spec.loader.exec_module(v)
independent_spec = importlib.util.spec_from_file_location("star_independent", HERE / "independent_check.py")
independent = importlib.util.module_from_spec(independent_spec)
independent_spec.loader.exec_module(independent)


class FailureControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.g = v.geometry()
        cls.supports, cls.misses = v.supports_and_misses(cls.g)
        cls.cheap = next((i, j) for i in range(240) for j in range(240)
                         if v.pairing_rank(cls.g, cls.supports[i][2], cls.supports[j][2]) == 7)

    def test_missing_frame(self):
        with self.assertRaisesRegex(ValueError, "frame count"):
            v.validate_frames(self.g.gram, self.g.live, self.g.frames[:-1])

    def test_duplicate_frame(self):
        with self.assertRaisesRegex(ValueError, "duplicate frame"):
            v.validate_frames(self.g.gram, self.g.live, self.g.frames[:-1] + self.g.frames[:1])

    def test_nonorthogonal_frame(self):
        frames = list(self.g.frames)
        frame = frames[0]
        bad = next(i for i in range(112) if i not in frame and
                   self.g.gram[self.g.live[frame[0]]][self.g.live[i]] != 0)
        frames[0] = tuple(sorted(frame[:-1] + (bad,)))
        with self.assertRaisesRegex(ValueError, "nonorthogonal frame"):
            v.validate_frames(self.g.gram, self.g.live, tuple(frames))

    def test_missing_trimmed_star_obstruction(self):
        misses = list(self.misses)
        i = next(i for i, mask in enumerate(misses) if mask)
        misses[i] = 0
        with self.assertRaisesRegex(ValueError, "star missed-frame formula"):
            v.validate_star_misses(self.g, self.supports, misses)

    def test_false_universal_rank_seven_atom(self):
        s = self.supports[2 * self.g.removed[0]]
        self.assertEqual(v.pairing_rank(self.g, s[2], s[2]), 8)
        with self.assertRaisesRegex(ValueError, "no live trimmed normal"):
            v.validate_cheap_atom(self.g, s, s, 0)

    def test_cheap_atom_missing_required_frame(self):
        i, j = self.cheap
        with self.assertRaisesRegex(ValueError, "omits a required missed frame"):
            v.validate_cheap_atom(self.g, self.supports[i], self.supports[j], 0)

    def test_broken_pair_completion(self):
        damaged = replace(self.g, incidence=(0,) + self.g.incidence[1:])
        with self.assertRaisesRegex(ValueError, "compatibility graph/Gram disagreement"):
            v.compatibility_graph(damaged)

    def test_nine_clique_is_found(self):
        graph = tuple(((1 << 9) - 1) ^ (1 << i) for i in range(9))
        witness, _ = v.find_clique(graph, 9)
        self.assertEqual(witness, tuple(range(9)))

    def test_target_clique_boundary(self):
        graph = tuple(((1 << 8) - 1) ^ (1 << i) for i in range(8))
        self.assertIsNone(v.find_clique(graph, 9)[0])
        self.assertEqual(v.find_clique(graph, 8)[0], tuple(range(8)))

    def test_coordinate_sharpness(self):
        self.assertEqual(v.verify_coordinate_decomposition(self.g, v.coordinate_vectors(self.g)), [8] * 8)

    def test_missing_coordinate_term(self):
        with self.assertRaisesRegex(ValueError, "coordinate decoder identity"):
            v.verify_coordinate_decomposition(self.g, v.coordinate_vectors(self.g)[:-1])

    def test_even_pair_cannot_be_zero_price_repair(self):
        i, j = self.g.frames[0][:2]
        self.assertEqual(v.pairing_rank(self.g, 1 << i, 1 << j), 1)
        odd_j = next(k for k in range(112) if abs(self.g.gram[self.g.live[i]][self.g.live[k]]) == 1)
        self.assertEqual(v.pairing_rank(self.g, 1 << i, 1 << odd_j), 0)

    def test_corrupted_certificate(self):
        expected = json.loads((HERE / "CERTIFICATE.json").read_text())
        damaged = json.loads(json.dumps(expected))
        damaged["invoice"]["sharp_copy_cost"] = 63
        with self.assertRaisesRegex(ValueError, "certificate mismatch"):
            v.check_receipt(expected, damaged)

    def test_maximal_clique_closure_deduplicates(self):
        self.assertEqual(independent.clique_counts_from_maximal([(0, 1, 2), (1, 2, 3)]),
                         {"0": 1, "1": 4, "2": 5, "3": 2})

    def test_reference_semantics_corruption(self):
        reference = independent.read_reference(HERE)
        damaged = json.loads(json.dumps(reference["atoms"]))
        damaged["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "PR1236 semantic mismatch: atoms"):
            independent.compare_reference(reference, {"atoms": damaged})

    def test_reference_bytes_corruption(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            (target / "reference").mkdir()
            shutil.copyfile(HERE / "SOURCES.json", target / "SOURCES.json")
            (target / "reference/PR1236-CERTIFICATE.json").write_bytes(
                (HERE / "reference/PR1236-CERTIFICATE.json").read_bytes() + b" ")
            with self.assertRaisesRegex(ValueError, "PR1236 receipt source pin"):
                independent.read_reference(target)

    def test_missing_reference_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(FileNotFoundError):
                independent.read_reference(Path(directory))


if __name__ == "__main__":
    unittest.main()
