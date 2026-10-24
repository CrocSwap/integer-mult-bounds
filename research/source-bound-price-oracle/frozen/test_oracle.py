"""Contract controls using explicitly synthetic evidence; no research admission."""
import copy
import unittest
from fractions import Fraction
import oracle as o


def synthetic(label="FUNDED_CONDITIONAL"):
    artifacts = {}
    def add(obj):
        raw = o.encode(obj)
        key = o.digest(raw)
        artifacts[key] = raw
        return key
    source = add({"SYNTHETIC_TEST_ONLY": "not research evidence"})
    c = {"schema": "source-bound-price-candidate/v1", "candidate_id": "SYNTHETIC",
         "scientific_head": "a"*40, "canonical_comparison_base": "b"*40,
         "source_dependencies": {"source": source}, "attribution": ["Synthetic test fixture"],
         "assumptions": list(o.ASSUMPTIONS), "literal_witness_sha256": source,
         "model": {"id": "SYNTHETIC", "parameters": {"power": 1}, "theorem_evidence_sha256": source},
         "profile": {"paid": {"1": 1}, "productive": {"2": 1}, "paid_jobs": 1,
                     "productive_jobs": 1, "excluded_productive_credit": {"aliases": 0, "copies": 0, "surrendered": 0}},
         "planes": {}, "receipts": {}, "requested_label": label}
    for plane in o.PLANES:
        c["planes"][plane] = [{"id": plane+"_charge", "state": "proved", "value_or_symbol": "SYNTHETIC",
                              "unit": "synthetic", "evidence_sha256": [source], "dependency_hashes": [source],
                              "invalidation_conditions": ["any synthetic premise changes"]}]
    p = {"candidate_id": c["candidate_id"], "scientific_head": c["scientific_head"],
         "canonical_comparison_base": c["canonical_comparison_base"], "source_dependencies": c["source_dependencies"],
         "model_id": "SYNTHETIC", "parameter_domain": [{"power": 1}],
         "charge_inventory": {plane: [plane+"_charge"] for plane in o.PLANES},
         "receipt_sha256": {}, "outer_predicate_ids": {"strict": ["s"], "functional": ["f"]},
         "arithmetic_check_ids": ["reserve", "tail", "adjacent_grid", "stock"],
         "optimization_scope": "SYNTHETIC_API_TEST_ONLY"}
    p["scientific_payload_sha256"] = o.digest(o.encode(o.scientific_payload(c)))
    for role in ("physical", "census", "closure", "arithmetic"):
        r = {"schema": "source-bound-price-receipt/v1", "role": role, "independent": True,
             "scientific_payload_sha256": p["scientific_payload_sha256"], "scientific_head": c["scientific_head"],
             "profile_sha256": o.profile_hash(c["profile"]), "source_dependencies": c["source_dependencies"],
             "coverage": list(o.COVERAGE[role]), "open_obligations": [], "evidence_sha256": [source]}
        if role == "arithmetic":
            r.update({"invoice_receipt_sha256": c["receipts"]["census"], "closure_receipt_sha256": c["receipts"]["closure"],
                      "model": c["model"], "funded_kappa": "1/100", "endpoint_funded": True, "tested_saving": "1/50",
                      "raw_root_interval": ["1/40", "1/30"], "root_sign_intervals": [["1", "2"], ["-2", "-1"]],
                      "compiler_domain": {"power": 1}, "strict_slacks": {"s": "1/1000"}, "functional_slacks": {"f": "1/10"},
                      "checks": {name: True for name in p["arithmetic_check_ids"]}, "same_five_assumptions": True})
        ref = add(r)
        c["receipts"][role] = ref
        p["receipt_sha256"][role] = ref
    return c, artifacts, p


def rebind_payload(c, artifacts, p):
    """Test-only trusted re-review lets a mutation reach its semantic guard."""
    newsha = o.digest(o.encode(o.scientific_payload(c)))
    p["scientific_payload_sha256"] = newsha
    for role in ("physical", "census", "closure", "arithmetic"):
        if role not in c["receipts"]:
            continue
        r = o.decode(artifacts[c["receipts"][role]])
        r["scientific_payload_sha256"] = newsha
        if role == "arithmetic":
            r["invoice_receipt_sha256"] = c["receipts"].get("census")
            r["closure_receipt_sha256"] = c["receipts"].get("closure")
        raw = o.encode(r)
        ref = o.digest(raw)
        artifacts[ref] = raw
        c["receipts"][role] = ref
        p["receipt_sha256"][role] = ref


