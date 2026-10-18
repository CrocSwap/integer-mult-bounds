"""Behavioral controls for the finite native numerical implication.

Sricharan Vagvala, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import bisect
import copy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import types
import unittest

HERE = Path(__file__).resolve().parent
V = types.ModuleType("current_native_audit")
V.__file__ = str(HERE / "verify.py")
exec(compile((HERE / "verify.py").read_bytes(), V.__file__, "exec"), V.__dict__)


class Controls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = V.load()
        cls.receipt = json.loads((HERE / "RESULT.json").read_text())

    def test_enumerated_binary_rounding_and_ties(self):
        # Enumerate a finite floating system, then select its nearest element.
        # This oracle does not discard significand bits or use float conversion.
        count = 0
        for bits in range(2, 8):
            positive = {Fraction(m) * Fraction(2) ** e
                        for m in range(2**(bits-1), 2**bits)
                        for e in range(-20, 13)}
            representable = sorted(positive | {-x for x in positive} | {Fraction(0)})
            for n in range(-1024, 1025):
                for denominator in (1, 8, 128):
                    q = Fraction(n, denominator)
                    at = bisect.bisect_left(representable, q)
                    if representable[at] == q:
                        expected = q
                    else:
                        low, high = representable[at-1:at+1]
                        if q-low != high-q:
                            expected = low if q-low < high-q else high
                        else:
                            expected = low if (low / (high-low)) % 2 == 0 else high
                    self.assertEqual(Fraction(V.nearest_integer(n, bits), denominator), expected)
                    count += 1
        self.assertEqual(count, 36882)

    def test_binary64_integer_rounding(self):
        rng = random.Random(30173036)
        for _ in range(5000):
            n = rng.randrange(-2**120, 2**120)
            self.assertEqual(V.nearest_integer(n, 53), int(float(n)))
        # Signed halfway cases at an exponent transition and within a binade.
        for n in (2**53+1, 2**53+3, 2**54-1, 2**54+2):
            for sign in (-1, 1):
                self.assertEqual(V.nearest_integer(sign*n, 53), int(float(sign*n)))

    def test_gaussian_butterfly_columns(self):
        # Independent displayed matrix formula on real and imaginary basis axes.
        exact = V.Dyadic(None)
        for axis in (1, 2, 4, 256):
            for at in (0, axis):
                for imaginary in (False, True):
                    re, im = [0] * 512, [0] * 512
                    (im if imaginary else re)[at] = 1
                    value = V.N.vector(re, im)
                    self.assertEqual(exact.line(value, axis), V.N.line(value, axis))
        # A sign error in the Gaussian crossing is visible on a real basis column.
        basis = V.N.vector([1] + [0]*511)
        forward = exact.line(basis, 1)
        backward = V.N.line(basis, 1, sign=-1)
        self.assertNotEqual(forward, backward)
        # The lowering order matters: ((T-1)-T)/2 loses the half-unit,
        # while the specified ((T-T)-(1-0))/2 retains it.
        re, im = [0]*512, [0]*512
        re[0], re[1], im[0] = 2**65, -2**65, 1
        paired = V.Dyadic(53).line(V.N.vector(re, im), 1)
        paired_real = Fraction(paired[0][0], 1 << paired[2])
        chained_real = ((float(2**65)-1.0) - float(2**65)) * 0.5
        self.assertEqual(paired_real, Fraction(-1, 2))
        self.assertEqual(chained_real, 0)
        self.assertNotEqual(paired_real, chained_real)

    def test_actual_literal_add_mutant_is_detected(self):
        altered = copy.deepcopy(self.data)
        altered[0][3887][1][3] = 1  # Literal -1/2 becomes +1/2.
        out, _, _ = V.run(altered)
        self.assertNotEqual(out, V.expected(rounded=True))

    def test_used_native_global_phase_is_detected(self):
        class PhaseMutant(V.Dyadic):
            changed = False

            def recipe(self, value, record, axes=9):
                if not self.changed and value != self.zero:
                    record = copy.deepcopy(record)
                    record["left"]["phase"] = (record["left"]["phase"] + 2) % 4
                    self.changed = True
                return super().recipe(value, record, axes)

        mutant = PhaseMutant(53)
        trace = []
        V.run(self.data, engine=mutant, trace=trace)
        self.assertTrue(mutant.changed)
        self.assertNotEqual(V.digest(trace), self.receipt["changed_field_trace_sha256"])

    def test_source_and_receipt_corruption(self):
        # Isolated roots keep the frozen source and normal receipt untouched.
        original_root = V.ROOT
        try:
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                for pin in json.loads((HERE / "SOURCES.json").read_text())["files"]:
                    if pin["usage"] == "input":
                        target = root / pin["path"]
                        target.parent.mkdir(parents=True, exist_ok=True)
                        target.write_bytes(b"corrupted scientific input")
                V.ROOT = root
                with self.assertRaisesRegex(ValueError, "Scientific source hash"):
                    V.load()
        finally:
            V.ROOT = original_root
        # Exercise the real CLI comparison with a replaced audit result, avoiding
        # another full replay merely to check receipt comparison.
        code = ("import sys,types;from pathlib import Path;"
                "p=Path(sys.argv[1]);m=types.ModuleType('v');m.__file__=str(p);"
                "exec(compile(p.read_bytes(),str(p),'exec'),m.__dict__);"
                "m.audit=lambda: {'bad':'receipt'};sys.argv=[str(p)];m.main()")
        result = subprocess.run([sys.executable, "-I", "-B", "-c", code,
                                 str(HERE / "verify.py")], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Result receipt mismatch", result.stderr)

    def test_native_primitive_source_is_authenticated(self):
        raw = (HERE / "vendor/native.py").read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), V.NATIVE_SHA)
        code = (HERE / "verify.py").read_text().replace(
            V.NATIVE_SHA, "0" * 64)
        module = types.ModuleType("bad_source")
        module.__file__ = str(HERE / "verify.py")
        with self.assertRaisesRegex(ValueError, "Pinned PR3017"):
            exec(compile(code, module.__file__, "exec"), module.__dict__)


if __name__ == "__main__":
    unittest.main()
