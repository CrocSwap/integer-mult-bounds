#!/usr/bin/env python3
"""Bind the rank-two response and the small clique cover to actual ports."""

import argparse
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
LANES = HERE.parents[1]
PINS = {
    "independent-review-20261017/cyclic-pair-flags-20261018/CYCLIC-FLAGS.json":
        "3034e1df3670f64e5b79a51a435d7903f3be7cef10d6b486a8bd4d420c989585",
    "controller-followthrough-20261017/matched-involution-20261018/MATCHED-INVOLUTION-PROGRAM.json":
        "e2443eee2a7081ce3b57b9b7afcf4f1b061b9d8ddf0fbbeb5f7b29ce0d148902",
}
CLIQUES = [
    [5, 34, 40, 85, 97], [3, 32, 38, 50, 95], [24, 48, 67, 80, 82],
    [23, 35, 55, 65, 68], [1, 17, 66, 75, 83], [8, 12, 45, 107, 109],
    [29, 49, 54, 56, 108], [26, 30, 64, 73, 96], [4, 33, 69, 74, 88],
    [18, 22, 84], [19, 28, 77], [39, 58, 86], [6, 98, 100, 101, 102],
    [31, 59, 60, 93, 103],
]


def need(test, message):
    if not test:
        raise ValueError(message)


def read(relative):
    raw = (LANES / relative).read_bytes()
    need(sha256(raw).hexdigest() == PINS[relative], "Source pin " + relative)
    return json.loads(raw)


def identity(n):
    return [{i: F(1)} for i in range(n)]


def add(target, source, coefficient=F(1)):
    for key, value in source.items():
        target[key] = target.get(key, F(0)) + coefficient * value
        if not target[key]:
            del target[key]


def product(a, b):
    result = []
    for row in a:
        value = {}
        for j, coefficient in row.items():
            add(value, b[j], coefficient)
        result.append(value)
    return result


def transpose(a, n):
    result = [{} for _ in range(n)]
    for i, row in enumerate(a):
        for j, value in row.items():
            result[j][i] = value
    return result


def restrict(a, ports):
    index = {p: i for i, p in enumerate(ports)}
    return [{index[p]: value for p, value in a[row].items() if p in index}
            for row in ports]


def rank(rows, columns):
    rows = [dict(row) for row in rows]
    pivot = 0
    for column in range(columns):
        found = next((i for i in range(pivot, len(rows)) if rows[i].get(column)), None)
        if found is None:
            continue
        rows[pivot], rows[found] = rows[found], rows[pivot]
        c = rows[pivot][column]
        rows[pivot] = {p: v / c for p, v in rows[pivot].items()}
        for i in range(pivot + 1, len(rows)):
            if rows[i].get(column):
                add(rows[i], rows[pivot], -rows[i][column])
        pivot += 1
    return pivot


def determinant(rows):
    rows = [dict(row) for row in rows]
    result = F(1)
    for column in range(len(rows)):
        found = next((i for i in range(column, len(rows)) if rows[i].get(column)), None)
        if found is None:
            return F(0)
        if found != column:
            rows[column], rows[found] = rows[found], rows[column]
            result = -result
        c = rows[column][column]
        result *= c
        for i in range(column + 1, len(rows)):
            if rows[i].get(column):
                add(rows[i], rows[column], -rows[i][column] / c)
    return result


def inverse_word(word):
    return [[op, target, origin, str(1 / F(c) if op == "scale" else -F(c))]
            for op, target, origin, c in reversed(word)]


def transpose_word(word):
    return [[op, target if op == "scale" else origin,
             origin if op == "scale" else target, c]
            for op, target, origin, c in reversed(word)]


def replay(word):
    state = identity(112)
    maximum = F(1)
    for op, target, origin, coefficient in word:
        c = F(coefficient)
        if op == "scale":
            state[target] = {p: c * v for p, v in state[target].items() if c * v}
        else:
            need(op == "add" and target != origin, "Scalar word grammar")
            add(state[target], state[origin], c)
        maximum = max(maximum, sum(abs(c) for c in state[target].values()))
    return state, maximum


def price(word):
    result = 0
    for op, _, _, coefficient in word:
        c = F(coefficient)
        a, b = abs(c.numerator), c.denominator
        need(a and not b & (b - 1), "Dyadic coefficient")
        if op == "scale":
            need(not a & (a - 1), "Dyadic unit scale")
            result += 2 * (abs(a.bit_length() - b.bit_length()) + (c < 0))
        else:
            result += 2 * (1 + a.bit_length() + a.bit_count() + b.bit_length())
    return result


