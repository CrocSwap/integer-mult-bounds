#!/usr/bin/env python3
"""Rebuild and certify the five public MOVE fusions on the exact #7000 word.

Prepared for ToikY with substantial OpenAI Codex assistance. Apache-2.0.
"""

import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction
import hashlib
import importlib.util
import gzip
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory


HERE = Path(__file__).resolve().parent
VENDOR = HERE.parent / "shared-wire-split-composition"
SOURCE = VENDOR / "data/final.json.gz"
SOURCE_HEAD = "93effe2a135bf57b9e484cb630d8dd057159aec9"
CANDIDATE_SHA = "d0de7804e56b2c8fe6db9d323560e53041810fd0377b91680cbed19b5176ebc0"
PAID_DELTA = {1: -7, 2: 2, 4: -3, 5: 3}


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def module(name, relative):
    path = VENDOR / relative
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value


def authenticate():
    deps = json.loads((HERE / "DEPENDENCIES.json").read_bytes())
    need(deps["source_commit"] == SOURCE_HEAD, "Pinned #7000 source head")
    registered = json.loads((HERE / "VERIFY.json").read_bytes())["inputs"]
    need([row["source_path"] for row in deps["files"]] == registered, "Complete registered source inventory")
    for row in deps["files"]:
        path = HERE.parents[1] / row["source_path"]
        need(path.resolve().is_relative_to(VENDOR), "Input is within the archived source")
        raw = path.read_bytes()
        git_blob = hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()
        need(sha(raw) == row["sha256"] and git_blob == row["git_blob"], row["source_path"])


def signed_delta(before, after):
    delta = Counter(after)
    delta.subtract(before)
    return {r: n for r, n in sorted(delta.items()) if n}


def margin(engine, invoice, kappa):
    return engine.sub(engine.moment(invoice["T"], kappa), engine.moment(invoice["P"], kappa))


