#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Meaningful scalar, source-binding and accounting controls; no native rebuild.
Sricharan Vagvala (@theon199), with substantial OpenAI Codex assistance.
"""
import copy
import importlib.util
import shutil
import struct
import tempfile
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('helper470_verify', HERE / 'verify.py')
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)


class PackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.word = V.load(V.ROOT / V.WORD)
        cls.checker = V.owning_checker(V.ROOT)

    def test_complete_dirty_maps_and_precise_interface_boundary(self):
        for full in (False, True):
            report = V.local_check(V.candidate(self.word, full), self.checker)
            self.assertTrue(all(report['conclusion'].values()))
            self.assertEqual([key for key, value in report['hypotheses'].items() if not value],
                             ['H4_C_literal_reverse_at_full'])
            self.assertEqual(report['nonfull_helpers'], [] if full else [470])

    def test_every_retirement_gate_is_necessary(self):
        for omitted in range(3):
            word = V.candidate(self.word)
            del word['B'][omitted]
            with self.subTest(omitted=omitted), self.assertRaisesRegex(ValueError, 'dirty scalar endpoint'):
                V.local_check(word, self.checker)

    def test_both_cleanup_changes_are_necessary(self):
        word = V.candidate(self.word)
        word['C'][580] = copy.deepcopy(self.word['C'][580])
        with self.assertRaisesRegex(ValueError, 'dirty scalar endpoint'):
            V.local_check(word, self.checker)
        word = V.candidate(self.word)
        word['C'].insert(2343, copy.deepcopy(self.word['C'][2343]))
        with self.assertRaisesRegex(ValueError, 'dirty scalar endpoint'):
            V.local_check(word, self.checker)

    def test_wrong_restoration_frame_is_rejected(self):
        word = V.candidate(self.word)
        word['B'][0][0] = 0
        with self.assertRaisesRegex(self.checker.Reject, 'climb not nested'):
            V.local_check(word, self.checker)

    def test_literal_interface_is_not_silently_relaxed(self):
        with self.assertRaisesRegex(self.checker.Reject, 'helper final frame is not full'):
            self.checker.Word(V.candidate(self.word)).full()
        self.checker.Word(V.candidate(self.word, True)).full()

    def test_patch_refuses_changed_source_positions(self):
        for position in (580, 2343):
            word = copy.deepcopy(self.word)
            word['C'][position][2] = [0]
            with self.subTest(position=position), self.assertRaisesRegex(ValueError, 'pinned cleanup'):
                V.candidate(word)

    def test_full_terminal_charge_is_counted(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'moves.bin'
            paths = [
                [(0, 470, 0, 79, 1, 0), (0, 470, 79, 1, 7, 0)],
                [(0, 470, 0, 79, 1, 0), (0, 470, 79, 186, 1, 0), (0, 470, 186, 513, 5, 0)],
                [(0, 470, 0, 79, 1, 0), (0, 470, 79, 186, 1, 0), (0, 470, 186, 513, 5, 0),
                 (0, 470, 513, 1, 1, 0)]]
            profiles = []
            for events in paths:
                path.write_bytes(b''.join(struct.pack('<6i', *row) for row in events))
                profiles.append(V.record_invoice(path)[0]['profile'])
            self.assertEqual(V.profile_delta(profiles[0], profiles[1]), {'1': 1, '5': 1, '7': -1})
            self.assertEqual(V.profile_delta(profiles[0], profiles[2]), {'1': 2, '5': 1, '7': -1})
            path.write_bytes(struct.pack('<6i', 0, 470, 513, 1, 0, 0))
            with self.assertRaisesRegex(ValueError, 'nonpositive exported MOVE'):
                V.record_invoice(path)

    def test_corrupt_live_source_is_rejected_before_execution(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for item in V.load(HERE / 'SOURCES.json')['files']:
                if item['usage'] == 'input':
                    destination = root / item['path']
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(V.ROOT / item['path'], destination)
            V.source_pins(root)
            with (root / V.WORD).open('ab') as stream:
                stream.write(b'fault')
            with self.assertRaisesRegex(ValueError, 'source SHA256'):
                V.source_pins(root)


if __name__ == '__main__':
    unittest.main(verbosity=2)
