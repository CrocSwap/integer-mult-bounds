#!/usr/bin/env python3
"""Exact finite corroboration of the dirty-scratch stability argument.

Apache-2.0; substantial OpenAI Codex assistance. Default operation is read-only.
The all-width theorem is the written proof, not this three-axis fixture.
"""
from pathlib import Path
from hashlib import sha256
import argparse
import json
import sys
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCES = (
    ('7eb4ef5251f7ba96c7e5d78c42fc98e66b7be4ba',
     'research/two-full-central-obstruction/grade/PROOF.md',
     '8fd775a9903eca0f53b186d7fb684d9f5f74afc9c105082b3d4981bd950fca33'),
    ('7eb4ef5251f7ba96c7e5d78c42fc98e66b7be4ba',
     'research/two-full-central-obstruction/inputs/native/clifford_exact.py',
     '2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962'),
)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load_sources():
    raw = []
    for commit, path, digest in SOURCES:
        data = (ROOT / path).read_bytes()
        need(sha256(data).hexdigest() == digest, 'source byte mismatch: ' + path)
        raw.append(data)
    ce = types.ModuleType('dirty_stability_exact')
    sys.modules[ce.__name__] = ce
    exec(compile(raw[1], SOURCES[1][1], 'exec'), ce.__dict__)
    return ce


def ga_add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def ga_mul(a, b):
    return (a[0]*b[0] - a[1]*b[1], a[0]*b[1] + a[1]*b[0])


class Algebra:
    """Sparse projective Clifford group algebra at central character f=1.

    Distinct signed tableaus remain distinct FORMAL basis elements, even if
    their one-column matrices are linearly dependent. Exact state vectors
    are used only to recover the scalar cocycle between identical tableaus.
    Thus a matrix-sum cancellation cannot masquerade as an algebra identity.
    """
    def __init__(self, ce, n):
        self.ce, self.n = ce, n
        self.refs, self.products, self.grades = {}, {}, {}
        self.one = self.word(ce.ident(n))

    def intern(self, op):
        key = op.tab
        if key not in self.refs:
            self.refs[key] = op
            self.grades[key] = self.ce.rank([x for x, z, p in op.tab[op.n:]])
            return key, (1, 0)
        av, ad = op.zero_state()
        bv, bd = self.refs[key].zero_state()
        for power, scalar in enumerate(((1, 0), (0, 1), (-1, 0), (0, -1))):
            if all((a[0]*(1 << bd), a[1]*(1 << bd)) ==
                   tuple(x*(1 << ad) for x in self.ce.mul_i(b, power))
                   for a, b in zip(av, bv)):
                return key, scalar
        raise ValueError('same tableau had an unexpected absolute phase')

    def word(self, op):
        key, phase = self.intern(op)
        return {key: phase}

    def add(self, *args):
        out = {}
        for arg in args:
            for key, value in arg.items():
                value = ga_add(out.get(key, (0, 0)), value)
                if value == (0, 0):
                    out.pop(key, None)
                else:
                    out[key] = value
        return out

    def scale(self, arg, scalar):
        if scalar == (0, 0):
            return {}
        return {key: ga_mul(value, scalar) for key, value in arg.items()}

    def mul(self, *args):
        out = self.one
        for arg in args:
            nxt = {}
            for left, lv in out.items():
                for right, rv in arg.items():
                    pair = (left, right)
                    if pair not in self.products:
                        # Op.then is chronological: right.then(left) = left*right.
                        self.products[pair] = self.intern(
                            self.refs[right].then(self.refs[left]))
                    key, phase = self.products[pair]
                    value = ga_mul(ga_mul(lv, rv), phase)
                    value = ga_add(nxt.get(key, (0, 0)), value)
                    if value == (0, 0):
                        nxt.pop(key, None)
                    else:
                        nxt[key] = value
            out = nxt
        return out

    def project(self, arg, lo, hi):
        return {key: value for key, value in arg.items()
                if lo <= self.grades[key] <= hi}

    def matrix(self, n):
        return [[{} for _ in range(n)] for _ in range(n)]

    def ident(self, n):
        out = self.matrix(n)
        for i in range(n):
            out[i][i] = self.one
        return out

    def mm(self, *args):
        out = args[0]
        for arg in args[1:]:
            n = len(out)
            out = [[self.add(*(self.mul(out[i][k], arg[k][j])
                              for k in range(n))) for j in range(n)]
                   for i in range(n)]
        return out

    def call(self, diagonal, dest, src, q):
        n = len(diagonal)
        shear, diag = self.ident(n), self.matrix(n)
        shear[dest][src] = q
        for i, entry in enumerate(diagonal):
            diag[i][i] = entry
        return self.mm(diag, shear)


