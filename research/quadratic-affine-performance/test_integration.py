"""Real gather omission and authenticated historical replay failure controls.

Douglas Colkitt, with OpenAI Codex assistance; Apache-2.0.
"""
from pathlib import Path
import json
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / 'scripts'))
import historical_packed as h
from experiments import quadratic_affine as qa
from reference import reference_rows


class IntegrationControls(unittest.TestCase):
    def test_actual_omitted_gather_stage_is_detected(self):
        fixtures = json.loads((ROOT/'scripts/experiments/quadratic_affine_witnesses.json').read_text())
        w = fixtures[5];f = qa.family(w['t'],w['complex_phases'],w['parity'])
        vectors = [qa.vector(f,i) for i in w['sample']]
        expected = reference_rows(vectors,w['independent_rows'])
        self.assertEqual(qa._orthogonality_rows(vectors,f['D'],w['independent_rows']),expected)
        masks = list(qa._GATHER_CACHE[len(vectors)])
        def omitted(flags,lanes):
            x = flags >> 7
            for i,mask in enumerate(masks):
                if i == 0:continue  # Omit an actual live gather stage.
                x = (x & ~mask) | ((x & mask) >> (7 << i))
            return x & ((1 << lanes)-1)
        with patch.object(qa,'_gather_lanes',omitted):
            self.assertNotEqual(qa._orthogonality_rows(vectors,f['D'],w['independent_rows']),expected)

    def config(self):
        return json.loads((HERE/'HISTORICAL-PACKED.json').read_text())

    def test_exact_historical_snapshot_and_input_tampering(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/'snapshot';expected=h.materialize(ROOT,root,self.config())
            manifest=json.loads((root/h.MANIFEST).read_text())
            for rel,pin in manifest['files'].items():self.assertEqual(h.digest((root/rel).read_bytes()),pin)
            h.verify_unchanged(root,expected)
            target=root/'scripts/experiments/quadratic_affine.py';target.write_bytes(target.read_bytes()+b' ')
            with self.assertRaisesRegex(ValueError,'Changed replay input'):h.verify_unchanged(root,expected)

    def test_wrong_live_successor_rejected(self):
        config=self.config();config['accepted_live']['scripts/experiments/quadratic_affine.py']=['0'*64]
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError,'Unrecognized live source'):
                h.materialize(ROOT,Path(tmp)/'snapshot',config)

    def test_wrong_historical_blob_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError,'Changed historical blob'):
                h.materialize(ROOT,Path(tmp)/'snapshot',self.config(),fetch=lambda *args:b'wrong')

    def test_changed_predecessor_package_rejected(self):
        config=self.config();config['package_files']['research/quadratic-affine-packed/verify.py']='0'*64
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError,'Changed predecessor package'):
                h.materialize(ROOT,Path(tmp)/'snapshot',config)

    def test_success_requires_exit_and_terminal_marker(self):
        h.check_completion(0,h.SUCCESS+'\n')
        for code,output in [(0,''),(1,h.SUCCESS),(0,h.SUCCESS+'\nmore')]:
            with self.assertRaisesRegex(ValueError,'Incomplete historical replay'):h.check_completion(code,output)


if __name__=='__main__':unittest.main()