class OracleContractControls(unittest.TestCase):
    def run_case(self, c, a, p):
        return o.evaluate(o.encode(c), a, p)

    def test_fully_bound_synthetic_api_path(self):
        c,a,p = synthetic()
        result = self.run_case(c,a,p)
        self.assertEqual(result["label"], "FUNDED_CONDITIONAL")
        self.assertEqual(result["funded_kappa"], "1/100")
        self.assertEqual(len(result["planes"]), 6)

    def test_candidate_mutations_rejected_even_after_test_trusted_rebind(self):
        mutations = {
            "stale_head": lambda c: c.update(scientific_head="c"*40),
            "stale_base": lambda c: c.update(canonical_comparison_base="c"*40),
            "alias_credit": lambda c: c["profile"]["excluded_productive_credit"].update(aliases=1),
            "copied_credit": lambda c: c["profile"]["excluded_productive_credit"].update(copies=1),
            "surrendered_credit": lambda c: c["profile"]["excluded_productive_credit"].update(surrendered=1),
            "missing_ordinary_charge": lambda c: c["planes"].update(ordinary=[]),
            "unsupported_model": lambda c: c["model"].update(id="anything"),
            "outside_proved_tuple": lambda c: c["model"].update(parameters={"power": 27}),
            "missing_plane": lambda c: c["planes"].pop("ownership_stock"),
            "unknown_as_zero": lambda c: c["planes"]["ordinary"][0].update(state="unknown", value_or_symbol=0),
            "missing_cost_invalidation": lambda c: c["planes"]["ordinary"][0].update(invalidation_conditions=[]),
            "wrong_histogram_census": lambda c: c["profile"].update(productive_jobs=2),
            "extra_assumption": lambda c: c["assumptions"].append("extra"),
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name):
                c,a,p = synthetic()
                mutate(c)
                rebind_payload(c,a,p)
                with self.assertRaises(o.ContractError):
                    self.run_case(c,a,p)

    def test_receipt_mutations_rejected(self):
        mutations = {
            "explicit_unfunded": lambda r: r.update(endpoint_funded=False),
            "unfunded_tested_endpoint": lambda r: r.update(funded_kappa="1/50"),
            "root_used_as_endpoint": lambda r: r.update(funded_kappa="1/40"),
            "failed_outer": lambda r: r.update(strict_slacks={"s": "0"}),
            "missing_outer": lambda r: r.update(functional_slacks={}),
            "stale_invoice": lambda r: r.update(invoice_receipt_sha256="0"*64),
            "unsupported_compiler": lambda r: r.update(compiler_domain={"power": 27}),
            "missing_grid": lambda r: r["checks"].pop("adjacent_grid"),
            "nonboolean_check": lambda r: r["checks"].update(stock="PASS"),
            "missing_coverage": lambda r: r.update(coverage=["PASS"]),
            "open_obligation": lambda r: r.update(open_obligations=["physical needed"]),
            "authored_pass_only": lambda r: (r.clear(), r.update(status="PASS")),
            "root_sign_overlap": lambda r: r.update(root_sign_intervals=[["-1", "1"], ["-2", "-1"]]),
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name):
                c,a,p = synthetic()
                r = o.decode(a[c["receipts"]["arithmetic"]])
                mutate(r)
                raw = o.encode(r); ref = o.digest(raw); a[ref] = raw
                c["receipts"]["arithmetic"] = ref
                p["receipt_sha256"]["arithmetic"] = ref
                with self.assertRaises(o.ContractError):
                    self.run_case(c,a,p)

    def test_unknown_or_optimistic_cost_cannot_promote(self):
        for state in ("unknown", "optimistically_relaxed"):
            c,a,p = synthetic("MODEL_ONLY")
            c["planes"]["ordinary"][0].update(state=state, value_or_symbol=None if state == "unknown" else "optimistic")
            rebind_payload(c,a,p)
            result = self.run_case(c,a,p)
            self.assertEqual(result["label"], "PHYSICAL_CHECKED")
            self.assertIsNone(result["funded_kappa"])
            c["requested_label"] = "FUNDED_CONDITIONAL"
            with self.assertRaisesRegex(o.ContractError, "UNSUPPORTED_PROMOTION"):
                self.run_case(c,a,p)

    def test_untrusted_or_corrupted_receipt(self):
        c,a,p = synthetic()
        ref = c["receipts"]["arithmetic"]
        a[ref] += b" "
        with self.assertRaisesRegex(o.ContractError, "ARTIFACT_HASH_MISMATCH"):
            self.run_case(c,a,p)
        c,a,p = synthetic()
        p["receipt_sha256"]["arithmetic"] = "0"*64
        with self.assertRaisesRegex(o.ContractError, "UNTRUSTED_RECEIPT_SHA256"):
            self.run_case(c,a,p)

    def test_selection_and_publication_not_inferred(self):
        for label in ("PUBLIC_REVIEWABLE", "SELECTED"):
            c,a,p = synthetic(label)
            with self.assertRaisesRegex(o.ContractError, "UNSUPPORTED_PROMOTION"):
                self.run_case(c,a,p)

    def test_equal_profile_does_not_transfer_physical_proof(self):
        c,a,p = synthetic()
        p.update(require_word_delta=True, prior_word_sha256=c["literal_witness_sha256"],
                 basis_physical_receipt_sha256=c["receipts"]["physical"],
                 word_delta_receipt_sha256=c["literal_witness_sha256"],
                 changed_dependencies=["preparation_order"])
        with self.assertRaisesRegex(o.ContractError, "MISSING_WORD_DELTA_RECEIPT"):
            self.run_case(c,a,p)

    def test_exact_json_and_duplicate_keys(self):
        for raw in (b'{"a":1,"a":2}', b'{"value":0.1}', b'{"value":NaN}'):
            with self.assertRaises(o.ContractError):
                o.decode(raw)

    def test_necessary_screen_cannot_fund(self):
        c,_,_ = synthetic()
        def backend(hist, exponent):
            self.assertIsInstance(exponent, Fraction)
            return (Fraction(sum(hist.values())),)*2
        result = o.source_moment_screen(c["profile"], "1/10", backend,
                                        {"saving_min": "0", "saving_max": "1/2", "profile_sha256": o.profile_hash(c["profile"]), "model_id": "SYNTHETIC"})
        self.assertEqual(result["admission_label"], "MODEL_ONLY")
        self.assertEqual(result["decision"], "REJECT_EXACT_PROFILE_TARGET")
        with self.assertRaisesRegex(o.ContractError, "OUTSIDE_PROVED_DOMAIN"):
            o.source_moment_screen(c["profile"], "3/4", backend,
                                   {"saving_min": "0", "saving_max": "1/2", "profile_sha256": o.profile_hash(c["profile"]), "model_id": "SYNTHETIC"})

if __name__ == "__main__":
    unittest.main(verbosity=2)
