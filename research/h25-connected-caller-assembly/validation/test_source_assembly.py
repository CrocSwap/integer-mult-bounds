"""Static/source-loader controls; no role, native observer or science runs."""
import ast
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import types
import unittest

D=Path(__file__).resolve().parents[1]
B=D/'implementation/bindings'
OLD=Path('/home/d3lerium/.codex/.chatgpt-projects/g-p-6ad5817fd84881918865926b6fd51453/outputs/caller-proof-completion-20261107T0155Z')

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

class SourceAssembly(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest=json.loads((B/'SOURCE-MANIFEST-v2.json').read_bytes())
        cls.loader=load('bounded_source_assembly_loader',B/'private_loader.py')

    def test_all_selected_pins_use_actual_strict_production_reader(self):
        m=self.manifest;l=self.loader
        for row in [*m['source_pins'].values(),*m['profiles'].values(),*m['control_pins']]:
            with self.subTest(path=row['path']):
                raw=l.read_fixed(Path(row['path']),row['bytes'],row,mode=row['mode'])
                self.assertEqual(hashlib.sha256(raw).hexdigest(),row['sha256'])
        self.assertIsNone(l.FIRST[0]);self.assertFalse(l.UNKNOWN[0])
        self.assertTrue(all(row[1] in ('FREE','CLOSED') for row in l.SLOTS))
        for key,path in l.FIXED_PYTHON_PATHS.items():
            self.assertEqual(str(path),m['source_pins'][key]['path'])
        self.assertEqual(m['source_pins']['runner'],m['source_pins']['common_runner'])

    def test_complete_stage_members_and_exact_scientific_inverse(self):
        for mode,leaf in [('normal','joined-full-candidate-v1'),('optimized','joined-full-candidate-refusal-v1')]:
            stage=B/'stages'/leaf;old=OLD/'implementation/bindings/stages'/leaf
            current=json.loads((stage/'STAGE.json').read_bytes());prior=json.loads((old/'STAGE.json').read_bytes())
            self.assertEqual(set(current['files']),set(prior['files'])|{'integration/candidate_entry.py'})
            for rel,row in current['files'].items():
                path=stage/rel
                self.assertEqual(path.stat().st_mode&0o777,row['mode'])
                self.assertEqual(digest(path),row['sha256'])
                if rel not in ('JOBS.json','integration/candidate_entry.py'):
                    self.assertEqual(row,prior['files'][rel])
                    self.assertEqual(path.read_bytes(),(old/rel).read_bytes())
            jobs=json.loads((stage/'JOBS.json').read_bytes())
            self.assertEqual(jobs[mode]['entry'],'integration/candidate_entry.py')
            self.assertNotIn('bootstrap',jobs[mode])
            self.assertEqual(digest(stage/'integration/candidate_entry.py'),self.manifest['source_pins']['waiting_entry']['sha256'])
            self.assertEqual(current['runner_sha256'],self.manifest['source_pins']['common_runner']['sha256'])

    def test_real_private_loader_lifecycle_and_wrong_pair_rejection(self):
        # This fixture owns only the source transport fields of a PrivateBundle.
        # It creates no Context/EX/guardian or actual runtime qualification.
        l=self.loader;b=object.__new__(l.PrivateBundle)
        b._pid=os.getpid();b.role='CONTROLLER';b.manifest=self.manifest
        b.modules={};b._images={};b._functions={};b._classes={};b._runtime_seen={}
        b._environment_association=None;b.guardian=None
        module=b.load('supervisor');b.check('supervisor')
        self.assertIsNone(module._COMMON)
        self.assertEqual(str(module.RUNNER_PATH),self.manifest['source_pins']['common_runner']['path'])
        self.assertEqual(module.RUNNER_SHA,self.manifest['source_pins']['common_runner']['sha256'])
        module._COMMON=(dict(self.manifest['source_pins']['common_runner']),dict(self.manifest['source_pins']['waiting_entry']))
        b.check('supervisor')
        module._COMMON=(dict(module._COMMON[0]),dict(module._COMMON[1],path='/tmp/unselected/candidate_entry.py'))
        with self.assertRaises(l.BootstrapStop):b.check('supervisor')

    def test_actual_role_entry_constructor_selects_this_bootstrap(self):
        roles=load('bounded_source_role_constructor',B/'role_contracts.py')
        for role,key in roles.ROLE_ENTRY.items():
            argv=roles.entry_argv(role,self.manifest['source_pins'])
            self.assertEqual(argv[0],self.manifest['source_pins'][key]['path'])
            self.assertTrue(argv[0].startswith(str(D)+'/implementation/'))
            self.assertIn('--manifest-sha256',argv)
            self.assertIn('--contracts-sha256',argv)
        # The constructor deliberately leaves actual grant/currentness/START
        # inputs with their genuine owner; this control never supplies them.

if __name__=='__main__':unittest.main(verbosity=2)
