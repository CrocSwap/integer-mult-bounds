#!/usr/bin/env python3
"""Check all native edges, endpoint phases, and complete literal data words."""
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import importlib.util
import json

HERE = Path(__file__).resolve().parent
LANES = HERE.parents[1]
SOURCE = LANES/'new-core-transfer-20261017/low-displacement-20261020'
PEER = LANES/'independent-review-20261017/rank-thirty-review-20261020'
INPUTS = {}


def need(test, message):
    if not test:
        raise ValueError(message)


def read(path, pin=None, compressed=False):
    data = path.read_bytes()
    digest = sha256(data).hexdigest()
    content = gzip.decompress(data) if compressed else data
    need(pin is None or sha256(content).hexdigest() == pin, 'Input pin: '+str(path))
    INPUTS[str(path.relative_to(LANES))] = {'sha256': digest}
    if compressed:
        INPUTS[str(path.relative_to(LANES))]['decompressed_sha256'] = sha256(content).hexdigest()
    return content


def frozen(path, name, pin):
    record = json.loads(read(path/name, pin))
    for file, digest in record['files'].items():
        read(path/file, digest)
    return record


def add(target, source, coefficient):
    for key, value in source.items():
        result = target.get(key, F(0))+coefficient*value
        if result:
            target[key] = result
        else:
            target.pop(key, None)


def span(vectors):
    result = {0}
    for vector in vectors:
        result |= {x ^ vector for x in result}
    return result


def reverse(events):
    """Return the full map by reverse propagation of output coefficients."""
    columns = [{i: F(1)} for i in range(640)]
    for event in reversed(events):
        if event[0] != 'scalar':
            continue
        op, target, origin, coefficient = event[1]
        c = F(coefficient)
        if op == 'scale':
            columns[target] = {j: c*v for j, v in columns[target].items()}
        else:
            need(op == 'add' and target != origin, 'Scalar grammar')
            add(columns[origin], columns[target], c)
    return columns


def response_columns(response, direction):
    columns = [{i: F(1)} for i in range(640)]
    for target, row in enumerate(response):
        for origin, coefficient in row.items():
            if direction == 'forward':
                add(columns[origin], {112+target: coefficient}, F(1))
            else:
                add(columns[112+target], {origin: -coefficient}, F(1))
    return columns


def scalar_price(events):
    count = 0
    for event in events:
        if event[0] != 'scalar':
            continue
        op, _, _, value = event[1]
        c = F(value)
        n, d = abs(c.numerator), c.denominator
        need(n > 0 and d & (d-1) == 0, 'Nonzero dyadic scalar coefficient')
        if op == 'scale':
            need(n & (n-1) == 0, 'Dyadic unit scale')
            count += 2*(abs(n.bit_length()-d.bit_length())+(c < 0))
        else:
            count += 2*(3+n.bit_length()-1+n.bit_count()+d.bit_length()-1)
    return count


