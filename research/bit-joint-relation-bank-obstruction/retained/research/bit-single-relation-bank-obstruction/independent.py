"""Check the receiver certificate with sets and prefix ranks."""
from collections import Counter, defaultdict
from fractions import Fraction
from hashlib import sha256
import json


def require(ok, message):
    if not ok:
        raise ValueError(message)


def insert(vector, basis):
    value = set(vector)
    while value:
        key = min(value)
        if key not in basis:
            basis[key] = value
            return True
        value.symmetric_difference_update(basis[key])
    return False


def rank(vectors):
    basis = {}
    for vector in vectors:
        insert(vector, basis)
    return len(basis)


def replay(word, backward):
    n = word['public']
    start, finish = (word['final'], word['start']) if backward else (word['start'], word['final'])
    state = {i: (chart, {i}) for i, chart in enumerate(start)}
    banks = defaultdict(dict)
    for i, chart in enumerate(start):
        banks[chart][-1-i] = {i}
    moves = {}
    length = len(word['program'])
    clocks = range(length-1, -1, -1) if backward else range(length)
    for clock, index in enumerate(clocks):
        event = word['program'][index]
        op, a = event[:2]
        if (op == 'INIT' and not backward) or (op == 'CLEAR' and backward):
            require(a >= n and a not in state, 'owned introduction')
            state[a] = event[2], set()
        elif (op == 'CLEAR' and not backward) or (op == 'INIT' and backward):
            require(a >= n and state[a][0] == event[2], 'owned exit')
            del state[a]
        elif op == 'ADD':
            b, chart = event[2:]
            require(a != b and state[a][0] == state[b][0] == chart, 'ADD chart')
            target, donor = (b, a) if backward else (a, b)
            state[target][1].symmetric_difference_update(state[donor][1])
        elif op == 'SWAP':
            b = event[2]
            state[a], state[b] = state[b], state[a]
        else:
            require(op == 'MOVE', 'operation')
            source, target = event[2:][::-1] if backward else event[2:]
            require(state[a][0] == source, 'MOVE chart')
            state[a] = target, state[a][1]
            banks[target][clock] = set(state[a][1])
            moves[clock] = source, target
    require(set(state) == set(range(n)), 'complete public inventory')
    for i in range(n):
        expected = {i}
        if backward and i < 111:
            expected.add(i+111)
        if not backward and 111 <= i < 222:
            expected.add(i-111)
        require(state[i] == (finish[i], expected), 'public endpoint')
    return start, finish, banks, moves


def rational_rank(rows):
    pivots = {}
    for row in rows:
        v = [Fraction(x) for x in row]
        for key, donor in pivots.items():
            coefficient = v[key]
            v = [x-coefficient*y for x, y in zip(v, donor)]
        if any(v):
            key = next(i for i, x in enumerate(v) if x)
            scale = v[key]
            pivots[key] = [x/scale for x in v]
    return len(pivots)


def orthogonal(left, right):
    return all(sum(Fraction(a)*Fraction(b) for a, b in zip(x, y)) == 0 for x in left for y in right)


def frames(word):
    fs = word['frames']
    for frame in fs.values():
        d, b, a = frame['dim'], frame['B'], frame['A']
        require(len(b) == d and len(a) == 8-d and all(len(row) == 8 for row in b+a), 'frame dimensions')
        require(rational_rank(b) == d and rational_rank(a) == 8-d and orthogonal(b, a), 'rational frame')
    pairs = {(e[2], e[3]) for e in word['program'] if e[0] == 'MOVE'}
    for left, right in pairs:
        x, y = fs[str(left)], fs[str(right)]
        small, large = (x, y) if x['dim'] < y['dim'] else (y, x)
        require(small['dim'] < large['dim'] and orthogonal(small['B'], large['A']), 'strict nested MOVE')
    return len(pairs)


def xor_rows(bank, keys):
    result = set()
    require(len(set(keys)) == len(keys), 'distinct witness tokens')
    for key in keys:
        require(key in bank, 'same-chart witness')
        result.symmetric_difference_update(bank[key])
    return result


def span_with_witness(basis):
    values = {frozenset(): set()}
    for row in basis:
        signal, witness = frozenset(row['signal']), set(row['relation'])
        values.update({value ^ signal: tags ^ witness for value, tags in list(values.items())})
    del values[frozenset()]
    return values


