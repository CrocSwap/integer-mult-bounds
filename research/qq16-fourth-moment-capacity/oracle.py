#!/usr/bin/env python3
"""Separate block-Gram/Frobenius calculation of all four moments.

Only source extraction is shared with verify.py. This implementation uses
row matrices and direct coefficient contractions, with no collision-pattern
assumption or cyclic stage-word reduction. Apache-2.0.
Prepared for commdata2338, with substantial OpenAI Codex assistance.
"""
import argparse
from fractions import Fraction as Q
import importlib.util
from itertools import product
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("qq16_source_oracle", HERE / "source.py")
src = importlib.util.module_from_spec(spec)
spec.loader.exec_module(src)


def rows(columns):
    n = len(columns)
    return tuple(sum(((columns[j] >> i) & 1) << j for j in range(n))
                 for i in range(n))


def row_product(A, B):
    output = []
    for a in A:
        value = 0
        for j, b in enumerate(B):
            if (a >> j) & 1:
                value ^= b
        output.append(value)
    return tuple(output)


def add_outer(table, route, coefficient, a, b):
    if coefficient:
        matrix = table.setdefault(route, [0]*64)
        for i, x in enumerate(a):
            for j, y in enumerate(b):
                matrix[8*i+j] += coefficient*x*y


def calculate(R, routes, stage_order=(0, 1, 2)):
    U = src.U
    c = {p: tuple(R[i][p] for i in range(8)) for p in U}
    dots = {(p, q): sum(x*y for x, y in zip(c[p], c[q])) for p, q in product(U, repeat=2)}
    gs = [[rows(g) for g in stage] for stage in routes]
    identity = tuple(1 << i for i in range(25))
    h = {(s, t): {p: row_product(gs[s][p], gs[t][p]) for p in U}
         for s, t in product(range(3), repeat=2) if s != t}
    m2 = m3 = m4 = 0
    blocks = {}
    for s, u in product(range(3), repeat=2):
        # C is the block matrix (B_s B_u*), normalized by 48 only at the end.
        C = {}
        if s == u:
            C[identity] = [48*int(i == j) for i in range(8) for j in range(8)]
        else:
            for p in U:
                add_outer(C, h[s, u][p], 1, c[p], c[p])
        C2 = {}
        for t in stage_order:
            if t == s or t == u:
                if s == u:
                    out = C2.setdefault(identity, [0]*64)
                    for i in range(8):
                        out[9*i] += 2304
                else:
                    for g, matrix in C.items():
                        out = C2.setdefault(g, [0]*64)
                        for i, x in enumerate(matrix):
                            out[i] += 48*x
            else:
                for p, q in product(U, repeat=2):
                    if dots[p, q]:
                        g = row_product(h[s, t][p], h[t, u][q])
                        add_outer(C2, g, dots[p, q], c[p], c[q])
        b2 = sum(sum(x*x for x in matrix) for matrix in C.values())
        b3 = sum(sum(x*y for x, y in zip(C[g], C2[g]))
                 for g in C.keys() & C2.keys())
        b4 = sum(sum(x*x for x in matrix) for matrix in C2.values())
        m2 += b2
        m3 += b3
        m4 += b4
        blocks[f"{s}{u}"] = str(Q(b4, 48**4))
    return [Q(24), Q(m2, 48**2), Q(m3, 48**3), Q(m4, 48**4)], blocks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=HERE.parents[1])
    args = parser.parse_args()
    R, routes = src.packet_data(src.load_packet(args.repo))
    src.check_grams(R)
    src.check_swap_charts(routes)
    moments, blocks = calculate(R, routes)
    src.need(moments == [Q(24), Q(28), Q(109, 3), Q(1823, 36)], "block-Gram moments")
    src.need(blocks == {f"{s}{t}": str(Q(1187, 108) if s == t else Q(53, 18))
                       for s, t in product(range(3), repeat=2)}, "block-Gram fourth traces")
    print("PASS_QQ16_BLOCK_GRAM_ORACLE moments=24,28,109/3,1823/36 blocks=9")


if __name__ == "__main__":
    main()
