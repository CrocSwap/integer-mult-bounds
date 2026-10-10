#!/usr/bin/env python3
"""Finite controls for the rank-minimal copied-center lower bound.

The proof for arbitrary characteristic-zero coefficients is in PROOF.md.
The coefficient sweep below is a finite adversarial control, not its proof.
"""
from __future__ import annotations

from itertools import combinations, product
from math import comb

from audit import binary_rank, need
from triangular_obstruction import inverse, matrix


def ports(p):
    labels = [tuple(2 * i + b for i, b in zip(coarse, bits))
              for coarse in combinations(range(p), 3)
              for bits in product((0, 1), repeat=3)]
    return labels, [sum(1 << j for j in label) for label in labels]


def support_rank(p, coefficients):
    labels, vectors = ports(p)
    return binary_rank(q for label, q in zip(labels, vectors)
                       if sum(coefficients[j] for j in label))


def sweep(p=5):
    labels, vectors = ports(p)
    threshold = 2 * p - 2
    checked = 0
    for coefficients in product((-1, 0, 1), repeat=2 * p):
        if not any(coefficients):
            continue
        pivots = {}
        for (a, b, c), q in zip(labels, vectors):
            if not coefficients[a] + coefficients[b] + coefficients[c]:
                continue
            while q:
                top = q.bit_length() - 1
                if top in pivots:
                    q ^= pivots[top]
                else:
                    pivots[top] = q
                    break
            if len(pivots) >= threshold:
                break
        need(len(pivots) >= threshold, "Finite source-support counterexample")
        checked += 1
    return {"p": p, "coefficient_alphabet": [-1, 0, 1], "nonzero_vectors_checked": checked,
            "certified_support_rank_floor": threshold,
            "scope": "Finite control only; the written lemma handles every characteristic-zero coefficient vector."}


def certificate():
    sharp = []
    for p in (5, 6, 11, 13, 16):
        h = 2 * p
        gram = matrix([[4 * comb(p - 1, 2) if i == j else 0 if i // 2 == j // 2
                        else 2 * (p - 2) for j in range(h)] for i in range(h)])
        inverse(gram)  # Exact full column rank of the port incidence matrix.
        center_rank = support_rank(p, [1] + [0] * (h - 1))
        omitted_pair = support_rank(p, [-2, -2] + [1] * (h - 2))
        need(center_rank == omitted_pair == h - 2, "Sharp center-support examples")
        sharp.append({"p": p, "h": h, "incidence_rank_Q": h,
                      "star_support_rank_F2": center_rank,
                      "omitted_pair_support_rank_F2": omitted_pair,
                      "rank_minimal_center_loss_floor": h * (h - 2)})
    small = support_rank(4, [-2, -2] + [1] * 6)
    need(small == 4 and small < 8 - 2, "The p>=5 domain is necessary")
    return {"status": "SHARP LOWER BOUND FOR RANK-MINIMAL COPIED CENTERS",
            "theorem": "For p>=5 and h=2p, every nonzero characteristic-zero linear combination of coordinate stars has binary source-support span at least h-2. Therefore any factorization of B=(AA^T-J)/2 through exactly h copied scalar centers has loss at least h(h-2).",
            "sharp_examples": sharp, "finite_sweep": sweep(),
            "excluded_domain_control": {"p": 4, "support_rank": small, "putative_floor": 6},
            "scope": "Exactly h linearly independent copied centers. Overcomplete factors, a different center mechanism, changed port families and global stage fusion remain outside this result."}


if __name__ == "__main__":
    import json
    print(json.dumps(certificate(), sort_keys=True, indent=2))
