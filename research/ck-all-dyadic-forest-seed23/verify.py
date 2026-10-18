#!/usr/bin/env python3
"""Exact CK all-dyadic single-parent forest exclusion. Apache-2.0."""
import argparse
from collections import Counter
from fractions import Fraction
import gzip
import hashlib
import json
from math import gcd
import struct
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = 'research/community-k492-audit/pr626/replay/mixed-global/base/providers/ck/CANONICAL-WORD.json.gz'
RECIPE = 'research/complex-ck-target-forest/RECIPE.json'
TARGETS = range(112, 224)
NUMERATORS = tuple(range(-543, 0)) + tuple(range(1, 544))


def require(value, message):
    if not value:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def price(n, d=1):
    if not n:
        return 0
    common = gcd(abs(n), d)
    a, b = abs(n)//common, d//common
    require(b & (b - 1) == 0, 'non-dyadic coefficient')
    return 3 + a.bit_length() - 1 + a.bit_count() + b.bit_length() - 1


def literal_price(n, d):
    """Independent count by actual binary-Horner operations, including dirty work."""
    q = Fraction(n, d)
    if not q:
        return 0
    a, b = abs(q.numerator), q.denominator
    digits = []
    while a:
        digits.append(a % 2)
        a //= 2
    work, work_denominator = 0, 1  # initial CLEAR discards arbitrary private dirt
    count = 1
    for i, digit in enumerate(reversed(digits)):
        if i:
            work += work
            count += 1
        if digit:
            work += 1
            count += 1
    while b > 1:
        require(b % 2 == 0, 'literal non-dyadic')
        work_denominator *= 2
        b //= 2
        count += 1
    require(work*q.denominator == abs(q.numerator)*work_denominator, 'literal coefficient')
    # Signed target accumulation and final private CLEAR.
    return count + 2


def load():
    pins = json.loads((HERE / 'SOURCES.json').read_text())
    objects = {}
    for name, pin in pins['files'].items():
        data = (ROOT / name).read_bytes()
        if pin['encoding'] == 'gzip-payload':
            data = gzip.decompress(data)
        require(hashlib.sha256(data).hexdigest() == pin['sha256'], 'source pin: ' + name)
        objects[name] = json.loads(data)
    word, recipe = objects[WORD], objects[RECIPE]
    require((word['v'], word['R'], word['h']) == (112, 492, 9), 'geometry')
    rows = {t: {} for t in TARGETS}
    for op, t, h, a, b, frame in word['compensation']:
        require(op == 'add' and t in rows and 224 <= h < 716 and frame == 0, 'panel interface')
        require(word['start'][t] == word['start'][h] == 0, 'panel frame')
        q, remainder = divmod(4*a, b)
        require(remainder == 0 and 0 < abs(q) <= 4 and h not in rows[t], 'quarter alphabet')
        rows[t][h] = q
    require(sum(map(len, rows.values())) == 8704, 'panel cardinality')
    return rows, recipe


def row_price(row):
    return sum(price(a, 4) for a in row.values())


def pair_histogram(left, right):
    return Counter((left.get(h, 0), right.get(h, 0)) for h in left.keys() | right.keys())


def edge_cost(histogram, n):
    return 2 * price(n, 8) + sum(count * price(8*a - n*b, 32) for (a, b), count in histogram.items())


def census(rows):
    # Aggregation is exact: the histogram retains every ordered coefficient pair.
    groups = {}
    for t in TARGETS:
        for p in TARGETS:
            if t != p:
                hist = tuple(sorted(pair_histogram(rows[t], rows[p]).items()))
                groups.setdefault(hist, []).append((t, p))
    table = {(a, b): [price(8*a-n*b, 32) for n in NUMERATORS]
             for a in range(-4, 5) for b in range(-4, 5) if a or b}
    boundaries = [2*price(n, 8) for n in NUMERATORS]
    # Exact 16-bit SIMD-in-an-integer: all residual prices are <=32 and
    # there are <=492 cells plus two boundary operations, so no lane carries.
    require(max(max(v) for v in table.values()) <= 32 and max(boundaries) <= 64,
            'packed scalar bound')
    require((492+2)*32 < 65536, 'packed sum bound')
    packed = {pair: int.from_bytes(struct.pack('<1086H', *values), 'little')
              for pair, values in table.items()}
    boundary = int.from_bytes(struct.pack('<1086H', *boundaries), 'little')
    histogram = Counter()
    root_winners = 0
    minimum = minimum_root = None
    unit_indices = [NUMERATORS.index(-8), NUMERATORS.index(8)]
    summaries = []
    for hist, pairs in sorted(groups.items()):
        root = sum(count*price(a, 4) for (a, _), count in hist)
        encoded = boundary + sum(count*packed[pair] for pair, count in hist)
        costs = list(struct.unpack('<1086H', encoded.to_bytes(2172, 'little')))
        baseline = min(root, *(costs[i] for i in unit_indices))
        multiplicity = len(pairs)
        first_pair = min(pairs)
        local_min = None
        for n, cost in zip(NUMERATORS, costs):
            if abs(n) == 8:
                continue
            margin, root_margin = cost-baseline, cost-root
            require(margin > 0, 'nonunit edge escapes domination')
            histogram[margin] += multiplicity
            root_winners += multiplicity * (root_margin < 0)
            record = (margin, *first_pair, n)
            root_record = (root_margin, *first_pair, n)
            minimum = record if minimum is None else min(minimum, record)
            minimum_root = root_record if minimum_root is None else min(minimum_root, root_record)
            local_min = margin if local_min is None else min(local_min, margin)
        summaries.append([list(map(list, hist)), len(pairs), digest(costs), local_min])
    return {
        'ordered_pairs': 12432, 'coefficient_count': len(NUMERATORS),
        'finite_cases': 12432*len(NUMERATORS), 'nonunit_cases': sum(histogram.values()),
        'histogram_groups': len(groups), 'minimum_domination': list(minimum),
        'minimum_root_margin': list(minimum_root), 'nonunit_edges_beating_root': root_winners,
        'margin_histogram': dict(sorted(histogram.items())), 'group_costs_sha256': digest(summaries),
    }