def block_pair_fixtures(alg, aa, bb, q1, q2, monos):
    """Curated joint-owner cases; universal m is proved in PROOF.md.

    Dense noncommuting query blocks grant more than disjoint native pairs.
    The two stages have deliberately different destination/source partitions.
    """
    cases = []
    for pairs in (2, 3):
        main = 2*pairs
        cset, cbar = list(range(pairs)), list(range(pairs, main))
        uset, ubar = list(range(0, main, 2)), list(range(1, main, 2))
        av, bv = [aa[i % 2] for i in range(main)], [bb[i % 2] for i in range(main)]
        for scratch in (0, 1, 2):
            n = main + scratch
            d1, d2 = alg.matrix(n), alg.matrix(n)
            e1, e2 = alg.ident(n), alg.ident(n)
            for i in range(n):
                d1[i][i] = av[i] if i < main else alg.one
                d2[i][i] = bv[i] if i < main else alg.one
            for c in cset:
                for j in cbar:
                    e1[c][j] = alg.mul(monos[(c+j) % len(monos)], q1)
            for i in ubar:
                for r in uset:
                    e2[i][r] = alg.mul(q2, monos[(i+2*r) % len(monos)])
            t1, t2 = alg.mm(d1, e1), alg.mm(d2, e2)
            w = [[alg.add(monos[(i+2*j) % len(monos)],
                          alg.scale(monos[(2*i+j+1) % len(monos)], (2, 0)))
                  for j in range(n)] for i in range(n)]
            body = alg.mm(t2, w, t1)
            cross_checks = 0
            for a in range(main, n):
                for c in cset:
                    pure = alg.mul(w[a][c], av[c])
                    need(body[a][c] == pure and alg.project(pure, 1, 2) == pure,
                         'joint-owner untouched input cross identity')
                    cross_checks += 1
                for r in uset:
                    pure = alg.mul(bv[r], w[r][a])
                    need(body[r][a] == pure and alg.project(pure, 1, 2) == pure,
                         'joint-owner untouched output cross identity')
                    cross_checks += 1
                for j in cbar:
                    expected = alg.add(alg.mul(w[a][j], av[j]),
                        *(alg.mul(w[a][c], av[c], e1[c][j]) for c in cset))
                    need(body[a][j] == expected, 'joint-owner first dense query order')
                    cross_checks += 1
                for i in ubar:
                    expected = alg.mul(bv[i], alg.add(w[i][a],
                        *(alg.mul(e2[i][r], w[r][a]) for r in uset)))
                    need(body[i][a] == expected, 'joint-owner second dense query order')
                    cross_checks += 1
            wfirst = [[dict(entry) for entry in row] for row in w]
            for a in range(main, n):
                for c in cset:
                    wfirst[a][c] = {}
                for r in uset:
                    wfirst[r][a] = {}
            first = alg.mm(t2, wfirst, t1)
            for a in range(main, n):
                for j in cbar:
                    pure = alg.mul(wfirst[a][j], av[j])
                    need(first[a][j] == pure and alg.project(pure, 1, 2) == pure,
                         'joint-owner remaining input cross after forced zero')
                for i in ubar:
                    pure = alg.mul(bv[i], wfirst[i][a])
                    need(first[i][a] == pure and alg.project(pure, 1, 2) == pure,
                         'joint-owner remaining output cross after forced zero')
            # After both zero steps the scratch block is unchanged.
            wblock = [[dict(entry) for entry in row] for row in w]
            for a in range(main, n):
                for i in range(main):
                    wblock[a][i], wblock[i][a] = {}, {}
            block = alg.mm(t2, wblock, t1)
            need(all(not block[a][i] and not block[i][a]
                     for a in range(main, n) for i in range(main)),
                 'joint-owner block decoupling')
            need([row[main:] for row in block[main:]] ==
                 [row[main:] for row in wblock[main:]], 'joint-owner scratch block')
            for r in uset:
                for c in cset:
                    pure = alg.mul(bv[r], wblock[r][c], av[c])
                    need(block[r][c] == pure and alg.project(pure, 0, 2) == pure,
                         'joint-owner lower-grade untouched corner block')
            # Algebraic consequence of Pi(main)=0: first remove W[U,C],
            # then verify all remaining entries in these columns are pure.
            wcorner = [[dict(entry) for entry in row] for row in wblock]
            for r in uset:
                for c in cset:
                    wcorner[r][c] = {}
            corner = alg.mm(t2, wcorner, t1)
            for i in ubar:
                for c in cset:
                    pure = alg.mul(bv[i], wcorner[i][c], av[c])
                    need(corner[i][c] == pure and alg.project(pure, 0, 2) == pure,
                         'joint-owner remaining zero-column block after corner zero')
            for i in range(main):
                for c in cset:
                    wcorner[i][c] = {}
            zero = alg.mm(t2, wcorner, t1)
            need(all(not zero[i][c] for i in range(n) for c in cset),
                 'joint-owner whole untouched column block vanishes')
            cases.append(dict(main_pairs=pairs, main_owners=main,
                scratch_owners=scratch, first_destination_columns=cset,
                second_source_rows=uset, independently_partitioned_stages=True,
                dense_noncommuting_query_blocks=True,
                exact_cross_entry_formulas=cross_checks,
                untouched_corner_entries=pairs*pairs,
                resulting_zero_columns=pairs))
    return cases


