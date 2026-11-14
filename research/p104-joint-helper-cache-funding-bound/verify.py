#!/usr/bin/env python3
"""Read-only source, funding and independent price checks; one stdout receipt."""
from fractions import Fraction as Q
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
WORD = ROOT / "inputs/WORD.json.gz"
CALLER = ROOT / "inputs/CALLER.json"
INVOICE = ROOT / "inputs/CURRENT-PRICE.json"
WORD_SHA = "acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9"
NOTICE_SHA = "78e060cbd33ebc4078cabf39e50191a977fb9eb5c41104533079e22da1d9d248"


def need(ok, label):
    if not ok:
        raise ValueError(label)


def load(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def rejects(call, expected):
    try:
        call()
    except (AssertionError, ValueError) as error:
        need(expected in str(error), "mutation rejected for intended reason")
        return True
    raise ValueError("mutation was incorrectly accepted: " + expected)


def independent_integer_margin(prices, power):
    base = {int(r): n for r, n in prices["baseline_signed_profile"].items()}
    native = {5: 1, 3: 1, 1: 2, 4: -2}
    ranks = base.keys() | native.keys()
    full = {r: base.get(r, 0) + 17*native.get(r, 0) for r in ranks}
    interval = power.moment(full)
    threshold = -Q(252581, 10000)
    need(interval[1] < threshold, "independent exact integer-power full margin")
    other = tuple(map(Q, prices["full_at_0038"]["exact"]))
    need(max(interval[0], other[0]) <= min(interval[1], other[1]),
         "independent power and Taylor intervals overlap")
    wrong_count = power.moment({r: base.get(r, 0) + 18*native.get(r, 0) for r in ranks})
    need(wrong_count[0] > threshold, "incorrect eighteen-call margin rejected")
    wrong_native = {5: 1, 3: 1, 1: 2, 4: 2}
    wrong_sign = power.moment({r: base.get(r, 0) + 17*wrong_native.get(r, 0) for r in ranks})
    need(wrong_sign[0] > 0, "incorrect target-debit sign rejected")
    certificate = power.CERTIFICATES[4]
    exact = 4**4981 * power.DP
    need((certificate["lower_numerator"]+1)**5000 > exact,
         "inward lower integer-price bracket rejected")
    certs = [power.CERTIFICATES[r] for r in sorted(power.CERTIFICATES)]
    return {"status": "PASS_INDEPENDENT_INTEGER_POWER_MARGIN",
            "kappa": "19/5000", "identity": "f(r)^5000=r^4981",
            "full": power.display(interval), "price_brackets": len(certs),
            "brackets_sha256": sha256(json.dumps(certs, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
            "controls": {"wrong_eighteen_calls": True, "wrong_target_debit_sign": True,
                         "wrong_lower_integer_bracket": True}}


def main():
    need(sha256(WORD.read_bytes()).hexdigest() == WORD_SHA, "native source pin")
    need(sha256((ROOT / "inputs/PREDECESSOR-NOTICE").read_bytes()).hexdigest() == NOTICE_SHA,
         "retained predecessor notice pin")
    engine = load("joint_funding_source", "verifier/engine.py")
    pricing = load("joint_funding_pricing", "verifier/pricing.py")
    power = load("joint_funding_integer_prices", "verifier/integer_prices.py")
    scope_fixtures = load("joint_funding_scope_fixtures", "verifier/scope_fixtures.py")
    block_fixtures = load("joint_funding_block_fixtures", "verifier/block_fixtures.py")
    independent_small = load("joint_funding_independent_small", "verifier/independent_small.py")
    replay = engine.rebuild(WORD)
    structure = engine.structure(replay)
    local = engine.local_bounds(replay, structure)
    independent_local = independent_small.run(replay, structure, local)
    semantic_controls = engine.negative_controls(replay, structure)
    prices = pricing.prove(replay, structure, local, CALLER, INVOICE)
    power_check = independent_integer_margin(prices, power)
    raw = bytearray(WORD.read_bytes())
    raw[len(raw)//2] ^= 1
    with tempfile.TemporaryDirectory(prefix="joint-funding-source-control-") as temp:
        changed = Path(temp) / "changed.gz"
        changed.write_bytes(raw)
        source_mutation = rejects(lambda: engine.rebuild(changed), "native WORD bytes")
    receipt = {
        "status": "PASS_JOINT_HELPER_CACHE_FUNDING_NO_NEW_KAPPA",
        "source": replay["receipt"], "structure": structure["receipt"],
        "largest_component": local["largest_component"],
        "six_zero_analytic_checks": local["six_zero_analytic_checks"],
        "small_component_counts": [
            {"cache_sites": c["cache_sites"], "subsets": c["subset_count"], "cases": c["case_count"]}
            for c in local["eight_small_components"]],
        "zero_only_quarter_certificate": local["zero_only_quarter_certificate"],
        "prices": prices, "independent_integer_power": power_check,
        "source_mutation_rejected": source_mutation,
        "semantic_controls": semantic_controls,
        "tangent_scope_fixtures": scope_fixtures.run(),
        "independent_block_fixtures": block_fixtures.run(),
        "independent_small_algebra": independent_local,
        "output": "stdout only; no package files written",
    }
    print(json.dumps(engine.to_jsonable(receipt), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
