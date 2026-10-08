"""Independent coefficient and full-export controls for split exploration."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts/experiments'))
from ternary_split_search import Search, transpose, exact_outputs
from intersection_circuit import build, feasible
from ternary_target_certify import build_checkers


class SplitSearch(unittest.TestCase):
    def test_transposition_preserves_every_coefficient(self):
        for n in range(4, 9):
            for k, l, r in ((1, 2, 0), (1, 3, 1), (2, 3, 1), (3, 2, 0)):
                if feasible(n, k, l, r):
                    c = build(n, k, l, r)
                    ct = transpose(c)
                    self.assertTrue(exact_outputs(ct))
                    self.assertLessEqual(ct.additions, c.additions+len(c.outputs)-len(c.inputs))

    def test_state_choices_and_complements_have_exact_outputs(self):
        search = Search()
        for n in range(4, 9):
            for k in range(n+1):
                for l in range(min(n, 3)+1):
                    for r in range(min(k, l)+1):
                        if feasible(n, k, l, r):
                            self.assertTrue(exact_outputs(search.build(n, k, l, r)))
        improved = search.build(8, 2, 2, 1)
        self.assertLess(improved.additions, build(8, 2, 2, 1).additions)
        self.assertEqual(search.choices[8, 2, 2, 1]['split'], 3)

    def test_exported_plan_passes_independent_support_and_frame_checkers(self):
        with tempfile.TemporaryDirectory(prefix='ternary-split-test-') as name:
            workdir = Path(name)
            plan, dag = workdir/'plan.bin', workdir/'dag.bin'
            Search().export(8, plan)
            binaries = build_checkers(workdir)
            support = json.loads(subprocess.check_output(
                [str(binaries['exact']), str(plan), str(dag)], text=True,
                stderr=subprocess.DEVNULL))
            frames = json.loads(subprocess.check_output(
                [str(binaries['dual']), str(dag), str(workdir/'unresolved')],
                text=True, stderr=subprocess.DEVNULL))
            self.assertTrue(support['every_output_family_independently_checked'])
            self.assertTrue(frames['every_final_frame_nondegenerate'])
            self.assertTrue(frames['source_region_ancestor_closed'])
            self.assertTrue(frames['all_centers_in_source_region'])


if __name__ == '__main__':
    unittest.main()
