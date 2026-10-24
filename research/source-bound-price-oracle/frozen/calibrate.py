"""Calibrate immutable profile identities against previously frozen evidence.

No scientific verifier, native job, nonintegral power or root search is run.
Historical imported evidence labels remain distinct from evaluate() receipts.
"""
from pathlib import Path
import json
from fractions import Fraction as Q
import oracle as o

HERE = Path(__file__).resolve().parent
WORK = HERE.parents[2]
CANON = "1ec1119972c9aefe42525172d07b332fcff81cb4"
PINS = {
    "selected": "outputs/price-plane-swarm-20261024/09-capsule-cold/capsule-v1/snapshot/certificates/selected-result.json",
    "4610_arithmetic": "outputs/owned-relation-5377-cost-review-20261024/frozen/4610-round6-ARITHMETIC.json",
    "5377_arithmetic_independent": "outputs/owned-relation-5377-cost-review-20261024/RESULT.json",
    "5377_arithmetic_source": "outputs/owned-relation-5377-cost-review-20261024/frozen/RESULT.json",
    "5377_physical": "outputs/owned-relation-5377-physical-review-20261024/independent-result.json",
    "5377_closure": "outputs/owned-relation-5377-cost-review-20261024/REPORT.md",
    "5377_cold": "outputs/owned-relation-5377-cold-validation-20261024/VALIDATION.json",
    "5384_publication_audit": "outputs/owned-relation-publication-audit-20261024/FINAL-PASS.json",
    "5383_invoice": "outputs/price-plane-swarm-20261024/02-census/INVOICE-v1.json",
    "5383_contract": "outputs/price-plane-swarm-20261024/02-census/CANDIDATE-CONTRACT-v1.json",
    "5383_author_source": "outputs/price-plane-swarm-20261024/09-capsule-cold/capsule-v1/snapshot/research/kappa-joint-relations-20261023/RESULT.json",
    "5383_witness": "outputs/price-plane-swarm-20261024/09-capsule-cold/capsule-v1/snapshot/research/kappa-joint-relations-20261023/WITNESS.json",
    "5383_manifest": "outputs/price-plane-swarm-20261024/09-capsule-cold/capsule-v1/IMMUTABLE-MANIFEST.json",
    "planning_pins": "outputs/price-plane-swarm-plan-20261024/PLAN.md",
}

def create():
    # The first freeze is explicit. Subsequent calibration reads only the frozen
    # own-directory bytes and refuses changes against SOURCE-PINS.json.
    pins = {}
    for name, relative in PINS.items():
        raw = (WORK / relative).read_bytes()
        key = o.digest(raw)
        suffix = ".md" if relative.endswith(".md") else ".json"
        local = "fixtures/"+name+suffix
        (HERE/local).write_bytes(raw)
        pins[name] = {"path": local, "sha256": key, "origin": relative}
    (HERE/"SOURCE-PINS.json").write_bytes(o.encode(pins))


