#!/usr/bin/env python3
"""Complete two-bank scalar policy with one credited resident SCALE2 edge."""
from fractions import Fraction
from itertools import permutations, product
import argparse
import gzip
import hashlib
import io
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
SOURCE_HASH = 'd9c3cedebf70439e9491e27ab21c9f3ab1638dd3be450217370f96217760d99d'
CASE_HASH = '6643eab23335c5aab85edf2599262d9020c5ce5e646d876e63c275747d8b16b8'
SCHEMA_HASH = '50ae780b73aff908bddb70d99438e7d2ec45d037b07fcccb63fc038948701e26'
START = (-1, -1, -1)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':')) + '\n').encode()


def unique(pairs):
    value = {}
    for key, item in pairs:
        require(key not in value, 'duplicate JSON key')
        value[key] = item
    return value


def bad_number(value):
    raise ValueError('noninteger JSON number: ' + value)


def parse(raw):
    return json.loads(raw, object_pairs_hook=unique, parse_float=bad_number, parse_constant=bad_number)


def decoded(path, cap):
    with gzip.GzipFile(fileobj=io.BytesIO(path.read_bytes())) as stream:
        raw = stream.read(cap + 1)
    require(len(raw) <= cap, 'decompressed byte cap')
    return parse(raw)


def authenticate():
    for name, expected in [('SOURCE-PINS.json', SOURCE_HASH), ('CASES.json', CASE_HASH),
                           ('SCHEMA.json', SCHEMA_HASH)]:
        require(sha((ROOT / name).read_bytes()) == expected, 'immutable ' + name)
    manifest = parse((ROOT / 'SOURCE-PINS.json').read_bytes())
    require(len(manifest['files']) == 15, '15 source objects')
    for row in manifest['files']:
        path = (ROOT / row['local_path']).resolve()
        require(path.parent == (ROOT / 'inputs').resolve(), 'source containment')
        raw = path.read_bytes()
        require(len(raw) == row['bytes'] and sha(raw) == row['sha256'], 'source bytes/SHA256')
        require(hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == row['git_blob'], 'source Git blob')
    return parse((ROOT / 'CASES.json').read_bytes())


def source_data(cases):
    cap = cases['limits']['input_decoded_bytes']
    word = decoded(ROOT / 'inputs/WORD.json.gz', cap)
    circuits = decoded(ROOT / 'inputs/CIRCUITS64.json.gz', cap)
    certs = decoded(ROOT / 'inputs/CERTIFICATES.json.gz', cap)
    require(len(circuits) == len(certs) == 43, '43 credited local templates')
    prices = {}
    for circuit, cert in zip(circuits, certs):
        key = (circuit[0], str(Fraction(circuit[1])))
        require(key not in prices and type(cert['total']) is int and cert['total'] >= 0, 'local price table')
        prices[key] = cert['total']
    require(word['program'][10481:10484] == [['ADD', 256, 257, '-1/2', 306],
            ['SCALE', 257, '2', 306], ['ADD', 257, 256, '3/2', 306]], 'actual selected resident window')
    return word['program'] + [['EXIT']], circuits, prices


def seek(previous, following):
    if previous == -1:
        return following * 128, 0
    delta = following - previous - 1
    return abs(delta) * 128, 1 if delta >= 0 else -1


def legal_orders(slots, needed):
    if needed is None:
        actions = [(0, bank, field) for bank, field in enumerate(slots) if field >= 0]
        for order in permutations(actions):
            yield (-1, -1), order
        return
    for assignment in permutations(needed):
        if any(old in needed and old != new for old, new in zip(slots, assignment)):
            continue
        actions = []
        for bank, (old, new) in enumerate(zip(slots, assignment)):
            if old != new:
                if old >= 0:
                    actions.append((0, bank, old))
                actions.append((1, bank, new))
        for order in permutations(actions):
            held = list(slots)
            for load, bank, field in order:
                if (load and (held[bank] != -1 or field in held)) or (not load and held[bank] != field):
                    break
                held[bank] = field if load else -1
            else:
                require(tuple(held) == assignment, 'legal bank endpoint')
                yield assignment, order


