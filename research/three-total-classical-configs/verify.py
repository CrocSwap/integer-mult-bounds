"""Replay for research/three-total-classical-configs (standard library only; about 60 s, about 3 min with --enumall).

usage: python3 -I -B research/three-total-classical-configs/verify.py [--enumall PATH_TO_COMPILED_c/enumall.c]
Prints one PASS/FAIL line per check and a final PASS_THREE_TOTAL_CLASSICAL_CONFIGS line; exit status 1 on any failure.
All acceptance checks are exact (integers and GF(2^k) bitmask arithmetic).  The search-free certificate checker and the
constructive Desargues count below are written here and do not import lib/universal.py.
"""
import hashlib, itertools, json, os, sys, time

PKG = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(PKG, 'lib'))
from classical import (pappus, desargues, check_config, frames, transform, setup, dot, det3, odd_diagonal,
                       cost_of, tomat)
from cr2 import realise, cfg_data                     # vendored from #2162 (DFS used for per-instance cross-checks)
from universal import universal_realise              # used only to replay the exhaustive exclusions

BAD = [0]; T0 = time.time()
ENUMALL = sys.argv[sys.argv.index('--enumall') + 1] if '--enumall' in sys.argv else None   # optional native replay


def report(name, ok, msg=''):
    print('%s %s  %s' % ('PASS' if ok else 'FAIL', name, msg), flush=True)
    if not ok:
        BAD[0] += 1


# ---------- independent GF(2^k) arithmetic ----------
POLY = {1: 0b11, 2: 0b111, 3: 0b1011, 4: 0b10011}


def gmul(a, b, k):
    r = 0
    while b:
        if b & 1:
            r ^= a
        b >>= 1; a <<= 1
        if a >> k & 1:
            a ^= POLY[k]
    return r


def gdot(a, b, k):
    return gmul(a[0], b[0], k) ^ gmul(a[1], b[1], k) ^ gmul(a[2], b[2], k)


def gcross(a, b, k):
    return (gmul(a[1], b[2], k) ^ gmul(a[2], b[1], k), gmul(a[2], b[0], k) ^ gmul(a[0], b[2], k),
            gmul(a[0], b[1], k) ^ gmul(a[1], b[0], k))


def supp_ok(V, W, k):
    return len(V) == 3 and any(V) and all(0 <= x < (1 << k) for x in V) and all(W[j] or not V[j] for j in range(3))


def universal_ok(P, L, k, X, Y):
    """Frame-universal certificate: supports shrink, and X[i].Y[j] == 0 over GF(2^k) iff P[i].L[j] == 0 over Z."""
    if len(X) != len(P) or len(Y) != len(L):
        return False
    if not all(supp_ok(a, b, k) for a, b in zip(X, P)) or not all(supp_ok(a, b, k) for a, b in zip(Y, L)):
        return False
    return all((dot(P[i], L[j]) == 0) == (gdot(X[i], Y[j], k) == 0) for i in range(len(P)) for j in range(len(L)))


def cr2_hyp_ok(P, Q, k, Pt, Qt):
    """Hypotheses of #2162 Lemma CR2 for one decoder configuration: supports, every in-block incidence, nonzero diagonal."""
    v = len(P); R, A, free = setup(P, Q)
    if len(Pt) != v or len(Qt) != v:
        return False
    if not all(supp_ok(Pt[t], P[t], k) and supp_ok(Qt[t], Q[t], k) for t in range(v)):
        return False
    return all(gdot(Pt[t], Qt[s], k) == 0 for (t, s) in free) and all(gdot(Pt[t], Qt[t], k) != 0 for t in range(v))