def signed_floor(rows, recipe):
    edges = [(row_price(rows[t]), -1, t, 0) for t in TARGETS]
    for t in TARGETS:
        for p in range(t+1, 224):
            hist = pair_histogram(rows[t], rows[p])
            for sign in (-1, 1):
                edges.append((edge_cost(hist, 8*sign), t, p, sign))
    # Independent dense Prim, not the predecessor's tie-broken Kruskal.
    graph = {v: {} for v in [-1, *TARGETS]}
    for w, a, b, _ in edges:
        graph[a][b] = graph[b][a] = min(w, graph[a].get(b, w))
    seen, best, total = {-1}, dict(graph[-1]), 0
    while len(seen) != 113:
        vertex = min((v for v in best if v not in seen), key=lambda v: (best[v], v))
        total += best[vertex]
        seen.add(vertex)
        for v, w in graph[vertex].items():
            if v not in seen:
                best[v] = min(best.get(v, w), w)
    selected = recipe['tree_edges']
    require(len(selected) == 112 and sum(e[0] for e in selected) == total, 'attaining floor')
    available = set(edges)
    adjacency = {v: [] for v in graph}
    for w, a, b, s in selected:
        require(tuple((w, a, b, s)) in available, 'unpriced selected edge')
        adjacency[a].append((b, s, w))
        adjacency[b].append((a, s, w))
    queue, visited, order = [(-1, None)], {-1}, []
    for parent, predecessor in queue:
        for child, sign, _ in sorted(adjacency[parent]):
            if child == predecessor:
                continue
            require(child not in visited, 'forest cycle')
            visited.add(child)
            order.append((child, parent, sign))
            queue.append((child, parent))
    require(len(visited) == 113, 'disconnected witness')
    maxima = {}
    for start in adjacency:
        walk = [(start, None, 0)]
        for vertex, parent, maximum in walk:
            maxima[start, vertex] = maximum
            walk.extend((child, vertex, max(maximum, w)) for child, _, w in adjacency[vertex] if child != parent)
    require(all(w >= maxima[a, b] for w, a, b, _ in edges), 'cycle inequality')
    return total, order, len(edges)


def compile_panel(rows, order, coefficients=None):
    coefficients = coefficients or {}
    prep = [(t, p, -coefficients.get(t, Fraction(s))) for t, p, s in reversed(order) if p != -1]
    residual = []
    for t, p, s in order:
        c = coefficients.get(t, Fraction(s))
        support = rows[t].keys() | (rows[p].keys() if p != -1 else set())
        for h in sorted(support):
            q = Fraction(rows[t].get(h, 0), 4) - (c*Fraction(rows[p].get(h, 0), 4) if p != -1 else 0)
            if q:
                residual.append((t, h, q))
    return prep + residual + [(t, p, -q) for t, p, q in reversed(prep)]


