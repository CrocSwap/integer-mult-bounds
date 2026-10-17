#!/usr/bin/env python3
"""Independent backward verification of the bounded V45 comparison.

No predecessor Python module or producer/forward replay is imported.  Rational
covectors are pulled backward through the literal gates; inverse columns are
obtained by independently reversing the gate operations.  Every nonzero free
word coefficient in the twelve requested rows is retained and compared.
"""
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import copy
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
U12 = (2, 61, 62, 63, 70, 71, 72, 94, 249, 251, 265, 267)
P4 = (249, 251, 265, 267)
J12 = (2, 9, 10, 11, 70, 71, 72, 79, 249, 251, 265, 267)
V45 = (256, 128, 64, 35, 16, 11, 5)
STEMS = {
    '2894': 'research/helper408-rank7-pairing/sources/data/PARENT',
    '2917': 'research/paired-helper-extension/data/WORD',
    '2942': 'research/rank7-joint-endframes/data/PARENT',
    '2979': 'research/rank7-joint-endframes/data/WORD',
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate():
    """Bind bytes before interpreting data; no imported source or pyc cache."""
    data = {}
    sources = json.loads((HERE / 'SOURCES.json').read_bytes())
    for item in sources['files']:
        if item['usage'] != 'input':
            continue
        path = item['path']
        require(path not in data, 'duplicate authenticated input')
        resolved = (ROOT / path).resolve()
        require(resolved.is_relative_to(ROOT.resolve()), 'input outside repository')
        raw = resolved.read_bytes()
        require(hashlib.sha256(raw).hexdigest() == item['sha256'], 'source sha256: ' + path)
        blob = b'blob ' + str(len(raw)).encode() + b'\0' + raw
        require(hashlib.sha1(blob).hexdigest() == item['git_blob'], 'source blob: ' + path)
        data[path] = raw
    return data


def read_data(raw, path):
    require(path in raw, 'unauthenticated input: ' + path)
    payload = gzip.decompress(raw[path]) if path.endswith('.gz') else raw[path]
    return json.loads(payload)


def live_registers(provider):
    removed = provider['removed']
    require(len(removed) == len(set(removed)), 'duplicate removed register')
    require(all(isinstance(r, int) and 0 <= r < 704 for r in removed), 'bad removed register')
    return tuple(r for r in range(704) if r not in removed and not 112 <= r < 224)


def eligible(provider, live):
    protected = set(map(int, provider['helper_final'])) | set(map(int, provider['start_extra']))
    protected.update(x['source'] for x in provider['initial_corrections'])
    return frozenset(r for r in live if r >= 224 and r not in protected)


def gates(provider):
    """Input immediately after prelude; stop after restore, before cleanup."""
    result = list(provider['A'][provider['prelude_events']:])
    resets = {}
    for symbol, record in enumerate(provider['warps'], 1):
        pos, reg = record[:2]
        require(0 <= pos <= len(provider['B']), 'warp position')
        resets.setdefault(pos, []).append(['warp', reg, symbol])
    for pos in range(len(provider['B']) + 1):
        result.extend(resets.get(pos, ()))
        if pos != len(provider['B']):
            result.append(provider['B'][pos])
    result.extend(provider['restore'])
    kept = [g for g in result if not 112 <= g[1] < 224]
    live = set(live_registers(provider))
    for g in kept:
        require(g[0] in ('add', 'scale', 'warp'), 'unrecognized gate')
        require(g[1] in live, 'gate outside live coordinates')
        if g[0] == 'add':
            require(g[2] in live and g[1] != g[2], 'illegal add dependency')
        if g[0] in ('add', 'scale'):
            a, b = g[3:5] if g[0] == 'add' else g[2:4]
            require(isinstance(a, int) and isinstance(b, int) and b != 0 and abs(b) & (abs(b) - 1) == 0, 'non-dyadic gate')
            if g[0] == 'scale':
                require(a != 0 and abs(a) & (abs(a) - 1) == 0, 'non-unit dyadic scale')
    return kept


def put(vector, key, value):
    value += vector.get(key, Q(0))
    if value:
        vector[key] = value
    else:
        vector.pop(key, None)


def append_word(word, symbol):
    return word[:-1] if word and word[-1] == -symbol else word + (symbol,)


def prepend_word(symbol, word):
    return word[1:] if word and word[0] == -symbol else (symbol,) + word


def backward_row(program, output):
    """r <- r G at each reversed gate; warp multiplication is on the right."""
    row = {(output, ()): Q(1)}
    for g in reversed(program):
        kind, dst = g[:2]
        terms = [(w, c) for (r, w), c in row.items() if r == dst]
        if not terms:
            continue
        if kind == 'add':
            q = Q(g[3], g[4])
            for word, c in terms:
                put(row, (g[2], word), q * c)
        elif kind == 'scale':
            q = Q(g[2], g[3])
            for word, c in terms:
                row[dst, word] = q * c
        else:
            for word, _ in terms:
                del row[dst, word]
            for word, c in terms:
                put(row, (dst, append_word(word, g[2])), c)
    return row


def inverse_column(program, output):
    """x <- G^-1 x in reverse chronological order; warp acts on the left."""
    state = {output: {(): Q(1)}}
    for g in reversed(program):
        kind, dst = g[:2]
        if kind == 'add':
            src = state.get(g[2], {})
            if src:
                dest = state.setdefault(dst, {})
                for word, value in tuple(src.items()):
                    put(dest, word, -Q(g[3], g[4]) * value)
                if not dest:
                    state.pop(dst)
        elif dst in state:
            if kind == 'scale':
                state[dst] = {w: c * Q(g[3], g[2]) for w, c in state[dst].items()}
            else:
                moved = {}
                for word, value in state[dst].items():
                    put(moved, prepend_word(-g[2], word), value)
                state[dst] = moved
    return {(r, w): c for r, poly in state.items() for w, c in poly.items()}


def nullspace(equations, size):
    rows = [[Q(v) for v in row] for row in equations if any(row)]
    require(all(len(row) == size for row in rows), 'equation width')
    pivots = []
    for col in range(size):
        selected = next((k for k in range(len(pivots), len(rows)) if rows[k][col]), None)
        if selected is None:
            continue
        k = len(pivots)
        rows[k], rows[selected] = rows[selected], rows[k]
        q = rows[k][col]
        rows[k] = [x / q for x in rows[k]]
        for j in range(len(rows)):
            if j != k and rows[j][col]:
                q = rows[j][col]
                rows[j] = [a - q * b for a, b in zip(rows[j], rows[k])]
        pivots.append(col)
    free = [j for j in range(size) if j not in pivots]
    result = []
    for j in free:
        v = [Q(0)] * size
        v[j] = Q(1)
        for k, pivot in enumerate(pivots):
            v[pivot] = -rows[k][j]
        result.append(v)
    return result


def allowed_combinations(vectors, H):
    keys = sorted({key for vec in vectors for key in vec if key[0] not in H or key[1]})
    equations = [[v.get(key, Q(0)) for v in vectors] for key in keys]
    basis = nullspace(equations, len(vectors))
    for b in basis:
        image = {}
        for c, vector in zip(b, vectors):
            for key, value in vector.items():
                put(image, key, c * value)
        require(all(r in H and not w for r, w in image), 'kernel image support')
    return basis


def dyadic_unit(q):
    q = Q(q)
    a, b = abs(q.numerator), q.denominator
    return a != 0 and a & (a - 1) == 0 and b & (b - 1) == 0


def determinant(matrix):
    a = [[Q(x) for x in row] for row in matrix]
    require(all(len(row) == len(a) for row in a), 'determinant nonsquare')
    value = Q(1)
    for col in range(len(a)):
        p = next((k for k in range(col, len(a)) if a[k][col]), None)
        if p is None:
            return Q(0)
        if p != col:
            a[p], a[col] = a[col], a[p]
            value = -value
        q = a[col][col]
        value *= q
        for j in range(col + 1, len(a)):
            ratio = a[j][col] / q
            for k in range(col + 1, len(a)):
                a[j][k] -= ratio * a[col][k]
    return value


def scalar_minor(rows, outputs, columns, H, expected):
    require(len(outputs) == len(columns), 'minor dimensions')
    require(len(set(columns)) == len(columns) and not set(columns) & H, 'minor protected columns')
    require(all(not word for r in outputs for col, word in rows[r] if col in columns), 'minor non-scalar coefficient')
    matrix = [[rows[r].get((c, ()), Q(0)) for c in columns] for r in outputs]
    require(determinant(matrix) == expected, 'minor determinant')
    return matrix


def span(values):
    """Explicit finite vector subspace, independent of the producer's basis RREF."""
    result = {0}
    for v in values:
        require(isinstance(v, int) and 0 <= v < 512, 'frame coordinate')
        result |= {x ^ v for x in result}
    return frozenset(result)


def terminals(provider):
    live = set(range(704)) - set(provider['removed'])
    current = {r: span([provider['ports'][r]]) if r < 112 else frozenset({0}) for r in live}
    for r, f in provider['start_extra'].items():
        current[int(r)] = span(f)

    def scalar(g):
        f = span(g[-1])
        regs = g[1:3] if g[0] == 'add' else g[1:2]
        for r in regs:
            require(r in current and current[r] <= f, 'nonmonotone frame incident')
            current[r] = f

    for g in provider['A']:
        if g[0] == 'warp':
            require(current[g[1]] == span(g[3]), 'A warp frame mismatch')
            require(provider['warps'][abs(g[2]) - 1][1] == g[1], 'A warp register mismatch')
            current[g[1]] = span(g[4])
        else:
            scalar(g)
    require(all(current[r] == span(f) for r, f in zip(provider['centers'], provider['center_frames'])), 'center frame mismatch')
    require(all(g[0] == 'add' and 112 <= g[1] < 224 and g[2] in provider['centers'] for g in provider['cut']), 'center cut convention')
    reset = {}
    for entry in provider['warps']:
        reset.setdefault(entry[0], []).append(entry)
    for position in range(len(provider['B']) + 1):
        for _, r, _, before, after in reset.get(position, ()):
            require(current[r] == span(before), 'B warp frame mismatch')
            current[r] = span(after)
        if position < len(provider['B']):
            scalar(provider['B'][position])
    for g in provider['restore']:
        scalar(g)
    for r, expected in provider['helper_final'].items():
        require(current[int(r)] == span(expected), 'declared helper final mismatch')
    return tuple(r for r in live_registers(provider) if current[r] <= span(V45))


def apply_stage1(provider, edits):
    result = copy.deepcopy(provider)
    for r, change in edits['helper_final_changes'].items():
        require(result['helper_final'][r] == change['old'], 'stage1 old helper frame')
        result['helper_final'][r] = change['new']
    for item in edits['frame_edits']:
        g = result[item['section']][item['index']]
        require(g[:-1] == item['gate'] and g[-1] == item['old_frame'], 'stage1 old scalar gate')
        g[-1] = item['new_frame']
    return result


def encode_rows(rows):
    return [[r, c, list(w), str(v)] for r in sorted(rows) for (c, w), v in sorted(rows[r].items())]


def exact_rows(actual, expected):
    require(encode_rows(actual) == encode_rows(expected), 'complete row coefficient mismatch')


def rejects(action, label, expected_message):
    try:
        action()
    except ValueError as error:
        if str(error) != expected_message:
            raise
        return label
    raise RuntimeError('negative control unexpectedly accepted: ' + label)


def fixtures():
    program = [['warp', 0, 1], ['add', 1, 0, 3, 2], ['warp', 1, 2], ['warp', 0, -1]]
    expected = {(0, (2, 1)): Q(3, 2), (1, (2,)): Q(1)}
    require(backward_row(program, 1) == expected, 'noncommuting right-product order fixture')
    require(inverse_column(program, 0) == {(0, ()): Q(1), (1, (1,)): Q(-3, 2)}, 'inverse-column fixture')
    require(append_word((1, 2), -2) == (1,), 'free reduction fixture')
    require(append_word((1, 2), -1) == (1, 2, -1), 'nonadjacent cancellation fixture')
    return ['noncommuting_order', 'inverse_column', 'adjacent_cancellation', 'nonadjacent_no_cancellation']


def decode_scalar(vector, allowed):
    require(isinstance(vector, dict), 'malformed scalar vector')
    out = {}
    for r, coefficient in vector.items():
        r = int(r)
        c = Q(coefficient)
        require(r in allowed and c != 0, 'scalar vector domain or zero coefficient')
        out[r, ()] = c
    return out


def combine(coefficients, vectors):
    out = {}
    for (r, word), factor in coefficients.items():
        require(not word and r in vectors, 'combination domain')
        for key, value in vectors[r].items():
            put(out, key, factor * value)
    return out


def check_primary_analysis(analysis, rows, inverse, support, H):
    """Verify its full basis witnesses against our independently computed maps."""
    m = len(support)
    left = allowed_combinations([rows[r] for r in support], H)
    right = allowed_combinations([inverse[r] for r in support], H)
    require(analysis['inverse']['dimension'] == len(left), 'primary left dimension')
    require(analysis['forward']['dimension'] == len(right), 'primary right dimension')
    require(len(analysis['Alpha']) == len(analysis['U']) == len(left), 'primary left basis size')
    require(len(analysis['Y']) == len(analysis['V']) == len(right), 'primary right basis size')
    alphas = [decode_scalar(a, support) for a in analysis['Alpha']]
    ys = [decode_scalar(y, support) for y in analysis['Y']]
    us = [decode_scalar(u, H) for u in analysis['U']]
    vs = [decode_scalar(v, H) for v in analysis['V']]
    for alpha, u in zip(alphas, us):
        require(combine(alpha, rows) == u, 'primary complete left witness')
    for y, v in zip(ys, vs):
        require(combine(y, inverse) == v, 'primary complete right witness')
    for basis in (alphas, ys):
        columns = [[v.get((r, ()), Q(0)) for v in basis] for r in support]
        require(not nullspace(columns, len(basis)), 'primary dependent basis')
    pairing = [[sum(a.get((r, ()), Q(0)) * y.get((r, ()), Q(0)) for r in support) for y in ys] for a in alphas]
    require([[str(x) for x in row] for row in pairing] == analysis['pairing'], 'primary pairing entries')
    expected_det = str(determinant(pairing)) if alphas and len(alphas) == len(ys) else None
    require(expected_det == analysis['pairing_determinant'], 'primary basis determinant')
    certificate = analysis['nuisance_certificate']
    columns = certificate['columns']
    require(certificate['rows'] == list(support), 'primary nuisance row list')
    require(len(set(columns)) == len(columns) and not set(columns) & H, 'primary nuisance column domain')
    require(all(not word for r in support for col, word in rows[r] if col in columns), 'primary nuisance scalar restriction')
    nuisance = [[rows[r].get((c, ()), Q(0)) for c in columns] for r in support]
    require(certificate['matrix'] == [[str(x) for x in row] for row in nuisance], 'primary nuisance entries')
    require(certificate['nonempty_word_coefficients'] == 0, 'primary nuisance word count')
    rank = len(columns) - len(nullspace(nuisance, len(columns)))
    require(certificate['rank'] == rank, 'primary nuisance rank')
    witness_rows = certificate['rank_witness_rows']
    require(set(witness_rows) <= set(support) and len(set(witness_rows)) == len(witness_rows), 'primary witness row domain')
    witness = [[rows[r].get((c, ()), Q(0)) for c in columns] for r in witness_rows]
    require(witness == [[Q(x) for x in row] for row in certificate['rank_witness_matrix']], 'primary witness entries')
    require(str(determinant(witness)) == certificate['rank_witness_determinant'], 'primary witness determinant')
    require(dyadic_unit(determinant(witness)) == certificate['rank_witness_dyadic_unit'], 'primary witness unit')
    det = determinant(nuisance) if len(nuisance) == len(columns) else None
    require((None if det is None else str(det)) == certificate['determinant'], 'primary nuisance determinant')
    require((False if det is None else dyadic_unit(det)) == certificate['dyadic_unit'], 'primary nuisance unit')
    completion = analysis.get('paired_nuisance_completion')
    if completion is not None:
        whole = [[y.get((r, ()), Q(0)) for y in ys] + row for r, row in zip(support, nuisance)]
        require(whole == [[Q(x) for x in row] for row in completion['matrix']], 'primary nuisance completion entries')
        require(str(determinant(whole)) == completion['determinant'], 'primary nuisance completion determinant')
        require(dyadic_unit(determinant(whole)) == completion['dyadic_unit'], 'primary nuisance completion unit')
        ab = [[sum(alpha.get((r, ()), Q(0)) * rows[r].get((c, ()), Q(0)) for r in support) for c in columns] for alpha in alphas]
        require(all(not x for row in ab for x in row), 'primary nuisance kernel inclusion')
        require(ab == [[Q(x) for x in row] for row in completion['alpha_times_nuisance']], 'primary nuisance kernel entries')
    if analysis.get('with_known_P4') is not None:
        check_primary_analysis(analysis['with_known_P4'], rows, inverse, support, H | frozenset(P4))


def check_primary_stage(primary, rows, inverse, support, H):
    require(primary['U12_coefficients'] == encode_rows(rows), 'primary complete U12 coefficients')
    require(primary['eligible_H'] == sorted(H), 'primary eligibility set')
    require(primary['literal_V45_support'] == list(support), 'primary literal support')
    check_primary_analysis(primary['U12'], rows, inverse, U12, H)
    check_primary_analysis(primary['literal'], rows, inverse, support, H)


def run(expected=None):
    raw = authenticate()
    if expected is None:
        expected = json.loads((HERE / 'EXPECTED.json').read_bytes())
    edits = read_data(raw, 'research/rank7-joint-endframes/data/STAGE1-FRAME-EDITS.json')
    report = {'method': 'backward_covectors_and_inverse_columns', 'fixtures': fixtures(), 'providers': {}, 'controls': []}
    cache = {}
    for variant in ('base', 'extra'):
        words = {stage: read_data(raw, stem + '-' + variant + '.json.gz') for stage, stem in STEMS.items()}
        words['stage1'] = apply_stage1(words['2942'], edits)
        for stage in ('2894', '2917', '2942', 'stage1', '2979'):
            p = words[stage]
            live = live_registers(p)
            H = eligible(p, live)
            prelude = p['A'][:p['prelude_events']]
            require(all(g[0] == 'warp' or 112 <= g[1] < 224 for g in prelude), 'prelude non-target scalar')
            require(not H & {g[1] for g in prelude if g[0] == 'warp'}, 'prelude modifies fresh H')
            prog = gates(p)
            rows = {r: backward_row(prog, r) for r in U12}
            inverse = [inverse_column(prog, r) for r in U12]
            A = allowed_combinations([rows[r] for r in U12], H)
            Y = allowed_combinations(inverse, H)
            pairing = [[sum(a * b for a, b in zip(alpha, y)) for y in Y] for alpha in A]
            support = terminals(p)
            expected_support = U12 if stage == 'stage1' else tuple(r for r in U12 if r not in (61, 63)) if stage == '2979' else ()
            require(support == expected_support, 'literal terminal support')
            old = stage in ('2894', '2917')
            require(len(A) == len(Y) == (4 if old else 0), 'fresh pairing spaces dimensions')
            if old:
                require(determinant(pairing) != 0, 'old pairing degenerate')
            else:
                require(all(c not in H for row in rows.values() for c, _ in row), 'fresh eligible dependence remains')
                scalar_minor(rows, U12, J12, H, Q(2))
                enlarged = H | frozenset(P4)
                require(len(allowed_combinations([rows[r] for r in U12], enlarged)) == 4, 'protected pivot left access control')
                require(len(allowed_combinations(inverse, enlarged)) == 4, 'protected pivot right access control')
                if stage == '2979':
                    j10 = tuple(c for c in J12 if c not in (9, 11))
                    scalar_minor(rows, support, j10, H, Q(1))
            primary_label = {'2894': 'PR2894', '2917': 'PR2917', '2942': 'PR2942', 'stage1': 'PR2979_stage1', '2979': 'PR2979_final'}[stage]
            primary = expected['variants'][variant]['stages'][primary_label]
            check_primary_stage(primary, rows, dict(zip(U12, inverse)), support, H)
            key = variant + ':' + stage
            cache[key] = rows
            report['providers'][key] = {
                'eligible_count': len(H), 'live_count': len(live), 'middle_gate_count': len(prog),
                'literal_support': list(support), 'row_coefficient_count': sum(map(len, rows.values())),
                'left_dimension': len(A), 'right_dimension': len(Y),
                'independent_basis_pairing_determinant': str(determinant(pairing)),
                'primary_basis_pairing_determinant': primary['U12']['pairing_determinant'],
                'nuisance_determinant': None if old else '2', 'rows': encode_rows(rows),
            }
        exact_rows(cache[variant + ':2894'], cache[variant + ':2917'])
        exact_rows(cache[variant + ':2942'], cache[variant + ':stage1'])
        exact_rows(cache[variant + ':2942'], cache[variant + ':2979'])
    for stage in ('2894', '2917', '2942', 'stage1', '2979'):
        exact_rows(cache['base:' + stage], cache['extra:' + stage])
    oldrows = cache['base:2894']
    corrupt = copy.deepcopy(oldrows)
    first = next(iter(corrupt[U12[0]]))
    corrupt[U12[0]][first] += 1
    report['controls'].append(rejects(lambda: exact_rows(corrupt, oldrows), 'single_coefficient_corruption', 'complete row coefficient mismatch'))
    p = words['2979']
    H = eligible(p, live_registers(p))
    rows = cache['extra:2979']
    report['controls'].append(rejects(lambda: scalar_minor(rows, U12, J12[:-1], H, Q(2)), 'missing_forbidden_column', 'minor dimensions'))
    report['controls'].append(rejects(lambda: scalar_minor(rows, U12, J12, H | frozenset(P4), Q(2)), 'protected_pivot_misclassified', 'minor protected columns'))
    report['controls'].append(rejects(lambda: require(terminals(p) == U12, 'literal terminal support'), 'wrong_terminal_support', 'literal terminal support'))
    non_scalar = copy.deepcopy(rows)
    non_scalar[U12[0]][J12[0], (1,)] = Q(1)
    report['controls'].append(rejects(lambda: scalar_minor(non_scalar, U12, J12, H, Q(2)), 'non_scalar_minor_coefficient', 'minor non-scalar coefficient'))
    return report


def main():
    report = run()
    if len(sys.argv) == 3 and sys.argv[1] == '--output':
        Path(sys.argv[2]).write_text(json.dumps(report, indent=2) + '\n')
    else:
        require(len(sys.argv) == 1, 'usage: independent.py [--output FILE]')
    concise = {key: {k: v for k, v in item.items() if k != 'rows'} for key, item in report['providers'].items()}
    print(json.dumps({'independent': 'PASS', 'providers': concise, 'controls': report['controls'], 'fixtures': report['fixtures']}, sort_keys=True))


if __name__ == '__main__':
    main()
