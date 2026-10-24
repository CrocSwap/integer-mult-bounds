"""Failure controls on the actual frozen source joins, without producer replay."""
from pathlib import Path
import copy
import unittest

import oracle as o
import verify

HERE = Path(__file__).resolve().parent / "frozen"


def load(view):
    path = HERE / view
    return (o.decode((path / "candidate.json").read_bytes()),
            {p.name: p.read_bytes() for p in (path / "artifacts").iterdir()},
            o.decode((path / "policy.json").read_bytes()))


class ActualJoinControls(unittest.TestCase):
    def test_both_exact_source_joins(self):
        for view, expected in (("joined-v5", "151333/50000000"),
                               ("joined-5387-v4", "605334953/200000000000")):
            with self.subTest(view=view):
                c, a, p = load(view)
                result = o.evaluate(o.encode(c), a, p)
                self.assertEqual(result["label"], "FUNDED_CONDITIONAL")
                self.assertEqual(result["funded_kappa"], expected)
                self.assertEqual(result["blocking_obligations"], [])
                self.assertTrue(result["selected_is_read_only"])

    def test_equal_histograms_cannot_reuse_old_physical_receipt(self):
        old, old_a, _ = load("joined-v5")
        new, new_a, p = load("joined-5387-v4")
        self.assertEqual(old["profile"], new["profile"])
        self.assertNotEqual(old["literal_witness_sha256"], new["literal_witness_sha256"])
        new["receipts"]["physical"] = old["receipts"]["physical"]
        new_a.update(old_a)
        with self.assertRaisesRegex(o.ContractError, "UNTRUSTED_RECEIPT_SHA256:physical"):
            o.evaluate(o.encode(new), new_a, p)

    def test_real_source_artifact_corruption_or_omission_fails(self):
        for view in ("joined-v5", "joined-5387-v4"):
            for mutation in ("corrupt", "missing"):
                with self.subTest(view=view, mutation=mutation):
                    c, a, p = load(view)
                    dep = c["source_dependencies"]["invoice"]
                    if mutation == "corrupt":
                        a[dep] += b" "
                    else:
                        del a[dep]
                    with self.assertRaises(o.ContractError):
                        o.evaluate(o.encode(c), a, p)

    def test_missing_fresh_closure_does_not_fund(self):
        c, a, p = load("joined-5387-v4")
        del c["receipts"]["closure"]
        # Arithmetic must bind the closure actually attached to this candidate.
        with self.assertRaisesRegex(o.ContractError, "ARITHMETIC_NOT_BOUND_TO_CLOSURE"):
            o.evaluate(o.encode(c), a, p)

    def test_fixed_reviewer_policy_rejects_candidate_authored_domain(self):
        for view in ("joined-v5", "joined-5387-v4"):
            _, _, p = load(view)
            forged = copy.deepcopy(p)
            forged["parameter_domain"].append({"power": 2048})
            with self.assertRaisesRegex(o.ContractError, "TRUSTED_POLICY_CHANGED"):
                verify.check_policy(view, o.encode(forged))

    def test_arithmetic_does_not_grant_publication_or_selection(self):
        c, a, p = load("joined-5387-v4")
        for requested in ("PUBLIC_REVIEWABLE", "SELECTED"):
            c["requested_label"] = requested
            with self.assertRaisesRegex(o.ContractError, "UNSUPPORTED_PROMOTION"):
                o.evaluate(o.encode(c), a, p)


if __name__ == "__main__":
    unittest.main(verbosity=2)
