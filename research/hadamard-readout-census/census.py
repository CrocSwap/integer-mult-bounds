"""Exact finite census; no floating point and no predecessor executable code."""

import argparse
from collections import Counter
from itertools import combinations_with_replacement, product
import json
from pathlib import Path

H = ((1, 1, 1, 1), (1, -1, 1, -1),
     (1, 1, -1, -1), (1, -1, -1, 1))
TARGETS = tuple((1,) + t for t in product((-1, 1), repeat=3))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def paths(prefix=(), counts=(0, 0, 0, 0)):
    """Every permutation of the multiset 00112233 exactly once."""
    if len(prefix) == 8:
        yield prefix
    else:
        for j in range(4):
            if counts[j] < 2:
                c = list(counts)
                c[j] += 1
                yield from paths(prefix + (j,), tuple(c))


def states(path):
    q = [0] * 4
    out = [tuple(q)]
    for j in path:
        q[j] = 1 - q[j]
        out.append(tuple(q))
    return tuple(out)


def readouts(qs):
    """Solve min ||a||_1 subject to sum a=0, sum a*q=target.

    At most four positive and four negative taps suffice, since each of the
    four unit coordinate differences occurs on the path. Exhaust all smaller
    equal-cardinality multisets. Repetition includes every integer coefficient.
    """
    vertices = tuple(dict.fromkeys(qs))
    unresolved = set(TARGETS)
    answer = {}
    for k in range(1, 5):
        sums = {}
        for ids in combinations_with_replacement(range(len(vertices)), k):
            total = tuple(sum(vertices[i][j] for i in ids) for j in range(4))
            sums.setdefault(total, ids)
        for target in sorted(unresolved):
            for total, pos in sums.items():
                neg = sums.get(tuple(total[j] - target[j] for j in range(4)))
                if neg is not None:
                    answer[target] = (2 * k, tuple(vertices[i] for i in pos),
                                      tuple(vertices[i] for i in neg))
                    break
        unresolved -= answer.keys()
        if not unresolved:
            break
    require(not unresolved, 'unit-edge upper bound failed')
    return answer


def profile_for(minima, signs):
    profile, reps = [], []
    for row in H:
        target = tuple(row[j] * signs[j] for j in range(4))
        orient = target[0]
        canonical = tuple(orient * x for x in target)
        n, positive, negative = minima[canonical]
        if orient < 0:
            positive, negative = negative, positive
        profile.append(n)
        reps.append((positive, negative))
    return tuple(profile), tuple(reps)


def emit(path, signs, reps):
    qs = states(path)
    taps = [[] for _ in qs]
    for i, (positive, negative) in enumerate(reps):
        for sign, vertices in ((1, positive), (-1, negative)):
            for v in vertices:
                taps[qs.index(v)].append(['A', i, sign])
    word = []
    for t, v in enumerate(qs):
        word.extend(taps[t])
        if t < 8:
            j = path[t]
            word.append(['B', j, signs[j] * (1 if v[j] == 0 else -1)])
    return word


def dominates(a, b):
    return a != b and all(x <= y for x, y in zip(a, b))


def balanced_calls(n):
    require(isinstance(n, int) and n >= 1, 'positive factor length required')
    if n == 1:
        return 1
    return 2 * balanced_calls(n // 2) + 2 * balanced_calls(n - n // 2)


def run():
    histogram = Counter()
    examples = {}
    count = 0
    for path in paths():
        count += 1
        minima = readouts(states(path))
        for signs in product((-1, 1), repeat=4):
            profile, reps = profile_for(minima, signs)
            histogram[profile] += 1
            examples.setdefault(profile, (path, signs, reps))
    frontier = sorted(p for p in histogram
                      if not any(dominates(q, p) for q in histogram))
    prices = tuple(balanced_calls(n) for n in (2, 3, 4, 5))
    bprices = tuple(balanced_calls(n) for n in (1, 2, 3, 4))
    chosen = min(frontier, key=lambda p: (sum(x * y for x, y in zip(p, prices)), p))
    path, signs, reps = examples[chosen]
    return {
        'format': 'hadamard-readout-census/1',
        'base_commit': 'ce7ad1b6ab09452c3478723a2e96ed5ff212dc08',
        'assignment_seed': 55,
        'unsigned_paths': count,
        'signed_paths': sum(histogram.values()),
        'profile_histogram': [{'profile': list(p), 'paths': histogram[p]}
                              for p in sorted(histogram)],
        'pareto_profiles': [list(p) for p in frontier],
        'minimum_queries': 8 + min(map(sum, histogram)),
        'A_lengths': [2, 3, 4, 5], 'B_lengths': [1, 2, 3, 4],
        'A_leaf_prices': list(prices), 'B_leaf_prices': list(bprices),
        'chosen_profile': list(chosen),
        'minimum_leaf_calls': 2 * sum(bprices) + sum(x * y for x, y in zip(chosen, prices)),
        'source_path': list(path), 'first_signs': list(signs),
        'word': emit(path, signs, reps),
        'frontier_words': [{'profile': list(p), 'word': emit(*examples[p])} for p in frontier],
        'scope': 'Exactly eight source calls, one positive and one negative per source; arbitrary repeated signed readouts at visited states; exact additive children, one dirty connector, no new kappa',
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = run()
    payload = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if args.output:
        with args.output.open('x', encoding='utf-8', newline='\n') as f:
            f.write(payload)
    print(json.dumps({k: result[k] for k in ('unsigned_paths', 'signed_paths',
          'pareto_profiles', 'minimum_queries', 'minimum_leaf_calls')}))


if __name__ == '__main__':
    main()