def ledger(word, ports, response, direction):
    current = list(word['start'])
    frames = word['frames']
    spaces = [span(basis) for basis in frames]
    need(len(current) == len(word['final']) == 640, 'Exactly 640 live roles')
    need(all(len(s) == 1 << len(b) and all(0 <= x < 512 for x in s)
             for s, b in zip(spaces, frames)), 'Independent literal frame bases')
    for p, q in enumerate(ports):
        need(spaces[current[p]] == {0, q} and spaces[current[112+p]] == {0},
             'Actual physical source line and target I')
        need(len(spaces[word['final'][p]]) == 512, 'Final X is FULL')
        need(spaces[word['final'][112+p]] ==
             {x for x in range(512) if (x & q).bit_count() % 2 == 0},
             'Final Y is the actual q hole')
    used = set()
    prefix_rows = [{i: F(1)} for i in range(224)]
    maximum = F(1)
    for event in word['events']:
        if event[0] == 'native':
            _, target, before, after, rank, key = event
            need(0 <= target < 224 and current[target] == before, 'Actual native source role and frame')
            need(spaces[before] < spaces[after], 'Strictly nested native frame')
            need(rank == len(frames[after])-len(frames[before])
                 == word['native_recipes'][key]['rank'], 'Native rank and dimension difference')
            need(key == str(before)+':'+str(after), 'Native occurrence has the exact edge key')
            current[target] = after
            used.add(key)
        else:
            need(event[0] == 'scalar', 'No hidden operation')
            gate, frame = event[1:]
            op, target, origin, coefficient = gate
            need(0 <= target < 224 and current[target] == frame, 'Scalar target has the declared frame')
            c = F(coefficient)
            if op == 'scale':
                need(origin is None, 'Scale has no hidden source')
                prefix_rows[target] = {j: c*v for j, v in prefix_rows[target].items()}
            else:
                need(op == 'add' and 0 <= origin < 224 and origin != target
                     and current[origin] == frame, 'Scalar source has the same actual frame')
                add(prefix_rows[target], prefix_rows[origin], c)
            maximum = max(maximum, sum(abs(v) for v in prefix_rows[target].values()))
    need(current == word['final'], 'Every final frame')
    need(current[224:] == word['start'][224:], 'All 416 other roles remain in their input frame')
    need(reverse(word['events']) == response_columns(response, direction), 'All 640 reverse columns')
    profile = Counter(e[4] for e in word['events'] if e[0] == 'native')
    for transfer in word['transfer_records']:
        event = word['events'][transfer['event']]
        need(event[0] == 'scalar' and event[1][0] == 'add'
             and event[1][-1] == transfer['coefficient'], 'Transfer metadata selects the actual ADD')
    return {
        'all_input_columns': 640, 'untouched_arbitrary_roles': 416,
        'owned_fields': 0, 'private_fields': 0, 'used_native_edges': len(used),
        'native_profile': dict(sorted(profile.items())),
        'native_mass': sum(rank*count for rank, count in profile.items()),
        'native_children': sum(profile.values()), 'real_scalar_primitives': scalar_price(word['events']),
        'top_level_array_norm_bound': str(maximum),
    }, used


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    frozen(SOURCE, 'NATIVE-FREEZE.json',
           'efdf8acc943934e83374f986a4a9a6f49ab7607a4f4e8d2973ec71cd5e1c5e24')
    frozen(SOURCE, 'RESPONSE-FREEZE.json',
           '59e43eb802114070aa40b39a7e355b3271a744b713a32c5a3e09c2e46ec7fdc9')
    frozen(PEER, 'FREEZE.json',
           '15c54c0f0d0f33bdcf420a4c7610d55fff6104fe22d2c4ade8ae9255a3ff8189')
    payload = json.loads(read(SOURCE/'native-normal-v2/NATIVE-PROGRAM.json.gz',
                             'e387b082422f085efc8122497cdda0b5211a86b0418af4b9fdbc1da15ac71558', True))
    for relative, (mode, pin) in payload['source_pins'].items():
        read(LANES/relative, pin, mode == 'decompressed')
    cyclic = json.loads(read(LANES/'independent-review-20261017/cyclic-pair-flags-20261018/CYCLIC-FLAGS.json',
                             '3034e1df3670f64e5b79a51a435d7903f3be7cef10d6b486a8bd4d420c989585'))
    core = json.loads(read(LANES/'new-core-transfer-20261017/CLEAN-J-PROGRAMS.json.gz',
                           'a6c5dc63a47c1fdb0a97314a3b8541035f507beccb1029762f703039465187fa', True))
    model = json.loads(read(SOURCE/'run-normal/RESPONSE-PROGRAM.json',
                            '5832788135e16c2427f8c746f251501621684a02ef88b0a14322056653dc2d7c'))
    need(payload['response'] == model['response'], 'Exact matrix-layer response')
    ports = cyclic['ports']
    need(all(p['canonical']['ports'] == ports for p in core['providers'].values()),
         'Both actual providers have the same port labels')
    interpreter = HERE.parent/'isotropic-pair-review-20261018/check.py'
    read(interpreter, 'e428f575ad93a8ade3a92b641a2b5eef111519f03ba5cceca4cd4957f008ba18')
    spec = importlib.util.spec_from_file_location('spatial_native_review', interpreter)
    phase = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(phase)
    need(set(payload['providers']) == {'base', 'extra'}, 'Both providers')
    need(payload['providers']['base'] == payload['providers']['extra'], 'Byte-equal provider words')
    words = payload['providers']['base']
    need(set(words) == {'forward', 'backward'}, 'Both directions')
    first = words['forward']
    for word in words.values():
        need(word['frames'] == first['frames'] and word['native_recipes'] == first['native_recipes']
             and word['endpoint_adapters'] == first['endpoint_adapters'], 'One exact native geometry')
        need(word['start'] == cyclic['start'] and word['final'] == cyclic['final'],
             'Exact inherited input and output frame declarations')
    frame_cache = {}

    def frame(index):
        if index not in frame_cache:
            frame_cache[index] = phase.canonical(first['frames'][index])
        return frame_cache[index]

    response = [{int(k): F(v) for k, v in row.items()} for row in payload['response']]
    reports, union = {}, set()
    for direction, word in words.items():
        report, used = ledger(word, ports, response, direction)
        need(report['native_profile'] == {1: 1036, 3: 48, 4: 55, 5: 55, 6: 9, 7: 9},
             'Complete declared native profile')
        need(report['native_mass'] == 1792 and report['native_children'] == 1212
             and report['real_scalar_primitives'] == 5288, 'Complete local invoice')
        need(report['top_level_array_norm_bound'] == ('46' if direction == 'forward' else '30'),
             'Exact top-level prefix bound')
        reports[direction] = report
        union |= used
    need(union == set(first['native_recipes']) and len(union) == 1141,
         'Every fresh recipe is used and every used edge is checked')
    phases = []
    for i, (key, record) in enumerate(first['native_recipes'].items(), 1):
        before, after = map(int, key.split(':'))
        result = phase.compare(frame(before)+phase.recipe(record), frame(after),
                               'Native '+key, 1 << len(first['frames'][after]))
        phases.append({'edge': key, 'rank': record['rank'], **result})
        if i % 40 == 0:
            print('Independent full native columns', i, '/ 1141', flush=True)
    endpoints = first['endpoint_adapters']
    need(len(endpoints) == 224 and {(r['port'], r['role']) for r in endpoints} ==
         {(p, role) for p in range(112) for role in ('source', 'target')}, 'All 224 endpoints')
    endpoint_checks = []
    full = [('C', 1 << j, 1) for j in range(9)]
    for i, record in enumerate(endpoints, 1):
        p, role = record['port'], record['role']
        target_frame = first['start'][p] if role == 'source' else first['final'][112+p]
        need(record['rank'] == 0 and record['right'] is None and record['frame'] == target_frame,
             'One explicit endpoint monomial with the actual endpoint frame')
        conventional = [('C', ports[p], 1)] if role == 'source' else [('C', ports[p], -1)]+full
        result = phase.compare(conventional+phase.recipe(record), frame(target_frame),
                               'Endpoint '+role+' '+str(p), 1 << len(first['frames'][target_frame]))
        endpoint_checks.append({'port': p, 'role': role, **result})
        if i % 32 == 0:
            print('Independent full endpoint columns', i, '/ 224', flush=True)
    key = next(iter(first['native_recipes']))
    before, after = map(int, key.split(':'))
    bad = frame(before)+phase.recipe(first['native_recipes'][key])+phase.compile_circuit([['phase', 1]])
    need(phase.run(bad, 0) != phase.run(frame(after), 0), 'Wrong global phase control')
    missing = list(first['events'])
    del missing[first['transfer_records'][0]['event']]
    need(reverse(missing) != response_columns(response, 'forward'), 'Missing transfer control')
    result = {
        'status': 'PASS_INDEPENDENT_FULL_NATIVE_RANK30',
        'literal_words': reports, 'providers_share_exact_words': ['base', 'extra'],
        'native_phase_checks': phases, 'endpoint_phase_checks': endpoint_checks,
        'native_edges': 1141, 'endpoint_maps': 224, 'spatial_columns_per_check': 512,
        'negative_controls': ['wrong global phase', 'one omitted nonzero transfer'],
        'matrix_layer_review': 'independent-review-20261017/rank-thirty-review-20261020/FREEZE.json',
        'scope': 'Complete local data maps and physical phases. No productive helper progress, recursive host, routed inverse code, terminal decoder, or complete supplier claim.',
    }
    for name, value in (('REVIEW.json', result), ('INPUTS.json', INPUTS)):
        (args.out/name).write_text(json.dumps(value, indent=2, sort_keys=True)+'\n')
    print(result['status'], flush=True)


if __name__ == '__main__':
    main()
