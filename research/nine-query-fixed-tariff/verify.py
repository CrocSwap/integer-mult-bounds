#!/usr/bin/env python3
"""Fixed nine-query tariff closure and independent X2 premise/word evidence."""
from collections import Counter
from itertools import combinations
import argparse
import gzip
import hashlib
import io
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
SOURCE_HASH = '0d1cbe7daa2cd1092c1a64a3615521b651faf8f83102b7db03896c17a0a09a1a'
CASE_HASH = 'fc2c9be60d410124b45da970af462acc749275a35e20a16969527dca5b56f4ea'
SCHEMA_HASH = '0d5089118230203c2f689e2084292997f1c6d07a735f9c3641fc788cb03f99c1'
PAIRS = list(combinations(range(9), 2))
PAIR_INDEX = {edge: index for index, edge in enumerate(PAIRS)}
XS = ['x' + str(i) for i in range(5)]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':')) + '\n').encode()


def unique(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'duplicate JSON key')
        result[key] = value
    return result


def bad_number(value):
    raise ValueError('noninteger JSON number: ' + value)


def parse(raw):
    return json.loads(raw, object_pairs_hook=unique, parse_float=bad_number, parse_constant=bad_number)


def typed_equal(a, b):
    if type(a) is not type(b):
        return False
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(typed_equal(a[k], b[k]) for k in a)
    if isinstance(a, list):
        return len(a) == len(b) and all(typed_equal(x, y) for x, y in zip(a, b))
    return a == b


def authenticate():
    for name, expected in [('SOURCE-PINS.json', SOURCE_HASH), ('CASES.json', CASE_HASH),
                           ('SCHEMA.json', SCHEMA_HASH)]:
        require(sha((ROOT / name).read_bytes()) == expected, 'immutable ' + name)
    manifest = parse((ROOT / 'SOURCE-PINS.json').read_bytes())
    require(len(manifest['files']) == 4, 'four inert sources')
    for row in manifest['files']:
        path = (ROOT / row['local_path']).resolve()
        require(path.parent == (ROOT / 'inputs').resolve(), 'source containment')
        raw = path.read_bytes()
        require(len(raw) == row['bytes'] and sha(raw) == row['sha256'], 'source bytes/SHA256')
        require(hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == row['git_blob'], 'source Git blob')
    return parse((ROOT / 'CASES.json').read_bytes())


def matchings(vertices):
    first = vertices[0]
    for second in vertices[1:]:
        rest = [v for v in vertices if v not in (first, second)]
        for partner in rest[1:]:
            last = [v for v in rest if v not in (rest[0], partner)]
            yield [(first, second), (rest[0], partner), tuple(last)]


def forest_classes():
    graphs = {}
    for center in range(9):
        for leaves in combinations([v for v in range(9) if v != center], 2):
            rest = [v for v in range(9) if v not in (center, *leaves)]
            for matching in matchings(rest):
                edges = sorted([tuple(sorted((center, v))) for v in leaves] + matching)
                code = sum(1 << PAIR_INDEX[edge] for edge in edges)
                require(code not in graphs and len(set(edges)) == 5, 'unique forest class')
                graphs[code] = edges
    return sorted(graphs.items())


def rank5(rows):
    basis = [0] * 5
    for row in rows:
        for bit in range(4, -1, -1):
            if row >> bit & 1:
                if basis[bit]:
                    row ^= basis[bit]
                else:
                    basis[bit] = row
                    break
    return sum(value != 0 for value in basis)


def graph_slots(edges):
    increments = [sum(1 << j for j, edge in enumerate(edges) if vertex in edge) for vertex in range(9)]
    require(all(increments) and rank5(increments) == 5, 'nonzero covering increments')
    points = [0]
    for delta in increments:
        points.append(points[-1] ^ delta)
    require(points[-1] == 0, 'closed forest path')
    require(sum(2 * (x.bit_count() - 1) for x in increments) == 2, 'actual X2 forest layer')
    return points[:-1]


