#!/usr/bin/env python3
"""Joint Gaussian-divisibility certificate for the pinned P104 physical dual.

New census and proof application by David with substantial OpenAI Codex
assistance. Retained arithmetic: Nick Petalas's PR2772. Apache-2.0.
Native correctness and tensor lifting are inherited premises.
"""
import argparse
from collections import Counter
from fractions import Fraction
import gzip
import hashlib
import json
from pathlib import Path
from types import ModuleType

HERE = Path(__file__).resolve().parent
CHART = 'Delta_W = conjugate(Gamma_W) = Gamma_W^(-T)'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'duplicate JSON key')
        result[key] = value
    return result


def decode(raw):
    return json.loads(raw, object_pairs_hook=unique)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'))


def load_inputs(directory=HERE):
    manifest = decode((directory / 'SOURCES.json').read_bytes())
    pins = manifest['vendored_files']
    require(len(pins) == 5, 'retained source inventory')
    verified = {}
    for pin in pins:
        data = (directory / pin['local']).read_bytes()
        require(hashlib.sha256(data).hexdigest() == pin['sha256'], 'source SHA256')
        header = b'blob ' + str(len(data)).encode() + b'\0'
        require(hashlib.sha1(header + data).hexdigest() == pin['git_blob'],
                'source Git blob')
        verified[pin['local']] = data
    word = decode(verified['inputs/WORD.json'])
    raw = gzip.decompress(verified['inputs/NATIVE.json.gz'])
    require(len(raw) < 4_000_000, 'native payload capacity')
    archive = decode(raw)
    require(word['chart'] == archive['chart'] == CHART, 'physical chart contract')
    require(len(word['program']) == 5398 and len(archive['transports']) == 1245,
            'word and native dimensions')
    # Authenticate every retained input before importing retained executable code.
    path = directory / 'inputs/predecessor_arithmetic.py'
    arithmetic = ModuleType('p104_retained_arithmetic')
    # Compile authenticated source bytes directly: -B alone still reads .pyc.
    exec(compile(verified['inputs/predecessor_arithmetic.py'], str(path),
                 'exec', dont_inherit=True),
         arithmetic.__dict__)
    return word, archive, arithmetic


def space(frame):
    require(isinstance(frame, list) and len(frame) <= 9, 'frame dimension')
    span = {0}
    for vector in frame:
        require(type(vector) is int and 0 < vector < 512 and vector not in span,
                'independent binary frame')
        span |= {value ^ vector for value in span}
    return span


def valuation(coefficient):
    require(coefficient != 0 and
            coefficient.denominator & (coefficient.denominator - 1) == 0,
            'nonzero dyadic coefficient')
    numerator = abs(coefficient.numerator)
    return ((numerator & -numerator).bit_length() -
            coefficient.denominator.bit_length())


