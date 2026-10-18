#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Ross Richardson, with substantial OpenAI Codex assistance.
"""Semantic premise controls, actual corruption, optimized relocation."""
import copy
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


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


V, O = load('verify'), load('oracle')


class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cert = json.loads((HERE / 'CERTIFICATE.json').read_text())
        cls.inputs = V.pinned()
        cls.words = O.source_words()

    def test_primary_and_separate_geometry(self):
        self.assertEqual(V.canonical(V.compute(self.inputs)), V.canonical(self.cert))
        receipt = O.check_blocks(self.cert, self.words)
        self.assertEqual(receipt['block_truth_inputs'], 61440)
        self.assertEqual(receipt['dirty_workspace_truth_inputs'], 122880)
        self.assertEqual(receipt['gram_witnesses'], 228)
        self.assertEqual(receipt['dirty_echo_extra_climbs_per_block'], {'4': 1})

    def test_common_frame_and_monotonicity_are_material(self):
        # target 1 ^= source 0; source's forward row is unchanged, but its
        # inverse column includes high-labelled initial target 1.
        cnot = tuple(x ^ ((x & 1) << 1) for x in range(4))
        O.frame_obligations(cnot, [1, 2], [3, 3])
        with self.assertRaisesRegex(ValueError, 'semantic frame'):
            O.frame_obligations(cnot, [1, 2], [1, 3])  # destination-only promotion
        with self.assertRaisesRegex(ValueError, 'semantic frame'):
            O.frame_obligations(tuple(range(4)), [3, 2], [1, 2])  # frame descent

    def test_clean_workspace_is_not_dirty_workspace(self):
        # z ^= x at low frame, then y ^= z at high frame. The requested
        # original CNOT holds for z=0 but fails for every z=1.
        circuit = []
        for state in range(8):
            x, y, z = state & 1, (state >> 1) & 1, state >> 2
            z ^= x
            y ^= z
            circuit.append(x | (y << 1) | (z << 2))
        cnot = tuple(x ^ ((x & 1) << 1) for x in range(4))
        self.assertTrue(all(circuit[x] % 4 == cnot[x] for x in range(4)))
        with self.assertRaisesRegex(ValueError, 'dirty original endpoint'):
            O.original_contract(circuit, cnot)

    def test_nonlinearity_and_reversibility_controls(self):
        toffoli = tuple(x ^ (((x & 1) & ((x >> 1) & 1)) << 2) for x in range(8))
        self.assertTrue(all(toffoli[x] == x for x in (0, 1, 2, 4)))
        with self.assertRaisesRegex(ValueError, 'dirty original endpoint'):
            O.original_contract(toffoli, tuple(range(8)))
        # Overwriting a dirty auxiliary with zero is not allowed garbage.
        with self.assertRaisesRegex(ValueError, 'not a permutation'):
            O.original_contract(tuple(x & 3 for x in range(8)), tuple(range(4)))

    def test_semantic_input_damage(self):
        damaged = copy.deepcopy(self.inputs)
        word = damaged[V.WORDS[0]]
        index = next(i for i, g in enumerate(word['B']) if g[0] == 508)
        word['B'][index][2][0] = word['B'][index][1]
        with self.assertRaises(ValueError):
            V.compute(damaged)
        changed = copy.deepcopy(self.inputs)
        changed[V.WORDS[0]]['C'].pop()
        with self.assertRaises(ValueError):
            V.compute(changed)

    def test_on_disk_certificate_corruption_both_engines(self):
        variants = []
        c = copy.deepcopy(self.cert)
        c['blocks'][3]['inverse_rows'][0] ^= 1
        variants.append(c)
        c = copy.deepcopy(self.cert)
        c['blocks'][3]['obligations'][0]['inverse_outputs'].remove(466)
        variants.append(c)
        c = copy.deepcopy(self.cert)
        c['blocks'][0]['obligations'][0]['witness'][1] = c['blocks'][0]['obligations'][0]['witness'][0]
        variants.append(c)
        c = copy.deepcopy(self.cert)
        c['blocks'][0]['entry_ranks'][0] -= 1
        variants.append(c)
        c = copy.deepcopy(self.cert)
        c['minimum_original_climbs']['2'] -= 1
        variants.append(c)
        c = copy.deepcopy(self.cert)
        c['blocks'][3]['obligations'][0]['forced_rank'] = 3
        variants.append(c)
        with tempfile.TemporaryDirectory(prefix='r439-frame-corrupt-') as tmp:
            package = Path(tmp) / 'research' / HERE.name
            shutil.copytree(HERE, package, ignore=shutil.ignore_patterns('__pycache__'))
            for damaged in variants:
                (package / 'CERTIFICATE.json').write_text(json.dumps(damaged))
                for engine in ('verify.py', 'oracle.py'):
                    done = subprocess.run([sys.executable, '-I', '-O', '-B', str(package / engine),
                                           '--root', str(ROOT)], capture_output=True, text=True, timeout=60)
                    self.assertNotEqual(done.returncode, 0, (engine, done.stdout))
                    self.assertIn('ValueError', done.stderr)

    def test_relocated_read_only_and_source_corruption(self):
        with tempfile.TemporaryDirectory(prefix='r439-frame-relocate-') as tmp:
            root = Path(tmp)
            package = root / 'research' / HERE.name
            shutil.copytree(HERE, package, ignore=shutil.ignore_patterns('__pycache__'))
            for pin in json.loads((HERE / 'SOURCES.json').read_text())['files']:
                if pin['usage'] == 'input':
                    dest = root / pin['path']
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(ROOT / pin['path'], dest)
            before = {p.relative_to(root): p.read_bytes() for p in root.rglob('*') if p.is_file()}
            for engine in ('verify.py', 'oracle.py'):
                done = subprocess.run([sys.executable, '-I', '-O', '-B', str(package / engine)],
                                      cwd=tmp, capture_output=True, text=True, timeout=60)
                self.assertEqual(done.returncode, 0, done.stderr)
            after = {p.relative_to(root): p.read_bytes() for p in root.rglob('*') if p.is_file()}
            self.assertEqual(before, after)
            archive = root / V.WORDS[0]
            raw = archive.read_bytes()
            archive.write_bytes(bytes([raw[0] ^ 1]) + raw[1:])
            for engine in ('verify.py', 'oracle.py'):
                done = subprocess.run([sys.executable, '-I', '-O', '-B', str(package / engine)],
                                      cwd=tmp, capture_output=True, text=True, timeout=60)
                self.assertNotEqual(done.returncode, 0)
                self.assertIn('source SHA256', done.stderr)


if __name__ == '__main__':
    unittest.main(verbosity=2)
