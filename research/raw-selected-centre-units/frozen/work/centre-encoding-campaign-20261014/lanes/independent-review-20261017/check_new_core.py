"""Review the changed clean-J words by free-operator transpose replay."""

import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as F
import gzip
from hashlib import sha256
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
LANES = HERE.parent
SOURCE = LANES / 'new-core-transfer-20261017'
UPSTREAM = LANES.parent / 'upstream-refresh-20261017/pr3148/research/coupled-carrier-cap740/words'
PINS = {
    'clean_payload': 'a6c5dc63a47c1fdb0a97314a3b8541035f507beccb1029762f703039465187fa',
    'interface': 'c6ca09711622ce4ad236f78cc28c03b6c46808a9d91cfc1722ff4fe371f38746',
    'source_base': '300a9b8ad1d554f0e6f84f43f3f5fd870a5b4e5f81ad856900b6e8999684892e',
    'source_extra': '495d030f1e03b90e954dad3043994f03293d41b9ed220a3beaef849df435d3f0',
    'canonical_base': 'bd6f84f6e7be075064f04e6141568d295631a3feab1efa75ff0326e6efa4f472',
    'canonical_extra': '1cf1714fc2a26c18b2b380827054246550c1402fde379745f626ff61f4ee6224',
    'local_source': '4048b4494793f31c6c9ce85a7de584c53cafae0cd5c119eb1084b221cfe04ad9',
    'proof': 'd12fca8b1abf95b20b9561334fb3d879d28ce880f6793a461ede0223fce1e2a0',
    'producer': '00ac96cc9906acd0ccc2d1f492411acd7308df217cfc51ff7e233e85b05efcfa',
    'producer_receipt': 'c173491679101d121a0fb43156c73ab62d9031e62b6a969a8ab80912bc36630e',
}


def need(ok, label):
    if not ok:
        raise ValueError(label)


def read(path, key, zipped=False):
    raw = path.read_bytes()
    if zipped:
        raw = gzip.decompress(raw)
    need(sha256(raw).hexdigest() == PINS[key], key + ' source pin')
    return json.loads(raw)


def plus(target, source, value=F(1)):
    for key, coefficient in source.items():
        coefficient = target.get(key, F(0)) + value * coefficient
        if coefficient:
            target[key] = coefficient
        else:
            target.pop(key, None)


def scalar(op):
    kind, target = op[0], tuple(op[1])
    source = tuple(op[2]) if kind in ('copy', 'add') else None
    coefficient = F(*op[-2:]) if kind in ('scale', 'add') else F(1)
    need(kind in ('clear', 'copy', 'scale', 'add'), 'Scalar grammar')
    need(source is None or source != target, 'Distinct scalar operands')
    return kind, target, source, coefficient


def pullback(events, fields, columns=None):
    columns = deepcopy(columns) if columns is not None else {f: {(f, ()): F(1)} for f in fields}
    for event in reversed(events):
        tag = event[0]
        if tag == 'scalar':
            kind, target, source, coefficient = scalar(event[1])
            if kind == 'add':
                plus(columns[source], columns[target], coefficient)
            elif kind == 'scale':
                columns[target] = {key: coefficient * value for key, value in columns[target].items()}
            elif kind == 'copy':
                need(target[0] in ('C', 'Z'), 'Only owned copies')
                plus(columns[source], columns[target])
                columns[target] = {}
            else:
                need(target == ('C', 0), 'Only serial owned C0 is cleared')
                columns[target] = {}
        elif tag == 'warp':
            target, symbol = tuple(event[1]), event[2]
            columns[target] = {
                (output, word[1:] if word and word[0] == -symbol else (symbol,) + word): value
                for (output, word), value in columns[target].items()
            }
        elif tag == 'zero_buffer':
            if event[1] == 'alloc':
                columns['Z', event[2]] = {}
            else:
                need(event[1] == 'free', 'Buffer lifetime grammar')
        else:
            need(tag in ('phase', 'climb', 'adapter', 'residual_adapter'), 'Centre-free event grammar')
    return columns


def expected_columns(fields, r, backward):
    out = {f: {} if f[0] == 'Z' or f == ('C', 0) else {(f, ()): F(1)} for f in fields}
    for p in range(112):
        source = ('L', 112 + p if backward else p)
        target = ('L', p if backward else 112 + p)
        plus(out[source], {(target, ()): F(-1 if backward else 1)})
        for row in r:
            for q, coefficient in row.items():
                target = ('L', q if backward else 112 + q)
                plus(out[source], {(target, ()): coefficient}, row.get(p, F(0)) * (1 if backward else -1) / 4)
    return out


