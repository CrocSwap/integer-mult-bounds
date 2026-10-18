"""Exact pooled-prefix audit; stdlib only, no predecessor checker imports.

AAAmirinu with substantial OpenAI Codex assistance. Apache-2.0.
The proof in README.md supplies the universal implication; this checks its
source-bound premises and finite upper/lower certificates over Q.
"""
from collections import Counter, defaultdict
from fractions import Fraction as Q
from functools import lru_cache
from itertools import combinations, product
from pathlib import Path
import argparse
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INTERVALS = [(0, 2525, 104), (2526, 2555, 103), (2556, 2571, 102),
             (2572, 2617, 101), (2618, 2645, 100), (2646, 2717, 99)]


def need(condition, message):
    if not condition:
        raise ValueError(message)


def unique(pairs):
    answer = {}
    for key, value in pairs:
        need(key not in answer, 'duplicate JSON key')
        answer[key] = value
    return answer


def read(path):
    return json.loads(path.read_bytes(), object_pairs_hook=unique)


def rank(rows):
    basis = {}
    for row in rows:
        add_basis(basis, row)
    return len(basis)


def add_basis(basis, row):
    row = list(map(Q, row))
    for pivot, old in sorted(basis.items()):
        coefficient = row[pivot]
        if coefficient:
            row = [x - coefficient * y for x, y in zip(row, old)]
    pivot = next((i for i, value in enumerate(row) if value), None)
    if pivot is None:
        return False
    divisor = row[pivot]
    basis[pivot] = [x / divisor for x in row]
    return True


def solvable(matrix, rhs):
    return rank(matrix) == rank([list(row) + [value]
                                for row, value in zip(matrix, rhs)])


@lru_cache(maxsize=None)
def frame(vectors):
    values = {0}
    for value in vectors:
        need(type(value) is int and 0 < value < 512, 'binary frame vector')
        values |= {value ^ old for old in tuple(values)}
    need(len(values) == 2 ** len(vectors), 'independent binary frame basis')
    return frozenset(values)


def geometry(fixture):
    lines = set()
    for first, second in combinations(range(8), 2):
        for sign in [-1, 1]:
            row = [0] * 8
            row[first], row[second] = 2, 2 * sign
            lines.add(tuple(row))
    for tail in product([-1, 1], repeat=7):
        if sum(x < 0 for x in tail) % 2 == 0:
            lines.add((1, *tail))
    removed = {tuple(row) for row in fixture['F0'] + fixture['C']}
    need(len(lines) == 120 and len(removed) == 16 and removed <= lines,
         'P104 punctured E8 fixture')
    ports = sorted(lines - removed)
    need(len(ports) == 104, '104 ports')
    need(all(sum(row[i] * row[j] for row in ports) == 104 * (i == j)
             for i in range(8) for j in range(8)), 'R R^T = 104 I')
    return ports


