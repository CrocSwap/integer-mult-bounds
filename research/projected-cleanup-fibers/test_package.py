"""Semantic, source and output controls for the projected-cleanup result."""
import copy
import itertools
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parent))
import algebra as A
import common as C
import independent as I
import selected_word as S
import verify


class Checks(unittest.TestCase):
    def test_short_literal_relators_and_omissions(self):
        gates = [(d, s) for d in range(3) for s in range(3) if d != s]
        unit = tuple(range(8))
        for length in range(5):
            for word in itertools.product(gates, repeat=length):
                if I.evaluate(3, word) == unit:
                    for z in (1, 2):
                        self.assertEqual(I.evaluate(3, [g for g in word if g[0] < z]), unit)
        for n, z, dst, src in ((3, 2, 0, 1), (2, 1, 0, 1), (3, 1, 0, 2)):
            word = A.loop(n, z, dst, src)
            self.assertEqual(I.evaluate(n, word), tuple(range(1 << n)))
            for i in range(len(word)):
                self.assertNotEqual(I.evaluate(n, word[:i]+word[i+1:]), tuple(range(1 << n)))

    def test_complete_boundary_is_not_raw_or_projected_alone(self):
        loop = A.loop(3, 2, 0, 1)
        self.assertEqual(I.evaluate(3, loop), tuple(range(8)))
        projected = [g for g in loop if g[0] < 2]
        # The raw identity is correct without cleanup and wrong with its
        # projected inverse; a clean-donor test would miss that error.
        complete = loop+projected[::-1]
        got = I.evaluate(3, complete)
        self.assertEqual(got[0], 0)
        self.assertEqual(got[1], 1)
        self.assertEqual(got[2], 3)
        self.assertNotEqual(got, tuple(range(8)))
        self.assertEqual(A.word_matrix(3, complete), (3, 2, 4))

    def test_joint_constructor_rejects_missing_hypotheses(self):
        unit = A.identity(3)
        for raw, shadow, z in [((0, 2, 4), unit, 2), (unit, (1, 1, 4), 2),
                               (unit, (1, 2, 5), 2), (unit, unit, 0), (unit, unit, 3)]:
            with self.subTest(raw=raw, shadow=shadow, z=z):
                with self.assertRaises(ValueError):
                    A.joint_word(raw, shadow, z)
        # With no targets the projection is the entire word; the theorem's
        # product conclusion is false, not merely unsupported by the compiler.
        word = [(0, 1)]
        self.assertEqual(A.word_matrix(2, word, 2), A.word_matrix(2, word))
        with self.assertRaises(ValueError):
            A.loop(2, 2, 0, 1)

    def test_selected_dirty_witness_and_cleanup_compilation(self):
        old = C.read(C.ROOT/C.WORD)
        good, bad, _ = S.variants(old)
        n = 2*old['v']+old['R']
        base = S.row_replay(n, S.stream(old))
        self.assertEqual(S.row_replay(n, S.stream(good)), base)
        wrong = S.row_replay(n, S.stream(bad))
        self.assertEqual([i for i in range(n) if base[i] != wrong[i]], [222])
        self.assertEqual(wrong[222], (1 << 222) | (1 << 223))
        self.assertEqual(S.cleanup_rows(bad, S.projected(bad)), list(A.identity(n)))
        self.assertNotEqual(S.cleanup_rows(good, S.projected(good)), list(A.identity(n)))
        self.assertEqual(S.row_replay(n, S.stream(bad, raw=True)), S.row_replay(n, S.stream(old, raw=True)))
        # Changing one donor breaks the exact endpoint-neutral premise.
        changed = copy.deepcopy(good)
        changed['A'][0][2] = [112]
        self.assertNotEqual(S.row_replay(n, S.stream(changed, raw=True)), S.row_replay(n, S.stream(old, raw=True)))

    def test_typed_receipts_and_json(self):
        for text in ('{"x":1,"x":2}', '{"x":NaN}', '{"x":Infinity}'):
            with self.assertRaises(ValueError):
                C.decode(text)
        for wrong in (False, 1.0, 2):
            with self.assertRaises(ValueError):
                verify.compare({'count': wrong}, {'count': 1}, 'type')
        result = C.read(C.PACKAGE/'EXPECTED.json')
        bad = copy.deepcopy(result)
        bad['selected_word']['variants']['projected_cleanup']['full_boundary'] = True
        with self.assertRaisesRegex(ValueError, 'certificate mismatch'):
            verify.compare(bad, result, 'forged admission')

    def test_readonly_optimized_export_and_source_drift(self):
        with tempfile.TemporaryDirectory(prefix='cleanup-fibers-export-') as temp:
            parent = Path(temp)
            root = parent/'source'
            package = root/'research'/C.PACKAGE.name
            package.parent.mkdir(parents=True)
            shutil.copytree(C.PACKAGE, package, ignore=shutil.ignore_patterns('__pycache__'))
            for name in C.INPUTS:
                target = root/name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(C.ROOT/name, target)
            files = [p for p in root.rglob('*') if p.is_file()]
            dirs = [root]+[p for p in root.rglob('*') if p.is_dir()]
            before = {str(p.relative_to(root)): C.sha(p) for p in files}
            try:
                for p in files:
                    p.chmod(0o444)
                for p in dirs:
                    p.chmod(0o555)
                completed = subprocess.run([sys.executable, '-I', '-O', '-B', str(package/'verify.py'),
                                            '--work', str(parent/'work')], cwd='/tmp',
                                           capture_output=True, text=True, timeout=120)
                self.assertEqual(completed.returncode, 0, completed.stdout+completed.stderr)
                self.assertIn('PASS_PROJECTED_CLEANUP_FIBERS', completed.stdout)
                self.assertEqual(before, {str(p.relative_to(root)): C.sha(p) for p in files})
            finally:
                for p in dirs:
                    p.chmod(0o755)
                for p in files:
                    p.chmod(0o644)
            source = root/C.WORD
            with source.open('r+b') as handle:
                first = handle.read(1)
                handle.seek(0)
                handle.write(bytes([first[0] ^ 1]))
            rejected = subprocess.run([sys.executable, '-I', '-B', str(package/'verify.py'),
                                       '--work', str(parent/'rejected')], cwd='/tmp',
                                      capture_output=True, text=True, timeout=20)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn('source drift', rejected.stderr)
            self.assertFalse((parent/'rejected').exists())

    def test_existing_output_preserved(self):
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp)
            (out/'marker').write_text('preserve')
            with self.assertRaisesRegex(ValueError, 'already exists'):
                verify.run(out)
            self.assertEqual((out/'marker').read_text(), 'preserve')
            self.assertEqual([p.name for p in out.iterdir()], ['marker'])


if __name__ == '__main__':
    unittest.main()
