"""Native regression for known drat-trim issue42 and predecessor fix PR43."""
import subprocess
import tempfile
import unittest
from pathlib import Path

from reproduce import accepted

ROOT = Path(__file__).resolve().parent


class NativeCheckerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory()
        cls.temp = Path(cls.directory.name)
        for name, source in [('original', ROOT / 'vendor/drat-trim/lrat-check.c'),
                             ('corrected', ROOT / 'vendor/lrat-check-pr43.c')]:
            built = subprocess.run(['gcc', '-std=c99', '-DLONGTYPE', '-O2', str(source),
                                    '-o', str(cls.temp / name)],
                                   capture_output=True, text=True, timeout=60)
            if built.returncode:
                raise RuntimeError(built.stderr)
        (cls.temp / 'sat.cnf').write_text('p cnf 1 1\n1 0\n')
        (cls.temp / 'fake.lrat').write_text('2 0 1 0\n')
        (cls.temp / 'no-hint.lrat').write_text('2 0 0\n')
        (cls.temp / 'unsat.cnf').write_text('p cnf 2 4\n1 2 0\n1 -2 0\n-1 2 0\n-1 -2 0\n')
        (cls.temp / 'valid.lrat').write_text('5 1 0 1 2 0\n6 0 5 3 4 0\n')
        (cls.temp / 'empty.lrat').write_text('')

    @classmethod
    def tearDownClass(cls):
        cls.directory.cleanup()

    def check(self, checker, cnf, proof):
        return subprocess.run([str(self.temp / checker), str(self.temp / cnf),
                               str(self.temp / proof)],
                              capture_output=True, text=True, timeout=20)

    def test_original_false_acceptance_is_reproduced(self):
        # Known issue42, not a claim of a newly discovered vulnerability.
        self.assertTrue(accepted(self.check('original', 'sat.cnf', 'fake.lrat'), 'c VERIFIED'))

    def test_corrected_checker_rejects_fake_refutations(self):
        for proof in ['fake.lrat', 'no-hint.lrat']:
            result = self.check('corrected', 'sat.cnf', proof)
            self.assertFalse(accepted(result, 'c VERIFIED'))
            self.assertEqual(result.returncode, 1)
            self.assertIn('c NOT VERIFIED', result.stdout)

    def test_corrected_checker_accepts_valid_refutation(self):
        self.assertTrue(accepted(self.check('corrected', 'unsat.cnf', 'valid.lrat'), 'c VERIFIED'))

    def test_corrected_checker_rejects_empty_proof(self):
        self.assertFalse(accepted(self.check('corrected', 'unsat.cnf', 'empty.lrat'), 'c VERIFIED'))


if __name__ == '__main__':
    unittest.main()
