#!/usr/bin/env python3
"""Check the row involution from signed blocks and reverse output rows."""

import argparse
from fractions import Fraction as F
from hashlib import sha256
import gzip
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
LANES = HERE.parents[1]
SOURCE = LANES / "controller-followthrough-20261017/row-involution-20261020"
PINS = {
    "FREEZE.json": "538ec208e510af7ee29aff4783d304e393c967697a6612e5c42e38fbc0ab9be2",
    "ROW-INVOLUTION.md": "c8470cc2280a057cbebf4a31ee679495990b200a6d6c033cc39e459eb2cf139f",
    "check_row_involution.py": "a675e5578de4bc264524f7c1a75c5685a1967a65f7d3cd020fb0dc19352d31e9",
    "run-normal/ROW-INVOLUTION.json": "a25551b3b99b82477fde561a742fabe1114acbfe6c67cd14284747aaac3dd95b",
    "run-normal/CHECKS.json": "130cb9ca1eedb58554b259b4a71dac5c4efd75de6790db54aafaec75593110e6",
    "LIMITS-FREEZE.json": "775c1b565ec0aa969f2dbecebb04f4b9a82a561e7e7d842c2b1abae7a75509a6",
    "COMPLETION-LIMITS.md": "91bd564b31766300cc89b87cf808439135d89c27bde655a2fc1842646c304607",
    "check_completion_limits.py": "f07260347b3b5a955c475a25f87873dded309f9bd0bd1ad382c5a21c5acb16bb",
    "limits-normal/COMPLETION-LIMITS.json": "25b15d03837fa2b3544bb2189208bacb06fcfc7dc6d4c8aee6d98174c8a512aa",
    "limits-normal/CHECKS.json": "eb60b314a3cb6896c6afd33b8dc88d422f5ce12ac5ab73ce9a704950c6975276",
}
OLD = LANES / "new-core-transfer-20261017/low-displacement-20261020/odd16-normal-v2/EXTENSION-PROGRAM.json.gz"
OLD_PIN = "d466cea24be92fb7f749d686c5efc63f44ea82575c15f78c38e9d6d4c972eba4"
PAIR = LANES / "independent-review-20261017/cyclic-pair-flags-20261018/CYCLIC-FLAGS.json"
PAIR_PIN = "3034e1df3670f64e5b79a51a435d7903f3be7cef10d6b486a8bd4d420c989585"
HELPER = LANES / "independent-review-20261017/route32-capture-review-20261020/check_review.py"
HELPER_PIN = "c419f63a47d655c4d2a789cf52f0a00d5186cb7728cdd58aac73ceb21845aa89"


def need(test, label):
    if not test:
        raise ValueError(label)


def eye(n):
    return [{i: F(1)} for i in range(n)]


def add(row, j, value):
    value += row.get(j, F(0))
    if value:
        row[j] = value
    else:
        row.pop(j, None)


def multiply(a, b):
    result = []
    for row in a:
        out = {}
        for j, c in row.items():
            for t, value in b[j].items():
                add(out, t, c * value)
        result.append(out)
    return result


def transpose(a, width):
    out = [{} for _ in range(width)]
    for i, row in enumerate(a):
        for j, c in row.items():
            out[j][i] = c
    return out


def difference(a, b):
    out = [dict(row) for row in a]
    for row, subtract in zip(out, b):
        for j, c in subtract.items():
            add(row, j, -c)
    return out


def modular_rank(rows, columns, prime):
    a = [[int(row.get(j, F(0)).numerator % prime) *
          pow(row.get(j, F(0)).denominator, -1, prime) % prime
          for j in columns] for row in rows]
    count = 0
    for j in range(len(columns)):
        found = next((i for i in range(count, len(a)) if a[i][j]), None)
        if found is None:
            continue
        a[count], a[found] = a[found], a[count]
        scale = pow(a[count][j], -1, prime)
        a[count] = [x * scale % prime for x in a[count]]
        for i in range(count + 1, len(a)):
            factor = a[i][j]
            if factor:
                a[i] = [(x - factor * y) % prime for x, y in zip(a[i], a[count])]
        count += 1
        if count == len(a):
            break
    return count