def even_minima(slots):
    require(len(slots) == 9 and slots[0] == 0, 'nine prefix slots')
    values, best, chosen = [0] * 512, [99] * 32, [None] * 32
    for subset in range(512):
        if subset:
            bit = subset & -subset
            values[subset] = values[subset ^ bit] ^ slots[bit.bit_length() - 1]
        weight = subset.bit_count()
        value = values[subset]
        if weight % 2 == 0 and weight < best[value]:
            best[value], chosen[value] = weight, subset
    require(all(0 < x < 99 and x % 2 == 0 for x in best[1:]), 'complete even-subset coverage')
    return best[1:], chosen[1:]


def records(limit):
    result = []
    for code, edges in forest_classes():
        slots = graph_slots(edges); minima, _ = even_minima(slots)
        result.append([code, slots, minima])
        require(len(result) <= limit, 'record cap without pruning')
    return result


def witness_word(closed):
    minima, chosen = even_minima(closed[:-1]); word = []
    for position in range(9):
        for mask, subset in enumerate(chosen, 1):
            if subset >> position & 1:
                word.append(['R', mask])
        delta = closed[position] ^ closed[position + 1]
        require(delta != 0, 'nonzero query edge')
        target = (delta & -delta).bit_length() - 1
        donors = [j for j in range(5) if j != target and delta >> j & 1]
        word.extend([['X', donor, target] for donor in donors])
        word.append(['Q', target])
        word.extend([['X', donor, target] for donor in reversed(donors)])
    return word, minima


def initial_state():
    names = XS + ['y' + str(m) for m in range(1, 32)] + ['z', 'w0', 'w1', 'w2']
    return {name: {(name,)} for name in names}


def apply_event(state, event):
    require(type(event) is list and event and type(event[0]) is str, 'instruction array')
    kind = event[0]
    if kind == 'X':
        require(len(event) == 3 and all(type(x) is int and 0 <= x < 5 for x in event[1:])
                and event[1] != event[2], 'source XOR distinct integer ports')
        source, target, prefix = XS[event[1]], XS[event[2]], ()
    elif kind == 'Q':
        require(len(event) == 2 and type(event[1]) is int and 0 <= event[1] < 5, 'query integer port')
        source, target, prefix = XS[event[1]], 'z', ('B',)
    elif kind == 'R':
        require(len(event) == 2 and type(event[1]) is int and 1 <= event[1] < 32, 'readout integer mask')
        source, target, prefix = 'z', 'y' + str(event[1]), ('A' + str(event[1]),)
    else:
        raise ValueError('instruction alphabet')
    state[target].symmetric_difference_update({prefix + term for term in state[source]})


def connector_point(polynomial):
    require(('z',) in polynomial, 'dirty connector retained')
    point = 0
    for term in polynomial - {('z',)}:
        require(len(term) == 2 and term[0] == 'B' and term[1] in XS, 'literal common-B connector projection')
        point ^= 1 << XS.index(term[1])
    return point


def expected_state():
    state = initial_state()
    for mask in range(1, 32):
        state['y' + str(mask)] |= {('A' + str(mask), 'B', XS[j]) for j in range(5) if mask >> j & 1}
    return state


def check_word(word, closed):
    state = initial_state(); prefixes = [0]; reads = {m: [] for m in range(1, 32)}; q = 0
    counts = Counter()
    for event in word:
        apply_event(state, event); counts[event[0]] += 1
        if event[0] == 'R':
            reads[event[1]].append(q)
        elif event[0] == 'Q':
            q += 1; prefixes.append(connector_point(state['z']))
    require(prefixes == closed, 'actual query prefix/path binding')
    minima, _ = even_minima(closed[:-1])
    for mask, slots in reads.items():
        require(len(slots) == minima[mask - 1] and len(set(slots)) == len(slots)
                and all(0 <= x < 9 for x in slots), 'actual minimum even readouts')
        value = 0
        for slot in slots:
            value ^= closed[slot]
        require(len(slots) % 2 == 0 and value == mask, 'actual even subset XOR')
    require(state == expected_state(), 'free noncommuting dirty root map/restoration')
    for event in reversed(word):
        apply_event(state, event)
    require(state == initial_state(), 'literal full-word inverse')
    Q, R, X = counts['Q'], counts['R'], counts['X']
    invoice = {'map_leaves': 28 * Q + R, 'echo_nodes': 9 * Q, 'source_XORs': X,
               'root_dispatches': len(word), 'borrowed_dirty_rows': 4,
               'total': 38 * Q + 2 * R + 2 * X}
    require(invoice['total'] == invoice['map_leaves'] + invoice['echo_nodes'] + X + len(word), 'complete fixture invoice')
    return {'closed': closed, 'Q': Q, 'R': R, 'X': X, 'tariff': invoice['total'], 'invoice': invoice}


