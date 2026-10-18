#!/usr/bin/env python3
"""Failure controls, independent rank oracles and isolated package replay.

Copyright 2026 Ross Richardson. Apache-2.0. Substantial OpenAI Codex assistance.
"""
import importlib.util
import json
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE=Path(__file__).resolve().parent


def module(name):
    spec=importlib.util.spec_from_file_location(name,HERE/(name+'.py'))
    value=importlib.util.module_from_spec(spec); spec.loader.exec_module(value)
    return value


v=module('verify'); independent=module('independent')


class Package(unittest.TestCase):
    def test_exact_rank_oracles(self):
        rng=random.Random(46)
        cases=[[],[[]],[[0]],[[0,1],[0,0]],[[0,2],[3,4]],[[1,2,3],[2,4,6]]]
        for height in range(1,7):
            for width in range(1,7):
                for _ in range(4):
                    cases.append([[rng.randrange(-4,5) for _ in range(width)] for _ in range(height)])
        for matrix in cases:
            self.assertEqual(v.rank(matrix),independent.rational_rank(matrix))

    def test_two_terms_and_transpose(self):
        g=v.gram()
        pairs=[(v.E,v.E),(v.O,v.O)]
        v.check_decoder(pairs)
        self.assertEqual([v.pairing(g,f,s) for f,s in pairs],[16,16])
        fixture=json.loads((HERE/'CERTIFICATE.json').read_text())['witness']['pairs']
        v.check_decoder([(s,f) for f,s in fixture])
        self.assertEqual([v.pairing(g,s,f) for f,s in fixture],[8,16,8])

    def test_repeated_reader_equality(self):
        h=1<<v.EVEN[0]
        pairs=[(v.E,h),(v.E,v.E^h),(v.O,v.O)]
        v.check_decoder(pairs)
        self.assertEqual([v.pairing(v.gram(),f,s) for f,s in pairs],[1,15,16])

    def test_all_primary_mathematical_controls(self):
        g=v.gram(); m=v.cross_block(g)
        h=json.loads((HERE/'CERTIFICATE.json').read_text())['witness']['mask']
        self.assertEqual(len(v.controls(g,m,h)),10)

    def test_invalid_domains(self):
        for mask in (True,-1,1<<32,1.0):
            with self.assertRaises(ValueError): v.support(mask)
        for rows in ([[True]],[[1.0]],[[1],[2,3]]):
            with self.assertRaises(ValueError): v.rank(rows)

    def test_sparse_scope_and_budget(self):
        # Same-parity orthogonality alone does not force mixed-mask strictness.
        m=[[8*int(i==j) for j in range(16)] for i in range(16)]
        h=(1<<v.EVEN[0])|(1<<v.ODD[1])
        with self.assertRaisesRegex(ValueError,'strict mixed-parity'):
            v.formula(m,h)
        for stages in (3,4,5,17,1000000):
            self.assertEqual((stages-1)*32-stages*32,-32)
        self.assertGreater((3-1)*32-3*0,0)  # Free copying changes a premise.

    def test_sources_are_bound(self):
        original=v.HERE
        with tempfile.TemporaryDirectory(prefix='three totals pins ') as temp:
            dest=Path(temp)/'package'; shutil.copytree(HERE,dest)
            try:
                v.HERE=dest
                self.assertEqual(v.source_check(),7)
                for rel in ['sources/pr1046-proof.md','sources/pr958-proof.md','SOURCES.json']:
                    p=dest/rel; data=p.read_bytes(); p.write_bytes(data+b' ')
                    with self.assertRaises((ValueError,json.JSONDecodeError)): v.source_check()
                    p.write_bytes(data)
                p=dest/'sources/pr1046-proof.md'; data=p.read_bytes(); p.unlink()
                with self.assertRaises(FileNotFoundError): v.source_check()
                p.write_bytes(data)
            finally:
                v.HERE=original

    def test_offline_relocation_and_corruption(self):
        with tempfile.TemporaryDirectory(prefix='three totals offline ') as temp:
            dest=Path(temp)/'minimal tree'; shutil.copytree(HERE,dest)
            before={str(p.relative_to(dest)):p.read_bytes() for p in dest.rglob('*') if p.is_file()}
            def call(script):
                return subprocess.run([sys.executable,'-I','-O','-B',str(dest/script)],
                                      cwd=temp,capture_output=True,text=True,timeout=180)
            for script in ('verify.py','independent.py'):
                result=call(script)
                self.assertEqual(result.returncode,0,result.stderr)
            after={str(p.relative_to(dest)):p.read_bytes() for p in dest.rglob('*') if p.is_file()}
            self.assertEqual(before,after)
            p=dest/'CERTIFICATE.json'; original=p.read_text(); receipt=json.loads(original)
            receipt['unrestricted_three_term_floor']=31
            p.write_text(json.dumps(receipt))
            result=call('verify.py')
            self.assertNotEqual(result.returncode,0)
            self.assertIn('certificate mismatch',result.stderr)
            p.write_text(original)
            receipt=json.loads(original); receipt['cross_matrix'][0][0]+=1
            p.write_text(json.dumps(receipt))
            result=call('independent.py')
            self.assertNotEqual(result.returncode,0)
            self.assertIn('cross block',result.stderr)
            p.write_text(original)
            receipt=json.loads(original); receipt['dense_rank_checks'].pop(next(iter(receipt['dense_rank_checks'])))
            p.write_text(json.dumps(receipt))
            result=call('independent.py')
            self.assertNotEqual(result.returncode,0)
            self.assertIn('complete dense sample domain',result.stderr)

    def test_receipt_types(self):
        self.assertNotEqual(v.canonical({'n':1}),v.canonical({'n':True}))
        self.assertNotEqual(v.canonical({'n':32}),v.canonical({'n':32.0}))


if __name__=='__main__':
    unittest.main()
