"""Reject three genuine mathematical undercharges, in ordinary and optimized mode.
Produced with OpenAI GPT-6.1 Sol at high reasoning effort through Codex.
Apache-2.0.
"""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class MathematicalMutations(unittest.TestCase):
    def test_reject_changed_mathematics(self):
        source = Path(__file__).with_name('verify.py').read_text(encoding='utf-8')
        mutations = (
            ('remainder dropped', 'return q*f[b]+f[r]', 'return q*f[b]',
             'packing dynamic program'),
            ('rank undercharged', 'ar = rank(a, p)', 'ar = min(rank(a, p), 1)',
             'arbitrary coupling crossing'),
            ('wrong formal sign', 'add(eye(len(a)), a, p, -1)',
             'add(eye(len(a)), a, p, 1)', 'full formal endpoint'),
        )
        with tempfile.TemporaryDirectory() as tmp:
            script = Path(tmp)/'verify.py'
            for name, old, new, reason in mutations:
                self.assertEqual(source.count(old), 1)
                script.write_text(source.replace(old, new), encoding='utf-8')
                for options in ([], ['-O']):
                    with self.subTest(mutation=name, options=options):
                        result = subprocess.run(
                            [sys.executable, '-I', *options, '-B', str(script)],
                            capture_output=True, text=True, timeout=30,
                        )
                        self.assertNotEqual(result.returncode, 0)
                        self.assertIn('ValueError: '+reason, result.stderr)


if __name__ == '__main__':
    unittest.main()
