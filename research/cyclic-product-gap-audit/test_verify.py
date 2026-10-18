"""Focused mathematical and source/receipt failure controls, stdlib only."""
from fractions import Fraction as F
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

P = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("product_gap_audit", P/"verify.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


class AuditTests(unittest.TestCase):
    def test_exact_two_site_witness(self):
        x, bs, exact = v.family(9, 2)
        actual = v.rounded_scan(x, bs, 11)
        self.assertEqual(v.dense_solve(x, bs), exact)
        self.assertEqual(actual[0][0], F(2731, 4))
        self.assertEqual(abs(actual[0][0]-exact[0][0]), F(1, 12))
        self.assertGreater(F(1, 12), F(1, 72))
        v.certify_output(actual, exact, v.certificate(x, bs, 11))

    def test_arbitrary_cut_lattice(self):
        for k in (1, 5, 13):
            for n in (2, 3, 9):
                x, bs, exact = v.family(k, n)
                for cut in range(n):
                    xx, bb = x[cut:]+x[:cut], bs[cut:]+bs[:cut]
                    actual = v.rounded_scan(xx, bb, 8)
                    big = (-cut) % n
                    self.assertGreaterEqual(abs(actual[big][0]-exact[0][0]), F(1 << k, 768))
                    self.assertEqual((actual[big][0]*256/(1 << k)).denominator, 1)

    def test_exact_inverse_norm_is_not_product_gap(self):
        for k in range(1, 9):
            _, bs, _ = v.family(k, 2)
            columns = [v.dense_solve([v.ONE, v.ZERO], bs),
                       v.dense_solve([v.ZERO, v.ONE], bs)]
            row_sums = [sum(abs(column[i][0]) for column in columns) for i in range(2)]
            self.assertEqual(max(row_sums), F(4*((1 << k)+1), 3))
            self.assertGreater(max(row_sums), F(4, 3))

    def test_complex_coefficients_and_zero_coefficients(self):
        for bs in ([v.ZERO], [(F(2), F(0)), (F(0), F(-1, 4))],
                   [(F(3, 5), F(4, 5)), v.ZERO, (F(-2), F(1))]):
            x = [(F(i+1, 3), F(1-i, 4)) for i in range(len(bs))]
            actual = v.rounded_scan(x, bs, 16)
            v.certify_output(actual, v.dense_solve(x, bs), v.certificate(x, bs, 16))

    def test_omitted_prefix_and_integer_guard_fail(self):
        x, bs, exact = v.family(9, 2)
        actual, cert = v.rounded_scan(x, bs, 11), v.certificate(x, bs, 11)
        bad = dict(cert, errors=[cert["seed_error"]+F(1, 2048)*q for q in cert["qs"]])
        with self.assertRaisesRegex(ValueError, "precision certificate"):
            v.certify_output(actual, exact, bad)
        with self.assertRaisesRegex(ValueError, "magnitude certificate"):
            v.certify_output(actual, exact, dict(cert, magnitude=F(4, 3)))

    def test_exact_gap_does_not_protect_rounded_denominator(self):
        b = (F(15, 16), F(0))
        self.assertEqual(v.sub(v.ONE, b), (F(1, 16), F(0)))
        self.assertEqual(v.grid(b, 3), v.ONE)
        with self.assertRaisesRegex(ValueError, "uncertified rounded denominator"):
            v.certificate([v.ONE], [b], 3)
        with self.assertRaisesRegex(ValueError, "singular cyclic operator"):
            v.dense_solve([v.ONE], [v.ONE])

    def test_grid_and_literal_cost_contract(self):
        for numerator in range(-32, 33):
            a = (F(numerator, 16), F(-numerator, 16))
            for bits in range(5):
                self.assertEqual(v.grid(a, bits), v.load_subject().rnd(a, bits))
        self.assertEqual(v.grid((F(-1, 2), F(1, 2)), 0), (F(0), F(1)))
        x, bs, _ = v.family(9, 2)
        subject = v.load_subject()
        _, height, rounds = v.replay_subject(subject, x, bs, F(3, 4), 11, 1)
        self.assertEqual(rounds, 7)
        self.assertLessEqual(height, v.certificate(x, bs, 11)["magnitude"]**2)
        original = subject.inverse_scan

        def hidden_extra_read(values, *args):
            _ = values[0]
            original(values, *args)

        subject.inverse_scan = hidden_extra_read
        with self.assertRaisesRegex(ValueError, "literal scan cost/access census"):
            v.replay_subject(subject, x, bs, F(3, 4), 11, 1)

    def test_source_corruption_and_missing_source(self):
        sources = v.check_sources()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for row in sources["files"]:
                if row["usage"] == "input":
                    dst = root/row["path"]
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(v.ROOT/row["path"], dst)
            v.check_sources(root)
            p = root/v.SUBJECT
            original = p.read_bytes()
            p.write_bytes(original+b"\n# mutation\n")
            with self.assertRaisesRegex(ValueError, "source drift"):
                v.check_sources(root)
            p.unlink()
            with self.assertRaisesRegex(ValueError, "missing source"):
                v.check_sources(root)

    def test_receipt_corruption_and_numeric_type(self):
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory)/"result.json"
            result = dict(status="PASS", cases=1)
            p.write_text(json.dumps(result))
            v.check_receipt(result, p)
            for wrong in (dict(status="FAIL", cases=1), dict(status="PASS", cases=True),
                          dict(status="PASS", cases=1.0), dict(status="PASS", cases=1, extra=0)):
                p.write_text(json.dumps(wrong))
                with self.assertRaisesRegex(ValueError, "receipt drift"):
                    v.check_receipt(result, p)


if __name__ == "__main__":
    unittest.main(verbosity=2)
