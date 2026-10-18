#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Fault-sensitive algebra, frame, invoice and portable-package controls."""
import copy
import importlib.util
import json
import random
import shutil
import subprocess
import sys
import tempfile
import unittest
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('early_retirement_check', HERE/'verify.py')
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)


class PackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = HERE.parents[1]
        cls.word = check.load_word(cls.root)
        cls.geometry = check.Geometry(cls.word)
        cls.frames, cls.values, _ = check.prefix_and_baseline(cls.word, cls.geometry)
        cls.inverse = check.invert(cls.values)
        cls.cert = json.loads((HERE/'CERTIFICATE.json').read_text())

    def candidate(self, sections=None, final=None):
        if final is None:
            final = self.word['final'][:]
            final[470] = 513
        return check.replay_complete(self.word, self.geometry,
            check.patched_sections(self.word) if sections is None else sections, final)

    def test_complete_receipt_and_independent_replay(self):
        self.assertEqual(check.canonical(check.analyze(self.word)), check.canonical(self.cert))
        p = subprocess.run([sys.executable, '-I', '-O', '-B', str(HERE/'independent.py')],
                           capture_output=True, text=True, timeout=30)
        self.assertEqual(p.returncode, 0, p.stdout+p.stderr)
        self.assertIn('PASS_INDEPENDENT_EARLY_RETIREMENT', p.stdout)

    def test_all_22_star_gate_omissions(self):
        count = 0
        for case in self.cert['retirements']:
            h = case['helper']
            for omitted in range(len(case['star_gates'])):
                state = self.values[:]
                for j, (t, s) in enumerate(case['star_gates']):
                    if j != omitted:
                        state[t] ^= state[s]
                isolated = state[h] == 1 << h and all(not row >> h & 1
                                                     for r, row in enumerate(state) if r != h)
                self.assertFalse(isolated, (h, omitted))
                count += 1
        self.assertEqual(count, 22)

    def test_three_retirement_gate_omissions(self):
        for j in range(3):
            gates = [g for i, g in enumerate(check.RETIREMENT_GATES) if i != j]
            with self.assertRaisesRegex(check.Reject, 'retirement separation'):
                self.candidate(check.patched_sections(self.word, gates))

    def test_both_cleanup_edits_are_necessary(self):
        sections = check.patched_sections(self.word)
        cleanup = copy.deepcopy(sections[-1][1])
        cleanup[580] = copy.deepcopy(self.word['C'][580])
        with self.assertRaisesRegex(check.Reject, 'complete dirty endpoint'):
            self.candidate(sections[:-1]+[('C', cleanup)])
        cleanup = copy.deepcopy(sections[-1][1])
        cleanup.insert(2343, copy.deepcopy(self.word['C'][2343]))
        with self.assertRaisesRegex(check.Reject, 'complete dirty endpoint'):
            self.candidate(sections[:-1]+[('C', cleanup)])

    def test_common_frame_promotion_breaks_target_access(self):
        gates = copy.deepcopy(check.RETIREMENT_GATES)
        gates[0][0] = 513
        with self.assertRaisesRegex(check.Reject, 'candidate frame descent'):
            self.candidate(check.patched_sections(self.word, gates))
        final = self.word['final'][:]
        final[470] = 0
        with self.assertRaisesRegex(check.Reject, 'candidate frame descent'):
            self.candidate(final=final)

    def test_exact_input_pair_and_geometric_witnesses(self):
        for case in self.cert['retirements']:
            witness = case['witness']
            delta = sum(1 << i for i in witness['original_input_delta'])
            wrong_delta = delta ^ (1 << case['helper'])
            actual = [int(bin(row & wrong_delta).count('1') % 2) for row in self.values]
            self.assertNotEqual(actual, [int(i == witness['boundary_coordinate']) for i in range(661)])
            target = witness['target']
            sep = witness['separation']
            normal = sep['normal']
            self.assertTrue(any(normal))
            self.assertTrue(all(sum(x*y for x, y in zip(normal, self.word['lines'][line])) == 0
                                for line in self.word['frames'][self.word['final'][target]]))
            self.assertNotEqual(sum(x*y for x, y in zip(normal, self.word['lines'][sep['line']])), 0)

    def test_geometry_scope_controls(self):
        w = copy.deepcopy(self.word)
        # Permitting every target to end at the full frame removes this cut.
        for t in range(w['v'], 2*w['v']):
            w['final'][t] = 1
        for case in self.cert['retirements']:
            self.assertEqual(check.lost_targets(self.inverse, case['forced_participants'],
                                                case['terminal_frame'], w, self.geometry), [])
        # The smaller first frame really is a distinct allowed mechanism.
        self.assertEqual([x['helper'] for x in self.cert['retirements']
                          if not x['least_frame_restoration']['lost_targets']], [470])
        self.assertEqual([len(x['least_frame_restoration']['lost_targets'])
                          for x in self.cert['retirements']], [1, 1, 1, 10, 0, 9])

    def test_small_binary_inverse_oracle(self):
        rng = random.Random(8)
        cases = 0
        for n in range(2, 7):
            for trial in range(12):
                rows = [1 << i for i in range(n)]
                for _ in range(4*n):
                    t, s = rng.sample(range(n), 2)
                    rows[t] ^= rows[s]
                inv = check.invert(rows)
                for bits in range(1 << n):
                    image = sum((bin(row & bits).count('1') % 2) << i for i, row in enumerate(rows))
                    restored = sum((bin(row & image).count('1') % 2) << i for i, row in enumerate(inv))
                    self.assertEqual(restored, bits)
                cases += 1
        self.assertEqual(cases, 60)
        with self.assertRaisesRegex(check.Reject, 'singular'):
            check.invert([1, 1])

    def test_interval_arithmetic_and_returned_idle_charge(self):
        invoice = self.cert['construction']['optimistic_hosting']
        a = Fraction(invoice['exponent'])
        with localcontext() as context:
            context.prec = 70
            exponent = Decimal(a.numerator)/Decimal(a.denominator)
            for case in invoice['cases']:
                delta = {int(k): v for k, v in case['profile_delta'].items()}
                self.assertEqual(sum(delta.values()), 0)
                self.assertEqual(sum(r*c for r, c in delta.items()), 0)
                removed_charge = dict(delta)
                del removed_charge[case['old_remainder']+8]
                self.assertNotEqual(sum(r*c for r, c in removed_charge.items()), 0)
                # Diagnostic cross-check of the rationally certified interval;
                # Decimal is not used to certify the sign.
                actual = sum(Decimal(c*r)*((Decimal(64)/r).ln()*exponent).exp()
                             for r, c in delta.items())
                lo, hi = map(Fraction, case['weighted_delta_interval'])
                self.assertLess(Decimal(lo.numerator)/lo.denominator, actual)
                self.assertLess(actual, Decimal(hi.numerator)/hi.denominator)
                self.assertLess(hi, 0)
        for r in (1, 2, 5, 7, 14):
            lo, hi = check.weight_interval(r, Fraction(0))
            self.assertEqual((lo, hi), (r, r))

    def test_offline_relocation_and_source_failure(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            package = root/'research'/'bit-early-retirement-cut'
            package.mkdir(parents=True)
            for name in ['verify.py', 'independent.py', 'SOURCES.json', 'CERTIFICATE.json']:
                shutil.copy2(HERE/name, package/name)
            source = root/check.WORD
            source.parent.mkdir(parents=True)
            shutil.copy2(self.root/check.WORD, source)
            original = {str(p.relative_to(root)): p.read_bytes() for p in root.rglob('*') if p.is_file()}
            for name in ['verify.py', 'independent.py']:
                p = subprocess.run([sys.executable, '-I', '-O', '-B', str(package/name)],
                                   cwd=temp, capture_output=True, text=True, timeout=30)
                self.assertEqual(p.returncode, 0, p.stdout+p.stderr)
            self.assertEqual(original, {str(p.relative_to(root)): p.read_bytes() for p in root.rglob('*') if p.is_file()})
            source.write_bytes(source.read_bytes()+b'corruption')
            for name in ['verify.py', 'independent.py']:
                p = subprocess.run([sys.executable, '-I', '-O', '-B', str(package/name)],
                                   capture_output=True, text=True, timeout=30)
                self.assertNotEqual(p.returncode, 0)
                self.assertIn('source', p.stderr)

    def test_receipt_corruptions_rejected_by_both_checkers(self):
        mutations = []
        for kind in ['cut', 'geometry', 'construction', 'invoice']:
            receipt = copy.deepcopy(self.cert)
            if kind == 'cut':
                receipt['retirements'][0]['lost_targets'].pop()
            elif kind == 'geometry':
                receipt['retirements'][0]['witness']['separation']['normal'] = [0]*8
            elif kind == 'construction':
                receipt['construction']['retirement_gates'].pop()
            else:
                receipt['construction']['candidate']['profile']['1'] -= 1
            mutations.append((kind, receipt))
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            for name in ['verify.py', 'independent.py', 'SOURCES.json']:
                shutil.copy2(HERE/name, folder/name)
            for kind, receipt in mutations:
                (folder/'CERTIFICATE.json').write_text(check.canonical(receipt))
                for script in ['verify.py', 'independent.py']:
                    p = subprocess.run([sys.executable, '-I', '-O', '-B', str(folder/script),
                                        '--root', str(self.root)], capture_output=True, text=True, timeout=30)
                    self.assertNotEqual(p.returncode, 0, (kind, script, p.stdout))
                    self.assertIn('REJECT:', p.stderr)


if __name__ == '__main__':
    unittest.main(verbosity=2)
