#!/usr/bin/env python3
"""Source-faithful literal clean pair; packed Boolean execution, no hidden reset gates."""
import argparse
from collections import defaultdict
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
SOURCE_HASH = '771b2147ada0ebcbb0db1525f2db67a3c31814e88fccdd00983466e9c216b469'
CASE_HASH = '432b6579917eee977f995fd942507cd1d82cc0d7b967562db9fe00297eb15877'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':')) + '\n').encode()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def unique(pairs):
    value = {}
    for key, item in pairs:
        require(key not in value, 'duplicate JSON key')
        value[key] = item
    return value


def bad_number(value):
    raise ValueError('nonfinite JSON: ' + value)


def parse(raw):
    return json.loads(raw, object_pairs_hook=unique, parse_constant=bad_number)


def same_typed(a, b):
    if type(a) is not type(b):
        return False
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(same_typed(a[k], b[k]) for k in a)
    if isinstance(a, list):
        return len(a) == len(b) and all(same_typed(x, y) for x, y in zip(a, b))
    return a == b


def authenticate():
    require(sha((ROOT / 'SOURCE-PINS.json').read_bytes()) == SOURCE_HASH, 'source manifest')
    require(sha((ROOT / 'CASES.json').read_bytes()) == CASE_HASH, 'case manifest')
    manifest = parse((ROOT / 'SOURCE-PINS.json').read_bytes())
    require(type(manifest) is dict and len(manifest['files']) == 10, 'ten source objects')
    executable = []
    for row in manifest['files']:
        path = (ROOT / row['local_path']).resolve()
        require(path.parent == (ROOT / 'inputs').resolve(), 'source containment')
        data = path.read_bytes()
        require(len(data) == row['bytes'] and sha(data) == row['sha256'], 'source bytes/hash')
        require(hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest() == row['git_blob'], 'source blob')
        if row['executable']:
            executable.append(path.name)
    require(sorted(executable) == ['3152-scalars.py', '6509-kernel.py'], 'exact declared executable predecessors')
    return parse((ROOT / 'CASES.json').read_bytes())


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, 'source loader')
    module = importlib.util.module_from_spec(spec)
    exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    return module


def packed_inputs(inputs, width):
    columns = [0] * (18 * width + 6)
    for index, vector in enumerate(inputs):
        for word, value in enumerate(vector):
            for bit in range(width):
                if (value >> bit) & 1:
                    columns[word * width + bit] |= 1 << index
    return columns


def run_gates(gates, initial):
    state = list(initial)
    for gate in gates:
        control = state[gate[0]]
        if len(gate) == 3:
            control &= state[gate[1]]
        state[gate[-1]] ^= control
    return state


def source_outputs(kernel, inputs, width, sign):
    rows = []
    for vector in inputs:
        first, second = kernel.pair(tuple(vector[:2]), tuple(vector[2:]), width, sign)
        output = list(first + second)
        inverse = kernel.pair(first, second, width, -sign)
        require(list(inverse[0] + inverse[1]) == vector, 'credited source inverse on reachable output')
        rows.append([vector, output])
    return rows


def check_group(width, sign, gates, inputs, kernel):
    rows = source_outputs(kernel, inputs, width, sign)
    initial = packed_inputs(inputs, width)
    expected = packed_inputs([row[1] for row in rows], width)
    after = run_gates(gates, initial)
    require(after[:4 * width] == expected[:4 * width], 'literal pair output differs from authenticated6509 source')
    require(all(value == 0 for value in after[4 * width:]), 'every owned bit returns zero')
    require(run_gates(reversed(gates), after) == initial, 'literal reverse complete-state inverse')
    return {'width': width, 'sign': sign, 'cases': len(inputs), 'io_sha256': sha(canonical(rows))}


def negative_controls(emitter, scalar, kernel):
    width = 6
    points = [[a, b, c, d] for a in [-1, 0, 1] for b in [-1, 0, 1]
              for c in [-1, 0, 1] for d in [-1, 0, 1]]
    gates = emitter.circuit(width, 1, scalar)
    initial = packed_inputs(points, width)
    expected = packed_inputs([row[1] for row in source_outputs(kernel, points, width, 1)], width)
    wrong = emitter.circuit(width, -1, scalar)
    require(run_gates(wrong, initial) != expected, 'wrong rotation control detected')
    evaluation, _ = emitter.evaluation(width, 1, scalar)
    no_uncompute = gates[:len(evaluation) + 4 * width] + gates[2 * len(evaluation) + 4 * width:]
    require(run_gates(no_uncompute, initial) != expected, 'omitted uncompute detected')
    require(not same_typed({'v': 1}, {'v': True}) and not same_typed({'v': 1}, {'v': 1.0}), 'strict typed aliases')


