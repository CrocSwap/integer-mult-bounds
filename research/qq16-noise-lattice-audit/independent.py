#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Separate dense single-channel and reverse-dual checks; no primary imports."""
import gzip
import hashlib
import json
from fractions import Fraction
from pathlib import Path

BASE = Path(__file__).resolve().parent
CERT = BASE.parents[1] / 'research/joint-query/certificate.json.gz'
CERT_HASH = 'a5ed85fac5ebf3c091482a113ab0d351eb5a7892fe2841a35e16017ec1ff49f7'


def check(ok, message):
    if not ok:
        raise ValueError(message)


def wire(token):
    return token[1] if token[0] == 'L' else 704 + token[1]


def sequence(packet, name):
    for item in packet['programs'][name]:
        if item[0] == 'retained_core':
            yield from packet['core_words'][item[1]]
        elif item[0] in ['cover_sweep', 'private_sweep']:
            yield from item[2]
        else:
            yield item


def forward_channel(events, origin):
    values = [Fraction(0) for _ in range(712)]
    if origin['event'] == -1:
        values[origin['wire']] = Fraction(1)
    peak = 0
    snapshots = {}
    for t, event in enumerate(events):
        if event[0] == 'scalar':
            g = event[1]
            d = wire(g[1])
            if g[0] == 'clear':
                values[d] = Fraction(0)
            elif g[0] == 'scale':
                values[d] *= Fraction(g[2], g[3])
            elif g[0] == 'add':
                values[d] += values[wire(g[2])] * Fraction(g[3], g[4])
            else:
                raise ValueError('unknown operation')
            peak = max(peak, values[d].denominator.bit_length() - 1)
            snapshots[(t, d)] = values[d]
        if t == origin['event']:
            values[origin['wire']] += 1
    return peak, snapshots


def reverse_coefficient(events, origin, attainment):
    dual = [Fraction(0) for _ in range(712)]
    dual[attainment['wire']] = Fraction(1)
    for t in range(attainment['event'], origin['event'], -1):
        e = events[t]
        if e[0] != 'scalar':
            continue
        g = e[1]
        d = wire(g[1])
        if g[0] == 'clear':
            dual[d] = Fraction(0)
        elif g[0] == 'scale':
            dual[d] *= Fraction(g[2], g[3])
        elif g[0] == 'add':
            dual[wire(g[2])] += dual[d] * Fraction(g[3], g[4])
    return dual[origin['wire']]


def verify(report, packet):
    checked = 0
    for name, record in report['cases'].items():
        events = list(sequence(packet, name))
        check(len(events) == record['event_count'], 'event count')
        for key in ('input_attainment', 'child_attainment'):
            witness = record[key]
            origin, endpoint = witness['origin'], witness['attainment']
            if origin['event'] >= 0:
                child = events[origin['event']]
                check(child[0] in ('climb', 'native_line'), 'fault is not at a child')
                target = child[2] if child[0] == 'climb' else wire(child[1])
                check(target == origin['wire'], 'fault is not on child wire')
            at = events[endpoint['event']]
            check(at[0] == 'scalar' and wire(at[1][1]) == endpoint['wire'], 'attainment is not a scalar destination')
            peak, snapshots = forward_channel(events, origin)
            expected = Fraction(endpoint['coefficient'])
            check(snapshots[(endpoint['event'], endpoint['wire'])] == expected, 'forward coefficient')
            check(reverse_coefficient(events, origin, endpoint) == expected, 'reverse coefficient')
            check(peak == endpoint['bits'], 'whole-channel guard maximum')
            check((expected * (1 << peak)).denominator == 1, 'sufficient guard')
            check(peak > 0 and (expected * (1 << (peak - 1))).denominator == 2, 'one fewer guard must fail')
            # Check the entire projected trajectory on this channel, not just the endpoint.
            check(all((v * (1 << peak)).denominator == 1 for v in snapshots.values()), 'channel guard closure')
            checked += 1
        local = record['seed_selected_local_witness']
        check(events[local['child_event']] == local['child'], 'child bytes')
        check(events[local['scalar_event']] == local['scalar'], 'scalar bytes')
        check(local['scalar_event'] == local['child_event'] + 1, 'not adjacent')
        child = local['child']
        src = child[2] if child[0] == 'climb' else wire(child[1])
        gate = local['scalar'][1]
        check(gate[0] == 'add' and wire(gate[2]) == src, 'wrong child consumer')
        factor = Fraction(gate[3], gate[4])
        check(factor == Fraction(-1, 2), 'wrong half ADD')
        for p in [0, 4, 17, 29, 61, 93, 256]:
            q = Fraction(1, 1 << p)
            clean, noisy = factor * 2 * q, factor * 3 * q
            check((clean / q).denominator == 1, 'ideal grid')
            check((noisy / q).denominator == 2, 'noise did not leave grid')
            check((noisy / (q / 2)).denominator == 1, 'one-bit local repair')
        checked += 1
    return checked


def main():
    raw = CERT.read_bytes()
    check(hashlib.sha256(raw).hexdigest() == CERT_HASH, 'source bytes')
    packet = json.loads(gzip.decompress(raw))
    report = json.loads((BASE / 'RESULT.json').read_text())
    count = verify(report, packet)
    print(f'PASS_QQ16_NOISE_INDEPENDENT witnesses={count} forward_dense_and_reverse_dual')


if __name__ == '__main__':
    main()
