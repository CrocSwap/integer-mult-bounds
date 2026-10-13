"""Mathematical and package controls; every rejection uses the production checker."""
import copy
import gzip
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import experiment as E
import independent as I
import verify as V


class Controls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c, cls.programs, cls.checks, cls.C, cls.recipe, cls.block, cls.changed = V.build(rerun_search=False)

    def test_missing_preparation_only_helper_test_is_insufficient(self):
        missing = self.block[56:]
        actual, _ = I._run(missing, 728, False)
        # A check confined to helper inputs incorrectly accepts omitted prep.
        for t, row in self.C.items():
            numerator, power = actual[t]
            observed = {k: E.Q(x, 1 << power) for k, x in numerator.items() if k >= 224}
            self.assertEqual(observed, row)
        with self.assertRaisesRegex(RuntimeError, 'endpoint mismatch'):
            I.check_compensation(missing, self.C, 112, 728)

    def test_compensation_mutations(self):
        controls = {'omit_restore': self.block[:-56],
                    'wrong_prep_sign': copy.deepcopy(self.block),
                    'wrong_restore_sign': copy.deepcopy(self.block),
                    'dropped_coefficient': self.block[:56]+self.block[57:],
                    'wrong_coefficient': copy.deepcopy(self.block),
                    'dirty_helper_write': self.block+[E.add(224, 112, 1)]}
        controls['wrong_prep_sign'][0][3] *= -1
        controls['wrong_restore_sign'][-1][3] *= -1
        controls['wrong_coefficient'][56][3] *= 2
        for label, block in controls.items():
            with self.subTest(label=label), self.assertRaisesRegex(RuntimeError, 'endpoint mismatch'):
                I.check_compensation(block, self.C, 112, 728)

    def test_complete_program_detects_missing_restore_in_both_orientations(self):
        program = E.logical_program(self.c, self.block[:-56])
        for back in (False, True):
            with self.subTest(back=back), self.assertRaisesRegex(RuntimeError, 'endpoint mismatch'):
                I.check(program, 728, dual=back)

    def test_private_stream_clears_are_paid_and_required(self):
        original = E.lower
        for omitted in ('first', 'last'):
            def broken(scalar):
                result = original(scalar)
                if scalar[0] == 'add':
                    return result[1:] if omitted == 'first' else result[:-1]
                return result
            with self.subTest(omitted=omitted), patch.object(E, 'lower', broken), self.assertRaises(RuntimeError):
                E.replay_emitted(self.changed['forward'], 728, 112)

    def test_recipe_overlap_and_unpaid_gain_reject(self):
        pairs = self.recipe['pairs']
        with self.assertRaisesRegex(RuntimeError, 'overlapping'):
            E.factored(self.C, pairs+[pairs[0]])
        unpaid = copy.deepcopy(pairs)
        unpaid[0][3] += 16
        with self.assertRaisesRegex(RuntimeError, 'recipe gain'):
            E.factored(self.C, unpaid)

    def test_independent_noncommuting_and_admission_controls(self):
        self.assertEqual(I.self_test()['rejected_controls'], 8)

    def test_every_literal_coefficient_lowering_has_exact_boundary(self):
        # Independent one-column numeric execution; arbitrary initial work=7
        # must be erased and initial target=11 must be preserved plus q*source.
        cases = {E.Q(e[1][3], e[1][4]) for p in self.changed.values()
                 for e in p if e[0] == 'scalar' and e[1][0] == 'add'}
        for q in cases:
            values = {('L', 0): E.Q(11), ('L', 1): E.Q(13), ('W', 0): E.Q(7)}
            scalar = ['add', ['L', 0], ['L', 1], q.numerator, q.denominator]
            for primitive in E.lower(scalar):
                tag, target = primitive[:2]
                if tag == 'clear': values[target] = E.Q(0)
                elif tag == 'scale': values[target] *= primitive[2]
                elif tag == 'copy': values[target] = values[primitive[2]]
                else: values[target] += primitive[3]*values[primitive[2]]
            self.assertEqual(values[('L', 0)], 11+13*q)
            self.assertEqual(values[('L', 1)], 13)
            self.assertEqual(values[('W', 0)], 0)

    def test_semantic_source_pins_and_recompression(self):
        with tempfile.TemporaryDirectory(prefix='x4 source controls ') as directory:
            root = Path(directory)/'package'
            shutil.copytree(E.HERE, root)
            for name in ('CANONICAL-WORD.json.gz', 'LOCAL-PROGRAMS.json.gz'):
                p = root/'inputs'/name
                p.write_bytes(gzip.compress(json.dumps(E.read(p), indent=1).encode(), mtime=1234))
            V.inputs(root)  # positive: changed formatting and gzip bytes
            name = 'CANONICAL-WORD.json.gz'
            p = root/'inputs'/name
            c = E.read(p)
            c['h'] = 10
            p.write_bytes(gzip.compress(json.dumps(c).encode()))
            with self.assertRaisesRegex(RuntimeError, 'source digest'):
                V.inputs(root)
            # Repairing the editable outer manifest cannot bypass source pins.
            manifest = E.read(root/'SOURCES.json')
            manifest['input_semantic_sha256'][name] = E.digest(c)
            (root/'SOURCES.json').write_text(json.dumps(manifest))
            with self.assertRaisesRegex(RuntimeError, 'selected canonical source pin'):
                V.inputs(root)

    def test_standalone_optimized_relocation_and_output(self):
        with tempfile.TemporaryDirectory(prefix='x4 standalone controls ') as directory:
            root = Path(directory)/'package with spaces'
            shutil.copytree(E.HERE, root)
            result = subprocess.run([sys.executable, '-I', '-O', '-B', str(root/'verify.py'),
                                     '--out', str(Path(directory)/'fresh output')],
                                    cwd=directory, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout+result.stderr)
            output = E.read(Path(directory)/'fresh output/CANDIDATE-PROGRAMS.json.gz')
            self.assertEqual({k: E.digest(v) for k, v in output.items()},
                             {k: E.digest(v) for k, v in self.changed.items()})
            receipt = E.read(root/'RESULT.json')
            receipt['orientations']['forward']['saved_real_primitives'] += 1
            (root/'RESULT.json').write_text(json.dumps(receipt))
            rejected = subprocess.run([sys.executable, '-I', '-O', '-B', str(root/'verify.py')],
                                      cwd=directory, capture_output=True, text=True)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn('saved result mismatch', rejected.stderr)


if __name__ == '__main__':
    unittest.main(verbosity=2)
