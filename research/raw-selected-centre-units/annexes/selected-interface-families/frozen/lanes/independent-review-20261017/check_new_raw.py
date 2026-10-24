"""Review raw selected exchanges by reverse ordered-operator propagation."""

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
U = [p for p in range(112) if p not in A]
PINS = {
    'RAW-SELECTED-TRANSFER.md': '53d8663fab6c1a6999fbc29ac310675fbea2b45f607f2f702af9787305c4ab03',
    'RAW-SELECTED-TRANSFER.json': 'da1831b17a79a4fd9ebe689d4f76e357bc912eda1e6b252818a7ef5685b1a739',
    'RAW-SELECTED-TRANSFER.json.gz': 'bc9fab3bc7c849da7eb055a9d7340bf110c11cdd54da049a8297a1324bfa54b1',
    'emit_raw_selected.py': 'a07cf4894a2599993006c7b99e6cb62146ece82f2ae6df72a28100ccb3a689bc',
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


def field(n):
    need(isinstance(n, int) and (0 <= n < 224 or 632 <= n < 640), 'Data or owned physical boundary field')
    return ('L', n) if n < 224 else ('C', n - 632)


def qgate(register, port, power):
    need(port in range(112) and power in (-1, 1), 'Q symbol range')
    return ['warp', list(register), power * (10000 + port), None, None]


def boundary(events):
    out = []
    for e in events:
        t, kind = field(e['target']), e['kind']
        if kind == 'line':
            need(t == ('C', 0) and e['port'] in A, 'Only selected owned line children')
            out.append(qgate(t, e['port'], e['power']))
            continue
        if kind == 'clear':
            need(t[0] == 'C', 'Only owned boundary clears')
            op = ['clear', list(t)]
        elif kind == 'copy':
            need(t == ('C', 0) and e['source'] < 224, 'Serial owned data copy')
            op = ['copy', list(t), list(field(e['source']))]
        elif kind == 'add':
            s, q = field(e['source']), F(e['coefficient'])
            need(s != t, 'Distinct physical ADD fields')
            op = ['add', list(t), list(s), q.numerator, q.denominator]
        else:
            need(kind == 'scale', 'Boundary event grammar')
            q = F(e['coefficient'])
            op = ['scale', list(t), q.numerator, q.denominator]
        out.append(['scalar', op, None])
    return out


def full_word(program):
    native = deepcopy(program['retained_core'])
    if program['orientation'] == 'backward':
        for e in native:
            if e[0] == 'warp':
                e[2] = (1000 + abs(e[2])) * (1 if e[2] > 0 else -1)
    return ([qgate(('L', p), p, 1) for p in range(112)]
            + boundary(program['prefix'] + program['input_exchange'])
            + [qgate(('L', p), p, -1) for p in range(112)]
            + native
            + [qgate(('L', 112 + p), p, -1) for p in range(112)]
            + boundary(program['suffix'] + program['owned_cleanup'])
            + [qgate(('L', 112 + p), p, 1) for p in range(112)])


def pullback(events, fields, core):
    columns = {f: {(f, ()): F(1)} for f in fields}
    for event in reversed(events):
        tag = event[0]
        if tag == 'scalar':
            kind, target, source, coefficient = core.scalar(event[1])
            if kind == 'add':
                core.plus(columns[source], columns[target], coefficient)
            elif kind == 'scale':
                columns[target] = {key: coefficient * value for key, value in columns[target].items()}
            elif kind == 'copy':
                need(target == ('C', 0), 'Only serial C0 is overwritten')
                core.plus(columns[source], columns[target])
                columns[target] = {}
            else:
                need(target[0] == 'C', 'No borrowed clear')
                columns[target] = {}
        elif tag == 'warp':
            target, symbol = tuple(event[1]), event[2]
            columns[target] = {(out, word[1:] if word and word[0] == -symbol else (symbol,) + word): value
                               for (out, word), value in columns[target].items()}
        elif tag == 'zero_buffer':
            if event[1] == 'alloc':
                columns['Z', event[2]] = {}
            else:
                need(event[1] == 'free', 'Buffer lifetime grammar')
        else:
            need(tag in ('phase', 'climb', 'adapter', 'residual_adapter'), 'Complete native grammar')
    return columns


def expected(fields, d, b, name, core):
    out = {f: {} if f[0] in ('C', 'Z') else {(f, ()): F(1)} for f in fields}
    def put(src, dst, coefficient, q=None):
        word = () if q is None else (q,)
        core.plus(out['L', src], {(('L', dst), word): F(coefficient)})
    if name.startswith('B'):
        for a in A:
            out['L', a] = {}
            out['L', 112 + a] = {}
            put(112 + a, a, 1 if name == 'B0' else -12, -(10000 + a))
            for p, coefficient in b[a].items():
                put(112 + p, a, coefficient)
            put(a, 112 + a, 1, 10000 + a)
        for p in U:
            put(112 + p, p, -1)
            for a, coefficient in d[p].items():
                if name != 'B16':
                    put(a, p, coefficient, 10000 + a)
                if name == 'B0':
                    put(112 + a, p, -coefficient, -(10000 + a))
                else:
                    put(112 + a, 112 + p, -coefficient, -(10000 + a))
    else:
        for a in A:
            for p, coefficient in b[a].items():
                put(p, a, -coefficient, -(10000 + a))
        for p in U:
            put(p, 112 + p, 1)
            for a, coefficient in d[p].items():
                for j, factor in b[a].items():
                    put(j, 112 + p, -coefficient * factor)
                if name == 'F0':
                    put(112 + a, 112 + p, -coefficient, -(10000 + a))
    return out


def boundary_bill(events, core):
    zero = set()
    scalar, lines = 0, 0
    for e in events:
        t, kind = field(e['target']), e['kind']
        if kind == 'clear':
            need(t[0] == 'C', 'Owned clear access')
            zero.add(t)
        elif kind == 'copy':
            need(t == ('C', 0) and t in zero, 'Copy starts in a cleared private field')
            zero.discard(t)
        elif kind == 'line':
            need(t == ('C', 0) and e['port'] in A and e['power'] in (-1, 1), 'Signed line access')
            lines += 1
            continue
        else:
            zero.discard(t)
        scalar += core.price(boundary([e])[0][1])
    return scalar, lines


def inverse_checks(d, b, core):
    fs = [('L', p) for p in range(224)]
    identity = {f: {(f, ()): F(1)} for f in fs}
    def put(matrix, source, target, value, q=None):
        core.plus(matrix['L', source], {(('L', target), () if q is None else (q,)): F(value)})
    def compose(left, right):
        out = {f: {} for f in fs}
        for source, column in right.items():
            for (middle, first), a in column.items():
                for (target, second), b_ in left[middle].items():
                    reduced = []
                    for symbol in first + second:
                        if reduced and reduced[-1] == -symbol:
                            reduced.pop()
                        else:
                            reduced.append(symbol)
                    core.plus(out[source], {(target, tuple(reduced)): a * b_})
        return out
    back = {f: {} for f in fs}
    for a in A:
        put(back, a, 112 + a, 1, 10000 + a)
        put(back, 112 + a, a, 1, -(10000 + a))
        for p, value in b[a].items():
            put(back, 112 + p, 112 + a, -value, 10000 + a)
    for p in U:
        put(back, p, p, 1)
        put(back, 112 + p, 112 + p, 1)
        put(back, 112 + p, p, 1)
        for a, value in d[p].items():
            put(back, a, p, value)
            put(back, 112 + a, p, -value)
            for j, factor in b[a].items():
                put(back, 112 + j, p, -value * factor)
    front = deepcopy(identity)
    for a in A:
        for p, value in b[a].items():
            put(front, p, a, value, -(10000 + a))
    for p in U:
        put(front, p, 112 + p, -1)
        for a, value in d[p].items():
            for j, factor in b[a].items():
                put(front, j, 112 + p, value * factor)
    for name, inverse in (('B0', back), ('F8', front)):
        forward = expected(fs, d, b, name, core)
        need(compose(inverse, forward) == identity, name + ' inverse after forward')
        need(compose(forward, inverse) == identity, name + ' forward after inverse')
    return {'B0': 'both orders in the free Q algebra', 'F8': 'both orders in the free Q algebra'}


def main(out):
    for name in PINS:
        load(name)
    data, clean = load('RAW-SELECTED-TRANSFER.json.gz'), load('CLEAN-J-PROGRAMS.json.gz')
    core, old = engine('check_new_core.py'), engine('check_oblique_backward.py')
    need(data['selected_A'] == A and set(data['providers']) == {'base', 'extra'}, 'Selected ports and providers')
    r = old.deserialize(clean['R'])
    d = {p: {a: sum(row.get(p, 0) * row.get(a, 0) for row in r) / 4 for a in A} for p in U}
    d = {p: {a: value for a, value in row.items() if value} for p, row in d.items()}
    b = {a: {p: d[p][a] for p in U if a in d[p]} for a in A}
    need(all(sum(b[a].get(p, 0) * d[p].get(z, 0) for p in U) == (13 if a == z else 0) for a in A for z in A), 'Literal BD equals 13I')
    report = {'status': 'PASS_INDEPENDENT_NEW_RAW_SELECTED_TRANSFER', 'source_pins': PINS, 'independent_engine_pins': ENGINE_PINS, 'providers': {}}
    report['two_sided_inverse_checks'] = inverse_checks(d, b, core)
    costs = {'B0': (168896, 0), 'B8': (173104, 8), 'B16': (177312, 16), 'F0': (164944, 0), 'F8': (169152, 8)}
    for provider, item in data['providers'].items():
        c = item['canonical']
        need(c == clean['providers'][provider]['canonical'] and set(item['programs']) == set(costs), 'Exact provider and five maps')
        fs = [('L', i) for i in range(632)] + [('C', i) for i in range(8)] + [('Z', z) for z in c['zero_buffers']]
        line_columns = old.native_lines(data['line_recipes'], c)
        reports = {}
        for name, program in item['programs'].items():
            direction = 'backward' if name.startswith('B') else 'forward'
            need(program['orientation'] == direction and program['retained_core'] == clean['providers'][provider]['programs'][direction], 'Exact retained core and orientation')
            need(program['events'] == program['prefix'] + program['input_exchange'] + program['retained_core'] + program['suffix'] + program['owned_cleanup'], 'Whole word composition')
            need(program['owned_cleanup'] == [{'kind': 'clear', 'target': 632 + p} for p in range(1, 8)], 'Seven explicit final private clears')
            actual = pullback(full_word(program), fs, core)
            goal = expected(fs, d, b, name, core)
            need(actual == goal, 'Whole ordered-operator map: ' + name)
            invoice = core.types_and_cost(program['retained_core'], c)
            extra_scalar, lines = boundary_bill(program['prefix'] + program['input_exchange'] + program['suffix'] + program['owned_cleanup'], core)
            need((invoice['scalar_cost'] + extra_scalar, lines) == costs[name], 'Independent complete invoice')
            reports[name] = {'scalar': invoice['scalar_cost'] + extra_scalar, 'native_rank_mass': invoice['native_mass'] + lines,
                             'native_children': 3507 + lines, 'new_rank_one_children': lines, 'new_monomial_wrappers': 2 * lines,
                             'boundary_scalar_cost': extra_scalar, 'owned_cleanup_scalar_cost': 14,
                             'arbitrary_input_columns': 640, 'arbitrary_helpers_restored': 408, 'private_outputs_zero': 8,
                             'zero_buffer_outputs_zero': 91, 'exact_signed_line_columns': line_columns,
                             'core_frame_checks': invoice['scalar_events'], 'core_warp_events': invoice['native_records']['warp']}
            print(provider, name, 'PASS', reports[name]['scalar'], reports[name]['native_rank_mass'], flush=True)
        controls = {}
        variants = [('B8', 'prefix', 'line'), ('B0', 'input_exchange', 'omit'), ('B0', 'suffix', 'omit'), ('F8', 'suffix', 'omit'), ('F8', 'prefix', 'omit')]
        for name, part, kind in variants:
            bad = deepcopy(item['programs'][name])
            if kind == 'line':
                next(e for e in bad[part] if e['kind'] == 'line')['power'] = 1
            else:
                bad[part] = []
            label = name + ':' + part + ':' + kind
            controls[label] = pullback(full_word(bad), fs, core) != expected(fs, d, b, name, core)
        need(all(controls.values()), 'Five physical boundary controls')
        report['providers'][provider] = {'programs': reports, 'negative_controls': controls}
    report['method'] = 'Reverse propagation through every literal event, with disjoint signed Q, K, and dual-K symbols; only adjacent inverse symbols cancel. Physical boundaries are conjugated by explicit endpoint Q operators.'
    report['scope'] = 'Local operator-coded maps and complete local costs, with exact core native and signed-line dependencies. Inter-call code conversion, exterior caller phases, controller, legal owner/hosting, precision, and full supplier remain separate.'
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print(report['status'], flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    main(parser.parse_args().out)
