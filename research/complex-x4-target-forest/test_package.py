"""Focused mathematical and package failure controls (stdlib, offline)."""
import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import experiment as e
import independent as ind


class Package(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.word,cls.programs,cls.checks=e.load()
        cls.recipe=json.loads((HERE/'RECIPE.json').read_text())
        cls.new,cls.prep,_=e.forest(cls.word,cls.recipe)
        cls.rows,cls.helpers=ind.rows_from_word(cls.word)
        cls.graph=ind.complete_graph(cls.rows)

    def test_underbilled_basis_rejected(self):
        recipe=copy.deepcopy(self.recipe)
        next(x for x in recipe['edges'] if x[0]!=-1)[3]-=8
        with self.assertRaisesRegex(ValueError,'edge price'):
            ind.check_tree(recipe,self.rows,self.graph)

    def test_nonminimal_valid_forest_rejected(self):
        # Root-only tree implements the original correct panel, but is not minimal.
        recipe={'edges':[x for x in self.graph if x[0]==-1]}
        new,prep,_=e.forest(self.word,recipe)
        self.assertEqual(prep,0)
        self.assertEqual(e.boundary(self.word,new,'forward'),e.boundary(self.word,self.word['compensation'],'forward'))
        with self.assertRaisesRegex(ValueError,'Prim optimum'):
            ind.check_tree(recipe,self.rows,self.graph)

    def test_cycle_rejected(self):
        recipe=copy.deepcopy(self.recipe);recipe['edges'][-1]=recipe['edges'][0]
        with self.assertRaisesRegex(ValueError,'cycle|repeated'):
            ind.check_tree(recipe,self.rows,self.graph)

    def test_missing_preparation_arbitrary_targets(self):
        original=self.word['compensation'];bad=self.new[self.prep:]
        self.assertEqual(e.boundary(self.word,bad,'forward',False),e.boundary(self.word,original,'forward',False))
        self.assertNotEqual(e.boundary(self.word,bad,'forward'),e.boundary(self.word,original,'forward'))

    def test_missing_private_clear(self):
        op=['add',['L',0],['L',1],-3,4]
        rows={('L',0):{0:e.Q(1)},('L',1):{1:e.Q(1)},e.WORK:{2:e.Q(1)}}
        for p in e.lower(op)[:-1]:e.step(rows,p)
        self.assertEqual(rows[('L',0)],{0:e.Q(1),1:e.Q(-3,4)})
        self.assertTrue(rows[e.WORK])

    def test_missing_initial_work_clear(self):
        op=['add',['L',0],['L',1],3,4]
        rows={('L',0):{0:e.Q(1)},('L',1):{1:e.Q(1)},e.WORK:{2:e.Q(1)}}
        for primitive in e.lower(op)[1:]:e.step(rows,primitive)
        self.assertFalse(rows[e.WORK])
        self.assertIn(2,rows[('L',0)])
        self.assertNotEqual(rows[('L',0)],{0:e.Q(1),1:e.Q(3,4)})

    def test_wrong_program_boundary(self):
        p=copy.deepcopy(self.programs['forward']);p[169][1][3]*=-1
        with self.assertRaisesRegex(ValueError,'compensation boundary'):
            e.replace(p,self.word,self.new,'forward')

    def test_source_pin_corruption(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            for path in json.loads((HERE/'SOURCES.json').read_text())['files']:
                target=root/path;target.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(e.ROOT/path,target)
            (root/e.WORDPIN).write_text('{}')
            with patch.object(e,'ROOT',root),self.assertRaisesRegex(ValueError,'source pin'):
                e.load()

    def test_relocated_minimal_source_closure(self):
        with tempfile.TemporaryDirectory(prefix='X4 forest with spaces ') as temp:
            root=Path(temp)
            package=root/'research/complex-x4-target-forest';package.mkdir(parents=True)
            for name in ('experiment.py','independent.py','RECIPE.json','SOURCES.json'):
                shutil.copyfile(HERE/name,package/name)
            for path in json.loads((HERE/'SOURCES.json').read_text())['files']:
                target=root/path;target.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(e.ROOT/path,target)
            code="import sys;sys.path.insert(0,sys.argv[1]);import experiment as e;w,p,c=e.load();r=e.synthesize(w);print(r['complex_primitive_floor'])"
            run=subprocess.run([sys.executable,'-I','-O','-B','-c',code,str(package)],cwd=root,text=True,capture_output=True)
            self.assertEqual(run.returncode,0,run.stderr)
            self.assertEqual(run.stdout.strip(),'10883')


if __name__=='__main__':unittest.main()
