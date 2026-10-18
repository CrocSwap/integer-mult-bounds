"""Mathematical and source-boundary controls. Apache-2.0."""

import json
import tempfile
import unittest
from itertools import combinations
from pathlib import Path
from unittest.mock import patch

import independent
import verify


class CapacityControls(unittest.TestCase):
    def test_complete_receipt_and_independent_reconstruction(self):
        self.assertEqual(
            json.loads(json.dumps(verify.compute())),
            json.loads((verify.PACKAGE / "RESULT.json").read_bytes()),
        )
        independent.check()

    def test_ambient_radical_and_balanced_contracts(self):
        for args in ((5, 0, False), (4, 4, True), (5, 3, False), (6, 2, False)):
            with self.assertRaises(ValueError):
                verify.affine_bound(*args)
        self.assertEqual(verify.affine_bound(4, 0, False), 0)
        self.assertEqual(verify.affine_bound(5, 2, False), 8)
        self.assertEqual(verify.affine_bound(4, 2, False), 12)
        self.assertEqual(verify.affine_bound(5, 4, False), 20)

    def test_plus_type_is_necessary(self):
        # Hyperbolic q on F2^8. Translate by a vector with q(a)=1,
        # then add one. This changes the global Gauss sum to -16.
        def q(x):
            return (
                sum((x >> (2 * i) & 1) * (x >> (2 * i + 1) & 1) for i in range(4)) % 2
            )

        def minus(x):
            return q(x ^ 3) ^ q(3)

        self.assertEqual(sum((-1) ** minus(x) for x in range(256)), -16)
        lagrangian = verify.span((1, 4, 16, 64))
        affine4 = [3 ^ x for x in lagrangian]
        self.assertEqual(sum(minus(x) for x in affine4), 16)
        direction5 = verify.span((1, 2, 4, 16, 64))
        self.assertEqual(sum(minus(x) for x in direction5), 24)

    def test_affine_rank_relation(self):
        for dimension, offset, basis, _ in verify.WITNESSES:
            labels = [1 | ((offset ^ x) << 1) for x in verify.span(basis)]
            self.assertEqual(verify.rank(labels), dimension + 1)
            self.assertEqual(independent.dense_rank(labels, 9), dimension + 1)
        with self.assertRaises(ValueError):
            verify.span((1, 2, 3))
        with self.assertRaises(ValueError):
            verify.rank([512])

    def test_source_corruption_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / verify.GEOMETRY
            target.parent.mkdir(parents=True)
            target.write_bytes((verify.ROOT / verify.GEOMETRY).read_bytes() + b"\n")
            with self.assertRaisesRegex(ValueError, "bytes differ"):
                verify.authenticate(root)
            target.write_bytes(b"x" * 100_001)
            with self.assertRaisesRegex(ValueError, "byte bound"):
                verify.authenticate(root)

    def test_malformed_source_inventory_rejected(self):
        original = json.loads((verify.PACKAGE / "SOURCES.json").read_bytes())
        mutants = []
        duplicate = json.loads(json.dumps(original))
        duplicate["files"][2] = duplicate["files"][1]
        mutants.append(duplicate)
        extra = json.loads(json.dumps(original))
        extra["files"].append(extra["files"][0])
        mutants.append(extra)
        malformed = json.loads(json.dumps(original))
        malformed["files"][0]["sha256"] = "g" * 64
        mutants.append(malformed)
        escape = json.loads(json.dumps(original))
        escape["files"][0]["path"] = "../geometry.py"
        mutants.append(escape)
        for mutant in mutants:
            with tempfile.TemporaryDirectory() as directory:
                package = Path(directory)
                (package / "SOURCES.json").write_text(json.dumps(mutant))
                with (
                    patch.object(verify, "PACKAGE", package),
                    self.assertRaises(ValueError),
                ):
                    verify.authenticate()

    def test_gauss_identity_all_small_affine_planes(self):
        # Every affine plane in hyperbolic F2^4, including balanced radicals.
        def q(x):
            return ((x & 1) * (x >> 1 & 1) + (x >> 2 & 1) * (x >> 3 & 1)) % 2

        spaces = {
            tuple(sorted(verify.span(basis)))
            for basis in combinations(range(1, 16), 2)
            if verify.rank(basis, 4) == 2
        }
        self.assertEqual(len(spaces), 35)
        for space in spaces:
            radical = [
                h for h in space if all(q(x ^ h) ^ q(x) ^ q(h) == 0 for x in space)
            ]
            for offset in range(16):
                signed = sum((-1) ** q(offset ^ x) for x in space)
                radical_sum = sum((-1) ** (q(offset ^ h) ^ q(offset)) for h in radical)
                self.assertEqual(signed * signed, len(space) * radical_sum)


if __name__ == "__main__":
    unittest.main()