def replay(gates, backward=False):
    # Exact row-wise dyadic integers; no floating point or modular recovery.
    state = [{i: 1} for i in range(716)]
    exponents = [0]*716
    for t, s, q in gates:
        if backward:
            t, s, q = s, t, -q
        require(t != s, 'aliased panel gate')
        a, b = q.numerator, q.denominator
        require(b & (b-1) == 0, 'non-dyadic panel gate')
        source_exponent = exponents[s] + b.bit_length()-1
        exponent = max(exponents[t], source_exponent)
        if exponent != exponents[t]:
            state[t] = {col: value << (exponent-exponents[t]) for col,value in state[t].items()}
        multiplier = a << (exponent-source_exponent)
        for col, value in state[s].items():
            result = state[t].get(col, 0) + multiplier*value
            if result:
                state[t][col] = result
            else:
                state[t].pop(col, None)
        exponents[t] = exponent
    normalized = []
    for row, exponent in zip(state, exponents):
        shift = min([exponent, *((abs(v)&-abs(v)).bit_length()-1 for v in row.values())])
        normalized.append((exponent-shift, {col:value >> shift for col,value in row.items()}))
    return normalized


def controls(rows, recipe, order, findings):
    original = [(t, h, Fraction(a, 4)) for t, row in rows.items() for h, a in row.items()]
    panel = compile_panel(rows, order)
    require([['add',t,s,q.numerator,q.denominator,0] for t,s,q in panel] == recipe['compensation'], 'source witness reconstruction')
    expected = [replay(original, b) for b in (False, True)]
    require(all(replay(panel, b) == expected[b] for b in (False, True)), '716-column witness')
    # Exercise nonunit coefficients on overlapping ancestor/descendant branches,
    # not merely disjoint pairs. This is endpoint evidence, not an infinite replay.
    mixed = {t: Fraction(((-1)**i)*(2*i+3), 8) for i,(t,p,_) in enumerate(order) if p != -1}
    extended = compile_panel(rows, order, mixed)
    require(all(replay(extended, b) == expected[b] for b in (False, True)), 'mixed dyadic forest identity')
    reject = []
    mutations = {
        'omitted_preparation': panel[1:],
        'omitted_restoration': panel[:-1],
        'sign_error': [(panel[0][0],panel[0][1],-panel[0][2]), *panel[1:]],
        'nonunit_stale_residual': [(panel[0][0],panel[0][1],2*panel[0][2]), *panel[1:]],
        'reversed_preparation': list(reversed(panel[:106])) + panel[106:],
        'reversed_restoration': panel[:-106] + list(reversed(panel[-106:])),
    }
    for name, mutant in mutations.items():
        require(replay(mutant) != expected[0], 'missed mutation: '+name)
        reject.append(name)
    # A root-only domination theorem would be false on this actual CK input.
    root_margin,t,p,n = findings['minimum_root_margin']
    require(edge_cost(pair_histogram(rows[t],rows[p]),n)-row_price(rows[t]) == root_margin < 0, 'root-only counterexample')
    reject.append('root_only_domination')
    # Quarter alphabet alone does not imply same-parent domination either.
    synthetic = {(3,1): 100}
    require(edge_cost(synthetic,24) < min(100*price(3,4),edge_cost(synthetic,-8),edge_cost(synthetic,8)), 'synthetic nonunit winner')
    reject.append('alphabet_only_domination')
    try:
        price(1,3)
    except ValueError:
        reject.append('non_dyadic_coefficient')
    else:
        raise ValueError('non-dyadic accepted')
    require(min(4+4, 8) >= max(price(a,4) for a in range(-4,5)), 'tail price threshold')
    # Reducing the denominator cutoff to 3 is unsound: 3/4-(5/8)*1=1/8.
    require(price(1,8) < price(3,4), 'tail arithmetic control')
    reject.append('denominator_tail_started_too_early')
    return {'columns':716, 'orientations':2, 'mixed_nonunit_edges':len(mixed), 'rejected':reject,
            'witness_additions':len(panel)}


def run():
    rows, recipe = load()
    # Covers every coefficient appearing anywhere in the complete finite census.
    for n in range(-2204,2205):
        require(price(n,32) == literal_price(n,32), 'literal lowering count')
    findings = census(rows)
    floor, order, inequalities = signed_floor(rows,recipe)
    require(floor == 16364, 'historical floor')
    result = {'format':'ck-all-dyadic-forest-v1','seed':23,'finite':findings,
              'signed_floor':floor,'cycle_inequalities':inequalities,
              'tail':{'max_entry_price':8,'denominator_exponent_from':4,'magnitude_from':68,
                      'argument':'coordinatewise root domination plus two strictly positive boundary shears'},
              'literal_coefficient_cases':4409,
              'controls':controls(rows,recipe,order,findings)}
    return json.loads(json.dumps(result))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--record', action='store_true')
    args = parser.parse_args()
    result = run()
    path = HERE/'EXPECTED.json'
    if args.record:
        path.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:
        require(json.loads(path.read_text()) == result, 'complete receipt mismatch')
    print('PASS_CK_ALL_DYADIC_FOREST cases=13501152 floor=16364 margin=63 columns=716x2 controls=10 no_new_kappa')


if __name__ == '__main__':
    main()
