#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Ali Romman with substantial OpenAI Codex assistance.
"""Check complete field staging, all-size costs and literal selected fixtures."""
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


def decode(bits):
    return sum(bit << i for i, bit in enumerate(bits))


def circuit_values(gates, values, width=64):
    bits = [(v >> j) & 1 for v in values for j in range(width)] + [0]
    for gate in gates:
        bits[gate[-1]] ^= int(all(bits[c] for c in gate[:-1]))
    require(bits[-1] == 0, 'circuit carry')
    return tuple(decode(bits[j * width:(j + 1) * width]) for j in range(2))


def physical_fixture(B, T, C, word, call, dimension, head, choice, gates, route):
    width, owners = 64, word['public'] + word['owned_fields']
    length = 2 * dimension * width
    values = [32 * ((17 * j + 3) % 31 - 15) for j in range(2 * owners * dimension)]
    target = call[-2] // length
    source = call[-1] // length
    if call[3] == 'COPY':
        values[2 * dimension * target:2 * dimension * (target + 1)] = [0] * (2 * dimension)
    initial = [(v >> bit) & 1 for v in values for bit in range(width)]
    expected = list(values)
    coefficient = Fraction(call[4])
    for coordinate in range(dimension):
        if call[3] == 'SCALE':
            positions = [2 * (target * dimension + coordinate) + c for c in (0, 1)]
            pair = [values[i] for i in positions]
            result = circuit_values(gates, pair)
            require(result == tuple(int(v * coefficient) % (1 << width) for v in pair), 'SCALE arithmetic')
            for position, value in zip(positions, result):
                expected[position] = value
        else:
            for component in (0, 1):
                positions = [2 * (f * dimension + coordinate) + component for f in (target, source)]
                pair = [values[i] for i in positions]
                result = circuit_values(gates, pair)
                arithmetic = (pair[0] + coefficient * pair[1], pair[1]) if call[3] == 'ADD' else (pair[1], pair[1])
                require(result == tuple(int(v) % (1 << width) for v in arithmetic), 'ADD/COPY arithmetic')
                for position, value in zip(positions, result):
                    expected[position] = value
    owner = T.Tape(initial)
    owner.head = head
    ribbons = [T.Tape([0] * length), T.Tape([0] * length)]
    carry = T.Tape((0,))
    B.execute(owner, ribbons, carry, call, width, dimension, choice, route)
    end, moves, _ = next(row for row in B.options(head, call, width, dimension) if row[2] == tuple(choice))
    repetitions = dimension if call[3] == 'SCALE' else 2 * dimension
    transferred = (4 if call[3] == 'SCALE' else 8) * dimension * width
    local = C.counts(route)
    expected_bill = dict(moves=moves + repetitions * local['moves'],
                         reads=4 * transferred + repetitions * local['reads'],
                         writes=2 * transferred + repetitions * local['writes'])
    observed = {name: sum(t.counts[name] for t in [owner, *ribbons, carry]) for name in expected_bill}
    require(observed == expected_bill, 'complete physical bill')
    require(owner.head == end and all(t.head == 0 for t in [*ribbons, carry]), 'physical head return')
    require(all(not any(t.snapshot()) for t in [*ribbons, carry]), 'staging and carry clean')
    expected_bits = tuple((v >> bit) & 1 for v in expected for bit in range(width))
    require(owner.snapshot() == expected_bits, 'all owner cells preserved or updated')
    return observed


def reject(action, message):
    try:
        action()
    except ValueError as error:
        require(message in str(error), 'control reason: ' + str(error))
        return
    raise ValueError('control accepted: ' + message)


