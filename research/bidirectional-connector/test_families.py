#!/usr/bin/env python3
"""Regression tests for generic cube schedules and charged-cost comparisons."""
from fractions import Fraction
from itertools import product
import ast
from hashlib import sha256
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import benchmark
import families as f
import verify as v


class FamilyTests(unittest.TestCase):
    def test_benchmark_function_pins(self):
        here=Path(__file__).resolve().parent
        receipt=json.loads((here/'BENCHMARKS.json').read_text())
        pins={**receipt['final_algorithm_function_sha256'],
              **receipt['current_signed_algorithm_function_sha256']}
        self.assertEqual(len(pins),23)
        for name,expected in pins.items():
            filename,function=name.split(':')
            self.assertIn(filename,('benchmark.py','families.py'))
            source=(here/filename).read_text()
            nodes=[node for node in ast.parse(source).body
                   if isinstance(node,ast.FunctionDef) and node.name==function]
            self.assertEqual(len(nodes),1,name)
            self.assertEqual(sha256(ast.get_source_segment(source,nodes[0]).encode()).hexdigest(),
                             expected,name)

    def test_benchmark_pin_drift_rejected(self):
        here=Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory() as directory:
            target=Path(directory)
            for name in ('benchmark.py','families.py','verify.py','test_families.py','BENCHMARKS.json'):
                shutil.copyfile(here/name,target/name)
            argv=[sys.executable,'-B',str(target/'test_families.py'),
                  'FamilyTests.test_benchmark_function_pins']
            valid=subprocess.run(argv,cwd=directory,capture_output=True,text=True,timeout=20)
            self.assertEqual(valid.returncode,0,valid.stderr)
            file=target/'benchmark.py';source=file.read_text()
            node=next(node for node in ast.parse(source).body
                      if isinstance(node,ast.FunctionDef) and node.name=='run_inplace')
            lines=source.splitlines(keepends=True)
            lines.insert(node.lineno,'    # Mutated measured function: receipt must reject drift.\n')
            file.write_text(''.join(lines))
            invalid=subprocess.run(argv,cwd=directory,capture_output=True,text=True,timeout=20)
            self.assertNotEqual(invalid.returncode,0)
            self.assertIn('benchmark.py:run_inplace',invalid.stderr)

    def test_balanced_and_unbalanced_generic_identities(self):
        for sizes in ((1,1,1), (2,1,1), (2,2,2), (1,2,4), (3,3,3), (4,4,4)):
            n = sum(sizes)
            word = f.construct_palette(sizes)
            v.check_endpoint(word, n, 2)
            counts = f.palette_screen(sizes)
            self.assertEqual(len(word), sum(counts[k] for k in ("source_calls", "readout_calls", "transfers")))
            self.assertEqual(sum(op[0]=='A' for op in word), counts['readout_calls'])
            self.assertTrue(all(op[2]==0 for op in word if op[0] in ('A','B')))

    def test_every_small_one_root_partition(self):
        for n in range(1,8):
            for sizes in f.partitions(n):
                word=f.construct(sizes)
                v.check_endpoint(word,n,1)
                self.assertEqual(sum(op[0]=='A' for op in word),f.readout_count(sizes))

    def test_palette_omissions_and_changed_ports(self):
        word=f.construct_palette((2,2,2))
        for index in range(len(word)):
            with self.subTest(index=index),self.assertRaises(ValueError):
                v.check_endpoint(word[:index]+word[index+1:],6,2)
        for kind in ('A','B','C'):
            changed=[list(op) for op in word]
            i=next(i for i,op in enumerate(changed) if op[0]==kind)
            changed[i][-1]^=1
            with self.assertRaises(ValueError):v.check_endpoint(changed,6,2)

    def test_exact_readout_formula_by_mask_enumeration(self):
        for sizes in ((1,), (1,1), (2,2,2), (1,2,3,3)):
            masks=[sum(1<<j for j in group) for group in f.blocks(sizes)]
            count=sum((t:=sum(bool(mask&g) for g in masks))+(t%2) for mask in range(1,1<<sum(sizes)))
            self.assertEqual(count,f.readout_count(sizes))
        for sizes in ((1,1,1),(2,2,2),(1,2,4)):
            masks=[sum(1<<j for j in group) for group in f.blocks(sizes)]
            count=sum(3 if all(mask&g for g in masks) else 2 for mask in range(1,1<<sum(sizes)))
            self.assertEqual(count,f.palette_screen(sizes)['readout_calls'])

    def test_all_partition_optimizer_and_strict_budget(self):
        # Retained Richardson repair attains the other branch of the exact
        # five-source optimum; the unused second dirty root remains arbitrary.
        repair=json.loads((Path(__file__).parent/'references'/'ONE-ROOT74.json').read_text())['word']
        v.check_endpoint(repair,5,2)
        self.assertEqual(len(repair),74)
        self.assertFalse(any(op[0]=='C' for op in repair))
        for n,b in ((9,20),(12,85),(15,200),(18,800)):
            best=f.best_single(n,b,1)
            self.assertTrue(all(f.cost(best,b,1)<=f.cost(other,b,1) for other in f.partitions(n)))
            best_palette=f.best_palette(n,b,1,1)
            self.assertTrue(all(f.palette_cost(best_palette,b,1,1)<=f.palette_cost(tuple(reversed(other)),b,1,1) for other in f.partitions(n) if len(other)==3))
            counts=f.palette_screen(best_palette)
            new=counts['source_calls']*b+counts['readout_calls']+counts['transfers']
            self.assertLess(new,f.cost(best,b,1))
        # Equal A/B/transfer prices do not make the multi-readout family cheaper.
        c=f.palette_screen((3,3,3))
        self.assertGreater(sum(c[k] for k in ('source_calls','readout_calls','transfers')),f.cost(f.best_single(9,1,1),1,1))
        # The 73-call/4-transfer alternative is dominated on both sides of s=c/3.
        for c,s in product((Fraction(1),Fraction(17,3)),(Fraction(1,100),Fraction(1,3),Fraction(2),Fraction(99))):
            self.assertGreaterEqual(73*c+4*s,min(74*c,72*c+6*s))

    def test_ram_backend_all_basis_inputs_dirty_scalar_and_inverse(self):
        n=3;width=2;maps=[[2,1],[1,3],[3,2]]
        for roots,word in ((1,f.construct((1,2))),(2,f.construct_palette((1,1,1)))):
            rows=n+(1<<n)-1+roots
            for coordinate in range(rows*width+1):
                data=[0]*(rows+1)
                if coordinate==rows*width:data[-1]=1
                else:data[coordinate//width]=1<<(coordinate%width)
                want=benchmark.expected(data,maps,n,roots)
                actual=list(data);benchmark.run_inplace(word,actual,maps,n,roots)
                self.assertEqual(actual,want)
                benchmark.run_inplace(list(reversed(word)),actual,maps,n,roots)
                self.assertEqual(actual,data)

    def test_signed_ram_backend_dirty_integer_and_literal_inverse(self):
        n=3;maps=[[[0,1],[0,0]], [[0,0],[1,0]], [[1,-1],[-1,0]]]
        for roots,word in ((1,f.construct_signed_single((1,2))),
                           (2,f.construct_signed_palette((1,1,1)))):
            rows=n+(1<<n)-1+roots
            for coordinate in range(rows*2+1):
                data=[[0,0] for _ in range(rows)]+[7]
                if coordinate<rows*2:data[coordinate//2][coordinate%2]=-3
                want=benchmark.expected_signed(data,maps,n)
                actual=[list(row) for row in data[:-1]]+[data[-1]]
                benchmark.run_signed_inplace(word,actual,maps,n,roots)
                self.assertEqual(actual,want)
                inverse=[op[:-1]+[-op[-1]] for op in reversed(word)]
                benchmark.run_signed_inplace(inverse,actual,maps,n,roots)
                self.assertEqual(actual,data)
        frontier=[f.signed_single_screen(sizes) for sizes in f.signed_single_frontier(9)]
        for partition in f.partitions(9):
            c=f.signed_single_screen(tuple(reversed(partition)))
            self.assertTrue(any(x['source_calls']<=c['source_calls'] and
                                x['readout_calls']<=c['readout_calls'] for x in frontier))

    def test_global_bounds_concave_endpoints_and_separation(self):
        for n in range(1,10):
            for roots in (1,2):
                for b in (1,3,49):
                    threshold=f.capacity_threshold(n,roots)
                    step=2 if roots==1 else 1
                    masks=(1<<n)-1; base=4 if roots==1 else 3; mult=1 if roots==1 else 3
                    exhaustive=min(k*b+max(2*masks,base*masks-(base-2)*mult*k*(k-1)//2)
                                   for k in range(2*n,threshold+7,step))
                    self.assertEqual(f.global_lower_bound(n,b,1,roots),exhaustive)
        for n in (9,12,15,18,30):
            b=f.critical_tariff(n);candidate=f.palette_cost(f.balanced_three(n),b,1,1)
            self.assertLess(candidate,f.global_lower_bound(n,b,1,1))
            self.assertGreaterEqual(candidate,f.global_lower_bound(n,b,1,2))
        for n in (30,60,90):
            masks=(1<<n)-1;b=f.critical_tariff(n)
            self.assertGreater(f.global_lower_bound(n,b,1,1),3*masks)
            self.assertGreaterEqual(f.global_lower_bound(n,b,1,2),3*masks)
        with self.assertRaises(ValueError):f.global_lower_bound(5,1,1,3)

    def test_reject_empty_blocks_and_unpriced_tariff(self):
        for sizes in ((),(0,1,1),(-1,2,2),(True,1,1)):
            with self.assertRaises(ValueError):f.validate(sizes)
        with self.assertRaises(ValueError):f.cost((2,2),0,1)
        with self.assertRaises(ValueError):f.construct_palette((2,2))
        with self.assertRaises(ValueError):f.construct((19,))


if __name__=='__main__':unittest.main()