def price(op):
    kind, _, _, value = scalar(op)
    if kind in ('clear', 'copy'):
        return 2
    numerator, denominator = abs(value.numerator), value.denominator
    need(numerator > 0 and not denominator & (denominator - 1), 'Dyadic scalar')
    if kind == 'scale':
        need(not numerator & (numerator - 1), 'Unit scale')
        return 2 * (abs(numerator.bit_length() - denominator.bit_length()) + int(value < 0))
    return 2 * (1 + numerator.bit_length() + numerator.bit_count() + denominator.bit_length())


def types_and_cost(events, canonical):
    frames = {('L', i): value for i, value in enumerate(canonical['start'])}
    frames.update({('C', i): None for i in range(8)})
    active, allocated, freed = set(), set(), set()
    profile, native, scalars, bill = Counter(), Counter(), 0, 0
    for event in events:
        tag = event[0]
        if tag == 'scalar':
            kind, target, source, _ = scalar(event[1])
            if kind == 'clear':
                need(target == ('C', 0), 'Only owned C0 can be cleared')
                frames[target] = event[2]
            else:
                need(frames[target] == event[2] and (source is None or frames[source] == event[2]), 'Scalar endpoint frames')
            need(all(ref[0] != 'C' or ref[1] == 0 for ref in (target, source) if ref is not None), 'C1 to C7 are untouched')
            bill += price(event[1])
            scalars += 1
        elif tag == 'climb':
            _, _, field, before, after, width = event
            need(frames['L', field] == before, 'Native frame input')
            need(len(canonical['frames'][after]) - len(canonical['frames'][before]) == width, 'Native frame width')
            frames['L', field] = after
            native[tag] += 1
            profile[width] += 1
        elif tag == 'warp':
            field = tuple(event[1])
            need(frames[field] == event[3], 'Warp input frame')
            frames[field] = event[4]
            native[tag] += 1
        elif tag == 'zero_buffer':
            field = ('Z', event[2])
            if event[1] == 'alloc':
                need(field not in allocated and field not in frames, 'Single clean allocation')
                active.add(field)
                allocated.add(field)
                frames[field] = 1
            else:
                need(event[1] == 'free' and field in active, 'Live buffer release')
                active.remove(field)
                freed.add(field)
                del frames[field]
        elif tag in ('adapter', 'residual_adapter'):
            native[tag] += 1
        else:
            need(tag == 'phase', 'Complete event grammar')
    need(not active and allocated == freed == {('Z', z) for z in canonical['zero_buffers']}, 'Every zero-buffer lifetime')
    need([frames['L', i] for i in range(632)] == canonical['final'], 'All live endpoint frames')
    need(frames['C', 0] == 0, 'C0 ends at I')
    need(profile == Counter({1: 2433, 2: 724, 3: 228, 4: 102, 5: 20}), 'Complete child profile')
    need(native == Counter(climb=3507, warp=240, adapter=978, residual_adapter=390), 'Retained native inventory')
    need(bill == 164514, 'Complete real scalar invoice')
    return {'scalar_events': scalars, 'scalar_cost': bill, 'native_profile': dict(sorted(profile.items())),
            'native_mass': sum(rank * count for rank, count in profile.items()),
            'native_records': dict(native), 'zero_lifetimes': len(allocated)}


