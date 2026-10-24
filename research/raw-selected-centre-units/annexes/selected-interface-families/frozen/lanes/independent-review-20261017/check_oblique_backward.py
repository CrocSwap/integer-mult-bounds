"""Check the oblique word with an independent transpose replay."""

import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as F
import gzip
from hashlib import sha256
import json
from pathlib import Path
import tarfile


HERE = Path(__file__).resolve().parent
LANES = HERE.parent
ROOT = HERE.parents[3]
A = [0, 7, 20, 27, 36, 46, 57, 111]
PINS = {
    'payload': '8ade3776246743642fda048d71e42724dd768e99e621afa3cb7452048a244545',
    'proof': 'eac6dfa562a114f5c94dc019f4b23eb88c682f2f5261b7d7fd889da7974cbbc3',
    'producer': 'c5d1e2b0cba8de2d719a773d29cc678bd9e0a2b7c1203e4bea571567f694f9f0',
    'producer_receipt': 'c036721c9505238b5f72531b7dcbe5a3b8dbc064213756ad816448e983bd7942',
    'uniform': '17122a343fb8a3dd804b2d7042d523aa209d0684447cdba63d84cc5561b6144f',
    'uniform_review': 'b1ce8571804b848f0d8427c971d44d9e43a43f7f8e627c2eef0ebd3fc6a21d2f',
    'core': 'fa60b4af013dd8b8db289845e3ed597720ff955751ad270c3d58236b64080877',
    'interface': '5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3',
    'word': '16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219',
    'archive': 'f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6',
    'phases': 'c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa',
}


def need(ok, label):
    if not ok:
        raise ValueError(label)


def pinned(path, name, zipped=False):
    raw = path.read_bytes()
    if zipped:
        raw = gzip.decompress(raw)
    need(sha256(raw).hexdigest() == PINS[name], name + ' source pin')
    return raw


def plus(target, source, scale=F(1)):
    for j, value in source.items():
        value = target.get(j, F(0)) + scale * value
        if value:
            target[j] = value
        else:
            target.pop(j, None)


def multiply(left, right):
    out = []
    for row in left:
        result = {}
        for j, value in row.items():
            plus(result, right[j], value)
        out.append(result)
    return out


def deserialize(rows):
    return [{int(j): F(value) for j, value in row.items()} for row in rows]


def transpose(rows, n):
    columns = [{} for _ in range(n)]
    for i, row in enumerate(rows):
        for j, value in row.items():
            columns[j][i] = value
    return columns


def register(ref):
    need(ref[0] in ('L', 'C'), 'Register namespace')
    value = ref[1] + (704 if ref[0] == 'C' else 0)
    need(0 <= value < 712, 'Register bound')
    return value


def scalar_gate(event):
    if isinstance(event, dict):
        kind = event['kind']
        if kind == 'intrinsic_line':
            return None
        names = {'clear_owned': 'clear', 'physical_copy': 'copy', 'physical_add': 'add'}
        need(kind in names, 'Physical scalar grammar')
        return names[kind], event['target'], event.get('source'), F(event.get('coefficient', 1))
    if event[0] != 'scalar':
        need(event[0] in ('climb', 'phase', 'adapter', 'residual_adapter'), 'Retained event grammar')
        return None
    gate = event[1]
    kind, target = gate[0], register(gate[1])
    source = register(gate[2]) if kind in ('copy', 'add') else None
    value = F(*gate[-2:]) if kind in ('add', 'scale') else F(1)
    need(kind in ('clear', 'copy', 'add', 'scale'), 'Retained scalar grammar')
    need(source is None or target != source, 'Distinct scalar operands')
    return kind, target, source, value


def pullback(events, columns=None):
    """Propagate output coefficients backward through the word."""
    columns = deepcopy(columns) if columns is not None else [{j: F(1)} for j in range(712)]
    for event in reversed(events):
        gate = scalar_gate(event)
        if gate is None:
            continue
        kind, target, source, value = gate
        if kind == 'add':
            plus(columns[source], columns[target], value)
        elif kind == 'scale':
            columns[target] = {j: value * x for j, x in columns[target].items()}
        elif kind == 'copy':
            need(target >= 704, 'Only owned fields can be overwritten')
            plus(columns[source], columns[target])
            columns[target] = {}
        else:
            need(target >= 704, 'Only owned fields can be cleared')
            columns[target] = {}
    return columns


