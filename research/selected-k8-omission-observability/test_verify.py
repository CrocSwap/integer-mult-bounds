#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Small exhaustive matrix oracles for the rank-one omission classifier."""
from collections import Counter
from fractions import Fraction as F
from itertools import product
import json
from pathlib import Path
import tempfile
import unittest
import importlib.util

SPEC = importlib.util.spec_from_file_location('observability', Path(__file__).with_name('verify.py'))
v = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(v)


def brute_counts(program, n, width, dual):
    baseline = [v.scalar_replay(program, n, j, dual) for j in range(n)]
    counts = Counter()
    targets = set(range(0, width) if dual else range(width, 2 * width))
    sources = set(range(width, 2 * width) if dual else range(width))
    data = set(range(2 * width))
    for index, gate in enumerate(program):
        changed = set()
        for column in range(n):
            actual = v.scalar_replay(program, n, column, dual, index)
            changed.update((row, column) for row in range(n) if actual[row] != baseline[column][row])
        counts.update(('events', 'scale' if gate[3] is None else 'add'))
        if not changed:
            counts['identity_omissions'] += 1
            continue
        counts['nonzero_defects'] += 1
        outputs, inputs = {r for r, _ in changed}, {c for _, c in changed}
        if not outputs & targets:
            counts['target_invisible'] += 1
        if not outputs & data:
            counts['all_data_invisible'] += 1
        if not inputs & data:
            counts['clean_helpers_invisible'] += 1
        if not inputs & sources:
            counts['source_only_invisible'] += 1
        if not outputs & data and not inputs & data:
            counts['data_and_clean_helpers_invisible'] += 1
    return dict(sorted(counts.items()))


class ObservabilityTests(unittest.TestCase):
    def test_exhaustive_short_rational_words(self):
        # 125 three-event words, both orientations, all four input/output columns.
        alphabet = [(0, 2, F(1, 2)), (2, 3, F(-2)), (1, 0, F(3, 4)),
                    (3, None, F(-1, 2)), (2, None, F(1))]
        for letters in product(alphabet, repeat=3):
            program = [('fixture', i, *gate) for i, gate in enumerate(letters)]
            for dual in (False, True):
                with self.subTest(letters=letters, dual=dual):
                    actual = v.census(program, 4, 1, dual, check_endpoint=False)
                    self.assertEqual(actual['counts'], brute_counts(program, 4, 1, dual))

    def test_cancellation_is_exact_not_support_union(self):
        program = [('fixture', 0, 2, 0, F(1)), ('fixture', 1, 2, 0, F(-1)),
                   ('cleanup', 2, 3, 2, F(1))]
        result = v.census(program, 4, 1, check_endpoint=False)
        example = result['examples']['cleanup_data_and_clean_helpers_invisible']
        self.assertEqual(example['input_column'], 2)
        self.assertEqual(example['input_support'], 1)
        self.assertEqual(example['delta'], [[3, '-1']])

    def test_dual_uses_inverse_scale_and_swapped_add(self):
        scale = ('fixture', 0, 3, None, F(-2))
        add = ('fixture', 1, 1, 2, F(3, 4))
        self.assertEqual(v.oriented(scale, True)[2:], (3, None, F(-1, 2)))
        self.assertEqual(v.oriented(add, True)[2:], (2, 1, F(-3, 4)))
        self.assertEqual(v.oriented(v.oriented(add, True), True), add)

    def test_wrong_complete_endpoint_rejects(self):
        with self.assertRaisesRegex(ValueError, 'complete scalar endpoint'):
            v.census([('fixture', 0, 2, 3, F(1))], 4, 1)

    def test_source_drift_rejects_before_computation(self):
        sources = json.loads((v.HERE / 'SOURCES.json').read_bytes())
        source = next(item for item in sources['files'] if item['usage'] == 'input')
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = root / source['path']
            path.parent.mkdir(parents=True)
            path.write_bytes((v.ROOT / source['path']).read_bytes() + b'\n')
            with self.assertRaisesRegex(ValueError, 'source pin:'):
                v.load_word(root)

    def test_malformed_source_gate_rejects(self):
        for gate in (['add', 1, 1, 1, 1, []], ['scale', 1, 0, 1, []], ['unknown']):
            with self.subTest(gate=gate), self.assertRaises(ValueError):
                v.decode(gate, 'fixture', 0)


if __name__ == '__main__':
    unittest.main()
