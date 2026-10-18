#!/usr/bin/env python3
"""Semantic certificate and Git-free source/export controls."""
import copy
import hashlib
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
spec = importlib.util.spec_from_file_location('reviewed_gauge_verifier', HERE/'verify.py')
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)


def files(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()}


class Controls(unittest.TestCase):
    def test_semantic_certificates_and_literal_word(self):
        result = V.read(HERE/'RESULT.json')
        word = result['full_word']
        cert = copy.deepcopy(word['certificate'])
        cert['weights'][0] += 1
        with self.assertRaisesRegex(ValueError, 'even denominator'):
            V.C.check(2, word['matrices'], cert)
        cert = {'kind': 'potential', 'weights': [False, 1]}
        with self.assertRaisesRegex(ValueError, 'integer potential'):
            V.C.check(2, word['matrices'], cert)
        bad = result['negative_cases'][2]
        with self.assertRaisesRegex(ValueError, 'does not close'):
            V.C.check(2, bad['matrices'], {'kind': 'negative-cycle', 'edge_indices': [1]})
        with self.assertRaisesRegex(ValueError, 'not negative'):
            V.C.check(2, bad['matrices'], {'kind': 'negative-cycle', 'edge_indices': [0]})
        matrices, operations = V.W.fixture()
        with self.assertRaisesRegex(ValueError, 'complete formal'):
            V.W.replay(matrices, operations[:7]+operations[8:])

    def export(self, root):
        package = root/'research'/HERE.name
        shutil.copytree(HERE, package, ignore=shutil.ignore_patterns('__pycache__'))
        manifest = V.read(HERE/'SOURCES.json')
        for row in manifest['files']:
            target = root/row['path']
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((ROOT/row['path']).read_bytes())
        return package

    def run_export(self, package, *extra):
        env = dict(os.environ, PATH='', PYTHONIOENCODING='utf-8')
        return subprocess.run([sys.executable, '-I', '-O', '-B', str(package/'verify.py'), *extra],
                              env=env, cwd=package.parents[1], capture_output=True,
                              text=True, timeout=60)

    def test_git_free_export_readonly_and_emission(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            package = self.export(root)
            before = files(root)
            run = self.run_export(package)
            self.assertEqual(run.returncode, 0, run.stderr)
            emitted = self.run_export(package, '--emit')
            self.assertEqual(emitted.returncode, 0, emitted.stderr)
            self.assertEqual(json.loads(emitted.stdout), V.read(HERE/'RESULT.json'))
            self.assertEqual(files(root), before)
            # Catalogue/selected bytes are historical Git provenance, not live inputs.
            manifest = V.read(HERE/'SOURCES.json')
            for row in manifest['files']:
                if row['usage'] == 'provenance':
                    (root/row['path']).write_text('new unrelated provenance revision\n')
            run = self.run_export(package)
            self.assertEqual(run.returncode, 0, run.stderr)

    def test_source_and_missing_receipt_fail(self):
        with tempfile.TemporaryDirectory() as td:
            package = self.export(Path(td))
            source = package/'source/PR2613-PROOF.md'
            raw = source.read_bytes()
            source.write_bytes(raw+b'\n')
            run = self.run_export(package)
            self.assertNotEqual(run.returncode, 0)
            self.assertIn('source SHA256', run.stderr)
            source.write_bytes(raw)
            (package/'RESULT.json').unlink()
            run = self.run_export(package)
            self.assertNotEqual(run.returncode, 0)
            self.assertIn('FileNotFoundError', run.stderr)

    def test_typed_and_semantic_receipt_fail(self):
        with tempfile.TemporaryDirectory() as td:
            package = self.export(Path(td))
            for field, value in [('schema_version', True), ('full_word', {})]:
                result = V.read(HERE/'RESULT.json')
                result[field] = value
                (package/'RESULT.json').write_text(json.dumps(result))
                run = self.run_export(package)
                self.assertNotEqual(run.returncode, 0)
                self.assertIn('typed result differs', run.stderr)
            (package/'RESULT.json').write_text('{"schema_version":1,"schema_version":1}')
            run = self.run_export(package)
            self.assertNotEqual(run.returncode, 0)
            self.assertIn('duplicate JSON key', run.stderr)


if __name__ == '__main__':
    unittest.main()
