#!/usr/bin/env python3
"""Finite inputs for extending PR1212's rank-8 rigidity theorem to the 896 admissible (type (1,...,1)) P104 units.

Independent implementation (own E8 model, classes, witnesses and propagation); nothing is imported from
PR1212.  Zero exclusion on this unit (PR1212 Lemma 8) and the orbit transport are cited.  With --pr1212-dir
they are also replayed by running PR1212's own verifier from a checkout whose files match the pinned git blobs.

    python3 -I -B research/complex-rank8-rigidity-p104-admissible/verify.py [--pr1212-dir DIR] [--out FILE]

Standard library only.  Exact integer / rational arithmetic throughout.
"""
import argparse
import hashlib
import itertools
import json
import os
import subprocess
import sys
from fractions import Fraction

FAILS = []
NCHECK = 0


def check(tag, cond, info=''):
    global NCHECK
    NCHECK += 1
    print(('PASS ' if cond else 'FAIL ') + tag + (' | ' + info if info else ''))
    if not cond:
        FAILS.append(tag)
    return bool(cond)


# ------------------------------------------------------------------ E8 model (doubled coordinates)
def lines_e8():
    """One representative per root line, roots in doubled coordinates (norm 8), canonical sign:
    the first nonzero coordinate is positive."""
    out = set()
    for i, j in itertools.combinations(range(8), 2):
        for sj in (2, -2):
            v = [0] * 8
            v[i], v[j] = 2, sj
            out.add(tuple(v))
    for s in itertools.product((1, -1), repeat=7):
        v = (1,) + s
        if v.count(-1) % 2 == 0:
            out.add(v)
    return sorted(out)


LINES = lines_e8()
IDX = {v: n for n, v in enumerate(LINES)}
NL = len(LINES)


def canon(v):
    v = tuple(v)
    first = next(a for a in v if a)
    return v if first > 0 else tuple(-a for a in v)


def ip(x, y):
    d = sum(a * b for a, b in zip(x, y))
    assert d % 4 == 0
    return d // 4


G = [[ip(LINES[i], LINES[j]) for j in range(NL)] for i in range(NL)]


def lid(v):
    return IDX[canon(v)]


def frame_lines(vs):
    return [lid(v) for v in vs]


# PR1212's FRAME0 and its admissible representative unit P112 minus DEAD with pivot PIVOT, as root vectors
# (from PR1212 head 57099cb5 verify.py `extension_units()`, unit 'P104-11111111'; --pr1212-dir rechecks the
# correspondence through PR1212's own line numbering).
FRAME0 = [(2, 2, 0, 0, 0, 0, 0, 0), (2, -2, 0, 0, 0, 0, 0, 0), (0, 0, 2, 2, 0, 0, 0, 0), (0, 0, 2, -2, 0, 0, 0, 0),
          (0, 0, 0, 0, 2, 2, 0, 0), (0, 0, 0, 0, 2, -2, 0, 0), (0, 0, 0, 0, 0, 0, 2, 2), (0, 0, 0, 0, 0, 0, 2, -2)]
DEAD = [(2, 0, 2, 0, 0, 0, 0, 0), (0, 2, 0, 0, 2, 0, 0, 0), (0, 0, 0, 2, 0, 0, 2, 0), (0, 0, 0, 0, 0, 2, 0, 2),
        (1, 1, -1, 1, -1, 1, -1, -1), (1, 1, -1, -1, -1, -1, 1, 1), (1, -1, -1, 1, 1, -1, -1, 1), (1, -1, -1, -1, 1, 1, 1, -1)]
PIVOT = [(2, 0, 0, 0, 0, 0, 0, 2), (2, 0, 0, 0, 0, 0, 0, -2), (0, 2, 0, 0, 0, 0, 2, 0), (0, 2, 0, 0, 0, 0, -2, 0),
         (0, 0, 2, 0, 0, 2, 0, 0), (0, 0, 2, 0, 0, -2, 0, 0), (0, 0, 0, 2, 2, 0, 0, 0), (0, 0, 0, 2, -2, 0, 0, 0)]
