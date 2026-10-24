#!/usr/bin/env python3
"""Route 2 construction: an explicit sparse T realising the design frames.

The lower-bound check showed every design frame has enough diagonal monomials inside it to
support the rows that need it, so an invertible scalar T exists in principle.  This receipt
builds one explicitly, p by p, and tests it:

    row i uses a set S_i of diagonal monomials with union of supports exactly the design frame;
    rows with the same frame get distinct sets, so T is not rank deficient;
    T is checked invertible over Q, T^-1 is formed, and M_new = T D T^-1 is assembled
    coefficient by coefficient (the coefficient of d_k is column k of T times row k of T^-1);
    the realised row frames are recomputed from M_new after exact coefficient collection;
    C.factor(M_new) must return the required diagonal.

Cost is reported as nnz(T) and nnz(T^-1), the two numbers a compiled scalar schedule pays for.
"""
import importlib.util, json, itertools, sys
from collections import Counter, defaultdict
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

def need(ok, why):
    if not ok: raise ValueError(why)

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod

def matmul(X, Y):
    n = len(X)
    return [[sum((X[i][k]*Y[k][j] for k in range(n)), Q(0)) for j in range(n)] for i in range(n)]

def matinv(X):
    n = len(X)
    M = [row[:] + [Q(int(i == j)) for j in range(n)] for i, row in enumerate(X)]
    for c in range(n):
        p = next((r for r in range(c, n) if M[r][c]), None)
        if p is None: return None
        M[c], M[p] = M[p], M[c]
        f = M[c][c]
        M[c] = [x/f for x in M[c]]
        for r in range(n):
            if r != c and M[r][c]:
                g = M[r][c]
                M[r] = [a - g*b for a, b in zip(M[r], M[c])]
    return [row[n:] for row in M]

