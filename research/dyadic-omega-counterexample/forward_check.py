#!/usr/bin/env python3
"""Separate forward simulation of the entire 128-factor witness.

@CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
No import of verify.py, its phase recurrences, or a predecessor interpreter.
Positive words are built once and their inverse is a literal reversed list.
Monomials use base-(n+1) integer encodings, rather than backward tuple words.
"""
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def demand(value, label):
    if not value:
        raise ValueError(label)


def inverse(events):
    return [(a, b, f, -s) for a, b, f, s in events[::-1]]


def positive(n, x=0, y=1, scratch=2, offset=0):
    if n == 1:
        return [(x, y, offset, 1)]
    left = positive(n // 2, x, scratch, scratch + 1, offset)
    right = positive(n - n // 2, scratch, y, scratch + 1, offset + n // 2)
    return left + right + inverse(left) + inverse(right)


def decode(value, base):
    out = []
    while value:
        value, digit = divmod(value, base)
        demand(1 <= digit < base, 'nonzero monomial digit')
        out.append(digit - 1)
    return tuple(out)


def record(field, cut, register, base):
    polys = [dict() for _ in range(cut)]
    for (error, code), coefficient in field.items():
        polys[error][decode(code, base)] = coefficient
    profile = Counter(sum(abs(c) for c in p.values()) for p in polys if p)
    rows = [[i, [[list(w), p[w]] for w in sorted(p)]] for i, p in enumerate(polys)]
    return {'completed_leaves': cut, 'register': register,
            'profile': {str(j): profile[j] for j in sorted(profile)},
            'nonzero_channels': sum(profile.values()),
            'total_mass': sum(j * c for j, c in profile.items()),
            'channel_polynomials_sha256': sha256(json.dumps(rows, separators=(',', ':')).encode()).hexdigest()}


def forward(n, events, observations, common_error=False, negative_errors=(), mass_trace=None):
    fields = [dict() for _ in range((n - 1).bit_length() + 2)]
    base = n + 1
    observed = {}
    if mass_trace is not None:
        mass_trace.append([0] * len(fields))
    for i, (source, dest, factor, sign) in enumerate(events):
        demand(source != dest, 'distinct registers')
        for (error, monomial), coefficient in fields[source].items():
            key = (error, base * monomial + factor + 1)
            value = fields[dest].get(key, 0) + sign * coefficient
            if value:
                fields[dest][key] = value
            else:
                fields[dest].pop(key, None)
        injection = (0 if common_error else i, 0)
        injected = -1 if i in negative_errors else 1
        value = fields[dest].get(injection, 0) + injected
        if value:
            fields[dest][injection] = value
        else:
            fields[dest].pop(injection, None)
        if mass_trace is not None:
            mass_trace.append([sum(abs(c) for c in f.values()) for f in fields])
        for reg, label in observations.get(i + 1, []):
            observed[label] = record(fields[reg], i + 1, reg, base)
    return observed


def same(a, b, label):
    demand(json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True), label)


def rejected(action, label):
    try:
        action()
    except ValueError:
        return label
    raise ValueError('control accepted: ' + label)


def main():
    witness = json.loads((HERE / 'WITNESS.json').read_text())
    n = witness['factor_count']
    demand(type(n) is int and n == 128 and witness['height'] == 7, 'fixed witness domain')
    events = positive(n)
    demand(len(events) == 16384, 'full literal length')
    obs = {15018: [(8, 'omega')], 16042: [(3, 'new')]}
    # Continue through the full word; independent errors are never merged.
    actual = forward(n, events, obs)
    for label in ('new', 'omega'):
        same(actual[label], witness[label], 'full forward ' + label)
    demand(actual['new']['total_mass'] > actual['omega']['total_mass'], 'strict counterexample')
    # A simple four-event calibration fixes update side, inverse order and error timing.
    tiny = positive(2)
    demand(tiny == [(0, 2, 0, 1), (2, 1, 1, 1), (0, 2, 0, -1), (2, 1, 1, -1)],
           'handwritten word')
    calibration = forward(2, tiny, {4: [(0, 'source'), (1, 'target'), (2, 'scratch')]})
    demand([calibration[k]['total_mass'] for k in ('source', 'target', 'scratch')] == [0, 3, 2],
           'handwritten independent endpoint masses')
    upper_cases = 0
    scratch_attainment = False
    for h in range(5):
        nw = positive(2**h)
        left, right = [], []
        forward(2**h, nw, {}, mass_trace=left)
        forward(2**h, inverse(nw), {}, mass_trace=right)
        for t in range(len(nw) + 1):
            for reg in range(h + 2):
                value = left[t][reg] + right[-t - 1][reg]
                bound = (0 if reg == 0 else (2 * 4**h - 3**h if reg == 1
                                             else 2 * (4**h - 3**h)))
                demand(value <= bound, 'paired-prefix upper bound')
                upper_cases += 1
                scratch_attainment |= reg >= 2 and value == bound and bound > 0
    demand(scratch_attainment, 'scratch upper-bound equality control')
    controls = []
    altered = json.loads(json.dumps(actual['new'])); altered['profile']['7'] += 1
    controls.append(rejected(lambda: same(altered, witness['new'], 'altered profile'),
                             'changed_channel_multiplicity'))
    altered = json.loads(json.dumps(actual['new'])); altered['completed_leaves'] -= 1
    controls.append(rejected(lambda: same(altered, witness['new'], 'off-by-one receipt'),
                             'off_by_one_cut_receipt'))
    altered = json.loads(json.dumps(actual['new'])); altered['channel_polynomials_sha256'] = '0' * 64
    controls.append(rejected(lambda: same(altered, witness['new'], 'changed polynomial digest'),
                             'changed_signed_polynomial_digest'))
    # Run an actual semantically different interpreter: one common error symbol.
    small = positive(2)
    probe = {4: [(2, 'row')]}
    correct = forward(2, small, probe, negative_errors=(2,))['row']
    shared = forward(2, small, probe, common_error=True, negative_errors=(2,))['row']
    demand(shared['total_mass'] == 0 and correct['total_mass'] == 2,
           'shared opposite-error cancellation is effective')
    controls.append(rejected(lambda: same(shared, correct, 'independence lost'),
                             'actual_shared_error_interpreter'))
    print(json.dumps({'status': 'PASS_FORWARD_OMEGA_COUNTEREXAMPLE',
                      'witness_leaves_executed': len(events),
                      'full_signed_channel_digests_matched': 2,
                      'all_cut_paired_prefix_cases': upper_cases,
                      'new_mass': actual['new']['total_mass'],
                      'omega_mass': actual['omega']['total_mass'],
                      'negative_controls': controls}, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
