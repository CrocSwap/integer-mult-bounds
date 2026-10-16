#!/usr/bin/env python3
"""Mutation, ownership and exported-source boundary checks; stdlib only."""
from copy import deepcopy
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location('l2_verifier', HERE/'verify.py')
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)


class TestBoundaries(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.R, cls.records, _ = V.N.load_sources()
        cls.word = V.program(cls.R)
        cls.temp = tempfile.TemporaryDirectory(prefix='qq16-l2-')
        cls.export = Path(cls.temp.name).resolve()
        if not cls.export.is_relative_to(Path(tempfile.gettempdir()).resolve()):
            raise RuntimeError('unexpected temporary export root')
        cls.package = cls.export/'research'/HERE.name
        shutil.copytree(HERE, cls.package, ignore=shutil.ignore_patterns('__pycache__'))
        sources = json.loads((HERE/'SOURCES.json').read_text(encoding='utf-8'))
        for item in sources['files']:
            if item['usage'] == 'input':
                target = cls.export/item['path']
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT/item['path'], target)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def run_export(self):
        env = dict(os.environ)
        env['PATH'] = ''
        return subprocess.run([sys.executable, '-I', '-O', '-B', str(self.package/'verify.py')],
                              cwd=self.export, capture_output=True, text=True, env=env, timeout=60)

    def test_private_scratch_must_be_clean(self):
        word = deepcopy(self.word)
        last = max(i for i, e in enumerate(word) if e['op'] == 'clear' and e['field'] == 'C')
        del word[last]
        with self.assertRaisesRegex(ValueError, 'private owner body not clean'):
            V.replay(word, self.R, self.records)

    def test_complete_alignment_precedes_scalar_body(self):
        word = deepcopy(self.word)
        index = next(i for i, e in enumerate(word) if e['op'] == 'map' and e['field'] == 'Z1' and not e['inverse'])
        moved = word.pop(index)
        index = next(i for i, e in enumerate(word) if e['op'] == 'add' and e['dst'] == 'Z1' and e['src'] == 'C')
        word.insert(index+1, moved)
        with self.assertRaisesRegex(ValueError, 'native ADD frame mismatch'):
            V.replay(word, self.R, self.records)

    def test_git_free_optimized_export_is_read_only(self):
        paths = [p for p in self.export.rglob('*') if p.is_file()]
        before = {p: p.read_bytes() for p in paths}
        result = self.run_export()
        self.assertEqual(result.returncode, 0, result.stdout+result.stderr)
        self.assertIn('PASS_QQ16_L2_NATIVE_RECONSTRUCTION', result.stdout)
        self.assertEqual(before, {p: p.read_bytes() for p in paths})
        self.assertFalse(any(self.export.rglob('__pycache__')))

    def test_receipt_and_literal_word_are_required(self):
        for name, change in [('RESULT.json', lambda v: v['invoice'].__setitem__('native_rank_mass', 400)),
                             ('WORD.json', lambda v: v[0].__setitem__('sign', -1))]:
            path = self.package/name
            before = path.read_bytes()
            try:
                value = json.loads(before)
                change(value)
                path.write_text(json.dumps(value), encoding='utf-8')
                result = self.run_export()
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('committed '+name+' differs', result.stderr)
            finally:
                path.write_bytes(before)
        path = self.package/'RESULT.json'
        target = self.package/'RESULT.saved'
        path.rename(target)
        try:
            self.assertNotEqual(self.run_export().returncode, 0)
        finally:
            target.rename(path)

    def test_cost_source_and_pending_evidence_drift_rejected(self):
        for relative in ['research/joint-query/verify_scalar.py',
                         'research/qq16-l2-native-reconstruction/evidence/PR2470-README.md']:
            path = self.export/relative
            before = path.read_bytes()
            try:
                path.write_bytes(before+b'\n# mutation\n')
                result = self.run_export()
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('source hash:', result.stderr)
            finally:
                path.write_bytes(before)


if __name__ == '__main__':
    unittest.main()