def main(write=False):
    authenticate()
    B = load('batched_owner', HERE / 'batched.py')
    S = load('coordinate_owner', HERE / 'staging.py')
    C = load('cached_route', HERE / 'inputs/cache.py')
    T = load('physical_tape', ROOT / 'research/rank7-paired-scale-routing/route.py')
    word = json.loads(gzip.decompress((ROOT / 'research/p104-helper470-twin-rung-removal/WORD.json.gz').read_bytes()))
    rows = json.loads(gzip.decompress((HERE / 'inputs/CIRCUITS64.json.gz').read_bytes()))
    local_certs = json.loads(gzip.decompress((HERE / 'inputs/CERTIFICATES.json.gz').read_bytes()))
    circuits, routes = {}, {}
    for (op, coefficient, gates), cert in zip(rows, local_certs):
        circuits[(op, coefficient)] = gates
        routes[(op, coefficient)] = C.compile_route(64, gates, cert)
    require(len(routes) == 43, 'source template coverage')
    sequence = B.calls(word, 1, 64)
    if write:
        first = B.solve(sequence, 64, 1)
        second = B.solve(B.calls(word, 2, 64), 64, 2)
        certificate = B.affine_certificate(sequence, 64, first, second)
        (HERE / 'AFFINE.json.gz').write_bytes(gzip.compress(json.dumps(certificate, separators=(',', ':')).encode(), mtime=0))
    certificate = json.loads(gzip.decompress((HERE / 'AFFINE.json.gz').read_bytes()))
    a, b = B.check_affine(sequence, 64, certificate)
    route_counts = {key: C.counts(route) for key, route in routes.items()}
    local_total = dict(moves=0, reads=0, writes=0)
    transferred = 0
    for call in sequence:
        if len(call) == 2:
            continue
        op, coefficient = call[3:5]
        repeats = 1 if op == 'SCALE' else 2
        counts = route_counts[(op, coefficient)]
        for name in counts:
            local_total[name] += repeats * counts[name]
        transferred += (4 if op == 'SCALE' else 8) * 64
    comparisons = []
    physical_count = 0
    physical_totals = dict(moves=0, reads=0, writes=0)
    for dimension in (1, 2, 3, 17):
        coordinate_calls = S.plan(word, dimension, 64)
        old_cert = S.solve(coordinate_calls, 64)
        old = S.check(coordinate_calls, 64, old_cert)
        seq = B.calls(word, dimension, 64)
        cert = B.solve(seq, 64, dimension)
        optimum = B.check(seq, 64, dimension, cert)
        require(optimum == a * dimension + b, 'all-size invoice fixture')
        comparisons.append(dict(dimension=dimension, coordinate_optimum=old, field_optimum=optimum,
                                saved_moves=old - optimum, coordinate_origin_each=S.fixed_bill(coordinate_calls, 64, True)))
        head = 0
        seen = set()
        for call, choice in zip(seq, certificate['choices']):
            if len(call) == 2:
                head = 0
                continue
            key = tuple(call[3:5])
            if dimension in (1, 2) and key not in seen:
                counts = physical_fixture(B, T, C, word, call, dimension, head, choice, circuits[key], routes[key])
                for name in counts:
                    physical_totals[name] += counts[name]
                seen.add(key)
                physical_count += 1
            head = next(end for end, _, c in B.options(head, call, 64, dimension) if c == tuple(choice))
        if dimension in (1, 2):
            require(seen == set(routes), 'all physical templates')
    bad = copy.deepcopy(certificate)
    bad['layers'][2][0][1] += 1
    reject(lambda: B.check_affine(sequence, 64, bad), 'edge potential')
    bad = copy.deepcopy(certificate)
    bad['total'][0] += 1
    reject(lambda: B.check_affine(sequence, 64, bad), 'attaining path')
    bad_word = copy.deepcopy(word)
    i = next(i for i, e in enumerate(bad_word['program']) if e[0] == 'ADD')
    bad_word['program'][i][2] = bad_word['program'][i][1]
    reject(lambda: S.plan(bad_word, 1, 64), 'distinct operands')
    dirty = T.Tape([1] * 64)
    clean = T.Tape([0] * 64)
    reject(lambda: B.transfer(clean, dirty, 64), 'clean transfer destination')
    reject(lambda: B.transfer(clean, clean, 64), 'distinct transfer')
    summary = dict(schema=1, width=64, source_events=len(word['program']), scalar_events=len(sequence) - sum(len(c) == 2 for c in sequence),
                   owner_bits_per_dimension=2 * 64 * (word['public'] + word['owned_fields']),
                   clean_staging_bits_per_dimension=256, clean_carry_bits=1, finite_control_bits=2, tapes=4,
                   staging_moves=dict(D=a, constant=b), staging_reads_per_dimension=4 * transferred,
                   staging_writes_per_dimension=2 * transferred, local_physical_per_dimension=local_total,
                   combined_physical=dict(D=a + 6 * transferred + sum(local_total.values()), constant=b),
                   unimplemented_reset_bits_per_dimension=128 * sum(e[0] in ('INIT', 'CLEAR') for e in word['program']),
                   all_D_potential_states=sum(map(len, certificate['layers'])),
                   physical_fixtures=physical_count, metered_fixture_operations=physical_totals,
                   controls=5, comparisons=comparisons)
    p = HERE / 'RESULT.json'
    if write:
        p.write_text(json.dumps(summary, indent=2) + '\n')
    require(summary == json.loads(p.read_text()), 'retained result')
    print('PASS_P104_OWNER_SCALAR_STAGING', summary['combined_physical'], physical_count, 'literal fixtures; all positive D')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    main(parser.parse_args().write)
