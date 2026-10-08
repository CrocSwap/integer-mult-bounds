"""Exact small controls for asymmetric top-partition screening."""
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts/experiments'))
from ternary_top_split_search import export, append_screening_cores
from ternary_split_search import Search, baseline
from ternary_target_certify import build_checkers
from ternary_target_fingerprint import export as inherited_export


class TopPartition(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix='ternary-top-tests-')
        cls.workdir = Path(cls.temporary.name)
        cls.checkers = build_checkers(cls.workdir)

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def test_half_partition_preserves_inherited_plan_bytes(self):
        a, b = self.workdir/'old.bin', self.workdir/'new.bin'
        inherited_export(10, a)
        export(10, 5, b, baseline.build)
        self.assertEqual(a.read_bytes(), b.read_bytes())

    def test_both_asymmetric_orientations_pass_exact_output_checker(self):
        search = Search()
        for split in (3, 5):
            with self.subTest(split=split):
                plan, dag = self.workdir/f'plan-{split}.bin', self.workdir/f'dag-{split}.bin'
                export(8, split, plan, search.build)
                result = json.loads(subprocess.check_output(
                    [str(self.checkers['exact']), str(plan), str(dag)],
                    text=True, stderr=subprocess.DEVNULL))
                self.assertTrue(result['every_output_family_independently_checked'])
                frames = json.loads(subprocess.check_output(
                    [str(self.checkers['dual']), str(dag), str(self.workdir/'unresolved')],
                    text=True, stderr=subprocess.DEVNULL))
                self.assertTrue(frames['every_final_frame_nondegenerate'])
                # The screening core appender must reproduce exact ZDD cores.
                original = dag.read_bytes()
                _, _, n, _ = struct.unpack_from('<4I', original)
                dag.write_bytes(original[:-4*n])
                append_screening_cores(dag)
                self.assertEqual(dag.read_bytes(), original)
                with self.assertRaisesRegex(ValueError, 'without appended source cores'):
                    append_screening_cores(dag)


if __name__ == '__main__':
    unittest.main()