def desargues_exact_count(k, a2_choices=None):
    """Constructive, exhaustive: Desargues 10_3 realisations over GF(2^k) with O, a0, a1 = e1, e2, e3 (WLOG by PGL(3):
    O, a0, a1 are non-collinear in any exact realisation).  Every point of line O a_i other than O, a_i is a_i + mu_i O with
    mu_i != 0; c_ij = a_ia_j x b_ib_j and axis = c01 x c02 are forced.  Counts the choices whose point-line incidence
    relation equals the combinatorial 10_3 incidences exactly."""
    q = 1 << k
    C = desargues(); pn, ln = C['pnames'], C['lnames']
    want = {(pn.index(p), ln.index(l)) for (p, l) in C['incidences']}
    O, a0, a1 = (1, 0, 0), (0, 1, 0), (0, 0, 1)
    allpts = [v for v in itertools.product(range(q), repeat=3) if any(v) and next(x for x in v if x) == 1]
    prs = [(0, 1), (0, 2), (1, 2)]
    cnt = 0
    for a2 in (a2_choices or allpts):
        A = [a0, a1, tuple(a2)]
        for mu in itertools.product(range(1, q), repeat=3):
            B = [(A[i][0] ^ mu[i], A[i][1], A[i][2]) for i in range(3)]
            c = [gcross(gcross(A[i], A[j], k), gcross(B[i], B[j], k), k) for (i, j) in prs]
            pts = [O] + A + B + c
            lines = [gcross(A[i], B[i], k) for i in range(3)] + [gcross(A[i], A[j], k) for (i, j) in prs] + \
                    [gcross(B[i], B[j], k) for (i, j) in prs] + [gcross(c[0], c[1], k)]
            if not all(any(x) for x in pts + lines):
                continue
            got = {(i, j) for i in range(10) for j in range(10) if gdot(pts[i], lines[j], k) == 0}
            cnt += got == want
    return cnt