def edges(state, event, prices, resident):
    slots, head, op = state[:2], state[2], event[0]
    needed = tuple(event[1:3]) if op in ('ADD', 'COPY') else None
    if needed is not None:
        require(len(set(needed)) == 2, 'distinct scalar operands')
    for held, transfers in legal_orders(slots, needed):
        end, a, b = head, 0, 0
        for _, _, field in transfers:
            da, db = seek(end, field)
            a, b, end = a + da + 1152, b + db - 3, field
        if op in ('ADD', 'COPY'):
            a += 512 + 2 * prices[(op, str(Fraction(event[3])))]
            b -= 256
        elif op == 'SCALE':
            da, db = seek(end, event[1])
            a += da + 2688 + prices[(op, str(Fraction(event[2])))]
            b += db - 267
            end = event[1]
        else:
            require(op in ('MOVE', 'INIT', 'CLEAR', 'EXIT'), 'source event domain')
            if end >= 0:
                a, b = a + (end + 1) * 128, b - 1
            end = -1
        yield (*held, end), (a, b), {'kind': 'old', 'transfers': [list(x) for x in transfers]}
    if resident and op == 'SCALE' and Fraction(event[2]) == 2 and event[1] in slots:
        yield state, (3284, -2), {'kind': 'resident', 'transfers': []}


def normalized_layer_edges(layer, event, prices, resident):
    result = []
    for state in sorted(layer):
        for end, cost, action in edges(state, event, prices, resident):
            result.append([list(state), list(end), list(cost), action['kind'], action['transfers']])
    return sorted(result)


def solve(events, prices, resident, limits):
    layers, parents = [{START: (0, 0, 0, 0)}], []
    stats = {'layers': len(events) + 1, 'total_states': 1, 'total_edges': 0, 'max_layer_states': 1}
    edge_hash = hashlib.sha256()
    for event in events:
        before, nxt, parent = layers[-1], {}, {}
        normalized = normalized_layer_edges(before, event, prices, resident)
        edge_hash.update(canonical(normalized)); stats['total_edges'] += len(normalized)
        require(stats['total_edges'] <= limits['total_edges'], 'complete edge cap')
        for state in sorted(before):
            one, two, pa, pb = before[state]
            for end, (a, b), action in edges(state, event, prices, resident):
                ca, cb = pa + a, pb + b
                new_one, new_two = ca + cb, two + 2 * a + b
                if end not in nxt:
                    nxt[end] = (new_one, new_two, ca, cb); parent[end] = (state, action)
                else:
                    old_one, old_two, old_a, old_b = nxt[end]
                    if (new_one, ca, cb) < (old_one, old_a, old_b):
                        old_one, old_a, old_b = new_one, ca, cb; parent[end] = (state, action)
                    nxt[end] = (old_one, min(old_two, new_two), old_a, old_b)
        require(bool(nxt), 'nonempty complete layer')
        stats['total_states'] += len(nxt)
        stats['max_layer_states'] = max(stats['max_layer_states'], len(nxt))
        require(stats['total_states'] <= limits['total_states'], 'complete state cap')
        layers.append(nxt); parents.append(parent)
    require(set(layers[-1]) == {START}, 'final complete owner origin')
    actions, state = [], START
    for parent in reversed(parents):
        state, action = parent[state]; actions.append(action)
    require(state == START, 'initial complete owner origin')
    rows = [[[s[0], s[1], s[2], v[1] - v[0], 2 * v[0] - v[1]]
             for s, v in sorted(layer.items())] for layer in layers]
    one, two, _, _ = layers[-1][START]
    stats.update(total=[two - one, 2 * one - two],
                 states_sha256=sha(canonical([[row[:3] for row in layer] for layer in rows])),
                 potentials_sha256=sha(canonical(rows)), edges_sha256=edge_hash.hexdigest())
    return {'total': stats['total'], 'layers': rows, 'actions': list(reversed(actions))}, stats


