#!/usr/bin/env python3
"""Offline exact replay, independent full census, and optimizer controls."""
from collections import Counter
from pathlib import Path
import copy
import gzip
import hashlib
import importlib.util
import json
import tempfile

HERE = Path(__file__).resolve().parent
CONTROL_SHA = "2b94953dc14a122e3ef089633f05b58ec689ec5156feb7c784ed3e137dc01883"
CALLER_SHA = "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc"
PRICE_SHA = "86f71ccbc923db5d7a6753aa971c3a9c8a572680534498ed17be072cfa2aae6b"


def need(ok, why):
    if not ok:
        raise ValueError(why)


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def profile_signature(row):
    return (tuple(row["choice_dimensions"]),
            tuple(sorted((int(k), v) for k, v in row["paid_delta"].items() if v)),
            tuple(row["extreme_savings"]))


def run():
    solver, independent = load("solver"), load("independent")
    primary = solver.run()
    normalized = json.loads(json.dumps(primary))
    need(normalized == json.loads((HERE / "RESULT.json").read_text()), "complete frozen primary receipt")
    alternate = independent.run()
    a, b = primary["factors"], alternate["combined"]["factors"]
    need([r["factor"] for r in a] == [r["factor"] for r in b], "independent factor partition")
    for x, y in zip(a, b):
        need((x["cases"], x["feasible"]) == (y["cartesian"], y["legal"]), "independent coverage")
        need(Counter(map(profile_signature, x["profiles"])) ==
             Counter(map(profile_signature, y["profiles"])), "every independent legal profile")
        need(x["maximum_extreme_savings"] == y["maxima_min_r_k"] == [0] * 9,
             "every independent exact concave maximum")
    native = json.loads(gzip.decompress((HERE / "inputs/pr7481-WORD.json.gz").read_bytes()))
    caller_bytes = (HERE / "inputs/CALLER.json").read_bytes()
    price_bytes = (HERE / "inputs/CURRENT-PRICE.json").read_bytes()
    need(hashlib.sha256(caller_bytes).hexdigest() == CALLER_SHA, "exact caller bytes")
    need(hashlib.sha256(price_bytes).hexdigest() == PRICE_SHA, "exact complete invoice bytes")
    caller, target, paid = json.loads(caller_bytes), Counter(), Counter()
    calls = sum(e[0] == "J" for e in caller["events"])
    need(calls == caller["stages"] == 17, "retained native call count")
    for d in caller["types"].values():
        for diagonal in d["diagonal"]:
            target[1 + 8 * sum(diagonal[2:])] += len(d["ports"])
    for e in caller["events"]:
        if e[0] == "J":
            continue
        ports = len(caller["types"][e[0]]["ports"])
        if e[1] == "QUERY":
            paid[1] += ports
        elif e[1] in ("IDLE_ONE", "IDLE_ODD"):
            paid[8 * len(e[3]) + int(e[1] == "IDLE_ODD")] += ports
    mains = set(native["live"]) | {i + 112 for i in native["live"]}
    mains |= set(native["hosted"]["X2"]) | set(native["hosted"]["Y2"])
    for h in set(range(native["public"])) - mains:
        target[abs(len(native["frames"][native["initial"][h]])
                   - len(native["frames"][native["final"][h]]))] += calls
    for rank, count in primary["original_paid"].items():
        paid[rank] += calls * count
    expected = json.loads(price_bytes)["after"]
    need(target == Counter({int(k): v for k, v in expected["T"].items()}), "full productive invoice")
    need(paid == Counter({int(k): v for k, v in expected["P"].items()}), "full paid invoice")
    # Same optimizer, restricted to one historical component with a known gain.
    source = HERE / "inputs/canonical-selected-WORD.json.gz"
    word = json.loads(gzip.decompress(source.read_bytes()))
    _, groups = solver.R.visit_components(word)
    selected = [j for j, g in enumerate(groups)
                if {v["owner"] for v in g} == {47, 158, 923}
                and solver.R.dim(solver.R.span(word["frames"][g[0]["chart"]])) == 4]
    need(len(selected) == 1, "historical positive-control component")
    control = solver.run(source=source, expected_sha=CONTROL_SHA, require_zero=False,
                         extra_frozen=set(range(len(groups))) - set(selected))
    gain = sum(r["maximum_extreme_savings"][1] for r in control["factors"])
    need(gain >= 1, "same optimizer detects historical positive min(r,2) saving")
    raw = bytearray((HERE / "inputs/pr7481-WORD.json.gz").read_bytes())
    raw[len(raw) // 2] ^= 1
    with tempfile.TemporaryDirectory(prefix="frame-source-control-") as t:
        bad = Path(t) / "changed.gz"
        bad.write_bytes(raw)
        caught = False
        try:
            solver.run(source=bad)
        except ValueError as exc:
            need("pin" in str(exc), "primary hash control precedes science")
            caught = True
        need(caught, "primary rejects changed source")
        old, independent.NATIVE = independent.NATIVE, bad
        caught = False
        try:
            independent.run()
        except AssertionError as exc:
            need("pin" in str(exc), "independent hash control precedes science")
            caught = True
        finally:
            independent.NATIVE = old
        need(caught, "independent rejects changed source")
    mutant = copy.deepcopy(word)
    e = next(e for e in mutant["program"] if e[0] == "MOVE")
    e[4] = not bool(e[4])
    caught = False
    try:
        solver.R.visit_components(mutant)
    except ValueError as exc:
        need("ownership" in str(exc), "wrong owned flag is detected")
        caught = True
    need(caught, "ownership mutation rejected")
    return {"status": "PASS_COMPLETE_CONTACT_RECHARTING_INDEPENDENT_REPLAY",
            "source_sha256": primary["source_sha256"], "components": primary["components"],
            "variable_components": primary["free_count"], "factors": len(a),
            "cartesian_factor_assignments": primary["total_factor_cases"],
            "legal_factor_assignments": primary["feasible_factor_cases"],
            "cross_direction_edges": alternate["cross_direction_edges"],
            "all_nine_concave_maxima_zero": True, "independent_all_profiles_match": True,
            "historical_same_optimizer_positive_control": gain,
            "complete_invoice": {"native_calls": calls, "productive_fields": sum(target.values()),
                                 "paid_jobs": sum(paid.values())},
            "changed_source_and_ownership_controls": True,
            "kappa_status": "No new kappa; fixed-template source-scoped obstruction"}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
