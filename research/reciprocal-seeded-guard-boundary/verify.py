"""Offline replay of the seeded guard boundary; standard library only.

Charles Bethin, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import copy
from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def require(ok, message):
    if not ok:
        raise ValueError(message)


def unique_pairs(pairs):
    out = {}
    for key, value in pairs:
        require(key not in out, "duplicate JSON key")
        out[key] = value
    return out


def read_json(path):
    return json.loads(path.read_text(), object_pairs_hook=unique_pairs)


def evaluate(c, p, guards):
    require(c.denominator & (c.denominator-1) == 0, "dyadic input required")
    q = c.denominator.bit_length()-1
    k = c.numerator
    # Signed integer significands, no Fraction operations in the recurrence.
    a, s, m = 5, 3, 1
    rows = []
    t = 6
    while True:
        C = (k << max(t-q, 0)) >> max(q-t, 0)
        U = (C*a) // (1 << s)
        X = (a*((2 << t)-U)) // (1 << s)
        rows.append([m, t, C, U, X])
        a, s = X, t
        if m == p:
            return rows
        m = min(2*m, p)
        t = m + guards


def load_checker():
    spec = importlib.util.spec_from_file_location("floor_certificate", HERE/"check_certificate.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.check


def main():
    # Authenticate every retained source and deterministic receipt before use.
    pins = read_json(HERE/"SOURCES.json")
    for item in pins["package_files"]:
        path = HERE/item["path"]
        require(hashlib.sha256(path.read_bytes()).hexdigest() == item["sha256"],
                "source or certificate changed: " + item["path"])
    check = load_checker()
    certificate = read_json(HERE/"CERTIFICATE.json")
    records = certificate["witnesses"]
    require([(r["guards"], r["p"], r["c"]) for r in records] ==
            [(0, 2, "9/8"), (1, 3, "39/32"), (2, 15, "127379/65536")],
            "witness inventory")
    for r in records:
        check(r)
        require(evaluate(Fraction(r["c"]), r["p"], r["guards"]) == r["rows"],
                "integer evaluator disagrees")
    positive = certificate["positive_controls"]
    require([(r["c"],r["p"],r["guards"]) for r in positive] ==
            [(r["c"],r["p"],g) for r in records for g in (3,5)],
            "positive control inventory")
    for r in positive:
        check(r, failure=False)
        require(evaluate(Fraction(r["c"]), r["p"], r["guards"]) == r["rows"],
                "positive evaluator disagrees")
    r = records[2]
    require(Fraction(r["residual"]) - Fraction(1,65536) == Fraction(655,8589934592),
            "strict failure margin")
    require(abs(Fraction(r["output"]) - 1/Fraction(r["c"])) < Fraction(1,65536),
            "absolute-error distinction")
    mutations = []
    def mutant(label, modify):
        bad = copy.deepcopy(r)
        modify(bad)
        mutations.append((label,bad))
    mutant("omitted stage", lambda b: b["rows"].pop(1))
    mutant("wrong input prefix", lambda b: b["rows"][-1].__setitem__(2,254757))
    mutant("wrong rounded product", lambda b: b["rows"][-1].__setitem__(3,130863))
    mutant("wrong rounded output", lambda b: b["rows"][-1].__setitem__(4,67436))
    mutant("wrong seed", lambda b: b.__setitem__("seed","3/4"))
    mutant("false interval", lambda b: b.__setitem__("failure_interval",
                                                 [b["c"],"254759/131072"]))
    mutant("wrong target", lambda b: b.__setitem__("p",16))
    for label,bad in mutations:
        try:
            check(bad)
        except ValueError:
            continue
        raise ValueError("accepted negative control: " + label)
    print("PASS_SEEDED_GUARD_BOUNDARY witnesses=3 controls=7; no new kappa")


if __name__ == "__main__":
    main()
