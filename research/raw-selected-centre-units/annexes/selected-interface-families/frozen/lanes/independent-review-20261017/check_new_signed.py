"""Review the signed extensions by reverse free-operator propagation."""

import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as F
import gzip
from hashlib import sha256
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'new-core-transfer-20261017'
A = [0, 7, 20, 27, 36, 46, 57, 111]
PINS = {
    'SIGNED-EXTENSIONS.md': '5c9dc4091a8c1c70e4a7090f9435f94740e6355f0ae0d8f861f38d1e35ebd635',
    'SIGNED-EXTENSIONS.json': '0b5a7ca0e1e2657d182db466c07042293ed6c504f9b01bbcac2bf6f15ca06a3a',
    'SIGNED-EXTENSIONS.json.gz': '76a318f7c066c65fc43bc5bd4e93faf60036245dac9a9f596f7f95739b2ab272',
    'emit_signed_extensions.py': '8a33029ce23ace9c626de7d90e44aa0318cd97025a9a928fc3a22d848326f6c5',
    'CLEAN-J-PROGRAMS.json.gz': 'a6c5dc63a47c1fdb0a97314a3b8541035f507beccb1029762f703039465187fa',
}
ENGINE_PINS = {
    'check_new_core.py': '6106c9808185747b221c149a668c8d087abbc34d79b9a7aca95e8a813e18186a',
    'check_oblique_backward.py': '7d9e52f9f120be04adeb9cdc3e26658373b221c35920e89160fdc0f16e7bdacd',
}


def need(ok, label):
    if not ok:
        raise ValueError(label)


def load(name):
    raw = (SOURCE / name).read_bytes()
    if name.endswith('.gz'):
        raw = gzip.decompress(raw)
    need(sha256(raw).hexdigest() == PINS[name], 'Source pin: ' + name)
    return json.loads(raw) if '.json' in name else raw


