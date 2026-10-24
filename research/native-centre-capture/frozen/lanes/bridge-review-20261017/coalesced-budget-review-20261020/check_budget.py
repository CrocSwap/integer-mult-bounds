"""Check the four stated coalesced budget limits with the third engine."""

from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
ENGINE = HERE.parent / "low-displacement-budget-review-20261020"
SOURCE = HERE.parent.parent / "budget-geometry-20261017/coalesced-reciprocal-budget-20261020/BUDGET.json"
ENGINE_PIN = "953690464698b38801b4f2ddf0f56035203a9337214595a557c7d3950e2e6f87"
SOURCE_PIN = "a24f6b95c5f341817b4f49ce845fa58b83060dc991c9f7772691c0edfcb9ad77"


def need(test, reason):
    if not test:
        raise ValueError(reason)


def main():
    raw = (ENGINE / "FREEZE.json").read_bytes()
    need(sha256(raw).hexdigest() == ENGINE_PIN, "Exact engine freeze")
    for name, pin in json.loads(raw)["files"].items():
        need(sha256((ENGINE / name).read_bytes()).hexdigest() == pin, "Exact engine file")
    spec = importlib.util.spec_from_file_location("third_budget_engine", ENGINE / "check_review.py")
    engine = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(engine)
    raw = SOURCE.read_bytes()
    need(sha256(raw).hexdigest() == SOURCE_PIN, "Budget receipt pin")
    source = json.loads(raw)
    need(F(source["saving_exponent"]) == engine.B and source["ambient_dimension"] == engine.D
         and source["productive_fields"] == engine.W and source["selected_commit"] == engine.BASE,
         "Historical exponent and dimensions")
    need(source["selected_certificate_sha256"] == engine.PINS["selected"]
         and source["assembly_sha256"] == engine.PINS["assembly"], "Historical source pins")
    base = Counter({1: 2913, 2: 711, 3: 138, 4: 36, 5: 15, 6: 33, 7: 30})
    need(base == engine.counts(source["three_call_profile"]) and engine.mass(base) == 5376,
         "Stated three-call profile")
    moment = engine.moment(base)
    engine.enclosure(moment, source["base_moment"], "Base")
    results = {}
    expected = {(0, 1): 198, (0, 2): 99, (64, 1): 134, (64, 2): 67}
    for (cleanup, rank), count in expected.items():
        key = f"cleanup_{cleanup}_rank_{rank}"
        profile = base.copy()
        profile[1] += cleanup
        profile[rank] += count
        low = engine.moment(profile)
        profile[rank] += 1
        high = engine.moment(profile)
        need(low[1] < 1 < high[0], "Both strict signs")
        original = source["limits"][key]
        need(original["maximum_count"] == count, "Exact threshold")
        engine.enclosure(low, original["accepted_moment"], key + " accepted")
        engine.enclosure(high, original["next_rejected_moment"], key + " rejected")
        results[key] = dict(maximum_count=count, accepted=list(map(str, low)), rejected=list(map(str, high)))
    output = dict(status="PASS_THIRD_ENGINE_COALESCED_BUDGET", checker_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                  engine_freeze_sha256=ENGINE_PIN, source_receipt_sha256=SOURCE_PIN,
                  base_moment=list(map(str, moment)), limits=results,
                  scope="Four fixed-profile numerical limits. No fresh native census, phase, caller, host or supplier review.")
    data = (json.dumps(output, sort_keys=True, indent=2) + "\n").encode()
    (HERE / (sys.argv[1] if len(sys.argv) > 1 else "normal.json")).write_bytes(data)
    print(output["status"])
    print(sha256(data).hexdigest())


if __name__ == "__main__":
    main()
