#!/usr/bin/env python3
"""Exact finite-domain CK frame analysis. @thakrarsagar / OpenAI Codex, Apache-2.0."""
import gzip
import hashlib
import itertools
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path

if not __debug__:
    raise RuntimeError('Run without -O; this certificate requires assertions.')

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / 'research/community-k492-audit/pr622/replay/ck-local/CANONICAL-WORD.json.gz'
SOURCE_SHA256 = 'ae3018c0646be06f47d345bb8baf0e6ea9220096a949fa30a8f7656aa4ad6f45'


def span(vectors):
    result = {0}
    for vector in vectors:
        result |= {x ^ vector for x in result}
    return frozenset(result)


def rank(frame):
    n = len(frame)
    assert n > 0 and n & (n - 1) == 0
    return n.bit_length() - 1


def operands(gate):
    assert gate[0] in ('add', 'scale')
    return gate[1:3] if gate[0] == 'add' else gate[1:2]


def interval(lower, upper):
    """Enumerate the entire subspace interval, including uncatalogued frames."""
    assert lower <= upper
    found = {lower}
    todo = [lower]
    while todo:
        frame = todo.pop()
        for vector in sorted(upper - frame):
            enlarged = frame | frozenset(x ^ vector for x in frame)
            if enlarged not in found:
                found.add(enlarged)
                todo.append(enlarged)
    return sorted(found, key=lambda x: (rank(x), tuple(sorted(x))))


def histogram(ranks):
    counts = Counter(r for r in ranks if r)
    assert all(0 < r <= 9 for r in counts)
    return tuple(counts[r] for r in range(10))


ZERO = (0,) * 10


def plus(left, right):
    return tuple(a + b for a, b in zip(left, right))


def dominates(left, right):
    """Sufficient exact order for every concave power r**p, 0 < p < 1."""
    if sum(r * n for r, n in enumerate(left)) != sum(r * n for r, n in enumerate(right)):
        return False
    return all(sum(min(r, k) * (a - b) for r, (a, b) in enumerate(zip(left, right))) <= 0
               for k in range(1, 10))


def problem(word):
    frames = list(map(span, word['frames']))
    gates = word['B']
    start = [frames[f] for f in word['start']]
    for gate in word['A']:
        for register in operands(gate):
            assert start[register] <= frames[gate[-1]]
            start[register] = frames[gate[-1]]
    end = start.copy()
    last = {}
    for i, gate in enumerate(gates):
        for register in operands(gate):
            assert end[register] <= frames[gate[-1]]
            end[register] = frames[gate[-1]]
            last[register] = i
    pinned = set(last.values())
    current = start.copy()
    lower = []
    for i, gate in enumerate(gates):
        frame = frames[gate[-1]] if i in pinned else span(
            x for register in operands(gate) for x in current[register])
        lower.append(frame)
        for register in operands(gate):
            assert current[register] <= frame
            current[register] = frame
    current = end.copy()
    upper = [None] * len(gates)
    for i in reversed(range(len(gates))):
        gate = gates[i]
        frame = frames[gate[-1]] if i in pinned else frozenset.intersection(
            *(current[register] for register in operands(gate)))
        upper[i] = frame
        for register in operands(gate):
            assert frame <= current[register]
            current[register] = frame
    domains = {}
    for i, (lo, hi) in enumerate(zip(lower, upper)):
        assert lo <= frames[gates[i][-1]] <= hi
        if lo != hi:
            domains[i] = interval(lo, hi)
    # A factor charges one register transition, with exact inclusion enforced.
    factors = []
    previous = [None] * len(start)
    for i, gate in enumerate(gates):
        for register in operands(gate):
            j = previous[register]
            keys = tuple(x for x in (j, i) if x in domains)
            table = {}
            for values in itertools.product(*(range(len(domains[x])) for x in keys)):
                assignment = dict(zip(keys, values))
                before = domains[j][assignment[j]] if j in domains else (
                    frames[gates[j][-1]] if j is not None else start[register])
                after = domains[i][assignment[i]] if i in domains else frames[gate[-1]]
                if before <= after:
                    table[values] = histogram([rank(after) - rank(before)])
            assert table
            factors.append((keys, table))
            previous[register] = i
    return frames, start, end, pinned, domains, factors


def pareto(histograms):
    """Keep every profile not excluded by exact concave dominance."""
    kept = []
    for candidate in sorted(set(histograms)):
        if any(dominates(old, candidate) for old in kept):
            continue
        kept = [old for old in kept if not dominates(candidate, old)]
        kept.append(candidate)
    return tuple(kept)


def combine(left, right):
    return pareto(plus(a, b) for a in left for b in right)


