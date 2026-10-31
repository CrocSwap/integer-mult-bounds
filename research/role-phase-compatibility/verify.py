#!/usr/bin/env python3
"""Check the reached, role-specific phase obstruction; no full supplier claim."""
from fractions import Fraction
from hashlib import sha256
import argparse
import gzip
import json
from pathlib import Path
import sys
import types

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
WORD = 'research/p104-helper470-twin-rung-removal/WORD.json.gz'
CLIFFORD = 'research/p104-native-channel/vendor/clifford_exact.py'
NATIVE = 'research/p104-native-channel/vendor/native_verify.py'
PINS = {
    WORD: '7834725d9e34ee846a9ccc615221ea81e0201613938afa185d2eda0c9a6c232f',
    CLIFFORD: '2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962',
    NATIVE: '3049471905b47b385c88378a1a3be7a18b8858aadd035b8a6da2f4a03b470f38',
}
ADDS = {
    8255: (229, 227, '-1', 3, 229, 227, 1),
    9031: (225, 227, '1', 3, 225, 227, -1),
    9034: (231, 225, '1', 3, 231, 225, -1),
    9916: (229, 87, '1', 81, 229, 87, 1),
    9924: (231, 27, '1', 25, 231, 27, 1),
    9982: (229, 238, '1', 254, 229, 238, 1),
    9983: (231, 236, '1', 256, 231, 7, 1),
    9997: (231, 229, '1', 259, 231, 81, 1),
}
MOVES = {
    9901: (231, 3, 25, 1), 9904: (229, 3, 81, 1),
    9938: (229, 81, 254, 0), 9955: (231, 25, 256, 1),
    9987: (231, 256, 259, 0), 9994: (229, 254, 259, 0),
}
PATH_A = (9904, 9938, 9994)
PATH_B = (9901, 9955, 9987)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def rejected(operation, message):
    try:
        operation()
    except ValueError:
        return 1
    raise ValueError('Control was accepted: ' + message)


def read_inputs():
    pins = json.loads((PACKAGE / 'SOURCES.json').read_text())
    declared = {r['path']: r['sha256'] for r in pins['files'] if r['usage'] == 'input'}
    need(declared == PINS, 'Exact declared input set')
    data = {}
    for path, digest in PINS.items():
        raw = (ROOT / path).read_bytes()
        need(sha256(raw).hexdigest() == digest, 'Source bytes: ' + path)
        data[path] = raw
    word = json.loads(gzip.decompress(data[WORD]))
    need(word['schema'] == 'p104-accumulated-block-composition/2', 'Word schema')
    need(word['public'] == 770 and word['owned_fields'] == 29, 'Public/owned inventory')
    need(len(word['program']) == 22803, 'Exact selected event count')
    return word, data


def source_module(raw, name):
    # Compile authenticated source bytes directly: no stale .pyc can replace them.
    module = types.ModuleType(name)
    module.__file__ = str(ROOT / name)
    exec(compile(raw, module.__file__, 'exec'), module.__dict__)
    return module


def witness_events(word):
    program = word['program']
    for index, (t, s, q, chart, _x, _y, _det) in ADDS.items():
        need(program[index] == ['ADD', t, s, q, chart], 'Named ADD ' + str(index))
    for index, (role, a, b, _phase) in MOVES.items():
        need(program[index] == ['MOVE', role, a, b, False], 'Named MOVE ' + str(index))
    windows = ((227, 8255, 9031, ()), (225, 9031, 9034, ()),
               (229, 8255, 9997, (9904, 9916, 9938, 9982, 9994)),
               (231, 9034, 9997, (9901, 9924, 9955, 9983, 9987)))
    for role, first, last, expected in windows:
        writes = tuple(i for i in range(first + 1, last) if program[i][1] == role)
        need(writes == expected, 'No hidden write in role window ' + str(role))
    return windows


def row_add(target, source, coefficient):
    result = dict(target)
    for key, value in source.items():
        result[key] = result.get(key, Fraction(0)) + coefficient * value
        if result[key] == 0:
            del result[key]
    return result


