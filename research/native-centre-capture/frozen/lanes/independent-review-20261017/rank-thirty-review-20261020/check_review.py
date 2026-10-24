#!/usr/bin/env python3
"""Check the full response with independent columns and clique extension."""

from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
LANES = HERE.parents[1]
SOURCE = LANES / "new-core-transfer-20261017/low-displacement-20261020"
PINS = {
    "RESPONSE-FREEZE.json": "59e43eb802114070aa40b39a7e355b3271a744b713a32c5a3e09c2e46ec7fdc9",
    "RESPONSE.md": "5ea5866231992c389ae2796f1534e0af90ca88bcedfa3fa9758d78f9457d2981",
    "check_response.py": "c6d92104e4345816e86163f6c1dea24fbd9b6e9b133ffd2e0c646dca17ca00a8",
    "run-normal/RESPONSE-PROGRAM.json": "5832788135e16c2427f8c746f251501621684a02ef88b0a14322056653dc2d7c",
    "run-normal/RESPONSE-CHECKS.json": "7f84440d79200b8c060aad07b910bb96f2bcdde95b07ddb8d41bcea1fcb09d5c",
}


def need(ok, label):
    if not ok:
        raise ValueError(label)


def unit(n, j):
    return [F(i == j) for i in range(n)]


def sparse(rows):
    return [{int(k): F(v) for k, v in row.items()} for row in rows]


def apply(rows, x):
    return [sum((v * x[j] for j, v in row.items()), F(0)) for row in rows]


def eliminate(rows, width):
    a = [dict(row) for row in rows]
    pivot, det = 0, F(1)
    for j in range(width):
        p = next((i for i in range(pivot, len(a)) if a[i].get(j)), None)
        if p is None:
            continue
        if p != pivot:
            a[p], a[pivot] = a[pivot], a[p]
            det = -det
        value = a[pivot][j]
        det *= value
        for i in range(pivot + 1, len(a)):
            value_i = a[i].get(j, F(0)) / value
            if not value_i:
                continue
            for k, c in a[pivot].items():
                new = a[i].get(k, F(0)) - value_i * c
                if new:
                    a[i][k] = new
                else:
                    a[i].pop(k, None)
        pivot += 1
        if pivot == len(a):
            break
    return pivot, det if pivot == width == len(a) else None


def restrict(rows, ports):
    return [{j: rows[p][q] for j, q in enumerate(ports) if q in rows[p]} for p in ports]


