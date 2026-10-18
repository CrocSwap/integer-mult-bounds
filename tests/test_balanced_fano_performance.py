"""Exact differential and independent dense controls for packed Fano replay."""
from hashlib import sha256
from itertools import product, zip_longest
import json
from pathlib import Path
import random
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'research/balanced-fano-performance'))
from common import canonical, load_baseline, source_pins
from experiments import balanced_fano as packed


def dense_columns(W, pairs, word):
    """Literal binary matrices: no packed-state or transpose helper calls."""
    rows = [[int(i == j) for j in range(W)] for i in range(W)]
    for (a, b), choice in zip(pairs, word):
        old_a, old_b = rows[a], rows[b]
        for target, coefficients in zip((a, b), packed.GL2[choice]):
            rows[target] = [((coefficients % 2)*x + (coefficients // 2)*y) % 2
                            for x, y in zip(old_a, old_b)]
    return tuple(sum(rows[i][j]*2**i for i in range(W)) for j in range(W))


class PackedFanoReplay(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline = load_baseline()

    def test_full_fano_streams_match_each_assignment_in_order(self):
        model = packed.balanced_fano()
        self.assertEqual(model, self.baseline.balanced_fano())
        halves = (model['pairs'][:7], list(reversed(model['pairs'][7:])))
        for pairs in halves:
            count = 0
            for old, new in zip_longest(self.baseline.assignments(10, pairs),
                                       packed._column_assignments(10, pairs)):
                self.assertIsNotNone(old, 'Extra optimized assignment')
                self.assertIsNotNone(new, 'Missing optimized assignment')
                rows, word = old
                self.assertEqual(new, (self.baseline.columns(rows), word))
                count += 1
            self.assertEqual(count, 279936)

    def test_packed_stream_against_independent_dense_actions(self):
        rng = random.Random(91)
        for W in (2, 3, 5, 9, 16, 33, 65):
            pairs = [tuple(rng.sample(range(W), 2)) for _ in range(3)]
            expected_words = product(range(6), repeat=len(pairs))
            count = 0
            for actual, expected_word in zip_longest(packed._column_assignments(W, pairs), expected_words):
                self.assertIsNotNone(actual)
                self.assertIsNotNone(expected_word)
                cols, word = actual
                self.assertEqual(word, expected_word)
                self.assertEqual(cols, dense_columns(W, pairs, word))
                count += 1
            self.assertEqual(count, 216)
        self.assertEqual(list(packed._column_assignments(9, [])),
                         [(tuple(1 << i for i in range(9)), ())])

    def test_complete_results_witnesses_and_early_stops_match(self):
        rng = random.Random(91)
        cases = [(2, [(0, 1)]*4), (3, [(1, 0), (2, 1), (0, 1)]),
                 (4, [(0, 3), (2, 1), (3, 1), (2, 0), (0, 1)]), (9, [])]
        for W in (2, 3, 4, 8, 9, 16, 33, 65):
            for gates in range(1, 6):
                cases.append((W, [tuple(rng.sample(range(W), 2)) for _ in range(gates)]))
        outcomes = set()
        for W, pairs in cases:
            targets = rng.sample(range(W), W)
            prescriptions = ({}, {i: i for i in range(W)},
                             {i: targets[i] for i in range(min(W, 3))})
            for prescribed in prescriptions:
                old = self.baseline.existence(W, pairs, prescribed)
                new = packed.existence(W, pairs, prescribed)
                self.assertEqual(new, old)
                outcomes.add(new['exists'])
                if new['exists']:
                    witness = new['witness']
                    cols = dense_columns(W, pairs, witness['choices'])
                    self.assertEqual(cols, tuple(1 << i for i in witness['rho']))
        self.assertEqual(outcomes, {True, False})

    def test_same_input_failures_and_exact_budget_boundary(self):
        invalid = [((1, []), {}), ((2, [(0, 0)]), {}), ((2, [(0, 2)]), {}),
                   ((2, [(-1, 1)]), {}), ((2, [(0, 1, 1)]), {}),
                   ((2, [(0, 1)], {0: 1, 1: 1}), {}),
                   ((2, [(0, 1)], {2: 1}), {}),
                   ((2, [(0, 1)]*4), {'half_budget': 35}),
                   ((2, []), {'half_budget': 0})]
        for args, kwargs in invalid:
            messages = []
            for module in (self.baseline, packed):
                with self.assertRaises(ValueError) as failure:
                    module.existence(*args, **kwargs)
                messages.append(str(failure.exception))
            self.assertEqual(*messages)
        self.assertEqual(packed.existence(2, [(0, 1)]*4, half_budget=36),
                         self.baseline.existence(2, [(0, 1)]*4, half_budget=36))

    def test_missing_assignment_changes_the_committed_receipt(self):
        # A skipped leaf must be detected even if this closed model still says
        # "no completion"; comparing only the Boolean result is insufficient.
        original = packed._column_assignments
        def omit_last(W, pairs):
            iterator = iter(original(W, pairs))
            pending = next(iterator)
            for item in iterator:
                yield pending
                pending = item
        model = packed.balanced_fano()
        with patch.object(packed, '_column_assignments', omit_last):
            result = packed.existence(model['W'], model['pairs'], model['prescribed'])
        expected = source_pins()['expected_result']
        self.assertFalse(result['exists'])
        self.assertEqual(result['prefix_assignments'], expected['prefix_assignments'] - 1)
        self.assertEqual(result['suffix_assignments'], expected['suffix_assignments'] - 1)
        self.assertNotEqual(result['prefix_sha256'], expected['prefix_sha256'])
        self.assertNotEqual(result['suffix_sha256'], expected['suffix_sha256'])
        self.assertNotEqual(canonical(result), canonical(expected))

    def test_only_historical_source_binding_changes(self):
        pins = source_pins()
        receipt = json.loads((ROOT / 'certificates/stronger-rank-screens.json').read_text())
        self.assertEqual(canonical(receipt['exact_scalar_search']), canonical(pins['expected_result']))
        source = 'scripts/experiments/balanced_fano.py'
        self.assertEqual(receipt['source_sha256'][source], sha256((ROOT / source).read_bytes()).hexdigest())
        receipt['source_sha256'][source] = pins['baseline_sha256']
        original_bytes = (json.dumps(receipt, indent=2, sort_keys=True) + '\n').encode()
        self.assertEqual(sha256(original_bytes).hexdigest(), pins['baseline_certificate_sha256'])


if __name__ == '__main__':
    unittest.main()
