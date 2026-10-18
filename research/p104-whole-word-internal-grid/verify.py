"""Whole-word internal precision certificate, without predecessor imports."""
import argparse
from collections import Counter
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from arithmetic import N, ZERO, add, chart, mapping, native, need, rotate, stage

HERE = Path(__file__).resolve().parent


def unique(pairs):
    out = {}
    for key, value in pairs:
        need(key not in out, 'duplicate JSON key')
        out[key] = value
    return out


def read(path):
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=unique)


def inputs():
    pins = read(HERE / 'SOURCES.json')['vendored_files']
    need(len(pins) == 4, 'retained source inventory')
    for pin in pins:
        data = (HERE / pin['local']).read_bytes()
        need(hashlib.sha256(data).hexdigest() == pin['sha256'], 'source SHA256')
        blob = hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        need(blob == pin['git_blob'], 'source Git blob')
    word = read(HERE / 'inputs/WORD.json')
    raw = gzip.decompress((HERE / 'inputs/NATIVE.json.gz').read_bytes())
    need(len(raw) < 4_000_000, 'native payload capacity')
    recipes = json.loads(raw, object_pairs_hook=unique)
    need(word['chart'] == recipes['chart'] ==
         'Delta_W = conjugate(Gamma_W) = Gamma_W^(-T)', 'physical chart')
    need(len(word['program']) == 5398 and len(recipes['transports']) == 1245,
         'source dimensions')
    return word, recipes


def bind_native(word, archive):
    uses, ranks = {}, Counter()
    for item in archive['transports']:
        recipe = item['recipe']
        rank = recipe['rank']
        need(type(rank) is int and 1 <= rank <= 8, 'native rank range')
        need(set(recipe) == {'rank', 'left', 'right'}, 'native factorization')
        mapping(recipe['left'])
        mapping(recipe['right'])
        for index in item['events']:
            need(type(index) is int and 0 <= index < 5398 and index not in uses,
                 'unique native occurrence')
            event = word['program'][index]
            need(event == ['transport', event[1], item['old'], item['new'], rank],
                 'native occurrence binding')
            uses[index] = recipe
            ranks[rank] += 1
    need(set(uses) == {i for i, e in enumerate(word['program']) if e[0] == 'transport'},
         'complete transport coverage')
    return uses, dict(sorted(ranks.items()))


def valuation(value):
    need(value != 0 and value.denominator & (value.denominator-1) == 0,
         'nonzero dyadic')
    n = abs(value.numerator)
    return (n & -n).bit_length()-1-(value.denominator.bit_length()-1)


def frame_space(frame):
    need(len(frame) <= 9, 'frame dimension')
    space = {0}
    for x in frame:
        need(type(x) is int and 0 < x < N and x not in space,
             'independent binary frame')
        space |= {y ^ x for y in space}
    return space


def observe(rows, frames, initial, role, forms):
    row = rows[role]
    for source, coefficient in row.items():
        slope = len(frames[role]) + len(initial[source])
        forms[slope] = max(forms.get(slope, -100), -valuation(coefficient))
    return sum(map(abs, row.values()), Q(0)), len(row)


def scalar_event(event, rows, frames):
    op, target = event[:2]
    if op == 'transport':
        _, _, old, new, rank = event
        a, b = frame_space(old), frame_space(new)
        need(frames[target] == old and (a < b or b < a), 'nested transport frame')
        need(rank == abs(len(old)-len(new)), 'nested transport rank')
        frames[target] = new
    elif op == 'add':
        _, _, source, factor, frame = event
        need(target != source and frames[target] == frames[source] == frame,
             'common ADD frame')
        factor = Q(factor)
        valuation(factor)
        for name, value in rows[source].items():
            result = rows[target].get(name, Q(0)) + factor*value
            if result:
                rows[target][name] = result
            else:
                rows[target].pop(name, None)
    elif op == 'sign':
        need(event[2] == '-1' and frames[target] == event[3], 'sign frame')
        rows[target] = {name: -value for name, value in rows[target].items()}
    elif op == 'zero':
        need(target == 'C' and target not in rows, 'private allocation')
        rows[target], frames[target] = {}, event[2]
    else:
        need(op == 'erase' and target == 'C' and not rows[target]
             and frames[target] == event[2], 'strict scalar erasure')
        del rows[target], frames[target]


