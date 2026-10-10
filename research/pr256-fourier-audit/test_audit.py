#!/usr/bin/env python3
"""Mutation controls on the real pinned program, statements and build evidence."""
import copy
import gzip
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch

import verify


class AuditControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = verify.source_check()
        cls.program = json.loads(gzip.decompress(
            (verify.PACKAGE/'certificates/gcert1-p11-pr233-flow.json.gz').read_bytes()))
        with tarfile.open(verify.VENDOR/'fourier-proof-source.tar.gz') as archive:
            cls.lean_program = json.loads(gzip.decompress(archive.extractfile(
                'tools/certificate/gcert1-p11-pr233-flow.json.gz').read()))
            cls.original = archive.extractfile(
                'third-party/openai-math/lean/ComparatorChallenges/UniformFourier.lean').read().decode()
            cls.challenge = archive.extractfile(
                'Work/Fourier233/UniformFourierChallenge.lean').read().decode()

    def test_provenance_text_is_not_mathematical_data(self):
        self.assertNotEqual(self.program['derived_from'], self.lean_program['derived_from'])
        verify.compare_programs(self.program, self.lean_program)

    def test_changed_register_stock_rejects(self):
        candidate = dict(self.program, R=self.program['R']-1)
        with self.assertRaisesRegex(ValueError, 'Lean input program differs'):
            verify.compare_programs(candidate, self.lean_program)

    def test_changed_child_count_rejects(self):
        candidate = copy.deepcopy(self.program)
        counts = next(iter(candidate['blocks'].values()))
        counts[next(iter(counts))] += 1
        with self.assertRaisesRegex(ValueError, 'Lean input program differs'):
            verify.compare_programs(candidate, self.lean_program)

    def test_original_challenge_matches(self):
        verify.compare_challenges(self.original, self.challenge)

    def test_unrecorded_exponent_rejects(self):
        candidate = self.challenge.replace('7547360', '7547362')
        self.assertNotEqual(candidate, self.challenge)
        with self.assertRaisesRegex(ValueError, 'challenge differs'):
            verify.compare_challenges(self.original, candidate)

    def test_weakened_statement_rejects(self):
        candidate = self.challenge.replace('∀', '∃', 1)
        self.assertNotEqual(candidate, self.challenge)
        with self.assertRaisesRegex(ValueError, 'challenge differs'):
            verify.compare_challenges(self.original, candidate)

    def check_bad_receipt(self, change, message):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(verify.BASE/'evidence', root/'evidence')
            path = root/'evidence/five_stage_lean_receipt.json'
            receipt = json.loads(path.read_text())
            change(receipt)
            path.write_text(json.dumps(receipt))
            with patch.object(verify, 'BASE', root):
                with self.assertRaisesRegex(ValueError, message):
                    verify.check_evidence(self.source)

    def test_extra_axiom_rejects(self):
        self.check_bad_receipt(lambda r: r['axioms']['OAI.PowerSaving.transform_mainY'].append('sorryAx'),
                              'unexpected recorded axioms')

    def test_missing_build_rejects(self):
        self.check_bad_receipt(lambda r: r.update(commands=[c for c in r['commands'] if c['label'] != 'build']),
                              'recorded commands differ')

    def test_wrong_source_revision_rejects(self):
        self.check_bad_receipt(lambda r: r.update(source_commit='0'*40), 'receipt source differs')

    def test_changed_log_rejects(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(verify.BASE/'evidence', root/'evidence')
            (root/'evidence/logs/build.log.gz').write_bytes(gzip.compress(b'Build completed', mtime=0))
            with patch.object(verify, 'BASE', root):
                with self.assertRaisesRegex(ValueError, 'recorded log differs: build'):
                    verify.check_evidence(self.source)

    def test_optimized_mode_refused(self):
        result = subprocess.run([sys.executable, '-B', '-O', str(verify.BASE/'verify.py')],
                                capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Run without -O', result.stderr)


if __name__ == '__main__':
    unittest.main()
