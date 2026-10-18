#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Small source/recipe/portability controls without historical replays."""
import copy
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import types
import unittest

P=Path(__file__).resolve().parent
def load(name):
    path=P/(name+'.py');m=types.ModuleType(name);m.__file__=str(path)
    exec(compile(path.read_bytes(),str(path),'exec'),m.__dict__);return m
engine=load('run_release')

class Bindings(unittest.TestCase):
    def recipe(self):
        source=Path('/pinned/source');recipe=[[name,['python','stage.py']] for name in engine.STAGES]
        recipe[-1][1]=['python','admit.py','--source',str(source),'--fill',str(source/'allocation/FILL.json.gz'),
                       '--order',str(source/'allocation/ORDER.json'),'--dispatch',str(source/'allocation/DISPATCH.json'),'--jobs','2']
        return source,recipe

    def test_exact_three_allocation_arguments(self):
        source,original=self.recipe();recipe,changes=engine.adapt(original,source,Path('/new'))
        self.assertEqual(original[:-1],recipe[:-1]);self.assertEqual(len(changes),3)
        self.assertEqual(sum(a!=b for a,b in zip(original[-1][1],recipe[-1][1])),3)
        self.assertEqual(original[-1][1][-2:],recipe[-1][1][-2:])
        self.assertIn(str(source/'allocation/FILL.json.gz'),original[-1][1])
        fresh=copy.deepcopy(original);fresh.insert(2,['fresh-retained-bootstrap',['python','prepare_retained.py']])
        adapted,changes=engine.adapt(fresh,source,Path('/new'))
        self.assertEqual(adapted[2],fresh[2]);self.assertEqual(len(changes),3)

    def test_missing_stage_and_stale_preimage_rejected(self):
        source,recipe=self.recipe()
        with self.assertRaises(ValueError):engine.adapt(recipe[1:],source,Path('/new'))
        bad=copy.deepcopy(recipe);bad[-1][1][bad[-1][1].index('--fill')+1]='/other/fill'
        with self.assertRaises(ValueError):engine.adapt(bad,source,Path('/new'))

    def test_regenerated_gzip_payload_not_container(self):
        saved_payload,saved_alloc=engine.FILL_PAYLOAD,engine.ALLOCATION
        payload=b'{"fixture":"same complete payload"}\n'
        try:
            engine.FILL_PAYLOAD=hashlib.sha256(payload).hexdigest()
            with tempfile.TemporaryDirectory() as tmp:
                p=Path(tmp)
                for name in ['ORDER.json','DISPATCH.json']:(p/name).write_bytes(b'[]\n')
                engine.ALLOCATION={name:engine.sha(p/name) for name in ['ORDER.json','DISPATCH.json']}
                hashes=[]
                for mtime,level in [(0,1),(1234,9)]:
                    (p/'COMPOSED-FILL.json.gz').write_bytes(gzip.compress(payload,mtime=mtime,compresslevel=level))
                    hashes.append(engine.allocation_binding(p)['fill_sha256'])
                self.assertNotEqual(*hashes)
                (p/'COMPOSED-FILL.json.gz').write_bytes(gzip.compress(payload+b' ',mtime=0))
                with self.assertRaises(ValueError):engine.allocation_binding(p)
        finally:engine.FILL_PAYLOAD,engine.ALLOCATION=saved_payload,saved_alloc

    def test_optimized_interpreter_refused(self):
        r=subprocess.run([sys.executable,'-O','-B',str(P/'verify.py'),'--finite-only'],capture_output=True,text=True)
        self.assertNotEqual(r.returncode,0);self.assertIn('retained checkers require enabled assertions',r.stderr)

if __name__=='__main__':unittest.main()
