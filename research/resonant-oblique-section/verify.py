#!/usr/bin/env python3
"""Exact dyadic oblique section of the frozen resonant channel."""
import argparse
from collections import Counter, defaultdict
from fractions import Fraction
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
SOURCE = 'research/resonant-all-width-projector/TARGET.json'
PIN = 'e7df852b5c641f326ac67cd35cea8da6cfdd059fa12df1cf6fb758bb4206d684'
IDENTITY = (tuple(range(8)), (0,) * 8)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def even(word):
    p, q = word
    shift = 2 * (q[0] // 2)
    return p, tuple((x - shift) % 4 for x in q)


def multiply(a, b):
    p, q = a
    r, s = b
    return even((tuple(p[j] for j in r), tuple((s[j] + q[r[j]]) % 4 for j in range(8))))


def inverse(a):
    p, q = a
    r, s = [0] * 8, [0] * 8
    for j, k in enumerate(p):
        r[k], s[k] = j, -q[j] % 4
    return even((tuple(r), tuple(s)))


def convolution(a, b):
    out = defaultdict(int)
    for g, x in a.items():
        for h, y in b.items():
            out[multiply(g, h)] += x * y
    return {g: x for g, x in out.items() if x}


def free_word(word):
    p, q = word
    if len(p) != 8 or len(q) != 8 or any(type(x) is not int for x in p) or sorted(p) != list(range(8)) or any(type(x) is not int or not 0 <= x < 4 for x in q):
        return False
    shift = p[0]
    columns = [p[1 << k] ^ shift for k in range(3)]
    if any(p[j] != shift ^ columns[0] * (j & 1) ^ columns[1] * ((j >> 1) & 1)
           ^ columns[2] * ((j >> 2) & 1) for j in range(8)):
        return False
    coefficients = list(q)
    for bit in (1, 2, 4):
        for j in range(8):
            if j & bit:
                coefficients[j] = (coefficients[j] - coefficients[j ^ bit]) % 4
    return coefficients[7] == 0 and all(coefficients[j] % 2 == 0 for j in (3, 5, 6))


def load_channel():
    raw = (ROOT / SOURCE).read_bytes()
    need(hashlib.sha256(raw).hexdigest() == PIN, 'source hash mismatch')
    records = json.loads(raw)
    actual = {}
    for record in records:
        g = tuple(record['permutation']), tuple(record['phase_i'])
        need(g not in actual and free_word(g), 'source free monomial')
        need(record['coefficient'] in ('1/16', '-1/16'), 'source scalar')
        actual[g] = 1 if record['coefficient'] == '1/16' else -1
    need(len(actual) == 256, 'source support')
    # Equal actual signs prove that the channel vanishes at every odd width.
    for (p, q), value in actual.items():
        need(actual.get((p, tuple((s + 2) % 4 for s in q))) == value, 'odd cancellation')
    quotient = defaultdict(int)
    for g, value in actual.items():
        quotient[even(g)] += value
    need(len(quotient) == 128 and set(quotient.values()) == {-2, 2}, 'even target quotient')
    a = min(quotient)
    channel = {multiply(inverse(a), g): value // 2 for g, value in quotient.items()}
    need(len(channel) == 128, 'normalized channel support')
    return records, a, channel


def stabilizer(channel, left):
    first = min(channel)
    candidates = {multiply(g, inverse(first)) if left else multiply(inverse(first), g) for g in channel}
    opposite = {g: -v for g, v in channel.items()}
    result = []
    for h in sorted(candidates):
        translated = {multiply(h, g) if left else multiply(g, h): v for g, v in channel.items()}
        if translated == channel:
            result.append((h, 1))
        elif translated == opposite:
            result.append((h, -1))
    return result


def expand_section(channel, recipe):
    left, right = stabilizer(channel, True), stabilizer(channel, False)
    need((len(left), len(right)) == (32, 16), 'signed stabilizer sizes')
    denominator = recipe['D_denominator']
    need(type(denominator) is int and denominator == 16384, 'section denominator')
    need(len(recipe['corners']) == 30, 'corner recipe size')
    result = defaultdict(int)
    for record in recipe['corners']:
        g = tuple(record['permutation']), tuple(record['phase_i'])
        value = record['numerator']
        need(type(value) is int and value != 0 and free_word(g) and even(g) == g, 'corner coefficient/word')
        orbit = defaultdict(int)
        for r, x in right:
            rg = multiply(r, g)
            for l, y in left:
                orbit[multiply(rg, l)] += x * y
        multiplicities = set(abs(v) for v in orbit.values())
        need(len(multiplicities) == 1 and 0 not in multiplicities, 'signed corner cancellation')
        multiplicity = multiplicities.pop()
        for h, v in orbit.items():
            result[h] += value * (v // multiplicity)
    result = {g: v for g, v in result.items() if v}
    need(all(free_word(g) for g in result), 'emitted monomial outside free alphabet')
    return result, denominator


def check_identity(channel, section, denominator):
    dc = convolution(section, channel)
    need(convolution(channel, dc) == {g: denominator * v for g, v in channel.items()},
         'coefficientwise C D C = C failed')
    return dc


def reject(call, label):
    try:
        call()
    except ValueError:
        return label
    raise ValueError('mutation accepted: ' + label)


def verify():
    records, a, channel = load_channel()
    recipe = json.loads((HERE / 'SECTION.json').read_text())
    anchor = tuple(recipe['anchor']['permutation']), tuple(recipe['anchor']['phase_i'])
    need(free_word(anchor) and anchor == a, 'source anchor')
    section, denominator = expand_section(channel, recipe)
    dc = check_identity(channel, section, denominator)
    need(len(section) == 1920 and len(dc) == 5408, 'section/projector support')
    b = {multiply(g, inverse(a)): v for g, v in section.items()}
    need(len(b) == 1920 and all(free_word(g) for g in b), 'actual decoder words')
    need(max(map(abs, b.values())) == 8 and any(abs(v) == 1 for v in b.values()), 'primitive dyadic numerator')
    norm = Fraction(sum(map(abs, b.values())), 2048)
    need(norm == Fraction(113, 32), 'all-width decoder norm bound')
    changed = dict(section)
    changed[next(iter(changed))] += 1
    controls = [reject(lambda: check_identity(channel, changed, denominator), 'changed_section_coefficient'),
                reject(lambda: check_identity(channel, section, denominator + 1), 'changed_denominator')]
    quarter = tuple(range(8)), (1,) * 8
    minus = tuple(range(8)), (2,) * 8
    need(even(quarter) != IDENTITY and even(minus) == IDENTITY, 'central quotient scope')
    controls.append('retain_quarter_phase')
    need(not free_word((tuple(range(8)), (0, 0, 0, 0, 0, 0, 0, 1))), 'cubic phase rejection')
    controls.append('reject_nonfree_cubic_phase')
    need(not free_word(((False, 1, 2, 3, 4, 5, 6, 7), (0,) * 8)), 'typed address rejection')
    controls.append('reject_boolean_address')
    return {'status': 'PASS_RESONANT_OBLIQUE_SECTION', 'source_sha256': PIN,
            'actual_target_terms': len(records), 'even_target_terms': len(channel),
            'left_signed_stabilizer': 32, 'right_signed_stabilizer': 16,
            'nonzero_corner_terms': len(recipe['corners']), 'D_denominator': denominator,
            'decoder_terms': len(b), 'decoder_common_denominator': 2048,
            'decoder_numerator_histogram': {str(k): v for k, v in sorted(Counter(b.values()).items())},
            'decoder_norm_upper_bound': str(norm), 'oblique_projector_terms': len(dc),
            'identity': 'A_f B_f A_f = A_f for every positive integer f',
            'operator_claim': 'B_f A_f is idempotent with kernel equal to kernel(A_f)',
            'controls': controls, 'new_kappa': False, 'complete_supplier': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = verify()
    path = HERE / 'RESULT.json'
    if args.write:
        path.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    else:
        need(json.dumps(json.loads(path.read_text()), sort_keys=True) == json.dumps(result, sort_keys=True), 'typed receipt mismatch')
    print(result['status'])


if __name__ == '__main__':
    main()
