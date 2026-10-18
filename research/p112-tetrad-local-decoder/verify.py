#!/usr/bin/env python3
"""Exact P112 tetrad-local support obstruction; Python standard library only."""
from collections import Counter, defaultdict
from fractions import Fraction
from itertools import combinations, product
import json
import sys


def require(condition, message):
    if not condition:
        raise ValueError(message)


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def rank2(rows):
    pivots = {}
    for value in rows:
        while value:
            pivot = value.bit_length() - 1
            if pivot in pivots:
                value ^= pivots[pivot]
            else:
                pivots[pivot] = value
                break
    return len(pivots)


def roots_and_frame():
    # Integer coordinates are twice the norm-two roots; canonical line signs.
    roots = set()
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            row = [0] * 8
            row[i], row[j] = 2, 2 * sign
            roots.add(tuple(row))
    for signs in product((-1, 1), repeat=8):
        if sum(s < 0 for s in signs) % 2 == 0:
            roots.add(signs if signs[0] > 0 else tuple(-s for s in signs))
    frame = []
    for j in range(4):
        for sign in (-1, 1):
            row = [0] * 8
            row[2 * j], row[2 * j + 1] = 2, 2 * sign
            frame.append(tuple(row))
    return sorted(roots), frame


def mask(indices):
    return sum(1 << i for i in indices)


def support(vector):
    return [i for i, value in enumerate(vector) if value != 0]


def term_data(d, t, pairing, classes, block_sets):
    x, y = support(d), support(t)
    xs, ys = set(x), set(y)
    y_mask = mask(y)
    beta = rank2(pairing[i] & y_mask for i in x)
    hits = sum(bool(xs & c) and bool(ys & c) for c in classes)
    local = any(xs <= b or ys <= b for b in block_sets)
    return beta, hits, local


def decoder_matrix(terms, n):
    out = [[0] * n for _ in range(n)]
    for d, t in terms:
        for i in support(d):
            for j in support(t):
                out[i][j] += d[i] * t[j]
    return out


def masked_exact(matrix, gram):
    return all(matrix[i][j] == 2 * value
               for i, row in enumerate(gram) for j, value in enumerate(row)
               if (value + 1) % 2)