def frame_and_cost_check(events, word):
    frames = word['start'][:] + [None] * 8
    zero = [False] * 712
    scalar_cost, scalar_checks = 0, 0
    profile, kinds = Counter(), Counter()
    for event in events:
        if isinstance(event, dict):
            kind, target = event['kind'], event['target']
            kinds[kind] += 1
            endpoint = event['endpoint']
            need(endpoint in ('input', 'output'), 'Physical endpoint')
            if kind != 'physical_add':
                need(target == 704, 'Only serial C0 is used')
            chart = 0 if endpoint == 'input' else 1
            if kind == 'clear_owned':
                need(target == 704, 'Only C0 is cleared in the new blocks')
                frame = event['zero_frame']
                if frame == 'I':
                    frames[target] = 0
                else:
                    need(frame[0] == 'selected_source' and frame[1] in A, 'Selected zero chart')
                    frames[target] = word['start'][frame[1]] if endpoint == 'input' else word['final'][112 + frame[1]]
                zero[target] = True
                scalar_cost += 2
            elif kind == 'physical_copy':
                source = event['source']
                need(target == 704 and zero[target] and frames[target] == frames[source], 'Zero physical copy target')
                need(source in A if endpoint == 'input' else source - 112 in A, 'Selected copy source')
                zero[target] = zero[source]
                scalar_cost += 2
            elif kind == 'intrinsic_line':
                port = event['port']
                old = word['start'][port] if endpoint == 'input' else word['final'][112 + port]
                need(port in A and target == 704 and frames[target] == old, 'Line entry frame')
                need(event['power'] == (-1 if endpoint == 'input' else 1), 'Line direction')
                frames[target] = chart
                profile[1] += 1
            else:
                need(kind == 'physical_add' and event['source'] == 704, 'Physical ADD source')
                need(frames[target] == frames[704] == chart, 'Physical ADD chart')
                need(abs(F(event['coefficient'])) == 1, 'Unit boundary ADD')
                zero[target] = zero[target] and zero[704]
                scalar_cost += 8
            continue
        if event[0] == 'climb':
            _, _, target, old, new, rank = event
            need(frames[target] == old, 'Retained native entry frame')
            frames[target] = new
            profile[rank] += 1
        elif event[0] == 'scalar':
            kind, target, source, value = scalar_gate(event)
            scalar_checks += 1
            if kind == 'clear':
                need(target >= 704, 'Owned CLEAR')
                frames[target], zero[target] = event[2], True
            else:
                need(frames[target] == event[2] and (source is None or frames[source] == event[2]), 'Scalar frame equality')
                if kind == 'copy':
                    need(target >= 704, 'Owned COPY')
                    zero[target] = zero[source]
                elif kind == 'add':
                    zero[target] = zero[target] and zero[source]
            if kind in ('copy', 'clear'):
                scalar_cost += 2
            else:
                numerator, denominator = abs(value.numerator), value.denominator
                need(numerator > 0 and denominator & (denominator - 1) == 0, 'Dyadic scalar')
                if kind == 'scale':
                    need(numerator & (numerator - 1) == 0, 'Unit scale')
                    scalar_cost += 2 * (abs(numerator.bit_length() - denominator.bit_length()) + int(value < 0))
                else:
                    scalar_cost += 2 * (1 + numerator.bit_length() + numerator.bit_count() + denominator.bit_length())
    need(frames == word['final'] + [0] * 8, 'Complete endpoint frames')
    need(kinds == Counter(clear_owned=32, physical_copy=16, physical_add=16, intrinsic_line=16), 'Complete serial boundary blocks')
    need(scalar_cost == 209674 and sum(k * v for k, v in profile.items()) == 5538, 'Full local invoice')
    return scalar_cost, scalar_checks, dict(sorted(profile.items()))


def action(rows, value):
    return sum(((row & value).bit_count() % 2) << i for i, row in enumerate(rows))