def main():
    # 0. manifest
    bad = []
    for line in open(os.path.join(PKG, 'MANIFEST.sha256')):
        h, p = line.split()
        if hashlib.sha256(open(os.path.join(PKG, p), 'rb').read()).hexdigest() != h:
            bad.append(p)
    PINS = {'lib/cr2.py': 'ff3c1bbd072c4d1f47158f903aa3ff4fcd8db5bbc4709c3d15b21a1815eef3bd',    # #2162 MANIFEST.sha256
            'c/enumall.c': '55d864202535c22952e1a9080ad834f1908d18ff857c8dc26211e25a847d1fc8',   # = #2111 c/enumall.c
            'data/tied_min.json': '670ed90924b601ade22f0d4adaff46d1667e5449326a0f7ba7b88dd8f5906f93',
            'data/cex_min_1.json': '86064701dde94b4f35427bc3e19275eaf1e40e9e90d4fea28e7857f3564d4dd7',
            'data/tm_noncr2.json': 'b5aa8ca01a87a898ae27160d5274af7ff08127cf0b27cf372f73a5725cd216a5',
            'data/cr2_realisations.json': '2ce114152529d375215f1f64a45072c9b78d1719d156e76bc692eff1fa955666'}
    bad += [p for p, h in PINS.items() if hashlib.sha256(open(os.path.join(PKG, p), 'rb').read()).hexdigest() != h]
    report('0 MANIFEST.sha256, and vendored lib/cr2.py, c/enumall.c and copied data match the #2162 head 113a7182 pins', not bad, str(bad))

    # 1. configurations
    confs = [(desargues(), 10), (pappus(), 9)]
    for C, n in confs:
        pts, lines = C['points'], C['lines']; inc = {tuple(x) for x in C['incidences']}
        pn, ln = C['pnames'], C['lnames']
        on = lambda tri: any(all((pn[i], ln[l]) in inc for i in tri) for l in range(n))
        at = lambda tri: any(all((pn[p], ln[l]) in inc for l in tri) for p in range(n))
        ec = [t for t in itertools.combinations(range(n), 3) if det3(*[pts[i] for i in t]) == 0 and not on(t)]
        el = [t for t in itertools.combinations(range(n), 3) if det3(*[lines[i] for i in t]) == 0 and not at(t)]
        report('1 %s %d_3 over Z: exactly the %d configuration incidences, no extra collinear point / concurrent line triples'
               % (C['name'], n, 3 * n), check_config(C, n, 3) and not ec and not el)

    # 2. frame-universal certificates (search-free check)
    U = json.load(open(os.path.join(PKG, 'data', 'universal.json')))
    kwant = {'desargues': 4, 'pappus': 2}; nframes = {}
    for C, n in confs:
        recs = U['configs'][C['name']]; frs = [('I',)] + frames(C)
        ok = [tuple(r['frame']) for r in recs] == frs; ks = set()
        for r, fr in zip(recs, frs):
            P2, L2 = (C['points'], C['lines']) if fr == ('I',) else transform(C, fr)
            ok &= [list(p) for p in P2] == r['P'] and [list(l) for l in L2] == r['L']
            ok &= 'k' in r and universal_ok(P2, L2, r['k'], r['X'], r['Y']); ks.add(r.get('k'))
        nframes[C['name']] = len(recs)
        report('2 %s: all %d frames (identity + %d point/line coordinate triangles) carry a frame-universal char-2 '
               'realisation over GF(%d)' % (C['name'], len(recs), len(recs) - 1, 1 << kwant[C['name']]),
               ok and ks == {kwant[C['name']]})

    # 3. exclusions (smaller fields): recorded for every frame, DFS replay on a fixed subset, independent constructive count
    for C, n in confs:
        recs = U['configs'][C['name']]; sub = recs[::15]; ok = True
        for r in sub:
            for k in r['excluded']:
                ok &= universal_realise(r['P'], r['L'], k, limit=200000) is None
        allex = all(r['excluded'] == list(range(1, kwant[C['name']])) and not r['timeout'] for r in recs)
        report('3 %s: frame-universal realisation exhaustively excluded over GF(2^k), k < %d, in every frame (recorded); '
               'DFS replay on %d frames%s' % (C['name'], kwant[C['name']], len(sub),
               '; for every frame this also follows from the count below, since a GF(4)/GF(8) frame certificate would be '
               'an exact 10_3 in PG(2,4)/PG(2,8) and GF(2) is a subfield of both' if C['name'] == 'desargues' else ''),
               ok and allex)
    c4, c8 = desargues_exact_count(2), desargues_exact_count(3)
    report('3 Desargues 10_3, separately coded constructive count: no exact realisation in PG(2,4) or PG(2,8)', c4 == 0 and c8 == 0,
           'counts %d, %d' % (c4, c8))
    r = next(x for x in U['configs']['desargues'] if x['frame'] == ['P', 0, 1, 2])
    c16 = desargues_exact_count(4, a2_choices=[r['X'][3]])
    report('3 positive control: the constructive count finds exact PG(2,16) realisations (a2 fixed to the stored one)', c16 > 0,
           'count %d' % c16)

    # 4. sampled instances: universal certificate applied per instance + stored per-instance cr2.py results
    I = json.load(open(os.path.join(PKG, 'data', 'instances.json')))
    cache = {}; n_cert = n_dfs = n_2adic = skipped = 0; nonCR2 = []; okall = True; fs = []
    byname = {C['name']: C for C, n in confs}
    ucert = {c: {tuple(r['frame']): r for r in U['configs'][c]} for c in U['configs']}
    for rec in I['instances']:
        C = byname[rec['config']]; fr = tuple(rec['frame'])
        if (C['name'], fr) not in cache:
            cache[(C['name'], fr)] = transform(C, fr)
        P2, L2 = cache[(C['name'], fr)]
        P = [P2[i] for i, k in rec['pairs']]; Q = [L2[k] for i, k in rec['pairs']]
        f = len(setup(P, Q)[2]); fs.append(f)
        okall &= all(dot(p, q) != 0 for p, q in zip(P, Q)) and 6 <= len(P) <= 10 and f == rec['f'] and len(P) == rec['v']
        u = ucert[C['name']][fr]
        Pt = [u['X'][i] for i, k in rec['pairs']]; Qt = [u['Y'][k] for i, k in rec['pairs']]
        uok = cr2_hyp_ok(P, Q, u['k'], Pt, Qt); okall &= uok; n_cert += uok
        if rec['status'] == 'CR2' and rec['via'] == 'dfs':
            okall &= cr2_hyp_ok(P, Q, rec['k'], rec['Pt'], rec['Qt']); n_dfs += 1
        elif rec['status'] == 'CR2' and rec['via'] == '2adic-a0':
            okall &= odd_diagonal(P, Q); n_2adic += 1
        else:
            nonCR2.append(rec); skipped += rec.get('exact') == 'skipped-f'
    report('4 %d sampled decoder configurations (v = 6..10, f = %d..%d, seed %d): Lemma CR2 hypotheses hold via the '
           'frame-universal certificate; independent per-instance cross-check: %d by the vendored cr2.py DFS, %d by the a = 0 '
           '2-adic test' % (len(I['instances']), min(fs), max(fs), I['seed'], n_dfs, n_2adic),
           okall and n_cert == len(I['instances']) and not nonCR2)

    # 5. controls
    T = json.load(open(os.path.join(PKG, 'data', 'tied_min.json'))); Pm = [l[0] for l in T]; Qm = [l[1] for l in T]
    R, A, free = setup(Pm, Qm); pi, sig = cfg_data(Pm, Qm)
    res = [realise(pi, sig, set(free), k=k) for k in (1, 2, 3)]
    report('5 control tied_min (#2111): NOT CR2 over GF(2), GF(4), GF(8) (exhaustive DFS), f = %d' % len(free),
           all(x is None for x in res) and len(free) == 72)
    S = (0, 1, 2, 3, 8, 10); P6 = [Pm[i] for i in S]; Q6 = [Qm[i] for i in S]; R, A, free = setup(P6, Q6); pi, sig = cfg_data(P6, Q6)
    res = [realise(pi, sig, set(free), k=k) for k in (1, 2, 3)]
    best = min(cost_of(P6, Q6, tomat(g, free, 6)) for g in range(1 << len(free)))
    report('5 control: six-line atom %s of tied_min (#2162): NOT CR2, and pure-Python exhaustive min over 2^%d admissible B '
           '= 6 = v (tight)' % (list(S), len(free)), all(x is None for x in res) and best == 6)
    D = json.load(open(os.path.join(PKG, 'data', 'cr2_realisations.json')))['cex_min_1']
    X = json.load(open(os.path.join(PKG, 'data', 'cex_min_1.json'))); Pc = [l[0] for l in X]; Qc = [l[1] for l in X]
    report('5 control: stored #2162 CR2 realisation of cex_min_1 (GF(%d)) passes the CR2 hypothesis checker' % (1 << D['k']),
           cr2_hyp_ok(Pc, Qc, D['k'], D['P'], D['Q']))
    neg = []                                             # negative controls: each must be REJECTED
    r = U['configs']['desargues'][1]; Xb = [list(x) for x in r['X']]; Xb[3][1] ^= 1
    neg.append(('corrupted certificate entry', universal_ok(r['P'], r['L'], r['k'], Xb, r['Y'])))
    r2 = U['configs']['desargues'][2]
    neg.append(('certificate checked against another frame', universal_ok(r2['P'], r2['L'], r['k'], r['X'], r['Y'])))
    r3 = U['configs']['pappus'][5]
    neg.append(('Pappus GF(4) certificate read over GF(8)', universal_ok(r3['P'], r3['L'], 3, r3['X'], r3['Y'])))
    Cb = desargues(); Cb['points'] = list(Cb['points']); p9 = Cb['points'][9]; Cb['points'][9] = (p9[0] + 1, p9[1], p9[2])
    neg.append(('corrupted Desargues realisation (one coordinate +1)', check_config(Cb, 10, 3)))
    Db = [list(x) for x in D['P']]; Db[0] = [0, 0, 0]
    neg.append(('cex_min_1 realisation with a zeroed point', cr2_hyp_ok(Pc, Qc, D['k'], Db, D['Q'])))
    r4 = U['configs']['pappus'][7]; Yb = [list(y) for y in r4['Y']]; Yb[0], Yb[3] = Yb[3], Yb[0]
    neg.append(('Pappus frame certificate with two line vectors swapped (incidence-only corruption)',
                universal_ok(r4['P'], r4['L'], r4['k'], r4['X'], Yb)))
    neg.append(('tied_min with a constant GF(2) assignment', cr2_hyp_ok(Pm, Qm, 1, [[1, 1, 1]] * 12, [[1, 1, 0]] * 12)))
    report('5 negative controls rejected: ' + '; '.join(nm for nm, val in neg), not any(val for nm, val in neg),
           str([nm for nm, val in neg if val]))

    # 6. special (zero-richer) realisations: combinatorial lemma for Desargues, certificates for the Pappus signatures
    for C, n in confs:
        inc = {tuple(x) for x in C['incidences']}; pn, ln = C['pnames'], C['lnames']
        colin = lambda a, b: any((pn[a], ln[l]) in inc and (pn[b], ln[l]) in inc for l in range(n))
        conc = lambda a, b: any((pn[p], ln[a]) in inc and (pn[p], ln[b]) in inc for p in range(n))
        free_pt = [t for t in itertools.combinations(range(n), 3) if not any(colin(a, b) for a, b in itertools.combinations(t, 2))]
        free_ln = [t for t in itertools.combinations(range(n), 3) if not any(conc(a, b) for a, b in itertools.combinations(t, 2))]
        if C['name'] == 'desargues':
            report('6 Desargues lemma: every point triple contains two points on a common configuration line (and dually), so no '
                   'exact realisation has an extra collinear / concurrent triple', not free_pt and not free_ln)
        else:
            report('6 Pappus: the only possible extra collinear point triples are A_iB_iC_i and the only extra concurrent line '
                   'triples are {l,m,pap}, {A0B1,A1B2,A2B0}, {A0B2,A1B0,A2B1}: %s / %s' % (free_pt, free_ln),
                   free_pt == [(0, 3, 6), (1, 4, 7), (2, 5, 8)] and free_ln == [(0, 1, 2), (3, 6, 7), (4, 5, 8)])
    SP = json.load(open(os.path.join(PKG, 'data', 'special.json'))); ok = True; nfr = 0; uncert = []
    ok &= SP['configs']['desargues']['signatures'] == 0
    for r in SP['configs']['pappus']['realisations']:
        C = pappus(**{k: tuple(v) for k, v in r['params'].items()})
        ok &= check_config(C, 9, 3) and [list(p) for p in C['points']] == r['points'] and [list(l) for l in C['lines']] == r['lines']
        frs = [('I',)] + frames(C); ok &= [tuple(f['frame']) for f in r['frames']] == frs
        for f, fr in zip(r['frames'], frs):
            P2, L2 = (C['points'], C['lines']) if fr == ('I',) else transform(C, fr)
            if f['k'] is None:
                uncert.append((r['params'], fr)); ok &= f.get('excluded_upto') == 4
                ok &= all(universal_realise(P2, L2, k, limit=10 ** 6) is None for k in (1, 2, 3, 4))
            else:
                ok &= universal_ok(P2, L2, f['k'], f['X'], f['Y']); nfr += 1
    sigs = {(tuple(map(tuple, r['extra_point_triples'])), tuple(map(tuple, r['extra_line_triples'])))
            for r in SP['configs']['pappus']['realisations']}
    report('6 Pappus special realisations: %d extra-triple signatures (grid %d points), %d frame certificates verified; '
           'exactly one coordinate system without one, exhaustively excluded over GF(2..16): %s'
           % (len(sigs), SP['configs']['pappus']['scanned'], nfr, uncert), ok and len(sigs) == 12 and len(uncert) == 1
           and uncert[0][1] == ('I',))

    # 7. per-instance classification on that coordinate system
    SI = json.load(open(os.path.join(PKG, 'data', 'special_instances.json')))
    tgts = [r for r in SP['configs']['pappus']['realisations'] if any(f['k'] is None for f in r['frames'])]
    if not tgts:
        report('7 special Pappus frame: no uncertified coordinate system recorded in data/special.json', False)
        print('FAIL_THREE_TOTAL_CLASSICAL_CONFIGS (%d failures)' % BAD[0]); sys.exit(1)
    tgt = tgts[0]
    P2, L2 = tgt['points'], tgt['lines']; ok = True; sc = dict(cr2=0, exact=0, skipped=0, py_exhaustive=0)
    special_mins = []
    for rec in SI['instances']:
        P = [P2[i] for i, k in rec['pairs']]; Q = [L2[k] for i, k in rec['pairs']]
        R_, A_, free = setup(P, Q); v = len(P)
        ok &= all(dot(p, q) != 0 for p, q in zip(P, Q)) and len(free) == rec['f'] and v == rec['v']
        if rec['status'] == 'CR2':
            ok &= cr2_hyp_ok(P, Q, rec['k'], rec['Pt'], rec['Qt']) if rec['via'] == 'dfs' else odd_diagonal(P, Q); sc['cr2'] += 1
            continue
        pi, sig = cfg_data(P, Q)
        ok &= rec['status'] == 'nonCR2' and all(realise(pi, sig, set(free), k=k) is None for k in (1, 2, 3))
        if rec.get('exact') == 'skipped-f':
            ok &= len(free) > 26; sc['skipped'] += 1; continue
        ok &= cost_of(P, Q, tomat(rec['witness_g'], free, v)) == rec['min'] and rec['witness_g'] < 1 << len(free)
        if len(free) <= 18:
            ok &= min(cost_of(P, Q, tomat(g, free, v)) for g in range(1 << len(free))) == rec['min']; sc['py_exhaustive'] += 1
        if ENUMALL:
            import subprocess
            inp = '%d %d\n' % (v, len(free)) + ''.join('%d %d\n' % e for e in free) + ''.join(
                '%d %s\n%d %s\n' % (len(R_[j]), ' '.join(map(str, R_[j])), len(A_[j]), ' '.join(map(str, A_[j]))) for j in range(3))
            ok &= int(subprocess.run([ENUMALL, '0'], input=inp, capture_output=True, text=True, check=True).stdout.split()[0]) == rec['min']
        sc['exact'] += 1; special_mins.append(rec['min'] - v)
    report('7 special Pappus frame: %d sampled instances (seed %d): %d CR2-certified (rechecked), %d with no CR2 realisation '
           'over GF(2/4/8) (cr2.py DFS re-run, exhaustive) of which %d have recorded exact minima: witness costs (upper bounds) '
           'rechecked for all; lower bounds re-derived by pure-Python exhaustion for %d (f <= 18)%s; %d skipped f > 26'
           % (len(SI['instances']), SI['seed'], sc['cr2'], sc['exact'] + sc['skipped'], sc['exact'], sc['py_exhaustive'],
              ', and for all by replaying the vendored enumall' if ENUMALL else
              '; the other lower bounds are recorded enumall output (pass --enumall BIN to replay them)', sc['skipped']), ok)

    summary = dict(CR2_certified=n_cert + sc['cr2'], noCR2_GF2to8_exact=sc['exact'], skipped=sc['skipped'],
                   universal_frames=nframes)
    mins = special_mins
    expected = dict(CR2_certified=2652, noCR2_GF2to8_exact=18, skipped=70, universal_frames={'desargues': 221, 'pappus': 151})
    report('8 summary equals the recorded result (counts %s, min(cost - v) = 1, no cost < v)%s' % (
        expected, '' if ENUMALL else '; lower bounds for f = 19..26 are recorded enumall output in default mode'),
        summary == expected and bool(mins) and min(mins) == 1)
    print('   counts %s; min(cost - v) over the set with no CR2 realisation over GF(2/4/8) and f <= 26: %s  (%.1fs)'
          % (summary, min(mins) if mins else 'n/a',
             time.time() - T0))
    print('PASS_THREE_TOTAL_CLASSICAL_CONFIGS' if not BAD[0] else 'FAIL_THREE_TOTAL_CLASSICAL_CONFIGS (%d failures)' % BAD[0])
    sys.exit(1 if BAD[0] else 0)


if __name__ == '__main__':
    main()
