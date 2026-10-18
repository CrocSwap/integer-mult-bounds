#!/usr/bin/env python3
"""Independent finite checks for MATH.md; no predecessor engine imports."""
import sys
if not __debug__:
    raise SystemExit("Run this mathematical checker without -O; its assertions are proof-relevant.")

from collections import Counter
from itertools import combinations, product
from math import comb
import json


def rows(n, s, t):
    q = 1 << (n - 1)
    budget = comb(s, 2) + comb(t, 2) - (q - 1)
    need = (s * t - q + 1) // 2
    if budget < 0 or s * t < q:
        return []
    return [(a, b) for a in range(budget + 1)
            for b in range(budget + 1 - a) if budget + a * b >= need]


def points(word):
    q, out = 0, {0}
    for j in word:
        q ^= 1 << j
        out.add(q)
    return out


def normalize(word):
    lab = {}
    return tuple(lab.setdefault(j, len(lab)) for j in word)


def stats(P, functional):
    E = {v for v in P if functional(v) == 0}
    O = P - E
    A = Counter(a ^ b for a, b in combinations(E, 2))
    B = Counter(a ^ b for a, b in combinations(O, 2))
    r = Counter(a ^ b for a in E for b in O)
    a = comb(len(E), 2) - len(A)
    b = comb(len(O), 2) - len(B)
    c = len(E) * len(O) - len(r)
    shared = set(A) & set(B)
    ab = sum(A[x] * B[x] for x in shared)
    assert sum(comb(v, 2) for v in r.values()) == 2 * ab
    assert ab <= len(shared) + a + b + a * b
    return (len(E), len(O)), a, b, c, A, B, r


def main():
    table = {}
    for length in (18, 20):
        splits = [(s, t) for s in range(1, length // 2 + 1)
                  for t in range(1, length // 2 + 1) if rows(7, s, t)]
        table[str(length)] = splits
    assert table['18'] == [(9, 9)]
    assert table['20'] == [(7, 10), (8, 10), (9, 9), (9, 10),
                           (10, 7), (10, 8), (10, 9), (10, 10)]
    checks = {}
    for n, length in ((3, 6), (3, 8), (4, 8)):
        restored = universal = 0
        histogram = Counter()
        canonical_universal = set()
        for word in product(range(n), repeat=length):
            cnt = Counter(word)
            if len(cnt) != n or any(v % 2 for v in cnt.values()):
                continue
            restored += 1
            P = points(word)
            if len({a ^ b for a in P for b in P}) != 1 << n:
                continue
            universal += 1
            st, a, b, c, A, B, r = stats(P, lambda v: v.bit_count() % 2)
            s, t = st
            assert s <= length // 2 and t <= length // 2
            assert len(set(A) | set(B)) == (1 << (n - 1)) - 1
            assert a + b <= comb(s, 2) + comb(t, 2) - ((1 << (n - 1)) - 1)
            assert c == s * t - (1 << (n - 1))
            assert len(r) == 1 << (n - 1)
            histogram[st] += 1
            rotated = word[1:] + word[:1]
            rt = stats(points(rotated), lambda v: v.bit_count() % 2)[0]
            assert rt == (t, s)
            if normalize(word) == word:
                canonical_universal.add(word)
            # The same algebra is valid for every nonzero linear functional.
            for mask in range(1, 1 << n):
                split2, a2, b2, c2, _, _, _ = stats(
                    P, lambda v, mask=mask: (v & mask).bit_count() % 2)
                s2, t2 = split2
                assert a2 + b2 <= comb(s2, 2) + comb(t2, 2) - ((1 << (n - 1)) - 1)
                assert c2 == s2 * t2 - (1 << (n - 1))
        rotated_canon = {normalize(w[1:] + w[:1]) for w in canonical_universal}
        assert rotated_canon == canonical_universal
        checks[f'n{n}_L{length}'] = dict(
            restored=restored, universal=universal,
            canonical_universal=len(canonical_universal),
            split_histogram={f'{s},{t}': v for (s, t), v in sorted(histogram.items())})
    tight = {}
    for s, t in ((9, 9), (10, 7)):
        q = 64
        budget = comb(s, 2) + comb(t, 2) - 63
        need = (s * t - q + 1) // 2
        assert budget == need
        # A one-unit stronger need still leaves arithmetic rows.
        surviving_stronger = [(a, b) for a in range(budget + 1)
                              for b in range(budget + 1 - a)
                              if budget + a * b >= need + 1]
        assert (1, 1) in surviving_stronger
        tight[f'{s},{t}'] = dict(budget=budget, need=need,
                               max_upper=budget + budget * budget // 4,
                               rows_after_need_plus_one=len(surviving_stronger))
    witness = tuple(map(int, '01021323'))
    P = points(witness)
    assert len(P) == 8
    assert len({a ^ b for a in P for b in P}) == 16
    weight, a, b, *_ = stats(P, lambda v: v.bit_count() % 2)
    bit0, a0, b0, *_ = stats(P, lambda v: v & 1)
    assert weight == (4, 4) and bit0 == (6, 2)
    assert a + b <= 5 and a0 + b0 == 8
    print(json.dumps(dict(admissible_splits=table, small_word_checks=checks,
                          tight_claim_countercheck=tight,
                          simple_n4_counterexample=dict(word='01021323',
                              weight_split=weight, weight_excess=a+b,
                              bit0_split=bit0, bit0_excess=a0+b0,
                              balanced_budget=5,
                              actual_bit0_budget=comb(6, 2)+comb(2, 2)-7)), indent=2))
    print('PASS_INDEPENDENT_MATH')


if __name__ == '__main__':
    main()
