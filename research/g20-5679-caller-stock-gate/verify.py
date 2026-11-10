#!/usr/bin/env python3
"""Selected Gaussian pricing cannot consume the PR5679 BIT component as admitted BIT.

The selected #6030 pricing reads ordinary and admitted BIT from the thinned
controller and requires atom > ordinary > admitted > TESTED before it calls the
PR4359 outer ledger with bit_saving=admitted. This verifier checks that gate
against PR5679's ordinary component. It does not replay the G20 caller.

PR5708's larger component is loaded only to show that the two receipts differ.
Rejecting the larger value does not, by itself, reject this smaller one.
"""
from fractions import Fraction
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PRICING = ROOT / "research/p104-helper470-twin-rung-removal/pricing.py"
CLAIM = ROOT / "certificates/frontier6030/CLAIM.json"
CONTROLLER = ROOT / "research/query-thinned-controllers/RESULT.json"
COMPONENT = ROOT / "research/g20-helper-split/ORDINARY-RESULT.json"
LATER = ROOT / "research/g20-conjugation-admission/ORDINARY-RESULT.json"
LEDGER = ROOT / "research/pr4359-p7-padding/dependencies/compiler-refill/endpoint.py"
Q = Fraction


def need(ok, message):
    if not ok:
        raise SystemExit("FAIL: " + message)


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_ledger():
    spec = importlib.util.spec_from_file_location("g20_5679_stock_gate_ledger", LEDGER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def selected_ordinary(atom, after_cover, epsilon):
    return (1 - atom) * after_cover + atom * epsilon


def main():
    pricing = PRICING.read_text(encoding="utf-8")
    need(pricing.count("KAPPA, TESTED = Q('0.003125804'), Q('0.0031258090')") == 1,
         "selected pricing kappa and tested literals")
    need(pricing.count("atom > ordinary > admitted > TESTED") == 1,
         "selected stock gate")
    need(pricing.count("ordinary=(1-atom)*Q(bit['after_cover'])+atom*Q('.0000384599')") == 1,
         "selected ordinary formula")
    need(pricing.count("'bit_saving':admitted") == 1, "ledger consumes admitted BIT")
    need(pricing.count("query-thinned-controllers/RESULT.json") == 1,
         "BIT numbers come from the thinned controller")
    need("params['beta']*(1-atom)" in pricing, "fourth outer functional check")

    ledger_text = LEDGER.read_text(encoding="utf-8")
    need(ledger_text.count("p['bit_saving']-a") == 1,
         "ledger uses bit_saving only in actual_bit_above_effective")

    claim = load_json(CLAIM)
    bit = load_json(CONTROLLER)["ordinary_BIT"]
    component_row = load_json(COMPONENT)
    later_row = load_json(LATER)
    need(component_row["status"] == "PASS_CONDITIONAL_G20_HELPER_SPLIT_ORDINARY_FIVE_FINITE_LEVELS",
         "PR5679 ordinary receipt status")
    need(component_row["whole_kappa"] is None, "PR5679 does not claim a whole kappa")
    need(later_row["status"] == "PASS_CONDITIONAL_G20_CONJUGATION_ORDINARY_FIVE_FINITE_LEVELS",
         "PR5708 ordinary receipt status")

    kappa = Q(claim["kappa"])
    tested = Q("0.0031258090")
    need(kappa == Q("0.003125804"), "claim kappa is the pricing literal")
    need(tested > kappa, "tested saving sits above kappa")
    gap = (tested - kappa) / 7
    need(gap == Q(1, 1400000000) and gap.numerator == 1, "exact compiler gap")
    uniform = kappa + 6 * gap
    effective = kappa + 4 * gap
    templates = {row["family"]: Q(row["saving"]) for row in claim["uniform_templates"]}
    need(templates["complex"] == uniform, "claim complex uniform saving is kappa+6*gap")
    need(Q(claim["admitted_BIT_saving"]) == Q(bit["admitted"]) == Q(17, 5000),
         "admitted BIT is 17/5000 in the claim and the controller")

    atom = Q(bit["atom"])
    after_cover = Q(bit["after_cover"])
    epsilon = Q("0.0000384599")
    need(atom == Q(1, 250) and after_cover == Q(69, 20000), "pinned stock atom and cover")
    ordinary = selected_ordinary(atom, after_cover, epsilon)
    admitted = Q(bit["admitted"])
    need(ordinary == Q(claim["ordinary_BIT_saving"]) == Q(8590884599, 2500000000000),
         "recomputed ordinary saving matches the selected claim")
    need(atom > ordinary > admitted > tested, "selected stock gate holds")

    component = Q(component_row["admitted"])
    later = Q(later_row["admitted"])
    need(component == Q(3507410738409, 1000000000000000), "pinned PR5679 component")
    need(later == Q(3507719059749, 1000000000000000), "pinned PR5708 component")
    need(component < later, "PR5679 component is strictly smaller than PR5708")
    need(component > ordinary, "smaller component still exceeds the selected ordinary stock")
    need(later > ordinary, "PR5708 component also exceeds that stock")
    need(not (atom > ordinary > component > tested),
         "PR5679 component cannot occupy the admitted slot")
    need(atom > component > admitted > tested,
         "component lies strictly between atom and the retained admitted BIT")
    need(uniform < admitted < ordinary < component < later < atom < Q(1, 32),
         "complex uniform saving remains below both BIT components")

    module = load_ledger()
    params = {
        "kappa": kappa,
        "tested_saving": tested,
        "complex_uniform_saving": uniform,
        "b": kappa + 5 * gap,
        "a": effective,
        "q": kappa + 3 * gap,
        "bit_saving": admitted,
        "epsilon": 1 - gap,
        "beta": 1 - 3 * gap,
        "r0": gap / 10,
        "stop": gap,
        "layout": gap,
        "d": gap,
    }
    need(params["a"] == effective and params["bit_saving"] == admitted, "selected parameter shape")

    def values(bit_saving):
        out = module.ledger(dict(params, bit_saving=bit_saving))
        strict = out["strict_checks"]
        functional = dict(out["functional_checks"])
        functional["actual_new_BIT_stock_sublinear"] = params["beta"] * (1 - atom)
        return strict, functional

    strict, functional = values(admitted)
    need(len(strict) == 54 and len(functional) == 4, "54 strict and 4 functional checks")
    need(all(item > 0 for item in strict.values()), "selected admitted BIT passes strict checks")
    need(all(item > 0 for item in functional.values()), "selected admitted BIT passes functional checks")
    need(strict["actual_bit_above_effective"] == admitted - effective, "BIT check is B-a")

    swapped_strict, swapped_functional = values(component)
    need(all(item > 0 for item in swapped_strict.values()), "ledger accepts the component as bit_saving")
    need(all(item > 0 for item in swapped_functional.values()), "functional checks ignore the larger BIT value")
    for key, value in strict.items():
        if key == "actual_bit_above_effective":
            need(swapped_strict[key] - value == component - admitted, "only the BIT gap changes")
        else:
            need(swapped_strict[key] == value, "strict check independent of bit_saving: " + key)
    need(swapped_functional == functional, "functional checks do not read bit_saving")

    low = values(Q("0.0027"))[0]
    need(any(item <= 0 for item in low.values()), "pricing's insufficient BIT control still fails")
    equal = values(effective)[0]["actual_bit_above_effective"]
    need(equal == 0, "bit_saving equal to a is not a strict pass")
    bare = selected_ordinary(atom, after_cover, Q(0))
    need(bare != ordinary, "dropping the atom epsilon term changes ordinary")
    need(selected_ordinary(atom, Q(bit["before_cover"]), epsilon) != ordinary,
         "before-cover is not the ordinary input")

    implied = (component - atom * epsilon) * (1 / (1 - atom))
    need(implied != after_cover, "the pinned cover is not the component's cover")
    need(selected_ordinary(atom, implied, epsilon) == component,
         "implied cover reproduces the component")
    need(implied == Q(3507256898809, 996000000000000), "pinned implied cover")
    later_implied = (later - atom * epsilon) / (1 - atom)
    need(later_implied != implied, "the two components do not share a cover")

    receipt = {
        "status": "PASS_G20_5679_CALLER_STOCK_GATE",
        "kappa": str(kappa),
        "tested": str(tested),
        "complex_uniform_saving": str(uniform),
        "effective_a": str(effective),
        "atom": str(atom),
        "selected_ordinary": str(ordinary),
        "admitted_BIT": str(admitted),
        "pr5679_component": str(component),
        "pr5708_component": str(later),
        "component_minus_ordinary": str(component - ordinary),
        "later_minus_component": str(later - component),
        "implied_after_cover": str(implied),
        "stock_rejects_component_as_admitted": True,
        "smaller_than_pr5708_still_rejected": True,
        "ledger_accepts_component_as_bit_saving": True,
        "complex_uniform_still_binds": True,
    }
    print("PASS_G20_5679_CALLER_STOCK_GATE")
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
