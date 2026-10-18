#!/usr/bin/env python3
"""Verify prescribed-target deletion budgets for signed two-ports (Python >=3.10).

The graph optimizer uses vertex partitions (with component colorings for C+).
The independent p=3 oracle enumerates every retained edge set and tests units
by binary column rank.  The independent p=4 oracle enumerates every decoder
labeling satisfying the prescribed unit values, modulo common translation.

Copyright 2026 Sam Sung. Apache-2.0. Substantial OpenAI Codex assistance.
Finite checks supplement GRAPH-TARGETS.md; they do not prove the uniform claims.
"""
import argparse
from collections import Counter
from hashlib import sha256
from itertools import combinations, permutations, product
import json
from math import comb
import os
from pathlib import Path
import subprocess
import sys
import tempfile


def require(ok, message):
    if not ok:
        raise ValueError(message)


def rank(values):
    basis = {}
    for value in values:
        while value:
            pivot = value.bit_length() - 1
            if pivot not in basis:
                basis[pivot] = value
                break
            value ^= basis[pivot]
    return len(basis)


def graph(p):
    return [(u, v) for u, v in combinations(range(2 * p), 2) if u // 2 != v // 2]


def positions(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def columns(edges, n, plus):
    return [(1 << u) ^ (1 << v) ^ ((1 << n) if plus else 0) for u, v in edges]


def units(retained, cols):
    ids = list(positions(retained))
    dimension = rank(cols[i] for i in ids)
    return sum(1 << i for i in ids if rank(cols[j] for j in ids if j != i) < dimension)


def cycle_units(retained, edges, n, plus):
    """Fundamental-cycle coordinate functionals, without binary elimination."""
    adjacency = [[] for _ in range(n)]
    for i in positions(retained):
        u, v = edges[i]
        adjacency[u].append((v, i))
        adjacency[v].append((u, i))
    paths = [None] * n
    tree = 0
    for root in range(n):
        if paths[root] is not None:
            continue
        paths[root] = 0
        stack = [root]
        while stack:
            u = stack.pop()
            for v, i in adjacency[u]:
                if paths[v] is None:
                    paths[v] = paths[u] ^ (1 << i)
                    tree |= 1 << i
                    stack.append(v)
    cycles = [paths[edges[i][0]] ^ paths[edges[i][1]] ^ (1 << i)
              for i in positions(retained & ~tree)]
    parity = sum((c.bit_count() % 2) << j for j, c in enumerate(cycles))
    answer = 0
    for i in positions(retained):
        functional = sum(((c >> i) & 1) << j for j, c in enumerate(cycles))
        if functional == 0 or (plus and functional == parity):
            answer |= 1 << i
    return answer


def partitions(n):
    labels = [0] * n
    def walk(i, count):
        if i == n:
            yield tuple(labels), count
            return
        for label in range(count + 1):
            labels[i] = label
            yield from walk(i + 1, max(count, label + 1))
    yield from walk(1, 1)


def partition_records(n, edges, plus):
    records = []
    for labels, count in partitions(n):
        free = [i for i in range(n) if i != labels.index(labels[i])]
        for color_bits in range(1 << len(free)) if plus else (0,):
            colors = [0] * n
            for j, i in enumerate(free):
                colors[i] = (color_bits >> j) & 1
            reduced = tuple((1 << labels[u]) ^ (1 << labels[v]) ^
                            (((1 ^ colors[u] ^ colors[v]) << count) if plus else 0)
                            for u, v in edges)
            zero = sum(1 << i for i, value in enumerate(reduced) if value == 0)
            records.append((zero.bit_count(), zero, reduced))
    records.sort(key=lambda item: (-item[0], item[1], item[2]))
    return records


def partition_optimum(target, cols, records, baseline=None):
    ids = list(positions(target))
    if rank(cols[i] for i in ids) != len(ids):
        return None
    best = baseline
    for count, zero, reduced in records:
        if best is not None and count + len(ids) <= best[0]:
            break
        if not zero & target and rank(reduced[i] for i in ids) == len(ids):
            best = (count + len(ids), zero | target)
            break
    require(best is not None, 'a target-independent set needs a retained witness')
    return best


def all_retained_oracle(p, edges):
    size = 1 << len(edges)
    best = [[-1] * size for _ in range(2)]
    witnesses = [[0] * size for _ in range(2)]
    cols = [columns(edges, 2 * p, plus) for plus in (False, True)]
    for retained in range(size):
        weight = retained.bit_count()
        for plus in (0, 1):
            decodable = units(retained, cols[plus])
            require(decodable == cycle_units(retained, edges, 2 * p, plus), 'cycle characterization')
            if weight > best[plus][decodable]:
                best[plus][decodable] = weight
                witnesses[plus][decodable] = retained
    for plus in (0, 1):
        for bit in range(len(edges)):
            for target in range(size):
                superset = target | (1 << bit)
                if best[plus][superset] > best[plus][target]:
                    best[plus][target] = best[plus][superset]
                    witnesses[plus][target] = witnesses[plus][superset]
    return best, witnesses


def target_orbits(p, edges, sizes):
    edge_id = {edge: i for i, edge in enumerate(edges)}
    maps = []
    for perm in permutations(range(p)):
        for flips in product(range(2), repeat=p):
            vertices = [2 * perm[i // 2] + ((i % 2) ^ flips[i // 2]) for i in range(2 * p)]
            maps.append([1 << edge_id[tuple(sorted((vertices[u], vertices[v])))] for u, v in edges])
    for size in sizes:
        todo = {sum(1 << i for i in ids) for ids in combinations(range(len(edges)), size)}
        while todo:
            target = min(todo)
            ids = list(positions(target))
            orbit = {sum(mapping[i] for i in ids) for mapping in maps}
            require(orbit <= todo, 'automorphism orbits must be disjoint')
            todo.difference_update(orbit)
            yield target, len(orbit)


def decoder_oracle(target, edges, n, plus):
    """Enumerate actual row combinations giving each target its own unit."""
    ids = list(positions(target))
    dimension = len(ids)
    alphabet = 1 << dimension
    adjacency = [[] for _ in range(n)]
    for j, i in enumerate(ids):
        u, v = edges[i]
        adjacency[u].append((v, 1 << j))
        adjacency[v].append((u, 1 << j))
    best = None
    assignments = 0
    for constant in range(alphabet) if plus else (0,):
        offsets = [None] * n
        components = [None] * n
        count = 0
        consistent = True
        for root in range(n):
            if offsets[root] is not None:
                continue
            offsets[root] = 0
            components[root] = count
            count += 1
            stack = [root]
            while stack:
                u = stack.pop()
                for v, value in adjacency[u]:
                    expected = offsets[u] ^ value ^ constant
                    if offsets[v] is None:
                        offsets[v] = expected
                        components[v] = components[u]
                        stack.append(v)
                    elif offsets[v] != expected:
                        consistent = False
        if not consistent:
            continue
        for rest in product(range(alphabet), repeat=count - 1):
            roots = (0,) + rest
            labels = [offsets[i] ^ roots[components[i]] for i in range(n)]
            retained = target
            for i, (u, v) in enumerate(edges):
                if labels[u] ^ labels[v] ^ constant == 0:
                    retained |= 1 << i
            assignments += 1
            score = retained.bit_count()
            if best is None or score > best[0]:
                best = (score, retained)
    return best, assignments


def histogram(values):
    return {str(key): value for key, value in sorted(Counter(values).items(), key=lambda item: str(item[0]))}


def components(n, edges, target):
    parent = list(range(n))
    def root(v):
        while parent[v] != v:
            v = parent[v]
        return v
    for i in positions(target):
        u, v = map(root, edges[i])
        if u == v:
            return None
        parent[u] = v
    blocks = {}
    for v in range(n):
        blocks.setdefault(root(v), []).append(v)
    return list(blocks.values())


def matching_number(blocks, p):
    slots = [sorted({v // 2 for v in block}) for block in blocks for _ in range(len(block) - 1)]
    owner = [-1] * p
    def augment(slot, seen):
        for pair in slots[slot]:
            if pair in seen:
                continue
            seen.add(pair)
            if owner[pair] < 0 or augment(owner[pair], seen):
                owner[pair] = slot
                return True
        return False
    return sum(augment(slot, set()) for slot in range(len(slots)))


def root_choice_number(blocks):
    states = {0}
    for block in blocks:
        options = {sum(1 << pair for pair in {v // 2 for v in block if v != root}) for root in block}
        states = {state | option for state in states for option in options}
    return max(state.bit_count() for state in states)


def forest_budget(p, edges, target):
    blocks = components(2 * p, edges, target)
    if blocks is None:
        return None
    nu = matching_number(blocks, p)
    require(nu == root_choice_number(blocks), 'capacity matching versus literal root choices')
    r = target.bit_count()
    return len(edges) - r - comb(2 * p - r, 2) + p - nu


def small_case(p):
    edges = graph(p)
    cols = [columns(edges, 2 * p, plus) for plus in (False, True)]
    records = [partition_records(2 * p, edges, plus) for plus in (False, True)]
    best, _ = all_retained_oracle(p, edges)
    budgets, forests = [], 0
    for target in range(1 << len(edges)):
        minus = partition_optimum(target, cols[0], records[0])
        plus = partition_optimum(target, cols[1], records[1], minus)
        row = [target]
        for model, result in enumerate((minus, plus)):
            expected = best[model][target]
            require((-1 if result is None else result[0]) == expected,
                    'partition optimum versus complete retained-graph oracle')
            if result is not None:
                require(result[1] & target == target, 'targets must survive')
                require(units(result[1], cols[model]) & target == target, 'witness unit rows')
            row.append(None if expected < 0 else len(edges) - expected)
        proposed = forest_budget(p, edges, target)
        require(proposed == row[1], 'forest formula versus retained-graph oracle')
        forests += proposed is not None
        budgets.append(row)
    result = dict(retained_graphs=1 << len(edges), target_sets=len(budgets),
                  model_target_cases=2 * len(budgets), forest_target_sets=forests,
                  partition_records=[len(x) for x in records],
                  budget_histograms=[histogram(row[m + 1] for row in budgets) for m in (0, 1)],
                  by_target_size={str(r): [histogram(row[m + 1] for row in budgets
                                                    if row[0].bit_count() == r) for m in (0, 1)]
                                  for r in range(len(edges) + 1)},
                  all_budgets_sha256=sha256(json.dumps(budgets, separators=(',', ':')).encode()).hexdigest())
    return result, budgets


def larger_case():
    edges = graph(4)
    cols = [columns(edges, 8, plus) for plus in (False, True)]
    records = [partition_records(8, edges, plus) for plus in (False, True)]
    cases, assignments, restorations, forests = [], [0, 0], 0, 0
    weighted = {r: [Counter(), Counter()] for r in (3, 4)}
    for target, orbit_size in target_orbits(4, edges, (3, 4)):
        minus = partition_optimum(target, cols[0], records[0])
        plus = partition_optimum(target, cols[1], records[1], minus)
        case = dict(target=[edges[i] for i in positions(target)], orbit_size=orbit_size,
                    budgets=[], retained_masks=[], decoder_assignments=[])
        for model, result in enumerate((minus, plus)):
            direct, count = decoder_oracle(target, edges, 8, bool(model))
            assignments[model] += count
            case['decoder_assignments'].append(count)
            require((None if result is None else result[0]) ==
                    (None if direct is None else direct[0]), 'partition versus decoder oracle')
            budget = None if result is None else len(edges) - result[0]
            case['budgets'].append(budget)
            case['retained_masks'].append(None if result is None else result[1])
            weighted[target.bit_count()][model][str(budget)] += orbit_size
            if result is not None:
                retained = result[1]
                require(retained & target == target, 'prescribed targets retained')
                require(units(retained, cols[model]) & target == target, 'direct retained unit check')
                for i in positions(((1 << len(edges)) - 1) ^ retained):
                    require(units(retained | (1 << i), cols[model]) & target != target,
                            'one deletion restoration must fail')
                    restorations += 1
        proposed = forest_budget(4, edges, target)
        require(proposed == case['budgets'][0], 'forest formula versus independent decoder oracle')
        forests += proposed is not None
        cases.append(case)
    require(len(cases) == 73 and sum(c['orbit_size'] for c in cases) == 12650,
            'complete triple/quadruple orbit coverage')
    return dict(target_sets=12650, orbits=len(cases), forest_orbits=forests,
                partition_records=[len(x) for x in records], decoder_assignments=assignments,
                by_target_size={str(r): [dict(sorted(c.items())) for c in weighted[r]] for r in (3, 4)},
                one_deletion_restorations_rejected=restorations, cases=cases)


def boundary_table():
    literal = [('02 03 04', '12', '45', 24, [5, 7, 1]),
               ('02 03 12', '02', '45', 12, [4, 6, 5]),
               ('02 04 12', '23', '45', 48, [5, 1, 6]),
               ('03 04 12', '12', '45', 48, [7, 1, 4]),
               ('04 05 12', '04', '23', 24, [4, 6, 1]),
               ('02 04 24', '01', '35', 8, [5, 6, 7]),
               ('03 04 24', '01', '25', 24, [5, 6, 2]),
               ('03 05 24', '01', '24', 24, [5, 6, 4]),
               ('05 13 24', '01', '24', 8, [6, 5, 4])]
    edges = graph(3)
    edge_id = {edge: i for i, edge in enumerate(edges)}
    orbits = dict(target_orbits(3, edges, (3,)))
    checked, rows = set(), []
    for names, left, right, size, expected in literal:
        targets = [tuple(map(int, name)) for name in names.split()]
        left, right = set(map(int, left)), set(map(int, right))
        target = sum(1 << edge_id[edge] for edge in targets)
        zero = sum(1 << edge_id[tuple(sorted((u, v)))] for u in left for v in right)
        require(zero.bit_count() == 4 and zero & target == 0, 'literal bipartite witness')
        require(orbits[target] == size and target not in checked, 'literal orbit count')
        checked.add(target)
        coordinates = {v: 0 for v in left | right}
        for i, v in enumerate(sorted(set(range(6)) - left - right)):
            coordinates[v] = 1 << i
        reduced = [coordinates[u] ^ coordinates[v] ^ ((1 ^ int(u in right) ^ int(v in right)) << 2)
                   for u, v in targets]
        require(reduced == expected and rank(reduced) == 3, 'literal independent target columns')
        require(units(zero | target, columns(edges, 6, True)) & target == target, 'literal full unit rows')
        rows.append(dict(target=targets, left=sorted(left), right=sorted(right),
                         orbit_size=size, quotient_columns=reduced))
    require(checked == set(orbits), 'literal table covers every p3 triple orbit')
    return rows


def arithmetic_checks():
    count = 0
    for p in range(3, 101):
        for r in range(1, 2 * p):
            s = 2 * p - r
            if s >= 3:
                gap = s - 2 - int(s - 1 >= p)
                loss = r // 2 if r <= p else s // 2
                require(gap >= loss, 'multiple-component gap bound')
            if p >= 6 and r <= p:
                require(comb(s, 2) - s // 2 >= (s + 1)**2 // 4,
                        'uniform constant-row irrelevance criterion')
            count += 1
    return count


def verify():
    p2, _ = small_case(2)
    p3, budgets = small_case(3)
    edges = graph(3)
    ids = {edge: i for i, edge in enumerate(edges)}
    def mask(edge_set):
        return sum(1 << ids[tuple(sorted(edge))] for edge in edge_set)
    triangle = mask([(0, 2), (2, 4), (0, 4)])
    square = mask([(0, 2), (2, 1), (1, 3), (3, 0)])
    two_triangles = triangle | mask([(1, 3), (3, 5), (1, 5)])
    cols = [columns(edges, 6, plus) for plus in (False, True)]
    require(units(triangle, cols[0]) == 0 and units(triangle, cols[1]) == triangle,
            'constant row control')
    require(units(square, cols[0]) == units(square, cols[1]) == 0, 'even target cycle infeasible')
    require(units(two_triangles, cols[1]) == 0, 'two odd cycles have an even dependency')
    require(rank([cols[1][0]]) == 1 and units((1 << len(edges)) - 1, cols[1]) & 1 == 0,
            'target-column independence does not imply unit decoding')
    require(budgets[triangle][1] is None and budgets[triangle][2] == 5, 'triangle feasibility')
    return dict(status='PASS', arithmetic='exact F2 integer bitsets',
                scope='Proper-star observations for k=2, with and without the empty star. '
                      'All target sets at p=2,3 and all triples/quadruples at p=4 are checked. '
                      'The uniform theorems are proved in GRAPH-TARGETS.md; no physical-cost or kappa claim.',
                p2=p2, p3=p3, p4=larger_case(), p3_literal_triple_witnesses=boundary_table(),
                forest_formula='E-r-binomial(2p-r,2)+p-nu(T); nu checked by matching and root-choice DP',
                integer_inequality_cases=arithmetic_checks(),
                negative_controls=['omitting the constant row loses triangle units',
                                   'an even target cycle is impossible in both models',
                                   'two edge-disjoint odd cycles cancel global parity',
                                   'target-column independence alone does not isolate targets',
                                   'every one-deletion restoration of each p4 optimum loses a required unit'],
                literal_controls=dict(p3_triangle_budgets=budgets[triangle][1:],
                                      p3_square_budgets=budgets[square][1:]))


RECEIPT = 'GRAPH-TARGETS-RESULTS.json'


def atomic_write(path, payload):
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent,
                                         prefix=path.name + '.', suffix='.tmp', delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def self_test(result):
    from unittest.mock import patch
    with tempfile.TemporaryDirectory() as directory:
        directory = Path(directory)
        script = directory / Path(__file__).name
        script.write_bytes(Path(__file__).read_bytes())
        receipt = directory / RECEIPT
        receipt.write_text(json.dumps(result), encoding='utf-8')
        command = [sys.executable, '-I', '-O', '-B', str(script)]
        run = subprocess.run(command, cwd=directory, capture_output=True, text=True)
        require(run.returncode == 0, f'minimal relocated optimized replay failed: {run.stderr}')
        damaged = json.loads(json.dumps(result))
        damaged['p3']['all_budgets_sha256'] = '0' * 64
        receipt.write_text(json.dumps(damaged), encoding='utf-8')
        protected = directory / 'protected.json'
        protected.write_text('preserve this output\n', encoding='utf-8')
        run = subprocess.run(command + ['--check', str(receipt), '--write', str(protected)],
                             cwd=directory, capture_output=True, text=True)
        require(run.returncode != 0 and 'receipt mismatch' in run.stderr, 'corrupt receipt accepted')
        require(protected.read_text() == 'preserve this output\n', 'failed check overwrote output')
        before = set(directory.iterdir())
        with patch('os.replace', side_effect=OSError('simulated replacement failure')):
            try:
                atomic_write(protected, 'must not replace the output\n')
            except OSError:
                pass
            else:
                raise ValueError('atomic replacement failure was not propagated')
        require(protected.read_text() == 'preserve this output\n', 'failed replacement lost output')
        require(set(directory.iterdir()) == before, 'failed replacement left a temporary file')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', type=Path, help='atomically write a receipt after all requested checks pass')
    parser.add_argument('--check', type=Path, help='compare this receipt before any output write')
    parser.add_argument('--self-test', action='store_true', help='check relocation, corruption rejection, and output preservation')
    args = parser.parse_args()
    result = json.loads(json.dumps(verify()))
    if args.check or not args.write:
        receipt = args.check or Path(__file__).resolve().with_name(RECEIPT)
        require(json.loads(receipt.read_text(encoding='utf-8')) == result, f'receipt mismatch: {receipt}')
    if args.self_test:
        self_test(result)
    if args.write:
        atomic_write(args.write, json.dumps(result, sort_keys=True, indent=2) + '\n')
    print('PASS graph targets: 4,112 complete target sets; 73 p4 orbits covering 12,650 targets; '
          f"{sum(result['p4']['decoder_assignments']):,} decoder assignments; forest formula verified")


if __name__ == '__main__':
    main()
