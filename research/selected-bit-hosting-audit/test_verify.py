"""Independent matrix algebra and rejection controls for the finite audit.

Prepared for commdata2338 with substantial OpenAI Codex assistance. Apache-2.0.
"""
from contextlib import redirect_stdout
from fractions import Fraction as Q
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

PACKAGE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("hosting_audit", PACKAGE / "verify.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def multiply(a, b):
    return [[sum(x * y for x, y in zip(row, col)) for col in zip(*b)] for row in a]


def operator(p):
    """Dense rational D(P), independently of the verifier's bit-mask operation."""
    n = len(p)
    complement = [[Q(i == j) - p[i][j] for j in range(n)] for i in range(n)]
    return [complement[i] + p[i] for i in range(n)] + [p[i] + complement[i] for i in range(n)]


def diagonal(bits):
    return [[Q(i == j and (bits >> i) & 1) for j in range(2)] for i in range(2)]


class AuditTests(unittest.TestCase):
    def test_complete_finite_receipt(self):
        expected = json.loads((PACKAGE / "RESULT.json").read_text())
        self.assertEqual(audit.verify(), expected)
        self.assertEqual(len(expected["rejected_controls"]), 12)

    def test_disjoint_union_vs_overlapping_symmetric_difference(self):
        for p in range(4):
            for q in range(4):
                actual = multiply(operator(diagonal(p)), operator(diagonal(q)))
                self.assertEqual(actual, operator(diagonal(p ^ q)))
                if p & q:
                    self.assertNotEqual(actual, operator(diagonal(p | q)))
                else:
                    self.assertEqual(actual, operator(diagonal(p | q)))
                for basis_column in range(4):
                    head = (1 << basis_column) if basis_column < 2 else 0
                    tail = (1 << (basis_column - 2)) if basis_column >= 2 else 0
                    h, t = audit.d_apply(p, *audit.d_apply(q, head, tail))
                    dense = [actual[i][basis_column] for i in range(4)]
                    self.assertEqual(dense, [Q((h >> i) & 1) for i in range(2)] +
                                     [Q((t >> i) & 1) for i in range(2)])

    def test_noncommuting_projectors_are_not_coordinate_factors(self):
        p = diagonal(1)
        q = [[Q(1, 2), Q(1, 2)], [Q(1, 2), Q(1, 2)]]
        self.assertEqual(multiply(q, q), q)
        self.assertNotEqual(multiply(p, q), multiply(q, p))
        self.assertNotEqual(multiply(operator(p), operator(q)), multiply(operator(q), operator(p)))

    def test_split_q_perp_is_outside_the_completion_free_argument(self):
        with self.assertRaisesRegex(audit.Reject, "whole q-perp"):
            audit.port_projectors({"lines": []}, [(0, 0, 0, 0, 1 << 1)], {})

    def test_changed_source_bytes_rejected_before_computation(self):
        pins = json.loads((PACKAGE / "SOURCES.json").read_text())
        source = next(p for p in pins["files"] if p["usage"] == "input")
        with tempfile.TemporaryDirectory(prefix="bit-host-source-", dir=PACKAGE) as folder:
            root = Path(folder)
            target = root / source["path"]
            target.parent.mkdir(parents=True)
            target.write_bytes((audit.ROOT / source["path"]).read_bytes() + b" ")
            with patch.object(audit, "ROOT", root):
                with self.assertRaisesRegex(audit.Reject, "source hash"):
                    audit.source_bindings()

    def test_changed_committed_receipt_rejected_by_cli(self):
        with tempfile.TemporaryDirectory(prefix="bit-host-receipt-", dir=PACKAGE) as folder:
            package = Path(folder)
            (package / "SOURCES.json").write_bytes((PACKAGE / "SOURCES.json").read_bytes())
            receipt = json.loads((PACKAGE / "RESULT.json").read_text())
            receipt["physical_census"]["helper_occurrences"] -= 1
            (package / "RESULT.json").write_text(json.dumps(receipt))
            with patch.object(audit, "PACKAGE", package), patch("sys.argv", ["verify.py"]):
                with redirect_stdout(io.StringIO()), self.assertRaisesRegex(SystemExit, "receipt mismatch"):
                    audit.main()


if __name__ == "__main__":
    unittest.main()