def admit(value):
    require(type(value) is dict and set(value) == {'schema_version', 'source_manifest_sha256', 'case_manifest_sha256', 'logical_inventory', 'case_groups'}, 'receipt keyset')
    require(type(value['schema_version']) is int and value['schema_version'] == 1, 'strict version')
    for key in ['source_manifest_sha256', 'case_manifest_sha256']:
        require(type(value[key]) is str and re.fullmatch('[0-9a-f]{64}', value[key]), 'manifest digest')
    require(type(value['logical_inventory']) is list and len(value['logical_inventory']) == 502, 'complete width-sign inventory')
    keys = {'width', 'sign', 'data_bits', 'clean_bits', 'wires', 'cx', 'ccx', 'x', 'gates', 'selector_bits', 'address_occurrences', 'control_incidences', 'encoded_bits'}
    for row in value['logical_inventory']:
        require(type(row) is dict and set(row) == keys and all(type(v) is int for v in row.values()), 'inventory exact integer schema')
    require(type(value['case_groups']) is list and len(value['case_groups']) == 16, 'case groups')
    for row in value['case_groups']:
        require(type(row) is dict and set(row) == {'width', 'sign', 'cases', 'io_sha256'}, 'group keys')
        require(all(type(row[k]) is int for k in ['width', 'sign', 'cases']), 'group integer fields')
        require(type(row['io_sha256']) is str and re.fullmatch('[0-9a-f]{64}', row['io_sha256']), 'group digest')
    return value


def compute():
    cases = authenticate()
    # All source files are authenticated BEFORE either executable predecessor import.
    scalar = load_module(ROOT / 'inputs/3152-scalars.py', '_credited3152')
    kernel = load_module(ROOT / 'inputs/6509-kernel.py', '_credited6509')
    emitter = load_module(ROOT / 'emitter.py', '_new_pair_emitter')
    grouped = defaultdict(list)
    for width, sign, vector in cases['cases']:
        grouped[(width, sign)].append(vector)
    inventory, groups, retained, hashes = [], [], [], []
    for width in range(6, 257):
        for sign in [-1, 1]:
            gates = emitter.circuit(width, sign, scalar)
            row = emitter.inventory(width, sign, gates)
            require(row['ccx'] == 96 * width - 80 and row['cx'] == 276 * width - 104, 'actual emitted count versus derived bill')
            inventory.append(row)
            hashes.append({'width': width, 'sign': sign, 'gate_sha256': sha(canonical(gates))})
            if width in cases['retained_gate_widths']:
                groups.append(check_group(width, sign, gates, grouped[(width, sign)], kernel))
                retained.append({'width': width, 'sign': sign, 'gates': gates})
            if width == 8 and sign == 1:
                print('MILESTONE: both signs, all promised W6/W7/W8 cases, zero-owned and literal reverse PASS', file=sys.stderr, flush=True)
    require(sum(row['cases'] for row in groups) == 14814, 'complete frozen case domain')
    negative_controls(emitter, scalar, kernel)
    result = {'schema_version': 1, 'source_manifest_sha256': SOURCE_HASH,
              'case_manifest_sha256': CASE_HASH, 'logical_inventory': inventory, 'case_groups': groups}
    return admit(result), {'schema_version': 1, 'circuits': retained}, hashes


def read_gates(path):
    with gzip.open(path, 'rb') as stream:
        raw = stream.read(16777217)
    require(len(raw) <= 16777216, 'gate artifact decompressed bound')
    return parse(raw)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emit', type=Path)
    parser.add_argument('--write-gates', type=Path)
    parser.add_argument('--write-inventory', type=Path)
    args = parser.parse_args()
    result, artifact, hashes = compute()
    if args.write_gates:
        args.write_gates.write_bytes(gzip.compress(canonical(artifact), mtime=0))
    if args.write_inventory:
        args.write_inventory.write_bytes(canonical(hashes))
    gates_path = args.write_gates if args.write_gates else ROOT / 'GATES.json.gz'
    hash_path = args.write_inventory if args.write_inventory else ROOT / 'GATE-INVENTORY.json'
    require(same_typed(read_gates(gates_path), parse(canonical(artifact))), 'actual retained gate-word values/types')
    require(same_typed(parse(hash_path.read_bytes()), hashes), 'all502 actual expanded gate hashes')
    if args.emit:
        args.emit.write_bytes(canonical(result))
    else:
        require(same_typed(admit(parse((ROOT / 'RESULT.json').read_bytes())), result), 'whole retained math/circuit profile')
    print(json.dumps({'status': 'pass', 'literal_circuits': 502, 'retained_words': 16, 'cases': 14814,
                      'every_owned_bit_zero': True, 'literal_inverse_checked': True}, sort_keys=True))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, TypeError, KeyError) as error:
        print('FAIL: ' + str(error), file=sys.stderr)
        raise SystemExit(1) from error