def main():
    mod = load('c4940_t', ROOT/'research/coded-reverse-controller/verify.py')
    C = mod.C
    out = {'status': 'SPARSE_T', 'cases': {}}
    for p, pat in ((3, 'IT'), (4, 'IIT'), (5, 'IITT')):
        thick = frozenset(range(1, 2*p, 2))
        co, _ = mod.controller(p, mod.keep_of(p, pat), {s: Q(1) for s in range(2*p+1)})
        base = C.factor(mod.thin(co, thick))
        need(base is not None, 'controller factorises at p=%d' % p)
        D_list = base['diagonal']
        n = len(D_list)
        d_supp = [frozenset(s for s, b in enumerate(k[1:]) if b) & thick for k in D_list]

        full = frozenset(range(2*p+1)); outs = [full, full]
        for i, ch in enumerate(pat, 1):
            outs += [frozenset(range(0, 2*i+1)) if ch == 'I' else frozenset(range(2*i, 2*p+1))]*2
        des = [frozenset(s & thick) for s in outs]

        # cheapest construction first: if every design frame is exactly the support of a
        # distinct diagonal monomial, T is a permutation and the scalar cost is n, not n^2
        by_supp = defaultdict(list)
        for k, supp in enumerate(d_supp): by_supp[supp].append(k)
        perm = {}
        used = set()
        exact = True
        for i, F in enumerate(des):
            cand = [k for k in by_supp.get(F, []) if k not in used]
            if not cand:
                exact = False
                break
            perm[i] = cand[0]; used.add(cand[0])
        if exact:
            T = [[Q(0)]*n for _ in range(n)]
            for i in range(n): T[i][perm[i]] = Q(1)
            Ti = matinv(T)
            keys = sorted(set(D_list))
            coeffs = {}
            for key in keys:
                E = [[Q(int(D_list[i] == key and i == j)) for j in range(n)] for i in range(n)]
                m = matmul(matmul(T, E), Ti)
                if any(any(r) for r in m): coeffs[key] = m
            rows = {i: set() for i in range(n)}
            for key, m in coeffs.items():
                sel = {s for s, b in enumerate(key[1:]) if b} & thick
                for i in range(n):
                    if any(m[i][j] for j in range(n)): rows[i] |= sel
            real = [frozenset(rows[i]) for i in range(n)]
            r2 = C.factor(coeffs)
            diag2 = None if r2 is None else sorted(Counter(sum(t[1:]) for t in r2['diagonal']).items())
            want = sorted(Counter(sum(t[1:]) for t in D_list).items())
            nnzT = sum(1 for row in T for v in row if v)
            nnzTi = sum(1 for row in Ti for v in row if v)
            out['cases']['p%d_%s' % (p, pat)] = {
                'construction': 'permutation T (exact support match)',
                'frames_realised': real == des, 'factorises': r2 is not None,
                'diagonal_required': want, 'diagonal_actual': diag2, 'diagonal_match': diag2 == want,
                'nnz_T': nnzT, 'nnz_T_inverse': nnzTi, 'n': n,
                'designed_frames': [sorted(s) for s in des]}
            print('p=%d %-4s PERMUTATION T: nnz(T)=%d nnz(T^-1)=%d  frames realised %s  factorises %s  '
                  'diagonal %s == %s : %s'
                  % (p, pat, nnzT, nnzTi, real == des, r2 is not None, diag2, want, diag2 == want))
            continue

        # otherwise build distinct row sets as before
        by_frame = defaultdict(list)
        for i, F in enumerate(des): by_frame[F].append(i)
        rows_sets = {}
        for F, idxs in by_frame.items():
            inside = [k for k, s in enumerate(d_supp) if s and s <= F]
            need(inside, 'some diagonal monomial lies inside frame %s at p=%d' % (sorted(F), p))
            chosen = []
            # first pick a minimal cover, then extend for the remaining rows
            cover = []
            have = set()
            for k in sorted(inside, key=lambda k: -len(d_supp[k])):
                if not d_supp[k] <= have:
                    cover.append(k); have |= d_supp[k]
                if have >= F: break
            need(have >= F, 'the frame is covered at p=%d' % p)
            chosen.append(sorted(cover))
            pool = [k for k in inside if k not in cover]
            for j in range(1, len(idxs)):
                if pool:
                    extra = pool.pop(0)
                    chosen.append(sorted(set(cover) | {extra}))
                else:
                    need(len(cover) > 1, 'no distinct set available for frame %s at p=%d' % (sorted(F), p))
                    chosen.append(sorted(set(cover) - {cover[-1]}))
            for S, i in zip(chosen, idxs): rows_sets[i] = S

        # frames implied by the chosen sets
        implied = [frozenset().union(*[d_supp[k] for k in rows_sets[i]]) if rows_sets[i] else frozenset()
                   for i in range(n)]
        frames_ok = implied == des

        # T with generic distinct entries on the chosen supports
        T = [[Q(0)]*n for _ in range(n)]
        for i in range(n):
            for k in rows_sets[i]:
                T[i][k] = Q(1, 1 + (i*n + k) % 7)
        Ti = matinv(T)
        need(Ti is not None, 'T is invertible at p=%d' % p)

        keys = sorted(set(D_list))
        coeffs = {}
        for key in keys:
            E = [[Q(int(D_list[i] == key and i == j)) for j in range(n)] for i in range(n)]
            m = matmul(matmul(T, E), Ti)
            if any(any(r) for r in m): coeffs[key] = m

        rows = {i: set() for i in range(n)}
        for key, m in coeffs.items():
            sel = {s for s, b in enumerate(key[1:]) if b} & thick
            for i in range(n):
                if any(m[i][j] for j in range(n)): rows[i] |= sel
        real = [frozenset(rows[i]) for i in range(n)]
        frames_realised = real == des

        r2 = C.factor(coeffs)
        diag2 = None if r2 is None else sorted(Counter(sum(t[1:]) for t in r2['diagonal']).items())
        want = sorted(Counter(sum(t[1:]) for t in D_list).items())

        nnzT = sum(1 for row in T for v in row if v)
        nnzTi = sum(1 for row in Ti for v in row if v)
        out['cases']['p%d_%s' % (p, pat)] = {
            'row_sets': {str(i): rows_sets[i] for i in range(n)},
            'implied_frames': [sorted(s) for s in implied], 'designed_frames': [sorted(s) for s in des],
            'frames_realised': frames_realised, 'factorises': r2 is not None,
            'diagonal_required': want, 'diagonal_actual': diag2, 'diagonal_match': diag2 == want,
            'nnz_T': nnzT, 'nnz_T_inverse': nnzTi, 'n': n}
        print('p=%d %-4s n=%d  nnz(T)=%d nnz(T^-1)=%d' % (p, pat, n, nnzT, nnzTi))
        print('        frames realised %s   factorises %s   diagonal %s == %s : %s'
              % (frames_realised, r2 is not None, diag2, want, diag2 == want))
        if not frames_realised:
            print('        implied %s' % [sorted(s) for s in implied])
            print('        designed %s' % [sorted(s) for s in des])

    ok = all(v['frames_realised'] and v['factorises'] and v['diagonal_match'] for v in out['cases'].values())
    out['status'] = 'PASS_SPARSE_T_CONSTRUCTION' if ok else 'FINDING_SPARSE_T_FAILS'
    (HERE/'P19_SPARSET.json').write_text(json.dumps(out, indent=2, sort_keys=True)+'\n')
    print(json.dumps({'status': out['status']}, sort_keys=True))

if __name__ == '__main__':
    main()
