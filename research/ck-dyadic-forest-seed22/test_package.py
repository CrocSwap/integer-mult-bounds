"""Focused adverse controls; Lauren, substantial OpenAI Codex assistance."""
import importlib.util
from pathlib import Path
import gzip
import json
import tempfile
import unittest
from fractions import Fraction as Q

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("ck_dyadic_verify", HERE / "verify.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


class ExactControls(unittest.TestCase):
    def test_prices(self):
        self.assertEqual([v.price(Q(a, 4)) for a in range(5)], [0, 6, 5, 8, 4])
        for a in range(-100, 101):
            for k in range(8):
                self.assertEqual(v.price(Q(a, 2**k)), v.price(Q(-a, 2**k)))
        with self.assertRaises(ValueError):
            v.price(Q(1, 3))

    def test_nonunit_can_win_on_other_data(self):
        child, parent = [3] * 2, [1] * 2
        best = min(v.row_price(child), v.edge_price(child, parent, Q(1)),
                   v.edge_price(child, parent, Q(-1)))
        self.assertEqual(v.edge_price(child, parent, Q(3)) - best, -4)

    def test_boundary_work_is_charged(self):
        self.assertEqual(v.edge_price([3] * 8, [1] * 8, Q(3)), 12)

    def test_cost_matches_literal_horner(self):
        for a in range(-35, 36):
            for k in range(6):
                q = Q(a, 2**k)
                word = v.horner(q)
                self.assertEqual(len(word), v.price(q))
                self.assertEqual(v.run_horner(word), (Q(1), q, Q(0)))

    def test_mutated_lowerings_rejected(self):
        word = v.horner(Q(3, 4))
        wanted = (Q(1), Q(3, 4), Q(0))
        for i in range(len(word)):
            try:
                actual = v.run_horner(word[:i] + word[i+1:])
            except ValueError:
                continue  # Removing the final clear must fail the work check.
            self.assertNotEqual(actual, wanted)

    def test_certificate_types(self):
        self.assertFalse(v.exact_equal({"count": 1}, {"count": True}))
        self.assertFalse(v.exact_equal({"count": 1}, {"count": 1.0}))

    def test_actual_ck_needs_same_parent_alternative(self):
        rows, _ = v.source_rows()
        child, parent = rows[114-112], rows[184-112]
        cost = v.edge_price(child, parent, Q(-3))
        self.assertEqual((cost, v.row_price(child)), (353, 469))
        self.assertLess(min(v.edge_price(child, parent, Q(1)),
                            v.edge_price(child, parent, Q(-1))), cost)

    def test_source_corruption_and_recompression(self):
        pins = json.loads((HERE / "SOURCES.json").read_text())
        with tempfile.TemporaryDirectory(prefix="ck dyadic ") as directory:
            root = Path(directory)
            for name in pins["files"]:
                dest = root / name
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes((v.ROOT / name).read_bytes())
            rows, _ = v.source_rows(root)
            path = root / v.WORD
            original = gzip.decompress(path.read_bytes())
            path.write_bytes(gzip.compress(original, compresslevel=1, mtime=123))
            self.assertEqual(v.source_rows(root)[0], rows)
            altered = json.loads(original)
            altered["compensation"][0][3] *= -1
            path.write_bytes(gzip.compress(json.dumps(altered).encode(), mtime=0))
            with self.assertRaisesRegex(ValueError, "source pin"):
                v.source_rows(root)

    def test_written_tail_boundaries(self):
        # Diagnostic boundary checks complement the universal written proof.
        for a in range(-4, 5):
            for b in range(-4, 5):
                for q in (Q(1,16), Q(-1,16), Q(3,32), Q(-33,16), Q(68), Q(-68), Q(1025)):
                    self.assertGreaterEqual(v.price(Q(a,4)-q*Q(b,4)), v.price(Q(a,4)))


if __name__ == "__main__":
    unittest.main()
