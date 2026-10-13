#!/usr/bin/env python3
"""Packaging and evidence-integrity controls; Apache-2.0, substantial Codex assistance."""
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


class PackageTests(unittest.TestCase):
    def run_verify(self, root, *arguments, optimize=False, env=None):
        command = [sys.executable, '-I', '-B']
        if optimize:
            command.append('-O')
        command.extend([str(root / 'research/r439-frame506-two-factor/verify.py'), *arguments])
        return subprocess.run(command, text=True, capture_output=True, env=env)

    def miniature(self, directory):
        root = Path(directory)
        shutil.copytree(HERE, root / 'research/r439-frame506-two-factor')
        for relative in json.loads((HERE / 'SOURCES.json').read_text())['sha256']:
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / relative, target)
        return root

    def test_optimized_and_environment_replay(self):
        environment = dict(os.environ, PYTHONOPTIMIZE='2')
        result = self.run_verify(ROOT, optimize=True, env=environment)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('ADDs=24305->24295', result.stdout)

    def test_minimal_relocation(self):
        with tempfile.TemporaryDirectory(prefix='frame506-relocation-') as directory:
            result = self.run_verify(self.miniature(directory))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('PASS_R439_FRAME506', result.stdout)

    def test_corrupt_source_preserves_certificate(self):
        with tempfile.TemporaryDirectory(prefix='frame506-pin-') as directory:
            root = self.miniature(directory)
            certificate = root / 'research/r439-frame506-two-factor/CERTIFICATE.json'
            before = certificate.read_bytes()
            path = root / 'research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz'
            path.write_bytes(path.read_bytes() + b'corrupt')
            result = self.run_verify(root, '--write-certificate')
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('source mismatch', result.stderr)
            self.assertEqual(certificate.read_bytes(), before)

    def test_factor_word_binding_rejects(self):
        with tempfile.TemporaryDirectory(prefix='frame506-binding-') as directory:
            root = self.miniature(directory)
            path = root / 'research/r439-frame506-two-factor/CANDIDATE.json'
            recipe = json.loads(path.read_text())
            recipe['candidate_gates'][0][2] = [6]
            path.write_text(json.dumps(recipe))
            result = self.run_verify(root, '--write-certificate')
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('candidate gates differ from independently checked factors', result.stderr)


if __name__ == '__main__':
    unittest.main()