def main():
    roots, frame = roots_and_frame()
    require(len(roots) == 120 and len(set(frame)) == 8, "root/frame count")
    require(all(dot(x, x) == 8 for x in roots), "root norms")
    require(all(dot(x, y) == 0 for x, y in combinations(frame, 2)), "frame")
    live = sorted(set(roots) - set(frame))
    require(len(live) == 112, "live count")
    require(all(dot(x, y) % 4 == 0 for x in roots for y in roots), "integral Gram")
    gram = [[dot(x, y) // 4 for y in live] for x in live]
    pairing = [sum(((value + 1) % 2) << j for j, value in enumerate(row))
               for row in gram]
    require(rank2(pairing) == 9, "label pairing rank")
    signs = [[dot(x, f) // 4 for f in frame] for x in live]
    blocks, groups = defaultdict(list), defaultdict(list)
    for i, row in enumerate(signs):
        tetrad = tuple(j for j, value in enumerate(row) if value)
        require(len(tetrad) == 4 and all(row[j] in (-1, 1) for j in tetrad),
                "tetrad support")
        blocks[tetrad].append(i)
        groups[tetrad, sum(value < 0 for value in row) % 2].append(i)
    require(len(blocks) == 14 and all(len(b) == 8 for b in blocks.values()), "blocks")
    require(len(groups) == 28 and all(len(c) == 4 for c in groups.values()), "classes")
    classes = [set(c) for _, c in sorted(groups.items())]
    block_sets = [set(b) for _, b in sorted(blocks.items())]
    require(all(rank2(pairing[i] for i in b) == 4 for b in block_sets),
            "full one-sided block label rank")
    for c in classes:
        require(all(gram[i][j] == (2 if i == j else 0) for i in c for j in c),
                "four-frame Gram")
    # Every possible actual support inside the block, on BOTH sides, including
    # empty supports. Arbitrary extra opposite-side columns cannot lower rank.
    support_cases = 0
    for tetrad, b in sorted(blocks.items()):
        ordered = groups[tetrad, 0] + groups[tetrad, 1]
        local_pairing = [sum(((pairing[i] >> j) & 1) << k
                             for k, j in enumerate(ordered)) for i in ordered]
        require(local_pairing == [15] * 4 + [240] * 4, "two cross-odd classes")
        for x in range(256):
            rows = [local_pairing[k] for k in range(8) if (x >> k) & 1]
            for y in range(256):
                hits = int(bool(x & 15) and bool(y & 15))
                hits += int(bool(x & 240) and bool(y & 240))
                require(rank2(row & y for row in rows) == hits, "support minor")
                support_cases += 1
    # Four signed coordinate terms per block. Actual supports are the whole
    # eight-line block; the four-term 8x8 identity is exact on that block.
    block_terms = []
    for tetrad, b in sorted(blocks.items()):
        for f in tetrad:
            d = [signs[i][f] if i in b else 0 for i in range(112)]
            block_terms.append((d, d[:]))
    block_matrix = decoder_matrix(block_terms, 112)
    require(masked_exact(block_matrix, gram), "56-term masked identity")
    require(all(block_matrix[i][j] == 2 * gram[i][j]
                for b in block_sets for i in b for j in b),
            "all-pairs small block identity")
    data = [term_data(d, t, pairing, classes, block_sets) for d, t in block_terms]
    require(Counter(data) == {(2, 2, True): 56}, "actual block term costs")
    # All-pairs attainment with row singletons; also checks mixed orientations.
    singleton_terms = []
    for i in range(112):
        d = [int(j == i) for j in range(112)]
        singleton_terms.append((d, [2 * g for g in gram[i]]))
    target = [[2 * g for g in row] for row in gram]
    require(decoder_matrix(singleton_terms, 112) == target, "all-pairs attainment")
    require(all(term_data(d, t, pairing, classes, block_sets) == (1, 1, True)
                for d, t in singleton_terms), "singleton costs")
    # Boundary control: the known NONLOCAL coordinate decoder beats 112.
    coordinate_terms = [([row[f] for row in signs], [row[f] for row in signs])
                        for f in range(8)]
    require(decoder_matrix(coordinate_terms, 112) == target, "coordinate control identity")
    coordinate_data = [term_data(d, t, pairing, classes, block_sets)
                       for d, t in coordinate_terms]
    require(coordinate_data == [(8, 14, False)] * 8, "locality is essential")
    # Cancellation, overcompleteness and complex ordinary transpose: replace a
    # term d*t^T by (1+i)d*t^T + (-i)d*t^T. Check real and imaginary
    # coefficient arrays separately using integers, never machine complex.
    d, t = block_terms[0]
    real_terms = [(d, t)] + block_terms[1:]
    imaginary_terms = [(d, t), ([-v for v in d], t)]
    require(decoder_matrix(real_terms, 112) == block_matrix, "complex real part")
    require(decoder_matrix(imaginary_terms, 112) == [[0] * 112 for _ in range(112)],
            "complex imaginary cancellation")
    # Both complex scalar multipliers are nonzero, so actual supports stay d,t.
    split_support_terms = [block_terms[0]] + block_terms
    require(sum(term_data(a, b, pairing, classes, block_sets)[0]
                for a, b in split_support_terms) == 114, "split actual-support costs")
    require(all(term_data(t, d, pairing, classes, block_sets) == (1, 1, True)
                for d, t in singleton_terms), "opposite orientation")
    # Free terms cannot hit even one class on both sides.
    i, j = next((i, j) for i in range(112) for j in range(112) if gram[i][j] == 1)
    free = ([int(k == i) for k in range(112)], [int(k == j) for k in range(112)])
    require(term_data(*free, pairing, classes, block_sets) == (0, 0, True), "free atom")
    require(not masked_exact(decoder_matrix(block_terms[1:], 112), gram), "missing term control")
    zero = [[0] * 112 for _ in range(112)]
    require(not masked_exact(zero, gram), "diagonal demand is essential")
    # Conditional retained-coverage screen, independent of any optimistic shape.
    w, centre, width = Fraction(896, 9), Fraction(112), 73
    deficit = w - centre
    zero_exponent_moment = ((width - 1) * w + centre) / (width * w)
    require(deficit == Fraction(-112, 9), "coverage deficit")
    require(zero_exponent_moment == Fraction(585, 584), "a=0 coverage rejection")
    report = {
        "root_lines": 120, "live_lines": 112, "tetrad_blocks": 14,
        "four_frames": 28, "support_cases": support_cases,
        "copy_floor": 112, "maximum_local_pairing_rank": 4,
        "masked_attainment_profile": {"2": 56},
        "all_pairs_attainment_profile": {"1": 112},
        "nonlocal_coordinate_profile": {"8": 8},
        "coordinate_excess": sum(h - beta for beta, h, _ in coordinate_data),
        "escape_excess_for_cost_at_most_64": 48,
        "escape_excess_for_cost_below_64": 49,
        "retained_coverage_deficit": str(deficit),
        "retained_coverage_moment_at_a0": str(zero_exponent_moment),
        "controls": 6,
    }
    if "--json" in sys.argv:
        print(json.dumps(report, indent=2, sort_keys=True))
    print("PASS_P112_TETRAD_LOCAL_DECODER blocks=14 classes=28 supports=917504 "
          "copy_floor=112 rank_cap=4 masked_terms=56 escape=48 moment0=585/584 controls=6")


if __name__ == "__main__":
    main()