def maximal_cliques(ports, q):
    n = len(ports)
    adjacent = [sum(1 << j for j, r in enumerate(ports)
                    if i != j and not (q[p] & q[r]).bit_count() % 2)
                for i, p in enumerate(ports)]
    result = []

    def visit(chosen, possible, excluded):
        if not possible and not excluded:
            result.append(chosen)
            return
        options = possible | excluded
        pivot = max((i for i in range(n) if options >> i & 1),
                    key=lambda i: (adjacent[i] & possible).bit_count(), default=0)
        todo = possible & ~adjacent[pivot]
        while todo:
            bit = todo & -todo
            i = bit.bit_length() - 1
            todo -= bit
            visit(chosen | bit, possible & adjacent[i], excluded & adjacent[i])
            possible -= bit
            excluded |= bit

    visit(0, (1 << n) - 1, 0)
    return [[ports[i] for i in range(n) if mask >> i & 1] for mask in sorted(result)]


def encoded(rows):
    return [{str(p): str(c) for p, c in sorted(row.items())} for row in rows]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    cyclic = read(next(name for name in PINS if "CYCLIC" in name))
    matching = read(next(name for name in PINS if "MATCHED" in name))
    selected, small = matching["selected_ports"], matching["small_ports"]
    selected_set = set(selected)
    q = cyclic["ports"]
    h = identity(112)
    codes = []
    for pair in cyclic["pair_codes"]:
        a, b = pair["ports"]
        aa, ab = pair["matrix"][0]
        ba, bb = pair["matrix"][1]
        h[a], h[b] = {a: F(aa), b: F(ab)}, {a: F(ba), b: F(bb)}
        if aa != 1:
            codes.append(["scale", a, None, str(aa)])
        codes.extend([["add", a, b, str(ab)], ["scale", b, None, str(2 * bb)],
                      ["add", b, a, str(ba * aa)]])
    hi = transpose(h, 112)
    for p in cyclic["affected_ports"]:
        hi[p] = {k: v / 2 for k, v in hi[p].items()}
    need(product(h, hi) == identity(112), "Actual pair inverse")
    mode = identity(112)
    mode_inverse = identity(112)
    mode_u, mode_v = [{} for _ in range(112)], []
    mode_word, assignments = [], []
    for vertex, group in enumerate(cyclic["cyclic_carriers"]):
        chosen = [p for p in group if selected_set.intersection(map(int, cyclic["mode_rows"][str(p)]))]
        rest = [p for p in group if p not in chosen]
        need(len(chosen) == 2 and len(rest) == 4, "Two selected modes per vertex")
        order = chosen + rest
        signs = [1, 1 if vertex % 2 == 0 else -1, 1, 1, 1, 1]
        e = [{j: F((i == j) - 1) for j in range(4) if i != j} | {4: F(1)}
             for i in range(4)]
        e += [{5: F(1)}, {0: F(-2), 1: F(-2), 2: F(-2), 3: F(-2), 4: F(3)}]
        swap = [0, 1, 2, 3, 5, 4]
        ei = [{swap[j]: c for j, c in e[swap[i]].items()} for i in range(6)]
        need(product(e, ei) == product(ei, e) == identity(6), "Six-mode reciprocal pair")
        for i, p in enumerate(order):
            mode[p] = {order[j]: c * signs[i] * signs[j] for j, c in e[i].items()}
            mode_inverse[p] = {order[j]: c * signs[i] * signs[j] for j, c in ei[i].items()}
        offset = len(mode_v)
        local_u = [[1, 0]] * 4 + [[0, 1], [2, -1]]
        local_v = [[-1, -1, -1, -1, 1, 0], [0, 0, 0, 0, -1, 1]]
        for i, p in enumerate(order):
            mode_u[p].update({offset + j: F(value * signs[i])
                             for j, value in enumerate(local_u[i]) if value})
        mode_v.extend([{order[j]: F(value * signs[j]) for j, value in enumerate(row) if value}
                       for row in local_v])
        a, b, c = order[:4], order[4], order[5]
        for i, p in enumerate(a):
            mode_word.append(["add", b, p, str(-signs[i])])
        for i, p in enumerate(a):
            mode_word.append(["add", p, b, str(signs[i])])
        mode_word.append(["scale", b, None, "-1"])
        for i, p in enumerate(a):
            mode_word.append(["add", b, p, str(signs[i])])
        mode_word.extend([["add", b, c, "1"], ["add", c, b, "-1"],
                          ["add", b, c, "1"], ["scale", c, None, "-1"]])
        assignments.append({"vertex": vertex, "ordered_carriers_a_b_c": order, "signs": signs})
    need(replay(mode_word)[0] == mode, "In-place rank-two mode code")
    response, response_inverse = product(hi, product(mode, h)), product(hi, product(mode_inverse, h))
    u, v = product(hi, mode_u), product(mode_v, h)
    small_word = []
    need(sorted(p for group in CLIQUES for p in group) == sorted(small), "Exact disjoint64 cover")
    for group in CLIQUES:
        k = len(group)
        need(k in (3, 5), "Dyadic clique size")
        need(all((q[p] & q[r]).bit_count() % 2 == int(p == r)
                 for p in group for r in group), "Actual orthonormal clique")
        for p in group:
            response[p] = {r: F(-1) for r in group if r != p}
            response_inverse[p] = {r: F(int(p == r)) - F(1, k - 1) for r in group}
            u[p] = {len(v): F(-1)}
        v.append({p: F(1) for p in group})
        a, rest = group[0], group[1:]
        small_word.extend([["add", a, p, "1"] for p in rest])
        small_word.extend([["add", p, a, "-1"] for p in rest])
        small_word.append(["scale", a, None, str(1 - k)])
        small_word.extend([["add", a, p, "-1"] for p in rest])
    word = codes + mode_word + inverse_word(codes) + small_word
    common_words = {"E": word, "inverse_E": inverse_word(word),
                    "transpose_E": transpose_word(word),
                    "inverse_transpose_E": transpose_word(inverse_word(word))}
    expected = {"E": response, "inverse_E": response_inverse,
                "transpose_E": transpose(response, 112),
                "inverse_transpose_E": transpose(response_inverse, 112)}
    word_receipts = {}
    for name, gates in common_words.items():
        actual, maximum = replay(gates)
        need(actual == expected[name], "Full112 scalar code " + name)
        need(replay(gates + inverse_word(gates))[0] == identity(112), "Both code orders " + name)
        word_receipts[name] = {"real_scalar_primitives": price(gates),
                               "prefix_row_l1_bound": str(maximum), "owned_fields": 0}
    need(product(response, response_inverse) == product(response_inverse, response) == identity(112),
         "Full112 reciprocal products")
    correction = [dict(row) for row in response]
    for i in range(112):
        add(correction[i], {i: F(-1)})
    need(product(u, v) == correction and rank(u, 30) == rank(v, 112) == 30,
         "Exact full rank30 correction factor")
    l = restrict(response, selected)
    li = [{int(p): F(c) for p, c in row.items()} for row in matching["selected_inverse"]]
    old_l = [{int(p): F(c) for p, c in row.items()} for row in matching["selected_block"]]
    need(l == restrict(response_inverse, selected) == old_l, "Both selected blocks retain L")
    need(product(l, li) == identity(8), "Selected inverse")
    ordinary = sorted(set(range(112)) - selected_set)
    p = [{j: response_inverse[r].get(s, F(0)) for j, s in enumerate(selected)
          if response_inverse[r].get(s)} for r in ordinary]
    n = [{j: response_inverse[r].get(s, F(0)) for j, s in enumerate(ordinary)
          if response_inverse[r].get(s)} for r in selected]
    ordinary_inverse = restrict(response_inverse, ordinary)
    for row, update in zip(ordinary_inverse, product(product(p, li), n)):
        add(row, update, -1)
    ordinary_block = restrict(response, ordinary)
    need(product(ordinary_block, ordinary_inverse) == product(ordinary_inverse, ordinary_block)
         == identity(104), "Both ordinary104 inverse orders")
    need(all(not c.denominator & (c.denominator - 1)
             for row in ordinary_inverse for c in row.values()), "Dyadic ordinary inverse")
    maxima = maximal_cliques(small, q)
    histogram = Counter(map(len, maxima))
    need(histogram == {4: 896, 8: 64}, "Exhaustive maximal clique census")
    # A separate exhaustive extension pass checks the absence of a ninth vertex.
    need(all(not any(p not in clique and all(not (q[p] & q[r]).bit_count() % 2 for r in clique)
                     for p in small) for clique in maxima), "Each reported clique is maximal")
    receipt = {
        "status": "PASS_LOW_DISPLACEMENT_RESPONSE",
        "source_pins": PINS, "checker_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "correction_rank_large48": 16, "correction_rank_small64": 14, "correction_rank_full112": 30,
        "selected_determinant": str(determinant(l)),
        "full_determinant": str(determinant(response)),
        "ordinary104_determinant": str(determinant(ordinary_block)),
        "small_clique_sizes": dict(sorted(Counter(map(len, CLIQUES)).items())),
        "all_maximal_small_clique_sizes": dict(sorted(histogram.items())),
        "common_frame_scalar_codes": word_receipts,
        "scope": "Exact port matrices, principal units, scalar codes and geometry. Native phases and terminal access are separate.",
    }
    payload = {
        "source_pins": PINS, "ports": q, "selected_ports": selected, "ordinary_ports": ordinary,
        "large_ports": cyclic["affected_ports"], "small_ports": small,
        "vertex_assignments": assignments, "mode_response": encoded(mode),
        "mode_inverse": encoded(mode_inverse), "small_cliques": CLIQUES,
        "response": encoded(response), "response_inverse": encoded(response_inverse),
        "correction_U": encoded(u), "correction_V": encoded(v),
        "selected_block": encoded(l), "selected_inverse": encoded(li),
        "ordinary_inverse": encoded(ordinary_inverse), "common_frame_words": common_words,
        "maximal_small_cliques": maxima,
    }
    raw = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode()
    (args.out / "RESPONSE-PROGRAM.json").write_bytes(raw)
    receipt["payload_sha256"] = sha256(raw).hexdigest()
    (args.out / "RESPONSE-CHECKS.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
