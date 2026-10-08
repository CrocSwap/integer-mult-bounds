"""Independent controls for the full-size C++ boundary-rank counter."""
from collections import defaultdict
from itertools import combinations
import json
from pathlib import Path
import shutil
import random
import struct
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts/experiments'))
from ternary_target_circuit import DirectProducer
from ternary_reuse_plateaus import plateau_plan, rational_basis


class BoundaryFusion(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = shutil.which('c++')
        if compiler is None:
            raise unittest.SkipTest('C++ compiler unavailable')
        cls.tmp = tempfile.TemporaryDirectory()
        cls.exe = Path(cls.tmp.name)/'fusion'
        subprocess.run([compiler, '-std=c++17', '-O2',
                        str(ROOT/'scripts/experiments/ternary_boundary_fusion.cpp'),
                        '-o', str(cls.exe)], check=True, capture_output=True)
        cls.span_exe = Path(cls.tmp.name)/'target-spans'
        subprocess.run([compiler, '-std=c++17', '-O2',
                        str(ROOT/'scripts/experiments/ternary_target_span_classes.cpp'),
                        '-o', str(cls.span_exe)], check=True, capture_output=True)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def count(self, parents, roots, labels, v, active=None):
        n = len(parents)
        active = active if active is not None else set(range(1, n))
        dag = Path(self.tmp.name)/'dag.bin'
        classes = Path(self.tmp.name)/'classes.bin'
        with dag.open('wb') as f:
            f.write(struct.pack('<4I', 28, v, n, len(roots)))
            for a, b in parents:
                f.write(struct.pack('<2I', a, b))
            f.write(struct.pack(f'<{len(roots)}I', *roots))
            f.write(bytes(int(i in active) for i in range(n)))
        classes.write_bytes(struct.pack(f'<{n}I', *labels))
        result = subprocess.run([str(self.exe), str(dag), str(classes)],
                                check=True, capture_output=True, text=True)
        return json.loads(result.stdout)

    def test_characteristic_three_and_distinct_output_deliveries(self):
        # J-I has rational rank four and F3 rank three.
        parents = [(0, 0)]*5
        roots = []
        for excluded in range(1, 5):
            a, b, c = [i for i in range(1, 5) if i != excluded]
            parents.append((a, b))
            parents.append((len(parents)-1, c))
            roots.append(len(parents)-1)
        labels = list(range(5))+[5]*8
        result = self.count(parents, roots, labels, 4)
        self.assertEqual(result['new_roles'], 5)
        self.assertEqual(result['saving'], 7)
        self.assertEqual(result['rank_histogram'], {'3': 1})
        # A second designated use needs its own physical output slot.
        duplicated = self.count(parents, roots+[roots[0]], labels, 4)
        self.assertEqual(duplicated['new_roles'], 6)

    def test_direct_h8_matches_independent_python_boundary_matrices(self):
        c = DirectProducer(8)
        descendants = {i: 0 for i in c.active}
        for output, node in c.outputs.items():
            descendants[node] |= 1 << output
        for node in sorted(c.active, reverse=True):
            for parent in c.args[node] or ():
                descendants[parent] |= descendants[node]
        keys = {}
        labels = [0]*len(c.args)
        groups = defaultdict(list)
        for node in sorted(c.active):
            key = ('input', node) if c.args[node] is None else ('targets', descendants[node])
            cl = keys.setdefault(key, len(keys)+1)
            labels[node] = cl
            groups[cl].append(node)
        home = {node: labels[node] for node in c.active}
        plan = plateau_plan(c, {node: () for node in c.active}, dict(groups), home)
        expected = len(c.inputs)+sum(len(b['uses'])-len(b['pivots']) for b in plan)
        result = self.count([a or (0, 0) for a in c.args], list(c.outputs.values()),
                            labels, len(c.inputs), c.active)
        self.assertEqual(result['new_roles'], expected)
        self.assertEqual(result['original_roles'], c.roles)

    def test_canonical_target_classes_match_independent_rational_spans(self):
        h = 8
        masks = [3+sum(1 << j for j in t) for t in combinations(range(2, h), 3)]
        rng = random.Random(3471)
        families = [masks]+[rng.sample(masks, rng.randrange(2, len(masks))) for _ in range(40)]
        # Include a proper subset with exactly the same rational span.
        independent = []
        for mask in masks:
            rows = tuple(tuple((m >> j) & 1 for j in range(h)) for m in independent+[mask])
            if len(rational_basis(rows)) > len(independent):
                independent.append(mask)
        families.append(independent)
        z = [(h, 0, 0, 0, 0), (h, 0, 0, 1, 0)]
        unique = {}

        def family(items):
            if not items:
                return 0
            union = 0
            for mask in items:
                union |= mask
            if not union:
                return 1
            bit = union & -union
            var = bit.bit_length()-1
            lo = family([mask for mask in items if not mask & bit])
            hi = family([mask ^ bit for mask in items if mask & bit])
            key = (var, lo, hi)
            if key not in unique:
                core = z[lo][4] & z[hi][4] if lo else z[hi][4] | bit
                unique[key] = len(z)
                z.append((*key, z[lo][3]+z[hi][3], core))
            return unique[key]

        roots = [0]+[family(masks) for masks in families]
        n = len(roots)
        dag = Path(self.tmp.name)/'target-dag.bin'
        targets = Path(self.tmp.name)/'targets.bin'
        classes = Path(self.tmp.name)/'target-classes.bin'
        dag.write_bytes(struct.pack('<4I', h, 0, n, 0)+bytes(8*n)+bytes([0]+[1]*(n-1))+bytes(4*n))
        with targets.open('wb') as f:
            f.write(struct.pack('<3I', h, n, len(z)))
            for row in z:
                f.write(struct.pack('<5I', *row))
            f.write(struct.pack(f'<{n}I', *roots))
            f.write(bytes(n))
        subprocess.run([str(self.span_exe), str(dag), str(targets), str(classes)],
                       check=True, capture_output=True)
        labels = struct.unpack(f'<{n}I', classes.read_bytes())[1:]
        exact = [rational_basis(tuple(tuple((m >> j) & 1 for j in range(h)) for m in rows))
                 for rows in families]
        for i in range(len(families)):
            for j in range(len(families)):
                self.assertEqual(labels[i] == labels[j], exact[i] == exact[j])
        self.assertEqual(labels[0], labels[-1])


if __name__ == '__main__':
    unittest.main()
