#!/usr/bin/env python3
"""Check the rational phase-class baseline with reverse output rows."""

import argparse
from fractions import Fraction as F
from hashlib import sha256
import gzip
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
LANES = HERE.parents[1]
ROOT = LANES.parent / "root"
PINS = {
    "PHASE-CLASS-CAPTURE-FREEZE-20261020.json": "eab4612fa42657ae663a652d9ea5afdfb8205ce5c17a706d7559c19e31ba0d6c",
    "PHASE-CLASS-CAPTURE-20261020.md": "dacaf9624bb8ec32fd473570380988bacb7369126c3fe4c9fdf1afd67275ba43",
    "check_phase_class_capture_20261020.py": "d50e84f8d23ddadee126028998b9cf870aa44f125f2a6bf408ad13515ac53725",
    "phase-class-capture-final-normal/PAIRED-CODE.json": "830a19a100763700dfc5142cb9eca1c284d9ad92828c4f4e1fe69bdc84e55b9d",
    "phase-class-capture-final-normal/CHECKS.json": "9e90c24848e296d030b329cb3c03884c6ab3022e284a1f7479e5c7f07809f3c6",
}
HELPER = LANES / "independent-review-20261017/route32-capture-review-20261020/check_review.py"
HELPER_PIN = "c419f63a47d655c4d2a789cf52f0a00d5186cb7728cdd58aac73ceb21845aa89"
OLD = LANES / "new-core-transfer-20261017/low-displacement-20261020/odd16-normal-v2/EXTENSION-PROGRAM.json.gz"
OLD_PIN = "d466cea24be92fb7f749d686c5efc63f44ea82575c15f78c38e9d6d4c972eba4"
CYCLIC = LANES / "independent-review-20261017/cyclic-pair-flags-20261018/CYCLIC-FLAGS.json"
CYCLIC_PIN = "3034e1df3670f64e5b79a51a435d7903f3be7cef10d6b486a8bd4d420c989585"


