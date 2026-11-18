#!/usr/bin/env python3
"""Check the fixed-order snapshot allocation and its exact scalar execution.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter, defaultdict
from hashlib import sha1, sha256
from heapq import heappop, heappush
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parent
GRID = 530841600


def need(ok, message):
    if not ok:
        raise ValueError(message)


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def source():
    for pin in json.loads((ROOT/'PREDECESSOR.json').read_text())['files']:
        raw = (ROOT/'predecessor'/pin['path']).read_bytes()
        need(len(raw) == pin['bytes'] and sha256(raw).hexdigest() == pin['sha256'], 'source bytes')
        need(sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest() == pin['git_blob'], 'source Git blob')
    sys.path.insert(0, str(ROOT/'predecessor'))
    import network
    word = network.source_word()
    parent, net, changes = network.networks(word)
    need(len(parent.moves) == 6157 and len(net.moves) == 6142 and len(changes) == 15, 'source inventory')
    return word, net


def intervals(net, order):
    first = {~r: 0 for r in range(len(net.initial))}
    first.update({v: i for i, v in enumerate(order, 1)})
    last = first.copy()
    for i, v in enumerate(order, 1):
        for donor in net.forms[v]:
            need(first[donor] < i, 'causal order')
            last[donor] = i
    for v in range(net.first_output, net.first_output+len(net.final)):
        last[v] = len(order)+1
    return first, last


def allocate(first, last):
    free, active, assignments = [], [], []
    capacity = 0
    for v in sorted(first, key=lambda v: (first[v], v)):
        while active and active[0][0] < first[v]:
            _, slot = heappop(active)
            heappush(free, slot)
        if free:
            slot = heappop(free)
        else:
            slot = capacity
            capacity += 1
        assignments.append([v, slot])
        heappush(active, (last[v], slot))
    return capacity, assignments


def interval_check(first, last, capacity, assignments):
    need(len(assignments) == len(first), 'allocation inventory')
    slots = dict(assignments)
    need(slots.keys() == first.keys(), 'allocation tokens')
    groups = defaultdict(list)
    for v, slot in assignments:
        need(type(slot) is int and 0 <= slot < capacity, 'bank capacity')
        groups[slot].append((first[v], last[v], v))
    for group in groups.values():
        chain = sorted(group)
        need(all(a[1] < b[0] for a, b in zip(chain, chain[1:])), 'overlapping owners')
    # A difference sweep does not use the allocation heaps.
    delta = Counter()
    for v in first:
        delta[first[v]] += 1
        delta[last[v]+1] -= 1
    total = peak = 0
    cut = None
    for t, change in sorted(delta.items()):
        total += change
        if total > peak:
            peak, cut = total, t
    need(total == 0 and peak == capacity, 'sharp interval capacity')
    witness = sorted(v for v in first if first[v] <= cut <= last[v])
    need(len(witness) == capacity and len({slots[v] for v in witness}) == capacity, 'peak witness')
    return cut, witness


def expected_outputs(word):
    rows = [{r: GRID} for r in range(word['public'])]
    for port, x in enumerate(word['live']):
        y = x+112
        if port in word['hosted']['Dports']:
            rows[y] = {x: GRID, y: GRID}
        else:
            rows[x] = {x: GRID, y: -GRID}
            rows[y] = {x: GRID//2, y: GRID//2}
    for x, y in zip(word['hosted']['X2'], word['hosted']['Y2'], strict=True):
        rows[x] = {x: GRID, y: -GRID}
    return rows


def execute(word, net, order, capacity, assignments, fault=None):
    slots = dict(assignments)
    need(len(slots) == len(assignments) == len(net.forms)+len(net.initial), 'execution inventory')
    need(slots.keys() == net.forms.keys() | {~r for r in range(len(net.initial))}, 'execution tokens')
    banks = [None]*capacity
    remaining = Counter(d for form in net.forms.values() for d in form)
    counts = Counter()
    maximum = 0
    early = next(~r for r in range(len(net.initial)) if remaining[~r] > 1)

    def put(token, chart, row):
        nonlocal maximum
        slot = slots[token]
        need(0 <= slot < capacity and banks[slot] is None, 'live bank overwrite')
        banks[slot] = (token, chart, row)
        counts['snapshot_init'] += 1
        counts['live'] += 1
        maximum = max(maximum, counts['live'])

    def get(token):
        value = banks[slots[token]]
        need(value is not None and value[0] == token, 'wrong or retired owner')
        return value

    def retire(token):
        get(token)
        banks[slots[token]] = None
        counts['snapshot_clear'] += 1
        counts['live'] -= 1

    for r, chart in enumerate(net.initial):
        put(~r, chart, {r: GRID})
    for r in range(len(net.initial)):
        if not remaining[~r]:
            retire(~r)
    for node in order:
        paid = node in net.moves
        start, finish = net.moves[node] if paid else (net.final[node-net.first_output],)*2
        # The return bank is reserved before any donor is read.
        put(node, finish, {})
        row = {} if paid else get(node)[2]
        if paid:
            counts['accumulator_init'] += 1
        for donor, factor in sorted(net.forms[node].items()):
            _, chart, value = get(donor)
            need(chart == start, 'donor chart')
            for owner, x in value.items():
                term, remainder = divmod(factor.numerator*x, factor.denominator)
                need(remainder == 0, 'scalar division')
                new = row.get(owner, 0)+term
                if new:
                    row[owner] = new
                else:
                    row.pop(owner, None)
                counts['coefficient_products'] += 1
            counts['terms'] += 1
        if paid:
            banks[slots[node]] = (node, finish, row)
            counts['paid_returns'] += 1
            counts['accumulator_clear'] += 1
        # This point is after the row, child and both adapters have returned.
        for donor in net.forms[node]:
            remaining[donor] -= 1
            if remaining[donor] == 0:
                retire(donor)
            elif fault == 'early-retire' and donor == early:
                retire(donor)
        if not remaining[node] and (paid or fault == 'drop-output'):
            retire(node)
    expected = expected_outputs(word)
    for r, chart in enumerate(net.final):
        node = net.first_output+r
        _, actual_chart, row = get(node)
        need(actual_chart == chart and row == expected[r], 'public output')
        counts['public_installs'] += 1
    for r in range(len(net.final)):
        retire(net.first_output+r)
    need(all(x is None for x in banks) and counts['live'] == 0, 'complete retirement')
    need(all(x == 0 for x in remaining.values()), 'all reads consumed')
    counts.pop('live')
    counts['peak_snapshots'] = maximum
    return dict(counts)


def rejected(call, expected):
    try:
        call()
    except ValueError as error:
        need(str(error) == expected, 'wrong failure control: '+str(error))
        return expected
    raise ValueError('fault accepted')


def compute():
    word, net = source()
    order = net.schedule()
    first, last = intervals(net, order)
    capacity, assignments = allocate(first, last)
    cut, witness = interval_check(first, last, capacity, assignments)
    certificate = {'capacity': capacity, 'assignments': assignments, 'peak_event': cut,
                   'peak_node': order[cut-1], 'peak_tokens': witness}
    counts = execute(word, net, order, capacity, assignments)
    need(capacity == counts['peak_snapshots'] == 2425, 'pool peak')
    need(counts['snapshot_init'] == counts['snapshot_clear'] == 9144, 'snapshot reset count')
    need(counts['accumulator_init'] == counts['accumulator_clear'] == len(net.moves), 'accumulator resets')
    need(counts['coefficient_products'] == 8533666 and counts['terms'] == 169343, 'exact arithmetic coverage')
    collided = [pair[:] for pair in assignments]
    newborn = order[cut-1]
    other = next(v for v in witness if v != newborn)
    next(pair for pair in collided if pair[0] == newborn)[1] = dict(assignments)[other]
    controls = [rejected(lambda: execute(word, net, order, capacity, collided), 'live bank overwrite'),
                rejected(lambda: execute(word, net, order, capacity, assignments, 'early-retire'), 'wrong or retired owner'),
                rejected(lambda: execute(word, net, order, capacity, assignments, 'drop-output'), 'wrong or retired owner'),
                rejected(lambda: interval_check(first, last, capacity-1, assignments), 'bank capacity'),
                rejected(lambda: execute(word, net, order, capacity, assignments[:-1]), 'execution inventory')]
    final = net.first_output
    saved = net.forms[final]
    net.forms[final] = {d: -q for d, q in saved.items()}
    controls.append(rejected(lambda: execute(word, net, order, capacity, assignments), 'public output'))
    net.forms[final] = saved
    lifetimes = counts['snapshot_init']+counts['accumulator_init']+4
    result = {'status': 'PASS_BANKED_NATIVE_SNAPSHOT_REUSE', 'execution': counts,
              'pool_capacity': capacity, 'shared_accumulators': 1, 'scalar_scratch': 4,
              'private_homes': capacity+5, 'source_private_homes': 15290,
              'private_homes_saved': 15290-capacity-5,
              'raw_caller_homes': 16*(capacity+5), 'source_raw_caller_homes': 244640,
              'initializations_per_native': lifetimes, 'retirements_per_native': lifetimes,
              'reset_services_per_native': 2*lifetimes,
              'raw_reset_allowance': 16*(2*lifetimes+4*(len(order)+counts['terms'])),
              'paid_calls_unchanged': len(net.moves), 'public_outputs': len(net.final),
              'peak_event': cut, 'peak_node': order[cut-1], 'peak_witness_size': len(witness),
              'schedule_sha256': sha256(encoded(order)).hexdigest(),
              'certificate_sha256': sha256(encoded(certificate)).hexdigest(),
              'negative_controls': controls,
              'scope': 'Fixed row order and distinct immutable snapshots; no global storage minimum or kappa claim.'}
    need(lifetimes == 15290 and result['raw_reset_allowance'] == 11816384, 'unchanged reset allowance')
    return result, certificate


if __name__ == '__main__':
    result, certificate = compute()
    need(json.loads((ROOT/'ALLOCATION.json').read_text()) == certificate, 'retained allocation')
    need(json.loads((ROOT/'RESULT.json').read_text()) == result, 'retained result')
    print(json.dumps(result, indent=2, sort_keys=True))
