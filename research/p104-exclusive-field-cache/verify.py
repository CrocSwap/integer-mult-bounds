#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Ali Romman with substantial OpenAI Codex assistance.
"""Check the exclusive-owner invariant, all-D bill and literal cache execution."""
import argparse
from collections import Counter
import copy
from fractions import Fraction
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent


def require(ok, message):
    if not ok:
        raise ValueError(message)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def authenticate():
    for row in json.loads((HERE / 'SOURCES.json').read_text())['files']:
        if row['usage'] == 'input':
            require(hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256'], 'main source pin')
    for row in json.loads((HERE / 'ORIGINS.json').read_text()):
        raw = (HERE / row['path']).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == row['sha256'], 'origin source pin')
        require(hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == row['git_blob'], 'origin blob pin')


def symbolic(word, events, policy):
    """Track exclusive authority without the optimizer's transition function."""
    slots = [-1, -1]
    alive = set(range(word['public']))
    on_owner = set(alive)
    states, stats = [], Counter()
    for event, actions in zip(events, policy['actions']):
        states.append(tuple(slots))
        op = event[0]
        if op in ('ADD', 'COPY'):
            stats['hits_' + str(sum(f in slots for f in event[1:3]))] += 1
        for acquire, bank, field in actions:
            require(field in alive and bank in (0, 1), 'live transfer field')
            if acquire:
                require(slots[bank] == -1 and field in on_owner, 'exclusive owner acquisition')
                on_owner.remove(field)
                slots[bank] = field
                stats['loads'] += 1
            else:
                require(slots[bank] == field and field not in on_owner, 'exclusive cache eviction')
                on_owner.add(field)
                slots[bank] = -1
                stats['evictions'] += 1
        if op in ('ADD', 'COPY'):
            require(event[1] != event[2] and all(f in slots for f in event[1:3]), 'resident operands')
        else:
            require(slots == [-1, -1] and on_owner == alive, 'complete external owner')
            stats['flush_boundaries'] += 1
            if op == 'INIT':
                require(event[1] not in alive, 'fresh owned field')
                alive.add(event[1]); on_owner.add(event[1])
            elif op == 'CLEAR':
                require(event[1] in alive and event[1] >= word['public'], 'live owned clear')
                alive.remove(event[1]); on_owner.remove(event[1])
            elif op in ('SCALE', 'MOVE'):
                require(event[1] in alive, 'live external field')
        resident = {f for f in slots if f >= 0}
        require(not (resident & on_owner) and resident | on_owner == alive, 'complete owner partition')
        require(len(resident) == sum(f >= 0 for f in slots), 'unique cached owner')
    require(slots == [-1, -1] and alive == set(range(word['public'])), 'final ownership')
    return states, dict(sorted(stats.items()))


def circuit(gates, values, width=64):
    bits = [(v >> j) & 1 for v in values for j in range(width)] + [0]
    for gate in gates:
        bits[gate[-1]] ^= int(all(bits[w] for w in gate[:-1]))
    require(bits[-1] == 0, 'logical carry return')
    return tuple(sum(bits[b * width + j] << j for j in range(width)) for b in range(2))


def arithmetic(event, reference):
    op = event[0]
    if op in ('ADD', 'COPY'):
        t, s = event[1:3]
        if op == 'COPY':
            require(reference[t] == (0, 0), 'COPY clean target')
            result = reference[s]
        else:
            c = Fraction(event[3])
            result = tuple(x + c * y for x, y in zip(reference[t], reference[s]))
        require(all(Fraction(v).denominator == 1 and -(1 << 63) < v < (1 << 63) for v in result), 'exact signed record')
        reference[t] = tuple(map(int, result))
    elif op == 'SCALE':
        result = tuple(Fraction(event[2]) * v for v in reference[event[1]])
        require(all(v.denominator == 1 and -(1 << 63) < v < (1 << 63) for v in result), 'exact SCALE record')
        reference[event[1]] = tuple(map(int, result))


