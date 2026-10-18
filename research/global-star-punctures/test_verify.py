#!/usr/bin/env python3
"""Direct decoder-equation checks, without the certificate generator or syndromes.

Copyright 2026 Alishan Ladhani. SPDX-License-Identifier: Apache-2.0
Prepared with substantial OpenAI Codex assistance.
"""
from itertools import combinations, product
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent


def word_family(p, k):
    # Ternary words independently describe absent / first / second coordinates.
    # Convert to the certificate's ordering only after generating the family.
    family = [tuple(2 * i + x - 1 for i, x in enumerate(word) if x)
              for word in product((0, 1, 2), repeat=p) if sum(x != 0 for x in word) == k]
    return sorted(family, key=lambda port: (tuple(c // 2 for c in port), tuple(c % 2 for c in port)))


def decoder_exists(p, k, target, deleted, include_target_star=False, allow_missing_target=False):
    family = word_family(p, k)
    if target in deleted and not allow_missing_target:
        raise ValueError('target not retained')
    terms = [set(s) for d in range(1, k) for s in word_family(p, d)]
    if include_target_star:
        terms.append(set(family[target]))
    rhs = len(terms) + k - 1
    pivots = {}
    for index, port in enumerate(family):
        if index in deleted:
            continue
        source = set(port)
        row = {i for i, term in enumerate(terms) if term <= source}
        overlap = len(source & set(family[target]))
        if 0 < overlap < k:
            row.add(len(terms) + overlap - 1)
        if index == target:
            row.add(rhs)
        while row:
            pivot = min(row)
            if pivot == rhs:
                return False
            if pivot not in pivots:
                pivots[pivot] = row
                break
            row = row ^ pivots[pivot]
    return True


class DecoderChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.certificate = json.loads((HERE / 'CERTIFICATE.json').read_text())

    def test_all_optima_and_every_one_port_restoration(self):
        for witness in self.certificate['optimal_deletions']:
            deleted = set(witness['deleted_indices'])
            self.assertTrue(decoder_exists(6, 4, 42, deleted))
            for restored in deleted:
                self.assertFalse(decoder_exists(6, 4, 42, deleted - {restored}))
        self.assertFalse(decoder_exists(6, 4, 42, set()))

    def test_same_size_wrong_punctures_fail(self):
        for witness in self.certificate['optimal_deletions']:
            deleted = set(witness['deleted_indices'])
            outside = next(i for i in range(240) if i not in deleted and i != 42)
            for removed in deleted:
                candidate = deleted - {removed} | {outside}
                self.assertFalse(decoder_exists(6, 4, 42, candidate))

    def test_scope_positive_controls(self):
        self.assertTrue(decoder_exists(6, 4, 42, set(), include_target_star=True))
        self.assertTrue(decoder_exists(4, 3, 0, set()))
        self.assertTrue(decoder_exists(4, 4, 0, {1}))
        with self.assertRaises(ValueError):
            decoder_exists(6, 4, 42, {42})
        self.assertTrue(decoder_exists(6, 4, 42, {42}, allow_missing_target=True))

    def test_information_set_decodes_every_retained_target(self):
        # Independently invert the restricted star matrix with coefficient
        # tracking, then check all 155 unit vectors against actual incidences.
        family = word_family(6, 4)
        stars = [set(s) for d in (1, 2, 3) for s in word_family(6, d)]
        retained = self.certificate['code']['information_set']
        columns = [{position for position, index in enumerate(retained)
                    if star <= set(family[index])} for star in stars]
        pivots = {}
        for i, original in enumerate(columns):
            row, coefficients = set(original), {i}
            while row:
                pivot = min(row)
                if pivot in pivots:
                    row ^= pivots[pivot][0]
                    coefficients ^= pivots[pivot][1]
                else:
                    pivots[pivot] = row, coefficients
                    break
        self.assertEqual(len(pivots), 155)
        for target in range(155):
            row, coefficients = {target}, set()
            while row:
                pivot = min(row)
                row ^= pivots[pivot][0]
                coefficients ^= pivots[pivot][1]
            result = set()
            for i in coefficients:
                result ^= columns[i]
            self.assertEqual(result, {target})

    def test_certificate_corruption_rejected_under_optimization(self):
        with tempfile.TemporaryDirectory() as directory:
            for mutation in ('target', 'check', 'coverage', 'solution'):
                changed = json.loads(json.dumps(self.certificate))
                if mutation == 'target':
                    changed['instance']['target_index'] = 41
                elif mutation == 'check':
                    changed['code']['parity_checks_hex'][0] = '0' * 60
                elif mutation == 'coverage':
                    changed['enumeration']['triples'] -= 1
                else:
                    changed['optimal_deletions'].pop()
                path = Path(directory) / (mutation + '.json')
                path.write_text(json.dumps(changed))
                run = subprocess.run([sys.executable, '-I', '-O', '-B', str(HERE / 'verify.py'),
                                      '--certificate', str(path)], capture_output=True, text=True)
                self.assertNotEqual(run.returncode, 0)
                self.assertIn('ValueError', run.stderr)
                self.assertNotIn('PASS_GLOBAL_STAR_PUNCTURES', run.stdout)


if __name__ == '__main__':
    unittest.main(verbosity=2)
