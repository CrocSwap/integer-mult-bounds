"""Fail-closed controls for public paired-cube verifiers.

Apache-2.0; maintainer integration with OpenAI Codex assistance.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class PairedCubeEntrypoints(unittest.TestCase):
    def test_optimized_interpreters_cannot_write_certificates(self):
        modes = [(['-O'], None), (['-OO'], None), ([], '1'), ([], '2')]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)/'certificate.json'
            for name in ('paired_cube_producer.py', 'paired_cube_bit.py', 'paired_cube_network.py'):
                for flags, setting in modes:
                    with self.subTest(script=name, flags=flags, environment=setting):
                        env = dict(os.environ)
                        env.pop('PYTHONOPTIMIZE', None)
                        if setting:
                            env['PYTHONOPTIMIZE'] = setting
                        result = subprocess.run(
                            [sys.executable, *flags, str(ROOT/'scripts'/name), '--output', str(output)],
                            cwd=ROOT, env=env, text=True, capture_output=True)
                        self.assertNotEqual(result.returncode, 0)
                        self.assertFalse(output.exists())
                        self.assertTrue('Assertions must remain enabled' in result.stderr
                                        or 'Run without -O' in result.stderr, result.stderr)

    def test_normal_bit_help(self):
        env = dict(os.environ)
        env.pop('PYTHONOPTIMIZE', None)
        result = subprocess.run([sys.executable, str(ROOT/'scripts/paired_cube_bit.py'), '--help'],
                                cwd=ROOT, env=env, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('--input', result.stdout)


if __name__ == '__main__':
    unittest.main()
