#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Noise-lattice audit of two pinned QQ16 scalar projections, not native execution."""
from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = 'research/joint-query/certificate.json.gz'
PAYLOAD_SHA256 = '2efe83c59978aa9c0db2c3e4eccc14cbfdcd3c9ce499432601b5dd34083472ef'
SEED = 61
NONSCALAR = {'climb', 'native_line', 'adapter', 'residual_adapter', 'phase', 'cover_map'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def load_packet():
    pins = json.loads((HERE / 'SOURCES.json').read_text())
    pin = next(p for p in pins['files'] if p['path'] == SOURCE)
    raw = (ROOT / SOURCE).read_bytes()
    require(hashlib.sha256(raw).hexdigest() == pin['sha256'], 'source SHA256 mismatch')
    require(hashlib.sha1(f'blob {len(raw)}\0'.encode() + raw).hexdigest() == pin['git_blob'], 'source Git blob mismatch')
    plain = gzip.decompress(raw)
    require(hashlib.sha256(plain).hexdigest() == PAYLOAD_SHA256, 'payload SHA256 mismatch')
    return json.loads(plain)


def register(token):
    kind, i = token
    require(kind in ('L', 'C') and type(i) is int, 'invalid register')
    require(0 <= i < (704 if kind == 'L' else 8), 'register out of range')
    return i + (704 if kind == 'C' else 0)


def expand(packet, case):
    result = []
    for event in packet['programs'][case]:
        if event[0] == 'retained_core':
            result.extend(packet['core_words'][event[1]])
        elif event[0] in ('cover_sweep', 'private_sweep'):
            result.extend(event[2])
        else:
            result.append(event)
    for event in result:
        require(event[0] == 'scalar' or event[0] in NONSCALAR, f'unknown event {event[0]}')
    return result


def child_wire(event):
    if event[0] == 'climb':
        return register(['L', event[2]])
    if event[0] == 'native_line':
        return register(event[1])
    return None


def denominator_bits(value):
    d = value.denominator
    require(d & (d - 1) == 0, 'non-dyadic coefficient')
    return d.bit_length() - 1


def direct_sites(events):
    """No ignored adapter/map lies between the actual child and half-scalar."""
    sites = []
    for i, (a, b) in enumerate(zip(events, events[1:])):
        w = child_wire(a)
        if w is None or b[0] != 'scalar':
            continue
        gate = b[1]
        if gate[0] == 'add' and register(gate[2]) == w:
            coeff = Q(gate[3], gate[4])
            require(register(gate[1]) != w, 'self ADD unsupported')
        elif gate[0] == 'scale' and register(gate[1]) == w:
            coeff = Q(gate[2], gate[3])
        else:
            continue
        if coeff.denominator == 2:
            sites.append({'child_event': i, 'scalar_event': i + 1,
                          'child': a, 'scalar': b, 'coefficient': str(coeff)})
    return sites


def analyze(events):
    """All independent input and child-fault columns at every completed scalar cut.

    Exactly the scalar projection of PR3181: non-scalar operators are identities.
    The extra independent symbols are additive defects AFTER each child.
    """
    rows = [{j: Q(1)} for j in range(712)]
    origins = [{'kind': 'input', 'event': -1, 'wire': j} for j in range(712)]
    maxima = [{'bits': 0, 'event': -1, 'wire': j, 'coefficient': '1'} for j in range(712)]
    for i, event in enumerate(events):
        w = child_wire(event)
        if w is not None:
            k = len(origins)
            origins.append({'kind': event[0], 'event': i, 'wire': w})
            maxima.append({'bits': 0, 'event': i, 'wire': w, 'coefficient': '1'})
            rows[w][k] = Q(1)
            continue
        if event[0] != 'scalar':
            continue
        gate = event[1]
        op, w = gate[0], register(gate[1])
        if op == 'clear':
            rows[w] = {}
        elif op == 'scale':
            c = Q(gate[2], gate[3])
            rows[w] = {k: v * c for k, v in rows[w].items() if v * c}
        elif op == 'add':
            s, c = register(gate[2]), Q(gate[3], gate[4])
            require(s != w, 'self ADD unsupported')
            for k, v in rows[s].items():
                value = rows[w].get(k, Q(0)) + c * v
                if value:
                    rows[w][k] = value
                else:
                    rows[w].pop(k, None)
        else:
            raise ValueError(f'unknown scalar {op}')
        for k, value in rows[w].items():
            bits = denominator_bits(value)
            if bits > maxima[k]['bits']:
                maxima[k] = {'bits': bits, 'event': i, 'wire': w, 'coefficient': str(value)}
    child_maxima = maxima[712:]
    histogram = Counter(m['bits'] for m in child_maxima)
    max_child = max(range(712, len(origins)), key=lambda k: maxima[k]['bits'])
    max_input = max(range(712), key=lambda k: maxima[k]['bits'])
    sites = direct_sites(events)
    require(bool(sites), 'no direct child-to-fractional-scalar witness')
    selected = sites[SEED % len(sites)]
    coefficient = Q(selected['coefficient'])
    # In working-grid units, ideal source=2 and actual source=3 for a half ADD.
    require(coefficient.denominator == 2, 'selected site is not a half scalar')
    selected.update({'selection': f'{SEED} modulo {len(sites)}',
                     'working_grid': 'q = 2^(-p), any integer p >= 0',
                     'ideal_source_units': 2, 'child_defect_units': 1,
                     'actual_source_units': 3,
                     'ideal_output_units': str(2 * coefficient),
                     'actual_output_units': str(3 * coefficient)})
    require((2 * coefficient).denominator == 1 and (3 * coefficient).denominator == 2,
            'local grid escape not established')
    full = [{'origin': o, 'attainment': m} for o, m in zip(origins, maxima)]
    return {
        'event_count': len(events), 'event_counts': dict(sorted(Counter(e[0] for e in events).items())),
        'input_columns': 712, 'child_defect_columns': len(child_maxima),
        'scalar_cuts': sum(e[0] == 'scalar' for e in events),
        'input_guard_bits': maxima[max_input]['bits'],
        'child_guard_bits': maxima[max_child]['bits'],
        'child_guard_histogram': {str(k): v for k, v in sorted(histogram.items())},
        'input_attainment': full[max_input], 'child_attainment': full[max_child],
        'all_column_attainments_sha256': hashlib.sha256(canonical(full)).hexdigest(),
        'direct_adjacent_sites': len(sites), 'seed_selected_local_witness': selected,
    }


def generate():
    packet = load_packet()
    cases = {case: analyze(expand(packet, case)) for case in ('F_0', 'B_1_2')}
    return {
        'schema_version': 1, 'no_new_kappa': True, 'assignment_seed': SEED,
        'scope': 'All completed scalar cuts of two identity-nonscalar projections; independent additive child defects. Direct adjacent witnesses retain actual instruction bytes.',
        'source_payload_sha256': PAYLOAD_SHA256, 'cases': cases,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='create an absent RESULT.json')
    args = parser.parse_args()
    report = generate()
    result_path = HERE / 'RESULT.json'
    if args.write:
        with result_path.open('x') as out:
            out.write(json.dumps(report, indent=2, sort_keys=True) + '\n')
    else:
        require(report == json.loads(result_path.read_text()), 'receipt mismatch')
    cases = [report['cases'][name] for name in ('F_0', 'B_1_2')]
    inputs = ','.join(str(c['input_guard_bits']) for c in cases)
    children = ','.join(str(c['child_guard_bits']) for c in cases)
    print(f'PASS_QQ16_NOISE_LATTICE_AUDIT input_guards={inputs} child_guards={children} cases=F_0,B_1_2 no_new_kappa')


if __name__ == '__main__':
    main()
