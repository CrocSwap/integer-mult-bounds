#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent source parser, reverse adjoint, RREF census and Bareiss checks.

No predecessor Python module or primary verifier is imported. Shared scientific
inputs are the two authenticated JSON providers and the proposed certificates.
The reverse-adjoint method follows the credited PR2918 independent checker;
its implementation here also checks every low-rank terminal row and endpoint.
"""
import copy
from collections import Counter
from fractions import Fraction as F
import gzip
import hashlib
import json
from math import lcm, prod
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / 'helper408-rank7-pairing/sources/data'
HASHES = {
    'base': 'c20a470aec0f3e61833cb41fe190639eb358f58017143d2336c55c80fba265eb',
    'extra': 'db34e39876241087b581ed9374c53e9cd393e3e86ef6103bfb54f3077c3d2761',
}
PIN = '9360ba7312cf8961e672e9eb26c612719028d39d'
TARGET = set(range(112, 224))


def check(ok, why):
    if not ok:
        raise ValueError(why)


def load_provider(raw, variant):
    check(hashlib.sha256(raw).hexdigest() == HASHES[variant], 'provider bytes changed')
    return json.loads(gzip.decompress(raw))


def span(basis):
    values = {0}
    for v in basis:
        check(isinstance(v, int) and 0 <= v < 512, 'frame outside GF(2)^9')
        values |= {x ^ v for x in values}
    return frozenset(values)


def parse(p):
    check(len(p['ports']) == 112 and len(p['warps']) == 72, 'provider shape')
    live = set(range(704)) - set(p['removed'])
    frames = [span([p['ports'][r]]) if r < 112 else span([]) for r in range(704)]
    for r, f in p['start_extra'].items():
        frames[int(r)] = span(f)
    after = {}
    for i, w in enumerate(p['warps']):
        check(0 <= w[0] <= len(p['B']), 'warp position')
        after.setdefault(w[0], []).append(['warp', w[1], i + 1, w[3], w[4]])
    events = list(p['A'])
    for i in range(len(p['B']) + 1):
        events.extend(after.get(i, []))
        if i < len(p['B']):
            events.append(p['B'][i])
    events.extend(p['restore'])
    seen = set()
    for i, g in enumerate(events):
        kind, d = g[:2]
        check(d in live, 'gate uses removed destination')
        if kind == 'warp':
            check(frames[d] == span(g[3]), 'warp before-frame')
            check(1 <= abs(g[2]) <= 72 and p['warps'][abs(g[2]) - 1][1] == d,
                  'warp register identity')
            regs, nxt = [d], span(g[4])
        else:
            check(kind in ('add', 'scale'), 'unknown operation')
            regs = [d, g[2]] if kind == 'add' else [d]
            nxt = span(g[-1])
            check(all(r in live and frames[r] <= nxt for r in regs), 'nonmonotone frame')
            q = F(g[3], g[4]) if kind == 'add' else F(g[2], g[3])
            check(q.denominator & (q.denominator - 1) == 0, 'non-dyadic gate coefficient')
            if kind == 'scale':
                check(unit(q), 'scale is not a dyadic unit')
        for r in regs:
            frames[r] = nxt
            seen.add(r)
        if i + 1 == len(p['A']):
            check(all(frames[r] == span(f) for r, f in zip(p['centers'], p['center_frames'])),
                  'center frame cut')
            check(all(g[0] == 'add' and g[1] in TARGET and g[2] in p['centers']
                      for g in p['cut']), 'center cut access')
    check(live <= seen, 'unaccounted terminal incidence')
    check(all(frames[int(r)] == span(f) for r, f in p['helper_final'].items()),
          'protected helper frame')
    eligible = (set(range(224, 704)) & live) - (
        set(map(int, p['helper_final'])) | set(map(int, p['start_extra'])) |
        {c['source'] for c in p['initial_corrections']})
    prelude = events[:p['prelude_events']]
    check(all(not ({g[1]} | ({g[2]} if g[0] == 'add' else set())) & eligible
              for g in prelude if g[1] not in TARGET), 'prelude touches eligible input')
    ops = []
    for g in events[p['prelude_events']:]:
        if g[1] in TARGET:
            continue
        check(g[0] != 'add' or g[2] not in TARGET, 'non-target depends on target')
        ops.append(g)
    check(len(ops) == 4583 and len(eligible) == 226, 'frozen interface size')
    return ops, {r: frames[r] for r in live - TARGET}, eligible


def add(dest, source, q):
    for key, c in list(source.items()):
        value = dest.get(key, F(0)) + q * c
        if value:
            dest[key] = value
        else:
            dest.pop(key, None)


def rows_by_adjoint(ops, terminals):
    state = [{} for _ in range(704)]
    for r in terminals:
        state[r][r, ()] = F(1)
    for g in reversed(ops):
        kind, d = g[:2]
        if kind == 'add':
            add(state[g[2]], state[d], F(g[3], g[4]))
        elif kind == 'scale':
            q = F(g[2], g[3])
            state[d] = {key: q * c for key, c in state[d].items()}
        else:
            t = g[2]
            state[d] = {(r, w[:-1] if w and w[-1] == -t else w + (t,)): c
                        for (r, w), c in state[d].items()}
    rows = {r: {} for r in terminals}
    for j, polynomials in enumerate(state):
        for (r, word), c in polynomials.items():
            rows[r][j, word] = c
    return rows


def inverse_column(ops, output):
    state = [{} for _ in range(704)]
    for r, c in output.items():
        state[r][()] = F(c)
    for g in reversed(ops):
        kind, d = g[:2]
        if kind == 'add':
            add(state[d], state[g[2]], -F(g[3], g[4]))
        elif kind == 'scale':
            q = F(g[3], g[2])
            state[d] = {w: q * c for w, c in state[d].items()}
        else:
            t = -g[2]
            state[d] = {w[1:] if w and w[0] == -t else (t,) + w: c
                        for w, c in state[d].items()}
    check(all(set(poly) <= {()} for poly in state), 'rank-eight inverse not scalar')
    return {r: poly[()] for r, poly in enumerate(state) if poly}


def endpoint_partition(frames):
    """Enumerate unique two-row reduced echelon normal matrices, low pivots.

    Primary census instead chooses the two least elements of each normal
    plane. This code forms each endpoint's full set of 128 bit vectors and
    tests containment of each full terminal-frame span.
    """
    orthogonal = [sum(1 << x for x in range(512) if (a & x).bit_count() % 2 == 0)
                  for a in range(512)]
    by_frame = {}
    for r, f in frames.items():
        if len(f) <= 128:
            by_frame.setdefault(sum(1 << x for x in f), []).append(r)
    groups = Counter()
    endpoints = set()
    for i in range(9):
        for j in range(i + 1, 9):
            free = [(0, c) for c in range(i + 1, 9) if c != j]
            free += [(1, c) for c in range(j + 1, 9)]
            for bits in range(1 << len(free)):
                normals = [1 << i, 1 << j]
                for k, (row, col) in enumerate(free):
                    if bits >> k & 1:
                        normals[row] |= 1 << col
                e = orthogonal[normals[0]] & orthogonal[normals[1]]
                check(e.bit_count() == 128 and e not in endpoints, 'endpoint repeated or wrong rank')
                endpoints.add(e)
                support = tuple(sorted(r for f, regs in by_frame.items() if f & ~e == 0 for r in regs))
                groups[support] += 1
    check(len(endpoints) == 43435 and len(groups) == 239, 'independent endpoint count')
    return groups


def bareiss(matrix):
    n = len(matrix)
    check(all(len(row) == n for row in matrix), 'minor not square')
    if not n:
        return F(1)
    scales = [lcm(*(c.denominator for c in row)) for row in matrix]
    a = [[int(c * scale) for c in row] for row, scale in zip(matrix, scales)]
    previous, sign = 1, 1
    for k in range(n - 1):
        p = next((i for i in range(k, n) if a[i][k]), None)
        if p is None:
            return F(0)
        if p != k:
            a[k], a[p] = a[p], a[k]
            sign = -sign
        pivot = a[k][k]
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                numerator = a[i][j] * pivot - a[i][k] * a[k][j]
                check(numerator % previous == 0, 'Bareiss inexact division')
                a[i][j] = numerator // previous
            a[i][k] = 0
        previous = pivot
    return F(sign * a[-1][-1], prod(scales))


def unit(q):
    a, b = abs(q.numerator), q.denominator
    return a != 0 and a & (a - 1) == 0 and b & (b - 1) == 0


def validate_minor(item, rows, frames, eligible):
    rr, jj = item['R'], item['forbidden_minor_columns']
    a, b = item['annihilator']
    check(0 < a < 512 and 0 < b < 512 and a != b, 'annihilator invalid')
    actual = {r for r, f in frames.items()
              if all((a & x).bit_count() % 2 == 0 and (b & x).bit_count() % 2 == 0 for x in f)}
    check(set(rr) == actual and len(rr) == len(actual), 'complete terminal support mismatch')
    check(len(jj) == len(rr) and len(set(jj)) == len(jj), 'minor size mismatch')
    check(set(jj) <= set(frames) - eligible, 'illegal nuisance input')
    matrix = []
    for r in rr:
        check(all(not word for (j, word) in rows[r] if j in jj), 'hidden operator in scalar minor')
        matrix.append([rows[r].get((j, ()), F(0)) for j in jj])
    check(all(c.denominator & (c.denominator - 1) == 0 for row in matrix for c in row),
          'minor coefficient is not dyadic')
    determinant = bareiss(matrix)
    check(unit(determinant), 'minor determinant is not a dyadic unit')
    check(determinant == F(item['forbidden_minor_determinant']), 'determinant certificate mismatch')
    check(item['pure_scalar_forbidden_rank'] == len(rr), 'certified rank mismatch')
    check(item['H_eligible'] == sorted(eligible & set(rr)), 'eligible terminal intersection')
    check(item['status'] == 'UNIVERSAL_SCALAR_MINOR_OBSTRUCTION', 'class status mismatch')
    return determinant


def coverage(items, groups):
    check(len(items) == len(groups), 'support class omitted')
    received = {tuple(c['R']): c['multiplicity'] for c in items}
    check(len(received) == len(items) and received == groups, 'endpoint partition differs')


def rejects(action, name, expected):
    try:
        action()
    except ValueError as error:
        check(str(error) == expected, 'negative control failed for wrong reason: ' + name + ': ' + str(error))
        return name
    raise ValueError('negative control accepted: ' + name)


def controls(raw, variant, report, rows, frames, eligible, groups):
    items = report['classes']
    item = next(c for c in items if c['R'])
    out = [rejects(lambda: load_provider(raw + b' ', variant), 'source drift', 'provider bytes changed')]
    bad = copy.deepcopy(item)
    bad['forbidden_minor_determinant'] = str(F(bad['forbidden_minor_determinant']) * 2)
    out.append(rejects(lambda: validate_minor(bad, rows, frames, eligible), 'wrong determinant', 'determinant certificate mismatch'))
    bad = copy.deepcopy(item)
    bad['forbidden_minor_columns'][0] = min(eligible)
    out.append(rejects(lambda: validate_minor(bad, rows, frames, eligible), 'eligible nuisance', 'illegal nuisance input'))
    out.append(rejects(lambda: coverage(items[:-1], groups), 'omitted class', 'support class omitted'))
    badrows = dict(rows)
    r, j = item['R'][0], item['forbidden_minor_columns'][0]
    badrows[r] = dict(rows[r])
    badrows[r][j, (72,)] = F(1)
    out.append(rejects(lambda: validate_minor(item, badrows, frames, eligible), 'hidden word', 'hidden operator in scalar minor'))
    badrows[r] = {key: c for key, c in rows[r].items() if key[0] not in item['forbidden_minor_columns']}
    out.append(rejects(lambda: validate_minor(item, badrows, frames, eligible), 'singular block', 'minor determinant is not a dyadic unit'))
    badrows[r] = dict(rows[r])
    badrows[r][j, ()] = F(1, 3)
    out.append(rejects(lambda: validate_minor(item, badrows, frames, eligible), 'non-dyadic entry', 'minor coefficient is not dyadic'))
    check(bareiss([[F(0), F(1)], [F(2), F(3)]]) == -2, 'Bareiss pivot-swap calibration')
    check(not unit(F(3)) and unit(F(-1, 4)) and not unit(F(0)), 'dyadic unit calibration')
    return out


def main():
    envelope = json.loads((HERE / 'certificates.json').read_text())
    check(envelope['schema_version'] == 1 and set(envelope['providers']) == set(HASHES), 'certificate envelope')
    receipts = {}
    for variant in HASHES:
        raw = (DATA / ('PARENT-' + variant + '.json.gz')).read_bytes()
        ops, frames, eligible = parse(load_provider(raw, variant))
        low = {r for r, f in frames.items() if len(f) <= 128}
        rows = rows_by_adjoint(ops, low | {42})
        check(len(low) == 164 and len(frames) == 520, 'terminal row count')
        groups = endpoint_partition(frames)
        report = envelope['providers'][variant]
        check(report['pin'] == PIN and report['source_sha256'] == HASHES[variant], 'report pin')
        check(report['H'] == sorted(eligible), 'report eligible inputs')
        coverage(report['classes'], groups)
        histogram = Counter(str(validate_minor(c, rows, frames, eligible)) for c in report['classes'])
        e8 = span([256, 128, 64, 36, 20, 8, 2, 1])
        alpha = {408: F(1), 42: F(1, 2), 105: F(1)}
        check(all(frames[r] <= e8 for r in alpha), 'rank-eight alpha support')
        u = {}
        for r, c in alpha.items():
            add(u, rows[r], c)
        check(all(j in eligible and not w for j, w in u), 'rank-eight alpha pullback support')
        v = inverse_column(ops, {42: F(2)})
        check(set(v) <= eligible, 'rank-eight inverse support')
        check(sum(c * v.get(j, F(0)) for (j, w), c in u.items()) == 1, 'rank-eight pairing')
        receipts[variant] = {'endpoints': sum(groups.values()), 'support_classes': len(groups),
            'max_support': max(map(len, groups)), 'eligible_rank_at_most_7': len(low & eligible),
            'determinants': dict(sorted(histogram.items())), 'rank_eight_calibration': 'PASS',
            'negative_controls': controls(raw, variant, report, rows, frames, eligible, groups)}
    check(receipts['base'] == receipts['extra'], 'provider conclusions differ')
    print(json.dumps({'status': 'PASS_INDEPENDENT_TERMINAL_INFORMATION_BARRIER',
                      'no_new_kappa': True, 'providers': receipts}, sort_keys=True))


if __name__ == '__main__':
    main()
