"""Check the phase-access identities without package imports."""

import argparse
from collections import Counter
from fractions import Fraction as F
import gzip
from hashlib import sha256
import json
from pathlib import Path


def need(value, message):
    if not value:
        raise ValueError(message)


def multiply(a, b):
    return [[sum(x * y for x, y in zip(row, col)) for col in zip(*b)] for row in a]


def unit(n):
    return [[F(i == j) for j in range(n)] for i in range(n)]


def update(u, v):
    return [[F(i == j) + x * y for j, y in enumerate(v)] for i, x in enumerate(u)]


def binary_product(a, b):
    result = []
    for row in a:
        value = 0
        for i, other in enumerate(b):
            if row >> i & 1:
                value ^= other
        result.append(value)
    return result


def binary_inverse(a):
    n = len(a)
    rows = [row | (1 << (n + i)) for i, row in enumerate(a)]
    for col in range(n):
        pick = next(i for i in range(col, n) if rows[i] >> col & 1)
        rows[col], rows[pick] = rows[pick], rows[col]
        for i in range(n):
            if i != col and rows[i] >> col & 1:
                rows[i] ^= rows[col]
    need([r & ((1 << n) - 1) for r in rows] == [1 << i for i in range(n)], "Binary inverse")
    return [r >> n for r in rows]


def binary_rank(rows):
    return len({r.bit_length() for r in echelon(rows)})


def echelon(rows):
    pivots = {}
    for row in rows:
        while row:
            k = row.bit_length()
            if k not in pivots:
                pivots[k] = row
                break
            row ^= pivots[k]
    return list(pivots.values())


def line(q):
    return [(1 << i) ^ ((q << 9) if q >> i & 1 else 0) for i in range(9)] + [1 << i for i in range(9, 18)]


def circuit(word):
    result = [1 << i for i in range(18)]
    for gate in word:
        if gate[0] == "C":
            step = line(gate[1]) if gate[2] % 2 else [1 << i for i in range(18)]
        elif gate[0] == "D":
            step = [1 << i for i in range(9)] + [(1 << (9 + i)) ^ gate[1][i] for i in range(9)]
        else:
            need(gate[0] == "P", "Address gate")
            back = binary_inverse(gate[1])
            step = gate[1] + [sum(((back[j] >> i) & 1) << (9 + j) for j in range(9)) for i in range(9)]
        result = binary_product(step, result)
    return result


def fourier_rank(matrix):
    return binary_rank([row >> 9 for row in matrix[:9]])


def gaussian_product(a, b):
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    pins = {}

    def read(name):
        raw = (args.source_root / name).read_bytes()
        pins[name] = sha256(raw).hexdigest()
        return json.loads(gzip.decompress(raw) if name.endswith(".gz") else raw)

    model = read("lanes/new-core-transfer-20261017/low-displacement-20261020/odd16-normal-v2/EXTENSION-PROGRAM.json.gz")["model"]
    labels = model["ports"]
    root_space = {0}
    for value in [30, 45, 75, 384]:
        root_space |= {x ^ value for x in root_space}
    classes = [min(q ^ x for x in root_space) for q in labels]
    need(len(root_space) == 16 and Counter(Counter(classes).values()) == {8: 14}, "Actual classes")
    groups = [(g["ordered_carriers_a_b_c"], g["signs"]) for g in model["vertex_assignments"]]
    groups += [(g, [1] * len(g)) for g in model["small_cliques"]]
    pairs = []
    for ports, signs in groups:
        k = len(ports)
        selected_pairs = [[p for p in ports if classes[p] == g] for g in sorted({classes[p] for p in ports})]
        need(all(len(pair) == 2 for pair in selected_pairs), "Actual class pairs")
        pairs += selected_pairs
        p, t = [ports.index(x) for x in selected_pairs[0]]
        d = list(map(F, signs))
        e = [d[i] if i in (p, t) else F(0) for i in range(k)]
        u = [2 * x - y for x, y in zip(e, d)]
        v = [2 * y / k - x / 2 for x, y in zip(e, d)]
        delta = 1 + sum(x * y for x, y in zip(u, v))
        need(delta == F(2 * (4 - k), k), "Rational determinant")
        s, si = update(u, v), update(u, [-x / delta for x in v])
        response = update(d, [-x for x in d])
        need(multiply(s, si) == unit(k), "Rational inverse")
        need(multiply(multiply(s, response), si) == update(e, [-F(k, 2) * x for x in e]), "Rational capture")
        if k == 6:
            a, b = [F(0)] * k, [F(0)] * k
            a[p], b[p], b[t] = 2 * d[p], 3 * d[p], -d[t]
            u = [x - y for x, y in zip(a, d)]
            v = [(x - y) / 4 for x, y in zip(d, b)]
        else:
            a = b = [2 * x for x in e]
            v = [-x / 4 for x in u]
        s = update(u, v)
        need(multiply(s, s) == unit(k), "Dyadic involution")
        need(multiply(multiply(s, response), s) == update(a, [-x for x in b]), "Dyadic capture")

    frames = [read("lanes/controller-followthrough-20261017/shared-root-eight-20261020/v2-normal/PROGRAM.json.gz")["W"], read("lanes/coherent-port/isotropic-pair-gauge-20261018/GAUGE-PROGRAMS.json")["W"]["circuit"]]
    matrices = [circuit(word) for word in frames]
    ranks = []
    for matrix in matrices:
        back = binary_inverse(matrix)
        ranks.append([fourier_rank(binary_product(binary_product(matrix, binary_product(line(labels[i]), line(labels[j]))), back)) for i, j in pairs])
    need(ranks == [[0] * 56, [2] * 56], "W_R succeeds and W45 fails on every pair")
    need([fourier_rank(x) for x in matrices] == [4, 1], "Exact frame ranks")
    need(binary_rank([labels[i] ^ labels[j] for i, j in pairs]) == 4, "Common gauge lower-bound input")

    powers = [[(1, 0)], [(1, 0)]]
    for _ in range(73):
        for seq, base in zip(powers, [(1, 1), (1, -1)]):
            seq.append(gaussian_product(seq[-1], base))
    endpoint_counts = {}
    for n in range(9, 74, 8):
        count = 0
        for wx in range(n + 1):
            for wy in range(n + 1):
                for overlap in range(max(0, wx + wy - n), min(wx, wy) + 1):
                    distance = wx + wy - 2 * overlap
                    right = gaussian_product(powers[0][n - distance], powers[1][distance])
                    sign = (-1) ** (wx // 2 + wy // 2)
                    right = tuple(sign * x for x in right)
                    left = (1, 1) if wx % 2 == wy % 2 else (1, -1)
                    scale = ((-1) ** (overlap + (wx % 2) * (wy % 2))) * (1 << ((n - 1) // 2))
                    need(right == tuple(scale * x for x in left), "Exact endpoint kernel by weight triple")
                    count += 1
        endpoint_counts[n] = count
    result = {"status": "PASS_INDEPENDENT_PHASE_ACCESS", "source_sha256": pins, "signed_blocks": len(groups), "actual_pairs": len(pairs), "W_R_pair_ranks": dict(Counter(ranks[0])), "W45_pair_ranks": dict(Counter(ranks[1])), "pair_difference_rank": 4, "endpoint_complete_weight_triples": endpoint_counts, "scope": "Exact source blocks, binary frame geometry, and every endpoint kernel weight class. No access or supplier admission."}
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"])


if __name__ == "__main__":
    main()