def whole_word(events, policy, circuits, owners):
    """Execute real scalar gates with explicit native-grid and reset stubs."""
    mask = (1 << 64) - 1
    reference = [(32 * (f % 31 - 15), 32 * ((7 * f) % 29 - 14)) for f in range(owners)]
    data = [tuple(v & mask for v in pair) for pair in reference]
    slots, buffers = [-1, -1], [(0, 0), (0, 0)]
    gate_calls = 0
    digest = hashlib.sha256()
    for index, (event, actions) in enumerate(zip(events, policy['actions'])):
        for acquire, bank, field in actions:
            if acquire:
                require(slots[bank] == -1 and buffers[bank] == (0, 0), 'clean abstract acquisition')
                buffers[bank], data[field], slots[bank] = data[field], (0, 0), field
            else:
                require(slots[bank] == field and data[field] == (0, 0), 'zero abstract owner slot')
                data[field], buffers[bank], slots[bank] = buffers[bank], (0, 0), -1
        op = event[0]
        if op in ('ADD', 'COPY'):
            t, s = (slots.index(f) for f in event[1:3])
            target, source = [], []
            for component in (0, 1):
                pair = circuit(circuits[(op, str(event[3]))], (buffers[t][component], buffers[s][component]))
                target.append(pair[0]); source.append(pair[1]); gate_calls += 1
            buffers[t], buffers[s] = tuple(target), tuple(source)
            arithmetic(event, reference)
        elif op == 'SCALE':
            require(slots == [-1, -1], 'abstract SCALE flush')
            data[event[1]] = circuit(circuits[(op, str(event[2]))], data[event[1]])
            gate_calls += 1
            arithmetic(event, reference)
        else:
            require(slots == [-1, -1], 'abstract external flush')
            if op == 'MOVE':
                reference[event[1]] = tuple(32 * ((index * 13 + c * 7 + event[1]) % 61 - 30) for c in (0, 1))
                data[event[1]] = tuple(v & mask for v in reference[event[1]])
            elif op in ('INIT', 'CLEAR'):
                reference[event[1]] = data[event[1]] = (0, 0)
        resolved = list(data)
        for field, values in zip(slots, buffers):
            if field >= 0:
                require(data[field] == (0, 0), 'no stale abstract owner copy')
                resolved[field] = values
        require(resolved == [tuple(v & mask for v in pair) for pair in reference], 'complete scalar prefix')
        for pair in resolved:
            for value in pair:
                digest.update(value.to_bytes(8, 'little'))
    return dict(events=len(events) - 1, scalar_circuit_calls=gate_calls, all_prefix_owner_records=owners * len(events), sha256=digest.hexdigest())