def eliminate(domains, initial_factors):
    """Exact min-fill elimination retaining all incomparable paid profiles."""
    factors = [(keys, {values: (profile,) for values, profile in table.items()})
               for keys, table in initial_factors]
    remaining = set(domains)
    evaluated = width = max_frontier = 0
    conditional_profiles = 0
    while remaining:
        graph = {x: set() for x in remaining}
        for keys, table in factors:
            for x in keys:
                graph[x].update(set(keys) - {x})
        def priority(x):
            neighbors = graph[x]
            missing = sum(b not in graph[a] for a in neighbors for b in neighbors if a < b)
            return missing, len(neighbors), x
        selected = min(remaining, key=priority)
        bucket = [(keys, table) for keys, table in factors if selected in keys]
        factors = [(keys, table) for keys, table in factors if selected not in keys]
        separator = tuple(sorted(set().union(*(set(keys) for keys, table in bucket)) - {selected}))
        width = max(width, len(separator))
        reduced = {}
        for values in itertools.product(*(range(len(domains[x])) for x in separator)):
            assignment = dict(zip(separator, values))
            candidates = []
            for value in range(len(domains[selected])):
                evaluated += 1
                assignment[selected] = value
                total = (ZERO,)
                for keys, table in bucket:
                    contribution = table.get(tuple(assignment[x] for x in keys))
                    if contribution is None:
                        break
                    total = combine(total, contribution)
                else:
                    candidates.extend(total)
            if not candidates:
                continue
            # Eliminated register ranks telescope; separators fix the mass.
            assert len({sum(r * n for r, n in enumerate(h)) for h in candidates}) == 1
            frontier = pareto(candidates)
            max_frontier = max(max_frontier, len(frontier))
            conditional_profiles += len(frontier)
            reduced[values] = frontier
        assert reduced
        factors.append((separator, reduced))
        remaining.remove(selected)
    result = (ZERO,)
    for keys, table in factors:
        assert keys == () and set(table) == {()}
        result = combine(result, table[()])
    return result, dict(evaluated=evaluated, induced_width=width,
                        max_conditional_frontier=max_frontier,
                        conditional_profiles=conditional_profiles)


def recount(word, frames, start, end, assigned):
    current = start.copy()
    increments = []
    for i, gate in enumerate(word['B']):
        frame = assigned.get(i, frames[gate[-1]])
        for register in operands(gate):
            assert current[register] <= frame
            increments.append(rank(frame) - rank(current[register]))
            current[register] = frame
    assert current == end
    return histogram(increments)


def outside_profile(word, frames, end):
    current = [frames[f] for f in word['start']]
    increments = []
    def climb(register, frame):
        assert current[register] <= frame
        increments.append(rank(frame) - rank(current[register]))
        current[register] = frame
    for gate in word['A']:
        for register in operands(gate):
            climb(register, frames[gate[-1]])
    for register, frame_id in zip(word['centers'], word['center_frames']):
        previous = frames[frame_id]
        assert current[register] == previous
        served = {word['target_levels'].get(str(gate[1] - word['v']), 0)
                  for gate in word['cut'] if gate[2] == register}
        for frame_id in sorted(served, key=lambda f: -rank(frames[f])):
            frame = frames[frame_id]
            assert frame <= previous
            increments.append(rank(previous) - rank(frame))
            previous = frame
    current = end.copy()
    for gate in word['tail']:
        for register in operands(gate):
            climb(register, frames[gate[-1]])
    for register, frame_id in enumerate(word['final']):
        climb(register, frames[frame_id])
    return histogram(increments)


def log_bounds(value):
    """Eight terms of log(x)=2*atanh((x-1)/(x+1)), with geometric tail."""
    z = Fraction(value - 1, value + 1)
    lower = 2 * sum((z ** (2 * k + 1) / (2 * k + 1) for k in range(8)), Fraction(0))
    upper = lower + 2 * z ** 17 / (17 * (1 - z * z))
    return lower, upper


def power_certificate(baseline, frontier):
    """Certify every retained alternative is worse for all 0 < p < 1."""
    for value, lower, upper in [(2, Fraction(69, 100), Fraction(7, 10)),
                                (3, Fraction(109, 100), Fraction(11, 10))]:
        lo, hi = log_bounds(value)
        assert lower < lo < hi < upper
    bounds = []
    assert baseline in frontier
    for alternative in frontier:
        delta = tuple(a - b for a, b in zip(alternative, baseline))
        if not any(delta):
            continue
        assert delta[0] == 0 and not any(delta[5:])
        a, b, c, d = delta[1:5]
        assert b <= 0 and d >= 0 and a + 2*b + 3*c + 4*d == 0
        # D'(1)=(2b+8d)log(2)+3c*log(3); README proves why its sign suffices.
        x, y = 2*b + 8*d, 3*c
        upper = x * (Fraction(7, 10) if x > 0 else Fraction(69, 100))
        upper += y * (Fraction(11, 10) if y > 0 else Fraction(109, 100))
        assert upper < 0
        bounds.append(upper)
    return dict(strict_alternatives=len(bounds),
                largest_derivative_upper=str(max(bounds)),
                exponent_interval='0 < p < 1', baseline_power_optimal=True)


def analyze(word):
    frames, start, end, pinned, domains, factors = problem(word)
    frontier, stats = eliminate(domains, factors)
    baseline = recount(word, frames, start, end, {})
    outside = outside_profile(word, frames, end)
    full = tuple(int(word['local_profile'].get(str(r), 0)) for r in range(10))
    assert plus(baseline, outside) == full
    return dict(gates=len(word['B']), registers=len(start), pinned_gates=len(pinned),
                flexible_gates=len(domains), domain_sizes=dict(sorted(Counter(map(len, domains.values())).items())),
                baseline_histogram=baseline, final_frontier=frontier,
                fixed_outside_histogram=outside, complete_local_histogram=full,
                power_certificate=power_certificate(baseline, frontier),
                **stats)


if __name__ == '__main__':
    pins = json.loads((HERE / 'SOURCES.json').read_text())
    for path, expected_hash in pins['files'].items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected_hash, path
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == SOURCE_SHA256, 'source pin mismatch'
    word = json.loads(gzip.decompress(SOURCE.read_bytes()))
    result = analyze(word)
    result['source_sha256'] = SOURCE_SHA256
    expected = json.loads((HERE / 'CERTIFICATE.json').read_text())
    assert json.loads(json.dumps(result)) == expected, 'certificate mismatch'
    print('PASS_CK_FIXED_END_B_FRAME_BOUND gates=1930 flexible=474 profiles=119 exponent=0<p<1')
