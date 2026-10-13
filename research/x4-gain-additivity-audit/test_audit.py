#!/usr/bin/env python3
"""Behavioral controls for the pinned X4 additivity audit."""
import copy
from fractions import Fraction as Q
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('x4_gain_verify', HERE / 'verify.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class AuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = audit.verify()

    def test_complete_audit_and_optimized_run(self):
        result = self.result
        self.assertEqual(result['status'], 'PASS_X4_PROFILE_ADDITIVE_IDEAL_KAPPA_NONADDITIVE')
        self.assertEqual(len(result['subsets']), 16)
        self.assertEqual(len(result['global_profiles']), 5)
        self.assertEqual(len(result['second_differences']), 3)
        self.assertGreater(Q(result['four_vs_four_singles'][0]), 0)
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'receipt.json'
            subprocess.run([sys.executable, '-O', '-B', '-I', str(HERE / 'verify.py'),
                            '--output', str(output)], check=True, capture_output=True, text=True)
            self.assertEqual(json.loads(output.read_text()), result)

    def test_corrupt_source_pin_rejected(self):
        sources = json.loads((HERE / 'SOURCES.json').read_text())
        sources['files'][audit.BUILDER] = '0'*64
        with self.assertRaisesRegex(ValueError, 'source digest differs'):
            audit.check_sources(audit.ROOT, sources)

    def test_archive_container_digest_is_reference_only(self):
        sources = json.loads((HERE / 'SOURCES.json').read_text())
        sources['archive_sha256_reference_only'] = '0'*64
        audit.check_sources(audit.ROOT, sources)
        word = audit.archive_word(audit.ROOT, sources)
        self.assertEqual(word['report']['R'], 504)

    def test_linearized_ideal_gain_rejected_by_exact_signs(self):
        sources = json.loads((HERE / 'SOURCES.json').read_text())
        rows = self.result['global_profiles']
        profiles = [{int(r): n for r, n in profile.items()} for profile in rows]
        def ideal_midpoint(j):
            low, high = map(Q, sources['root_brackets'][str(j)])
            a = (low+high)/2
            return a/(1+a)
        linear_k2 = 2*ideal_midpoint(1)-ideal_midpoint(0)
        linear_a2 = linear_k2/(1-linear_k2)
        low = Q((linear_a2*10**24).__floor__(), 10**24)
        sources['root_brackets']['2'] = [str(low), str(low + Q(1, 10**24))]
        moment = audit.load(audit.ROOT / (audit.ENGINES + 'moment.py'), 'moment_control')
        base_two = audit.load(audit.ROOT / (audit.ENGINES + 'base_two_moment.py'), 'base_two_control')
        with self.assertRaisesRegex(ValueError, 'root bracket sign fails'):
            audit.exact_brackets(profiles, sources, moment, base_two)

    def test_linearized_profile_substitution_rejected(self):
        rows = self.result['global_profiles']
        selected = {int(r): n for r, n in rows[4].items()}
        idle = {1: 1, 3: 1, 44: 1, 48: 2396}
        locals_ = []
        for row in rows:
            profile = {int(r): n for r, n in row.items()}
            locals_.append({r: (n-idle.get(r, 0))//72 for r, n in profile.items()
                            if n != idle.get(r, 0)})
        bad = copy.deepcopy(locals_)
        bad[2][1] += 2
        bad[2][2] -= 1
        with self.assertRaisesRegex(ValueError, 'local profile is not the paired delta'):
            audit.check_profile_family(bad, selected, idle, 72)


if __name__ == '__main__':
    unittest.main()
