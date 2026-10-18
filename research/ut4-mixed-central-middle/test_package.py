#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Separate dense/truncated-word and literal-address checks of the new census."""
from functools import reduce
from itertools import combinations_with_replacement, product
from operator import xor
import json
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify as V

RAW_WORDS = tuple(''.join(word) for degree in range(4)
                  for word in product('abc', repeat=degree))
RAW_INDEX = {word: i for i, word in enumerate(RAW_WORDS)}
POSITIONS = ((0, 1), (1, 2), (2, 3), (0, 2), (1, 3), (0, 3))


def matrix(g):
    rows = [[int(i == j) for j in range(4)] for i in range(4)]
    for bit, (i, j) in enumerate(POSITIONS):
        rows[i][j] = (g >> bit) & 1
    return rows


def dense_product(a, b):
    return [[sum(x * y for x, y in zip(row, column)) % 2
             for column in zip(*b)] for row in a]


def literal_product(g, h):
    result = dense_product(matrix(g), matrix(h))
    return sum(result[i][j] << bit for bit, (i, j) in enumerate(POSITIONS))


def relation_basis():
    """Full two-sided relation space on forty raw words, not rewrite rules."""
    basis = {}
    for left, right in product(RAW_WORDS, repeat=2):
        if len(left) + len(right) > 1:
            continue
        for a, b in (('aa', None), ('bb', None), ('cc', None), ('ca', 'ac')):
            row = 1 << RAW_INDEX[left + a + right]
            if b:
                row ^= 1 << RAW_INDEX[left + b + right]
            for pivot in range(39, -1, -1):
                if (row >> pivot) & 1:
                    if pivot in basis:
                        row ^= basis[pivot]
                    else:
                        basis[pivot] = row
                        break
    return basis


RELATIONS = relation_basis()


def normal(row):
    for pivot in range(39, -1, -1):
        if ((row >> pivot) & 1) and pivot in RELATIONS:
            row ^= RELATIONS[pivot]
    return row


def dense_quotient(word):
    result = {'': [[1, 0], [0, 1]]}
    for letter, encoded in word:
        n = [[(encoded >> (2 * i + j)) & 1 for j in range(2)] for i in range(2)]
        updated = {name: [row[:] for row in mat] for name, mat in result.items()}
        for name, mat in result.items():
            if len(name) == 3:
                continue
            key = name + letter
            increment = dense_product(mat, n)
            old = updated.get(key, [[0, 0], [0, 0]])
            updated[key] = [[a ^ b for a, b in zip(row, add)]
                            for row, add in zip(old, increment)]
        result = updated
    rows = [[0, 0], [0, 0]]
    for name, mat in result.items():
        for i, j in product(range(2), repeat=2):
            rows[i][j] ^= mat[i][j] << RAW_INDEX[name]
    return [[normal(row) for row in entry] for entry in rows]


def primary_to_dense(image):
    rows = [[0, 0], [0, 0]]
    for name, encoded in image.items():
        for i, j in product(range(2), repeat=2):
            rows[i][j] ^= ((encoded >> (2 * i + j)) & 1) << RAW_INDEX[name]
    return [[normal(row) for row in entry] for entry in rows]


def regular_action(word, role, address):
    """Faithful left-regular action using literal four-by-four address matrices."""
    state = [set() for _ in range(3)]
    state[role].add(address)
    for letter, n in reversed(word):
        x, y = V.SPLIT[n]
        summed = set()
        for source in range(2):
            if (y >> source) & 1:
                summed.symmetric_difference_update(state[source])
        delta = set()
        generator = {'a': 1, 'b': 2, 'c': 4}[letter]
        for h in summed:
            delta.symmetric_difference_update((h, literal_product(generator, h)))
        for target in range(2):
            if (x >> target) & 1:
                state[target].symmetric_difference_update(delta)
    return state


