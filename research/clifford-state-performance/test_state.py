"""Differential exact states, algebraic controls and complete helper replay."""
import copy
import gzip
import hashlib
import json
from pathlib import Path
import random
import runpy
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from common import HERE, ROOT, SOURCE, fixture_runs, load_clifford, verify_sources
import fast_state as fast


class StateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        verify_sources()
        cls.c = load_clifford()

    def setUp(self):
        fast.clear_caches()

    def test_gate_tables(self):
        rng = random.Random(86)
        for n in range(1, 10):
            for _ in range(10):
                rows = tuple(rng.randrange(1 << n) for _ in range(n))
                linear = tuple(rng.randrange(4) for _ in range(n))
                self.assertEqual(fast.permutation_table(n, rows),
                                 tuple(self.c.mv(rows, x) for x in range(1 << n)))
                self.assertEqual(fast.phase_table(n, rows, linear),
                                 tuple(self.c.qvalue(rows, linear, x, n)
                                       for x in range(1 << n)))
        self.assertLessEqual(fast.permutation_table.cache_info().currsize, 64)
        self.assertLessEqual(fast.phase_table.cache_info().currsize, 64)

    def test_seeded_valid_circuit_prefixes(self):
        rng = random.Random(86)
        comparisons = 0
        for n in range(1, 10):
            for _ in range(6):
                op = self.c.ident(n)
                for step in range(15):
                    kind = step % 5
                    if kind == 0:
                        rows = [1 << i for i in range(n)]
                        for _ in range(2*n):
                            a, b = rng.randrange(n), rng.randrange(n)
                            if a != b:
                                rows[a] ^= rows[b]
                        gate = self.c.perm(n, tuple(rows))
                    elif kind == 1:
                        rows = [0] * n
                        for i in range(n):
                            for j in range(i, n):
                                if rng.randrange(2):
                                    rows[i] |= 1 << j
                                    rows[j] |= 1 << i
                        linear = [(rows[i] >> i & 1) + 2*rng.randrange(2)
                                  for i in range(n)]
                        gate = self.c.diag(n, tuple(rows), tuple(linear))
                    elif kind == 2:
                        gate = self.c.xgate(n, rng.randrange(1 << n))
                    elif kind == 3:
                        gate = self.c.cgate(n, rng.randrange(1, 1 << n),
                                           rng.choice((-1, 1)))
                    else:
                        gate = self.c.Op(n, self.c.identity(n),
                                         [('phase', rng.randrange(-4, 8))])
                    op = op.then(gate)
                    bases = (range(1 << n) if n <= 4 else
                             [0, (1 << n)-1, rng.randrange(1 << n)])
                    for basis in bases:
                        self.assertEqual(fast.zero_state(op, basis), op.zero_state(basis))
                        comparisons += 1
                adjoint = op.adjoint()
                self.assertEqual(fast.zero_state(adjoint), adjoint.zero_state())
                inverse = op.then(adjoint)
                self.assertEqual(fast.zero_state(inverse), self.c.ident(n).zero_state())
        print('Exact seeded prefix comparisons:', comparisons)

    def test_phase_and_reduction_controls(self):
        for n in range(1, 6):
            for basis in range(1 << n):
                op = self.c.fourier(n)
                phased = op.then(self.c.Op(n, self.c.identity(n), [('phase', 1)]))
                self.assertNotEqual(fast.zero_state(op, basis), fast.zero_state(phased, basis))
                self.assertEqual(fast.zero_state(phased, basis), phased.zero_state(basis))
                inverse = op.then(op.adjoint())
                expected = ([(int(x == basis), 0) for x in range(1 << n)], 0)
                self.assertEqual(fast.zero_state(inverse, basis), expected)
        empty = self.c.ident(0)
        self.assertEqual(fast.zero_state(empty), ([(1, 0)], 0))
        unknown = self.c.Op(1, self.c.identity(1), [('unknown',)])
        for evaluator in (fast.zero_state, self.c.Op.zero_state):
            with self.assertRaises(AssertionError):
                evaluator(unknown)

    def test_every_state_in_full_helper_replay(self):
        reference = self.c.Op.zero_state
        calls = []

        def differential(op, basis=0):
            expected = reference(op, basis)
            actual = fast.zero_state(op, basis)
            self.assertEqual(actual, expected)
            calls.append((op.n, len(op.circuit)))
            return actual

        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'receipt.json'
            script = ROOT / SOURCE['checker']
            argv = [str(script), *map(str, fixture_runs()), '--entering', '36',
                    '--cold', '22', '--out', str(out)]
            with patch.object(self.c.Op, 'zero_state', differential), \
                    patch.object(sys, 'argv', argv), \
                    patch.object(sys, 'path', [str(script.parent), *sys.path]):
                runpy.run_path(str(script), run_name='__main__')
            self.assertEqual(hashlib.sha256(out.read_bytes()).hexdigest(),
                             SOURCE['expected_receipt_sha256'])
            receipt = json.loads(out.read_text())
            self.assertEqual(sum(i['phase_mutations_rejected']
                                 for i in receipt['instances']), 68)
        self.assertEqual(len(calls), 204)
        print('Exact full-replay state comparisons:', len(calls))

    def test_adapter_refusals(self):
        # A fresh source tree with one changed byte must fail before execution.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = next(iter(SOURCE['files']))
            p = root / first
            p.parent.mkdir(parents=True)
            p.write_bytes((ROOT / first).read_bytes() + b'\n')
            with self.assertRaisesRegex(ValueError, 'Pinned source changed'):
                verify_sources(root)
            out = root / 'receipt.json'
            command = [sys.executable, '-B', str(HERE / 'run.py'),
                       '--engine', 'fast', '--out', str(out)]
            bad = subprocess.run([command[0], '-O', *command[1:]],
                                 capture_output=True, text=True)
            self.assertNotEqual(bad.returncode, 0)
            self.assertIn('Assertions must remain enabled', bad.stderr)
            self.assertFalse(out.exists())
            out.write_text('preserve this file')
            bad = subprocess.run(command, capture_output=True, text=True)
            self.assertNotEqual(bad.returncode, 0)
            self.assertIn('Use a fresh output file', bad.stderr)
            self.assertEqual(out.read_text(), 'preserve this file')

    def test_changed_artifacts_fail_in_both_engines(self):
        source = fixture_runs()[0]
        word = json.loads(gzip.decompress((source / 'CANONICAL-WORD.json.gz').read_bytes()))
        adapters = json.loads((source / 'RESIDUAL-ADAPTERS.json').read_text())
        helper = next(r for r in range(2*word['v'], len(word['start']))
                      if word['final'][r] != 1)
        key = f"{word['start'][helper]}:{word['final'][helper]}"
        for mutation in ('phase', 'rank', 'last_frame', 'cleanup_touch'):
            bad_word, bad_adapters = copy.deepcopy(word), copy.deepcopy(adapters)
            if mutation == 'phase':
                recipe = bad_adapters['recipes'][key]['left']
                recipe['phase'] = (recipe['phase'] + 1) % 4
                message = 'Exact wrapper identity fails'
            elif mutation == 'rank':
                bad_adapters['recipes'][key]['rank'] += 1
                message = 'Wrong cold width'
            elif mutation == 'last_frame':
                bad_word['final'][helper] = 0
                message = 'Last tail frame differs from terminal frame'
            else:
                bad_word['cleanup'].append(['scale', helper, -1, 1,
                                            word['final'][helper]])
                message = 'Cleanup touches an early-ended helper'
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as tmp:
                directory = Path(tmp)
                (directory / 'CANONICAL-WORD.json.gz').write_bytes(
                    gzip.compress(json.dumps(bad_word).encode()))
                (directory / 'RESIDUAL-ADAPTERS.json').write_text(json.dumps(bad_adapters))
                for engine in ('reference', 'fast'):
                    out = directory / f'{engine}.json'
                    command = [sys.executable, '-B', str(HERE / 'run.py'),
                               '--engine', engine, '--runs', str(directory),
                               str(fixture_runs()[1]), '--out', str(out)]
                    bad = subprocess.run(command, capture_output=True, text=True)
                    self.assertNotEqual(bad.returncode, 0)
                    self.assertIn(message, bad.stderr)
                    self.assertFalse(out.exists())


if __name__ == '__main__':
    unittest.main(verbosity=2)
