#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Direct address-column and boundary controls for the mixed-width lemma."""
from fractions import Fraction as Q
import gzip
import importlib.util
import itertools
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("mixed_geometry", HERE / "verify.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


def explicit_d(support, q, head, tail):
    """Separate 128-coordinate rational action, not a bit-mask swap oracle.

K_q acts in the original eight-coordinate basis, generally not diagonally.
"""
    difference = [a - b for a, b in zip(head, tail)]
    projected = [Q(0) for _ in range(64)]
    if support & 254:
        if support & 255 != 254:
            raise ValueError("completion not specified")
        component = sum(Q(x) * y for x, y in zip(q, difference[:8])) / 4
        projected[:8] = [difference[i] - q[i] * component for i in range(8)]
    for i in range(8, 64):
        if (support >> i) & 1:
            projected[i] = difference[i]
    return ([a - b for a, b in zip(head, projected)],
            [a + b for a, b in zip(tail, projected)])


class GeometryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        v.pins()
        cls.source = v.predecessor()
        cls.children = v.source_children(cls.source)
        word = json.loads(gzip.decompress((v.ROOT / v.BIT / "tune/bitE8mut-p111-tuned.json.gz").read_bytes()))
        cls.lines = word["lines"]
        cls.fixtures = {}
        for k in (1, 2, 74):
            _, _, plan, _ = cls.source.wopt.solve(k, Q(1, 570), True)
            slots = []
            cls.source.build(k, plan, slots)
            cls.fixtures[k] = slots

    def test_arbitrary_head_tail_columns(self):
        checked = 0
        for k, slots in self.fixtures.items():
            for child in (0, 2, 7):
                c = self.children[child]
                factors = []
                used = set()
                for i, cp, off, width, _, _ in slots:
                    if (i, cp) == (child, 0):
                        axes = set(c["axes"][off:off + width])
                        factors.append(sum(2**j for j in axes))
                        used.update(axes)
                factors.append(sum(2**j for j in set(c["axes"]) - used))
                whole = sum(2**j for j in c["axes"])
                for q in (self.lines[0], self.lines[55], self.lines[110]):
                    for column in range(128):
                        vector = [Q(int(i == column)) for i in range(128)]
                        head, tail = vector[:64], vector[64:]
                        expected = explicit_d(whole, q, head, tail)
                        for factor in factors:
                            head, tail = explicit_d(factor, q, head, tail)
                        self.assertEqual((head, tail), expected, (k, child, column))
                        checked += 1
        self.assertEqual(checked, 3456)

    def test_prefix_boundary_for_every_small_word(self):
        # Independent finite illustration of the general written prefix lemma.
        checked = 0
        for capacity in (7, 14, 28, 42):
            for length in range(7):
                for widths in itertools.product((7, 8), repeat=length):
                    if sum(widths) > capacity:
                        continue
                    cursor, factors = 1, []
                    for width in widths:
                        factors.append(sum(2**i for i in range(cursor, cursor + width)))
                        cursor += width
                    factors.append(sum(2**i for i in range(cursor, 1 + capacity)))
                    v.partition(sum(2**i for i in range(1, 1 + capacity)), factors)
                    checked += 1
        self.assertEqual(checked, 86)
        # The first slice is the relevant threshold; a later width-six slice is fine.
        whole = sum(2**i for i in range(1, 15))
        v.partition(whole, [v.mask(range(1, 8)), v.mask(range(8, 14)), v.mask([14])])
        with self.assertRaisesRegex(v.Reject, "split local"):
            v.partition(whole, [v.mask(range(1, 7)), v.mask(range(7, 15))])

    def test_same_ranks_different_address_operator(self):
        q = self.lines[0]
        head, tail = [Q(int(i == 8)) for i in range(64)], [Q(0)] * 64
        original = v.mask(range(8, 15))
        changed = (original ^ (1 << 8)) | (1 << 36)
        self.assertEqual(original.bit_count(), changed.bit_count())
        self.assertNotEqual(explicit_d(original, q, head, tail), explicit_d(changed, q, head, tail))

    def test_gap_and_overlap_are_not_prefix_placements(self):
        original = self.fixtures[1]
        # In child2/copy0, two width-eight slots and a width-seven slot leave five axes.
        which = next(i for i, row in enumerate(original) if row[:3] == (2, 0, 16))
        bad = [list(row) for row in original]
        bad[which][2] += 1
        with self.assertRaisesRegex(v.Reject, "contiguous prefix"):
            v.audit(1, bad, self.children)
        bad[which][2] -= 2
        with self.assertRaisesRegex(v.Reject, "contiguous prefix"):
            v.audit(1, bad, self.children)

    def test_basis_change_preserves_whole_but_not_split(self):
        q = self.lines[55]
        columns = v.completion(q)
        changed = columns[:]
        changed[6], changed[7] = changed[7], changed[6]
        self.assertEqual(v.projector(columns[1:]), v.projector(changed[1:]))
        self.assertNotEqual(v.projector(columns[1:7]), v.projector(changed[1:7]))

    def test_source_level_and_typed_role_rejections(self):
        bad = [list(row) for row in self.fixtures[1]]
        bad[0][1] = True
        with self.assertRaisesRegex(v.Reject, "typed slot"):
            v.audit(1, bad, self.children)
        with self.assertRaisesRegex(v.Reject, "axis domain"):
            v.mask([1, 1])


if __name__ == "__main__":
    unittest.main()
