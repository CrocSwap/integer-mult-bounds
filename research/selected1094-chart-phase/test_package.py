#!/usr/bin/env python3
"""Semantic failure controls and actual optimized subprocess checks.
Gareth Davidson, with OpenAI Codex assistance. Apache-2.0.
"""
import itertools
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import algebra as a
import verify as v


def dense_column(axes, ambient, column, sign=1):
    state = [(0, 0)] * (1 << ambient)
    state[column] = (1, 0)
    for q in axes:
        old = state
        state = []
        for x in range(1 << ambient):
            ar, ai = old[x]
            br, bi = old[x ^ q]
            state.append((ar-sign*ai+br+sign*bi, ai+sign*ar+bi-sign*br))
    return state


class Tests(unittest.TestCase):
    def test_every_column_and_spectator_fiber(self):
        good, bad = (1, 2, 4, 8), (14, 13, 11, 7)
        changed = 0
        for x in range(64):
            expected = dense_column(good, 6, x)
            actual = dense_column(bad, 6, x)
            kernel = a.convolution(good)
            for y in range(64):
                self.assertEqual(expected[y], kernel.get(x ^ y, (0, 0)))
                multiplier = -1 if ((x ^ y) & 15).bit_count() & 1 else 1
                self.assertEqual(actual[y], tuple(multiplier*t for t in expected[y]))
                if expected[y] != (0, 0):
                    self.assertEqual(x >> 4, y >> 4)
                changed += expected[y] != actual[y]
        self.assertEqual(changed, 512)

    def test_inverse_and_square(self):
        for axes in ((1, 2, 4, 8), (14, 13, 11, 7)):
            forward, backward = a.convolution(axes), a.convolution(axes, -1)
            inverse, square = {}, {}
            for x, p in forward.items():
                for y, q in backward.items():
                    u, z = a.multiply(p, q); r, s = inverse.get(x ^ y, (0, 0)); inverse[x ^ y] = (u+r, z+s)
                for y, q in forward.items():
                    u, z = a.multiply(p, q); r, s = square.get(x ^ y, (0, 0)); square[x ^ y] = (u+r, z+s)
            self.assertEqual({x:p for x,p in inverse.items() if p != (0,0)}, {0:(256,0)})
            self.assertEqual({x:p for x,p in square.items() if p != (0,0)}, {15:(256,0)})

    def test_low_dimension_exhaustion(self):
        # A different enumerator tries every tuple, without orthogonal-prefix pruning.
        for n in range(1, 5):
            brute = set()
            for columns in itertools.product(range(1, 1 << n), repeat=n):
                if all((x & y).bit_count() % 2 == (i == j)
                       for i,x in enumerate(columns) for j,y in enumerate(columns)):
                    brute.add(columns)
            self.assertEqual(brute, set(a.orthogonal_matrices(n)))

    def test_nonpermutation_positive_and_projector_control(self):
        positive = tuple(63 ^ (1 << i) for i in range(6))
        self.assertTrue(all(q.bit_count() == 5 for q in positive))
        self.assertEqual(a.convolution(positive), a.convolution((1,2,4,8,16,32)))
        self.assertEqual(a.defect(positive), 0)
        bad = (14,13,11,7)
        self.assertEqual(a.projector(bad,4), a.projector((1,2,4,8),4))
        self.assertNotEqual(a.convolution(bad), a.convolution((1,2,4,8)))
        with self.assertRaisesRegex(ValueError, 'axis range/type'):
            a.orthonormal((True,), 1)

    def test_json_controls(self):
        for text in ('{"x":0,"x":1}', '{"x":NaN}', '{"x":Infinity}'):
            with self.assertRaises(ValueError):
                v.load_bytes(text.encode())

    def process(self, package, root, *args):
        return subprocess.run([sys.executable, '-I', '-O', '-B', str(package/'verify.py'),
                               '--source-root', str(root), *map(str,args)],
                              cwd='/tmp', text=True, capture_output=True, timeout=180)

    def test_actual_source_and_immutable_container_corruption(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            pins = [p for p in v.read(HERE/'SOURCES.json')['files'] if p['usage']=='input']
            for item in pins:
                target = root/item['path']; target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(HERE.parents[1]/item['path'],target)
            first = root/pins[0]['path']; raw = first.read_bytes(); first.write_bytes(raw+b' ')
            p = self.process(HERE,root)
            self.assertNotEqual(p.returncode,0); self.assertIn('source pin:',p.stderr)
            first.write_bytes(raw)
            archive = root/v.ARCHIVE; raw = bytearray(archive.read_bytes()); raw[4] ^= 1; archive.write_bytes(raw)
            p = self.process(HERE,root)
            self.assertNotEqual(p.returncode,0); self.assertIn('source pin:',p.stderr)

    def test_actual_receipt_corruption(self):
        with tempfile.TemporaryDirectory() as temp:
            package = Path(temp)/'package'; shutil.copytree(HERE,package)
            receipt = v.read(package/'EXPECTED.json'); receipt['selected']['kernel_coefficients_both_signs'] -= 1
            (package/'EXPECTED.json').chmod(0o644)  # Only this disposable mutant copy.
            (package/'EXPECTED.json').write_text(json.dumps(receipt))
            p = self.process(package,HERE.parents[1])
            self.assertNotEqual(p.returncode,0); self.assertIn('complete receipt mismatch',p.stderr)

    def test_occupied_outputs_are_preserved(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp)/'kept.json'; target.write_text('preserve me')
            p = self.process(HERE,HERE.parents[1],'--receipt',target)
            self.assertNotEqual(p.returncode,0); self.assertIn('receipt already exists',p.stderr)
            self.assertEqual(target.read_text(),'preserve me')
            p = self.process(HERE,HERE.parents[1],'--write-expected')
            self.assertNotEqual(p.returncode,0); self.assertIn('expected receipt already exists',p.stderr)


if __name__ == '__main__':
    unittest.main()