def need(test, label):
    if not test:
        raise ValueError(label)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    for name, pin in PINS.items():
        need(sha256((ROOT / name).read_bytes()).hexdigest() == pin, "Root pin " + name)
    need(sha256(HELPER.read_bytes()).hexdigest() == HELPER_PIN, "Independent helper pin")
    need(sha256(CYCLIC.read_bytes()).hexdigest() == CYCLIC_PIN, "Pair source pin")
    raw = gzip.decompress(OLD.read_bytes())
    need(sha256(raw).hexdigest() == OLD_PIN, "Response source pin")
    old = json.loads(raw)["model"]
    cyclic = json.loads(CYCLIC.read_text())
    source = json.loads((ROOT / "phase-class-capture-final-normal/PAIRED-CODE.json").read_text())
    spec = importlib.util.spec_from_file_location("independent_matrix", HELPER)
    r = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(r)
    groups = [(item["ordered_carriers_a_b_c"], item["signs"]) for item in old["vertex_assignments"]]
    groups += [(ps, [1] * len(ps)) for ps in old["small_cliques"]]
    need(groups == [(g["ports"], g["signs"]) for g in source["groups"]], "Actual block binding")
    space = r.binary_span([30, 45, 75, 384])
    classes = [min(q ^ z for z in space) for q in old["ports"]]
    need(source["classes"] == classes, "Actual phase classes")

    def pair(x, inverse=False):
        y = list(x)
        for record in cyclic["pair_codes"]:
            ps, h = record["ports"], record["matrix"]
            need(classes[ps[0]] == classes[ps[1]], "Physical pair class")
            for i, p in enumerate(ps):
                y[p] = sum((F(h[j][i], 2) if inverse else F(h[i][j])) * x[ps[j]]
                           for j in range(2))
        return y

    def formula(x, inverse=False):
        z = pair(x)
        y = list(z)
        for (ps, d), record in zip(groups, source["groups"]):
            selected = set(record["centre_pair"])
            need(len(selected) == 2 and len({classes[p] for p in selected}) == 1, "Centre class pair")
            k = len(ps)
            u = [F(sign * (2 * (p in selected) - 1)) for p, sign in zip(ps, d)]
            v = [F(2 * sign, k) - F(sign * (p in selected), 2) for p, sign in zip(ps, d)]
            delta = 1 + sum(a * b for a, b in zip(u, v))
            need(delta == F(2 * (4 - k), k) != 0, "Rank-one determinant")
            query = sum(value * z[p] for p, value in zip(ps, v))
            factor = -1 / delta if inverse else 1
            for p, value in zip(ps, u):
                y[p] += factor * value * query
        return pair(y, True)

    rows = r.rows_from_columns([formula(r.unit(112, j)) for j in range(112)])
    inverse_rows = r.rows_from_columns([formula(r.unit(112, j), True) for j in range(112)])
    need(rows == r.sparse(source["code"]) and inverse_rows == r.sparse(source["inverse_code"]),
         "Independent rational rank-one columns")
    e, k = r.sparse(old["response"]), r.sparse(source["centre_response"])
    need(all(classes[p] == classes[t] for p, row in enumerate(k) for t in row), "Coded class support")
    for j in range(112):
        x = r.unit(112, j)
        need(formula(formula(x), True) == formula(formula(x, True)) == x, "Both inverse orders")
        need(formula(r.apply(e, formula(x, True))) == r.apply(k, x), "Actual response conjugation")
    reports = {}
    converted = {}
    for name, key, expected in [("forward", "scalar_word", rows),
                                ("inverse", "inverse_scalar_word", inverse_rows)]:
        old_units = divides = multiplies = 0
        events = []
        forward_rows = [{p: F(1)} for p in range(112)]
        norm = F(1)
        for kind, target, origin, text in source[key]:
            c = F(text)
            need(0 <= target < 112, "Actual target field")
            if kind in ("fixed_divide", "fixed_multiply"):
                need(origin is None and c == 3, "Fixed odd service")
                divides += 2 * (kind == "fixed_divide")
                multiplies += 2 * (kind == "fixed_multiply")
                c = 1 / c if kind == "fixed_divide" else c
                kind = "scale"
            else:
                a, b = abs(c.numerator), c.denominator
                need(c and b & (b - 1) == 0, "Old dyadic event")
                if kind == "add":
                    need(0 <= origin < 112 and origin != target, "Actual source field")
                    old_units += 2 * (1 + a.bit_length() + a.bit_count() + b.bit_length())
                else:
                    need(kind == "scale" and origin is None and a & (a - 1) == 0, "Old unit scale")
                    old_units += 2 * (abs(a.bit_length() - b.bit_length()) + int(c < 0))
            events.append([kind, target, origin, str(c)])
            if kind == "scale":
                forward_rows[target] = {p: value * c for p, value in forward_rows[target].items()}
            else:
                for p, value in forward_rows[origin].items():
                    r.add(forward_rows[target], p, c * value)
            norm = max(norm, sum(map(abs, forward_rows[target].values()), F(0)))
        need(old_units == 4204 and norm == 12, "Full old invoice and prefix norm")
        need((divides, multiplies) == ((16, 0) if name == "forward" else (0, 16)), "Odd service invoice")
        for i in range(640):
            want = {(p, 0): value for p, value in expected[i].items()} if i < 112 else {(i, 0): F(1)}
            need(r.reverse_output(events, i) == want, "All640 reverse literal outputs")
        converted[name] = events
        reports[name] = {"old_scalar_units": old_units, "real_division_by_three_scans": divides,
                         "real_multiplication_by_three_scans": multiplies, "prefix_row_one_norm": str(norm)}
    need(all(r.reverse_output(converted["forward"] + converted["inverse"], i) == {(i, 0): F(1)}
             for i in range(640)), "All640 literal restoration outputs")
    active = set(source["active_sum_carriers"])
    reduced = r.sparse(source["reduced_code"])
    need(len(active) == 56, "Active class sums")
    need(all(row == {p: F(1)} for p, row in enumerate(reduced) if p not in active), "Passive identity")
    need(all(set(reduced[p]) <= active for p in active), "No passive reads")
    reduction_events = source["reduction_word"]
    t = [{p: c for (p, mask), c in r.reverse_output(reduction_events, i).items() if mask == 0}
         for i in range(112)]
    ti = [{p: c for (p, mask), c in r.reverse_output(r.inverse_word(reduction_events), i).items() if mask == 0}
          for i in range(112)]
    need(t == r.sparse(source["reduction"]), "Literal reduction matrix")
    need(all(classes[p] == classes[i] for i, row in enumerate(t) for p in row),
         "Actual reduction preserves global classes")
    reduced_events = []
    for kind, target, origin, text in source["reduced_code_word"]:
        c = F(text)
        if kind == "fixed_divide":
            kind, c = "scale", 1 / c
        elif kind == "fixed_multiply":
            kind = "scale"
        reduced_events.append([kind, target, origin, str(c)])
    for i in range(112):
        want = {(p, 0): c for p, c in reduced[i].items()}
        need(r.reverse_output(reduced_events, i) == want, "Literal reduced code")
        x = r.unit(112, i)
        need(r.apply(t, formula(r.apply(ti, x))) == r.apply(reduced, x),
             "Actual active-coordinate factorization")
    receipt = {"status": "PASS_INDEPENDENT_PHASE_CLASS_REDUCTION_BASELINE",
               "root_pins": PINS, "helper_pin": HELPER_PIN, "old_response_pin": OLD_PIN,
               "pair_pin": CYCLIC_PIN, "arbitrary_output_rows": 640, "unchanged_roles": 528,
               "reports": reports, "active_fields": 56,
               "scope": "General ordered proof and exact rational scalar baseline. No compiled physical phase recipes or caller admission."}
    raw = (json.dumps(receipt, indent=2, sort_keys=True) + "\n").encode()
    (args.out / "CHECKS.json").write_bytes(raw)
    print(receipt["status"])
    print("receipt_sha256=" + sha256(raw).hexdigest())


if __name__ == "__main__":
    main()
