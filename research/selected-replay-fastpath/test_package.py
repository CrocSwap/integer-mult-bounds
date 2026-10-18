#!/usr/bin/env python3
"""Check exact states, phase rejection and the complete compiler boundary."""
import gzip
import itertools
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import lowering
from sources import HERE, ROOT, SOURCE, engines
import sparse_state


def fixture():
    return dict(h=3, v=3, frames=[[], [1], [2], [4], [1, 2], [1, 4],
                                [2, 4], [1, 2, 4]],
                edges=[[0, 1], [1, 4], [4, 7], [7, 6], [6, 3], [3, 0]],
                center_frames=list(range(8)), ports=[1, 2, 4],
                start=[1, 2, 3, 0, 0, 0], final=[0, 0, 0, 6, 5, 4])


class ExactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c, cls.tables = engines()

    def evaluate(self, op, basis=0):
        return sparse_state.zero_state(op, self.tables, basis)

    def test_all_small_gate_inputs(self):
        # The retained scalar evaluator is the independent oracle for the update.
        count = 0
        for n in range(4):
            gates = [self.c.ident(n)]
            for rows in itertools.product(range(1 << n), repeat=n):
                if self.c.rank(rows) == n:
                    gates.append(self.c.perm(n, rows))
                if self.c.transpose(rows, n) == rows:
                    for signs in itertools.product((0, 2), repeat=n):
                        alpha = tuple((rows[i] >> i & 1) + signs[i] for i in range(n))
                        gates.append(self.c.diag(n, rows, alpha))
            for q in range(1 << n):
                gates.extend([self.c.xgate(n, q), self.c.cgate(n, q),
                              self.c.cgate(n, q, -1)])
            gates.extend(self.c.Op(n, self.c.identity(n), [('phase', p)]) for p in range(4))
            for gate in gates:
                for basis in range(1 << n):
                    self.assertEqual(self.evaluate(gate, basis), gate.zero_state(basis))
                    count += 1
        print('PASS exhaustive small gate states', count)

    def test_mixed_circuits_and_exact_cancellation(self):
        count = 0
        for n in range(1, 10):
            rows = tuple((1 << i) ^ (1 << (i+1) if i+1 < n else 0) for i in range(n))
            Q = tuple(((1 << n)-1) ^ (1 << i) for i in range(n))
            alpha = tuple(2*(i % 2) for i in range(n))
            op = self.c.ident(n)
            gates = [self.c.fourier(n), self.c.perm(n, rows), self.c.diag(n, Q, alpha),
                     self.c.xgate(n, (1 << n)-1), self.c.cgate(n, (1 << n)-1, -1),
                     self.c.Op(n, self.c.identity(n), [('phase', 3)])]
            for gate in gates + [g.adjoint() for g in reversed(gates)]:
                op = op.then(gate)
                bases = range(1 << n) if n <= 4 else (0, 1, (1 << n)-1)
                for basis in bases:
                    self.assertEqual(self.evaluate(op, basis), op.zero_state(basis))
                    count += 1
            for basis in (0, (1 << n)-1):
                expected = ([(int(x == basis), 0) for x in range(1 << n)], 0)
                self.assertEqual(self.evaluate(op, basis), expected)
        print('PASS mixed circuit states', count)

    def test_global_phase_is_not_a_tableau_check(self):
        for n in range(1, 5):
            original = self.c.fourier(n)
            _, compiled = lowering.lower_child(original, self.c, self.evaluate)
            for phase in (1, 2, 3):
                bad = compiled.then(self.c.Op(n, self.c.identity(n), [('phase', phase)]))
                self.assertEqual(original.tab, bad.tab)
                self.assertNotEqual(self.evaluate(original), self.evaluate(bad))
            malformed = self.c.Op(n, original.tab, [('unknown',)])
            for evaluate in (self.evaluate, self.c.Op.zero_state, self.tables.zero_state):
                with self.assertRaises(AssertionError):
                    evaluate(malformed)

    def test_compiler_and_corrupted_words(self):
        mutations = {
            'dependent_frame': lambda w: w['frames'].__setitem__(4, [1, 1]),
            'nonnested_edge': lambda w: w['edges'].append([1, 2]),
            'wrong_source_frame': lambda w: w['start'].__setitem__(0, 0),
            'wrong_target_frame': lambda w: w['final'].__setitem__(3, 0),
        }
        with tempfile.TemporaryDirectory(prefix='selected-phase-controls-') as tmp:
            work = Path(tmp)
            expected = None
            for name, mutate in [('valid', None), *mutations.items()]:
                word = fixture()
                if mutate:
                    mutate(word)
                path = work / (name + '.json.gz')
                path.write_bytes(gzip.compress(json.dumps(word).encode(), mtime=0))
                for engine in ('original', 'dense', 'sparse'):
                    out = work / (name + '-' + engine)
                    if engine == 'original':
                        out.mkdir()
                        shutil.copyfile(path, out / 'CANONICAL-WORD.json.gz')
                        command = [sys.executable, '-B', str(ROOT / SOURCE['original_driver']),
                                   str(out), str((ROOT / SOURCE['algebra']).parent)]
                    else:
                        command = [sys.executable, '-B', str(HERE / 'run.py'), '--engine', engine,
                                   '--word', str(path), '--out', str(out)]
                    proc = subprocess.run(command, capture_output=True, text=True)
                    if mutate:
                        self.assertNotEqual(proc.returncode, 0, (name, engine))
                        self.assertIn('AssertionError', proc.stderr, (name, engine, proc.stderr))
                        self.assertFalse((out / 'CLIFFORD-RECIPES.json').exists())
                    else:
                        self.assertEqual(proc.returncode, 0, proc.stderr)
                        actual = (out / 'CLIFFORD-RECIPES.json').read_bytes()
                        if expected is None:
                            expected = actual
                        self.assertEqual(actual, expected)
            print('PASS corrupted word controls', len(mutations) * 3)

    def test_refusals_and_relocated_source(self):
        with tempfile.TemporaryDirectory(prefix='selected-phase-package-') as tmp:
            work = Path(tmp)
            package = work / 'research/selected-replay-fastpath'
            shutil.copytree(HERE, package, ignore=shutil.ignore_patterns('__pycache__'))
            for relative in SOURCE['files']:
                target = work / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / relative, target)
            word = work / 'word.json.gz'
            word.write_bytes(gzip.compress(json.dumps(fixture()).encode(), mtime=0))
            output = work / 'output'
            command = [sys.executable, '-B', str(package / 'run.py'),
                       '--word', str(word), '--out', str(output)]
            good = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(good.returncode, 0, good.stderr)
            original = (output / 'CLIFFORD-RECIPES.json').read_bytes()
            reused = subprocess.run(command, capture_output=True, text=True)
            self.assertNotEqual(reused.returncode, 0)
            self.assertIn('Use a fresh output directory', reused.stderr)
            self.assertEqual((output / 'CLIFFORD-RECIPES.json').read_bytes(), original)
            command[-1] = str(work / 'new-output')
            optimized = subprocess.run([command[0], '-O', *command[1:]],
                                       capture_output=True, text=True)
            self.assertNotEqual(optimized.returncode, 0)
            self.assertIn('Assertions must remain enabled', optimized.stderr)
            self.assertFalse(Path(command[-1]).exists())
            source = work / SOURCE['algebra']
            source.write_bytes(source.read_bytes() + b'\n')
            changed = subprocess.run(command, capture_output=True, text=True)
            self.assertNotEqual(changed.returncode, 0)
            self.assertIn('Pinned source changed', changed.stderr)
            self.assertFalse(Path(command[-1]).exists())


if __name__ == '__main__':
    unittest.main(verbosity=2)