PR1212 = {
    'head': '57099cb5684f38877f31d149d598801671a633db',
    'dir': 'research/complex-rank8-decoder-rigidity',
    'blobs': {'verify.py': 'c3707b0993d04b78e20c5d3512d370495690df8b',
              'proof-P104-11111111.drup': 'e71c3c93deeb43a08772614fc439bd4b7bd08a24'},
    'pass_lines': ['PASS G.P104-11111111.zero-exclusion', 'PASS G.P104-11111111.class-witnesses',
                   'PASS G.frame-orbits', 'PASS G.pr717-p104-orbit'],
    'unit_line': ('PASS G.P104-11111111.unit', 'P112 minus the frame (2, 18, 40, 52, 77, 86, 107, 112)',
                  'pivot [12, 13, 22, 23, 30, 31, 36, 37]'),
    'dead_idx': [2, 18, 40, 52, 77, 86, 107, 112],
    'pivot_idx': [12, 13, 22, 23, 30, 31, 36, 37],
}


def is_frame(S):
    return len(S) == 8 and all(G[a][b] == 0 for a in S for b in S if a != b)


# ------------------------------------------------------------------ exact linear algebra
def rank_q(rows):
    M = [[Fraction(x) for x in r] for r in rows]
    if not M:
        return 0
    r = 0
    for c in range(len(M[0])):
        p = next((i for i in range(r, len(M)) if M[i][c] != 0), None)
        if p is None:
            continue
        M[r], M[p] = M[p], M[r]
        for i in range(len(M)):
            if i != r and M[i][c] != 0:
                f = M[i][c] / M[r][c]
                M[i] = [a - f * b for a, b in zip(M[i], M[r])]
        r += 1
    return r


def lcg(seed):
    x = seed
    while True:
        x = (6364136223846793005 * x + 1442695040888963407) % (1 << 64)
        yield x >> 33


def rand_nonzero(rng):
    while True:
        n = next(rng) % 17 - 8
        d = next(rng) % 7 + 1
        if n:
            return Fraction(n, d)


# ------------------------------------------------------------------ structure relative to a pivot
def relative(F, lines):
    """line -> (T, eps): T the pivot lines (in pivot order) the line is odd to, eps the signs G_if."""
    out = {}
    for i in lines:
        if i in F:
            continue
        T = tuple(f for f in F if G[i][f] != 0)
        out[i] = (T, tuple(G[i][f] for f in T))
    return out


def parity(eps):
    return sum(1 for s in eps if s < 0) % 2


def classes_of(rel):
    cl = {}
    for i, (T, eps) in rel.items():
        cl.setdefault((T, parity(eps)), []).append(i)
    return cl


def connected(nodes, edges):
    nodes = list(nodes)
    if not nodes:
        return False
    seen, todo = {nodes[0]}, [nodes[0]]
    while todo:
        x = todo.pop()
        for p, q in edges:
            for y in ((q,) if p == x else (p,) if q == x else ()):
                if y not in seen:
                    seen.add(y)
                    todo.append(y)
    return len(seen) == len(nodes)


def gauge_form(rel, F, g, dd):
    """a_i = d'_i eps_i g, b_i = 4 (d'_i g)^-1 eps_i on T_i (PR1212 section 7), pivots a_f = b_f = 4 e_f."""
    a = {i: {f: (dd[i] * G[i][f] * g[f] if f in rel[i][0] else Fraction(0)) for f in F} for i in rel}
    b = {i: {f: (4 / (dd[i] * g[f]) * G[i][f] if f in rel[i][0] else Fraction(0)) for f in F} for i in rel}
    for f in F:
        a[f] = {h: Fraction(4 if h == f else 0) for h in F}
        b[f] = {h: Fraction(4 if h == f else 0) for h in F}
    return a, b


def system_holds(a, b, live, F, rows=None):
    """Equations (2) of PR1212: a_i . b_j = 16 [i = j] on the diagonal and on orthogonal live pairs."""
    rows = live if rows is None else rows
    return all(sum(a[i][f] * b[j][f] for f in F) == (16 if i == j else 0)
               for i in rows for j in live if i == j or G[i][j] == 0)