def census(word):
    initial = word['initial_frames']
    require(len(initial) == 358, 'all public inputs')
    for frame in initial.values():
        space(frame)
    rows = {name: {name: Fraction(1)} for name in initial}
    frames = {name: list(frame) for name, frame in initial.items()}
    forms, witnesses, counts = {}, {}, Counter()
    peak, observations, terms = Fraction(0), 0, 0

    def observe(role, index, extra=0):
        nonlocal peak, observations, terms
        observations += 1
        peak = max(peak, sum(map(abs, rows[role].values()), Fraction(0)))
        for source, coefficient in rows[role].items():
            terms += 1
            gates = len(frames[role]) + len(initial[source]) + extra
            intercept = -valuation(coefficient)
            if intercept > forms.get(gates, -100):
                forms[gates] = intercept
                witnesses[gates] = {'event': index, 'role': role, 'source': source,
                                    'coefficient': str(coefficient),
                                    'entrance_dimension': len(frames[role]),
                                    'initial_dimension': len(initial[source]),
                                    'native_rank': extra}

    for name in initial:
        observe(name, -1)
    for index, event in enumerate(word['program']):
        op, role = event[:2]
        counts[op] += 1
        if op == 'transport':
            _, _, old, new, rank = event
            a, b = space(old), space(new)
            require(frames[role] == old and (a < b or b < a), 'nested transport')
            require(type(rank) is int and rank == abs(len(old) - len(new)),
                    'transport rank')
            observe(role, index, rank)
            frames[role] = new
        elif op == 'add':
            _, _, source, factor, frame = event
            require(role != source and frames[role] == frames[source] == frame,
                    'common ADD chart')
            factor = Fraction(factor)
            valuation(factor)
            for source_input, coefficient in rows[source].items():
                value = rows[role].get(source_input, Fraction(0)) + factor * coefficient
                if value:
                    rows[role][source_input] = value
                else:
                    rows[role].pop(source_input, None)
        elif op == 'sign':
            require(event[2] == '-1' and frames[role] == event[3], 'sign chart')
            rows[role] = {source: -value for source, value in rows[role].items()}
        elif op == 'zero':
            require(role == 'C' and role not in rows, 'private allocation')
            space(event[2])
            rows[role], frames[role] = {}, event[2]
        else:
            require(op == 'erase' and role == 'C' and not rows[role]
                    and frames[role] == event[2], 'exact private erasure')
            del rows[role], frames[role]
        if op != 'erase':
            observe(role, index)
    require(frames == word['final_frames'], 'final charts')
    for role, row in rows.items():
        if not role.startswith('X'):
            require(row == {role: Fraction(1)}, 'arbitrary dirty restoration')
        else:
            require(row.get(role) == 1 and
                    all(s == role or s.startswith('Y') for s in row), 'dual shear')
    require(counts['erase'] == 8 and peak == Fraction(127, 2), 'retained range')
    require(forms == {0: 1, **{k: 2 for k in range(1, 10)}, 10: 0, 15: 2},
            'joint gate-count envelope')
    require(witnesses[15] == {'event': 2031, 'role': 'C', 'source': 'Y27',
                             'coefficient': '1/4', 'entrance_dimension': 8,
                             'initial_dimension': 0, 'native_rank': 7},
            'limiting certificate term')
    return rows, {'gate_counts': {str(k): v for k, v in sorted(forms.items())},
                  'limiting_term': witnesses[15], 'observations': observations,
                  'nonzero_term_visits': terms, 'logical_l1': str(peak),
                  'counts': dict(sorted(counts.items()))}


def bind_native(word, archive, arithmetic):
    uses, plans, profile = {}, {}, Counter()
    for record in archive['transports']:
        recipe = record['recipe']
        rank = recipe['rank']
        require(type(rank) is int and 1 <= rank <= 8, 'native rank')
        require(set(recipe) == {'rank', 'left', 'right'}, 'native factorization')
        key = canonical(recipe)
        if key not in plans:
            plans[key] = (arithmetic.mapping(recipe['right']), rank,
                          arithmetic.mapping(recipe['left']))
        for index in record['events']:
            require(type(index) is int and 0 <= index < 5398 and index not in uses,
                    'unique native occurrence')
            event = word['program'][index]
            require(event == ['transport', event[1], record['old'], record['new'], rank],
                    'native occurrence binding')
            uses[index] = plans[key]
            profile[rank] += 1
    require(set(uses) == {i for i, e in enumerate(word['program'])
                         if e[0] == 'transport'}, 'complete native coverage')
    return uses, {str(k): v for k, v in sorted(profile.items())}