def main():
    for name, digest in PINS.items():
        need(sha256((SOURCE / name).read_bytes()).hexdigest() == digest, "Producer pin")
    packet = json.loads((SOURCE / "run-normal/RESPONSE-PROGRAM.json").read_text())
    inputs = {}
    for name, digest in packet["source_pins"].items():
        raw = (LANES / name).read_bytes()
        need(sha256(raw).hexdigest() == digest, "Inherited source pin")
        inputs[Path(name).name] = json.loads(raw)
    cyclic = inputs["CYCLIC-FLAGS.json"]
    matching = inputs["MATCHED-INVOLUTION-PROGRAM.json"]
    selected = matching["selected_ports"]
    need(packet["selected_ports"] == selected, "Original selected set")
    need(packet["ports"] == cyclic["ports"], "Actual binary directions")
    assignments = []
    for v, c in enumerate(cyclic["cyclic_carriers"]):
        chosen = [p for p in c if set(map(int, cyclic["mode_rows"][str(p)])) & set(selected)]
        need(len(chosen) == 2, "Selected mode count")
        assignments.append({"vertex": v, "ordered_carriers_a_b_c":
                            chosen + [p for p in c if p not in chosen],
                            "signs": [1, (-1) ** v, 1, 1, 1, 1]})
    need(assignments == packet["vertex_assignments"], "Selected-mode assignment")

    def pair(x, inverse=False):
        out = list(x)
        for entry in cyclic["pair_codes"]:
            ps, h = entry["ports"], entry["matrix"]
            for i, p in enumerate(ps):
                out[p] = sum((F(h[j][i], 2) if inverse else F(h[i][j])) * x[ps[j]]
                             for j in range(2))
        return out

    def formula(x, inverse=False, wrong_sign=False):
        coded, result = pair(x), list(x)
        mixed = list(coded)
        for entry in assignments:
            ps, d = entry["ordered_carriers_a_b_c"], list(entry["signs"])
            if wrong_sign:
                d[1] = 1
            values = [coded[p] * sign for p, sign in zip(ps, d)]
            if inverse:
                values[-2], values[-1] = values[-1], values[-2]
            query = values[-2] - sum(values[:4])
            values = [a + query for a in values[:4]] + [values[-2] + 2 * query, values[-1]]
            if not inverse:
                values[-2], values[-1] = values[-1], values[-2]
            for p, sign, value in zip(ps, d, values):
                mixed[p] = sign * value
        result = pair(mixed, True)
        for c in packet["small_cliques"]:
            total = sum(x[p] for p in c) / (len(c) - 1 if inverse else 1)
            for p in c:
                result[p] = x[p] - total
        return result

    e, ei = sparse(packet["response"]), sparse(packet["response_inverse"])
    columns, inverse_columns = [], []
    for j in range(112):
        x = unit(112, j)
        a, b = formula(x), formula(x, True)
        need(a == apply(e, x) and b == apply(ei, x), "Independent response columns")
        need(formula(a, True) == formula(b) == x, "Full inverse orders")
        columns.append(a)
        inverse_columns.append(b)
    need(any(formula(unit(112, p), wrong_sign=True) != formula(unit(112, p)) for p in selected),
         "Reject omitted selected sign")
    old_l = sparse(matching["selected_block"])
    li = sparse(packet["selected_inverse"])
    need(restrict(e, selected) == restrict(ei, selected) == old_l, "Both selected blocks")
    need(all(apply(old_l, apply(li, unit(8, j))) == apply(li, apply(old_l, unit(8, j))) == unit(8, j)
             for j in range(8)), "Selected inverse orders")
    ordinary = sorted(set(range(112)) - set(selected))
    need(ordinary == packet["ordinary_ports"], "Ordinary partition")
    h, hi = restrict(e, ordinary), sparse(packet["ordinary_inverse"])
    need(all(c.denominator & (c.denominator - 1) == 0 for row in hi for c in row.values()),
         "Dyadic ordinary inverse")
    need(all(apply(h, apply(hi, unit(104, j))) == apply(hi, apply(h, unit(104, j))) == unit(104, j)
             for j in range(104)), "Ordinary inverse orders")
    need(eliminate(old_l, 8)[1] == F(1, 16), "Selected determinant")
    need(eliminate(e, 112)[1] == 2 ** 25, "Full determinant")
    need(eliminate(h, 104)[1] == 2 ** 21, "Ordinary determinant")
    u, v = sparse(packet["correction_U"]), sparse(packet["correction_V"])
    need(eliminate(u, 30)[0] == eliminate(v, 112)[0] == 30, "Factor ranks")
    for j in range(112):
        x = unit(112, j)
        need(apply(u, apply(v, x)) == [a - b for a, b in zip(columns[j], x)], "Correction factor")

    word_receipts = {}
    for name, gates in packet["common_frame_words"].items():
        expected = inverse_columns if "inverse" in name else columns
        if "transpose" in name:
            expected = [list(row) for row in zip(*expected)]
        prefix_norms = [F(0)] * len(gates)
        price = 0
        parsed = []
        for kind, target, origin, text in gates:
            c = F(text)
            need(0 <= target < 112 and c != 0, "Literal field and coefficient")
            need(c.denominator & (c.denominator - 1) == 0, "Dyadic gate")
            a, b = abs(c.numerator), c.denominator
            if kind == "add":
                need(isinstance(origin, int) and 0 <= origin < 112 and origin != target,
                     "Arbitrary-input addition")
                price += 2 * (1 + a.bit_length() + a.bit_count() + b.bit_length())
            else:
                need(kind == "scale" and origin is None and a & (a - 1) == 0, "Unit scale")
                price += 2 * (abs(a.bit_length() - b.bit_length()) + (c < 0))
            parsed.append((kind, target, origin, c))
        for j in range(112):
            x = unit(112, j)
            for k, (kind, target, origin, c) in enumerate(parsed):
                x[target] = x[target] * c if kind == "scale" else x[target] + c * x[origin]
                prefix_norms[k] += abs(x[target])
            need(x == expected[j], "Literal word column " + name)
        norm = max([F(1)] + prefix_norms)
        need(price == 3210 and norm == (14 if "transpose" in name else 44), "Scalar invoice")
        word_receipts[name] = {"columns": 112, "scalar": price, "prefix_row_norm": str(norm)}

    small, q = packet["small_ports"], packet["ports"]
    need(sorted(p for c in packet["small_cliques"] for p in c) == small, "Disjoint small cover")
    need(Counter(map(len, packet["small_cliques"])) == {3: 3, 5: 11}, "Clique cover sizes")
    need(all((q[p] & q[r]).bit_count() % 2 == (p == r)
             for c in packet["small_cliques"] for p in c for r in c), "Actual clique cover")
    need(all(q[p].bit_count() % 2 == (q[p] & 45).bit_count() % 2 == 1 for p in small)
         and (45).bit_count() % 2 == 0, "Affine isotropic obstruction to size nine")
    adjacent = [{r for r in small if r != p and (q[p] & q[r]).bit_count() % 2 == 0}
                for p in range(112)]
    maxima, visited = [], Counter()

    def extend(chosen, options, common):
        visited[len(chosen)] += 1
        if not common:
            maxima.append(tuple(chosen))
        for i, p in enumerate(options):
            extend(chosen + [p], [r for r in options[i + 1:] if r in adjacent[p]],
                   common & adjacent[p])

    extend([], small, set(small))
    need(Counter(map(len, maxima)) == {4: 896, 8: 64}, "Separate maximal clique census")
    need(sorted(maxima) == sorted(tuple(sorted(c)) for c in packet["maximal_small_cliques"]),
         "Every reported maximal clique")
    need(max(visited) == 8, "Maximum clique dimension")
    receipt = {
        "status": "PASS_INDEPENDENT_RANK_THIRTY_RESPONSE",
        "producer_pins": PINS,
        "source_pins": packet["source_pins"],
        "response_columns_per_direction": 112,
        "correction_rank": 30,
        "determinants": {"selected": "1/16", "ordinary": str(2 ** 21), "full": str(2 ** 25)},
        "word_checks": word_receipts,
        "all_clique_sizes": dict(sorted(visited.items())),
        "maximal_clique_sizes": dict(sorted(Counter(map(len, maxima)).items())),
        "scope": "Matrix, scalar words, and actual graph. Native phases and routed terminal are separate.",
    }
    raw = (json.dumps(receipt, indent=2, sort_keys=True) + "\n").encode()
    (HERE / "CHECKS.json").write_bytes(raw)
    print(receipt["status"])
    print("receipt_sha256=" + sha256(raw).hexdigest())


if __name__ == "__main__":
    main()
