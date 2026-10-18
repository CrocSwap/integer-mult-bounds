#!/usr/bin/env python3
"""Independent Decimal diagnostics and failure controls (not interval proofs)."""
import importlib.util
import json
from decimal import Decimal as D, localcontext
from fractions import Fraction as Q
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('tensor_rate_audit', HERE/'verify.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def dec(x):
    x = Q(x)
    return D(x.numerator)/D(x.denominator)


class AuditTests(unittest.TestCase):
    def test_source_depth_one_and_two_histograms(self):
        # Literal independently published histograms in PR647 sections 8/README.
        self.assertEqual(dict(audit.lifetime_profile(1)[0]),
                         {1:41040,2:240,7:20160,8:1440,9:48})
        self.assertEqual(dict(audit.lifetime_profile(2)[0]),
                         {1:4968000,2:28800,8:86400,9:328320,63:161280,
                          72:92160,79:2419200,80:129600,81:384})

    def test_log_bounds_with_separate_decimal_implementation(self):
        values = [Q(1),Q(3,2),Q(2),Q(3),Q(27,7),Q(243,242),Q(3*9**66)]
        values += [Q(3*9**6,s) for s in audit.closed_profile(6)]
        with localcontext() as ctx:
            ctx.prec = 120
            for x in values:
                lo,hi = audit.log_bounds(x)
                expected = dec(x).ln()
                self.assertLessEqual(dec(lo),expected)
                self.assertLessEqual(expected,dec(hi))
                self.assertLess(hi-lo,Q(1,10**50))

    def test_root_brackets_by_direct_high_precision_moments(self):
        # A different implementation evaluates the nonlinear moment directly.
        # This is a diagnostic; the proof of the rational enclosure is analytic.
        with localcontext() as ctx:
            ctx.prec = 250
            for n in (1,2,3,6,16,66):
                h,v,_,_,_,m,deficit = audit.parameters(n)
                hist = audit.closed_profile(n)
                lo,hi = map(Q,audit.audit(n)['scaled_root_bounds'])
                logs = {s:(D(m)/D(s)).ln() for s in hist}
                def increase(scaled):
                    k = dec(scaled)/D(h)
                    return sum(D(s*c)*((k*logs[s]).exp()-1) for s,c in hist.items())
                self.assertLess(increase(lo),D(deficit))
                self.assertGreater(increase(hi),D(deficit))

    def test_cost_and_same_mass_mutants(self):
        self.assertEqual(len(audit.negative_controls()),9)

    def test_invalid_domain_and_optimized_failure(self):
        for depth in (0,-1,True,Q(3,2)):
            with self.assertRaises(ValueError):
                audit.parameters(depth)
        # A corrupted receipt must fail even when Python disables assertions.
        result = json.loads((HERE/'RESULTS.json').read_text())
        result['depths'][0]['helpers'] += 1
        with tempfile.TemporaryDirectory() as directory:
            bad = Path(directory)/'bad.json'
            bad.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
            proc = subprocess.run([sys.executable,'-B','-I','-O',str(HERE/'verify.py'),
                                   '--check',str(bad)],capture_output=True,text=True)
            self.assertNotEqual(proc.returncode,0)
            self.assertIn('receipt mismatch',proc.stderr)


if __name__ == '__main__':
    unittest.main()
