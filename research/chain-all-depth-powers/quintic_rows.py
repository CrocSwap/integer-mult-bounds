"""Two exact counters for the small roots in the depth-five shift.
SHIN09-git with OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from itertools import combinations_with_replacement, product
from math import comb, factorial, prod

from census import check
from law import root_target
from oracle import balanced_words, literal_matrix

# Excluding the known singletons and the target leaves nine interval entries.
PROPER = [(j, i-1, j-i+1) for j in range(2, 6) for i in range(1, j)
          if (i, j) != (1, 5)]


def halves(length, n):
    for word in product(range(1, 6), repeat=length):
        counts = tuple(word.count(i) for i in range(1, 6))
        if max(counts) <= n:
            yield word, counts


def signature(word, n, inverse):
    matrix = literal_matrix(word, 5)
    sign = -1 if inverse else 1
    proper = tuple((sign**span * matrix[j][k]) % n for j, k, span in PROPER)
    return proper, sign*matrix[5][0] % n


def split_row(n, cut):
    """Join a literal prefix P with inverse suffix S^-1 using S P = I+cE."""
    prefix, mass = {}, Counter()
    left = right = compatible = 0
    row = [0]*n
    for word, counts in halves(cut, n):
        proper, top = signature(word, n, False)
        bucket = prefix.setdefault((counts, proper), [0]*n)
        bucket[top] += 1
        mass[counts] += 1
        left += 1
    for reversed_suffix, counts in halves(5*n-cut, n):
        complement = tuple(n-c for c in counts)
        # Negating every shear multiplies an interval by (-1)^length.
        proper, inverse_top = signature(reversed_suffix, n, True)
        for t, ways in enumerate(prefix.get((complement, proper), ())):
            row[(t-inverse_top) % n] += ways
        compatible += mass.get(complement, 0)
        right += 1
    check(compatible == factorial(5*n)//factorial(n)**5, "split multinomial mass")
    return dict(row=row, cut=cut, prefix_words=left, reverse_suffix_words=right,
                prefix_keys=len(prefix), compatible_pairs=compatible)


def placements(n):
    result = []
    for gaps in combinations_with_replacement(range(3*n+1), n):
        counts = tuple(gaps.count(i) for i in range(3*n+1))
        before = tuple(sum(g <= i for g in gaps) for i in range(3*n))
        result.append((counts, before, tuple(n-x for x in before)))
    return result


def middle_features(word):
    first, second, third = [[i for i, x in enumerate(word) if x == label] for label in (1, 2, 3)]
    ab = [(i, j) for i in first for j in second if i < j]
    bc = [(j, k) for j in second for k in third if j < k]
    triples = [(i, k) for i, j in ab for k in third if j < k]
    return first, third, ab, bc, triples


def gap_row(n):
    options = placements(n)
    weights = [[prod(comb(x+y, x) for x, y in zip(a[0], b[0])) for b in options]
               for a in options]
    mass_per_middle = sum(map(sum, weights))
    row = [0]*n
    total = restored = accepted = 0
    for middle in balanced_words(3, n):
        total += 1
        first, third, ab, bc, triples = middle_features(middle)
        if any(len(f) % n for f in (ab, bc, triples)):
            continue
        restored += 1
        starts = (first, [i for i, j in ab], [i for i, k in triples])
        ends = (third, [k for j, k in bc], [k for i, k in triples])
        left = [(u, b) for u, (_, b, _) in enumerate(options)
                if all(sum(b[i] for i in indices) % n == 0 for indices in starts)]
        right = [(v, a) for v, (_, _, a) in enumerate(options)
                 if all(sum(a[k] for k in indices) % n == 0 for indices in ends)]
        for u, b in left:
            for v, a in right:
                residue = sum(b[i]*a[k] for i, k in triples) % n
                row[residue] += weights[u][v]
                accepted += 1
    mass = total*mass_per_middle
    check(mass == factorial(5*n)//factorial(n)**5, "gap multinomial mass")
    return dict(row=row, middle_words=total, restored_middle=restored,
                accepted_gap_pairs=accepted, all_words=mass)


def small_quintic_rows():
    result = {}
    for n in (2, 3):
        cut = 5*n//2
        split, gaps = split_row(n, cut), gap_row(n)
        check(split["row"] == gaps["row"], "split and gap W5 rows differ")
        result[str(n)] = dict(split=split, gaps=gaps)
    check(result["2"]["split"]["row"] == [25520, 0], "literal quintic binary row")
    nonprimitive = []
    for c in range(15):
        check(all(root_target(5, 15//d, d, c) is None for d in (3, 15)), "unexpected order at m=15")
        t = root_target(5, 3, 5, c)
        nonprimitive.append(0 if t is None else result["3"]["split"]["row"][t])
    check([i for i, v in enumerate(nonprimitive) if v] == [3], "m=15 periodic targets")
    check(nonprimitive[3] % 15 == 0, "m=15 period population")
    result["m15"] = dict(nonprimitive_words=nonprimitive, period_15_classes=nonprimitive[3]//15,
                         W_target_3_modulo_75=nonprimitive[3] % 75)
    return result