def main(out):
    for filename, key in (('CLEAN-J-TRANSFER.md', 'proof'), ('emit_clean_j.py', 'producer'), ('CLEAN-J-TRANSFER.json', 'producer_receipt')):
        need(sha256((SOURCE / filename).read_bytes()).hexdigest() == PINS[key], key + ' source pin')
    data = read(SOURCE / 'CLEAN-J-PROGRAMS.json.gz', 'clean_payload', True)
    interface = read(SOURCE / 'INTERFACE.json', 'interface')
    r = [{int(j): F(value) for j, value in row.items()} for row in interface['R']]
    h = [{int(j): F(value) for j, value in row.items()} for row in interface['H']]
    need(data['R'] == interface['R'] and data['H'] == interface['H'], 'Whole interface metadata')
    need(len(set().union(*(set(row) for row in h))) == 106 and sum(map(len, h)) == 367, 'Changed helper debt support')
    result = {'status': 'PASS_INDEPENDENT_NEW_CORE_LOGICAL_TRANSFER', 'source_pins': PINS, 'providers': {}}
    for name in ('base', 'extra'):
        published = json.loads(gzip.decompress((UPSTREAM / (name + '.json.gz')).read_bytes()))
        need(sha256((UPSTREAM / (name + '.json.gz')).read_bytes()).hexdigest() == PINS['source_' + name], 'Published source bytes')
        local = SOURCE / ('native-original-' + name)
        need(published == json.loads(gzip.decompress((local / 'FULL-WORD.json.gz').read_bytes())), 'Source word object equality')
        canonical = read(local / 'CANONICAL-WORD.json.gz', 'canonical_' + name, True)
        original = read(local / 'LOCAL-PROGRAMS.json.gz', 'local_source', True)
        provider = data['providers'][name]
        need(provider['canonical'] == canonical, 'Whole canonical metadata')
        kept = list(range(224)) + canonical['helper_origin']
        need(len(kept) == len(set(kept)) == 632, 'Compact role inventory')
        need(canonical['ports'] == published['ports'], 'Actual published port labels')
        need(kept == sorted(set(range(704)) - set(published['removed'])), 'Actual published live roles')
        mapping = {role: i for i, role in enumerate(kept)}
        need(all(canonical['start'][mapping[j]] == 0 and canonical['final'][mapping[j]] == 1 for row in h for j in row), 'All correction helper roles have I/FULL endpoints')
        fields = [('L', i) for i in range(632)] + [('C', i) for i in range(8)] + [('Z', z) for z in canonical['zero_buffers']]
        result['providers'][name] = {}
        for orientation in ('forward', 'backward'):
            events = provider['programs'][orientation]
            old = original[orientation]
            left, right = old.index(['phase', 'centers']), old.index(['phase', 'B'])
            deleted = old[left + 1:right]
            need(deleted == provider['removed_centre_blocks'][orientation], 'Exact removed centre block')
            need(Counter(e[4] for e in deleted if e[0] == 'center') == Counter({8: 8}), 'Eight rank-eight centre children removed')
            prefix_end = events.index(['phase', 'zero_frame_precondition'])
            need(prefix_end == 832 and len(events) == 23388, 'Complete word boundaries')
            tail = old[:left + 1] + old[right:]
            need(events[prefix_end:] == tail, 'Only the stated deletion changes the retained source')
            native = lambda word: [e for e in word if e[0] in ('climb', 'warp', 'adapter', 'residual_adapter')]
            need(native(events) == native(old), 'Every native event is byte-identical')
            controls = {}
            tail_columns = pullback(tail, fields)
            actual = pullback(events[:prefix_end], fields, tail_columns)
            expected = expected_columns(fields, r, orientation == 'backward')
            need(actual == expected, 'Complete exact free-operator map')
            need(all(actual['L', j] == {(('L', j), ()): F(1)} for j in range(224, 632)), 'All arbitrary helpers restored')
            need(all(not actual['Z', z] for z in canonical['zero_buffers']), 'All zero-input columns erased at allocation')
            need(all(output[0] != 'Z' for column in actual.values() for (output, word) in column), 'Every Z output is zero at its release')
            controls['omitted_input_correction'] = tail_columns != expected
            wrong = deepcopy(events[:prefix_end])
            first_add = next(e for e in wrong if e[0] == 'scalar' and e[1][0] == 'add')
            first_add[1][3] = -first_add[1][3]
            controls['wrong_input_coefficient'] = pullback(wrong, fields, tail_columns) != expected
            need(all(controls.values()), 'Changed-word controls')
            report = types_and_cost(events, canonical)
            report.update(formal_arbitrary_inputs=640, arbitrary_helpers=408, owned_zero_buffers=91,
                          C0_output='zero', C1_to_C7='untouched arbitrary inputs', events=len(events),
                          free_operator_output_words='all empty', controls=controls)
            result['providers'][name][orientation] = report
            print(name, orientation, 'PASS_640_ARBITRARY_COLUMNS_AND_91_ZERO_OUTPUTS', flush=True)
    result['checker_sha256'] = sha256(Path(__file__).read_bytes()).hexdigest()
    result['physical_phase_status'] = 'Only exact native-record inheritance checked here; fresh recipe verification is a separate obligation.'
    result['native_owner_or_recursive_invoice'] = False
    need(not out.exists(), 'Use a new output path')
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(result['status'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    main(parser.parse_args().out)