def physical_windows(F, B, T, events, policy, states, routes, circuits, costs, owners, dimension):
    """Run actual source windows from their complete valid owner/cache states."""
    width, length = 64, 128 * dimension
    selected = {}
    for i, event in enumerate(events):
        if event[0] in ('ADD', 'COPY', 'SCALE'):
            key = (event[0], str(event[2] if event[0] == 'SCALE' else event[3]))
            selected.setdefault(key, i)
        if event[0] in ('ADD', 'COPY'):
            hits = sum(f in states[i] for f in event[1:3])
            selected.setdefault(('cache_hits', hits), i)
        elif event[0] in ('MOVE', 'INIT', 'CLEAR'):
            selected.setdefault(('boundary', event[0]), i)
    totals = Counter()
    phase_counts = Counter()
    state = F.START
    heads = []
    for event, actions in zip(events, policy['actions']):
        heads.append(state[1])
        order = tuple(map(tuple, actions))
        state = next(end for end, _, seq in F.edges(state, event, width, costs, B) if seq == order)
    starts = sorted(set(selected.values()))
    for start in starts:
        slots = states[start]
        reference = [[((f * 37 + r * 13 + 11) * 32) & ((1 << width) - 1) for r in range(2 * dimension)] for f in range(owners)]
        owner_values = [list(row) for row in reference]
        ribbon_values = []
        for field in slots:
            ribbon_values.append(list(reference[field]) if field >= 0 else [0] * (2 * dimension))
            if field >= 0:
                owner_values[field] = [0] * (2 * dimension)
        owner = T.Tape((v >> j) & 1 for row in owner_values for v in row for j in range(width))
        owner.head = 0 if heads[start] == -1 else (heads[start] + 1) * length - 1
        ribbons = [T.Tape((v >> j) & 1 for v in row for j in range(width)) for row in ribbon_values]
        carry = T.Tape((0,))
        state = (slots, heads[start])
        for index in range(start, min(start + 5, len(events))):
            event, actions = events[index], policy['actions'][index]
            op = event[0]
            order = tuple(map(tuple, actions))
            [(expected_state, (a, b), _)] = [row for row in F.edges(state, event, width, costs, B) if row[2] == order]
            before = sum(sum(t.counts.values()) for t in [owner, *ribbons, carry])
            slots = F.execute(owner, ribbons, carry, slots, event, width, dimension, actions, routes, B)
            charge = sum(sum(t.counts.values()) for t in [owner, *ribbons, carry]) - before
            require(charge == a * dimension + b, 'literal complete cache charge')
            require(slots == expected_state[0], 'literal cache labels')
            end_head = 0 if expected_state[1] == -1 else (expected_state[1] + 1) * length - 1
            require(owner.head == end_head and all(t.head == 0 for t in [*ribbons, carry]), 'literal cache heads')
            if op in ('ADD', 'COPY'):
                t, s = event[1:3]
                for r in range(2 * dimension):
                    reference[t][r], reference[s][r] = circuit(circuits[(op, str(event[3]))], (reference[t][r], reference[s][r]))
                phase_counts['hits_' + str(sum(f in state[0] for f in event[1:3]))] += 1
            elif op == 'SCALE':
                for j in range(dimension):
                    reference[event[1]][2*j:2*j+2] = circuit(circuits[(op, str(event[2]))], reference[event[1]][2*j:2*j+2])
                phase_counts['SCALE_flush'] += 1
            else:
                phase_counts['external_flush'] += 1
                require(slots == (-1, -1), 'physical complete external owner')
            expected_owner = [list(row) for row in reference]
            for bank, field in enumerate(slots):
                expected_ribbon = reference[field] if field >= 0 else [0] * (2 * dimension)
                require(ribbons[bank].snapshot() == tuple((v >> bit) & 1 for v in expected_ribbon for bit in range(width)), 'physical resident field')
                if field >= 0:
                    expected_owner[field] = [0] * (2 * dimension)
            require(owner.snapshot() == tuple((v >> bit) & 1 for row in expected_owner for v in row for bit in range(width)), 'physical exclusive owner values')
            require(carry.snapshot() == (0,), 'physical carry return')
            state = expected_state
            if op not in ('ADD', 'COPY', 'SCALE'):
                break
        for name in ('moves', 'reads', 'writes'):
            totals[name] += sum(t.counts[name] for t in [owner, *ribbons, carry])
    return dict(windows=len(starts), phases=dict(sorted(phase_counts.items())), operations=dict(totals))


def reject(action, expected):
    try:
        action()
    except ValueError as error:
        require(expected in str(error), 'wrong rejection reason: ' + str(error))
        return
    raise ValueError('control accepted: ' + expected)


