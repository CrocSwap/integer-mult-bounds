"""Unit tests for the seed-93 fast exact HPE audit. Apache-2.0."""
import importlib.util
import random
import subprocess
import sys
import unittest
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


F = load('hpe_fast_test', HERE / 'hpe_audit_fast.py')
# Pairwise-era Fraction-dict reference; production PR635 path ships integer rows.
R = load('hpe_reference_test', HERE / 'baseline.py')


class RowArithmetic(unittest.TestCase):
    def test_random_programs_match_fraction_rows(self):
        rng = random.Random(93)
        for trial in range(300):
            n = rng.randrange(2, 7)
            ref = [{r: Q(1)} for r in range(n)]
            fast = F.rows_identity(n)
            for _ in range(rng.randrange(1, 60)):
                if rng.random() < 0.2:
                    e = ['scale', rng.randrange(n), rng.choice([-4, -1, 1, 2, 3, 2 ** 70]), rng.choice([1, 2, 3, 5 ** 30])]
                else:
                    t, s = rng.sample(range(n), 2)
                    e = ['add', t, s, rng.randrange(-5, 6), rng.choice([1, 2, 4, 3, 7 ** 25])]
                R.apply(e, ref)
                F.apply(e, fast)
            self.assertTrue(F.rows_equal(fast, ref))
            self.assertEqual([F.row_fractions(r) for r in fast], ref)

    def test_zero_entries_are_never_stored(self):
        rows = F.rows_identity(2)
        F.apply(['add', 0, 1, 1, 1], rows)
        F.apply(['add', 0, 1, -1, 1], rows)
        self.assertEqual(rows[0][1], {0: 1})

    def test_errors_are_the_reference_errors(self):
        for e in (['scale', 0, 0, 1], ['add', 0, 0, 1, 1], ['add', 0, 1, 1, 0], ['add', 0, 1, 'x', 1]):
            outcomes = []
            for module, rows in ((R, [{0: Q(1)}, {1: Q(1)}]), (F, F.rows_identity(2))):
                try:
                    module.apply(e, rows)
                    outcomes.append(None)
                except Exception as exc:
                    outcomes.append((type(exc), exc.args))
            self.assertEqual(outcomes[0], outcomes[1], e)


class Copies(unittest.TestCase):
    def test_copy_never_shares_nested_lists(self):
        e = ['add', 3, 4, 1, 2, [5, 6]]
        c = F._copy(e)
        self.assertEqual(c, e)
        c[-1].append(7)
        self.assertEqual(e[-1], [5, 6])

    def test_unusual_shapes_fall_back_to_deepcopy(self):
        e = ['add', 3, 4, 1, 2, [[5]]]
        c = F._copy(e)
        c[-1][0].append(1)
        self.assertEqual(e[-1], [[5]])
        self.assertEqual(F.inverse(e), R.inverse(e))
        self.assertEqual(F.dual(['scale', 1, 2, 3, None]), R.dual(['scale', 1, 2, 3, None]))


class CrosscheckControl(unittest.TestCase):
    def test_wrong_fast_audit_is_caught_not_absorbed(self):
        import gzip, os, tarfile, tempfile
        archive = HERE.parents[1] / 'research/community-frontier1042-audit/selected-replay.tar.gz'
        with tarfile.open(archive) as tar:
            data = tar.extractfile('chain/p6n/FULL-WORD.json.gz').read()
        tmp = Path(tempfile.mkdtemp())
        word = tmp / 'w.json.gz'
        word.write_bytes(data)
        os.environ.update(HPE_AUDIT_MODE='crosscheck', HPE_AUDIT_REFERENCE=str(HERE / 'baseline.py'))
        try:
            shim = load('hpe_shim_test', HERE / 'shim/hpe_audit_and_transport.py')
        finally:
            os.environ.pop('HPE_AUDIT_MODE')

        class Wrong:
            @staticmethod
            def run(raw, routing, out):
                raise AssertionError("'arbitrary-dirt endpoint'")
        shim._fast = Wrong
        with self.assertRaises(RuntimeError) as cm:
            shim.run(word, R.Path(str(HERE.parents[1] / 'research/complex-k492-owner-repair/vendor/multicold/vendor/'
                                      'pr558/vendor/pr552/complex-local/inputs/phase-baseline/CANONICAL-WORD.json.gz')),
                     tmp / 'out')
        self.assertIn('crosscheck mismatch', str(cm.exception))


class Differential(unittest.TestCase):
    def test_archived_words_and_small_fuzz(self):
        r = subprocess.run([sys.executable, '-I', '-B', str(HERE / 'verify.py'), '--fuzz', '5', '--seed', '7'],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn('PASS_HPE_AUDIT_FAST_EQUIVALENCE', r.stdout)


if __name__ == '__main__':
    unittest.main()
