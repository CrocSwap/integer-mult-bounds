"""Exact finite-domain optimization for the remaining coupled chart components."""

from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
from hashlib import sha256
from itertools import product
from math import prod
from pathlib import Path
import gzip
import json
import sys

PREVIOUS = Path(__file__).resolve().parents[2] / 'kappa-helper-boundary-20261110T0853Z' / 'evidence'
sys.path.append(str(PREVIOUS))
from screen import basis, load
from geometry import geometry, subspace_count

WORD = 'cfdfa3a83cb3714576517b66b56a174c0b83841aee90a828cdb0ae1dfe882970'
BRACKET = ('0.00363381505866791008145080644149513',
           '0.00363381505866791008145080644149514')
GRID = 10**45


def bits(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def chart(space):
    return sum(1 << v for v in space), len(space).bit_length() - 1


@lru_cache(None)
def domain(lo, hi):
    found = {lo}
    todo = [lo]
    for s in todo:
        for v in sorted(hi - s):
            t = s | {v ^ x for x in s}
            if t not in found:
                found.add(t)
                todo.append(t)
    d = len(hi).bit_length() - len(lo).bit_length()
    assert len(todo) == sum(subspace_count(d, k) for k in range(d+1))
    return sorted(map(chart, todo))


def top_two(values):
    first = second = None
    for value in values:
        if value is None or value == first or value == second:
            continue
        if first is None or value > first:
            first, second = value, first
        elif second is None or value > second:
            second = value
    return first, second


def elimination(factors, sizes):
    """Maximize additive factors, retaining the top two distinct totals."""
    pending = set(sizes)
    history = []
    work = peak = 0
    while pending:
        scopes = {i: set().union(*(set(s) for s, _ in factors if i in s)) for i in pending}
        vertex = min(pending, key=lambda i: (prod(sizes[j] for j in scopes[i]), i))
        scope = sorted(scopes[vertex])
        assert vertex in scope
        context = tuple(j for j in scope if j != vertex)
        grouped = [(s, t) for s, t in factors if vertex in s]
        factors = [(s, t) for s, t in factors if vertex not in s]
        positions = [tuple((context + (vertex,)).index(j) for j in s) for s, _ in grouped]
        result, witness = {}, {}
        volume = prod(sizes[j] for j in scope)
        work += volume
        peak = max(peak, volume)
        for co in product(*(range(sizes[i]) for i in context)):
            best = second = None
            for v in range(sizes[vertex]):
                state = (*co, v)
                values = [t.get(tuple(state[k] for k in idx)) for (_, t), idx in zip(grouped, positions)]
                if any(value is None for value in values):
                    continue
                total = sum(value[0] for value in values)
                alternatives = [value[1] - value[0] for value in values if value[1] is not None]
                other = total + max(alternatives) if alternatives else None
                if best is None or total > best:
                    witness[co] = v
                best, second = top_two((best, second, total, other))
            if best is not None:
                result[co] = (best, second)
        assert result
        factors.append((context, result))
        history.append((vertex, context, witness))
        pending.remove(vertex)
    finals = [table[()] for scope, table in factors if not scope]
    assert len(finals) == len(factors)
    best = sum(first for first, _ in finals)
    gaps = [second - first for first, second in finals if second is not None]
    runner_up = best + max(gaps) if gaps else None
    assignment = {}
    for vertex, context, witness in reversed(history):
        assignment[vertex] = witness[tuple(assignment[i] for i in context)]
    return best, runner_up, assignment, {'max_table_volume': peak, 'searched_cells': work}


def solve(block, base, lo, hi, paid, target, intervals, graph, compare_winner=False):
    vertices = set(block)
    edges = sorted({(a, b) for a, b in paid.keys() | target.keys() if a in vertices or b in vertices})
    signed = {e: target[e]-paid[e] for e in edges}
    mass = sum(abs(c) for c in signed.values())
    if not mass:
        return dict(vertices=block, proof='pointwise target and paid cancellation', signed_edges=0)

    # Scores order midpoint sums first, and then uniquely encode distinct
    # signed rank profiles within each midpoint tie.
    radix = 2*mass+1
    stride = radix**9
    mid = {r: int(GRID * (a+b)/2) for r, (a, b) in intervals.items()}
    score = {r: v*stride + radix**(r-1) for r, v in mid.items()}
    score[0] = 0
    uncertainty = max(max(abs(Q(mid[r], GRID)-a), abs(Q(mid[r], GRID)-b))
                      for r, (a, b) in intervals.items())
    domains = {i: domain(lo[i], hi[i]) for i in vertices}
    all_states = {i: (base[i],) for a, b in edges for i in (a, b) if i not in vertices}
    all_states.update(domains)
    factors = []
    for a, b in edges:
        scope = tuple(sorted({a, b} & vertices))
        table = {}
        old_rank = base[b][1] - base[a][1]
        for j, (am, ad) in enumerate(all_states[a]):
            for k, (bm, bd) in enumerate(all_states[b]):
                if am & ~bm or (target[a, b] and am == bm):
                    continue
                key = tuple(j if i == a else k for i in scope)
                table[key] = (signed[a, b]*(score[bd-ad]-score[old_rank]), None)
        assert table
        factors.append((scope, table))
    best, second, assignment, stats = elimination(factors, {i: len(d) for i, d in domains.items()})
    assert best >= 0
    new = base.copy()
    for i, j in assignment.items():
        new[i] = domains[i][j]
    gain_profile = Counter()
    for a, b in edges:
        assert not new[a][0] & ~new[b][0] and (not target[a, b] or new[a] != new[b])
        old_rank = base[b][1]-base[a][1]
        new_rank = new[b][1]-new[a][1]
        gain_profile[old_rank] -= signed[a, b]
        if new_rank:
            gain_profile[new_rank] += signed[a, b]
    gain_profile = {r: c for r, c in sorted(gain_profile.items()) if c}
    assert best == sum(score[r]*c for r, c in gain_profile.items())
    assert sum(r*c for r, c in gain_profile.items()) == 0
    record = dict(vertices=block, signed_edges=sum(bool(c) for c in signed.values()), stats=stats,
                  best_encoded_score=str(best), best_gain_profile=gain_profile)
    if best == 0:
        assert not gain_profile
        if second is None:
            record['proof'] = 'all feasible signed profiles identical'
        else:
            center = Q((second + stride//2)//stride, GRID)
            bound = center + 2*mass*uncertainty
            record['nonzero_profile_upper'] = str(bound)
            if bound < 0:
                record['proof'] = 'every other signed profile strictly loses'
            else:
                record['proof'] = 'interval inconclusive'
    else:
        lo_gain, hi_gain = graph.margin({r: -c for r, c in gain_profile.items()}, intervals)
        record.update(proof='strict positive candidate' if lo_gain > 0 else 'interval inconclusive',
                      best_gain=[str(lo_gain), str(hi_gain)],
                      changed_bases={i: basis(frozenset(bits(new[i][0]))) for i in sorted(vertices)
                                     if new[i] != base[i]})
        if compare_winner and second is not None:
            center_gap = Q((second + stride//2)//stride - (best + stride//2)//stride, GRID)
            record['other_profile_minus_winner_upper'] = str(center_gap + 2*mass*uncertainty)
    return record


def main(word_path, graph_path, price_path, verified_path=None):
    raw = gzip.decompress(word_path.read_bytes())
    assert sha256(raw).hexdigest() == WORD
    graph = load('chart_graph', graph_path)
    price = load('directed_price', price_path)
    space, lo, hi, moves, helpers, islands = geometry(json.loads(raw), graph)
    paid = Counter((a,b) for _, a, b in moves)
    target = Counter((a,b) for _, a, b in helpers)
    base = {i: chart(s) for i, s in enumerate(space) if s is not None}
    checked = None if verified_path is None else json.loads(verified_path.read_bytes())
    if checked:
        assert checked['base_canonical_sha256'] == WORD
        assert checked['candidate_canonical_sha256'] == 'cca66a7ec924bab47ccd1410968d16e071a01dc6110b5c08040bd207f753d066'
        bracket = checked['independent_price']['crossing_intervals']['candidate']
    else:
        bracket = BRACKET
    left, right = map(Q, bracket)
    intervals = {r: (price.raw_margin({r:1}, right)[0], price.raw_margin({r:1}, left)[1])
                 for r in range(1, 10)}
    assert graph.margin({1: 1, 2: -2, 3: 1}, intervals)[0] > 0
    assert top_two((4, 2, 3, 4)) == (4, 3)
    records = [solve(block, base, lo, hi, paid, target, intervals, graph, bool(checked))
               for choices, block in sorted(islands) if checked or choices > 50000]
    assert len(records) == (99 if checked else 14)
    result = dict(word=WORD, crossing=bracket, formerly_open=14,
                  outcomes=Counter(r['proof'] for r in records), results=records)
    if checked:
        winners = [r for r in records if r['proof'] == 'strict positive candidate']
        assert len(winners) == 1
        assert not any(r['proof'] == 'interval inconclusive' for r in records)
        literal_gain = Counter({int(r): n for r, n in checked['local_target_delta'].items()})
        literal_gain.subtract({int(r): n for r, n in checked['local_paid_delta'].items()})
        assert winners[0]['best_gain_profile'] == {r:n for r,n in literal_gain.items() if n}
        assert winners[0]['changed_bases'] == {107: []}
        assert Q(winners[0]['other_profile_minus_winner_upper']) < 0
        result['winner_word'] = checked['candidate_canonical_sha256']
        result['fixed_scalar_chart_margin_optimized'] = True
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    if not __debug__:
        raise RuntimeError('Assertions are proof checks')
    main(*(Path(p) for p in sys.argv[1:]))
