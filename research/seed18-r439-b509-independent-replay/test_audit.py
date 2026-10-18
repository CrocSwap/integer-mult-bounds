#!/usr/bin/env python3
"""Focused controls for the seed18 R439 frame-509 matrix audit."""

import importlib.util
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("seed18_matrix_verify", HERE / "verify.py")
verify = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(verify)


class MatrixAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.prior = verify.load_json(verify.HERE / verify.PRIOR)
        cls.candidate = verify.load_json(verify.HERE / verify.CANDIDATE)

    def test_receipt_replays(self):
        result = verify.audit()
        self.assertEqual(result["whole_word_ADD_invoice"],
                         {"selected": 24305, "predecessor": 24285, "candidate": 24283})
        self.assertEqual(result["integer_delta_prior_minus_candidate"],
                         [{"destination": 468, "source": 33, "prior_minus_candidate": 2}])

    def test_wrong_operand_breaks_boolean_endpoint(self):
        mutated = json.loads(json.dumps(self.candidate["gates"]))
        mutated[0][2][0] = 60 if mutated[0][2][0] != 60 else 67
        before = verify.local_map(self.prior["gates"], verify.WIRES, True)
        after = verify.local_map(mutated, verify.WIRES, True)
        self.assertNotEqual(before, after)

    def test_omitted_gate_breaks_boolean_endpoint(self):
        mutated = self.candidate["gates"][:-1]
        before = verify.local_map(self.prior["gates"], verify.WIRES, True)
        after = verify.local_map(mutated, verify.WIRES, True)
        self.assertNotEqual(before, after)


if __name__ == "__main__":
    unittest.main(verbosity=2)