def validate_group(group, initial, final, banks, moves, dimensions):
    a, d = group['entrance'], group['exit']
    roles = {i for i in range(222, len(initial)) if (initial[i], final[i]) == (a, d)}
    lost = abs(dimensions[a]-dimensions[d])
    require(set(group['roles']) == roles and group['lost_rank'] == lost, 'productive target debit')
    require(group['checked_receivers'] == len(banks)-1, 'all receiver charts')
    supplied = {row['chart']: row['basis'] for row in group['spaces']}
    require(len(supplied) == len(group['spaces']) and set(supplied) <= set(banks)-{a}, 'unique receiver spaces')
    exceptional, witnesses = set(), {}
    for chart, bank in banks.items():
        if chart == a:
            continue
        dimension = len(bank)-rank(value-roles for value in bank.values())
        basis = supplied.get(chart, [])
        require(len(basis) == dimension and rank(row['signal'] for row in basis) == dimension, 'complete clean dimension')
        for row in basis:
            signal = set(row['signal'])
            require(signal and signal <= roles and signal == xor_rows(bank, row['relation']), 'exact clean witness')
        if chart != d:
            require(dimension <= 4, 'small nonterminal space')
            witnesses[chart] = span_with_witness(basis)
            exceptional.update(witnesses[chart])
    terminal = supplied[d]
    require(len(terminal) == len(roles), 'full terminal space')
    prefix, last_keys = {}, []
    for key, value in banks[d].items():
        if not insert(value-roles, prefix):
            last_keys.append(key)
    paid_rank = lambda key: abs(dimensions[moves[key][0]]-dimensions[moves[key][1]])
    require(last_keys == group['terminal_pivots'] and all(key >= 0 for key in last_keys), 'causal terminal pivots')
    require(max(map(paid_rank, last_keys)) == group['terminal_rank_max'] <= lost, 'terminal rank bound')
    cases = {frozenset(row['signal']): row for row in group['exceptional_cases']}
    require(len(cases) == len(group['exceptional_cases']) and set(cases) == exceptional, 'complete exceptional union')
    for signal, case in cases.items():
        expected_charts = {c for c, table in witnesses.items() if signal in table} | {d}
        hits = {hit['chart']: hit for hit in case['hits']}
        require(set(hits) == expected_charts and len(hits) == len(case['hits']), 'complete receiver hits')
        for chart, hit in hits.items():
            tags = hit['relation']
            require(xor_rows(banks[chart], tags) == set(signal), 'exact removal relation')
            require(hit['pivot'] == max(tags) >= 0 and hit['rank'] == paid_rank(hit['pivot']), 'earlier-bank reconstruction')
        require(sum(hit['rank'] for hit in hits.values()) < lost, 'strict saved rank deficit')
    require(lost**99 > (lost-1)**100, 'uniform power inequality')
    return len(cases)


def validate_orientation(word, certificate, backward):
    initial, final, banks, moves = replay(word, backward)
    dimensions = {int(c): f['dim'] for c, f in word['frames'].items()}
    require(all(rank(bank.values()) == len(bank) for bank in banks.values()), 'independent receiver rows')
    rows = [[c, [[key, str(sum(1 << i for i in value))] for key, value in bank.items()]] for c, bank in sorted(banks.items())]
    require(sha256(json.dumps(rows, separators=(',', ':')).encode()).hexdigest() == certificate['bank_rows_sha256'], 'all literal bank values')
    groups = {(initial[i], final[i]) for i in range(222, len(initial))}
    require({(g['entrance'], g['exit']) for g in certificate['groups']} == groups and len(certificate['groups']) == len(groups), 'all helper groups')
    total = sum(validate_group(g, initial, final, banks, moves, dimensions) for g in certificate['groups'])
    require(total == certificate['exceptional_directions'], 'exception count')
    require(certificate['paid'] == len(moves) == 2871 and certificate['receiver_charts'] == len(banks), 'bank count')
    require(certificate['retained_rows'] == sum(map(len, banks.values())), 'all retained rows')
    return initial, final, banks, moves, dimensions


def invoice(word, caller):
    dimensions = {int(c): f['dim'] for c, f in word['frames'].items()}
    paid, targets = Counter(), Counter()
    calls = 0
    for event in caller['events']:
        if event[0] == 'LOCAL':
            calls += 1
            for gate in word['program']:
                if gate[0] == 'MOVE':
                    paid[abs(dimensions[gate[2]]-dimensions[gate[3]])] += 1
            for i in range(222, word['public']):
                targets[abs(dimensions[word['start'][i]]-dimensions[word['final'][i]])] += 1
        if event[0] == 'QUERY':
            paid[1] += caller['ports']
        if event[0] == 'IDLE_ONE':
            paid[7*len(event[2])] += caller['ports']
    for root in caller['diagonal']:
        targets[root['q']+7*len(root['stages'])] += caller['ports']
    return dict(paid=dict(sorted(paid.items())), targets=dict(sorted(targets.items())), calls=calls,
                paid_count=sum(paid.values()), target_count=sum(targets.values()),
                rank_surplus=sum(r*n for r,n in targets.items())-sum(r*n for r,n in paid.items()))
