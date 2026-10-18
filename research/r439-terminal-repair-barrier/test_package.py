#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent frame oracle, finite legal-suffix fixture and real corruption tests.

Arham Tahir, with substantial OpenAI Codex assistance.
"""
from collections import deque
import gzip
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location('terminal_repair', HERE / 'verify.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


def legal_fixture(promote_target=False):
    # Frames: zero, Q*e1, Q*e2, Q^2. Wire0=target, wire1=helper,
    # wire2=independent dirty extra. This exhausts the finite fixture's
    # complete reachable states, rather than imposing a word-length cutoff.
    frames = [frozenset(), frozenset({0}), frozenset({1}), frozenset({0, 1})]
    end = (3 if promote_target else 1, 3, 3)
    initial = ((1, 3, 0), (1, 2, 4))
    seen, todo = {initial}, deque([initial])
    helper_reaches_target = False
    goal_reached = False
    while todo:
        current, rows = todo.popleft()
        helper_reaches_target |= bool(rows[0] & 2)
        goal_reached |= rows == (3, 2, 4)
        for d in range(3):
            for s in range(3):
                if d == s:
                    continue
                for f, space in enumerate(frames):
                    if not all(frames[current[r]] <= space <= frames[end[r]] for r in (d, s)):
                        continue
                    changed_frames, changed_rows = list(current), list(rows)
                    changed_frames[d] = changed_frames[s] = f
                    changed_rows[d] ^= changed_rows[s]
                    state = (tuple(changed_frames), tuple(changed_rows))
                    if state not in seen:
                        seen.add(state)
                        todo.append(state)
    return len(seen), helper_reaches_target, goal_reached


class Tests(unittest.TestCase):
    def test_independent_hyperplane_oracle(self):
        # Dot products with the named target normal, no rational elimination.
        receipt = json.loads((HERE / 'CERTIFICATE.json').read_text())
        for result in receipt['words']:
            w = json.loads(gzip.decompress((ROOT / v.WORDS[result['name']]).read_bytes()))
            for t in range(w['v'], 2*w['v']):
                normal = w['lines'][t-w['v']]
                cache = {}
                for f in set(w['final']):
                    cache[f] = all(sum(a*b for a, b in zip(w['lines'][i], normal)) == 0 for i in w['frames'][f])
                actual = [r for r, f in enumerate(w['final']) if cache[f]]
                self.assertEqual(actual, [t])
                self.assertEqual(actual, result['target_cones'][str(t)])

    def test_complete_finite_suffix_fixture(self):
        count, reaches, goal = legal_fixture()
        self.assertGreater(count, 1)
        self.assertFalse(reaches)
        self.assertFalse(goal)
        count2, reaches2, goal2 = legal_fixture(True)
        self.assertGreater(count2, count)
        self.assertTrue(reaches2)
        self.assertTrue(goal2)

    def test_sharp_scalar_repair_dense_dirty_inputs(self):
        for sources in ([0], [0, 1]):
            for targets in ([2, 3], [2, 3, 4], [2, 3, 4, 5]):
                gates = v.repair(targets, sources)
                for value in range(1 << 7):
                    bits = [bool(value >> r & 1) for r in range(7)]
                    expected = list(bits)
                    parity = sum(bits[s] for s in sources) % 2
                    for t in targets:
                        expected[t] ^= bool(parity)
                    for _, d, s in gates:
                        bits[d] ^= bits[s]
                    self.assertEqual(bits, expected)

    def test_real_input_and_inventory_corruptions(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for path in v.INPUTS:
                out = root / path
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_bytes((ROOT / path).read_bytes())
            v.pins(root)
            path = root / v.BASELINE
            original = path.read_bytes()
            path.write_bytes(original + b'\0')
            with self.assertRaisesRegex(ValueError, 'source hash'):
                v.pins(root)
            path.write_bytes(original)
            v.pins(root)
            path.unlink()
            with self.assertRaises(FileNotFoundError):
                v.pins(root)

    def test_optimized_minimal_readonly_export_and_receipt_corruption(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            package = root / 'research/r439-terminal-repair-barrier'
            package.mkdir(parents=True)
            for name in ('verify.py', 'SOURCES.json', 'CERTIFICATE.json'):
                shutil.copyfile(HERE / name, package / name)
            for path in v.INPUTS:
                out = root / path
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_bytes((ROOT / path).read_bytes())
            snapshot = {p.relative_to(root): p.read_bytes() for p in root.rglob('*') if p.is_file()}
            command = [sys.executable, '-I', '-O', '-B', str(package / 'verify.py'), '--source-root', str(root)]
            good = subprocess.run(command, capture_output=True, text=True, timeout=240)
            self.assertEqual(good.returncode, 0, good.stderr)
            self.assertIn('PASS_R439_TERMINAL_REPAIR_BARRIER', good.stdout)
            after = {p.relative_to(root): p.read_bytes() for p in root.rglob('*') if p.is_file()}
            self.assertEqual(snapshot, after)
            path = package / 'CERTIFICATE.json'
            receipt = json.loads(path.read_text())
            receipt['words'][0]['relaxed_repairs'][0]['repair_minimum_XORs_without_frames'] -= 1
            path.write_text(json.dumps(receipt))
            bad = subprocess.run(command, capture_output=True, text=True, timeout=240)
            self.assertNotEqual(bad.returncode, 0)
            self.assertIn('certificate mismatch', bad.stderr)


if __name__ == '__main__':
    unittest.main()
