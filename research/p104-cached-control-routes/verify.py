#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Ali Romman with substantial OpenAI Codex assistance.
"""Check source circuits, cache potentials, literal routes and physical bills."""
import argparse
from collections import Counter
import copy
from fractions import Fraction
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import random

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
            require(hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256'], 'live source pin')
    for row in json.loads((HERE / 'ORIGINS.json').read_text()):
        raw = (HERE / row['path']).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == row['sha256'], 'vendor source pin')
        require(hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == row['git_blob'], 'vendor blob pin')


def route_invariant(width, gates, route):
    """Check symbolic cell tags independently of the optimizer's states."""
    heads = [0, 0, 0]
    tags = [None, None]
    index = 0
    for op, first, second in route:
        if op == 'move':
            require(first in (0, 1, 2) and second in (-1, 1), 'unit move')
            heads[first] += second
            require(0 <= heads[first] < (width if first < 2 else 1), 'physical ribbon bound')
        elif op == 'xor':
            wire = second * width + heads[second]
            if tags[first] is None:
                tags[first] = wire
            else:
                require(tags[first] == wire, 'uncompute unchanged cell')
                tags[first] = None
        elif op == 'flipmask':
            require(index < len(gates), 'no extra gate')
            gate = gates[index]
            target = first * width + heads[first]
            require(target == gate[-1], 'literal target')
            require(target not in tags, 'no stale cached target')
            require(second in (1, 2, 3), 'control mask')
            used = [tags[j] for j in range(2) if second & (1 << j)]
            require(None not in used and sorted(used) == sorted(gate[:-1]), 'literal gate controls')
            index += 1
        else:
            raise ValueError('instruction domain')
    require(index == len(gates) and tags == [None, None], 'complete gates and cache return')
    require(heads == [0, 0, 0], 'complete head return')


def direct(width, gates, values):
    bits = [(v >> j) & 1 for v in values for j in range(width)] + [0]
    for gate in gates:
        bits[gate[-1]] ^= int(all(bits[w] for w in gate[:-1]))
    require(bits[-1] == 0, 'logical carry return')
    return tuple(sum(bits[b * width + j] << j for j in range(width)) for b in range(2))


def fixtures(tape, cache, width, gates, route, oldroute, op, coefficient):
    rng = random.Random(op + coefficient)
    cases = [(0, 0), (-1, -1), (1, 1), (-(1 << 63), (1 << 63) - 1)]
    cases += [(rng.randrange(-(1 << 63), 1 << 63), rng.randrange(-(1 << 63), 1 << 63)) for _ in range(3)]
    cases += [(32, 64), (-64, 96), (224, -160), (0, 32)]
    for index, values in enumerate(cases):
        tapes = [tape.Tape((v >> j) & 1 for j in range(width)) for v in values] + [tape.Tape((0,))]
        observed = cache.run(route, tapes)
        result = tuple(sum(bit << j for j, bit in enumerate(t.snapshot())) for t in tapes[:2])
        require(result == direct(width, gates, values) and tapes[2].snapshot() == (0,), 'literal circuit endpoint')
        baseline = [tape.Tape((v >> j) & 1 for j in range(width)) for v in values] + [tape.Tape((0,))]
        require(tape.run_route(width, oldroute, baseline)['components'] == result, 'baseline route endpoint')
        require(observed == cache.counts(route), 'fixture bill')
        if index >= 7 and (op != 'COPY' or values[0] == 0):
            c = Fraction(coefficient)
            if op == 'ADD':
                expected = (values[0] + c * values[1], values[1])
            elif op == 'SCALE':
                expected = tuple(c * v for v in values)
            else:
                expected = (values[1], values[1])
            require(all(Fraction(v).denominator == 1 for v in expected), 'aligned fixture')
            require(result == tuple(int(v) % (1 << width) for v in expected), 'rational fixture endpoint')
    return len(cases)


def rejected(action, expected):
    try:
        action()
    except (ValueError, IndexError) as error:
        require(expected in str(error), 'control rejected for wrong reason: ' + str(error))
        return
    raise ValueError('control accepted: ' + expected)