def run():
    pins = json.loads((HERE/"SOURCE-PINS.json").read_text())
    data = {}
    for name, pin in pins.items():
        raw = (HERE/pin["path"]).read_bytes()
        if o.digest(raw) != pin["sha256"]:
            raise o.ContractError("CALIBRATION_SOURCE_CHANGED:"+name)
        if pin["path"].endswith(".json"):
            data[name] = json.loads(raw)
    selected = data["selected"]
    a = data["4610_arithmetic"]
    b = data["5377_arithmetic_independent"]
    bsource = data["5377_arithmetic_source"]["arithmetic"]
    inv = data["5383_invoice"]
    author = data["5383_author_source"]["arithmetic"]
    assert selected["audited_source_head"] == "20bb93cd990d2ff683e4d0fc56b87a42cd5d3296"
    assert selected["audit_pr"] == 5241 and Q(selected["kappa"]) == Q(a["kappa"]) == Q(".0030217758")
    assert Q(b["kappa"]) == Q(bsource["kappa"]) == Q(".00302235")
    assert b["head"] == data["5377_physical"]["head"] == data["5377_cold"]["head"] == "c448d13c71908647f968b06cddb795ce7d288139"
    assert data["5384_publication_audit"]["publication_head"] == "411648821f0208d60099be8ca42957ca3a1c4316"
    assert inv["candidate"]["head"] == "4bd6efa51a495a7c7b7754915cf0244e7e60969e"
    assert inv["capsule_manifest_sha256"] == pins["5383_manifest"]["sha256"]
    assert inv["histograms"]["paid"] == author["paid"] and inv["histograms"]["productive"] == author["targets"]
    assert Q(author["kappa"]) == Q(".00302666")
    records = []
    for name, paid, productive, status, kappa, rawroot in (
        ("4610", a["paid"], a["targets"], "SELECTED", a["kappa"], a["raw_root_interval"]),
        ("5377", b["paid"], b["targets"], "PUBLIC_REVIEWABLE", b["kappa"], b["root"]),
        ("5383", inv["histograms"]["paid"], inv["histograms"]["productive"], "WITNESS_READY", None, author["raw_root_interval"]),
    ):
        profile = {"paid": paid, "productive": productive}
        totals = o.exact_rank_totals(profile)
        expected = {"4610": (64404, 10928), "5377": (64372, 10912), "5383": (64148, 10800)}[name]
        assert (totals["paid"]["jobs"], totals["productive"]["jobs"]) == expected
        assert totals["productive"]["rank_mass"] - totals["paid"]["rank_mass"] == 752
        row = {"candidate": name, "profile": profile, "totals": totals,
               "profile_sha256": o.profile_hash(profile), "imported_evidence_label": status,
               "funded_kappa": str(Q(kappa)) if kappa else None,
               "author_claim_kappa": str(Q(author["kappa"])) if name == "5383" else None,
               "raw_root_interval": [str(Q(x)) for x in rawroot],
               "same_five_assumptions": list(o.ASSUMPTIONS), "selected_read_only": name == "4610",
               "admission_origin": "frozen prior independent receipts" if kappa else "literal independent census, author arithmetic pending independent closure/funding",
               "fresh_math_replayed_by_oracle": False}
        if kappa:
            row["gain_against_selected"] = str(Q(kappa)-Q(selected["kappa"]))
        if name == "5377":
            assert b["outer_strict_count"] == len(bsource["outer"]["strict_checks"]) == 54
            assert b["outer_functional_count"] == len(bsource["outer"]["functional_checks"]) == 4
            assert all(Q(x)>0 for x in bsource["outer"]["strict_checks"].values())
            assert Q(b["root_signs"][0][0]) > 0 and Q(b["root_signs"][1][1]) < 0
            row["public_verification"] = {"pr": 5384, "head": data["5384_publication_audit"]["publication_head"],
                                           "url": "https://github.com/CrocSwap/integer-mult-bounds/pull/5384",
                                           "construction_credit": "Ali Romman #5377"}
        records.append(row)
    result = {"schema": "source-bound-calibration/v1", "canonical_base": CANON,
              "scope": "Frozen calibration imports; oracle admission of new #5383 is a separate receipt join.",
              "records": records, "source_artifacts": pins,
              "optimization_domain": "Fixed complete profiles and their exact source tuples; no global construction optimum established.",
              "global_optimum_unproven_because": ["unexamined physically realizable words and allocations",
                   "changed compiler tuples need explicit source theorem domain", "necessary moments omit unresolved physical costs"]}
    (HERE/"CALIBRATION-v1.json").write_bytes(o.encode(result))
    return result

if __name__ == "__main__":
    import sys
    if "--freeze" in sys.argv:
        create()
    output = run()
    print(json.dumps({"calibration": [(r["candidate"], r["imported_evidence_label"], r["funded_kappa"]) for r in output["records"]],
                      "fresh_math_replay": False}, indent=2))
