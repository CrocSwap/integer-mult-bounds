"""Independent finite checks, without a solver or third-party dependency."""
import copy
from collections import Counter
from fractions import Fraction as Q
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import circuit
import verify


class CircuitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pins, cls.sources = verify.load_sources()
        cls.word = cls.sources['word']
        cls.recipe = json.loads((HERE / 'CERTIFICATE.json').read_text())['search']
        cls.gates = circuit.construct(cls.word, cls.recipe)

    def test_independent_exhaustive_price_census(self):
        # Build sparse columns directly from the source. Price with explicit
        # subtraction/division of integer coefficients, not circuit.price.
        columns = [dict() for _ in range(492)]
        for _, target, source, n, d, _ in self.word['compensation']:
            columns[source - 224][target] = n * (4 // d)

        def real_cost(n):
            if n == 0:
                return 0
            n, denominator = abs(n), 4
            while denominator > 1 and n % 2 == 0:
                n //= 2
                denominator //= 2
            steps = 3
            while n:
                steps += n % 2
                n //= 2
                if n:
                    steps += 1
            while denominator > 1:
                steps += 1
                denominator //= 2
            return 2 * steps

        eligible = [i for i in range(492) if self.word['start'][i + 224] == 0
                    and self.word['final'][i + 224] == 1]
        positive, count = [], 0
        for a in eligible:
            for b in eligible:
                if a == b:
                    continue
                # Joint coefficient histogram independently aggregates targets.
                histogram = Counter((columns[a].get(t, 0), columns[b].get(t, 0))
                                    for t in columns[a].keys() | columns[b].keys())
                for sign in (-1, 1):
                    saving = sum(m * (real_cost(y) - real_cost(y - sign * x))
                                 for (x, y), m in histogram.items()) - 16
                    count += 1
                    if saving > 0:
                        positive.append([saving, a, b, sign])
        positive.sort(key=lambda x: (-x[0], (x[1] - 24) % 492, (x[2] - 24) % 492, x[3]))
        raw = json.dumps(positive, sort_keys=True, separators=(',', ':')).encode()
        self.assertEqual(count, self.recipe['candidates'])
        self.assertEqual(len(positive), self.recipe['profitable'])
        self.assertEqual(hashlib.sha256(raw).hexdigest(), self.recipe['profitable_sha256'])
        used, selected = set(), []
        for p in positive:
            if not used.intersection(p[1:3]):
                used.update(p[1:3])
                selected.append(p)
        self.assertEqual(selected, self.recipe['pairs'])

    def test_all_pair_maps_by_independent_dense_columns(self):
        # Three coordinates [h_a,h_b,y_t], with independent input columns.
        coeff = {(e[1], e[2]): Q(e[3], e[4]) for e in self.word['compensation']}
        for _, a, b, s in self.recipe['pairs']:
            for t in range(112, 224):
                ca, cb = coeff.get((t, a + 224), Q(0)), coeff.get((t, b + 224), Q(0))
                ops = [(0, 1, Q(s)), (2, 0, ca), (2, 1, cb - s * ca), (0, 1, Q(-s))]
                for backward in (False, True):
                    matrix = [[Q(int(i == j)) for j in range(3)] for i in range(3)]
                    for target, source, q in ops:
                        if backward:
                            target, source, q = source, target, -q
                        matrix[target] = [x + q * y for x, y in zip(matrix[target], matrix[source])]
                    expected = ([[1, 0, -ca], [0, 1, -cb], [0, 0, 1]] if backward
                                else [[1, 0, 0], [0, 1, 0], [ca, cb, 1]])
                    self.assertEqual(matrix, expected)

    def test_duplicate_pair_is_rejected(self):
        recipe = copy.deepcopy(self.recipe)
        recipe['pairs'].append(recipe['pairs'][0])
        with self.assertRaisesRegex(ValueError, 'non-disjoint'):
            circuit.construct(self.word, recipe)

    def test_nonzero_frame_helper_is_rejected(self):
        word = copy.deepcopy(self.word)
        word['start'][224 + self.recipe['pairs'][0][1]] = 1
        with self.assertRaisesRegex(ValueError, 'nonzero-frame'):
            circuit.construct(word, self.recipe)

    def test_cold_wrapped_helper_is_rejected(self):
        word = copy.deepcopy(self.word)
        r = 224 + self.recipe['pairs'][0][1]
        word['final'][r] = 0
        with self.assertRaisesRegex(ValueError, 'wrapped'):
            circuit.construct(word, self.recipe)

    def test_favorable_cost_corruption_is_rejected(self):
        recipe = copy.deepcopy(self.recipe)
        recipe['pairs'][0][0] += 2
        with self.assertRaisesRegex(ValueError, 'pair price'):
            circuit.construct(self.word, recipe)

    def test_wrong_dual_sign_fails(self):
        reference = circuit.block_replay(circuit.dual(self.word['compensation']))[0][:716]
        mutant = circuit.dual(self.gates)
        mutant[0][3] *= -1
        self.assertNotEqual(circuit.block_replay(mutant)[0][:716], reference)

    def test_dirty_private_work_is_cleared(self):
        result, price = circuit.block_replay([circuit.gate(112, 224, Q(-3, 4))], primitives=True)
        self.assertEqual(result[112], {112: 1, 224: Q(-3, 4)})
        self.assertEqual(result[224], {224: 1})
        self.assertEqual(result[716], {})
        self.assertEqual(price, 16)

    def test_source_mutation_rejected_before_use(self):
        with tempfile.TemporaryDirectory(prefix='ck-pins-') as directory:
            root = Path(directory)
            record = self.pins['files']['word']
            dest = root / record['path']
            dest.parent.mkdir(parents=True)
            import gzip
            dest.write_bytes(gzip.compress(b'{}'))
            with patch.object(verify, 'ROOT', root):
                with self.assertRaisesRegex(ValueError, 'source hash: word'):
                    verify.load_sources()

    def test_gzip_container_change_is_accepted(self):
        import gzip
        with tempfile.TemporaryDirectory(prefix='ck-repack-') as directory:
            root = Path(directory)
            for record in self.pins['files'].values():
                source = verify.ROOT / record['path']
                dest = root / record['path']
                dest.parent.mkdir(parents=True, exist_ok=True)
                raw = source.read_bytes()
                if source.suffix == '.gz':
                    raw = gzip.compress(gzip.decompress(raw), compresslevel=1, mtime=42)
                dest.write_bytes(raw)
            with patch.object(verify, 'ROOT', root):
                _, sources = verify.load_sources()
            self.assertEqual(sources['word'], self.word)

    def test_semantic_controls_reject(self):
        self.assertEqual(len(verify.controls(self.word, self.gates)), 6)


if __name__ == '__main__':
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(CircuitTests))
    if os.environ.get('TEST_SKIP_LOG'):
        Path(os.environ['TEST_SKIP_LOG']).write_text(''.join(
            f'{test}: {reason}\n' for test, reason in result.skipped))
    sys.exit(not result.wasSuccessful())
