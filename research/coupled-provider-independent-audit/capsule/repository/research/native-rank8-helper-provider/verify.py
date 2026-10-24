#!/usr/bin/env python3
"""Source-bound coupled provider, exact rational rows and absolute phases.

No scratch registry, pending Git object, network access or third-party package.
The authenticated predecessor Clifford evaluator is the only imported module.
"""
from collections import Counter
from fractions import Fraction as F
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import importlib.util
import json
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
SOURCE_HASH = 'cfcd36b40326d7a5815e1db5313444379b3fb756b27d5201c561574c085cc0dd'
WITNESS_HASH = '24599011da06325e1012619b2b84a4dd3aceb90ab42d3caaf6414879e7d16591'
MODE = [224, 225, 227, 229, 240, 241, 256, 257]
PAID = Counter({1: 2193, 2: 412, 3: 510, 4: 127, 5: 40})


def need(condition, message):
    if not condition:
        raise ValueError(message)


def enc(row):
    return [[j, str(a)] for j, a in sorted(row.items()) if a]


def add(target, source, factor=1):
    for key, value in tuple(source.items()):
        value = target.get(key, F(0)) + factor * value
        if value:
            target[key] = value
        else:
            target.pop(key, None)


def addr(ref):
    need(ref[0] in ('L', 'C'), 'unknown field kind')
    return ref[1] + (632 if ref[0] == 'C' else 0)


def replay(program, c, owners, snapshots=()):
    """Every owner is an independent free-group column, including dirty C fields."""
    rows = [{(j, ()): F(1)} for j in range(owners)]
    charts = c['start'][:] + [None] * (owners - 632)
    paid, scalar = Counter(), Counter()
    zeros, dirt_clears, saved = [], [], {}
    for event, e in enumerate(program):
        kind = e[0]
        if kind == 'scalar':
            op, chart = e[1:]
            dst = addr(op[1])
            scalar[op[0]] += 1
            if op[0] == 'clear':
                need(dst >= 632, 'persistent CLEAR forbidden')
                dirt = {k: v for k, v in rows[dst].items() if k[0] >= 632}
                if dirt:
                    dirt_clears.append((dst, dirt))
                rows[dst], charts[dst] = {}, chart
            else:
                need(charts[dst] == chart, 'destination chart')
                if op[0] in ('copy', 'add'):
                    src = addr(op[2])
                    need(charts[src] == chart, 'source chart')
                    if op[0] == 'copy':
                        need(dst >= 632 and not rows[dst], 'COPY must fill owned zero')
                        rows[dst] = dict(rows[src])
                    else:
                        need(dst != src, 'ADD self alias')
                        add(rows[dst], rows[src], F(op[3], op[4]))
                else:
                    need(op[0] == 'scale', 'unknown scalar operation')
                    factor = F(op[2], op[3])
                    rows[dst] = {k: v * factor for k, v in rows[dst].items() if v * factor}
        elif kind == 'warp':
            _, ref, warp, old, new = e
            dst = addr(ref)
            need(charts[dst] == old, 'warp chart')
            symbol = (1 if warp > 0 else -1) * (abs(warp) + 1000000)
            after = {}
            for (owner, word), value in rows[dst].items():
                word = word[1:] if word and word[0] == -symbol else (symbol,) + word
                add(after, {(owner, word): value})
            rows[dst], charts[dst] = after, new
        elif kind in ('climb', 'center'):
            if kind == 'climb':
                _, _, dst, old, new, rank = e
                expected = len(c['frames'][new]) - len(c['frames'][old])
            else:
                _, dst, old, new, rank = e
                dst += 632
                expected = abs(len(c['frames'][new]) - len(c['frames'][old]))
            need(charts[dst] == old and rank == expected and rank > 0,
                 'paid child chart/rank')
            charts[dst] = new
            paid[rank] += 1
        elif kind == 'zero_retag':
            _, dst, old, new = e
            need(charts[dst] == old and not rows[dst], 'zero retag has nonzero input')
            zeros.append([event, dst, old, new])
            charts[dst] = new
        else:
            # Inherited source annotations / physical boundary bindings. The
            # predecessor's normalized-row convention treats these as no row
            # update; they remain byte-for-byte records in the emitted word.
            # New physical boundaries are checked separately below, with phase.
            need(kind in ('phase', 'adapter', 'residual_adapter'), 'unknown source record')
        for at, owner in snapshots:
            if event == at:
                saved[(at, owner)] = (charts[owner], dict(rows[owner]))
    return rows, charts, paid, scalar, zeros, dirt_clears, saved


