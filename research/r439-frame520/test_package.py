#!/usr/bin/env python3
"""Relocation, optimized replay, and fail-closed package regressions.

Runs one complete finite replay under ``python -O`` in a minimal closure whose
path contains spaces. Rejection cases must fail before loading the source
checker, so malformed metadata never triggers repeated expensive replays.
Ross Richardson, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

HERE = Path(__file__).resolve().parent


def load_verifier(path):
    spec = importlib.util.spec_from_file_location('frame520_package_verifier', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.work = tempfile.TemporaryDirectory(prefix='frame520 package tests ')
        cls.addClassCleanup(cls.work.cleanup)
        cls.root = Path(cls.work.name) / 'minimal source closure with spaces'
        cls.here = cls.root / 'research/r439-frame520'
        cls.here.mkdir(parents=True)
        original = load_verifier(HERE / 'verify.py')
        for relative in [*original.PINS, 'research/r439-frame520/verify.py',
                         'research/r439-frame520/candidate.json']:
            target = cls.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(original.ROOT / relative, target)
        cls.verify = load_verifier(cls.here / 'verify.py')
        cls.certificate = json.loads((cls.here / 'candidate.json').read_text())

    def reject_before_source_checker(self, certificate, message):
        candidate = self.here / 'invalid candidate.json'
        candidate.write_text(json.dumps(certificate))
        out = self.root / 'must not publish receipt'
        # A missing certificate guard becomes an immediate failure, rather than
        # silently passing by a later unrelated check or running another replay.
        with mock.patch.object(self.verify.importlib.util, 'spec_from_file_location',
                               side_effect=AssertionError('source checker reached')):
            with self.assertRaisesRegex(self.verify.Reject, message):
                self.verify.run(out, candidate)
        self.assertFalse(out.exists())

    def test_optimized_replay_after_minimal_relocation(self):
        out = self.root / 'optimized replay with spaces'
        completed = subprocess.run(
            [sys.executable, '-I', '-B', '-O', str(self.here / 'verify.py'), '--out', str(out)],
            cwd=self.root, text=True, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, timeout=240, check=False)
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertIn('PASS_R439_FRAME520', completed.stdout)
        self.assertIn('block=41->29', completed.stdout)
        receipt = json.loads((out / 'receipt.json').read_text())
        self.assertEqual(receipt['status'], 'PASS_R439_FRAME520')
        self.assertEqual(receipt['source_pins'], self.verify.PINS)
        self.assertEqual((receipt['local']['before'], receipt['local']['after']), (41, 29))
        self.assertEqual(receipt['local']['truth_table_inputs'], 4096)
        self.assertEqual(receipt['baseline']['bill']['total_additions'] -
                         receipt['replacement']['bill']['total_additions'], 24)
        self.assertEqual(receipt['baseline']['bill']['paid_profile'],
                         receipt['replacement']['bill']['paid_profile'])
        self.assertEqual(receipt['baseline']['frame_paths_sha256'],
                         receipt['replacement']['frame_paths_sha256'])
        self.assertTrue(all(receipt['replacement']['hypotheses'].values()))
        self.assertTrue(all(receipt['replacement']['conclusion'].values()))
        self.assertIn('omit_cleanup', receipt['controls'])
        self.assertEqual(receipt['controls']['omit_cleanup'], 'rejected')
        self.assertTrue((out / 'baseline.json.gz').is_file())
        self.assertTrue((out / 'replacement.json.gz').is_file())

    def test_existing_receipt_is_preserved(self):
        out = self.root / 'existing evidence'
        out.mkdir()
        prior = b'previous independent receipt must survive\n'
        (out / 'receipt.json').write_bytes(prior)
        with mock.patch.object(self.verify.importlib.util, 'spec_from_file_location',
                               side_effect=AssertionError('existing output should fail early')):
            with self.assertRaises((self.verify.Reject, FileExistsError)):
                self.verify.run(out, self.here / 'candidate.json')
        self.assertEqual((out / 'receipt.json').read_bytes(), prior)
        self.assertEqual(sorted(p.name for p in out.iterdir()), ['receipt.json'])

    def test_each_immutable_source_pin_rejects_corruption(self):
        for relative in self.verify.PINS:
            with self.subTest(source=relative):
                path = self.root / relative
                saved = path.read_bytes()
                try:
                    path.write_bytes(saved + b'\ncorruption\n')
                    self.reject_before_source_checker(self.certificate, 'source digest differs')
                finally:
                    path.write_bytes(saved)

    def test_certificate_matrix_corruption(self):
        for field in ('forward_transfer', 'candidate_reverse_positive_transfer',
                      'original_reverse_positive_transfer'):
            with self.subTest(field=field):
                candidate = copy.deepcopy(self.certificate)
                candidate[field][0][0] += 1
                self.reject_before_source_checker(candidate, 'certificate matrix differs')

    def test_certificate_gate_bill_corruption(self):
        for field in ('candidate_gate_count', 'original_gate_count'):
            with self.subTest(field=field):
                candidate = copy.deepcopy(self.certificate)
                candidate[field] += 1
                self.reject_before_source_checker(candidate, 'certificate gate bill differs')

    def test_certificate_source_pin_corruption(self):
        candidate = copy.deepcopy(self.certificate)
        candidate['source_sha256'] = '0' * 64
        self.reject_before_source_checker(candidate, 'certificate source pin differs')

    def test_frozen_research_metadata_corruption(self):
        mutations = {
            'base_commit': '0' * 40,
            'assignment_seed': 6,
            'search_seed': 6,
            'phase': 'C',
            'completed_trajectories': 1832,
            'exact_factorizations': 371,
            'requested_trajectories': 4999,
            'selected_attempt_zero_based': 1831,
            'status': 'unchecked',
            'reverse_positive_entrywise_dominated': False,
        }
        for field, value in mutations.items():
            with self.subTest(field=field):
                candidate = copy.deepcopy(self.certificate)
                candidate[field] = value
                self.reject_before_source_checker(candidate, 'frozen certificate metadata differs: ' + field)

    def test_search_coverage_count_corruption(self):
        candidate = copy.deepcopy(self.certificate)
        candidate['length_histogram']['29'] += 1
        self.reject_before_source_checker(candidate, 'search histogram count differs')

    def test_certificate_object_corruption(self):
        for field in ('frame', 'start', 'stop', 'wires'):
            with self.subTest(field=field):
                candidate = copy.deepcopy(self.certificate)
                if field == 'wires':
                    candidate[field] = list(reversed(candidate[field]))
                else:
                    candidate[field] += 1
                self.reject_before_source_checker(candidate, 'certificate object differs')

    def test_certificate_program_alias_corruption(self):
        candidate = copy.deepcopy(self.certificate)
        candidate['candidate_ops'][0][1] = 21
        self.reject_before_source_checker(candidate, 'certificate program aliases disagree')

    def test_certificate_original_program_corruption(self):
        candidate = copy.deepcopy(self.certificate)
        candidate['original_ops'][0][1] = 21
        self.reject_before_source_checker(candidate, 'old program differs')

    def test_foreign_register_rejected(self):
        candidate = copy.deepcopy(self.certificate)
        candidate['operations'][0][0] = 999999
        self.reject_before_source_checker(candidate, 'invalid block operand')


if __name__ == '__main__':
    unittest.main(verbosity=2)
