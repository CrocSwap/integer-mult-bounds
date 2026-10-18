#!/usr/bin/env python3
"""Independent bound checks and package faults; standard library, Apache-2.0."""
from fractions import Fraction
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("chirp_audit", HERE / "verify.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class Mathematics(unittest.TestCase):
    def test_guard_bound_by_repeated_doubling(self):
        # Different integer procedure from guard_bits()/bit_length().
        for p in (*range(257), 303, 3434, 8738):
            q = 2**p
            bound = (q+32)*(q+2)
            radix, guard = q*q, 0
            while radix <= bound:
                radix *= 2
                guard += 1
            self.assertEqual(audit.guard_bits(p), guard)
            self.assertLess(bound, radix)
            self.assertGreaterEqual(bound, radix//2)
            for length in (1,2,3,8,68):
                for magnitude in (Fraction(1),Fraction(3,2),Fraction(7,3),Fraction(16)):
                    coefficient_bound = length*int(magnitude*(q+32))*(q+2)
                    bits = audit.slot_bits(p,magnitude,length,guard)
                    self.assertLess(coefficient_bound, 2**bits)

    def test_log_boundary(self):
        for k in range(1,101):
            self.assertEqual(audit.ceil_log2(2**k), k)
            self.assertEqual(audit.ceil_log2(Fraction(3*2**k-1,3)), k)
            self.assertEqual(audit.ceil_log2(Fraction(3*2**k+1,3)), k+1)

    def test_high_precision_alias_with_nonzero_ideal_kernel(self):
        p, outputs = 101, 2
        q = 2**p
        # Ideal g=1, K_0=1, K_-1=1/Q>0. The latter may round to zero.
        # Both approximations are within the source's stated inner errors.
        self.assertLessEqual(Fraction(1,q), Fraction(2,q))
        true = [(q+32)*(q+2), 0]
        bad = audit.packed([q+32],[0],[0,q+2],outputs,2*p)
        self.assertNotEqual([x[0] for x in bad], true)
        self.assertEqual(bad[0][0]+q*q*bad[1][0], true[0])
        self.assertEqual(bad[1][0], 1)
        good = audit.packed([q+32],[0],[0,q+2],outputs,2*p+1)
        self.assertEqual([x[0] for x in good], true)

    def test_error_envelope_and_missing_terms(self):
        for p in (*range(12),101,303):
            q = 2**p
            # All errors align: exact error is 34/Q+64/Q^2.
            error = Fraction((q+32)*(q+2),q*q)-1
            self.assertEqual(error, Fraction(34,q)+Fraction(64,q*q))
            self.assertLessEqual(error, Fraction(98,q))
            self.assertLess(error, Fraction(128,q))
            self.assertGreater(error, Fraction(32,q))

    def test_domain_rejections(self):
        for action in (
            lambda: audit.guard_bits(-1),
            lambda: audit.guard_bits(True),
            lambda: audit.slot_bits(3,Fraction(1,2),2),
            lambda: audit.slot_bits(3,1,0),
            lambda: audit.packed([1],[],[1],1,8),
            lambda: audit.packed([1],[0],[1,2],1,8),
            lambda: audit.check_case([37],[0],[1],1,2,1),
            lambda: audit.check_case([1],[0],[7],1,2,1),
            lambda: audit.pack_unsigned([256],8),
            lambda: audit.unpack_unsigned(256,8,1),
        ):
            with self.assertRaises(ValueError):
                action()


class Package(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="chirp audit relocation ")
        cls.root = Path(cls.temp.name)
        cls.package = cls.root / "research" / HERE.name
        shutil.copytree(HERE,cls.package,ignore=shutil.ignore_patterns("__pycache__"))
        records = json.loads((HERE/"SOURCES.json").read_text())["files"]
        for row in records:
            if row["usage"] == "input":
                destination = cls.root/row["path"]
                destination.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(audit.ROOT/row["path"],destination)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def run_verifier(self,*args):
        return subprocess.run([sys.executable,"-I","-O","-B",str(self.package/"verify.py"),*args],
                              cwd=self.root,capture_output=True,text=True,timeout=120)

    def test_relocated_replay(self):
        before = {p:p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        result = self.run_verifier()
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn("PASS_CHIRP_PACKED_CORRELATION",result.stdout)
        after = {p:p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(before,after)

    def test_source_drift(self):
        path = self.root/"notes"/"fast-gaussian-resampling.tex"
        original = path.read_bytes()
        try:
            path.write_bytes(original+b"\nmutation\n")
            result = self.run_verifier()
            self.assertNotEqual(result.returncode,0)
            self.assertIn("source drift",result.stderr)
        finally:
            path.write_bytes(original)

    def test_missing_source(self):
        path = self.root/"notes"/"chirp-scaling-correction.tex"
        original = path.read_bytes()
        try:
            path.unlink()
            result = self.run_verifier()
            self.assertNotEqual(result.returncode,0)
            self.assertIn("FileNotFoundError",result.stderr)
        finally:
            path.write_bytes(original)

    def test_receipt_drift(self):
        path = self.package/"RESULT.json"
        original = path.read_bytes()
        try:
            result = json.loads(original)
            result["counts"]["basis_packings"] -= 1
            path.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
            run = self.run_verifier()
            self.assertNotEqual(run.returncode,0)
            self.assertIn("receipt mismatch",run.stderr)
        finally:
            path.write_bytes(original)

    def test_occupied_output_preserved(self):
        path = self.root/"occupied.json"
        path.write_text("untouched\n")
        result = self.run_verifier("--write",str(path))
        self.assertNotEqual(result.returncode,0)
        self.assertIn("FileExistsError",result.stderr)
        self.assertEqual(path.read_text(),"untouched\n")


if __name__ == "__main__":
    unittest.main(verbosity=2)
