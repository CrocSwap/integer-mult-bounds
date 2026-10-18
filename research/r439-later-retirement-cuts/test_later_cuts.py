# SPDX-License-Identifier: Apache-2.0
import copy
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE=Path(__file__).resolve().parent

def module(name):
    s=importlib.util.spec_from_file_location(name,HERE/(name+'.py'))
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

P,Q=module('later_cuts'),module('check_later_cuts')

class LaterCutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.cert=json.loads((HERE/'LATER-CUTS.json').read_text())

    def test_complete_both_engines(self):
        self.assertEqual(P.compute(),self.cert)
        Q.check(self.cert)

    def test_named_boundary_witnesses(self):
        cases={e['helper']:e for e in self.cert['helpers']}
        def row(h,k):return next(r['conditions'] for r in cases[h]['runs'] if r['first_cut']<=k<=r['last_cut'])
        self.assertEqual(row(465,9)['lost_targets'],[122])
        self.assertEqual(row(465,10)['lost_targets'],[])
        self.assertEqual(row(465,48)['joint_rank'],7)
        self.assertEqual(row(465,49)['joint_rank'],8)
        self.assertEqual(row(468,30)['lost_targets'],[144])
        self.assertEqual(row(468,31)['lost_targets'],[])
        self.assertEqual(row(468,88)['joint_rank'],7)
        self.assertEqual(row(468,89)['joint_rank'],8)
        self.assertEqual(row(466,78)['lost_targets'],[208])
        self.assertEqual(row(466,79)['joint_rank'],8)
        self.assertEqual(row(466,89)['joint_rank'],8)

    def test_mathematical_certificate_faults(self):
        mutations=[lambda c:c['helpers'][0]['windows'][0].__setitem__(0,9),
                   lambda c:c['helpers'][0]['runs'][0]['conditions']['lost_targets'].clear(),
                   lambda c:c['helpers'][1]['runs'][0]['conditions']['restore_donors'].append(1),
                   lambda c:c['helpers'][3]['runs'][0]['conditions'].update({'joint_rank':8}),
                   lambda c:c['helpers'][4]['runs'][-1].update({'last_cut':711}),
                   lambda c:c['helpers'].pop()]
        for mut in mutations:
            bad=copy.deepcopy(self.cert);mut(bad)
            self.assertNotEqual(P.compute(),bad)
            with self.assertRaises(ValueError):Q.check(bad)

    def test_source_only_optimized_relocation_and_controls(self):
        with tempfile.TemporaryDirectory(prefix='later bit cuts ') as tmp:
            root=Path(tmp);pkg=root/'research/r439-later-retirement-cuts'
            shutil.copytree(HERE,pkg)
            raw=root/P.V.WORD;raw.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(P.V.ROOT/P.V.WORD,raw)
            for script in ['later_cuts.py','check_later_cuts.py']:
                run=subprocess.run([sys.executable,'-I','-O','-B',str(pkg/script)],cwd=root,capture_output=True,text=True)
                self.assertEqual(run.returncode,0,run.stderr)
            out=root/'later-regenerated.json'
            cmd=[sys.executable,'-I','-O','-B',str(pkg/'later_cuts.py'),'--output',str(out)]
            self.assertEqual(subprocess.run(cmd,capture_output=True).returncode,0)
            self.assertEqual(json.loads(out.read_text()),self.cert)
            self.assertNotEqual(subprocess.run(cmd,capture_output=True).returncode,0)
            raw.write_bytes(raw.read_bytes()+b'corrupt')
            for script in ['later_cuts.py','check_later_cuts.py']:
                run=subprocess.run([sys.executable,'-I','-O','-B',str(pkg/script)],capture_output=True,text=True)
                self.assertNotEqual(run.returncode,0)
                self.assertIn('source hash',run.stderr)

if __name__=='__main__':unittest.main(verbosity=2)
