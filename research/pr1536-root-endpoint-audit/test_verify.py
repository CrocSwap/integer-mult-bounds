#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Arithmetic, actual rounding mutants, source integrity and relocation controls."""
from fractions import Fraction as F
import importlib.util
import json
from math import isqrt
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('root_audit',HERE/'verify.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


class RootAuditTests(unittest.TestCase):
    def test_rounding_all_small_and_large_square_boundaries(self):
        values = list(range(4096))
        for root in (2**64-1,2**255+17,2**1024+1):
            values.extend([root*root-1,root*root,root*root+1])
        for n in values:
            r = v.ceil_sqrt(n)
            self.assertGreaterEqual(r*r,n)
            self.assertTrue(r == 0 or (r-1)**2 < n)
        for n in range(64):
            for d in range(1,33):
                r = v.ceil_div(n,d)
                self.assertGreaterEqual(r*d,n)
                self.assertLess((r-1)*d,n)

    def test_exact_cleared_power_inequalities_nondyadic_exponents(self):
        for base in (F(1),F(3,2),F(73,48),F(73),F(16,9)):
            for p,q in ((0,1),(1,1),(1,3),(2,5),(7,11),(5,8)):
                lo,hi = v.power_bounds(base,F(p,q),32,128)
                self.assertLessEqual(lo**q,base**p)
                self.assertGreaterEqual(hi**q,base**p)
        self.assertEqual(v.power_bounds(F(1),F(1,3)),(F(1),F(1)))
        self.assertEqual(v.power_bounds(F(73),F(0)),(F(1),F(1)))

    def test_actual_sqrt_rounding_mutation_fails_power_inequality(self):
        v.root_ladder.cache_clear()
        with patch.object(v,'ceil_sqrt',isqrt):
            _,hi = v.power_bounds(F(2),F(1,2),8,32)
            self.assertLess(hi*hi,2)
        v.root_ladder.cache_clear()
        _,hi = v.power_bounds(F(2),F(1,2),8,32)
        self.assertGreaterEqual(hi*hi,2)

    def test_actual_product_rounding_mutation_fails_power_inequality(self):
        v.root_ladder.cache_clear()
        roots = v.root_ladder(F(9,4),8,16)
        with patch.object(v,'ceil_div',lambda n,d:n//d):
            _,upper = v.dyadic_product(192,roots,16)  # exponent 3/4
        self.assertLess(F(upper,2**16)**4,F(9,4)**3)
        _,upper = v.dyadic_product(192,roots,16)
        self.assertGreaterEqual(F(upper,2**16)**4,F(9,4)**3)

    def test_exponent_truncation_cannot_be_used_as_upper(self):
        roots = v.root_ladder(F(73),8,128)
        n = (F(1,3)*2**8).__floor__()
        _,unsafe = v.dyadic_product(n,roots,128)
        self.assertLess(F(unsafe,2**128)**3,73)
        _,safe = v.power_bounds(F(73),F(1,3),8,128)
        self.assertGreaterEqual(safe**3,73)

    def test_invalid_domain_and_unresolved_intervals(self):
        for args in ((F(1,2),F(1,3)),(F(2),F(-1)),(F(2),F(2))):
            with self.assertRaises(ValueError):
                v.power_bounds(*args)
        for precision in (0,-1,True,4097):
            with self.assertRaises(ValueError):
                v.power_bounds(F(2),F(1,2),8,precision)
        self.assertEqual(v.sign((F(0),F(1))),0)
        self.assertEqual(v.sign((F(-1),F(0))),0)
        for expected in (-1,1):
            with self.assertRaisesRegex(ValueError,'unresolved'):
                v.strict_decision((F(-1),F(1)),expected)
        with self.assertRaisesRegex(ValueError,'incorrect endpoint'):
            v.strict_decision((F(-2),F(-1)),1)

    def test_certificate_and_mathematical_controls(self):
        report = v.audit()
        self.assertEqual(report,json.loads((HERE/'CERTIFICATE.json').read_bytes()))
        self.assertEqual([r['sign'] for r in report['decisions']],[-1,1,-1,1])
        self.assertEqual(report['rank_mass'],4816512)
        self.assertEqual(report['deficit'],23680)
        self.assertEqual(len(report['controls']['semantic_controls']),12)
        # Bind the compact rational display intervals in the README to evidence.
        ticks = [(-1232,-1231),(1690,1691),(-986,-985),(1935,1936)]
        for row,(low,high) in zip(report['decisions'],ticks):
            lo,hi = map(F,row['residual'])
            self.assertLessEqual(low*v.GRID/1000,lo)
            self.assertGreaterEqual(high*v.GRID/1000,hi)

    def test_each_source_corruption_rejected(self):
        pins = json.loads((HERE/'INPUTS.json').read_bytes())
        with tempfile.TemporaryDirectory(prefix='pr1536-source-',dir=HERE.parent) as temp:
            package = Path(temp)/'package'
            shutil.copytree(HERE,package)
            for source in pins['files']:
                path = package/source['local_path']
                original = path.read_bytes()
                path.write_bytes(original+b'\n')
                with self.assertRaisesRegex(ValueError,'source bytes mismatch'):
                    v.read_inputs(package)
                path.write_bytes(original)
            self.assertEqual(v.read_inputs(package),v.read_inputs())

    def test_pin_inventory_and_head_corruption_rejected(self):
        with tempfile.TemporaryDirectory(prefix='pr1536-pins-',dir=HERE.parent) as temp:
            package = Path(temp)/'package'
            shutil.copytree(HERE,package)
            path = package/'INPUTS.json'
            pins = json.loads(path.read_bytes())
            pins['source_head'] = '0'*40
            path.write_text(json.dumps(pins))
            with self.assertRaisesRegex(ValueError,'head mismatch'):
                v.read_inputs(package)
            pins = json.loads((HERE/'INPUTS.json').read_bytes())
            pins['files'].pop()
            path.write_text(json.dumps(pins))
            with self.assertRaisesRegex(ValueError,'inventory mismatch'):
                v.read_inputs(package)

    def test_optimized_relocated_read_only_replay_and_certificate_corruption(self):
        with tempfile.TemporaryDirectory(prefix='pr1536-relocate-',dir=HERE.parent) as temp:
            package = Path(temp)/'package'
            shutil.copytree(HERE,package)
            command = [sys.executable,'-I','-O','-B',str(package/'verify.py')]
            before = {p.relative_to(package):p.read_bytes() for p in package.rglob('*') if p.is_file()}
            done = subprocess.run(command,cwd=temp,text=True,capture_output=True,timeout=30)
            self.assertEqual(done.returncode,0,done.stderr)
            self.assertIn('PASS_PR1536_INTEGER_ROOT_ENDPOINT_AUDIT',done.stdout)
            after = {p.relative_to(package):p.read_bytes() for p in package.rglob('*') if p.is_file()}
            self.assertEqual(before,after)
            cert_path = package/'CERTIFICATE.json'
            cert = json.loads(cert_path.read_bytes())
            cert['decisions'][1]['sign'] = -1
            cert_path.write_text(json.dumps(cert))
            done = subprocess.run(command,cwd=temp,text=True,capture_output=True,timeout=30)
            self.assertNotEqual(done.returncode,0)
            self.assertIn('certificate mismatch',done.stderr)


if __name__ == '__main__':
    unittest.main()