def main(write=False):
    authenticate()
    F = load('exclusive_cache', HERE / 'field_cache.py')
    B = load('field_staging', HERE / 'inputs/batched.py')
    S = load('coordinate_staging', HERE / 'inputs/staging.py')
    C = load('bit_control_cache', HERE / 'inputs/cache.py')
    T = load('source_tape', ROOT / 'research/rank7-paired-scale-routing/route.py')
    word = json.loads(gzip.decompress((ROOT / 'research/p104-helper470-twin-rung-removal/WORD.json.gz').read_bytes()))
    S.plan(word, 1, 64)
    events = word['program'] + [['EXIT']]
    rows = json.loads(gzip.decompress((HERE / 'inputs/CIRCUITS64.json.gz').read_bytes()))
    local_certs = json.loads(gzip.decompress((HERE / 'inputs/CERTIFICATES.json.gz').read_bytes()))
    circuits, routes, costs = {}, {}, {}
    for (op, c, gates), cert in zip(rows, local_certs):
        key = (op, c)
        circuits[key] = gates
        routes[key] = C.compile_route(64, gates, cert)
        costs[key] = sum(C.counts(routes[key]).values())
    require(len(routes) == 43, 'all templates')
    policy_path = HERE / 'POLICY.json.gz'
    if write:
        one, two = (F.solve(events, 64, d, costs, B) for d in (1, 2))
        policy = F.affine_certificate(one, two)
        policy_path.write_bytes(gzip.compress(json.dumps(policy, separators=(',', ':')).encode(), mtime=0))
    policy = json.loads(gzip.decompress(policy_path.read_bytes()))
    a, b = F.check(events, 64, costs, B, policy)
    states, stats = symbolic(word, events, policy)
    baseline = json.loads((HERE / 'inputs/BASELINE.json').read_text())
    base_cert = json.loads(gzip.decompress((HERE / 'inputs/AFFINE.json.gz').read_bytes()))
    ba, bb = B.check_affine(B.calls(word, 1, 64), 64, base_cert)
    local_bill = sum((1 if e[0] == 'SCALE' else 2) * costs[(e[0], str(e[2] if e[0] == 'SCALE' else e[3]))]
                     for e in events if e[0] in ('ADD', 'COPY', 'SCALE'))
    transfers = sum((4 if e[0] == 'SCALE' else 8) * 64 for e in events if e[0] in ('ADD', 'COPY', 'SCALE'))
    require((ba + local_bill + 6 * transfers, bb) == tuple(baseline['combined_physical'][k] for k in ('D', 'constant')), 'complete baseline bill')
    delta_a, delta_b = baseline['combined_physical']['D'] - a, baseline['combined_physical']['constant'] - b
    require(delta_a > 0 and delta_a + delta_b > 0, 'strict saving for all D')
    owners = word['public'] + word['owned_fields']
    whole = whole_word(events, policy, circuits, owners)
    physical = {str(d): physical_windows(F, B, T, events, policy, states, routes, circuits, costs, owners, d) for d in (1, 2)}
    require(all(x['phases'].get('hits_2', 0) and x['phases'].get('hits_1', 0) and x['phases'].get('hits_0', 0)
                and x['phases'].get('SCALE_flush', 0) and x['phases'].get('external_flush', 0) for x in physical.values()), 'physical policy coverage')
    bad = copy.deepcopy(policy)
    bad['total'][0] += 1
    reject(lambda: F.check(events, 64, costs, B, bad), 'attaining all-D')
    bad = copy.deepcopy(policy)
    bad['layers'][2][0][2] += 1
    reject(lambda: F.check(events, 64, costs, B, bad), 'edge inequality')
    bad = copy.deepcopy(policy)
    i = next(i for i, actions in enumerate(bad['actions']) if any(a[0] == 1 for a in actions))
    j = next(j for j, action in enumerate(bad['actions'][i]) if action[0] == 1)
    bad['actions'][i].pop(j)
    reject(lambda: symbolic(word, events, bad), 'resident operands')
    bad = copy.deepcopy(policy)
    i = next(i for i, e in enumerate(events) if e[0] not in ('ADD', 'COPY') and bad['actions'][i])
    bad['actions'][i].pop()
    reject(lambda: symbolic(word, events, bad), 'complete external owner')
    tape = T.Tape([0] * 128)
    reject(lambda: F.execute(tape, [tape, T.Tape([0] * 128)], T.Tape((0,)), (-1, -1), ['EXIT'], 64, 1, [], routes, B), 'four distinct tapes')
    summary = dict(schema=1, width=64, source_events=len(word['program']), all_positive_D_cost=dict(D=a, constant=b),
                   baseline_cost=baseline['combined_physical'], saved_operations=dict(D=delta_a, constant=delta_b),
                   owner_bits_per_dimension=102272, clean_staging_bits_per_dimension=256, clean_carry_bits=1,
                   finite_control_bits=2, tapes=4, unimplemented_reset_bits_per_dimension=7936,
                   all_D_certificate_states=sum(map(len, policy['layers'])), maximum_layer_states=max(map(len, policy['layers'])),
                   cache_statistics=stats, whole_word_grid_stub=whole, physical=physical, negative_controls=5)
    result_path = HERE / 'RESULT.json'
    if write:
        result_path.write_text(json.dumps(summary, indent=2) + '\n')
    require(summary == json.loads(result_path.read_text()), 'retained result')
    print('PASS_P104_EXCLUSIVE_FIELD_CACHE', summary['all_positive_D_cost'], 'saving', summary['saved_operations'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    main(parser.parse_args().write)