def reject(call, fragment):
    try:
        call()
    except ValueError as error:
        require(fragment in str(error), 'intended rejection diagnostic')
        return
    raise ValueError('negative control accepted')


def controls(word, closed):
    reject(lambda: parse(b'{"x":1,"x":2}'), 'duplicate')
    reject(lambda: parse(b'{"x":NaN}'), 'noninteger')
    reject(lambda: parse(b'{"x":1.0}'), 'noninteger')
    for event, fragment in [(['Q', True], 'query'), (['R', 32], 'readout'),
                            (['X', 0, 0], 'XOR'), (['bad', 0], 'alphabet')]:
        reject(lambda: apply_event(initial_state(), event), fragment)
    for kind, fragment in [('Q', 'prefix/path'), ('R', 'minimum even'), ('X', 'prefix/path')]:
        index = next(i for i, event in enumerate(word) if event[0] == kind)
        changed = word[:index] + word[index + 1:]
        reject(lambda: check_word(changed, closed), fragment)
    return 10


def read_artifact(path, cap):
    with gzip.GzipFile(fileobj=io.BytesIO(path.read_bytes())) as stream:
        raw = stream.read(cap + 1)
    require(len(raw) <= cap, 'artifact byte cap')
    return parse(raw)


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--emit', type=Path)
    parser.add_argument('--write-floor', type=Path); args = parser.parse_args()
    cases = authenticate(); rows = records(cases['limits']['records'])
    word, _ = witness_word(cases['closed'])
    artifact = {'schema_version': 1, 'records': rows, 'witness_word': word}
    raw = canonical(artifact); require(len(raw) <= cases['limits']['artifact_bytes'], 'artifact byte cap')
    if args.write_floor:
        with gzip.open(args.write_floor, 'wb') as stream:
            stream.write(raw)
    histogram = Counter(sum(row[2]) for row in rows)
    require(len(rows) == 3780 and min(histogram) == 70, 'credited X2 premise independently checked')
    witness = check_word(word, cases['closed']); control_count = controls(word, cases['closed'])
    require([witness[k] for k in ['Q', 'R', 'X', 'tariff']] == [9, 70, 2, 486], 'credited witness full fixed invoice')
    require(38 * 9 + 2 * cases['credited_premises']['unrestricted_R_lower_bound'] + 2 * 6 == 490, 'credited higher-X fixed-price bound')
    floor = {'classes': len(rows), 'labeled_walks': len(rows) * math.factorial(5),
             'coordinate_labelings': math.factorial(5), 'minimum_R': min(histogram),
             'histogram': [list(x) for x in sorted(histogram.items())], 'records_sha256': sha(canonical(rows))}
    result = {'schema_version': 1, 'source_manifest_sha256': SOURCE_HASH,
              'case_manifest_sha256': CASE_HASH, 'floor': floor, 'witness': witness}
    if args.emit:
        args.emit.write_bytes(canonical(result))
    else:
        require(typed_equal(parse((ROOT / 'RESULT.json').read_bytes()), result), 'actual complete retained result differs')
        require(typed_equal(read_artifact(ROOT / 'FLOOR.json.gz', cases['limits']['artifact_bytes']), artifact), 'actual complete retained FLOOR differs')
    print('PASS_NINE_QUERY_FIXED_TARIFF classes=3780 fixed_tariff=486 controls=' + str(control_count))


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError) as error:
        print('FAIL: ' + str(error), file=sys.stderr); sys.exit(1)