def generate():
    source_manifest = json.loads((HERE / 'SOURCES.json').read_text())
    for row in source_manifest['files']:
        if row['usage'] == 'input':
            need(sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256'],
                 'declared live input byte mismatch: ' + row['path'])
    ce = load_sources()
    alg = Algebra(ce, 3)
    identity = ce.ident(3)
    ca, cb, cq = (ce.cgate(3, 1 << i) for i in (1, 2, 0))
    za = ce.diag(3, (2, 1, 0))       # CZ(q,a), actual absolute phase +1 at zero.
    zb = ce.diag(3, (4, 0, 1))       # CZ(q,b).
    swap = ce.perm(3, (2, 1, 4))     # Full-monomial central/fresh routing.
    sq = ce.diag(3, (1, 0, 0))
    xq = ce.xgate(3, 1)
    mon_ops = [identity, za, zb, swap, sq, xq]
    monos = [alg.word(op) for op in mon_ops]
    need(all(alg.project(m, 0, 0) == m for m in monos), 'monomial grades')

    # Keep signs, noncommutation, and role-dependent raw monomial corrections.
    aa = [alg.word(ca), alg.word(ca.then(xq))]
    bb = [alg.word(cb), alg.word(zb.then(cb))]
    q1 = alg.word(za.then(cq).then(za))
    q2 = alg.scale(alg.word(zb.then(cq.adjoint()).then(zb)), (-1, 0))
    need(alg.mul(q1, aa[0]) != alg.mul(aa[0], q1), 'noncommuting first query')
    need(alg.mul(q2, bb[0]) != alg.mul(bb[0], q2), 'noncommuting second query')
    need(aa[0] != aa[1] and bb[0] != bb[1], 'role-dependent factors')
    for entry in aa + bb:
        need(alg.project(entry, 1, 1) == entry, 'rank-one raw fixture factor')

    # Corroborate the grade-band bimodule identity on actual mixed words.
    samples = [alg.one, *aa, *bb, q1, q2,
               alg.mul(bb[0], q2, monos[1], aa[0], q1),
               alg.add(alg.one, aa[0], alg.mul(alg.word(cq), aa[0], bb[0]))]
    bimodule_cases = 0
    for left in monos:
        for right in monos:
            for sample in samples:
                for lo, hi in ((0, 0), (1, 2), (0, 2)):
                    need(alg.project(alg.mul(left, sample, right), lo, hi) ==
                         alg.mul(left, alg.project(sample, lo, hi), right),
                         'grade-band bimodule fixture')
                    bimodule_cases += 1

    orientation_rows = []
    scratch_cross_entries = 0
    for s in (1, 2, 3):
        n = 2 + s
        for u, v in ((0, 1), (1, 0)):
            for x, y in ((0, 1), (1, 0)):
                c, cp, r, rp = u, v, y, x
                t1 = alg.call(aa + [alg.one]*s, u, v, q1)
                t2 = alg.call(bb + [alg.one]*s, x, y, q2)
                w = [[alg.add(monos[(i+2*j) % len(monos)],
                              alg.scale(monos[(2*i+j+1) % len(monos)], (2, 0)))
                      for j in range(n)] for i in range(n)]
                m = alg.mm(t2, w, t1)
                for a in range(2, n):
                    first_col = alg.mul(w[a][c], aa[c])
                    first_row = alg.mul(bb[r], w[r][a])
                    need(m[a][c] == first_col and m[r][a] == first_row,
                         'untouched row/column exact actual-order identity')
                    for entry in (first_col, first_row):
                        need(bool(entry) and alg.project(entry, 1, 2) == entry,
                             'first cross entries retained by intermediate grades')
                    need(m[a][cp] == alg.add(alg.mul(w[a][cp], aa[cp]),
                         alg.mul(w[a][c], aa[c], q1)), 'other input query order')
                    need(m[rp][a] == alg.mul(bb[rp], alg.add(w[rp][a],
                         alg.mul(q2, w[r][a]))), 'other output query order')
                    scratch_cross_entries += 4
                # Apply only the first forced zeros, then check the second step.
                wfirst = [[dict(entry) for entry in row] for row in w]
                for a in range(2, n):
                    wfirst[a][c], wfirst[r][a] = {}, {}
                mfirst = alg.mm(t2, wfirst, t1)
                for a in range(2, n):
                    left = alg.mul(wfirst[a][cp], aa[cp])
                    right = alg.mul(bb[rp], wfirst[rp][a])
                    need(mfirst[a][cp] == left and mfirst[rp][a] == right,
                         'second cross identities after first zeros')
                    need(alg.project(left, 1, 2) == left and
                         alg.project(right, 1, 2) == right,
                         'second cross entries retained by intermediate grades')
                # Invertible Wm is a product of elementary B-valued shears.
                wm1, wm2 = alg.ident(2), alg.ident(2)
                wm1[0][1] = alg.add(monos[1], monos[3])
                wm2[1][0] = alg.add(monos[2], alg.scale(monos[4], (0, 1)))
                wm = alg.mm(wm1, wm2)
                ws = alg.ident(s)
                if s > 1:
                    ws[0][s-1] = alg.add(monos[1], monos[4])
                wblock = alg.matrix(n)
                for i in range(2):
                    for j in range(2):
                        wblock[i][j] = wm[i][j]
                for i in range(s):
                    for j in range(s):
                        wblock[i+2][j+2] = ws[i][j]
                mblock = alg.mm(t2, wblock, t1)
                need(all(not mblock[a][b] and not mblock[b][a]
                         for a in range(2, n) for b in range(2)), 'block decoupling')
                need([row[2:] for row in mblock[2:]] == ws, 'scratch block retained')
                need(any(alg.project(mblock[i][j], 0, 2)
                         for i in range(2) for j in range(2)),
                     'invertible main fixture cannot have zero lower-grade block')
                orientation_rows.append(dict(scratch=s, first=[u+1, v+1],
                    second=[x+1, y+1], untouched_column=c+1, untouched_row=r+1))

    # Discriminating boundary: a productively transformed scratch owner is
    # not an identity spectator. The cross entry can have maximal grade and
    # be invisible to rho although W[a,c] is nonzero.
    t1 = alg.call(aa + [alg.one], 0, 1, q1)
    transformed = alg.word(cq.then(cb))
    t2 = alg.call(bb + [transformed], 1, 0, q2)
    w = alg.ident(3)
    w[2][0] = alg.one
    m = alg.mm(t2, w, t1)
    need(bool(w[2][0]) and bool(m[2][0]), 'productive scratch boundary nonzero')
    need(alg.project(m[2][0], 3, 3) == m[2][0] and
         not alg.project(m[2][0], 1, 2), 'productive scratch breaks grade-eight gate')

    # Keep the actual 17-axis thresholds visible, without constructing a
    # 2^17 matrix or pretending a three-axis fixture proves the theorem.
    def grade(op):
        return ce.rank([x for x, z, p in op.tab[op.n:]])
    a17 = ce.fourier(17, range(1, 9))
    b17 = ce.fourier(17, range(9, 17))
    full17 = ce.fourier(17)
    need(grade(a17) == grade(b17) == 8 and grade(a17.then(b17)) == 16
         and grade(full17) == 17, 'actual 17-axis threshold fixture')

    joint_blocks = block_pair_fixtures(alg, aa, bb, q1, q2, monos)

    return dict(status='PASS_SCOPED_ALGEBRAIC_CORROBORATION',
        proof_sha256=sha256((HERE / 'PROOF.md').read_bytes()).hexdigest(),
        source_manifest_sha256=sha256((HERE / 'SOURCES.json').read_bytes()).hexdigest(),
        independent_checker_sha256=sha256((HERE / 'independent_symbolic.py').read_bytes()).hexdigest(),
        source_inputs=[dict(commit=c, path=p, sha256=h) for c, p, h in SOURCES],
        exact_algebra='sparse projective Clifford group algebra, central character f=1',
        matrix_sum_cancellations_used=False, finite_fixture_axes=3,
        intermediate_band=[1, 2], native_theorem_band=[1, 16],
        grade_bimodule_fixture_cases=bimodule_cases,
        all_orientation_scratch_cases=orientation_rows,
        joint_main_block_cases=joint_blocks,
        arbitrary_m_proved_in_written_argument=True,
        exact_cross_entry_formula_checks=scratch_cross_entries,
        noncommuting_queries=True, role_dependent_raw_factors=True,
        arbitrary_s_proved_in_written_argument=True,
        transformed_scratch_boundary=dict(cross_grade=3,
            intermediate_projection_zero=True, interstage_cross_nonzero=True,
            scope='this is a failed proof hypothesis, not a positive endpoint'),
        actual17_axis_grades=dict(first_raw=8, second_raw=8,
            raw_product=16, target=17),
        all_width_theorem_source='PROOF.md plus inherited PR4920 tensor-separation lemma',
        finite_fixture_is_universal_proof=False,
        new_native_endpoint=False, new_kappa=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='authoring: replace RESULT.json')
    args = parser.parse_args()
    result = generate()
    path = HERE / 'RESULT.json'
    if args.write:
        path.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    else:
        need(path.exists(), 'RESULT.json missing; author with --write')
        need(json.loads(path.read_text()) == result, 'RESULT.json differs from exact replay')
    print(json.dumps(dict(status=result['status'], read_only=not args.write,
        orientation_scratch_cases=len(result['all_orientation_scratch_cases']),
        joint_main_block_cases=len(result['joint_main_block_cases']),
        cross_entry_formula_checks=result['exact_cross_entry_formula_checks'],
        new_kappa=False), sort_keys=True))


if __name__ == '__main__':
    main()