def native_lines(recipes, word):
    seen, count = set(), 0
    for item in recipes:
        port, inv = item['port'], item['inverse']
        need((port, inv) not in seen and port in A, 'Unique line recipe')
        seen.add((port, inv))
        recipe = item['recipe']
        label = word['ports'][port]
        need(recipe['rank'] == 1 and item['label'] == label, 'Actual line direction')
        left, right = recipe['left'], recipe['right']
        for view in (left, right):
            need(view['phase'] == 0 and not any(view['linear_Z4']) and not any(view['quadratic_rows']), 'Exact monomial phases')
        for source in range(512):
            middle = action(right['matrix_rows'], source) ^ right['offset']
            actual = {action(left['matrix_rows'], middle) ^ left['offset']: (1, 1),
                      action(left['matrix_rows'], middle ^ 1) ^ left['offset']: (1, -1)}
            expected = {source: (1, -1) if inv else (1, 1), source ^ label: (1, 1) if inv else (1, -1)}
            need(actual == expected, 'Exact Gaussian line column with denominator two')
            need(actual != {source: expected[source ^ label], source ^ label: expected[source]}, 'Wrong line sign control')
            count += 1
    need(seen == {(p, inv) for p in A for inv in (False, True)}, 'Both signs for every selected port')
    return count


