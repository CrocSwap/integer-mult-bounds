"""Classify all Type A late-mask transpositions at a single fixed cut."""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations
from json import dumps, loads
from pathlib import Path
from signal import SIGALRM, alarm, signal

ROOT = Path(__file__).resolve().parent
PINS = {
    'inputs/CALLER.json': '255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc',
    'inputs/R178-REVERSE.json': 'ad9bbc64a9b866a89f48f1fac0b0346c18105c4b69e62aa41a9cd5575e5c5942',
}
HEAD = 'aaeec8c0acf01e99a5f331ef363a698d9c084ace'
CALLER = '07a76c5e2738882c0cb322278e56f6cae3c9885d'
CUT = 1741
N = 36


def read(name):
    raw = (ROOT / name).read_bytes()
    assert sha256(raw).hexdigest() == PINS[name]
    return loads(raw)


def identity():
    return [[Q(i == j) for j in range(N)] for i in range(N)]


def expand(entries):
    out = [[Q(0)] * N for _ in range(N)]
    for i, j, value in entries:
        assert not out[i][j] and Q(value)
        out[i][j] = Q(value)
    return out


def product(left, right):
    columns = list(zip(*right, strict=True))
    return [[sum(x*y for x, y in zip(row, col, strict=True) if x and y)
             for col in columns] for row in left]


def solve(left, right):
    augmented = [a + b for a, b in zip(left, right, strict=True)]
    for j in range(N):
        i = next(i for i in range(j, N) if augmented[i][j])
        augmented[j], augmented[i] = augmented[i], augmented[j]
        pivot = augmented[j][j]
        augmented[j] = [x/pivot for x in augmented[j]]
        for i, row in enumerate(augmented):
            if i != j and row[j]:
                multiplier = row[j]
                augmented[i] = [x - multiplier*y for x, y in zip(row, augmented[j], strict=True)]
    assert [row[:N] for row in augmented] == identity()
    return [row[N:] for row in augmented]


def exchange(i, a, b):
    if i == a:
        return b
    if i == b:
        return a
    return i


def noncommuting_entries(h, a, b):
    result = []
    for i in range(N):
        for j in range(N):
            xh = h[exchange(i, a, b)][j]
            hx = h[i][exchange(j, a, b)]
            if xh != hx:
                result.append([i, j, str(xh), str(hx)])
    return result


def timeout(*_):
    raise TimeoutError('30-second runner cap')


def main():
    assert __debug__
    signal(SIGALRM, timeout)
    alarm(30)
    c = read('inputs/CALLER.json')
    receipt = read('inputs/R178-REVERSE.json')
    assert (receipt['benchmark'], receipt['caller'], receipt['cut']) == (HEAD, CALLER, CUT)
    assert receipt['pins'] == {'inputs/CALLER.json': PINS['inputs/CALLER.json']}
    assert receipt['central_signs'] == [1, -1] and receipt['basis_columns'] == N
    tape = c['events']
    assert len(tape) == 4783 and tape[CUT] == ['A', 'ADD', 10, 0, '2']
    for start, end, stages, queries in ((0, CUT, range(1, 9), 4),
                                         (CUT, len(tape), range(9, 18), 0)):
        events = tape[start:end]
        assert sorted(e[1] for e in events if e[0] == 'J') == list(stages)
        assert sum(e[:2] == ['A', 'QUERY'] for e in events) == queries
        assert all(set(e[3]) <= set(stages) for e in events if e[:2] == ['A', 'IDLE_ONE'])
    d = c['types']['A']['diagonal']
    assert len(d) == N and all(row[:2] == [-1, 0] for row in d)
    counts = [(sum(row[2:10]), sum(row[10:])) for row in d]
    gp = expand(receipt['prefix_plus'])
    gm = expand(receipt['prefix_minus'])
    h = solve(gm, gp)
    assert product(gm, h) == gp
    assert product(h, solve(h, identity())) == identity()
    cases = []
    stats = Counter()
    for a, b in combinations(range(N), 2):
        e_a, l_a = counts[a]
        e_b, l_b = counts[b]
        old = [1 + 8*(e_a + l_a), 1 + 8*(e_b + l_b)]
        new = [1 + 8*(e_a + l_b), 1 + 8*(e_b + l_a)]
        assert sum(old) == sum(new)
        old_spread = abs(old[0] - old[1])
        new_spread = abs(new[0] - new[1])
        price = ('improves' if new_spread < old_spread else
                 'ties' if new_spread == old_spread else 'worsens')
        case = {'pair': [a, b], 'old_ranks': old, 'new_ranks': new,
                'old_spread': old_spread, 'new_spread': new_spread, 'price': price}
        if price == 'improves':
            defects = noncommuting_entries(h, a, b)
            case['commuting'] = not defects
            case['commutator_nonzeros'] = len(defects)
            case['first_commutator_entry'] = defects[0] if defects else None
            stats['survivors' if not defects else 'excluded'] += 1
        stats[price] += 1
        cases.append(case)
    assert len(cases) == 630
    assert stats['survivors'] + stats['excluded'] == stats['improves']
    predecessor = next(case for case in cases if case['pair'] == [0, 9])
    assert predecessor['old_ranks'] == [137, 9] and predecessor['new_ranks'] == [73, 73]
    assert predecessor['price'] == 'improves' and not predecessor['commuting']
    assert not noncommuting_entries(identity(), 0, 9)
    alarm(0)
    print(dumps({'benchmark': HEAD, 'caller': CALLER, 'cut': CUT, 'pins': PINS,
                 'pair_cap': 630, 'runner_cap_seconds': 30, 'central_signs': [1, -1],
                 'rank_formula': '1+8*(early+late)', 'statistics': dict(stats),
                 'survivors': sorted((case for case in cases if case.get('commuting')),
                                     key=lambda case: (case['new_spread'] - case['old_spread'],
                                                       case['pair'])),
                 'case_results': cases}, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
