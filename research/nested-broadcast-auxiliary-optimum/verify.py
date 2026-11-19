"""Check auxiliary-vertex elimination and the source-bound broadcast tariff."""
from fractions import Fraction as F
from hashlib import sha1, sha256
from itertools import product
from pathlib import Path
import argparse
import json
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
TERMINALS = (0, 4, 6, 7)


def need(value, reason):
    if not value:
        raise ValueError(reason)


def read(path):
    return json.loads(path.read_text())


def connected(vertices, edges):
    seen = {next(iter(vertices))}
    while True:
        new = seen | {b for a, b in edges if a in seen} | {a for a, b in edges if b in seen}
        if new == seen:
            return seen == set(vertices)
        seen = new


def trees(n):
    result = []
    for code in product(range(n), repeat=n-2):
        degrees = [1]*n
        for v in code:
            degrees[v] += 1
        edges = []
        for v in code:
            leaf = degrees.index(1)
            edges.append(tuple(sorted((leaf, v))))
            degrees[leaf] -= 1
            degrees[v] -= 1
        edges.append(tuple(i for i, d in enumerate(degrees) if d == 1))
        edges = tuple(sorted(edges))
        need(len(edges) == n-1 and connected(range(n), edges), 'decoded labeled tree')
        result.append(edges)
    need(len(set(result)) == len(result) == n**(n-2), 'complete distinct Prufer census')
    return result


def basis_cost(lengths):
    return [sum(min(length, cap) for length in lengths) for cap in range(1, 10)]


def check_tariff(values):
    need(values[0] == 0, 'zero origin tariff')
    slopes = [b-a for a, b in zip(values, values[1:])]
    need(min(slopes) >= 0, 'nondecreasing tariff')
    need(all(a >= b for a, b in zip(slopes, slopes[1:])), 'concave tariff')
    weights = [a-b for a, b in zip(slopes, slopes[1:])]+[slopes[-1]]
    need(all(sum(w*min(r, s+1) for s, w in enumerate(weights)) == values[r]
             for r in range(len(values))), 'exact concave-basis reconstruction')
    return weights


def integer_census():
    floor = basis_cost([1, 2, 4])
    digest = sha256()
    rows = []
    for extra in range(3):
        n = 4+extra
        family = trees(n)
        minimum = [10**9]*9
        minimizers = [0]*9
        cases = 0
        for edges in family:
            for auxiliary in product(range(10), repeat=extra):
                ranks = TERMINALS+auxiliary
                lengths = sorted(abs(ranks[a]-ranks[b]) for a, b in edges)
                costs = basis_cost(lengths)
                need(all(a >= b for a, b in zip(costs, floor, strict=True)),
                     'all increasing concave integer-grid tariffs')
                for i, cost in enumerate(costs):
                    if cost < minimum[i]:
                        minimum[i], minimizers[i] = cost, 1
                    elif cost == minimum[i]:
                        minimizers[i] += 1
                digest.update(json.dumps([extra, edges, auxiliary, lengths], separators=(',', ':')).encode()+b'\n')
                cases += 1
        need(minimum == floor and cases == n**(n-2)*10**extra, 'census completeness and attainment')
        rows.append(dict(auxiliary_vertices=extra, labeled_trees=len(family),
                         placements_per_tree=10**extra, cases=cases,
                         basis_minimum=minimum, basis_minimizer_counts=minimizers))
    weights = []
    # Every one of these spectra defines an increasing concave tariff exactly.
    for mask in range(512):
        w = [(mask>>s)&1 for s in range(9)]
        values = [sum(a*min(r, s+1) for s, a in enumerate(w)) for r in range(10)]
        need(check_tariff(values) == w, 'all binary basis combinations')
        weights.append(w)
    return dict(terminal_ranks=list(TERMINALS), auxiliary_rank_domain=[0, 9],
                basis_caps=list(range(1, 10)), basis_floor=floor, cases=rows,
                total_cases=sum(r['cases'] for r in rows), census_sha256=digest.hexdigest(),
                tariff_reconstructions=len(weights))


def cost(edges, ranks, cap):
    return sum(min(abs(ranks[a]-ranks[b]), cap) for a, b in edges)


def contract_auxiliaries(edges, positions, cap):
    edges = set(edges)
    ranks = dict(enumerate(positions))
    start = cost(edges, ranks, cap)
    steps = []
    for vertex in range(4, len(positions)):
        neighbors = sorted(b if a == vertex else a for a, b in edges if vertex in (a, b))
        need(neighbors, 'connected auxiliary vertex')
        x = ranks[vertex]
        points = sorted({ranks[v] for v in neighbors})
        if x <= points[0]:
            choices = [points[0]]
        elif x >= points[-1]:
            choices = [points[-1]]
        else:
            choices = [max(y for y in points if y <= x), min(y for y in points if y >= x)]
        def local(y):
            return sum(min(abs(y-ranks[v]), cap) for v in neighbors)
        target = min(choices, key=lambda y: (local(y), y))
        need(local(target) <= local(x), 'concave endpoint move does not increase cost')
        before = cost(edges, ranks, cap)
        ranks[vertex] = target
        survivor = next(v for v in neighbors if ranks[v] == target)
        replacement = set()
        for a, b in edges:
            a = survivor if a == vertex else a
            b = survivor if b == vertex else b
            if a != b:
                replacement.add(tuple(sorted((a, b))))
        need(len(replacement) == len(edges)-1, 'one tree edge contracted')
        edges = replacement
        del ranks[vertex]
        after = cost(edges, ranks, cap)
        need(after <= before and connected(ranks, edges), 'connected nonincreasing contraction')
        need(all(ranks[i] == TERMINALS[i] for i in range(4)), 'terminals do not move')
        steps.append([vertex, survivor, str(x), str(target), str(before), str(after)])
    need(set(ranks) == set(range(4)) and len(edges) == 3, 'terminal tree remains')
    final = cost(edges, ranks, cap)
    floor = sum(min(r, cap) for r in (1, 2, 4))
    need(start >= final >= floor, 'terminal-tree lower bound')
    return steps, sorted(edges), start-final