def main(out):
    directory = LANES / 'oblique-native-20261017'
    for name, key in (('OBLIQUE-BACKWARD.md', 'proof'), ('emit_oblique_backward.py', 'producer'), ('OBLIQUE-BACKWARD.json', 'producer_receipt')):
        pinned(directory / name, key)
    data = json.loads(pinned(directory / 'OBLIQUE-BACKWARD-PROGRAM.json.gz', 'payload', True))
    source = json.loads(pinned(LANES / 'paired-package-review/upstream-followthrough-20261015/current-query-encoder/UNIFORM-SIGNED-PROGRAMS.json.gz', 'uniform', True))
    pinned(LANES / 'coherent-port/current-query-review-20261015/UNIFORM-REVIEW.json', 'uniform_review')
    core = json.loads(pinned(LANES / 'circuit-interface/CENTRE-FREE-PROGRAMS.json.gz', 'core', True))['backward']
    word = json.loads(gzip.decompress(pinned(ROOT / 'work/five-pr-sprint-20261013/lanes/centre-sharing/CANONICAL-WORD.json.gz', 'word')))
    interface = json.loads(pinned(LANES / 'circuit-interface/INTERFACE.json', 'interface'))
    archive_path = ROOT / 'worktrees/k5-persistent-cleanup/research/community-frontier1094-audit/selected-replay.tar.gz'
    pinned(archive_path, 'archive')
    with tarfile.open(archive_path) as archive:
        raw = archive.extractfile('candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json').read()
    need(sha256(raw).hexdigest() == PINS['phases'], 'Phase source pin')
    phases = json.loads(raw)
    prefix = source['programs']['forward']['prefix']
    coded = source['programs']['coded_backward']
    program = data['program']
    need(program['input_return'] == prefix and len(prefix) == 40, 'Exact source input correction')
    need(program['retained_coded_backward'] == coded and coded['retained_core'] == core, 'Exact complete accepted tail')
    need(program['events'] == prefix + coded['events'], 'Whole word composition')
    need(program['events'][program['core_first']:program['core_first'] + program['core_length']] == core, 'Core span')

    r = deserialize(interface['R'])
    eye = [{j: F(1)} for j in range(112)]
    k = [{j: row[p] / 4 for j, row in enumerate(r) if p in row} for p in range(112)]
    kr = multiply(k, r)
    s = deepcopy(eye)
    a = deepcopy(eye)
    p = [dict(row) if i in A else {} for i, row in enumerate(kr)]
    for i in range(112):
        plus(s[i], kr[i], -1)
        if i in A:
            plus(s[i], {i: F(1)}, -1)
            a[i] = {i: F(12)}
        for j, value in kr[i].items():
            if (i in A) != (j in A):
                a[i][j] = -value
    pi = [{i: F(1)} if i in A else {} for i in range(112)]
    need(multiply(s, a) == multiply(a, s) == eye, 'Both source-derived inverse products')
    need(multiply(p, p) == p and multiply(p, a) == [{j: -v for j, v in row.items()} for row in pi], 'Oblique projection and source return')
    need(deserialize(data['R']) == r and deserialize(data['P']) == p and deserialize(data['S']) == s and deserialize(data['inverse_S']) == a, 'Independent matrix metadata')
    need(data['selected_A'] == A and deserialize(data['Pi']) == pi, 'Selected metadata')
    need(deserialize(data['K_A']) == [dict(row) if i in A else {} for i, row in enumerate(k)], 'Selected section metadata')
    expected = [{i: F(1)} for i in range(712)]
    for i in range(112):
        expected[i] = dict(a[i])
        plus(expected[i], pi[i])
        expected[i][112 + i] = F(-1)
        plus(expected[112 + i], pi[i], -1)
    expected[704:] = [{} for _ in range(8)]
    tail_columns = pullback(coded['events'])
    actual = pullback(prefix, tail_columns)
    need(actual == transpose(expected, 712), 'All 712 columns by reverse transpose propagation')
    need(all(actual[i] == {i: F(1)} for i in range(224, 704)), 'Every arbitrary helper restored')
    need(all(not actual[i] for i in range(704, 712)), 'No arbitrary private input leakage')
    need(tail_columns != actual, 'Omitted-return control')
    wrong = deepcopy(prefix)
    for event in wrong:
        if event['kind'] == 'physical_add':
            event['coefficient'] = '1'
    need(pullback(wrong, tail_columns) != actual, 'Reversed-return control')
    bad = deepcopy(prefix)
    bad[0]['target'] = 224
    try:
        pullback(bad, tail_columns)
    except ValueError:
        pass
    else:
        raise ValueError('Borrowed CLEAR control')
    cost, scalar_checks, profile = frame_and_cost_check(program['events'], word)
    columns = native_lines(data['line_recipes'], word)
    phase_cases = 0
    for port in A:
        recipe = phases['recipes'][port]
        q = recipe['q']
        axes = recipe['idle_children'][0]['orthogonal_axes'][:8]
        need(q == word['ports'][port] and q.bit_count() % 2 == 1, 'Actual odd line label')
        need(all((q & v).bit_count() % 2 == 0 for v in axes), 'Native route axes fix q')
        for stage, view in enumerate(recipe['stage_alignment']):
            moved = q
            if stage:
                for j, old in enumerate(axes):
                    v = old ^ (1 << (8 * stage + j + 1))
                    if (moved & v).bit_count() % 2:
                        moved ^= v
            need(moved == q, 'Actual route fixes the input and output line')
            need(view['entry_X'] == view['entry_Y'] and view['exit_X'] == view['exit_Y'], 'Paired exact exterior views')
            # C_q and its inverse cancel exactly. All native C directions
            # and exterior translations are polynomials in commuting X shifts.
            phase_cases += 2
    need(phase_cases == 144, 'All nine stages and both ends')
    result = dict(status='PASS_INDEPENDENT_OBLIQUE_BACKWARD', source_pins=PINS,
                  checker_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                  independent_method='reverse transpose propagation; no producer or prior interpreter import',
                  formal_input_columns=712, restored_helpers=480, private_zero_outputs=8,
                  scalar_cost=cost, scalar_frame_checks=scalar_checks, native_profile=profile,
                  native_mass=sum(k * v for k, v in profile.items()), native_children=sum(profile.values()),
                  exact_Gaussian_line_columns=columns, actual_exterior_cases=phase_cases,
                  controls=['omitted input return', 'reversed input return', 'borrowed helper CLEAR', 'all sixteen reversed line signs'],
                  retained_native_proof='inherited byte-identical accepted uniform word',
                  global_controller_or_recursive_invoice=False)
    need(not out.exists(), 'Use a new receipt path')
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(result['status'])
    print(json.dumps({k: result[k] for k in ('scalar_cost', 'native_mass', 'native_children', 'exact_Gaussian_line_columns', 'actual_exterior_cases')}, sort_keys=True))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    main(parser.parse_args().out)