def main(write=False):
    authenticate()
    cache = load('control_cache', HERE / 'cache.py')
    tape = load('source_tape', ROOT / 'research/rank7-paired-scale-routing/route.py')
    rows = json.loads(gzip.decompress((HERE / 'inputs/CIRCUITS64.json.gz').read_bytes()))
    word = json.loads(gzip.decompress((ROOT / 'research/p104-helper470-twin-rung-removal/WORD.json.gz').read_bytes()))
    occurrences = Counter()
    resets = 0
    for event in word['program']:
        op = event[0]
        if op in ('ADD', 'COPY'):
            occurrences[(op, str(Fraction(event[3])))] += 2
        elif op == 'SCALE':
            occurrences[(op, str(Fraction(event[2])))] += 1
        elif op in ('INIT', 'CLEAR'):
            resets += 128
    require(set(occurrences) == {(op, c) for op, c, _ in rows} and len(rows) == 43, 'all source templates')
    cert_path = HERE / 'CERTIFICATES.json.gz'
    if write:
        certs = [cache.optimize(64, gates) for _, _, gates in rows]
        cert_path.write_bytes(gzip.compress(json.dumps(certs, separators=(',', ':')).encode(), mtime=0))
    certs = json.loads(gzip.decompress(cert_path.read_bytes()))
    require(len(certs) == len(rows), 'certificate count')
    totals = {policy: dict(moves=0, reads=0, writes=0) for policy in ('baseline', 'cached')}
    details = []
    certificates_states = 0
    max_states = 0
    fixture_count = 0
    literal_hash = hashlib.sha256()
    for (op, c, gates), cert in zip(rows, certs):
        optimum = cache.check_certificate(64, gates, cert)
        route = cache.compile_route(64, gates, cert)
        route_invariant(64, gates, route)
        baseline = tape.compile_route(64, gates)
        old, new = tape.counters(baseline), cache.counts(route)
        require(sum(new.values()) == optimum <= sum(old.values()), 'physical improvement')
        require(new['writes'] == old['writes'] == len(gates), 'same target writes')
        fixture_count += fixtures(tape, cache, 64, gates, route, baseline, op, c)
        literal_hash.update(json.dumps([op, c, route], separators=(',', ':')).encode())
        for name in new:
            totals['baseline'][name] += occurrences[(op, c)] * old[name]
            totals['cached'][name] += occurrences[(op, c)] * new[name]
        certificates_states += sum(map(len, cert['layers']))
        max_states = max(max_states, max(map(len, cert['layers'])))
        details.append(dict(op=op, coefficient=c, occurrences=occurrences[(op, c)], gates=len(gates), baseline=old, cached=new))
    gates, cert = rows[0][2], certs[0]
    bad = copy.deepcopy(cert)
    bad['total'] += 1
    rejected(lambda: cache.check_certificate(64, gates, bad), 'terminal potential')
    bad = copy.deepcopy(cert)
    bad['layers'][1].pop()
    rejected(lambda: cache.check_certificate(64, gates, bad), 'edge potential')
    route = cache.compile_route(64, gates, cert)
    rejected(lambda: route_invariant(64, gates, route[:-1]), 'cache return')
    rejected(lambda: route_invariant(64, gates, route + [('move', 0, 1)]), 'head return')
    broken = list(route)
    i = next(i for i, r in enumerate(broken) if r[0] == 'flipmask')
    broken[i] = ('flipmask', broken[i][1], 3)
    rejected(lambda: route_invariant(64, gates, broken), 'literal gate controls')
    stale = [('xor', 0, 0), ('xor', 1, 1), ('flipmask', 0, 2)]
    rejected(lambda: route_invariant(64, [(64, 0)], stale), 'stale cached target')
    result = dict(schema=1, width=64, source_events=len(word['program']), templates=len(rows),
                  scalar_circuit_calls=sum(occurrences.values()), physical=totals,
                  total_saved=sum(totals['baseline'].values()) - sum(totals['cached'].values()),
                  separate_unimplemented_bit_resets=resets, clean_carry_bits=1, finite_control_bits=2,
                  certified_states=certificates_states, maximum_layer_states=max_states,
                  literal_route_sha256=literal_hash.hexdigest(), paired_physical_fixtures=fixture_count,
                  negative_controls=6, details=details)
    result_path = HERE / 'RESULT.json'
    if write:
        result_path.write_text(json.dumps(result, indent=2) + '\n')
    require(result == json.loads(result_path.read_text()), 'retained receipt')
    print('PASS_P104_CACHED_CONTROL_ROUTES', result['total_saved'], 'physical operations saved;', fixture_count, 'paired fixtures')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    main(parser.parse_args().write)