def analyse(cert):
    print('== unit')
    F0 = frame_lines(FRAME0)
    P112 = [i for i in range(NL) if i not in F0]
    dead = frame_lines(DEAD)
    live = [i for i in P112 if i not in dead]
    F = frame_lines(PIVOT)
    check('unit.live', is_frame(dead) and set(dead) <= set(P112) and len(live) == 104
          and is_frame(F) and set(F) <= set(live), 'P112 minus a frame inside P112; live 104; pivot is a live frame')

    # Type of the punctured frame relative to FRAME0: how many of its lines fall in each FRAME0 class.
    cl0 = classes_of(relative(F0, range(NL)))
    hits = sorted((sum(1 for i in v if i in dead) for v in cl0.values()), reverse=True)
    check('unit.admissible-type', hits[:8] == [1] * 8 and sum(hits) == 8,
          'the punctured frame meets 8 distinct FRAME0 classes once each: type (1,...,1), the 896-orbit (PR968 admissible)')

    # Lemma 2 facts used below, recomputed relative to the pivot.
    rel_all = relative(F, range(NL))
    rel = relative(F, live)
    blocks = sorted({T for T, _ in rel_all.values()})
    ok_a = all(len(T) == 4 and all(abs(s) == 1 for s in e) for T, e in rel_all.values())
    steiner = len(blocks) == 14 and all(sum(1 for B in blocks if set(t) <= set(B)) == 1
                                        for t in itertools.combinations(F, 3))
    cl_all = classes_of(rel_all)
    had = len(cl_all) == 28 and all(
        len(v) == 4 and all(G[i][j] == 0 for i in v for j in v if i != j)
        and all(sum(x * y for x, y in zip(rel_all[i][1], rel_all[j][1])) == (4 if i == j else 0) for i in v for j in v)
        for v in cl_all.values())
    rule = True
    for i, j in itertools.combinations(rel_all, 2):
        Ti, ei = rel_all[i]
        Tj, ej = rel_all[j]
        s = sum(ei[Ti.index(f)] * ej[Tj.index(f)] for f in set(Ti) & set(Tj))
        rule &= (2 * G[i][j] == s)
    check('unit.d4-structure', ok_a and steiner and had and rule,
          '112 non-pivot lines odd to 4 pivot lines; 14 blocks = S(3,4,8); 28 Hadamard 4-frame classes; 2G_ij = sum of sign products')

    cl = classes_of(rel)
    sizes = {}
    for key in cl_all:
        n = len(cl.get(key, []))
        sizes[n] = sizes.get(n, 0) + 1
    check('unit.class-profile', sizes == {0: 2, 2: 4, 4: 22}, f'live rows per class -> count: {dict(sorted(sizes.items()))}')
    complete = {k: v for k, v in cl.items() if len(v) == 4}
    known = {i for v in complete.values() for i in v}
    rest = [i for i in rel if i not in known]

    # (I3) Lemma 5 step 1: every live group of every complete class has a live witness in another block.
    wit_ok, nwit = True, 0
    for (T, _), rows in complete.items():
        for c, c2 in itertools.combinations(range(4), 2):
            for i, i2 in itertools.combinations(rows, 2):
                if rel[i][1][c] * rel[i][1][c2] != rel[i2][1][c] * rel[i2][1][c2]:
                    continue
                nwit += 1
                wit_ok &= any(set(Tj) & set(T) == {T[c], T[c2]} and G[j][i] == 0 and G[j][i2] == 0
                              for j, (Tj, _) in rel.items())
    check('lemma5.group-witnesses', wit_ok and nwit == 22 * 12,
          f'{nwit} live groups (22 complete classes x 6 column pairs x 2 groups) each have a live witness')

    # (I4) Lemma 6: every block carries a complete live class, and for complete classes C, C' in distinct
    # blocks meeting in {k, k'}, every row j of C' is orthogonal to exactly two rows of C.
    cblocks = {T for (T, _) in complete}
    pair_ok, npair = True, 0
    for c1, c2 in itertools.permutations(complete, 2):
        if c1[0] == c2[0] or len(set(c1[0]) & set(c2[0])) != 2:
            continue
        npair += 1
        pair_ok &= all(sum(1 for i in complete[c1] if G[i][j] == 0) == 2 for j in complete[c2])
    check('lemma6.blocks-and-gluing', len(cblocks) == 14 and pair_ok,
          f'14/14 blocks carry a complete class; {npair} ordered class pairs through a pivot pair glue')

    # Lemma 9 (propagation) input: for every live line i outside the complete classes, the column pairs
    # {k, k'} of T_i witnessed by a line j of a complete class with G_ij = 0 and T_i n T_j = {k, k'}
    # connect T_i.  Also checked: every such witness has eps_ik eps_jk = -eps_ik' eps_jk', the identity
    # the derivation uses.
    prop_ok, sign_ok, prop = True, True, {}
    for i in rest:
        T, ei = rel[i]
        edges, nw = [], 0
        for c, c2 in itertools.combinations(range(4), 2):
            ws = [j for j in known if G[i][j] == 0 and set(rel[j][0]) & set(T) == {T[c], T[c2]}]
            for j in ws:
                ej = rel[j][1]
                Tj = rel[j][0]
                sign_ok &= ei[c] * ej[Tj.index(T[c])] == -ei[c2] * ej[Tj.index(T[c2])]
            if ws:
                edges.append((c, c2))
            nw += len(ws)
        prop[i] = (edges, nw)
        prop_ok &= connected(range(4), edges)
    full = all(len(e) == 6 for e, _ in prop.values())
    check('lemma9.propagation-connected', len(rest) == 8 and prop_ok and sign_ok,
          f'{len(rest)} two-row lines: witnessed column pairs connect T_i'
          + (' (all 6 pairs witnessed for every line)' if full else ''))

    # Lemma 9 algebra, cross-checked on the actual equations rather than the simplified ratio form: with the
    # complete classes in gauge form for random rational g, d', the witnessed equations (E2) in the order
    # a_i . b_j are linear in the 4 unknowns a_i|T and have a 1-dimensional solution space spanned by eps_i o g;
    # in the order a_j . b_i the same holds for b_i with eps_i / g.
    rng = lcg(1212)
    g = {f: rand_nonzero(rng) for f in F}
    dd = {i: rand_nonzero(rng) for i in rel}
    alg_ok = True
    for i in rest:
        T, ei = rel[i]
        wit = [j for j in known if G[i][j] == 0 and len(set(rel[j][0]) & set(T)) == 2]
        rows_a = [[4 / (dd[j] * g[f]) * G[j][f] for f in T] for j in wit]   # b_j|T coefficients
        rows_b = [[dd[j] * G[j][f] * g[f] for f in T] for j in wit]         # a_j|T coefficients
        va = [ei[n] * g[f] for n, f in enumerate(T)]
        vb = [ei[n] / g[f] for n, f in enumerate(T)]
        alg_ok &= rank_q(rows_a) == 3 and all(sum(r[n] * va[n] for n in range(4)) == 0 for r in rows_a)
        alg_ok &= rank_q(rows_b) == 3 and all(sum(r[n] * vb[n] for n in range(4)) == 0 for r in rows_b)
    check('lemma9.solution-line', alg_ok,
          'witnessed (E2) equations have rank 3 on a_i|T and on b_i|T, kernel spanned by eps_i o g and eps_i / g')

    # Assembly control (PR1212 section 7 on this unit): gauge forms satisfy (2) and assemble to D (2G) D^-1.
    a, b = gauge_form(rel, F, g, dd)
    D = {i: dd[i] / 2 for i in rel}
    D.update({f: 1 / g[f] for f in F})
    asm_ok = system_holds(a, b, live, F) and all(
        sum(a[i][f] * b[j][f] for f in F) / 4 == 2 * G[i][j] * D[i] / D[j] for i in live for j in live)
    check('assembly-control', asm_ok, 'gauge forms satisfy (2) on all 104 live lines and assemble to D (2G) D^-1 exactly')
    cert.update({'live': len(live), 'dead_frame': DEAD, 'pivot': PIVOT, 'class_profile': sizes,
                 'two_row_lines': {str(LINES[i]): {'support': [LINES[f] for f in rel[i][0]],
                                                   'witnessed_pairs': len(prop[i][0]), 'witnesses': prop[i][1]}
                                   for i in rest},
                 'group_witnesses': nwit, 'glued_class_pairs': npair, 'floor': 56})
    return live, F, rel, complete, known, rest, g, dd