def scalar_invoice(word, width):
    rows = eye(width)
    cost, norm, height = 0, F(1), 0
    for kind, target, origin, text in word:
        c = F(text)
        a, b = abs(c.numerator), c.denominator
        need(0 <= target < width and c and b & (b - 1) == 0, "Dyadic field event")
        if kind == "add":
            need(0 <= origin < width and origin != target, "Distinct ADD fields")
            cost += 2 * (1 + a.bit_length() + a.bit_count() + b.bit_length())
            for j, value in rows[origin].items():
                add(rows[target], j, c * value)
        else:
            need(kind == "scale" and origin is None and a & (a - 1) == 0, "Unit SCALE")
            cost += 2 * (abs(a.bit_length() - b.bit_length()) + int(c < 0))
            rows[target] = {j: c * value for j, value in rows[target].items()}
        norm = max(norm, sum(map(abs, rows[target].values()), F(0)))
        height = max(height, *(x.denominator.bit_length() - 1 for x in rows[target].values()))
    return rows, {"old_real_scalar_units": cost, "prefix_row_one_norm": str(norm),
                  "binary_denominator_height": height}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    for name, pin in PINS.items():
        need(sha256((SOURCE / name).read_bytes()).hexdigest() == pin, "Producer pin " + name)
    need(sha256(HELPER.read_bytes()).hexdigest() == HELPER_PIN, "Independent helper pin")
    need(sha256(PAIR.read_bytes()).hexdigest() == PAIR_PIN, "Pair source pin")
    raw = gzip.decompress(OLD.read_bytes())
    need(sha256(raw).hexdigest() == OLD_PIN, "Actual response pin")
    old = json.loads(raw)["model"]
    source = json.loads((SOURCE / "run-normal/ROW-INVOLUTION.json").read_text())
    limits = json.loads((SOURCE / "limits-normal/COMPLETION-LIMITS.json").read_text())
    flags = json.loads(PAIR.read_text())
    spec = importlib.util.spec_from_file_location("independent_matrix", HELPER)
    r = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(r)
    pivots = [0, 27, 36, 111, 20, 7, 57, 46, 1, 3, 6, 8, 17, 18, 24, 23]
    need(source["pivots"] == pivots, "Actual pivot order")
    pset = set(pivots)
    rest = sorted(set(range(112)) - pset)
    groups = [(x["ordered_carriers_a_b_c"], x["signs"]) for x in old["vertex_assignments"]]
    groups += [(ports, [1] * len(ports)) for ports in old["small_cliques"]]
    need(sorted(p for ports, _ in groups for p in ports) == list(range(112)), "Block partition")
    h, hi = eye(112), eye(112)
    large = set()
    for record in flags["pair_codes"]:
        ps, matrix = record["ports"], record["matrix"]
        need(not (set(ps) & pset) or set(ps) <= pset, "Complete selected pair")
        large.update(ps)
        for i, p in enumerate(ps):
            h[p] = {ps[j]: F(matrix[i][j]) for j in range(2) if matrix[i][j]}
            hi[p] = {ps[j]: F(matrix[j][i], 2) for j in range(2) if matrix[j][i]}
    need(len(large) == 48, "Actual large component")
    need(multiply(h, hi) == multiply(hi, h) == eye(112), "Actual pair inverses")
    metric = [{i: F(2 if i in large else 1)} for i in range(112)]
    need(multiply(h, transpose(h, 112)) == metric, "Physical transpose metric")
    mode_e, mode_a = eye(112), eye(112)
    mode_u, mode_v = [{} for _ in range(112)], []
    for j, (ps, signs) in enumerate(groups):
        d = dict(zip(ps, map(F, signs)))
        selected = pset & set(ps)
        need(len(selected) == 1, "One pivot per signed block")
        p = next(iter(selected))
        need(d[p] == 1 and len(ps) in (6, 8), "Actual signed pivot")
        mode_v.append(d)
        for i in ps:
            mode_u[i] = {j: -d[i]}
            for t, sign in d.items():
                add(mode_e[i], t, -d[i] * sign)
                add(mode_a[i], t, (F(len(ps) - 2 if i == p else 0) - d[i]) * sign)
    e = multiply(hi, multiply(mode_e, h))
    a = multiply(hi, multiply(mode_a, h))
    at = transpose(a, 112)
    u, v = multiply(hi, mode_u), multiply(mode_v, h)
    need(e == r.sparse(old["response"]), "Independent old response")
    need(u == r.sparse(old["correction_U"]) and v == r.sparse(old["correction_V"]), "Actual factor gauge")
    need(a == r.sparse(source["response"]) and at == r.sparse(source["response_transpose"]),
         "Independent signed-block response columns")
    need(multiply(metric, transpose(mode_a, 112)) == multiply(transpose(mode_a, 112), metric),
         "No cross-metric component")
    need(multiply(h, multiply(at, hi)) == transpose(mode_a, 112), "Physical transpose through pair chart")
    need(multiply(a, a) == multiply(at, at) == eye(112), "Both involutions")
    need(all(a[i] == e[i] for i in rest), "All96 ordinary rows")
    need(all(at[i].get(j, F(0)) == e[i].get(j, F(0)) for i in range(112) for j in rest),
         "All96 ordinary transpose columns")
    need(r.eliminate(difference(a, eye(112)), 112)[0] == 16, "Rank(A-I)")
    need(r.eliminate(difference(a, e), 112)[0] == 16, "Separate actual rank(A-E)")
    need(r.eliminate([u[i] for i in rest], 16)[0] == 16, "Ordinary factors force full rank")
    need(r.eliminate(a, 112) == (112, F(1)), "Full determinant")
    need(sum(a[i].get(i, F(0)) for i in range(112)) == 80, "Trace")
    vp = [{j: row.get(p, F(0)) for j, p in enumerate(pivots) if row.get(p)} for row in v]
    vpt = transpose(vp, 16)
    gram = [{i: F(2 if i < 8 else 1)} for i in range(16)]
    need(multiply(vp, vpt) == gram, "Actual selected Gram")
    gram_inverse = [{i: 1 / row[i]} for i, row in enumerate(gram)]
    vpi = multiply(vpt, gram_inverse)
    need(multiply(vp, vpi) == multiply(vpi, vp) == eye(16), "Selected inverse both orders")
    ordinary_u = [u[i] if i in rest else {} for i in range(112)]
    desired = difference([{i: F(-2)} for i in range(16)], multiply(v, ordinary_u))
    completed_u = [dict(row) for row in ordinary_u]
    for p, row in zip(pivots, multiply(vpi, desired)):
        completed_u[p] = row
    need(multiply(v, completed_u) == [{i: F(-2)} for i in range(16)], "General completion contraction")
    need(difference(a, eye(112)) == multiply(completed_u, v), "General completion matches signed formula")
    c = eye(112)
    for p, row in zip(pivots, multiply(vpi, v)):
        c[p] = row
    ci = difference(eye(112), difference(c, eye(112)))
    need(multiply(c, ci) == multiply(ci, c) == eye(112), "Normalized code inverse")
    need(c == r.sparse(source["row_code"]) and ci == r.sparse(source["row_code_inverse"]), "Code binding")
    encoded = eye(112)
    fanout = multiply(u, vp)
    for p in pivots:
        encoded[p] = {p: F(-1)}
    for i in rest:
        for j, value in fanout[i].items():
            add(encoded[i], pivots[j], value)
    need(multiply(c, multiply(a, ci)) == encoded == r.sparse(source["encoded_response"]),
         "Lower triangular encoded response")
    reports = {}
    for section, price in (("common_frame_words", 3276), ("direct_physical_words", 5600)):
        for name, expected in (("A", a), ("AT", at)):
            word = source[section][name]
            forward, invoice = scalar_invoice(word, 112)
            need(forward == expected and invoice["old_real_scalar_units"] == price, "Full scalar invoice")
            for i in range(640):
                want = {(j, 0): value for j, value in expected[i].items()} if i < 112 else {(i, 0): F(1)}
                need(r.reverse_output(word, i) == want, "All640 reverse scalar outputs")
                need(r.reverse_output(word + word, i) == {(i, 0): F(1)}, "All640 literal square")
            reports[section + "/" + name] = invoice
    for name, response, price in (("A", a, 2960), ("AT", at, 1984)):
        word = source["final_query_words"][name]
        expected = eye(224)
        for p in pivots:
            for j, value in response[p].items():
                add(expected[p], 112 + j, value)
        forward, invoice = scalar_invoice(word, 224)
        need(forward == expected and invoice["old_real_scalar_units"] == price, "Late query invoice")
        for i in range(640):
            want = {(j, 0): value for j, value in expected[i].items()} if i < 224 else {(i, 0): F(1)}
            need(r.reverse_output(word, i) == want, "All640 arbitrary-baseline query outputs")
        reports["late_query/" + name] = invoice
    projector = [{i: F(1)} if i in pset else {} for i in range(112)]
    signature = [{i: F(-1 if i in pset else 1)} for i in range(112)]
    symmetric = difference(e, projector)
    symmetric_inverse = multiply(ci, multiply(signature, transpose(ci, 112)))
    need(symmetric == transpose(symmetric, 112) == multiply(c, a), "Symmetric completion")
    need(symmetric == multiply(transpose(c, 112), multiply(signature, c)), "Exact congruence")
    need(symmetric == r.sparse(limits["symmetric_response"]) and
         symmetric_inverse == r.sparse(limits["symmetric_response_inverse"]), "Symmetric source binding")
    need(multiply(symmetric, symmetric_inverse) == multiply(symmetric_inverse, symmetric) == eye(112),
         "Both symmetric inverse orders")
    need(r.eliminate(difference(symmetric, eye(112)), 112)[0] == 32, "Symmetric displacement rank")
    need(r.eliminate(symmetric, 112) == (112, F(1)), "Symmetric determinant")
    for name, key, expected in (("S", "symmetric_word", symmetric),
                                ("S_inverse", "symmetric_inverse_word", symmetric_inverse)):
        word = limits[key]
        forward, invoice = scalar_invoice(word, 112)
        need(forward == expected and invoice["old_real_scalar_units"] == 2508, "Symmetric literal invoice")
        for i in range(640):
            want = {(j, 0): value for j, value in expected[i].items()} if i < 112 else {(i, 0): F(1)}
            need(r.reverse_output(word, i) == want, "All640 symmetric outputs")
        reports["common_frame_words/" + name] = invoice
    for first, second in (("symmetric_word", "symmetric_inverse_word"),
                          ("symmetric_inverse_word", "symmetric_word")):
        need(all(r.reverse_output(limits[first] + limits[second], i) == {(i, 0): F(1)}
                 for i in range(640)), "Both literal symmetric inverse orders")
    expected = eye(224)
    for p in pivots:
        for j, value in symmetric[p].items():
            add(expected[p], 112 + j, value)
    forward, invoice = scalar_invoice(limits["symmetric_query_word"], 224)
    need(forward == expected and invoice["old_real_scalar_units"] == 1904, "Symmetric late query")
    for i in range(640):
        want = {(j, 0): value for j, value in expected[i].items()} if i < 224 else {(i, 0): F(1)}
        need(r.reverse_output(limits["symmetric_query_word"], i) == want,
             "All640 symmetric arbitrary-baseline query outputs")
    reports["late_query/S"] = invoice
    response_metric = [{i: F(-1)} for i in range(112)]
    for ps, _ in groups:
        p = next(iter(pset & set(ps)))
        response_metric[p] = {p: F(len(ps) - 3)}
    response_metric_inverse = [{i: 1 / row[i]} for i, row in enumerate(response_metric)]
    need(response_metric == r.sparse(limits["metric"]) and
         response_metric_inverse == r.sparse(limits["metric_inverse"]), "Response metric binding")
    need(multiply(h, response_metric) == multiply(response_metric, h), "Metric preserved by pair chart")
    need(at == multiply(response_metric_inverse, multiply(a, response_metric)), "Weighted transpose")
    need(multiply(at, multiply(response_metric_inverse, a)) == response_metric_inverse,
         "Inverse metric preservation")
    need({value.denominator for row in response_metric_inverse for value in row.values()} == {1, 3, 5},
         "Odd inverse-metric services remain")
    small = sorted(set(range(112)) - large)
    modular = {"large_mod5_rank": modular_rank([e[i] for i in sorted(large)], sorted(large), 5),
               "small_mod7_rank": modular_rank([e[i] for i in small], small, 7)}
    need(modular == {"large_mod5_rank": 40, "small_mod7_rank": 56}, "Actual modular row obstruction")
    receipt = {
        "status": "PASS_INDEPENDENT_ROW_INVOLUTION",
        "producer_pins": PINS, "old_response_pin": OLD_PIN, "pair_pin": PAIR_PIN,
        "independent_helper_pin": HELPER_PIN, "reports": reports,
        "ordinary_factor_rank": 16, "rank_A_minus_I": 16, "rank_A_minus_E": 16,
        "determinant": "1", "trace": 80, "unchanged_ordinary_rows": 96,
        "symmetric_displacement_rank": 32, "symmetric_determinant": "1",
        "modular_ranks": modular, "arbitrary_input_fields": 640,
        "scope": "Exact completion algebra, actual transpose metric, scalar words and baseline queries. No native service or caller.",
    }
    output = (json.dumps(receipt, indent=2, sort_keys=True) + "\n").encode()
    (args.out / "CHECKS.json").write_bytes(output)
    print(receipt["status"])
    print("receipt_sha256=" + sha256(output).hexdigest())


if __name__ == "__main__":
    main()
