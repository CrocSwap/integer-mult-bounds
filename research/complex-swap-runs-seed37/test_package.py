"""Boundary, corruption and relocation checks. ToikY/Codex, Apache-2.0."""
import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import compiler
import independent_checker as independent
import verify


class PackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lower = staticmethod(verify.sources())

    def test_mathematical_controls(self):
        result = verify.controls(self.lower)
        self.assertEqual(len(result['rejected']), 8)
        self.assertEqual(len(result['independent_block_controls']['rejected']), 5)

    def test_actual_materialization_copy_deletions(self):
        rejected = 0
        for provider in ('ck', 'jp8'):
            programs = verify.read(verify.ROOT / verify.PROVIDERS / provider / 'LOCAL-PROGRAMS.json.gz')
            for events in programs.values():
                for block in compiler.compile_program(events, self.lower):
                    if not block['swap_starts']:
                        continue
                    locations = {tuple(a): tuple(b) for a, b in block['permutation']}
                    tail, _ = compiler.materialize(locations)
                    begin = len(block['primitives']) - len(tail)
                    for k, op in enumerate(tail):
                        if op[0] != 'copy':
                            continue
                        bad = block['primitives'][:begin + k] + block['primitives'][begin + k + 1:]
                        with self.assertRaises(ValueError):
                            independent.check_block(events, block['start'], block['end'], bad)
                        rejected += 1
        self.assertEqual(rejected, 728)

    def test_copy_remapping_and_barriers(self):
        a, b, c = ['L', 0], ['L', 1], ['L', 2]
        swap = [['scalar', ['add', a, b, 1, 1], 3], ['scalar', ['add', b, a, -1, 1], 3],
                ['scalar', ['add', a, b, 1, 1], 3], ['scalar', ['scale', b, -1, 1], 3]]
        events = swap + [['scalar', ['copy', c, a], 3]] + swap
        block = compiler.compile_block(events, 0, len(events), self.lower)
        independent.check_block(events, 0, len(events), block['primitives'])
        bad = copy.deepcopy(swap)
        bad[-1][1][1] = a
        self.assertIsNone(compiler.swapped_pair(bad, 0))
        for barrier in (['phase', 'boundary'], ['climb', 0, 0, 1, 0, 1]):
            split = swap + [barrier] + swap
            self.assertEqual(len(compiler.scalar_runs(split)), 2)
        with self.assertRaises(ValueError):
            compiler.compile_block(swap + [['phase', 'stop']], 0, 5, self.lower)

    def test_known_zero_clear_elision_starts_dirty(self):
        w = compiler.WORK
        word = [('clear', w), ('clear', w), ('copy', w, ('L', 0)), ('clear', w), ('clear', w)]
        actual, zero = verify.clear_elision(word)
        self.assertEqual(actual, [word[0], word[2], word[3]])
        self.assertTrue(zero)
        # Arbitrary incoming W must be erased, even for identity permutations.
        self.assertEqual(compiler.materialize({('L', 0): ('L', 0)})[0], [('clear', w)])

    def test_source_inventory_and_typed_receipt(self):
        expected = verify.read(HERE / 'EXPECTED.json')
        wrong = copy.deepcopy(expected)
        wrong['assignment_seed'] = 37.0
        self.assertNotEqual(verify.canonical(expected), verify.canonical(wrong))
        wrong = copy.deepcopy(expected)
        wrong['programs']['ck/forward']['receipts']['deferred']['real_primitives'] -= 2
        self.assertNotEqual(verify.canonical(expected), verify.canonical(wrong))
        pins = verify.read(HERE / 'SOURCES.json')
        self.assertEqual(set(pins['files']), set(verify.INPUTS))
        with tempfile.TemporaryDirectory(prefix='source corruption ') as folder:
            closure = Path(folder)
            for path in pins['files']:
                target = closure / path
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(verify.ROOT / path, target)
            path = closure / verify.LOWER_PATH
            path.write_bytes(path.read_bytes() + b'\n# source drift\n')
            with self.assertRaisesRegex(ValueError, 'source SHA256'):
                verify.sources(closure)

    def test_complete_optimized_minimal_relocation_and_output_preservation(self):
        with tempfile.TemporaryDirectory(prefix='deferred swaps offline ') as folder:
            closure = Path(folder) / 'checkout with spaces'
            package = closure / 'research/complex-swap-runs-seed37'
            shutil.copytree(HERE, package)
            for path in verify.INPUTS:
                target = closure / path
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(verify.ROOT / path, target)
            output = Path(folder) / 'receipt.json'
            command = [sys.executable, '-I', '-O', '-B', str(package / 'verify.py'), '--output', str(output)]
            completed = subprocess.run(command, cwd=folder, capture_output=True, text=True, timeout=240)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertIn('PASS_DEFERRED_SWAP_SCALAR', completed.stdout)
            self.assertEqual(output.read_bytes(), (package / 'EXPECTED.json').read_bytes())
            # Source corruption fails before trying to write an existing result.
            source = closure / verify.LOWER_PATH
            source.write_bytes(source.read_bytes() + b'\n# bad source\n')
            prior = output.read_bytes()
            failed = subprocess.run(command, cwd=folder, capture_output=True, text=True, timeout=20)
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn('source SHA256', failed.stderr)
            self.assertEqual(output.read_bytes(), prior)


if __name__ == '__main__':
    unittest.main(verbosity=2)
