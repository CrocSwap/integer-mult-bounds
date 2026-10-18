"""Mathematical and on-disk rejection controls (standard library only)."""
import copy
import itertools
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parent))
import core as C
import flow_check as F
import verify
import stream_check as S


class Checks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old, cls.phases, cls.audit, cls.owners = C.inputs()
        cls.new, cls.groups, cls.table, cls.contexts = C.derive(cls.old, cls.phases, cls.owners)

    def test_small_flow_against_complete_colour_assignments(self):
        cases = 0
        for k in (2, 3, 4):
            for sizes in ((1,), (2,), (1, 2), (2, 2), (1, 1, 2), (1, 2, 3)):
                if max(sizes) > k:
                    continue
                counts = set()
                choices = [list(itertools.combinations(range(k), q)) for q in sizes]
                for assignment in itertools.product(*choices):
                    counts.add(tuple(sum(j in row for row in assignment) for j in range(k)))
                for rank in F.compositions(sum(sizes), k):
                    self.assertEqual(F.solve(k, 0, list(sizes), rank)[0], rank in counts)
                    cases += 1
        self.assertGreater(cases, 100)

    def test_legacy_abstract_polynomial_against_literal_evaluation(self):
        for mask in range(1, 32):
            frames = [dict(child=0, orthogonal_axes=[mask, 1]), dict(child=1, orthogonal_axes=[3, 16])]
            recipe = dict(stage_alignment=[dict(entry_X=mask, entry_Y=3, exit_X=16, exit_Y=0)],
                          terminal_Y_translation=7, idle_children=[dict(translation_after=5), dict(translation_after=mask)])
            shift, const, linear, quadratic = C.legacy_flattened_operator(frames, recipe)
            for u in range(32):
                literal_u, phase = u ^ mask ^ 3 ^ 16, 0
                for row in frames:
                    phase += sum(C.dot(literal_u, v) for v in row['orthogonal_axes'])
                    literal_u ^= recipe['idle_children'][row['child']]['translation_after']
                literal_u ^= 7
                poly = const+sum(c*((u >> i) & 1) for i, c in enumerate(linear))
                poly += sum(c*((u >> i) & 1)*((u >> j) & 1) for i, j, c in quadratic)
                self.assertEqual((phase % 4, literal_u), (poly % 4, u ^ shift))

    def test_real_geometry_and_metadata_mutations(self):
        C.check_assignment(self.old, self.new, self.phases, self.owners)
        eligible = {C.label(r) for rows in C.eligible_groups(self.old, self.owners).values() for r in rows}
        i = next(i for i, r in enumerate(self.new) if C.label(r) in eligible and r['rank'] == 51)
        j = next(i for i, r in enumerate(self.new) if C.label(r) not in eligible)
        changes = [
            ('duplicate axis', lambda x: x[i]['orthogonal_axes'].__setitem__(0, x[i]['orthogonal_axes'][1])),
            ('lost axis', lambda x: x[i]['orthogonal_axes'].pop()),
            ('forged rank', lambda x: x[i].__setitem__('rank', 52)),
            ('owner metadata', lambda x: x[i].__setitem__('family', x[i]['family']+1)),
            ('hosted child', lambda x: x[j]['orthogonal_axes'].__setitem__(0, 0)),
            ('missing child', lambda x: x.pop()),
        ]
        for name, mutate in changes:
            with self.subTest(name=name):
                bad = copy.deepcopy(self.new)
                mutate(bad)
                with self.assertRaises(ValueError):
                    C.check_assignment(self.old, bad, self.phases, self.owners)

    def test_hall_obstructions_and_cap(self):
        # Six duplicated axes cannot leave either of two children, even though
        # dropping multiplicity makes a 51+45 optimistic profile look feasible.
        self.assertFalse(F.solve(2, 42, [2]*6, (51, 45))[0])
        self.assertTrue(F.solve(2, 42, [2]*6, (48, 48))[0])
        # The low-mobility three-child motif cannot attain the rank-only ceiling.
        self.assertFalse(F.solve(3, 42, [1, 2, 3]*3, (51, 51, 42))[0])
        self.assertTrue(F.solve(3, 42, [1, 2, 3]*3, (51, 48, 45))[0])
        table = copy.deepcopy(self.table)
        table[-1]['prefix_bounds'][2] += 1
        with self.assertRaises(ValueError):
            F.census(table)

    def test_physical_stream_counterexample(self):
        result = S.report(self.old, self.new, self.phases, self.owners)
        self.assertFalse(result['admitted'])
        self.assertEqual(result['baseline_modes'], 147)
        self.assertEqual(result['differences'], [
            [1, 1, [0, 1], [-1, 0]], [3, 1, [0, 0], [-1, -1]], [7, 7, [0, 1], [1, 0]]])
        prepared = S.prepare(S.template(), self.phases, self.owners)
        S.require_equal(prepared, self.old, self.old, 32)
        # The uniform mode cannot detect this error; the nonuniform mode does.
        S.require_equal(prepared, self.old, self.new, 0)
        with self.assertRaisesRegex(ValueError, 'physical stream operator differs'):
            S.require_equal(prepared, self.old, self.new, 32)
        # Address translation X_32 multiplies character 32 by -1; it does not
        # send it to character 0. C_32 therefore multiplies it by i.
        self.assertEqual(S.rotate(S.ONE, 2*C.dot(32, 32)), (-1, 0))
        self.assertEqual(S.rotate(S.ONE, C.dot(32, 32)), (0, 1))

    def test_json_types_and_expected_certificate(self):
        for raw in ('{"x":1,"x":2}', '{"x":NaN}', '{"x":Infinity}'):
            with self.assertRaises(ValueError):
                C.decode(raw)
        for bad in (True, 1.0, 2):
            with self.assertRaises(ValueError):
                verify.compare({'count': bad}, {'count': 1}, 'typed certificate')
        expected = C.read(C.PACKAGE/'EXPECTED.json')['mathematics']
        bad = copy.deepcopy(expected)
        bad['profile']['51'] += 1
        with self.assertRaises(ValueError):
            verify.compare(bad, expected, 'profile')

    def test_readonly_optimized_export_and_source_corruption(self):
        with tempfile.TemporaryDirectory(prefix='idle27-export-') as temp:
            parent = Path(temp)
            root = parent/'export'
            package = root/'research'/C.PACKAGE.name
            package.parent.mkdir(parents=True)
            shutil.copytree(C.PACKAGE, package, ignore=shutil.ignore_patterns('__pycache__'))
            for name in C.INPUTS:
                destination = root/name
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(C.ROOT/name, destination)
            files = [p for p in root.rglob('*') if p.is_file()]
            before = {str(p.relative_to(root)): C.sha(p) for p in files}
            dirs = sorted([root]+[p for p in root.rglob('*') if p.is_dir()], key=lambda p: len(p.parts), reverse=True)
            try:
                for p in files:
                    p.chmod(0o444)
                for p in dirs:
                    p.chmod(0o555)
                result = subprocess.run([sys.executable, '-I', '-O', '-B', str(package/'verify.py'),
                                         '--work', str(parent/'result')], cwd='/tmp', text=True, capture_output=True, timeout=60)
                self.assertEqual(result.returncode, 0, result.stdout+result.stderr)
                self.assertIn('PASS_SELECTED1094_IDLE_OPTIMUM', result.stdout)
                self.assertEqual(before, {str(p.relative_to(root)): C.sha(p) for p in files})
            finally:
                for p in dirs:
                    p.chmod(0o755)
                for p in files:
                    p.chmod(0o644)
            source = root/C.REPLAY
            with source.open('r+b') as f:
                first = f.read(1)
                f.seek(0)
                f.write(bytes([first[0] ^ 1]))
            result = subprocess.run([sys.executable, '-I', '-B', str(package/'verify.py'),
                                     '--work', str(parent/'bad')], cwd='/tmp', text=True, capture_output=True, timeout=10)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('source drift', result.stderr)

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