def scalar(row):
    need(all(not word for _, word in row), 'endpoint has unreduced native word')
    return {j: a for (j, _), a in row.items()}


def rewrite(source, witness):
    centers = {r['event']: i for i, r in enumerate(witness)}
    late = {r['zero_event']: i for i, r in enumerate(witness)}
    caches = {r['cached_event']: i for i, r in enumerate(witness)}
    need(len(centers) == len(late) == len(caches) == 8, 'distinct eight sites')
    need(max(caches) < min(centers), 'caches must precede all replacements')
    word = []
    for event, op in enumerate(source['programs']['backward']):
        if event in centers:
            i = centers[event]
            frame = witness[i]['frame']
            need(op == ['center', 0, 0, frame, 8], 'center source binding')
            word += [['scalar', ['clear', ['C', 0]], frame],
                     ['scalar', ['copy', ['C', 0], ['C', i + 1]], frame]]
        elif event in late:
            r = witness[late[event]]
            need(op == ['climb', 'warp_retimed', r['zero_role'], r['frame'], 1, 1],
                 'late H1 source binding')
            word.append(['zero_retag', r['zero_role'], r['frame'], 1])
        else:
            word.append(op)
        if event in caches:
            i = caches[event]
            r = witness[i]
            word += [['scalar', ['clear', ['C', i + 1]], r['frame']],
                     ['scalar', ['copy', ['C', i + 1], ['L', r['cached_role']]], r['frame']]]
    return {'source_sha256': SOURCE_HASH, 'direction': 'backward', 'word': word}


def inverse(matrix):
    n = len(matrix)
    a, b, ops = [dict(r) for r in matrix], [{j: F(1)} for j in range(n)], []
    for j in range(n):
        k = next((i for i in range(j, n) if a[i].get(j)), None)
        need(k is not None, 'singular basis')
        if k != j:
            a[j], a[k], b[j], b[k] = a[k], a[j], b[k], b[j]
            ops.append(['swap', j, k])
        factor = 1 / a[j][j]
        if factor != 1:
            a[j] = {k: factor * v for k, v in a[j].items()}
            b[j] = {k: factor * v for k, v in b[j].items()}
            ops.append(['scale', j, str(factor)])
        for i in range(n):
            if i == j or not a[i].get(j):
                continue
            factor = -a[i][j]
            add(a[i], a[j], factor)
            add(b[i], b[j], factor)
            ops.append(['add', i, j, str(factor)])
    need(a == [{j: F(1)} for j in range(n)], 'basis reduction')
    return b, ops


def ordinary(ops, roles, reverse=False):
    out = []
    for e in reversed(ops) if reverse else ops:
        if e[0] == 'swap':
            a, b = roles[e[1]], roles[e[2]]
            out += [['add', a, b, '1'], ['add', b, a, '-1'],
                    ['add', a, b, '1'], ['scale', b, '-1']]
        elif e[0] == 'scale':
            v = F(e[2])
            out.append(['scale', roles[e[1]], str(1 / v if reverse else v)])
        else:
            v = F(e[3])
            out.append(['add', roles[e[1]], roles[e[2]], str(-v if reverse else v)])
    return out


def apply_ordinary(program, rows):
    rows = [dict(r) for r in rows]
    for e in program:
        if e[0] == 'add':
            need(e[1] != e[2], 'ordinary ADD alias')
            add(rows[e[1]], rows[e[2]], F(e[3]))
        else:
            need(e[0] == 'scale', 'ordinary operation')
            rows[e[1]] = {j: a * F(e[2]) for j, a in rows[e[1]].items() if a * F(e[2])}
    return rows