def check_policy(events, prices, resident, policy):
    require(type(policy) is dict and set(policy) == {'total', 'layers', 'actions'}, 'policy keys')
    require(len(policy['layers']) == len(events) + 1 and len(policy['actions']) == len(events), 'policy shape')
    layers = []
    for rows in policy['layers']:
        require(all(type(row) is list and len(row) == 5 and all(type(x) is int for x in row) for row in rows), 'strict potential rows')
        layer = {tuple(row[:3]): tuple(row[3:]) for row in rows}
        require(len(rows) == len(layer) and rows == sorted(rows), 'unique sorted state layer')
        layers.append(layer)
    require(layers[0] == {START: (0, 0)} and set(layers[-1]) == {START}, 'potential boundary')
    state, total_a, total_b, used = START, 0, 0, []
    for index, event in enumerate(events):
        reached = set()
        for before, (pa, pb) in layers[index].items():
            for end, (a, b), _ in edges(before, event, prices, resident):
                require(end in layers[index + 1], 'all reachable states retained')
                reached.add(end); na, nb = layers[index + 1][end]
                require(pa + a - na >= 0 and pa + pb + a + b - na - nb >= 0, 'all-D complete edge dual')
        require(reached == set(layers[index + 1]), 'exact complete state coverage')
        action = policy['actions'][index]
        matches = [(end, cost) for end, cost, candidate in edges(state, event, prices, resident) if candidate == action]
        require(len(matches) == 1, 'unique attaining physical-bank action')
        if action['kind'] == 'resident':
            used.append([index, event[1], state.index(event[1]), state[2]])
        state, (a, b) = matches[0]; total_a += a; total_b += b
    require(state == START and [total_a, total_b] == policy['total'] == list(layers[-1][START]), 'all-D attained complete total')
    return used


def gates(dimension):
    result = []
    for record in range(2 * dimension):
        base = 64 * record
        for bit in range(62, -1, -1):
            a, b = base + bit, base + bit + 1
            result.extend([[a, b], [b, a], [a, b]])
        result.append([base + 63, base])
    return result


def route(dimension):
    head, word = 0, []
    for control, target in gates(dimension):
        for address, opcode in [(control, 'xor'), (target, 'flipmask'), (control, 'xor')]:
            step = 1 if address >= head else -1
            word.extend([['move', 0, step] for _ in range(abs(address - head))])
            head = address; word.append([opcode, 0, 1 if opcode == 'flipmask' else 0])
    word.extend([['move', 0, -1] for _ in range(head)])
    return word


def run_route(word, bits):
    value, head, scratch = list(bits), 0, 0
    reads, writes, moves = 0, 0, 0
    for op, first, second in word:
        require(type(first) is int and type(second) is int and first == 0, 'resident instruction operands')
        if op == 'move':
            require(second in (-1, 1), 'unit move')
            head += second; moves += 1
            require(0 <= head < len(value), 'resident tape bounds')
        elif op == 'xor':
            require(second == 0, 'resident xor tape')
            scratch ^= value[head]; reads += 1
        elif op == 'flipmask':
            require(second == 1, 'resident control mask')
            value[head] ^= scratch; reads += 1; writes += 1
        else:
            raise ValueError('resident instruction grammar')
    require(head == 0 and scratch == 0, 'resident head/control return')
    return value, (reads, writes, moves)


def reverse_route(word):
    return [[op, first, -second if op == 'move' else second] for op, first, second in reversed(word)]


def gate_map(word, bits):
    value = list(bits)
    for gate in word:
        require(type(gate) is list and len(gate) == 2 and gate[0] != gate[1], 'literal source SCALE2 CNOT')
        value[gate[1]] ^= value[gate[0]]
    return value


def signed_bits(values):
    return [(value >> bit) & 1 for value in values for bit in range(64)]


def signed_values(bits):
    result = []
    for start in range(0, len(bits), 64):
        x = sum(bits[start + bit] << bit for bit in range(64))
        result.append(x - (1 << 64) if x >> 63 else x)
    return result


