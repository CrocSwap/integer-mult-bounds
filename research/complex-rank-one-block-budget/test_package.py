#!/usr/bin/env python3
"""Scoped corruption, arithmetic-mutation and relocated-source controls.

Arham Tahir with substantial OpenAI Codex assistance. Apache-2.0.
"""
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


class PackageControls(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='rank block control ')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.package = self.root/'research'/HERE.name
        self.package.mkdir(parents=True)
        for name in ('verify.py','SOURCES.json','RESULT.json'):
            shutil.copyfile(HERE/name,self.package/name)
        for row in json.loads((HERE/'SOURCES.json').read_text())['files']:
            if row['usage']=='input':
                destination = self.root/row['path']
                destination.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(ROOT/row['path'],destination)

    def replay(self, optimized=False):
        command = [sys.executable,'-I','-B']
        if optimized:
            command.append('-O')
        command.append(str(self.package/'verify.py'))
        return subprocess.run(command,cwd=self.root,capture_output=True,text=True,timeout=45)

    def test_readonly_relocation(self):
        for path in self.root.rglob('*'):
            if path.is_file():
                path.chmod(0o444)
        result = self.replay(optimized=True)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn('PASS_COMPLEX_RANK_ONE_BLOCK_BUDGET',result.stdout)

    def test_source_drift(self):
        source = self.root/'research/complex-local-word-ceiling/ceiling.py'
        source.write_text(source.read_text()+'\n# corruption control\n')
        result = self.replay()
        self.assertNotEqual(result.returncode,0)
        self.assertIn('source drift:',result.stderr)

    def test_source_inventory_omission(self):
        path = self.package/'SOURCES.json'
        sources = json.loads(path.read_text())
        sources['files'] = [row for row in sources['files']
                            if row['path'] != 'research/complex-local-word-ceiling/ceiling.py']
        path.write_text(json.dumps(sources))
        result = self.replay()
        self.assertNotEqual(result.returncode,0)
        self.assertIn('source inventory',result.stderr)

    def test_receipt_value_and_type_drift(self):
        path = self.package/'RESULT.json'
        original = json.loads(path.read_text())
        changed = json.loads(json.dumps(original))
        changed['rows'][14]['minimum_replaced'] -= 1
        path.write_text(json.dumps(changed))
        result = self.replay()
        self.assertNotEqual(result.returncode,0)
        self.assertIn('result drift',result.stderr)
        changed = json.loads(json.dumps(original))
        changed['rank16_complete_overhead_by_rank'][3]['max_calls'] = True
        path.write_text(json.dumps(changed))
        result = self.replay(optimized=True)
        self.assertNotEqual(result.returncode,0)
        self.assertIn('result drift',result.stderr)

    def test_independent_oracle_mutation(self):
        spec = importlib.util.spec_from_file_location('block_budget_control',self.package/'verify.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        original = module.binomial_cost

        def wrong(r,a):
            bounds = original(r,a)
            return tuple(x+module.Q(1,10) for x in bounds)

        module.binomial_cost = wrong
        with self.assertRaisesRegex(ValueError,'baseline lower sign'):
            module.verify()

    def test_binomial_square_root_enclosures(self):
        spec = importlib.util.spec_from_file_location('block_budget_sqrt',self.package/'verify.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        # At a=1/2, squaring checks the interval without either moment engine.
        for rank in range(1,73):
            lo,hi = module.binomial_cost(rank,module.Q(1,2))
            self.assertGreater(lo,0)
            self.assertLessEqual(lo*lo,module.Q(rank,73))
            self.assertGreaterEqual(hi*hi,module.Q(rank,73))


if __name__=='__main__':
    unittest.main()