def exact_prefix(word):
    rows = [{i: Fraction(1)} for i in range(770)] + [{} for _ in range(29)]
    current = list(word['initial']) + [None] * 29
    active = set()
    minors = {}
    for index, event in enumerate(word['program'][:9998]):
        op, role = event[:2]
        need(type(role) is int and 0 <= role < 799, 'Role domain')
        if op == 'INIT':
            need(role >= 770 and role not in active and not rows[role], 'Owned INIT')
            current[role] = event[2]
            active.add(role)
        elif op == 'CLEAR':
            need(role in active and not rows[role], 'Owned exact CLEAR')
            need(current[role] == event[2], 'CLEAR chart')
            current[role] = None
            active.remove(role)
        elif op == 'MOVE':
            _op, _role, a, b, owned = event
            need(current[role] == a and (role in active) is owned, 'MOVE state')
            current[role] = b
        elif op == 'SCALE':
            need(current[role] == event[-1], 'SCALE chart')
            coefficient = Fraction(event[2])
            need(coefficient != 0, 'Nonzero SCALE')
            rows[role] = {k: coefficient * v for k, v in rows[role].items()}
        elif op in ('ADD', 'COPY'):
            _op, _role, source, q, chart = event
            need(current[role] == current[source] == chart, 'Scalar common chart')
            need(role != source, 'Distinct scalar roles')
            if op == 'COPY':
                need(not rows[role], 'COPY into exact zero')
            if index in ADDS:
                _t, _s, _q, _f, x, y, expected = ADDS[index]
                matrix = [[rows[r].get(k, Fraction(0)) for k in (x, y)] for r in (role, source)]
                det = matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]
                need(det == expected and det != 0, 'Reached rank-two ADD ' + str(index))
                minors[str(index)] = {'columns': [x, y], 'matrix': [[str(z) for z in r] for r in matrix], 'determinant': str(det)}
            rows[role] = row_add(rows[role], rows[source], Fraction(q))
        else:
            raise ValueError('Unknown opcode')
    need(len(minors) == 8, 'Every independent contact certified')
    return minors


def native_edges(word, raw):
    clifford = source_module(raw[CLIFFORD], 'phase_clifford')
    native = source_module(raw[NATIVE], 'phase_native')
    recipes, stripped, phases = {}, {}, {}
    for index, (_role, a, b, expected_phase) in MOVES.items():
        chart_a = clifford.canonical_frame(9, word['frames'][a])
        chart_b = clifford.canonical_frame(9, word['frames'][b])
        record, _compiled = clifford.lower_child(chart_a.adjoint().then(chart_b))
        recipe = native.recipe(record)
        phases[index] = sum(g[1] for g in recipe if g[0] == 'phase') % 4
        need(record['rank'] == 1 and phases[index] == expected_phase, 'Native rank/phase')
        literal = native.adjoint(native.frame(tuple(word['frames'][a]), 9))
        literal += native.frame(tuple(word['frames'][b]), 9)
        for address in range(512):
            need(native.state(recipe, address) == native.state(literal, address), 'Every native basis column')
        recipes[index] = tuple(recipe)
        stripped[index] = tuple(g for g in recipe if g[0] != 'phase')
    return native, recipes, stripped, phases


def path_loop(native, recipes, stripped):
    full_a = sum((recipes[i] for i in PATH_A), ())
    full_b = sum((recipes[i] for i in PATH_B), ())
    bare_a = sum((stripped[i] for i in PATH_A), ())
    bare_b = sum((stripped[i] for i in PATH_B), ())
    full = full_b + tuple(native.adjoint(full_a))
    bare = bare_b + tuple(native.adjoint(bare_a))
    for address in range(512):
        need(native.state(full, address) == ({address: (1, 0)}, 0), 'Full paths agree')
        need(native.state(bare, address) == ({address: (0, -1)}, 0), 'Bare paths differ by -i')
    return bare