def certify_price(engine, baseline, candidate, source):
    old_lo, old_hi = map(Fraction, (source["raw_lower"], source["raw_upper"]))
    bit = Fraction(source["numeric_BIT_price"])
    need(margin(engine, baseline, old_lo)[0] > 0 and margin(engine, baseline, old_hi)[1] < 0,
         "Original literal invoice crosses in the pinned bracket")
    need(margin(engine, candidate, old_hi)[0] > 0, "Positive strict gain at the old upper endpoint")
    scale = 10**32
    lo, hi = int(old_hi * scale), int(bit * scale)
    need(margin(engine, candidate, Fraction(hi, scale))[1] < 0, "Complex price binds below BIT")
    while hi - lo > 1:
        middle = (hi + lo) // 2
        value = margin(engine, candidate, Fraction(middle, scale))
        if value[0] > 0:
            lo = middle
        else:
            need(value[1] < 0, "Every crossing-bisection sign is exact")
            hi = middle
    lower, upper = Fraction(lo, scale), Fraction(hi, scale)
    gap = Fraction(1, 10**14)
    claim = Fraction((lower - 7*gap) * 10**11 // 1, 10**11)
    tested = claim + 7*gap
    old_claim = Fraction(source["claim"])
    need(old_claim < old_hi < claim, "Published rational claim exceeds the previous raw upper bound")
    gate = engine.gate(candidate, claim, tested, lower, upper, bit)
    need(gate["compiler_gap"] == str(gap), "Exact compiler gap")
    return gate, {"claim_gain": str(claim - old_claim),
                  "claim_vs_old_raw_upper": str(claim - old_hi),
                  "raw_gain_interval": [str(lower - old_hi), str(upper - old_lo)],
                  "new_margin_at_old_upper": engine.show(margin(engine, candidate, old_hi))}


def chart_maps(word, edits):
    compiler = module("stop_fusion_clifford", "frozen/clifford_exact.py")
    check = module("stop_fusion_native", "frozen/native_verify.py")
    frames = word["frames"]
    recipes = []
    changed = {(p["old_moves"][0]["event"][2], p["old_moves"][1]["event"][3]) for p in edits["plans"]}
    for a, b in sorted(changed):
        ca, cb = (compiler.canonical_frame(9, tuple(frames[k])) for k in (a, b))
        recipe, _ = compiler.lower_child(ca.adjoint().then(cb))
        expected = check.adjoint(check.frame(frames[a], 9)) + check.frame(frames[b], 9)
        need(recipe["rank"] == len(frames[b]) - len(frames[a]) > 0, "Fused paid rank")
        lowered = check.recipe(recipe)
        check.equal(lowered, expected, "Every signed Pauli and absolute phase")
        for column in range(512):
            need(check.state(lowered, column) == check.state(expected, column), "Changed Gaussian column")
        wrong = deepcopy(recipe)
        wrong["left"]["phase"] = (wrong["left"]["phase"] + 1) % 4
        try:
            check.equal(check.recipe(wrong), expected, "Wrong absolute phase")
        except ValueError:
            pass
        else:
            raise ValueError("Accepted a wrong absolute phase")
        recipes.append({"a": a, "b": b, "recipe": recipe, "exact_columns": 512})
    need(len(recipes) == 4, "Four distinct fused chart maps")
    return recipes


def bit_binding(independent, manifest):
    bit = independent.load(VENDOR / "data/bit-admission.json")
    previous = Fraction(bit["previous_ordinary"])
    need(previous == Fraction(".0034") and bit["empty_body_targets"] ==
         {"count": 0, "rank1_productive_credit": 0}, "Selected start and E-free BIT targets")
    for row in bit["ordinary_bootstrap"]:
        atom, covered, admitted = map(Fraction, (row["atom"], row["covered"], row["admitted"]))
        envelope = (1-atom)*covered + atom*previous
        need(previous == Fraction(row["previous"]) and envelope == Fraction(row["envelope"]) and
             previous < admitted < envelope, "Exact BIT bootstrap")
        previous = admitted
    need(previous == Fraction(bit["ordinary_admitted"]) == Fraction(".00385248") and
         Fraction(manifest["numeric_BIT_price"]) < previous, "Retained BIT margin")


def certify(candidate_path, edits):
    independent = module("stop_fusion_independent", "independent.py")
    engine = module("stop_fusion_intervals", "interval_gate.py")
    precision = module("stop_fusion_precision", "precision_replay.py")
    manifest = independent.load(VENDOR / "INDEPENDENT-SOURCES.json")
    word, baseline = map(independent.load, (candidate_path, SOURCE))
    caller = independent.load(VENDOR / "data/caller.json")
    bit_binding(independent, manifest)
    original_native = independent.native(baseline)
    native = independent.native(word)
    need(not original_native["bad_inputs"] and not native["bad_inputs"], "Independent all-input native adjoint")
    need(all(original_native[name] == native[name] for name in
             ("public", "helpers", "rises", "owned_peak", "lifetimes")), "Same target and owned census")
    need(native["events"] == original_native["events"] - 5, "Five paid fusions in literal word")
    need(signed_delta(original_native["paid"], native["paid"]) == PAID_DELTA, "Literal local paid histogram")
    old_invoice = independent.invoices(baseline, caller, original_native)
    invoice = independent.invoices(word, caller, native)
    need(old_invoice["T"] == invoice["T"] and old_invoice["S"] == invoice["S"] == 1520 and
         invoice["empty_root_credits"] == 0, "Complete T and rank surplus unchanged")
    need(signed_delta(old_invoice["P"], invoice["P"]) == {r: 18*n for r, n in PAID_DELTA.items()},
         "Complete paid profile over the 18 literal LOCALs")
    old_ordinary = independent.ordinary(baseline, caller, original_native)
    ordinary = independent.ordinary(word, caller, native)
    need(ordinary["conservative_total"] == old_ordinary["conservative_total"] - 90000 < 10**9,
         "Conservative ordinary tariff and route savings")
    caller_result = independent.caller(caller)
    need(not caller_result["bad_outputs"], "Exact formal caller")
    gate, gain = certify_price(engine, old_invoice, invoice, manifest)
    precision_result = precision.run(word, caller, gate, manifest)
    changed_maps = chart_maps(word, edits)

    bad_event = next(i for i, e in enumerate(word["program"])
                     if e[:4] == edits["plans"][0]["slides"][0]["event"][:4] and e[-1] == 127)
    need(independent.native(word, mutant=bad_event)["bad_inputs"], "Fused-word scalar mutation must fail")
    wrong = deepcopy(caller)
    query = next(i for i, e in enumerate(wrong["events"]) if e[0] != "J" and e[1] == "QUERY")
    del wrong["events"][query]
    need(independent.caller(wrong)["bad_outputs"], "Omitted QUERY must fail")
    lower, upper = gate["raw_bracket"]
    try:
        engine.gate(invoice, gate["claim"], gate["claim"], lower, upper, gate["BIT_pin"])
    except AssertionError:
        pass
    else:
        raise ValueError("Closed compiler gap accepted")
    need(margin(engine, invoice, Fraction(upper))[1] < 0, "Unfunded upper crossing rejected")
    return {"status": "PASS_SHARED_WIRE_STOP_FUSION", "source_head": SOURCE_HEAD,
            "candidate_canonical_sha256": CANDIDATE_SHA, "native": native, "invoice": invoice,
            "ordinary": ordinary, "caller": caller_result, "gate": gate, "gain": gain,
            "precision": precision_result, "new_chart_maps": changed_maps,
            "controls": {"native_scalar": bad_event, "deleted_query": query, "closed_compiler_gap": True,
                         "unfunded_upper_endpoint": True, "chart_phases": len(changed_maps)}}


def command(*args):
    subprocess.run([sys.executable, "-I", "-B", *map(str, args)], check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, help="Write a new, explicit result path for a clean comparison")
    args = parser.parse_args()
    authenticate()
    with TemporaryDirectory(prefix="p104-stop-fusion-") as temporary:
        word = Path(temporary) / "word.json.gz"
        command(HERE / "build_candidate.py", "--source", SOURCE, "--candidate", word)
        need(sha(gzip.decompress(word.read_bytes())) == CANDIDATE_SHA, "Frozen candidate payload")
        command(VENDOR / "frozen/verify_host3_odd.py", word, "1125")
        command(HERE / "audit_native.py", word)
        result = certify(word, json.loads((HERE / "EDITS.json").read_bytes()))
        command(VENDOR / "frozen/physical.py", word, VENDOR / "frozen/clifford_exact.py", "1000000009", "11")
    canonical = json.loads(json.dumps(result))
    if args.out is not None:
        with args.out.open("x") as stream:
            json.dump(canonical, stream, indent=2)
            stream.write("\n")
    else:
        need(canonical == json.loads((HERE / "RESULT.json").read_bytes()), "Frozen proof-relevant receipt")
    print(result["status"], result["gate"]["claim"], result["gain"]["claim_gain"], flush=True)


if __name__ == "__main__":
    main()