def logical(word):
    initial = word['initial_frames']
    need(len(initial) == 358, 'public input count')
    for frame in initial.values():
        frame_space(frame)
    rows = {name: {name: Q(1)} for name in initial}
    frames = dict(initial)
    forms, counts = {}, Counter()
    maximum, terms, boundaries = Q(0), 0, 0
    for role in initial:
        norm, size = observe(rows, frames, initial, role, forms)
        maximum, terms, boundaries = max(maximum, norm), terms+size, boundaries+1
    for event in word['program']:
        scalar_event(event, rows, frames)
        counts[event[0]] += 1
        if event[0] != 'erase':
            norm, size = observe(rows, frames, initial, event[1], forms)
            maximum, terms, boundaries = max(maximum, norm), terms+size, boundaries+1
    need(frames == word['final_frames'], 'complete final frame map')
    for role, row in rows.items():
        if not role.startswith('X'):
            need(row == {role: Q(1)}, 'arbitrary dirty restoration')
        else:
            need(row.get(role) == 1
                 and all(s == role or s.startswith('Y') for s in row),
                 'public dual shear')
    need(forms == {0: 1, **{k: 2 for k in range(1, 10)}, 10: 0}, 'atomic grid envelope')
    need(maximum == Q(127, 2) and counts['erase'] == 8, 'atomic range and erasures')
    return rows, {'forms': {str(k): v for k, v in sorted(forms.items())},
                  'logical_l1': str(maximum), 'counts': dict(counts),
                  'boundaries': boundaries, 'term_visits': terms}


def execute(word, uses, start):
    states = dict(start)
    erases, halvings = [], 0
    for index, event in enumerate(word['program']):
        op, role = event[:2]
        if op == 'transport':
            states[role] = native(states[role], uses[index])
            halvings += uses[index]['rank'] * N * 2
        elif op == 'add':
            states[role] = add(states[role], states[event[2]], event[3])
        elif op == 'sign':
            states[role] = tuple((-a, -b) for a, b in states[role])
        elif op == 'zero':
            need(role not in states, 'physical allocation')
            states[role] = ZERO
        else:
            need(op == 'erase' and states[role] == ZERO, 'strict physical erasure')
            erases.append(index)
            del states[role]
    return states, erases, halvings


def oracle(word, rows, start):
    logical_inputs = {name: chart(value, word['initial_frames'][name], inverse=True)
                      for name, value in start.items()}
    expected = {}
    for role, row in rows.items():
        value = ZERO
        for source, coefficient in row.items():
            value = add(value, logical_inputs[source], coefficient)
        expected[role] = chart(value, word['final_frames'][role])
    return expected


def fixture(word, uses, rows, dense=False):
    scale = 1 << 15
    start = {name: ZERO for name in word['initial_frames']}
    if dense:
        for j, name in enumerate(start):
            start[name] = tuple((scale*((x+3*j) % 7-3), scale*((2*x+j) % 5-2))
                                for x in range(N))
    else:
        start['Y2'] = ((scale, 0),) + ZERO[1:]
    actual, erases, halvings = execute(word, uses, start)
    need(actual == oracle(word, rows, start), 'complete physical endpoint oracle')
    need(len(erases) == 8, 'eight physical erasures')
    if not dense:
        need(actual['X0'][0] == (-512, 512), 'credited Y2 endpoint witness')
    return {'input': 'all-public dense complex integer' if dense else 'Y2=delta_0',
            'matched_public_fields': len(actual), 'erase_events': erases,
            'scheduled_real_halvings': halvings}