def engine(name):
    path = HERE / name
    need(sha256(path.read_bytes()).hexdigest() == ENGINE_PINS[name], 'Independent engine pin')
    spec = importlib.util.spec_from_file_location(name.replace('.', '_'), path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def field(number):
    need(isinstance(number, int) and 0 <= number < 640, 'Boundary field bound')
    return ('L', number) if number < 632 else ('C', number - 632)


def normalized(events):
    out = []
    for e in events:
        if not isinstance(e, dict):
            out.append(e)
            continue
        kind, target = e['kind'], field(e['target'])
        if kind == 'intrinsic_line':
            continue
        if kind == 'clear_owned':
            need(target == ('C', 0), 'Only C0 is cleared')
            op = ['clear', list(target)]
        elif kind == 'physical_copy':
            op = ['copy', list(target), list(field(e['source']))]
        else:
            need(kind == 'physical_add', 'Boundary scalar grammar')
            q = F(e['coefficient'])
            op = ['add', list(target), list(field(e['source'])), q.numerator, q.denominator]
        out.append(['scalar', op, None])
    return out


def expected(fields, s, a, name, core):
    result = {f: {} if f[0] == 'Z' or f == ('C', 0) else {(f, ()): F(1)} for f in fields}
    def put(source, target, value):
        core.plus(result[source], {(target, ()): F(value)})
    if name.endswith('forward'):
        for i in range(112):
            if name.startswith('coded'):
                result['L', 112 + i] = {}
            for j, value in s[i].items():
                put(('L', j), ('L', 112 + i), value)
        if name.startswith('coded'):
            for i in range(112):
                for j, value in s[i].items():
                    put(('L', 112 + j), ('L', 112 + i), value)
    elif name == 'backward':
        for i in range(112):
            for j, value in s[i].items():
                put(('L', 112 + j), ('L', i), -value)
    else:
        for j in range(112):
            result['L', j] = {}
        for i in range(112):
            for j, value in a[i].items():
                put(('L', j), ('L', i), value)
            put(('L', 112 + i), ('L', i), -1)
        if name == 'oblique_backward':
            for p in A:
                put(('L', p), ('L', p), 1)
                put(('L', p), ('L', 112 + p), -1)
    return result


def frame_bill(events, c, core):
    frames = {('L', i): f for i, f in enumerate(c['start'])}
    frames.update({('C', i): None for i in range(8)})
    zero = set()
    allocated, active, freed = set(), set(), set()
    profile, boundary = Counter(), Counter()
    scalar, checks = 0, 0
    for e in events:
        if isinstance(e, dict):
            kind, target = e['kind'], field(e['target'])
            endpoint = e['endpoint']
            need(endpoint in ('input', 'output'), 'Boundary endpoint')
            common = 0 if endpoint == 'input' else 1
            boundary[kind] += 1
            if kind == 'clear_owned':
                need(target == ('C', 0), 'Owned boundary clear')
                z = e['zero_frame']
                if z == 'I':
                    frames[target] = 0
                else:
                    need(z[0] == 'selected_source' and z[1] in A, 'Selected zero frame')
                    frames[target] = c['start'][z[1]] if endpoint == 'input' else c['final'][112 + z[1]]
                zero.add(target)
                scalar += 2
            elif kind == 'physical_copy':
                source = field(e['source'])
                need(target == ('C', 0) and target in zero and frames[target] == frames[source], 'Clean boundary copy')
                need(source == ('L', e['source']) and (source[1] in A if endpoint == 'input' else source[1] - 112 in A), 'Selected boundary source')
                zero.discard(target)
                scalar += 2
            elif kind == 'intrinsic_line':
                p = e['port']
                need(p in A and target == ('C', 0), 'Selected owned line')
                old = c['start'][p] if endpoint == 'input' else c['final'][112 + p]
                need(frames[target] == old and e['power'] == (-1 if endpoint == 'input' else 1), 'Line sign and entry frame')
                frames[target] = common
                profile[1] += 1
            else:
                need(kind == 'physical_add' and field(e['source']) == ('C', 0), 'Boundary ADD source')
                need(frames[target] == frames['C', 0] == common and abs(F(e['coefficient'])) == 1, 'Boundary ADD frame and unit')
                zero.discard(target)
                scalar += 8
            checks += 1
            continue
        tag = e[0]
        if tag == 'scalar':
            kind, target, source, _ = core.scalar(e[1])
            need(all(f[0] != 'C' or f[1] == 0 for f in (target, source) if f is not None), 'Untouched C1 through C7')
            if kind == 'clear':
                need(target == ('C', 0), 'Owned scalar clear')
                frames[target] = e[2]
                zero.add(target)
            else:
                need(frames[target] == e[2] and (source is None or frames[source] == e[2]), 'Complete scalar frame access')
                if kind == 'copy':
                    need(target == ('C', 0), 'Owned scalar copy')
                zero.discard(target)
            scalar += core.price(e[1])
            checks += 1
        elif tag == 'climb':
            _, _, r, old, new, width = e
            need(frames['L', r] == old and len(c['frames'][new]) - len(c['frames'][old]) == width, 'Child frame and rank')
            frames['L', r] = new
            profile[width] += 1
        elif tag == 'warp':
            f = tuple(e[1])
            need(frames[f] == e[3], 'Warp source frame')
            frames[f] = e[4]
        elif tag == 'zero_buffer':
            f = ('Z', e[2])
            if e[1] == 'alloc':
                need(f not in allocated, 'Single zero-buffer allocation')
                allocated.add(f)
                active.add(f)
                frames[f] = 1
            else:
                need(e[1] == 'free' and f in active, 'Zero-buffer release')
                active.remove(f)
                freed.add(f)
                del frames[f]
        else:
            need(tag in ('phase', 'adapter', 'residual_adapter'), 'Event grammar')
    need(not active and allocated == freed == {('Z', z) for z in c['zero_buffers']}, 'All 91 buffer lifetimes')
    need([frames['L', r] for r in range(632)] == c['final'], 'All live endpoint frames')
    need(frames['C', 0] == 0 and all(frames['C', p] is None for p in range(1, 8)), 'C0 zero frame and untouched other C')
    need(boundary['intrinsic_line'] in (8, 16) and boundary == Counter(clear_owned=2 * boundary['intrinsic_line'], physical_copy=boundary['intrinsic_line'], physical_add=boundary['intrinsic_line'], intrinsic_line=boundary['intrinsic_line']), 'Complete signed boundary blocks')
    return {'scalar': scalar, 'rank_mass': sum(k * v for k, v in profile.items()), 'children': sum(profile.values()),
            'profile': dict(sorted(profile.items())), 'new_line_children': boundary['intrinsic_line'], 'scalar_and_boundary_frame_checks': checks}


def main(out):
    for name in PINS:
        load(name)
    signed = load('SIGNED-EXTENSIONS.json.gz')
    clean = load('CLEAN-J-PROGRAMS.json.gz')
    need(set(signed['providers']) == {'base', 'extra'}, 'Both provider words')
    core, old = engine('check_new_core.py'), engine('check_oblique_backward.py')
    r = old.deserialize(clean['R'])
    eye = [{i: F(1)} for i in range(112)]
    k = [{j: row[i] / 4 for j, row in enumerate(r) if i in row} for i in range(112)]
    kr = old.multiply(k, r)
    s, a = deepcopy(eye), deepcopy(eye)
    for i in range(112):
        old.plus(s[i], kr[i], -1)
        if i in A:
            old.plus(s[i], {i: F(1)}, -1)
            a[i] = {i: F(12)}
        for j, value in kr[i].items():
            if (i in A) != (j in A):
                a[i][j] = -value
    p = [dict(row) if i in A else {} for i, row in enumerate(kr)]
    need(old.multiply(r, k) == [{j: F(14)} for j in range(8)], 'Actual query Gram matrix')
    need(old.multiply(r, [row if i in A else {} for i, row in enumerate(k)]) == [{j: F(1)} for j in range(8)], 'Selected unit section')
    need(old.multiply(s, a) == old.multiply(a, s) == eye, 'Both dyadic inverse orders')
    need(old.multiply(p, p) == p and old.multiply(p, a) == [{i: F(-1)} if i in A else {} for i in range(112)], 'Oblique projection and return identity')
    need(signed['selected_A'] == A and old.deserialize(signed['S']) == s and old.deserialize(signed['inverse_S']) == a, 'Derived matrix metadata')
    report = {'status': 'PASS_INDEPENDENT_NEW_SIGNED_EXTENSIONS', 'source_pins': PINS, 'independent_engine_pins': ENGINE_PINS, 'providers': {}}
    for provider, item in signed['providers'].items():
        need(set(item['programs']) == {'forward', 'backward', 'coded_forward', 'coded_backward', 'oblique_backward'}, 'All five local maps')
        c = item['canonical']
        need(c == clean['providers'][provider]['canonical'], 'Exact new core frame metadata')
        fs = [('L', i) for i in range(632)] + [('C', i) for i in range(8)] + [('Z', z) for z in c['zero_buffers']]
        lines = old.native_lines(signed['line_recipes'], c)
        reports = {}
        for name, program in item['programs'].items():
            orientation = 'forward' if name.endswith('forward') else 'backward'
            need(program['orientation'] == orientation and program['core'] == clean['providers'][provider]['programs'][orientation], 'Complete retained clean core')
            need(program['events'] == program['prefix'] + program['core'] + program['suffix'], 'Whole literal composition')
            actual = core.pullback(normalized(program['events']), fs)
            need(actual == expected(fs, s, a, name, core), 'Every arbitrary live/private input and zero-buffer output')
            bill = frame_bill(program['events'], c, core)
            need(bill['scalar'] == (172050 if name == 'oblique_backward' else 171938 if name.startswith('coded') else 164626), 'Full scalar invoice')
            need(bill['rank_mass'] == (5089 if name == 'oblique_backward' else 5081), 'Full native invoice')
            bill.update(arbitrary_input_columns=640, arbitrary_helpers_restored=408, zero_buffer_outputs_zero=91,
                        exact_signed_line_columns=lines, core_native_records_inherited=True)
            reports[name] = bill
            print(provider, name, 'PASS', bill['scalar'], bill['rank_mass'], flush=True)
        chosen = item['programs']['oblique_backward']
        tail = core.pullback(normalized(chosen['core'] + chosen['suffix']), fs)
        prefix = normalized(chosen['prefix'])
        correct = core.pullback(prefix, fs, tail)
        need(tail != correct, 'Omitted oblique prefix control')
        wrong = deepcopy(prefix)
        gate = next(e for e in wrong if e[0] == 'scalar' and e[1][0] == 'add')
        gate[1][-2] *= -1
        need(core.pullback(wrong, fs, tail) != correct, 'Wrong prefix sign control')
        bad = deepcopy(chosen['prefix'])
        next(e for e in bad if isinstance(e, dict) and e['kind'] == 'clear_owned')['target'] = 224
        try:
            normalized(bad)
        except ValueError:
            pass
        else:
            raise ValueError('Borrowed helper clear control')
        report['providers'][provider] = reports
    report['negative_controls'] = ['omitted oblique input return', 'wrong return sign', 'borrowed helper clear', 'wrong signed-line kernel sign on every spatial column']
    report['scope'] = 'Ten local maps, complete scalar/frame accounting, and exact signed-line kernels. Core phase recipes have a separate independent review. Exterior caller phase matching, global controller, owner, hosting, and complete recursive supplier remain separate.'
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print(report['status'], flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    main(parser.parse_args().out)
