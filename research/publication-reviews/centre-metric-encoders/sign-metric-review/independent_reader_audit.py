#!/usr/bin/env python3
"""Check the selected readers without importing a source program."""

import argparse
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path


ZERO, ONE = (Q(0), Q(0)), (Q(1), Q(0))


def need(condition, label):
    if not condition:
        raise ValueError(label)


def add(a, b):
    return a[0]+b[0], a[1]+b[1]


def mul(a, b):
    return a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]


def conjugate(a):
    return a[0], -a[1]


def decode(rows):
    return [{int(j): tuple(Q(x) for x in z) for j, z in row.items()} for row in rows]


def eye(n):
    return [{i: ONE} for i in range(n)]


def product(a, b):
    result = []
    for row in a:
        target = {}
        for k, value in row.items():
            for j, other in b[k].items():
                target[j] = add(target.get(j, ZERO), mul(value, other))
        result.append({j: z for j, z in target.items() if z != ZERO})
    return result


def restrict(rows, columns):
    return [{j: row[p] for j, p in enumerate(columns) if p in row} for row in rows]


def residue(q):
    return q.numerator*pow(q.denominator, -1, 5) % 5


def residue_rank(rows, columns, image_i):
    a = [[(residue(row.get(j, ZERO)[0])+image_i*residue(row.get(j, ZERO)[1])) % 5
          for j in columns] for row in rows]
    pivot = 0
    for j in range(len(columns)):
        found = next((i for i in range(pivot, len(a)) if a[i][j]), None)
        if found is None:
            continue
        a[pivot], a[found] = a[found], a[pivot]
        scale = pow(a[pivot][j], -1, 5)
        a[pivot] = [x*scale % 5 for x in a[pivot]]
        for i in range(pivot+1, len(a)):
            scale = a[i][j]
            a[i] = [(x-scale*y) % 5 for x, y in zip(a[i], a[pivot])]
        pivot += 1
        if pivot == len(a):
            break
    return pivot


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--annex", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    need(not args.out.exists(), "Use a new output file")
    root = args.annex / "frozen/root"
    pins = {"sign-metric-normal-20261020/RESPONSE.json":
            "9ae1c4bf391f8ac082d2137e686f7de474005002399648bff5d443c3bc215c9c",
            "sign-metric-unit-normal-20261020/RESPONSE.json":
            "1fe13e786e70ef7408fb5fbd121d08fb40d8ce0e117fe096aaee9f4243140d6a"}
    packets = []
    for name, expected in pins.items():
        raw = (root/name).read_bytes()
        need(sha256(raw).hexdigest() == expected, "Frozen payload pin")
        packets.append(json.loads(raw))
    old, new = packets
    old_v, new_v = decode(old["correction_V"]), decode(new["correction_V"])
    selected, full, centres = old["selected"], new["full_ports"], new["centre_ports"]
    need(len(selected) == 24 and len(full) == 32 and len(centres) == 16, "Actual field counts")
    ranks = {}
    for image_i in (2, 3):
        need((image_i*image_i+1) % 5 == 0, "Gaussian residue map")
        ranks[str(image_i)] = {
            "old_selected24": residue_rank(old_v, selected, image_i),
            "old_full112": residue_rank(old_v, list(range(112)), image_i),
            "old_expanded32": residue_rank(old_v, full, image_i),
            "new_centres16": residue_rank(new_v, centres, image_i),
        }
    need(ranks["3"] == {"old_selected24": 8, "old_full112": 16,
                        "old_expanded32": 16, "new_centres16": 16}, "Actual F5 obstruction and release")
    need(ranks["2"] == {"old_selected24": 16, "old_full112": 16,
                        "old_expanded32": 16, "new_centres16": 16}, "Other Gaussian residue sector")
    real_only = [{j: (value[0], Q(0)) for j, value in row.items()} for row in old_v]
    need(residue_rank(real_only, selected, 3) == 16, "Discarding imaginary coefficients loses the obstruction")
    vanished = [i for i, row in enumerate(old_v)
                if all((residue(row.get(j, ZERO)[0])+3*residue(row.get(j, ZERO)[1])) % 5 == 0
                       for j in selected)]
    need(vanished == list(range(8, 16)), "Exactly the eight small reader rows vanish")

    minor, inverse = decode(new["centre_minor"]), decode(new["centre_minor_inverse"])
    need(minor == restrict(new_v, centres), "Actual selected minor")
    need(product(minor, inverse) == product(inverse, minor) == eye(16), "Both exact minor inverse orders")
    reader = decode(new["centre_reader"])
    need(product(inverse, new_v) == reader and restrict(reader, centres) == eye(16), "Actual normalized reader")
    code, code_inverse = decode(new["row_code"]), decode(new["row_code_inverse"])
    expected = eye(112)
    for row, p in zip(reader, centres):
        expected[p] = row
    need(code == expected, "Actual row code")
    need(product(code, code_inverse) == product(code_inverse, code) == eye(112), "Both exact code inverse orders")
    need(all(q.denominator & (q.denominator-1) == 0
             for rows in (minor, inverse, reader, code, code_inverse)
             for row in rows for value in row.values() for q in value), "All reader and code coefficients are dyadic")

    # A concrete off-diagonal entry of C*DC differs from the diagonal metric.
    p, j = next((p, j) for p in centres for j, value in code[p].items()
                if j not in centres and value != ZERO)
    metric = decode(new["metric"])
    entry = ZERO
    for k in range(112):
        entry = add(entry, mul(mul(conjugate(code[k].get(p, ZERO)), metric[k][k]),
                               code[k].get(j, ZERO)))
    need(entry != ZERO and metric[p].get(j, ZERO) == ZERO, "C does not preserve D")
    need(mul((Q(1), Q(-1)), (Q(1, 2), Q(1, 2))) == ONE, "Norm-two reader unit")
    need([(a, b) for a in range(3) for b in range(3) if (a*a+b*b) % 3 == 0] == [(0, 0)],
         "Norm-three descent residue")
    result = {
        "status": "PASS_INDEPENDENT_SIGN_METRIC_READER_AUDIT",
        "method": "Direct Gaussian-rational arithmetic and both F5 residue sectors; no source program import",
        "payload_pins": pins,
        "residue_ranks": ranks,
        "vanishing_selected_reader_rows_at_i3": vanished,
        "real_only_mutation_rank": 16,
        "exact_minor_inverse_orders": 2,
        "exact_code_inverse_orders": 2,
        "reader_and_code_gaussian_dyadic": True,
        "coded_metric_rejection_witness": {"row": p, "column": j,
                                          "C_star_D_C": [str(x) for x in entry], "D": ["0", "0"]},
        "scope": "Selected-reader obstruction and unit-code release; modular full ranks alone are not a unit proof",
        "checks_not_run": ["Native lowering or cost", "Complete caller or recursive invoice", "Kappa calculation"],
    }
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True)+"\n", encoding="utf-8")
    print(result["status"])


if __name__ == "__main__":
    main()
