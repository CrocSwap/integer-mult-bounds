"""Focused exact controls, not a new selected-supplier admission.

Prepared for Adam Gall with OpenAI Codex assistance. Apache-2.0.
"""
import gzip
import itertools
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import recover
import verify


class ChartTests(unittest.TestCase):
    def test_elimination_all_three_dimensional_matrices(self):
        invertible = 0
        for columns in itertools.product(range(8), repeat=3):
            columns = list(columns)
            images = [verify.apply_columns(columns, x) for x in range(8)]
            if len(set(images)) < 8:
                with self.assertRaises(verify.Rejected):
                    verify.elimination_inverse(columns)
            else:
                inverse = verify.elimination_inverse(columns)
                invertible += 1
                for x in range(8):
                    self.assertEqual(verify.apply_columns(inverse, images[x]), x)
                    self.assertEqual(verify.apply_columns(columns, verify.apply_columns(inverse, x)), x)
        self.assertEqual(invertible, 168)

    def test_recovery_against_exhaustive_independent_factor_oracle(self):
        # Enumerate factors, rather than using the producer's anchor or matching.
        expected = set()
        for permutation in itertools.permutations(range(3)):
            for update, coefficients in itertools.product(range(8), repeat=2):
                if (update & coefficients).bit_count() % 2:
                    continue
                columns = []
                for j in range(3):
                    basis = [int(i == permutation[j]) for i in range(3)]
                    value = sum(basis[i] * ((coefficients >> i) & 1) for i in range(3)) % 2
                    columns.append(sum((basis[i] ^ (value * ((update >> i) & 1))) << i for i in range(3)))
                expected.add(tuple(columns))
        accepted = set()
        for columns in itertools.product(range(8), repeat=3):
            try:
                witness = recover.recover(list(columns))
            except ValueError:
                self.assertNotIn(columns, expected)
            else:
                verify.check_certificate(list(columns), witness, 3)
                accepted.add(columns)
        self.assertEqual(accepted, expected)
        self.assertLess(len(expected), 168)
        self.assertGreater(len(expected), 6)

    def test_dictionary_key_binds_order(self):
        identity = [1 << i for i in range(verify.N)]
        key = verify.digest(verify.canonical(identity))
        entries = {key: recover.recover(identity)}
        witnesses = {"format": "pr1879-five-array-chart-witnesses-v1", "dimension": verify.N, "entries": entries}
        self.assertEqual(verify.check_dictionary({key: identity}, witnesses)["charts"], 1)
        identity[0], identity[1] = identity[1], identity[0]
        entries[key] = recover.recover(identity)
        with self.assertRaisesRegex(verify.Rejected, "content key"):
            verify.check_dictionary({key: identity}, witnesses)

    def test_json_duplicate_and_numeric_policies(self):
        with self.assertRaises(verify.Rejected):
            verify.decode(b'{"k":0,"k":1}')
        with self.assertRaises(verify.Rejected):
            verify.decode(b'{"k":NaN}')
        for raw in (b"[true]", b"[1.0]", b"[1e0]", b"[-1]", b"[2]"):
            with self.assertRaises(verify.Rejected):
                verify.vector(verify.decode(raw), 1, 2, "bit")
        self.assertEqual(verify.vector(verify.decode(b"[1]"), 1, 2, "bit"), [1])

    def test_column_coefficient_is_after_permutation(self):
        witness = [[1, 2, 0], [2, 0, 1], [1, 4, 2], [1, 1, 0], [1, 1, 0]]
        verify.check_certificate(witness[2], witness, 3)
        wrongly_indexed = [(1 << witness[0][j]) ^ (3 if witness[4][j] else 0) for j in range(3)]
        witness[2] = wrongly_indexed
        with self.assertRaisesRegex(verify.Rejected, "coefficient"):
            verify.check_certificate(wrongly_indexed, witness, 3)

    def test_compression_headers_are_not_mathematical_identity(self):
        value = {"entries": {"k": [[0], [0], [1], [0], [0]]}}
        raw = verify.canonical(value)
        a, b = gzip.compress(raw, mtime=0), gzip.compress(raw, mtime=1)
        self.assertNotEqual(a, b)
        self.assertEqual(verify.canonical(verify.decode(gzip.decompress(a))),
                         verify.canonical(verify.decode(gzip.decompress(b))))

    def test_source_drift_is_rejected_before_archive_read(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = root / "research/community-frontier1094-audit/REPLAY.json"
            path.parent.mkdir(parents=True)
            path.write_text("{}\n")
            with patch.object(verify, "ROOT", root):
                with self.assertRaisesRegex(verify.Rejected, "changed source"):
                    verify.load_inputs()

    def test_all_odd_nonfull_ports_have_exact_orthogonal_bases(self):
        for q in range(511):
            if q.bit_count() % 2 == 0:
                continue
            columns = verify.port_basis(q)
            inverse = verify.elimination_inverse(columns)
            transpose = [sum(((column >> i) & 1) << j for j, column in enumerate(columns))
                         for i in range(verify.N)]
            self.assertEqual(inverse, transpose)


if __name__ == "__main__":
    unittest.main()
