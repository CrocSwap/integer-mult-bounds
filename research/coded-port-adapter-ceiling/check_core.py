"""Exact source interface/grade/moment checks; no producer or caller search.
Apache-2.0; credit in ATTRIBUTION.md. Substantial OpenAI Codex assistance.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256, sha1
from pathlib import Path
import gzip
import json
import sys
import types


def need(test, why):
    if not test:
        raise ValueError(why)


def authenticate_sources(here):
    origins = json.loads((here / 'ORIGINS.json').read_text())
    raw = {}
    for row in origins['files']:
        path = here / row['path']
        need(not path.is_symlink(), 'Source is not a symlink')
        value = path.read_bytes()
        need(sha256(value).hexdigest() == row['sha256'], 'Source SHA256 ' + row['path'])
        blob = sha1(b'blob ' + str(len(value)).encode() + b'\0' + value).hexdigest()
        need(blob == row['git_blob'], 'Source Git blob ' + row['path'])
        raw[path.name] = value
    return origins, raw


def matrix_code(code):
    need(len(code) == 112 and all(len(r) == 112 for r in code), 'Code dimensions')
    A = [[Q(x) for x in row] for row in code]
    need(all(A[i][i] == 0 for i in range(112)), 'Code zero diagonal')
    need(all(A[i][j] == A[j][i] for i in range(112) for j in range(112)), 'Code symmetry')
    need(all(x in (Q(0), Q(1, 2), Q(-1, 2)) for row in A for x in row), 'Code dyadic alphabet')
    M = [[int(2*x) for x in row] for row in A]
    for i in range(112):
        for j in range(112):
            need(sum(M[i][k]*M[k][j] for k in range(112)) + 24*M[i][j]
                 == 52*int(i == j), 'Code inverse polynomial A^2+12A=13I')
    return A


def check_inverse(A, inverse):
    # Exact entrywise rational identity; no numerical determinant or eigenvalue.
    for i in range(112):
        for j in range(112):
            need(sum(A[i][k]*inverse[k][j] for k in range(112)) == int(i == j),
                 'Explicit code matrix inverse')


def grade(op):
    # Independent binary row reduction of the physical Z->X tableau block.
    pivots = {}
    for x, z, phase in op.tab[op.n:]:
        while x:
            bit = x.bit_length()-1
            if bit not in pivots:
                pivots[bit] = x
                break
            x ^= pivots[bit]
    return len(pivots)


def supported_grades(A, U):
    result = Counter()
    for i in range(112):
        for j in range(112):
            if A[i][j]:
                # then is chronological: this matrix is U_i U_j^*.
                r = grade(U[j].adjoint().then(U[i]))
                need(r == 2, 'Supported entrance transport has grade two')
                result[r] += 1
    need(result == Counter({2: 5824}), 'Complete supported-pair census')
    return result


def reject(name, action, message):
    try:
        action()
    except ValueError as error:
        need(message in str(error), 'Mutation rejected at intended gate: ' + name)
        return name
    raise ValueError('Mutation not rejected: ' + name)


def outward(value, digits=30):
    scale = 10**digits
    def dec(n):
        s = str(abs(n)).rjust(digits+1, '0')
        return ('-' if n < 0 else '') + s[:-digits] + '.' + s[-digits:]
    lo = (value[0]*scale).__floor__()
    hi = -((-value[1]*scale).__floor__())
    return {'lower': dec(lo), 'upper': dec(hi),
            'exact_rational': [str(value[0]), str(value[1])]}


def price(moment, T, P, C):
    a, b = moment(dict(T), 1-C), moment(dict(P), 1-C)
    return a[0]-b[1], a[1]-b[0]


def run(here):
    origins, raw = authenticate_sources(here)
    source = json.loads(gzip.decompress(raw['ACTUAL-WORD.json.gz']))
    coded = json.loads(gzip.decompress(raw['CODED-WORDS.json.gz']))
    c, cc = source['canonical'], coded['canonical']
    need(sha256(raw['ACTUAL-WORD.json.gz']).hexdigest()
         == '7679daa4ec6a40f56fc7f0202379a6f454310e94945aba4f48beaaaafb838d05', 'Actual compressed source')
    need(sha256(gzip.decompress(raw['ACTUAL-WORD.json.gz'])).hexdigest()
         == 'cfcd36b40326d7a5815e1db5313444379b3fb756b27d5201c561574c085cc0dd', 'Same decompressed source')
    for key, value in c.items():
        if key != 'local_profile':
            need(cc[key] == value, 'Original native frames/maps/owners retained')
    frames = c['frames']
    need(len({c['start'][i] for i in range(112)}) == 112, '112 distinct X entrance charts')
    need(all(len(frames[c['start'][i]]) == 1 and c['final'][i] == 1
             for i in range(112)), 'Rank-one X entrances / common full exit')
    need(all(c['start'][i] == 0 and len(frames[c['final'][i]]) == 8
             for i in range(112, 224)), 'Ground Y entrances / rank-eight exits')
    H = Counter(len(frames[c['final'][i]]) - len(frames[c['start'][i]])
                for i in range(224, 632))
    need(H == Counter({4: 28, 7: 7, 8: 47, 9: 326}), 'Every independent helper once')
    P = Counter({1: 2201, 2: 412, 3: 510, 4: 127, 5: 40})
    invoice = {}
    for direction in ('forward', 'backward'):
        old, new = source['programs'][direction], coded['programs'][direction]
        oldP = Counter(e[5] for e in old if e[0] == 'climb')
        oldP.update(e[4] for e in old if e[0] == 'center')
        newP = Counter(e[5] for e in new if e[0] == 'climb')
        newP.update(e[4] for e in new if e[0] == 'center')
        need(newP == P and oldP == P+Counter({8: 8}), 'Literal removed eight H8')
        need(len(new)-len(old) == 6596, 'Literal fixed precompensation length')
        allowance = 0
        for e in new[:6596]:
            need(e[0] == 'scalar' and e[1][0] == 'add' and e[2] == 0,
                 'Ground dyadic ADD precompensation')
            a, b = e[1][1:3]
            need(a[0] == b[0] == 'L' and c['start'][a[1]] == c['start'][b[1]] == 0,
                 'Actual source and target common ground chart')
            q = Q(e[1][3], e[1][4])
            need(abs(q.numerator) <= 4 and q.denominator <= 4, 'Dyadic coefficient bounds')
            allowance += (3 + abs(q.numerator).bit_length()-1
                          + abs(q.numerator).bit_count() + q.denominator.bit_length()-1)
        need(allowance == 32652, 'Finite precompensation scalar allowance')
        invoice[direction] = {'paid': dict(newP), 'events': len(new),
                              'additional_ADDs': 6596, 'precomp_scalar_allowance': allowance}
    ce = types.ModuleType('coded_port_pinned_clifford')
    sys.modules[ce.__name__] = ce
    exec(compile(raw['clifford_exact.py'], 'source/clifford_exact.py', 'exec'), ce.__dict__)
    U = [ce.canonical_frame(9, frames[c['start'][i]]) for i in range(112)]
    A = matrix_code(json.loads(raw['CODE.json'])['A'])
    inverse = [[(A[i][j]+12*int(i == j))/13 for j in range(112)] for i in range(112)]
    check_inverse(A, inverse)
    grades = supported_grades(A, U)
    controls = []
    badA = [row[:] for row in A]
    badA[0][0] = Q(1, 2)
    controls.append(reject('nonzero_code_diagonal', lambda: matrix_code(badA), 'Code zero diagonal'))
    bad_inverse = [row[:] for row in inverse]
    j = next(j for j in range(112) if A[0][j])
    bad_inverse[j][0] += Q(1, 13)
    controls.append(reject('wrong_code_inverse', lambda: check_inverse(A, bad_inverse), 'Explicit code matrix inverse'))
    badU = U[:]
    badU[j] = U[0]
    controls.append(reject('supported_transport_grade_zero', lambda: supported_grades(A, badU), 'Supported entrance transport has grade two'))
    bad_poly = [row[:] for row in A]
    bad_poly[0][j] *= -1
    bad_poly[j][0] *= -1
    controls.append(reject('wrong_code_polynomial', lambda: matrix_code(bad_poly), 'Code inverse polynomial'))
    env = {'__name__': 'coded_port_pinned_intervals', '__file__': str(here/'source/intervals.py')}
    exec(compile(raw['intervals.py'], 'source/intervals.py', 'exec'), env)
    paid = Counter({r: 2*n for r, n in P.items()})
    target = Counter({r: 2*n for r, n in H.items()})
    target[17] = 224
    models = {}
    for label, extra in [('unrealized_two_bank', {}), ('after112H1', {1: 112}),
                         ('after224H1', {1: 224}), ('after112H2', {2: 112})]:
        cost = paid+Counter(extra)
        coefficient = {r: target.get(r, 0)-cost.get(r, 0) for r in target.keys() | cost.keys()
                       if target.get(r, 0) != cost.get(r, 0)}
        need(all((n < 0 and r <= 5) or (n > 0 and r >= 7)
                 for r, n in coefficient.items()), 'Moment sign separation at five')
        values = {}
        for cs in ('.0030217758', '.0034'):
            value = price(env['moment'], target, cost, Q(cs))
            need(value[1] < 0 if label in ('after224H1', 'after112H2') else value[0] > 0,
                 'Optimistic tariff model sign ' + label)
            values[cs] = outward(value)
        models[label] = {'target': dict(target), 'paid': dict(cost), 'values': values,
                         'interval_reason': 'M(t)/5^t strictly increasing; sign at proper endpoint',
                         'endpoint_constructed': False}
    future = Counter(target)
    future[17] += 112
    future[9] -= 224
    future16 = Counter(future)
    future16[17] -= 112
    future16[16] += 112
    future_models = {}
    for label, T in [('unproved_three_H17_banks', future), ('third_bank_H16_template_grant', future16)]:
        values = {cs: outward(price(env['moment'], T, paid, Q(cs))) for cs in ('.0030217758', '.0034')}
        need(all((T.get(r, 0)-paid.get(r, 0) < 0 and r <= 5) or (T.get(r, 0)-paid.get(r, 0) > 0 and r >= 7) for r in T.keys() | paid.keys() if T.get(r, 0) != paid.get(r, 0)), 'Future offer sign separation')
        for cs in ('.0030217758', '.0034'):
            v = price(env['moment'], T, paid, Q(cs))
            need(v[0] > 0 if label == 'unproved_three_H17_banks' else v[1] < 0, 'Future offer tariff sign')
        future_models[label] = {'target': dict(T), 'owners': sum(T.values()), 'paid': dict(paid),
                                'values': values, 'coded_endpoint_constructed': False}
    return {'status': 'PASS_CODED_PORT_ADAPTER_CEILING', 'producer_head': origins['producer_head'],
            'source_compressed_sha256': sha256(raw['ACTUAL-WORD.json.gz']).hexdigest(),
            'source_payload_sha256': sha256(gzip.decompress(raw['ACTUAL-WORD.json.gz'])).hexdigest(),
            'native_invoice': invoice, 'helper_profile': dict(H), 'A_dimension': 112,
            'A_entries': dict(Counter(str(x) for row in A for x in row)),
            'supported_pair_grades': dict(grades), 'semantic_controls': controls,
            'forward_adapter': 'K=U A^-1 U*; scalar exit A on common-full X',
            'raw_dual_adapter': 'barU A^T barU*; scalar exit A^(-T) on conjugate-full X',
            'one_parallel_bank_grade2_channels_at_least': 112,
            'allwidth_claim_basis': 'Written phase-quotient/projective tensor-separation proof',
            'tariff_models': models, 'future_tariff_models': future_models,
            'producer_632_endpoint_replayed': False, 'consumer_constructed': False,
            'compiler_or_outer_replayed': False, 'new_kappa': None}