def controls(data):
    print('== controls')
    live, F, rel, complete, known, rest, g, dd = data
    # C1: inside a two-row class, every in-class condition (E0, E4 both ways, Lemma 5 step-1 parallelism on the
    # one live group, for a and for b) admits a non-gauge solution.  Rows 1, 2 have eps_1 o eps_2 = s (1,1,-1,-1)
    # in the column order where they form a group; u_1 = (1,1,1,1), u_2 = (1,1,t,t), v_1 = (8t,8t,8,8)/(t+1),
    # v_2 = 8 (1,1,1,1)/(t+1), with a = eps o u, b = eps o v.  For t = 2 it is not of gauge form.
    i1 = rest[0]
    T, e1 = rel[i1]
    i2 = next(j for j in rest if j != i1 and rel[j][0] == T and parity(rel[j][1]) == parity(e1))
    e2 = rel[i2][1]
    p = [e1[n] * e2[n] for n in range(4)]
    grp = next((c, c2) for c, c2 in itertools.combinations(range(4), 2) if p[c] == p[c2])
    oth = tuple(n for n in range(4) if n not in grp)
    t = Fraction(2)
    u1 = [Fraction(1)] * 4
    u2 = [t if n in oth else Fraction(1) for n in range(4)]
    v1 = [8 * (t if n in grp else 1) / (t + 1) for n in range(4)]
    v2 = [Fraction(8) / (t + 1)] * 4
    A = {i1: [e1[n] * u1[n] for n in range(4)], i2: [e2[n] * u2[n] for n in range(4)]}
    B = {i1: [e1[n] * v1[n] for n in range(4)], i2: [e2[n] * v2[n] for n in range(4)]}

    def dot(x, y):
        return sum(x[n] * y[n] for n in range(4))
    in_class = (dot(A[i1], B[i1]) == 16 and dot(A[i2], B[i2]) == 16 and dot(A[i1], B[i2]) == 0
                and dot(A[i2], B[i1]) == 0 and G[i1][i2] == 0)
    par = all(X[i1][c] * X[i2][c2] == X[i1][c2] * X[i2][c] for X in (A, B) for c, c2 in (grp, oth))
    gauge = rank_q([[A[i1][n] * e1[n] for n in range(4)], [A[i2][n] * e2[n] for n in range(4)]]) == 1
    check('control.in-class-not-forced', in_class and par and not gauge,
          'a non-gauge two-row solution satisfies every in-class condition (PR1212: one-parameter family)')
    # C2: the same rows fail a witnessed cross-block equation (E2) once the complete classes are in gauge form
    # (any scaling: here g = 1 on T, matching u_1, so row 1 passes and row 2 must fail).
    g1 = {f: Fraction(1) for f in F}
    _, bg = gauge_form(rel, F, g1, dd)
    wit = [j for j in known if G[i2][j] == 0 and len(set(rel[j][0]) & set(T)) == 2]
    fails = [j for j in wit if sum(A[i2][n] * bg[j][f] for n, f in enumerate(T)) != 0]
    check('control.cross-block-rejects', len(fails) > 0,
          f'{len(fails)}/{len(wit)} witnessed (E2) equations reject the non-gauge row')
    # C3: the connectivity input is necessary for the conclusion: dropping every witness at one column of T_i
    # leaves a 2-dimensional solution space for a_i|T.
    i = rest[0]
    T, _ = rel[i]
    wit = [j for j in known if G[i][j] == 0 and len(set(rel[j][0]) & set(T)) == 2 and T[0] not in rel[j][0]]
    rows_a = [[4 / (dd[j] * g[f]) * G[j][f] for f in T] for j in wit]
    check('control.disconnected-not-forced', 4 - rank_q(rows_a) == 2,
          'without witnesses at one column the propagation equations leave 2 free directions')
    # C4: tripling one entry of a two-row line in an exact gauge solution breaks (2).
    a, b = gauge_form(rel, F, g, dd)
    a[i][T[0]] *= 3
    check('control.perturbed-fails', not system_holds(a, b, live, F, rows=[i]), 'tripling one a-entry of a two-row line violates (2)')