def authenticate():
    pins = json.loads((HERE / 'SOURCES.json').read_text())
    for r in pins['files']:
        if r['usage'] == 'input':
            need(sha256((ROOT / r['path']).read_bytes()).hexdigest() == r['sha256'],
                 'changed scientific input: ' + r['path'])
    raw = gzip.decompress((ROOT / 'research/native-center-free-code/SOURCE-WORD.json.gz').read_bytes())
    need(sha256(raw).hexdigest() == SOURCE_HASH, 'native payload')
    need(sha256((HERE / 'WITNESS.json').read_bytes()).hexdigest() == WITNESS_HASH,
         'Ali verbatim candidate provenance')
    cp = ROOT / 'research/coded-native-caller/clifford_exact.py'
    spec = importlib.util.spec_from_file_location('rank8_provider_clifford', cp)
    ce = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = ce
    spec.loader.exec_module(ce)
    return json.loads(raw), json.loads((HERE / 'WITNESS.json').read_text()), ce


def main(emit=False):
    started = time.monotonic()
    source, witness, ce = authenticate()
    c = source['canonical']
    normal = json.loads((ROOT / 'research/coded-native-caller/NORMALIZERS.json').read_text())
    M = normal['mode_columns']
    A = [[F(a) for a in r] for r in json.loads((ROOT / 'research/native-center-free-code/CODE.json').read_text())['A']]
    need(c['start'][112:224] == [0] * 112, 'main Y inputs have ground chart')
    need(len(M) == 8 and all(len(r) == 112 for r in M), 'M dimensions')
    need(all(sum(M[k][i] * M[l][i] for i in range(112)) == 56 * int(k == l)
             for k in range(8) for l in range(8)), 'M Gram')
    need(all(A[i][j] == F(i == j) - sum(F(M[k][i] * M[k][j], 4) for k in range(8))
             for i in range(112) for j in range(112)), 'A factorization')
    original = replay(source['programs']['backward'], c, 633,
                      [(r['cached_event'], r['cached_role']) for r in witness])
    oldrows, oldcharts, oldpaid, oldscalar = original[:4]
    expected = [{(j, ()): F(1)} for j in range(632)]
    for j in range(112):
        expected[j][(j + 112, ())] = F(-1)
    need(oldrows[:632] == expected and not oldrows[632], 'original 632-row endpoint')
    need(oldcharts[:632] == c['final'], 'original exit charts')

    centerfree = [['scalar', ['clear', ['C', e[1]]], e[3]] if e[0] == 'center' else e
                  for e in source['programs']['backward']]
    cf = replay(centerfree, c, 633)
    cfrows = [scalar(r) for r in cf[0]]
    need(cf[1][:632] == c['final'] and not cfrows[632], 'center-free charts/owned')
    P = [[-cfrows[j + 224].get(i + 112, F(0)) for i in range(112)] for j in range(408)]
    B = [[sum(P[j][i] * M[k][i] for i in range(112)) / 56 for j in range(408)] for k in range(8)]
    need(all(P[j][i] == sum(B[k][j] * M[k][i] for k in range(8))
             for j in range(408) for i in range(112)), 'full native coupling factorization')
    for j in range(632):
        row = {j: F(1)}
        if j < 112:
            for i in range(112):
                if A[i][j]:
                    row[i + 112] = -A[i][j]
        elif j >= 224:
            for i, a in enumerate(P[j - 224]):
                if a:
                    row[i + 112] = -a
        need(cfrows[j] == row, 'center-free complete scalar endpoint')

    delta = [{j - 224: F(a) for j, a in r['relation']} for r in witness]
    coupling = [[sum(a * B[k][j] for j, a in d.items()) for k in range(8)] for d in delta]
    need(all(sum(bool(a) for a in r) == 1 and set(r) <= {F(0), F(1), F(-1)}
             for r in coupling), 'candidate is not a signed retraction')
    perm = [next(k for k, a in enumerate(r) if a) for r in coupling]
    sign = [coupling[i][perm[i]] for i in range(8)]
    need(sorted(perm) == list(range(8)), 'retraction permutation')
    E = [{} for _ in range(8)]
    for i, k in enumerate(perm):
        E[k] = {j: sign[i] * a for j, a in delta[i].items()}
        row = {(j + 224, ()): F(witness[i]['zero_factor']) * a for j, a in delta[i].items()}
        for j in range(112):
            a = -F(witness[i]['zero_factor']) * sign[i] * M[k][j]
            if a:
                row[(j + 112, ())] = a
        need(original[6][(witness[i]['cached_event'], witness[i]['cached_role'])]
             == (witness[i]['frame'], row), 'fresh original cached row binding')
    need(all(sum(a * B[l][j] for j, a in E[k].items()) == int(k == l)
             for k in range(8) for l in range(8)), 'E B^T identity')
    active = sorted(set(j for r in B for j, a in enumerate(r) if a) | set(j for r in E for j in r))
    roles, index = [224 + j for j in active], {j: i for i, j in enumerate(active)}
    need(len(active) == 122 and all(c['start'][j] == 0 and c['final'][j] == 1 for j in roles),
         'basis requires 122 actual cold H9 owners')
    J = [j - 224 for j in MODE]
    L = [{} for _ in active]
    for k, j in enumerate(J):
        for r in active:
            if B[k][r]:
                L[index[r]][index[j]] = B[k][r]
    for j in active:
        if j in J:
            continue
        for r in active:
            a = F(r == j) - sum(B[k][r] * E[k].get(j, F(0)) for k in range(8))
            if a:
                L[index[r]][index[j]] = a
    Li, ops = inverse(L)
    for left, right in ((L, Li), (Li, L)):
        for i, row in enumerate(left):
            product = {}
            for j, a in row.items():
                add(product, right[j], a)
            need(product == {i: F(1)}, 'two-sided basis inverse')
    for k, row in enumerate(E):
        product = {}
        for j, a in row.items():
            add(product, L[index[j]], a)
        need(product == {index[J[k]]: F(1)}, 'E L mode selection')
    need(all(sum(a * B[k][active[j]] for j, a in row.items()) == int(i == index[J[k]])
             for i, row in enumerate(Li) for k in range(8)), 'Li B mode embedding')
    need(all(a.denominator & (a.denominator - 1) == 0
             for matrix in (L, Li) for row in matrix for a in row.values()), 'dyadic basis')
    entrance, exitword = ordinary(ops, roles, True), ordinary(ops, roles)
    identity = [{j: F(1)} for j in range(632)]
    entered = apply_ordinary(entrance, identity)
    def check_basis(rows):
        for i, j in enumerate(roles):
            need(rows[j] == {roles[k]: a for k, a in L[i].items()}, 'literal L program')
    check_basis(entered)
    need(apply_ordinary(exitword, entered) == identity, 'literal Li program')
    need(Counter(e[0] for e in entrance) == Counter(add=822, scale=12), 'basis program bill')
    need(Counter(e[0] for e in exitword) == Counter(add=822, scale=12), 'inverse program bill')

    changed = rewrite(source, witness)
    frozen_word = json.loads(gzip.decompress((HERE / 'WORD.json.gz').read_bytes()))
    need(changed == frozen_word, 'committed exact word differs from source rewrite')
    result = replay(changed['word'], c, 641)
    rawrows, charts, paid, scalars, zeros, dirt = result[:6]
    need(charts[:632] == c['final'] and not rawrows[632], 'changed persistent charts/C0')
    need(paid == PAID and oldpaid == paid + Counter({1: 8, 8: 8}), 'paid children')
    need(scalars == oldscalar + Counter(clear=16, copy=16), 'source ordinary delta')
    need(len(zeros) == 8, 'eight exact zero retags')
    need(len(dirt) == 9 and {j for j, _ in dirt} == set(range(632, 641))
         and all(d == {(j, ()): F(1)} for j, d in dirt), 'all arbitrary owned dirt cleared')
    need(not any(j >= 632 for row in rawrows for j, _ in row), 'owned dirt leaked')
    need(sum(rawrows[j] != oldrows[j] for j in range(632)) == 218, 'changed endpoint count')
    endpoint = []
    for row in rawrows:
        out = {}
        for j, a in scalar(row).items():
            add(out, entered[j], a)
        endpoint.append(out)
    endpoint = apply_ordinary(exitword, endpoint)
    for j in range(632):
        expected = {} if j in MODE else {j: F(1)}
        if j < 112:
            expected[j + 112] = F(-1)
            for k in range(8):
                if M[k][j]:
                    expected[MODE[k]] = F(M[k][j], 4)
        need(endpoint[j] == expected, 'composed all-owner endpoint at ' + str(j))
    def check_cache(i, row):
        r, k = witness[i], perm[i]
        factor = F(r['zero_factor']) * sign[i]
        expected = {MODE[k]: factor}
        for j in range(112):
            if M[k][j]:
                expected[j + 112] = -factor * M[k][j]
        need(row == expected and charts[633 + i] == r['frame'], 'composed retained cache')
    for i in range(8):
        check_cache(i, endpoint[633 + i])
    first_cache = dict(endpoint[633])

    def conjugate(op):
        circuit = []
        for e in op.circuit:
            if e[0] == 'D':
                circuit.append(('D', e[1], tuple((-x) % 4 for x in e[2])))
            elif e[0] == 'C':
                circuit.append(('C', e[1], -e[2]))
            elif e[0] == 'phase':
                circuit.append(('phase', (-e[1]) % 4))
            else:
                circuit.append(e)
        return ce.Op(9, tuple((x, z, -p % 4) for x, z, p in op.tab), circuit)

    @lru_cache(None)
    def frame(j, back=False):
        op = ce.canonical_frame(9, c['frames'][j])
        return conjugate(op) if back else op

    def literal(word):
        op = ce.ident(9)
        for e in word:
            if e[0] == 'P':
                part = ce.perm(9, tuple(e[1]))
            elif e[0] == 'D':
                part = ce.diag(9, tuple(e[1]), tuple(e[2]))
            elif e[0] == 'X':
                part = ce.xgate(9, e[1])
            elif e[0] == 'phase':
                part = ce.Op(9, ce.identity(9), [('phase', e[1])])
            else:
                raise ValueError('boundary contains a Gaussian gate')
            op = op.then(part)
        return op

    def equal(a, b):
        return a.tab == b.tab and a.zero_state() == b.zero_state()

    def rank(op):
        return ce.rank([x for x, _, _ in op.tab[9:]])

    def receipt(op):
        vec, den = op.zero_state()
        j = next(j for j, a in enumerate(vec) if a != (0, 0))
        return {'literal_word': op.circuit, 'signed_tableau': op.tab,
                'zero_column_anchor': {'index': j, 'gaussian_numerator': vec[j],
                                       'denominator_power2': den}}

    def compile_monomial(op):
        need(rank(op) == 0, 'nonmonomial boundary map')
        compiled, _ = ce.monomial(op)
        need(equal(compiled, op) and equal(literal(compiled.circuit), op),
             'literal phase-correct monomial compilation')
        return compiled

    R, D = frame(1), ce.fourier(9, range(1, 9))
    Km, N = [None] * 8, [None] * 8
    records = [None] * 8
    for i, r in enumerate(witness):
        k = perm[i]
        candidates = [q for q in range(1, 512)
                      if all(ce.parity(q & v) == 0 for v in c['frames'][r['frame']])]
        need(len(candidates) == 1, 'rank-eight missing line')
        q = candidates[0]
        need(q.bit_count() % 2 == 1 and q != 511, 'odd noncharacteristic line')
        if not q & 1:
            transvections = [1 ^ q]
        else:
            j = next(j for j in range(1, 9) if not q >> j & 1)
            transvections = [1 ^ (1 << j), (1 << j) ^ q]
        cols = []
        for j in range(9):
            x = 1 << j
            for v in transvections:
                x ^= v if ce.parity(x & v) else 0
            cols.append(x)
        G = ce.transpose(cols, 9)
        z = sum((((row.bit_count() - 1) // 2) & 1) << j for j, row in enumerate(G))
        K = ce.perm(9, G).then(ce.diag(9, (0,) * 9, tuple(2 * ((z >> j) & 1) for j in range(9))))
        need(equal(K.then(R), R.then(K)), 'mode K/R absolute phase')
        need(all((ce.mv(ce.transpose(G, 9), x).bit_count() - x.bit_count()
                  - 2 * ce.parity(z & x)) % 4 == 0 for x in range(512)), 'K weight congruence')
        F8 = frame(r['frame'], True)
        need(rank(F8) == 8, 'actual cache rank')
        Km[k] = compile_monomial(K)
        N[k] = compile_monomial(K.then(F8).adjoint().then(D))
        records[k] = {'mode': k, 'owner': MODE[k], 'cache_slot': 633 + i,
                      'witness_row': i, 'frame': r['frame'], 'missing_line': q,
                      'cache_scalar': str(1 / (2 * F(r['zero_factor']) * sign[i])),
                      'input_K': receipt(Km[k]), 'output_N': receipt(N[k])}
    Kp = [literal(r['K_word']) for r in normal['ports']]
    checks = Counter()
    for j, port in enumerate(normal['ports']):
        need(port['port'] == j and rank(Kp[j]) == 0 and equal(Kp[j].then(R), R.then(Kp[j])),
             'port K binding and R commutation')
        wrappers = port['compiled_wrappers']
        BX, BY, OX, OY = [literal(wrappers[key]['word']) for key in
                          ('backward_input_X', 'backward_input_Y', 'backward_output_X', 'backward_output_Y')]
        birth, final, finalY = frame(c['start'][j], True), frame(c['final'][j], True), frame(c['final'][112 + j], True)
        need(equal(BX.then(birth.adjoint()).then(final).then(OX), D), 'X diagonal physical block')
        need(equal(BY.then(finalY).then(OY), D), 'Y diagonal physical block')
        need(equal(BY.then(final).then(OX), R), 'main shear physical block')
        checks['main_diagonal_and_shear'] += 3
        for k in range(8):
            if not M[k][j]:
                continue
            need(equal(Km[k].then(final).then(OX), Km[k].then(Kp[j].adjoint()).then(R)),
                 'helper-to-main physical coupling')
            F8 = frame(records[k]['frame'], True)
            need(equal(BY.then(F8).then(N[k]), Kp[j].then(Km[k].adjoint()).then(D)),
                 'main-to-helper physical coupling')
            checks['two_coupling_directions'] += 2
    for k in range(8):
        need(equal(Km[k].then(frame(records[k]['frame'], True)).then(N[k]), D),
             'helper diagonal physical block')
        checks['helper_diagonal'] += 1
    need(dict(checks) == {'main_diagonal_and_shear': 336, 'two_coupling_directions': 896,
                          'helper_diagonal': 8}, '1,240 physical bindings')
    autonomous = Counter(len(c['frames'][c['final'][j]]) - len(c['frames'][c['start'][j]])
                         for j in range(224, 632) if j not in MODE)
    need(autonomous == Counter({4: 28, 7: 7, 8: 47, 9: 318}), '400 retained native helper jobs')
    # Physical normalization precedes a complete-field SWAP, including chart tags.
    for r in records:
        owner, cache = r['owner'], r['cache_slot']
        need(not endpoint[owner], 'SWAP destination must be identically zero')
        endpoint[owner], endpoint[cache] = endpoint[cache], endpoint[owner]
    need(all(not endpoint[j] for j in range(632, 641)), 'all owned outputs clean')

    # Failure controls invoke the same predicates as the construction.
    controls = []
    bad_c = dict(c)
    bad_c['start'] = c['start'][:]
    bad_c['start'][0] = 0
    try:
        replay([['zero_retag', 0, 0, 1]], bad_c, 641)
    except ValueError as e:
        need(str(e) == 'zero retag has nonzero input', 'wrong rejection')
        controls.append('nonzero zero-retag rejected')
    need(len(controls) == 1, 'zero-retag control accepted')
    corrupted = [e[:] for e in entrance]
    mutated = next(e for e in corrupted if e[0] == 'add')
    mutated[3] = str(F(mutated[3]) + 1)
    try:
        check_basis(apply_ordinary(corrupted, identity))
    except ValueError as e:
        need(str(e) == 'literal L program', 'wrong basis rejection')
        controls.append('one altered basis ADD coefficient rejected')
    need(len(controls) == 2, 'basis coefficient mutation accepted')
    badN = ce.Op(9, N[0].tab, N[0].circuit + [('phase', 1)])
    need(badN.tab == N[0].tab and not equal(Km[0].then(frame(records[0]['frame'], True)).then(badN), D),
         'phase-only error escaped')
    controls.append('same-tableau phase-only cache error rejected')
    wrong = dict(first_cache)
    add(wrong, {MODE[perm[0]]: F(1)})
    try:
        check_cache(0, wrong)
    except ValueError as e:
        need(str(e) == 'composed retained cache', 'wrong cache rejection')
        controls.append('one altered saved-cache coefficient rejected')
    need(len(controls) == 4, 'saved-cache coefficient mutation accepted')

    # An explicit, conservative local error-amplification bound for this finite
    # schedule. Gaussian and monomial field maps have Euclidean norm one.
    def log2_bound(a):
        a, exponent = max(F(1), a), 0
        while a > 1:
            a /= 2
            exponent += 1
        return exponent
    amplification = 0
    for e in changed['word']:
        if e[0] == 'scalar':
            op = e[1]
            if op[0] == 'add':
                amplification += log2_bound(1 + abs(F(op[3], op[4])))
            elif op[0] == 'scale':
                amplification += log2_bound(abs(F(op[2], op[3])))
    for e in entrance + exitword:
        amplification += log2_bound(1 + abs(F(e[3]))) if e[0] == 'add' else log2_bound(abs(F(e[2])))
    amplification += 8 * log2_bound(F(2))
    amplification += sum(log2_bound(abs(F(r['cache_scalar']))) for r in records)

    artifact = {
        'schema_version': 1, 'source_payload_sha256': SOURCE_HASH,
        'candidate_witness_sha256': WITNESS_HASH,
        'word_payload_sha256': sha256(gzip.decompress((HERE / 'WORD.json.gz').read_bytes())).hexdigest(),
        'basis_roles': roles, 'mode_owners': MODE,
        'candidate_mode_permutation': perm, 'candidate_mode_signs': list(map(str, sign)),
        'canonical_retraction_E': [enc(row) for row in E],
        'input_basis_program': entrance, 'output_basis_program': exitword,
        'mode_boundaries': records,
        'ordered_schedule': [
            'Main input wrappers: NORMALIZERS.ports[j].compiled_wrappers.backward_input_X/Y.',
            'On each mode owner apply input_K and scalar 2; run input_basis_program.',
            'Run every instruction of WORD.json.gz; C0..C8 initially arbitrary.',
            'Run output_basis_program on the 122 persistent common-chart helpers.',
            'For each mode apply cache_scalar and output_N to its owned cache; SWAP the whole field and chart with its zero original owner; CLEAR the owned zero.',
            'Main output wrappers: NORMALIZERS.ports[j].compiled_wrappers.backward_output_X/Y.'
        ],
        'paid': dict(sorted(paid.items())), 'autonomous_native_helpers': dict(sorted(autonomous.items())),
        'owned_fields': {'count': 9, 'initial_values': 'arbitrary', 'final_values': 'zero', 'productive_credit': 0},
        'added_ordinary_work_vs_original_raw_source': {
            'ADD': 1644, 'SCALE': 40, 'COPY': 16, 'CLEAR': 24, 'whole_field_SWAP': 8,
            'monomial_field_maps': 464,
            'monomial_breakdown': {'fused_inherited_main_standardizers': 448, 'mode_inputs': 8, 'cache_outputs': 8}},
        'local_error_amplification_power2_bound': amplification,
        'source_original_scalar_counts': dict(sorted(oldscalar.items())),
        'source_changed_scalar_counts': dict(sorted(scalars.items())),
        'physical_phase_bindings': dict(checks), 'exact_zero_retags': zeros,
        'formula': {'X': 'D x - R y + R W h', 'Y': 'D y', 'H': 'D (h - Z y)',
                    'W': 'diag(K_port^-1) M diag(K_mode)/2',
                    'Z': 'diag(K_mode^-1) M^T diag(K_port)/2'},
        'failure_controls': controls,
        'scope': 'Changed coupled backward provider. No autonomous credit for eight coupled outputs; no completed caller, inverse/transpose implementation, new kappa or selected-result change.'
    }
    artifact = json.loads(json.dumps(artifact))
    path = HERE / 'PROVIDER.json'
    if emit:
        path.write_text(json.dumps(artifact, indent=2) + '\n')
    else:
        need(json.loads(path.read_text()) == artifact, 'committed boundary recipe differs from replay')
    print('PASS_NATIVE_RANK8_HELPER_PROVIDER ' + json.dumps({
        'original_inputs': 632, 'arbitrary_owned_inputs': 9, 'owned_outputs_zero': 9,
        'autonomous_helpers': 400, 'coupled_helpers': 8, 'paid': dict(sorted(paid.items())),
        'phase_bindings': sum(checks.values()), 'seconds': round(time.monotonic() - started, 3)}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emit', action='store_true', help='regenerate the package-local boundary recipe')
    main(parser.parse_args().emit)
