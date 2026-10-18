#!/usr/bin/env python3
"""Full-oracle differential checks, corruption controls and optional timing.

Cinna Davis (1337isnot1337), substantial OpenAI Codex assistance; Apache-2.0.
"""
import argparse
import copy
import gzip
import hashlib
import json
import platform
from pathlib import Path
import statistics
import sys
import tempfile
import time
import types

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from prepared_bit_checker import CHECKER_SHA256, CheckerIntegrityError, PreparedBitChecker

CHECKER = ROOT / "research/e8-bit-p111-tuned/code/xcheck_p.py"
WORD = ROOT / "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def outcome(check, word):
    try:
        result = check(word)
        return {"kind": "receipt", "value": result[1:]}
    except Exception as exc:
        return {"kind": "exception", "type": type(exc).__name__, "message": str(exc)}


def fixtures(word):
    v = word["v"]
    helper = 2 * v
    out = []

    def add(name, edit, expected, route="geometry"):
        w = copy.deepcopy(word)
        edit(w)
        out.append((name, w, expected, route))

    add("selected", lambda w: None, "admitted")
    add("canceling-D-pair", lambda w: w["D"].extend([[0, v, [helper]], [0, v, [helper]]]), "admitted")
    # Scalar identity and final frames hold, but literal-reversal H4 fails.
    add("canceling-C-pair-H4-false", lambda w: w["C"].extend([[1, helper, [0]], [1, helper, [0]]]), "flag-false")
    add("single-D-dirty-leak", lambda w: w["D"].append([0, v, [helper]]), "reject")
    add("missing-A-gate", lambda w: w["A"].pop(0), "reject")
    add("missing-C-restoration", lambda w: w["C"].pop(), "reject")
    add("out-of-range-frame", lambda w: w["A"][0].__setitem__(0, len(w["frames"])), "reject")
    add("self-source", lambda w: w["A"][0].__setitem__(2, [w["A"][0][1]]), "reject")
    add("malformed-gate", lambda w: w["B"].append([0, v]), "reject")
    add("scatter-out-of-range", lambda w: w["scatter"][0].append(len(w["ret"])), "reject", "fallback")
    add("retained-source", lambda w: w["ret"].__setitem__(0, 0), "reject", "fallback")
    add("wrong-final-target", lambda w: w["final"].__setitem__(v, 1), "reject", "fallback")
    add("invalid-label", lambda w: w["lines"][0].__setitem__(0, w["lines"][0][0] + 2), "reject", "fallback")
    add("nonclosed-frame", lambda w: w["frames"][1].pop(), "reject", "fallback")
    add("annotation-change", lambda w: w.__setitem__("extra_annotation", "conservative fallback"), "admitted", "fallback")
    add("wrong-header", lambda w: w.__setitem__("h", 7), "reject", "fallback")
    return out


