import subprocess
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

from reproduce import accepted


class AcceptanceTests(unittest.TestCase):
    def test_exact_success(self):
        self.assertTrue(accepted(subprocess.CompletedProcess([], 0, 'c VERIFIED\n', ''),
                                 'c VERIFIED'))

    def test_exit_status_and_exact_line_required(self):
        for status, output in [(1, 'c VERIFIED\n'), (0, 'c NOT VERIFIED\n'),
                               (0, 'prefix c VERIFIED\n'), (0, '')]:
            self.assertFalse(accepted(subprocess.CompletedProcess([], status, output, ''),
                                      'c VERIFIED'))

    def test_cli_rejects_source_corruption_in_both_modes(self):
        root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory() as directory:
            stage = Path(directory)
            for name in ['reproduce.py', 'checks.py', 'SOURCES.json']:
                shutil.copyfile(root / name, stage / name)
            shutil.copytree(root / 'vendor', stage / 'vendor',
                            ignore=shutil.ignore_patterns('__pycache__'))
            with (stage / 'vendor/search_sat.py').open('a') as stream:
                stream.write('\n# deliberately corrupted source pin\n')
            for flags in [[], ['-O']]:
                result = subprocess.run([sys.executable, *flags, '-B',
                                         str(stage / 'reproduce.py')],
                                        capture_output=True, text=True, timeout=20)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, '')
                self.assertIn('source pin mismatch', result.stderr)


if __name__ == '__main__':
    unittest.main()
