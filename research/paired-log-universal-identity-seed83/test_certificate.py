#!/usr/bin/env python3
"""Failure controls for the independent block-certificate checker.

Copyright 2026 Sricharan Vagvala (@theon199). Apache-2.0.
Substantial OpenAI Codex assistance.
"""
from copy import deepcopy
from pathlib import Path
import gzip
import importlib.util
import json
import unittest

PACKAGE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("block_checker", PACKAGE / "check_certificate.py")
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class CertificateControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = json.loads(gzip.decompress((PACKAGE / "CERTIFICATE.json.gz").read_bytes()))
        cls.recipe = json.loads(gzip.decompress((checker.ROOT / checker.RECIPE).read_bytes()))

    def test_positive_certificate(self):
        result = checker.audit(self.original, self.recipe)
        self.assertEqual(result, {"two_sided_block_identities": 578,
                                 "forward_monomials": 541, "decoder_monomials": 2070,
                                 "maximum_word_length": 10})

    def test_mutated_coefficient_and_reader(self):
        changed = deepcopy(self.original)
        changed["decoder"][0]["terms"][0][1] *= -1
        with self.assertRaisesRegex(ValueError, "inverse certificate failed"):
            checker.audit(changed, self.recipe)
        changed = deepcopy(self.original)
        reader = next(term for term in changed["decoder"][8]["terms"]
                      if term[0] == 4 and term[2] == ["R0"])
        reader[2] = ["R8"]
        with self.assertRaisesRegex(ValueError, "inverse certificate failed"):
            checker.audit(changed, self.recipe)

    def test_two_fake_identity_maps(self):
        changed = deepcopy(self.original)
        identity = [{"codomain": checker.SPACES[i], "terms": [[i, 1, []]]}
                    for i in range(17)]
        changed["forward"] = identity
        changed["decoder"] = identity
        with self.assertRaisesRegex(ValueError, "elementary matrices"):
            checker.audit(changed, self.recipe)

    def test_numeric_and_shape_errors(self):
        for value in (True, 1.0, 0):
            with self.subTest(coefficient=value):
                changed = deepcopy(self.original)
                changed["decoder"][0]["terms"][0][1] = value
                with self.assertRaisesRegex(ValueError, "invalid coefficient"):
                    checker.audit(changed, self.recipe)
        changed = deepcopy(self.original)
        changed["decoder"][0]["terms"][0][0] = True
        with self.assertRaisesRegex(ValueError, "invalid input index"):
            checker.audit(changed, self.recipe)
        changed = deepcopy(self.original)
        changed["decoder"].pop()
        with self.assertRaisesRegex(ValueError, "invalid block matrix"):
            checker.audit(changed, self.recipe)

    def test_operator_order_is_preserved(self):
        self.assertEqual(checker.reduce_right(("R8", "P8")), ())
        self.assertEqual(checker.reduce_right(("R8", "P3")), ("R8", "P3"))
        first = checker.reduce_right(("Z8", "R3", "P3", "R8"))
        second = checker.reduce_right(("P3", "R8", "Z8", "R3"))
        self.assertNotEqual(first, second)


if __name__ == "__main__":
    unittest.main(verbosity=2)