def contraction_census():
    digest = sha256()
    cases = 0
    maximum_drop = F(0)
    samples = []
    positions = [(-2, 9), (F(1, 2), F(11, 2)), (4, 4)]
    for edges in trees(6):
        for pair in positions:
            for cap in (1, 3, 9):
                steps, final, drop = contract_auxiliaries(edges, TERMINALS+pair, cap)
                row = dict(edges=[list(edge) for edge in edges], auxiliary=list(map(str, pair)), cap=cap,
                           steps=steps, final_edges=[list(edge) for edge in final])
                digest.update(json.dumps(row, sort_keys=True, separators=(',', ':')).encode()+b'\n')
                if not samples or drop > maximum_drop:
                    samples.append(row)
                maximum_drop = max(maximum_drop, drop)
                cases += 1
    need(cases == 1296*3*3, 'all specified contraction traces')
    return dict(cases=cases, contractions=2*cases, trace_sha256=digest.hexdigest(),
                maximum_cost_drop=str(maximum_drop), sample_traces=samples)


def reject(label, operation):
    try:
        operation()
    except ValueError as error:
        return dict(control=label, rejection=str(error))
    raise ValueError('accepted mutation '+label)


def run():
    pins = read(HERE/'SOURCE-PINS.json')['sources']
    for pin in pins:
        raw = (HERE/pin['retained']).read_bytes()
        need(sha256(raw).hexdigest() == pin['sha256'] and
             sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == pin['git_blob'],
             'retained source bytes')
    source = HERE/'retained/source7790'
    command = [sys.executable, '-W', 'error', *(['-O'] if sys.flags.optimize else []),
               '-B', str(source/'verify.py')]
    replay = subprocess.run(command, capture_output=True, text=True, check=True, timeout=60)
    need('PASS_BINARY_ROOTED_ROUTING_OPTIMUM' in replay.stdout, 'unchanged source replay')
    receipt = read(source/'RESULT.json')
    need(receipt['routing']['dimensions'] == list(TERMINALS) and
         receipt['routing']['ports'] == [0, 509, 390, 517] and
         receipt['optimal_paid_ranks'] == [1, 2, 4] and
         receipt['actual_packet_chain'] == [2944, 2943, 2942], 'actual source-chain binding')
    census = integer_census()
    contraction = contraction_census()
    controls = [reject('convex squared tariff', lambda: check_tariff([r*r for r in range(10)])),
                reject('decreasing tariff', lambda: check_tariff([0, 2, 1])),
                reject('nonzero origin', lambda: check_tariff([1, 2, 3]))]
    need(sum(r*r for r in (2, 2, 2, 1)) == 13 < 21 == sum(r*r for r in (4, 2, 1)),
         'convex tariff gains from one auxiliary rank-two port')
    need(2+1 < 4+2+1, 'a free second copy at rank four changes the boundary')
    need(not connected(range(4), [(0, 1), (2, 3)]), 'disconnected demand control')
    controls.append(reject('false strict floor', lambda: need(min(census['basis_floor']) > 3,
                                                            'attaining chain has cap-one cost three')))
    return dict(source_files=len(pins), source_word_sha256=receipt['word_sha256'],
                ports=receipt['routing']['ports'], source_packet_chain=receipt['actual_packet_chain'],
                source_replay=dict(coefficients_each_orientation=receipt['coefficients_each_orientation'],
                                   dirty_retirements_each_orientation=receipt['dirty_retirements_each_orientation']),
                integer_census=census, contraction_census=contraction, controls=controls,
                scope_counterexamples=dict(convex_old_cost=21, convex_extra_port_cost=13,
                                           free_second_copy_linear_cost=3, one_source_linear_cost=7),
                disconnected_demand_control=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--write-result', action='store_true')
    args = parser.parse_args()
    start = time.monotonic()
    result = run()
    path = HERE/'RESULT.json'
    if args.write_result:
        path.write_text(json.dumps(result, indent=2)+'\n')
    else:
        need(result == read(path), 'computed receipt matches committed receipt')
    print('PASS_NESTED_BROADCAST_AUXILIARY_OPTIMUM', result['integer_census']['total_cases'],
          'tree placements;', result['contraction_census']['cases'], 'contraction traces;',
          round(time.monotonic()-start, 2), 'seconds')
