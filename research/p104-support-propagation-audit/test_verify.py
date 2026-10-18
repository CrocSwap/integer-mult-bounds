#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Behavioral controls for the scoped PR3182 audit (standard library only)."""
import copy
import importlib.util
from itertools import product
from pathlib import Path
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("p104_support_audit", HERE / "verify.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class SupportAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        audit.authenticate()
        cls.old = audit.load_predecessor()
        (cls.word, cls.paths, cls.frames, cls.matrix, cls.required,
         cls.direct, cls.pairings) = audit.data(cls.old)
        cls.pairing = cls.pairings["PR3019"]
        edges = list(enumerate(cls.pairing))
        layers = cls.old.build_general_interval_layers(cls.frames, edges, cls.paths)
        args = (cls.frames, edges, layers, cls.paths, cls.direct)
        cls.legacy = cls.old.propagate_with_subspace_memory_bitmap(*args, full_memory=True)
        cls.fixed = audit.memory_variant(cls.old, write_all=True)(*args, full_memory=True)

    def witness(self, **overrides):
        kwargs = dict(old=self.old, word=self.word, frames=self.frames,
                      matrix=self.matrix, pairing=self.pairing,
                      legacy=self.legacy, write_all=self.fixed)
        kwargs.update(overrides)
        return audit.direct_path_witness(**kwargs)

    def test_tiny_arbitrary_dirty_and_order_controls(self):
        result = audit.tiny_checks(self.old)
        self.assertEqual(result["memory_legacy_reverse_all_reverse"]["True"], [1, 2, 3, 3])

    def test_literal_source_timing_and_flag(self):
        result = self.witness()
        self.assertEqual((result["read_cut"], result["write_cut"]), (594, 4058))
        self.assertEqual(len(result["flag_bases"]), 10)

    def test_unavailable_source_cut_rejected(self):
        changed = copy.deepcopy(self.word)
        # The event immediately before cut 594 establishes the read frame.
        self.assertEqual(changed["program"][593][:2], ["transport", "X1"])
        changed["program"][593][3] = list(changed["program"][593][2])
        with self.assertRaisesRegex(ValueError, "source available"):
            self.witness(word=changed)

    def test_wrong_pairing_and_coefficient_rejected(self):
        pairing = list(self.pairing)
        pairing[201] = 196
        with self.assertRaisesRegex(ValueError, "arrival slot"):
            self.witness(pairing=pairing)
        matrix = copy.deepcopy(self.matrix)
        matrix[98][1] *= -1
        with self.assertRaisesRegex(ValueError, "required coefficient"):
            self.witness(matrix=matrix)

    def test_wrong_output_semantics_rejected(self):
        with self.assertRaisesRegex(ValueError, "literal dependency"):
            self.witness(write_all=self.legacy)
        with self.assertRaisesRegex(ValueError, "literal dependency"):
            self.witness(legacy=self.fixed)

    def test_reversed_cycle_has_incompatible_endpoints(self):
        result = audit.cycle_direction_audit(self.old, self.frames, self.pairings["PR3013"])
        self.assertEqual(result["incompatible_pairs"], [[39, 186], [139, 23], [154, 7]])
        with self.assertRaisesRegex(ValueError, "compatible pairing"):
            self.old.check_pairing(self.pairings["PR3182_B_as_encoded"], self.frames[-1])

    def test_source_drift_rejected(self):
        original = Path.read_bytes
        target = audit.ROOT / audit.PREDECESSOR / "verify.py"

        def altered(path):
            payload = original(path)
            return payload + b"\n" if path == target else payload

        with patch.object(Path, "read_bytes", altered):
            with self.assertRaisesRegex(ValueError, "source changed"):
                audit.authenticate()

    def test_two_layer_fixed_frame_census(self):
        # Every two-helper equal-frame partition, two-source read mask and
        # one-target write subset, in two dimensions: 128^2 = 16,384 cases.
        choices = []
        for adjacency, r0, r1, writers in product(((1, 2), (3, 3)), range(4), range(4), range(4)):
            choices.append((list(adjacency), [r0, r1], [writers & 1, (writers >> 1) & 1]))

        def oracle(layers):
            mask = 0
            for source in range(2):
                reached = set()
                pending = [(d, h) for d, layer in enumerate(layers)
                           for h in range(2) if layer[1][h] >> source & 1]
                while pending:
                    d, h = pending.pop()
                    if (d, h) in reached:
                        continue
                    reached.add((d, h))
                    if layers[d][2][h]:
                        mask |= 1 << source
                    pending += [(d, j) for j in range(2) if layers[d][0][h] >> j & 1]
                    if d == 0:
                        pending.append((1, h))
            return mask

        checked = 0
        for layers in product(choices, repeat=2):
            actual = audit.one_hop_read_first(layers, [0] * 104)
            self.assertEqual(actual[0], oracle(layers))
            self.assertEqual(actual[1:], [0] * 103)
            checked += 1
        self.assertEqual(checked, 16384)


if __name__ == "__main__":
    unittest.main()