def replay(word, ports, wanted=()):
    """Dense integer rows on an exactly checked denominator-eight lattice.

    Track all 280 inputs, not just code projections. Enumerate same-frame
    snapshots at EVERY cut. Pool only up to 2717; replay the whole endpoint.
    """
    names = list(word['initial_frames'])
    need(len(names) == 280 and set(names) == set(word['final_frames']), 'boundary names')
    need(names[:104] == ['X' + str(i) for i in range(104)], 'source column order')
    need(names[104:208] == ['Y' + str(i) for i in range(104)], 'target column order')
    indices = {name: i for i, name in enumerate(names)}
    state = {name: tuple(8 * (i == j) for j in range(280))
             for i, name in enumerate(names)}
    frames = {name: frame(tuple(value)) for name, value in word['initial_frames'].items()}
    initial = dict(state)
    need(all(frames[name] == frozenset({0}) for name in names[104:]), 'initial nuisance units')
    pools = [set() for _ in ports]
    snapshots = {}
    desired = set(wanted)
    checkpoints = {}
    projection_cache = {}
    observed = set()
    profile, operations = Counter(), Counter()

    def inspect(cut):
        groups = defaultdict(list)
        for name, value in frames.items():
            groups[value].append(name)
        for group in groups.values():
            targets = [int(name[1:]) for name in group if name.startswith('Y')]
            if not targets:
                continue
            for name in group:
                row = state[name]
                if row not in projection_cache:
                    x = row[:104]
                    coeff = tuple(Q(sum(x[s] * ports[s][j] for s in range(104)), 832)
                                  for j in range(8))
                    need(all(sum(coeff[j] * ports[s][j] for j in range(8)) == Q(x[s], 8)
                             for s in range(104)), 'eligible source projection outside root code')
                    projection_cache[row] = coeff
                coeff = projection_cache[row]
                for target in targets:
                    if name == 'Y' + str(target):
                        continue
                    need(row[104 + target] == 0, 'eligible snapshot contains own target dirt')
                    observed.add((target, row))
                    if any(coeff) and cut <= 2717:
                        pools[target].add(coeff)
                    key = target, cut, name
                    if key in desired:
                        snapshots[key] = coeff
        if cut in {end for _, end, _ in INTERVALS}:
            checkpoints[cut] = [set(pool) for pool in pools]

    inspect(0)
    for cut, event in enumerate(word['program'], 1):
        op, name = event[:2]
        operations[op] += 1
        if op == 'transport':
            _, _, old, new, paid = event
            before, after = frame(tuple(old)), frame(tuple(new))
            need(frames[name] == before, 'transport entry frame')
            need(before <= after or after <= before, 'nested transport')
            need(type(paid) is int and paid == abs(len(new) - len(old)) and paid > 0,
                 'transport rank')
            frames[name] = after
            profile[paid] += 1
        elif op == 'zero':
            need(name == 'C' and name not in state, 'owned private allocation')
            state[name] = (0,) * 280
            frames[name] = frame(tuple(event[2]))
        elif op == 'erase':
            need(name == 'C' and frames[name] == frame(tuple(event[2])), 'owned private discard')
            del state[name], frames[name]
        elif op == 'copy':
            _, _, source, chart = event
            need(name == 'C' and not any(state[name]), 'copy into owned zero')
            need(frames[name] == frames[source] == frame(tuple(chart)), 'copy chart')
            state[name] = state[source]
        else:
            need(op == 'add', 'known operation')
            _, _, source, weight, chart = event
            need(name != source and frames[name] == frames[source] == frame(tuple(chart)), 'add chart')
            factor = Q(weight)
            scaled = [factor.numerator * x for x in state[source]]
            need(all(x % factor.denominator == 0 for x in scaled), 'denominator-eight lattice')
            state[name] = tuple(x + y // factor.denominator for x, y in zip(state[name], scaled))
        inspect(cut)
    need(len(word['program']) == 4058 and set(state) == set(names), 'full trace closure')
    for name in names:
        expected = list(initial[name])
        if name.startswith('Y'):
            target = int(name[1:])
            for source in range(104):
                expected[source] += sum(a * b for a, b in zip(ports[target], ports[source]))
        need(state[name] == tuple(expected), 'arbitrary-input endpoint ' + name)
        need(frames[name] == frame(tuple(word['final_frames'][name])), 'final frame ' + name)
    need(dict(profile) == {1: 1074, 2: 58, 3: 86, 4: 104, 5: 48, 6: 24, 7: 8, 8: 8},
         'unchanged local paid profile')
    need(set(snapshots) == desired, 'contact absent or self-contact')
    return checkpoints, snapshots, len(observed), dict(profile)


def lower_bound(pools, ports):
    union, operators = {}, {}
    for target, pool in enumerate(pools):
        for coeff in sorted(pool):
            add_basis(union, coeff)
            add_basis(operators, [x * y for x in ports[target] for y in coeff])
    u = list(union.values())
    e = list(operators.values())
    equations = [[sum(row[i] * op[i * 8 + j] for i in range(8)) for op in e]
                 for row in u for j in range(8)]
    rhs = [row[j] for row in u for j in range(8)]
    possible = solvable(equations, rhs)
    # I-M fixes ker(U). Equality rank(I-M)=8-rank(U) forces U M=U.
    return 104 - len(u) + (not possible), len(u), len(e), possible


def upper_bound(terms, snapshots, ports, start):
    a = [[Q(0)] * 8 for _ in ports]
    seen = set()
    for target, cut, register, weight in terms:
        need(type(target) is int and 0 <= target < 104 and type(cut) is int and 0 <= cut <= start,
             'upper contact index or future cut')
        key = target, cut, register
        need(key not in seen and key in snapshots, 'duplicate or unavailable upper contact')
        seen.add(key)
        need(isinstance(weight, str) and Q(weight) != 0, 'nonzero rational contact weight')
        a[target] = [x + Q(weight) * y for x, y in zip(a[target], snapshots[key])]
    matrix = [[Q(i == j) - sum(ports[t][i] * a[t][j] for t in range(104))
               for j in range(8)] for i in range(8)]
    small = rank(matrix)
    # Independently measure the actual 104-source correction-row rank.
    correction = [[Q(t == s) - Q(sum(ports[t][j] * ports[s][j] for j in range(8)), 8)
                   + 12 * sum(a[t][j] * ports[s][j] for j in range(8))
                   for s in range(104)] for t in range(104)]
    large = rank(correction)
    need(large == 96 + small, 'small/large rank identity')
    return large


def sources():
    values = {}
    for item in read(HERE / 'SOURCES.json')['files']:
        if item['usage'] != 'input':
            continue
        path = ROOT / item['path']
        need(hashlib.sha256(path.read_bytes()).hexdigest() == item['sha256'], 'input hash ' + item['path'])
        values[path.name] = read(path)
    return values


def run(certificate=None):
    data = sources()
    ports = geometry(data['P104-FIXTURE.json']['section4_explicit_P104'])
    certificate = read(HERE / 'WITNESS.json') if certificate is None else certificate
    need(set(certificate) == {'schema', 'witnesses'} and certificate['schema'] == 'p104-prefix-minrank/1',
         'certificate schema')
    witnesses = certificate['witnesses']
    need([x['cut'] for x in witnesses] == [x[0] for x in INTERVALS[1:]], 'witness cut coverage')
    wanted = [tuple(term[:3]) for item in witnesses for term in item['terms']]
    pools, snaps, count, profile = replay(data['LOWRANK-WITNESS.json'], ports, wanted)
    results = []
    for index, (start, end, expected) in enumerate(INTERVALS):
        low, row_rank, operator_rank, possible = lower_bound(pools[end], ports)
        high = 104 if index == 0 else upper_bound(witnesses[index - 1]['terms'], snaps, ports, start)
        need(low == high == expected, 'interval does not have matching exact bounds')
        results.append(dict(start=start, end=end, minimum=low, union_rank_at_end=row_rank,
                            operator_rank_at_end=operator_rank, projector_feasible_at_end=possible))
    return dict(schema='p104-prefix-minrank-result/1', status='PASS_P104_EARLY_PREFIX_MINRANK',
                cuts_replayed=4059, boundary_columns=280, distinct_target_snapshots=count,
                intervals=results, local_profile={str(k): v for k, v in sorted(profile.items())},
                scope='Rational unchanged-trace pooled snapshots only; no chronological correction or paid cost result.')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    need(args.out is None or not args.out.exists(), 'output already exists')
    result = run()
    need(result == read(HERE / 'RESULT.json'), 'exact receipt mismatch')
    if args.out:
        with args.out.open('x', encoding='utf-8') as handle:
            json.dump(result, handle, indent=2, sort_keys=True)
            handle.write('\n')
    print(result['status'], 'intervals=6 cuts=4059 columns=280')


if __name__ == '__main__':
    main()