def git_blob_sha1(path):
    data = open(path, 'rb').read()
    return hashlib.sha1(b'blob %d\0' % len(data) + data).hexdigest()


def replay_pr1212(root, cert):
    print('== PR1212 replay (zero exclusion, witnesses, transport)')
    pkg = os.path.join(root, PR1212['dir'])
    blobs = {f: git_blob_sha1(os.path.join(pkg, f)) for f in PR1212['blobs']}
    if not check('pr1212.blobs', blobs == PR1212['blobs'], f'files match head {PR1212["head"][:8]}'):
        return
    out = subprocess.run([sys.executable, '-I', '-B', os.path.join(pkg, 'verify.py')], capture_output=True, text=True,
                         cwd=root).stdout
    lines = out.splitlines()
    for p in PR1212['pass_lines']:
        check('pr1212.' + p.split()[1], any(l.startswith(p + ' ') or l == p for l in lines), p)
    head, unit, piv = PR1212['unit_line']
    check('pr1212.unit-line', any(l.startswith(head) and unit in l and piv in l for l in lines), f'{unit}; {piv}')
    code = ('import sys,json; sys.path.insert(0, sys.argv[1]); import verify as V; '
            'print(json.dumps({"lines": V.LINES}))')
    vec = json.loads(subprocess.run([sys.executable, '-I', '-B', '-c', code, pkg], capture_output=True, text=True).stdout)
    same = (sorted(canon(vec['lines'][i]) for i in PR1212['pivot_idx']) == sorted(canon(v) for v in PIVOT)
            and sorted(canon(vec['lines'][i]) for i in PR1212['dead_idx']) == sorted(canon(v) for v in DEAD))
    check('pr1212.unit-vectors', same, 'same punctured frame and pivot as root vectors')
    cert['pr1212_replayed'] = True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pr1212-dir', help='checkout of PR1212 head 57099cb5 (repo root); replays its zero-exclusion checks')
    ap.add_argument('--out', help='write certificate JSON (must not exist)')
    args = ap.parse_args()
    cert = {'pr1212_head': PR1212['head'], 'pr1212_replayed': False}
    print('== model')
    check('model.lines', NL == 120 and {abs(G[i][j]) for i in range(NL) for j in range(NL) if i != j} == {0, 1},
          '120 lines, Gram off-diagonal in {0,+-1}')
    check('model.frame0', is_frame(frame_lines(FRAME0)), 'FRAME0 is a frame')
    data = analyse(cert)
    controls(data)
    if args.pr1212_dir:
        replay_pr1212(args.pr1212_dir, cert)
    else:
        print('NOTE zero exclusion and orbit transport cited from PR1212 (not replayed; pass --pr1212-dir)')
    if args.out:
        with open(args.out, 'x') as fh:
            json.dump(cert, fh, indent=1, default=list)
    if FAILS:
        print('FAILED: ' + ', '.join(FAILS))
        sys.exit(1)
    print(f'PASS_COMPLEX_RANK8_RIGIDITY_P104_ADMISSIBLE: checks {NCHECK}; classes 22 complete + 4 two-row; '
          f'8 two-row lines propagated; floor 56; zero exclusion '
          + ('replayed from PR1212' if cert['pr1212_replayed'] else 'cited from PR1212'))


if __name__ == '__main__':
    main()