def verify():
    source = CHECKER.read_bytes()
    require(hashlib.sha256(source).hexdigest() == CHECKER_SHA256, "source pin")
    oracle = types.ModuleType("full_bit_oracle")
    exec(compile(source, str(CHECKER), "exec"), oracle.__dict__)
    word = json.load(gzip.open(WORD, "rt"))
    template = copy.deepcopy(word)
    prepared = PreparedBitChecker(CHECKER, template)
    template["lines"][0][0] += 100
    records = []
    cases = fixtures(word)
    for name, w, expected, route in cases:
        old_hits, old_fallbacks = prepared.geometry_hits, prepared.full_fallbacks
        full = outcome(oracle.check, w)
        fast = outcome(prepared.check, w)
        require(full == fast, "oracle mismatch: " + name)
        require(prepared.geometry_hits - old_hits == (route == "geometry"), "geometry route: " + name)
        require(prepared.full_fallbacks - old_fallbacks == (route == "fallback"), "fallback route: " + name)
        if expected == "reject":
            require(full["kind"] == "exception" and full["type"] == "Reject", "meaningful rejection: " + name)
        else:
            require(full["kind"] == "receipt", "unexpected rejection: " + name)
            H, C = full["value"][2:4]
            if expected == "admitted":
                require(all(H.values()) and all(C.values()), "unexpected false interface: " + name)
            else:
                require(H["H4_C_literal_reverse_at_full"] is False, "H4 control missing")
        records.append({"name": name, "route": route, "expected": expected, "result": full})
    require(records[1]["result"]["value"][1]["gates"]["D"] ==
            records[0]["result"]["value"][1]["gates"]["D"] + 2, "stale gate report")
    try:
        prepared.check(cases[6][1])
    except prepared.reject_type:
        pass
    else:
        raise RuntimeError("public Reject class did not catch invalid frame")
    returned = prepared.check(word)
    returned[0].w["A"].clear()
    returned[0].fdim.clear()
    returned[1].clear()
    require(outcome(prepared.check, word) == records[0]["result"], "returned-object cache poisoning")
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "checker.py"
        p.write_bytes(source)
        pinned = PreparedBitChecker(p, word)
        p.write_bytes(source + b"\n")
        require(outcome(pinned.check, word)["type"] == "CheckerIntegrityError", "changed checker accepted")
        try:
            PreparedBitChecker(p, word)
        except CheckerIntegrityError:
            pass
        else:
            raise RuntimeError("wrong initial source pin accepted")
    # Initial screen: one A write and no A donor use. Not an impossibility theorem.
    writes = {r: 0 for r in range(2 * word["v"], 2 * word["v"] + word["R"])}
    donors = set()
    for _, dest, srcs in word["A"]:
        if dest in writes:
            writes[dest] += 1
        donors.update(srcs)
    eligible = sorted(r for r, count in writes.items() if count == 1 and r not in donors)
    require(eligible == [], "cold-A screen changed")
    return oracle, word, cases, {
        "schema_version": 1, "base_commit": "81e81af67714bdc8d1693b0bf5c29468b92f62ff",
        "assignment_seed": 7, "checker_sha256": CHECKER_SHA256,
        "word_sha256": hashlib.sha256(WORD.read_bytes()).hexdigest(),
        "columns": 2 * word["v"] + word["R"], "cases": records,
        "isolation_controls": ["template-mutation", "returned-object-mutation", "checker-change", "initial-checker-pin"],
        "cold_A_screen_eligible_helpers": eligible,
    }


def benchmark(oracle, word, cases, repeats):
    variants = [w for _, w, _, _ in cases[:3]]
    start = time.perf_counter()
    prepared = PreparedBitChecker(CHECKER, word)
    setup = time.perf_counter() - start
    timings = {"full": [], "prepared": []}
    # Identical inputs; alternate order, with seed7 selecting first order.
    for k in range(repeats * len(variants)):
        w = variants[k % len(variants)]
        order = ("prepared", "full") if (k + 7) % 2 else ("full", "prepared")
        for method in order:
            start = time.perf_counter()
            out = outcome(oracle.check if method == "full" else prepared.check, w)
            elapsed = time.perf_counter() - start
            require(out["kind"] == "receipt", "benchmark unexpectedly rejected")
            timings[method].append(elapsed)
    return {
        "python": platform.python_version(), "platform": platform.platform(),
        "samples_per_path": len(timings["full"]), "variants": [c[0] for c in cases[:3]],
        "preparation_seconds": setup, "seconds": timings,
        "median_full_seconds": statistics.median(timings["full"]),
        "median_prepared_seconds": statistics.median(timings["prepared"]),
        "median_speedup": statistics.median(timings["full"]) / statistics.median(timings["prepared"]),
        "batch_speedup_including_setup": sum(timings["full"]) / (setup + sum(timings["prepared"])),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--benchmark", action="store_true")
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    require(1 <= args.repeats <= 20, "repeats outside bounded domain")
    oracle, word, cases, receipt = verify()
    evidence_path = Path(__file__).resolve().parent / "EVIDENCE.json"
    if not args.output:
        committed = json.loads(evidence_path.read_text())
        committed.pop("benchmark", None)
        require(json.loads(json.dumps(receipt)) == committed, "committed semantic receipt differs")
    if args.benchmark:
        receipt["benchmark"] = benchmark(oracle, word, cases, args.repeats)
        print(json.dumps(receipt["benchmark"], sort_keys=True))
    if args.output:
        args.output.write_text(json.dumps(receipt, indent=2) + "\n")
    print("PASS_BIT_PREPARED_GEOMETRY: 16 exact oracle cases, 4 isolation controls, 661 symbolic columns")


if __name__ == "__main__":
    main()