def execute(word, uses, start, arithmetic):
    states, erasures = dict(start), []
    for index, event in enumerate(word['program']):
        op, role = event[:2]
        if op == 'transport':
            if states[role] == arithmetic.ZERO:
                continue
            right, rank, left = uses[index]
            vector = arithmetic.monomial(states[role], right)
            for bit in range(rank):
                vector = arithmetic.stage(vector, bit)
            states[role] = arithmetic.monomial(vector, left)
        elif op == 'add':
            states[role] = arithmetic.add(states[role], states[event[2]], event[3])
        elif op == 'sign':
            states[role] = tuple((-a, -b) for a, b in states[role])
        elif op == 'zero':
            require(role not in states, 'physical allocation')
            states[role] = arithmetic.ZERO
        else:
            require(op == 'erase' and states[role] == arithmetic.ZERO,
                    'physical zero erasure')
            erasures.append(index)
            del states[role]
    return states, erasures


def fixture(word, uses, rows, arithmetic, dense, guard=10):
    scale = 1 << guard
    start = {name: arithmetic.ZERO for name in word['initial_frames']}
    if dense:
        for j, name in enumerate(start):
            start[name] = tuple((scale * ((x + 3*j) % 7 - 3),
                                 scale * ((2*x + j) % 5 - 2)) for x in range(512))
    else:
        start['Y2'] = ((scale, 0),) + arithmetic.ZERO[1:]
    actual, erasures = execute(word, uses, start, arithmetic)
    logical = {s: arithmetic.chart(v, word['initial_frames'][s], inverse=True)
               for s, v in start.items()}
    for role, row in rows.items():
        expected = arithmetic.ZERO
        for source, coefficient in row.items():
            expected = arithmetic.add(expected, logical[source], coefficient)
        expected = arithmetic.chart(expected, word['final_frames'][role])
        require(actual[role] == expected, 'canonical-chart endpoint oracle')
    require(len(erasures) == 8, 'all physical erasures')
    if not dense:
        require(actual['X0'][0] == (-scale//64, scale//64), 'credited Y2 witness')
    return {'input': 'dense all-public' if dense else 'Y2=delta_0',
            'guard_bits': guard, 'matched_real_coordinates': 358 * 512 * 2,
            'erase_events': erasures}


def gaussian_lemma():
    # Independent Fraction calculation of the distinct-axis extremal entry.
    real, imag = Fraction(1), Fraction(0)
    guards = []
    for gates in range(19):
        if gates:
            real, imag = (real - imag) / 2, (real + imag) / 2
        require(all((v * 2**((gates+1)//2)).denominator == 1
                    for v in (real, imag)), 'Gaussian factor divisibility')
        require(max(v.denominator.bit_length()-1 for v in (real, imag))
                == (gates+1)//2, 'distinct-axis sharp factor count')
        guards.append((gates+1)//2)
    return guards


def expect_failure(action, message):
    try:
        action()
    except ValueError as error:
        require(message in str(error), 'wrong rejection: ' + str(error))
        return
    raise ValueError('fault accepted: ' + message)


def run():
    word, archive, arithmetic = load_inputs()
    rows, evidence = census(word)
    uses, profile = bind_native(word, archive, arithmetic)
    fixtures = [fixture(word, uses, rows, arithmetic, dense) for dense in (False, True)]
    expect_failure(lambda: fixture(word, uses, rows, arithmetic, False, 6),
                   'inexact internal halving')
    return {'schema_version': 1, 'status': 'PASS_P104_JOINT_PREFIX_GRID',
            'sufficient_extra_fractional_bits': 'ceil(15*lambda/2)+2',
            'one_layer_bits': 10, 'predecessor_one_layer_bits': 15,
            'census': evidence, 'native_profile': profile,
            'gaussian_factor_guards_0_through_18': gaussian_lemma(),
            'fixtures': fixtures, 'undergrid_control': 'six bits rejected',
            'native_correctness': 'inherited', 'minimality_claimed': False,
            'no_new_kappa': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    result = run()
    require(canonical(result) == canonical(decode((HERE / 'RESULT.json').read_bytes())),
            'complete typed receipt')
    if args.out:
        with args.out.open('x', encoding='utf-8') as stream:
            stream.write(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