def physical(routes, circuits, cases):
    selected = [row[2] for row in circuits if row[:2] == ['SCALE', '2']]
    require(len(selected) == 1, 'unique source SCALE2 circuit')
    old = selected[0]; source_basis = 0; records = []
    for entry in routes:
        d, word = entry['D'], entry['word']; size = 128 * d
        require(word == route(d), 'actual resident instruction word')
        expected = (1140 * d, 380 * d, 1764 * d - 2)
        for column in range(size + 1):
            bits = [int(column == bit) for bit in range(size)]
            out, meter = run_route(word, bits)
            require(meter == expected, 'literal resident forward meter')
            require(run_route(reverse_route(word), out)[0] == bits, 'literal instruction inverse')
            logical = gate_map(gates(d), bits)
            require(out == logical, 'actual physical instruction map')
            if d == 1:
                old_in = bits + [int(column == size)]
                require(gate_map(old, old_in) == out + [old_in[-1]], 'credited source129 basis dependency')
                source_basis += 1
        for values in cases['signed_values'][str(d)]:
            require(len(values) == 2 * d and all(-(1 << 62) <= x < (1 << 62) for x in values), 'signed no-overflow fixture')
            bits = signed_bits(values); out, meter = run_route(word, bits)
            require(signed_values(out) == [2 * x for x in values], 'actual signed resident output')
            require(meter == expected and run_route(reverse_route(word), out)[0] == bits, 'signed meter/inverse')
        records.append({'D': d, 'reads': expected[0], 'writes': expected[1], 'moves': expected[2],
                        'total': sum(expected), 'basis_columns': size + 1})
    require(source_basis == 129, '129 literal source basis columns')
    return {'source_basis_columns': source_basis, 'records': records}


def typed_equal(left, right):
    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        return left.keys() == right.keys() and all(typed_equal(left[k], right[k]) for k in left)
    if isinstance(left, list):
        return len(left) == len(right) and all(typed_equal(a, b) for a, b in zip(left, right))
    return left == right


def emit_artifact(path, artifact, cap):
    raw = canonical(artifact)
    require(len(raw) <= cap, 'combined proof artifact byte cap')
    if path:
        with gzip.open(path, 'wb') as stream:
            stream.write(raw)
    return raw


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--emit', type=Path)
    parser.add_argument('--write-policy', type=Path)
    args = parser.parse_args(); cases = authenticate()
    events, circuits, prices = source_data(cases)
    policies, profiles = {}, {}
    for name, enabled in [('baseline', False), ('candidate', True)]:
        limits = dict(cases['limits'])
        if enabled:
            limits['total_states'] -= profiles['baseline']['total_states']
            limits['total_edges'] -= profiles['baseline']['total_edges']
        policies[name], profiles[name] = solve(events, prices, enabled, limits)
    routes = [{'D': d, 'word': route(d)} for d in cases['dimensions']]
    artifact = {'schema_version': 1, 'width': 64, **policies, 'routes': routes}
    raw = emit_artifact(args.write_policy, artifact, cases['limits']['artifact_decoded_bytes'])
    baseline_used = check_policy(events, prices, False, policies['baseline'])
    candidate_used = check_policy(events, prices, True, policies['candidate'])
    require(not baseline_used and candidate_used, 'actual complete resident occurrence')
    require(profiles['baseline']['total'] == [800847760, -5118198], 'credited complete baseline reproduced')
    gain = [a - b for a, b in zip(profiles['baseline']['total'], profiles['candidate']['total'])]
    require(gain[0] >= 0 and sum(gain) > 0, 'strict complete all-D gain')
    result = {'schema_version': 1, 'source_manifest_sha256': SOURCE_HASH,
              'case_manifest_sha256': CASE_HASH, 'policies': profiles,
              'physical': physical(routes, circuits, cases)}
    if args.emit:
        args.emit.write_bytes(canonical(result))
    else:
        require(typed_equal(parse((ROOT / 'RESULT.json').read_bytes()), result), 'actual complete retained result differs')
        retained = decoded(ROOT / 'POLICY.json.gz', cases['limits']['artifact_decoded_bytes'])
        require(typed_equal(retained, artifact), 'actual complete retained policy differs')
    print('PASS_P104_RESIDENT_SCALE_POLICY complete_all_D_dual_and_path literal_routes_source_basis')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError) as error:
        print('FAIL: ' + str(error), file=sys.stderr)
        sys.exit(1)