def profiles_of(word):
    p, q = [], []
    a = c = 0
    middle = []
    for letter, n in word:
        if letter == 'a':
            a ^= n
        elif letter == 'c':
            c ^= n
        else:
            middle.append(n)
            p.append(a)
            q.append(c)
    return tuple(middle), tuple(p), tuple(q)


class MixedCentralTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalogue, cls.outer_count = V.gap_catalogue()

    def test_literal_group_law(self):
        for g, h in product(range(64), repeat=2):
            self.assertEqual(V.group_product(g, h), literal_product(g, h))
        self.assertEqual(len(RELATIONS), 23)
        representatives = [normal(1 << RAW_INDEX[s]) for s in V.BASIS]
        self.assertEqual(len(set(representatives)), 17)
        self.assertNotIn(0, representatives)

    def test_every_short_word_against_raw_relation_oracle(self):
        alphabet = tuple(product('abc', V.COUPLINGS))
        checked = 0
        for length in range(4):
            for word in product(alphabet, repeat=length):
                self.assertEqual(primary_to_dense(V.quotient(word)), dense_quotient(word))
                checked += 1
        self.assertEqual(checked, 20440)

    def test_full_witness_and_dirty_basis_columns(self):
        word = tuple(tuple(step) for step in V.positive_and_controls()['full_word'])
        for role, address in product(range(3), range(64)):
            target = [set(), set(), set()]
            target[role].add(literal_product((32, 40, 0)[role], address))
            self.assertEqual(regular_action(word, role, address), target)
        error = (('a', 1),)
        self.assertNotEqual(regular_action(error, 0, 0), [{0}, set(), set()])

    def test_five_column_relaxation_is_not_a_word(self):
        x = [[1, 1, 1, 0, 1], [0, 0, 0, 1, 1]]
        y = [[1, 0], [1, 0], [0, 1], [0, 1], [0, 1]]
        u = [[0, 0, 1, 1, 0], [0, 0, 0, 0, 1]]
        v = [[1, 0], [0, 0], [1, 1], [0, 1], [0, 1]]
        self.assertEqual(dense_product(x, y), [[0, 0], [0, 0]])
        self.assertEqual(dense_product(u, y), [[0, 0], [0, 1]])
        self.assertEqual(dense_product(x, v), [[0, 0], [0, 0]])
        self.assertEqual(dense_product(u, v), [[1, 0], [0, 1]])
        v[0][0] ^= 1
        self.assertNotEqual(dense_product(x, v), [[0, 0], [0, 0]])

    def test_planted_words_survive_complete_reconstruction(self):
        rng = random.Random(20261014)
        middles = [ns for ns in product(V.COUPLINGS, repeat=5) if V.total(ns) == 0]
        outer = [ns for ns in product(V.COUPLINGS, repeat=4) if reduce(xor, ns) == 0]
        positions = tuple(combinations_with_replacement(range(6), 4))
        for _ in range(48):
            middle = rng.choice(middles)
            ra, rc = ((rng.choice(outer), rng.choice(positions)) for _ in range(2))
            # Plant a concrete word without invoking the producer's expansion.
            planted = []
            for gap in range(6):
                pending = [[('a', n) for n, p in zip(*ra) if p == gap],
                           [('c', n) for n, p in zip(*rc) if p == gap]]
                for _ in range(sum(map(len, pending))):
                    which = rng.choice([i for i in range(2) if pending[i]])
                    planted.append(pending[which].pop(0))
                if gap < 5:
                    planted.append(('b', middle[gap]))
            word = tuple(planted)
            _, pa, pc = profiles_of(word)
            self.assertIn(ra, self.catalogue[pa])
            self.assertIn(rc, self.catalogue[pc])
            self.assertIn(word, tuple(V.expanded_words(middle, ra, rc)))
            self.assertEqual(len(word), 13)
            image = V.quotient(word)
            tab = V.side_table(middle)
            packed_a = packed_c = 0
            for j in range(5):
                packed_a ^= tab[j][pa[j]]
                packed_c ^= tab[j][pc[j]]
            for shift, name in enumerate(('ab', 'ba', 'aba', 'bab')):
                self.assertEqual((packed_a >> (4 * shift)) & 15, image.get(name, 0))
            for shift, name in enumerate(('cb', 'bc', 'cbc', 'bcb')):
                self.assertEqual((packed_c >> (4 * shift)) & 15, image.get(name, 0))
            ka, kc = V.profile_key(middle, pa), V.profile_key(middle, pc)
            self.assertEqual(V.cross_key(ka, kc), (image.get('abc', 0), image.get('cba', 0)))
            self.assertEqual(primary_to_dense(image), dense_quotient(word))

    def test_key_join_matches_direct_pairs(self):
        rng = random.Random(314159)
        for _ in range(32):
            a = tuple(tuple(rng.randrange(32) for _ in range(4)) for _ in range(24))
            c = tuple(tuple(rng.randrange(32) for _ in range(4)) for _ in range(24))
            direct = {(ka, kc) for ka, kc in product(a, c) if V.cross_key(ka, kc) == (9, 9)}
            self.assertEqual(set(V.compatible_keys(set(a), set(c))), direct)
        # A positive join fixture ensures an accidentally empty implementation fails.
        ka = (1, 2, 1, 2)
        self.assertEqual(tuple(V.compatible_keys((ka,), (ka,))), ((ka, ka),))

    def test_catalogue_and_illegal_alphabet(self):
        self.assertEqual((len(self.catalogue), self.outer_count), (9721, 441))
        self.assertEqual(sum(len(v) for v in self.catalogue.values()), 441 * 126)
        self.assertEqual(len(V.SPLIT), 9)
        for word in ((('a', 9),), (('z', 1),), (('a', 0),)):
            with self.assertRaises(ValueError):
                V.quotient(word)
        with self.assertRaises(ValueError):
            V.formal((('a', 1),) * 15)

    def test_receipt_rejects_semantic_and_type_drift(self):
        actual = V.positive_and_controls()
        with tempfile.TemporaryDirectory() as temporary:
            receipt = Path(temporary) / 'receipt.json'
            receipt.write_text(json.dumps(actual))
            V.check_receipt(actual, receipt)
            changed = dict(actual)
            changed['formal_basis_columns'] = 191
            receipt.write_text(json.dumps(changed))
            with self.assertRaisesRegex(ValueError, 'receipt mismatch'):
                V.check_receipt(actual, receipt)
            changed = dict(actual)
            changed['wrong_letter_controls'] = True
            receipt.write_text(json.dumps(changed))
            with self.assertRaisesRegex(ValueError, 'receipt mismatch'):
                V.check_receipt(actual, receipt)

    def test_cli_refuses_overwrite_and_drifted_source(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            occupied = root / 'receipt.json'
            occupied.write_text('keep\n')
            argv = [sys.executable, '-I', '-O', '-B', str(V.HERE / 'verify.py')]
            completed = subprocess.run(argv + ['--emit', str(occupied)], capture_output=True,
                                       text=True, timeout=10)
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn('refuse existing receipt', completed.stderr)
            self.assertEqual(occupied.read_text(), 'keep\n')
            package = root / 'research' / 'fixture'
            package.mkdir(parents=True)
            (package / 'verify.py').write_bytes((V.HERE / 'verify.py').read_bytes())
            sources = json.loads((V.HERE / 'SOURCES.json').read_text())
            for item in sources['files']:
                if item['usage'] == 'input':
                    target = root / item['path']
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes((V.ROOT / item['path']).read_bytes())
            first = next(item for item in sources['files'] if item['usage'] == 'input')
            first['sha256'] = '0' * 64
            (package / 'SOURCES.json').write_text(json.dumps(sources))
            completed = subprocess.run([sys.executable, '-I', '-O', '-B', str(package / 'verify.py')],
                                       capture_output=True, text=True, timeout=10)
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn('source digest', completed.stderr)


if __name__ == '__main__':
    unittest.main()