def finite_phase_check(phases):
    a = sum(phases[i] for i in PATH_A) % 4
    b = sum(phases[i] for i in PATH_B) % 4
    need((a, b) == (1, 2), 'Distinct chronological path phases')
    # Tree equations determine every gauge from the free root. The final
    # ADD demands equality. This is corroboration, not the all-f proof.
    counts = [sum((root - width*a) % 4 == (root - width*b) % 4
                  for root in range(4)) for width in range(1, 5)]
    need(counts == [0, 0, 0, 4], 'Finite gauge solution counts')
    return counts


def controls(word, raw, native, bare, phases):
    count = 0
    for path, payload in raw.items():
        count += rejected(lambda: need(sha256(payload+b'\n').hexdigest() == PINS[path], 'Changed source'), path)
    bad = json.loads(json.dumps(word))
    bad['program'][9997][2] = 230
    count += rejected(lambda: witness_events(bad), 'Changed contact')
    bad = json.loads(json.dumps(word))
    bad['program'][9000] = ['SCALE', 227, '1', 3]
    count += rejected(lambda: witness_events(bad), 'Hidden write')
    count += rejected(lambda: need(native.state(bare) == ({0: (1, 0)}, 0), 'No loop phase'), 'Phase deletion')
    count += rejected(lambda: need(native.state(bare) == ({0: (0, 1)}, 0), 'Wrong sign'), 'Loop sign')
    bad_phase = dict(phases)
    bad_phase[9955] = 0
    count += rejected(lambda: finite_phase_check(bad_phase), 'Wrong native phase')
    # A missing independence hypothesis cannot justify equal phases.
    a, b = (1, 0), (0, 0)
    need(a[0]*b[1]-a[1]*b[0] == 0, 'Dependent control is actually dependent')
    count += rejected(lambda: need(a[0]*b[1]-a[1]*b[0] != 0, 'Required rank two'), 'Zero source')
    # Removing the closing contact leaves a tree with four gauges at each width.
    need(all(len({(q, (q-f)%4, (q-2*f)%4) for q in range(4)}) == 4 for f in range(1,5)), 'Open tree control')
    # An actual altered ADD coefficient would repair this cycle only.
    def rotate(pair, power):
        x, y = pair
        return ((x,y),(-y,x),(-x,-y),(y,-x))[power % 4]
    for f in range(1,5):
        target, source = rotate((1,2), -2*f), rotate((3,4), -f)
        correction = rotate(source, -f)
        repaired = tuple(x+y for x,y in zip(target, correction))
        required = rotate((4,6), -2*f)
        need(repaired == required, 'Actual changed-coefficient ADD')
        unmodified = tuple(x+y for x,y in zip(target, source))
        if f % 4:
            count += rejected(lambda: need(unmodified == required, 'Unmodified ADD'), 'Missing compensating coefficient')
        else:
            need(unmodified == required, 'Width-four unchanged ADD')
    return count


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write-result', action='store_true')
    args = parser.parse_args()
    word, raw = read_inputs()
    witness_events(word)
    minors = exact_prefix(word)
    native, recipes, stripped, phases = native_edges(word, raw)
    bare = path_loop(native, recipes, stripped)
    counts = finite_phase_check(phases)
    rejected_count = controls(word, raw, native, bare, phases)
    result = {'schema':'role-phase-compatibility/1', 'no_new_kappa':True,
              'prefix_events':9998, 'witness_event_count':14, 'independent_adds':minors,
              'native_move_phases':{str(k):v for k,v in phases.items()},
              'native_basis_column_comparisons':3072, 'loop_basis_columns':512,
              'path_phase_sums_mod4':[1,2], 'stripped_relative_loop':'-i I',
              'gauge_counts_widths_1_to_4':counts, 'rejecting_controls':rejected_count,
              'input_sha256':PINS}
    result_path = PACKAGE / 'RESULT.json'
    if args.write_result:
        need(not result_path.exists(), 'Refuse to overwrite retained result')
        result_path.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:
        need(json.loads(result_path.read_text()) == result, 'Exact retained result')
    print(json.dumps(result,sort_keys=True))
    print('PASS_ROLE_PHASE_COMPATIBILITY events=14 contacts=8 moves=6 iff_four_divides_width')


if __name__ == '__main__':
    main()