def prefix_lemma():
    """Literal distinct-coordinate C prefixes vs the closed tensor column."""
    vector = ((256, 0),) + ZERO[1:]
    bits, norms = [], []
    for k in range(9):
        if k:
            vector = stage(vector, k-1)
        real, imag = 1, 0
        for _ in range(k):
            real, imag = real-imag, real+imag
        expected = []
        for x in range(N):
            if x < 1 << k:
                a, b = rotate((real, imag), -x.bit_count())
                expected.append((a*(256 >> k), b*(256 >> k)))
            else:
                expected.append((0, 0))
        need(vector == tuple(expected), 'closed distinct-coordinate prefix')
        common = min((abs(v) & -abs(v)).bit_length()-1
                     for pair in vector for v in pair if v)
        bits.append(8-common)
        norms.append(sum(abs(a)+abs(b) for a, b in vector)//256)
    need(bits == [0, 1, 1, 2, 2, 3, 3, 4, 4], 'prefix lattice')
    need(norms == [1, 2, 2, 4, 4, 8, 8, 16, 16], 'prefix component row norms')
    return {'ranks': list(range(9)), 'extra_bits': bits, 'component_row_norms': norms}


def controls(word, archive, uses):
    from copy import deepcopy
    damaged = deepcopy(archive)
    damaged['transports'][0]['events'].append(0)
    try:
        bind_native(word, damaged)
    except ValueError as error:
        need(str(error) == 'native occurrence binding',
             'native coverage control reason')
    else:
        raise ValueError('bad native binding accepted')
    for index, factor, reason in ((2038, '1', 'strict scalar erasure'),
                                   (next(i for i, e in enumerate(word['program'])
                                         if e[0] == 'add'), '1/3', 'nonzero dyadic')):
        changed = deepcopy(word)
        changed['program'][index][3] = factor
        try:
            logical(changed)
        except ValueError as error:
            need(str(error) == reason, 'scalar control reason')
        else:
            raise ValueError('bad scalar word accepted')
    changed_uses = dict(uses)
    changed_uses[2031] = deepcopy(uses[2031])
    changed_uses[2031]['left']['phase'] = (uses[2031]['left']['phase']+2) % 4
    start = {name: ZERO for name in word['initial_frames']}
    start['D31'] = ((1 << 15, 0),) + ZERO[1:]
    for recipes, states, reason in (
            (changed_uses, start, 'strict physical erasure'),
            (uses, {**{name: ZERO for name in start},
                    'Y2': ((64, 0),) + ZERO[1:]}, 'inexact internal halving')):
        try:
            execute(word, recipes, states)
        except ValueError as error:
            need(str(error) == reason, 'physical control reason')
        else:
            raise ValueError('bad physical execution accepted')
    return ['native occurrence mismatch', 'missing private compensation',
            'non-dyadic ADD', 'native phase corrupts private erasure',
            'six-bit physical execution is inexact']


def compute():
    word, archive = inputs()
    uses, ranks = bind_native(word, archive)
    rows, scalar = logical(word)
    return {'status': 'PASS_P104_WHOLE_WORD_INTERNAL_GRID', 'events': 5398,
            'native_records': len(archive['transports']),
            'native_occurrences': len(uses),
            'profile': {str(k): v for k, v in ranks.items()},
            'atomic': scalar, 'prefix': prefix_lemma(),
            'extra_fractional_bits': 'max(14*lambda,13*lambda+2)',
            'one_layer_extra_bits': 15,
            'physical_fixtures': [fixture(word, uses, rows),
                                  fixture(word, uses, rows, True)],
            'controls': controls(word, archive, uses)}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    result = compute()
    need(canonical(result) == canonical(read(HERE / 'RESULT.json')),
         'typed receipt mismatch')
    if args.out:
        with args.out.open('x', encoding='utf-8') as handle:
            handle.write(json.dumps(result, indent=2)+'\n')
    print(result['status'])


if __name__ == '__main__':
    main()
