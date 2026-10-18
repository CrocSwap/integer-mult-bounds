#!/usr/bin/env python3
"""Small exhaustive cross-checks. @thakrarsagar / OpenAI Codex, Apache-2.0."""
import gzip
import itertools
import json
import runpy
from fractions import Fraction
from functools import lru_cache

import verify as v

@lru_cache(None)
def linear_rank(vectors):
    """Independent Gaussian elimination, rather than log2 of a span's size."""
    pivots = {}
    for x in vectors:
        while x:
            bit = x.bit_length() - 1
            if bit not in pivots:
                pivots[bit] = x
                break
            x ^= pivots[bit]
    return len(pivots)


def inside(before, after):
    return linear_rank(tuple(sorted(before | after))) == linear_rank(tuple(sorted(after)))


def score(profile):
    jumps = [r for r, count in enumerate(profile) for _ in range(count)]
    return sum(jumps), tuple(sum(min(r, k) for r in jumps) for k in range(1, 10))


def reference_frontier(profiles):
    profiles = set(profiles)
    scores = {p: score(p) for p in profiles}
    return {p for p in profiles if not any(
        q != p and scores[q][0] == scores[p][0]
        and all(a <= b for a, b in zip(scores[q][1], scores[p][1]))
        for q in profiles)}


def factor_profile(factors, assignment):
    result = [0] * 10
    for keys, table in factors:
        contribution = table.get(tuple(assignment[x] for x in keys))
        if contribution is None:
            return None
        for r, count in enumerate(contribution):
            result[r] += count
    return tuple(result)


def direct_profile(word, domains, assignment, expected_end):
    frames = [frozenset(basis) for basis in word['frames']]
    current = [frames[f] for f in word['start']]
    for gate in word['A']:
        for register in gate[1:3] if gate[0] == 'add' else gate[1:2]:
            current[register] = frames[gate[-1]]
    result = [0] * 10
    for i, gate in enumerate(word['B']):
        frame = domains[i][assignment[i]] if i in domains else frames[gate[-1]]
        for register in gate[1:3] if gate[0] == 'add' else gate[1:2]:
            before = current[register]
            if not inside(before, frame):
                return None
            jump = linear_rank(tuple(sorted(frame))) - linear_rank(tuple(sorted(before)))
            if jump:
                result[jump] += 1
            current[register] = frame
    if not all(inside(a, b) and inside(b, a) for a, b in zip(current, expected_end)):
        return None
    return tuple(result)


def exhaustive(domains, factors, word=None, end=None):
    keys = sorted(domains)
    profiles = set()
    checked = 0
    for values in itertools.product(*(range(len(domains[x])) for x in keys)):
        assignment = dict(zip(keys, values))
        profile = factor_profile(factors, assignment)
        if word is not None:
            assert profile == direct_profile(word, domains, assignment, end)
        if profile is not None:
            profiles.add(profile)
        checked += 1
    actual, _ = v.eliminate(domains, factors)
    assert set(actual) == reference_frontier(profiles)
    return checked, set(actual)


def components(domains, factors):
    neighbors = {x: set() for x in domains}
    for keys, _ in factors:
        for x in keys:
            neighbors[x].update(set(keys) - {x})
    remaining = set(domains)
    result = []
    while remaining:
        component = {remaining.pop()}
        pending = list(component)
        while pending:
            adjacent = neighbors[pending.pop()] & remaining
            remaining -= adjacent
            component |= adjacent
            pending.extend(adjacent)
        result.append(component)
    return result


def main():
    runpy.run_path(str(v.HERE / 'verify.py'), run_name='__main__')
    word = json.loads(gzip.decompress(v.SOURCE.read_bytes()))
    frames, start, end, pinned, domains, factors = v.problem(word)
    assert len(pinned) == 492 and len(domains) == 474
    for frame in frames:
        assert v.rank(frame) == linear_rank(tuple(sorted(frame)))
    baseline_assignment = {i: domains[i].index(frames[word['B'][i][-1]]) for i in domains}
    baseline = direct_profile(word, domains, baseline_assignment, end)
    assert baseline == factor_profile(factors, baseline_assignment)
    assert baseline == (0, 1236, 496, 200, 96, 0, 0, 0, 0, 0)

    groups = components(domains, factors)
    small = [group for group in groups if len(group) <= 3]
    assert len(groups) == 120 and len(small) == 100
    checked = 0
    for group in small:
        local_factors = [(keys, table) for keys, table in factors if set(keys) & group]
        assert all(set(keys) <= group for keys, _ in local_factors)
        count, _ = exhaustive({x: domains[x] for x in group}, local_factors)
        checked += count

    # Three flexible gates form a triangle, so this exercises coupled elimination.
    toy = dict(frames=[[], [1], [2], [1, 2]], start=[0, 0, 0], A=[], B=[
        ['add', 0, 1, 1, 1, 1], ['add', 1, 2, 1, 1, 1],
        ['add', 0, 2, 1, 1, 3], ['add', 0, 1, 1, 1, 3],
        ['add', 1, 2, 1, 1, 3]])
    tf, ts, te, _, td, factors = v.problem(toy)
    count, frontier = exhaustive(td, factors, toy, te)
    assert count == 125 and frontier == {(0, 0, 3, 0, 0, 0, 0, 0, 0, 0)}
    original = v.recount(toy, tf, ts, te, {})
    assert original == (0, 6, 0, 0, 0, 0, 0, 0, 0, 0)
    assert not any(v.dominates(original, p) for p in frontier)

    # Equal ranks cannot substitute for actual subspace containment.
    bad = {i: td[i].index(tf[3]) for i in td}
    bad[0] = td[0].index(tf[1])
    bad[1] = td[1].index(tf[2])
    assert factor_profile(factors, bad) is None
    assert direct_profile(toy, td, bad, te) is None
    assert linear_rank((1,)) == linear_rank((2,)) and not inside(frozenset({1}), frozenset({2}))

    # Independent integral bounds, rather than verify.py's atanh series.
    for x, lo, hi in [(2, Fraction(69, 100), Fraction(7, 10)),
                      (3, Fraction(109, 100), Fraction(11, 10))]:
        right = sum((Fraction(x - 1, 1000 + k * (x - 1)) for k in range(1, 1001)), Fraction(0))
        left = right + Fraction(x - 1, 1000) * (1 - Fraction(1, x))
        assert lo < right < left < hi
    receipt = json.loads((v.HERE / 'CERTIFICATE.json').read_text())
    strict_bounds = []
    for profile in receipt['final_frontier']:
        delta = [a - b for a, b in zip(profile, receipt['baseline_histogram'])]
        if not any(delta):
            continue
        assert delta[0] == 0 and not any(delta[5:])
        a, b, c, d = delta[1:5]
        assert b <= 0 <= d and a + 2*b + 3*c + 4*d == 0
        coefficients = (2*b + 8*d, 3*c)
        intervals = ((Fraction(69, 100), Fraction(7, 10)),
                     (Fraction(109, 100), Fraction(11, 10)))
        upper = sum(max(coefficient * endpoint for endpoint in interval)
                    for coefficient, interval in zip(coefficients, intervals))
        assert upper < 0
        strict_bounds.append(upper)
    assert len(strict_bounds) == 118 and max(strict_bounds) == Fraction(-21, 25)
    print(json.dumps(dict(status='PASS_EXHAUSTIVE_CROSS_CHECKS',
        actual_components=len(small), actual_assignments=checked,
        coupled_synthetic_assignments=count, negative_controls=2,
        strict_power_alternatives=len(strict_bounds)), sort_keys=True))


if __name__ == '__main__':
    main()
