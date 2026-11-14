"""P104 methods: ABSORPTION (a helper settles a relay's residue against another register's outstanding junk, not against Y).

Standard library only, exact Fractions. Sources (own lane code, ported): UBUS (section 0.1 mechanism, section 2 algebra and
legality), ABSORBAUDIT (section 1), ABSORBLIFT (section 3, alg_absorb.py: sigma-anchor schedule), LTOKEN (section 0.4,
t2.py/eng.py: last-outstanding-cell rule).

Contract per port (toy): X = x - y, Y = x.  Geometry A_m: ports q_ij = e_i + e_j + e_{m+1}, roots e_i - e_j, G = Gram (rank m),
partner cells (p,t) = {p != t, G_pt odd}, Z = G/2 - I on partner cells, n = #roots, r = m, n - r = GLIFT charge deficiency.

SCOPE.  Part 1 is the exact absorption identity on random instances.  Parts 2 and 3 are the FRAME-FREE ALGEBRA on the toys
A3 (n=6, r=3) and A4 (n=10, r=4): NO frame legality is checked here and E8 is NOT simulated.  The lane's frame-legality replay on
real E8 ports (ABSORBAUDIT replay.py) and the E8 statements are quoted, not reproduced.

Checked:
  1. identity: H = h + sum_t (sum_r d_r psi_rt - lambda_t) y_t exactly on 40 random instances; H clean iff lambda = sum d psi;
     controls: coefficient x2 and dropped lump leave H dirty; dropped absorb ADD leaves H dirty;
  2. sigma-anchor algebra (one early pure-anchor relay per column from the parked pure copy, one late direct reference cell per
     column, every other cell absorbed): D = 0 and Y exact on A3 (3 seeds x 3 absorb timings + mid-read + d = 3/7) and A4
     (2 seeds x 3 timings); controls: no sigma (all settled) D = n - r (3 / 6), absorb ADD dropped D = n - r, coefficient x2
     D = n - r;
  3. last-outstanding-cell rule: random absorb time D = n - r on 5/5 A3 seeds (the lane's seeds), with the rule D = 0 on 5/5.
Prints PASS_METHODS_ABSORPTION."""
import itertools, random, sys
from fractions import Fraction as Fr


def say(s):
    print(s, flush=True)


def expect(name, got, want):
    if got != want:
        raise SystemExit('FAIL %s: got %r want %r' % (name, got, want))
    say('ok  %s: %r' % (name, got))


def rank(rows):
    """Exact rank of a list of sparse rows {key: Fraction}."""
    piv = {}
    r = 0
    for row in rows:
        v = {k: Fr(x) for k, x in row.items() if x}
        while v:
            k = min(v)
            if k in piv:
                c = v[k]
                for kk, xx in piv[k].items():
                    nv = v.get(kk, 0) - c * xx
                    if nv:
                        v[kk] = nv
                    else:
                        v.pop(kk, None)
            else:
                c = v[k]
                piv[k] = {kk: xx / c for kk, xx in v.items()}
                r += 1
                break
    return r


def geometry(m):
    pairs = list(itertools.combinations(range(m + 1), 2))
    roots = [[(1 if k == i else -1 if k == j else 0) for k in range(m + 1)] for i, j in pairs]
    ports = [(1 << i) | (1 << j) | (1 << (m + 1)) for i, j in pairs]
    n = len(roots)
    G = [[sum(a * b for a, b in zip(roots[s], roots[t])) for t in range(n)] for s in range(n)]
    B = [[Fr(r[k]) for k in range(m)] for r in roots]
    IJ = [[Fr(1 + (a == b)) for b in range(m)] for a in range(m)]
    C = [[sum(B[t][a] * IJ[a][j] for a in range(m)) / 2 for j in range(m)] for t in range(n)]
    for s in range(n):
        for t in range(n):
            assert sum(C[s][j] * B[t][j] for j in range(m)) == Fr(G[s][t], 2)
            even_label = bin(ports[s] & ports[t]).count('1') % 2 == 0
            assert (G[s][t] % 2 == 1) == (s != t and even_label)
    Z = {(s, t): Fr(G[s][t], 2) for s in range(n) for t in range(n) if s != t and G[s][t] % 2}
    return n, G, B, C, Z


# ------------------------------------------------------------------------------------------------ part 1: the identity
def vadd(d, c, s):
    for k, v in s.items():
        nv = d.get(k, 0) + c * v
        if nv:
            d[k] = nv
        else:
            d.pop(k, None)


def absorption_instance(rng, nr, nt, lam_mode='match', mult=1, drop_lump=False, drop_absorb=False):
    """Helper H = h.  Lump -lambda.y at {0}; at K: H += sum d_r X_r(tau_K) ; at V: H -= sum d_r X_r^final.
    X_r(tau) = xf_r + sum_t psi_rt y_t  (junk in the y coordinates it will later be cleaned against).
    Returns (H as dict, expected dirt dict, lam, d, psi)."""
    psi = [[Fr(rng.randint(-5, 5), rng.randint(1, 4)) for _ in range(nt)] for _ in range(nr)]
    d = [Fr(rng.randint(1, 6), rng.randint(1, 3)) for _ in range(nr)]
    lam = [sum(d[r] * psi[r][t] for r in range(nr)) for t in range(nt)]
    if lam_mode == 'random':
        lam = [Fr(rng.randint(-5, 5)) for _ in range(nt)]
    H = {'h': Fr(1)}
    if not drop_lump:
        for t in range(nt):
            vadd(H, -lam[t], {'y%d' % t: Fr(1)})
    X_K = [dict({'xf%d' % r: Fr(1)}, **{'y%d' % t: psi[r][t] for t in range(nt) if psi[r][t]}) for r in range(nr)]
    X_f = [{'xf%d' % r: Fr(1)} for r in range(nr)]
    if not drop_absorb:
        for r in range(nr):
            vadd(H, mult * d[r], X_K[r])
    for r in range(nr):
        vadd(H, -d[r], X_f[r])
    pred = {'h': Fr(1)}
    for t in range(nt):
        c = sum(d[r] * psi[r][t] for r in range(nr)) - lam[t]
        if c:
            pred['y%d' % t] = c
    return H, pred, lam, d, psi


def part1():
    rng = random.Random(11)
    ok_clean = ok_ident = 0
    for i in range(40):
        nr, nt = rng.randint(1, 4), rng.randint(1, 5)
        H, pred, lam, d, psi = absorption_instance(rng, nr, nt)
        assert H == {'h': Fr(1)}
        ok_clean += 1
        # identity for an arbitrary lambda: H = h + sum_t (sum d psi - lambda_t) y_t
        rng2 = random.Random(1000 + i)
        H2, pred2, lam2, d2, psi2 = absorption_instance(rng2, nr, nt, lam_mode='random')
        assert H2 == pred2
        ok_ident += 1
    expect('identity H = h + sum_t(sum_r d_r psi_rt - lambda_t) y_t on random lambda', ok_ident, 40)
    expect('H ends clean when lambda = sum_r d_r psi_r', ok_clean, 40)
    dirty = {'x2': 0, 'nolump': 0, 'noabs': 0}
    for i in range(40):
        nr, nt = rng.randint(1, 4), rng.randint(1, 5)
        if absorption_instance(random.Random(i), nr, nt, mult=2)[0] != {'h': Fr(1)}:
            dirty['x2'] += 1
        if absorption_instance(random.Random(i), nr, nt, drop_lump=True)[0] != {'h': Fr(1)}:
            dirty['nolump'] += 1
        if absorption_instance(random.Random(i), nr, nt, drop_absorb=True)[0] != {'h': Fr(1)}:
            dirty['noabs'] += 1
    # an instance can have psi all zero (then even a dropped item is harmless); require dirt on most, none clean-by-error
    expect('control coefficient x2: H dirty on all 40', dirty['x2'], 40)
    expect('control dropped lump: H dirty on all 40', dirty['nolump'], 40)
    expect('control dropped absorb ADD: H dirty on all 40', dirty['noabs'], 40)


# ------------------------------------------------------------------------------------------------ parts 2-3: sigma-anchor algebra
def pick_maps(m, seed):
    n, G, B, C, Z = geometry(m)
    part = {t: [p for p in range(n) if (p, t) in Z] for t in range(n)}
    rng = random.Random(seed)
    for _ in range(20000):
        cols = list(range(n))
        rng.shuffle(cols)
        u1, u2, sig, ref, ok = set(), set(), {}, {}, True
        for t in cols:
            c = [p for p in part[t] if p not in u1]
            if not c:
                ok = False
                break
            sig[t] = rng.choice(c)
            u1.add(sig[t])
            c = [p for p in part[t] if p not in u2 and p != sig[t]]
            if not c:
                ok = False
                break
            ref[t] = rng.choice(c)
            u2.add(ref[t])
        if ok:
            return sig, ref
    raise SystemExit('no sigma/ref maps')


def run(m, seed, abs_when='pre_anchor', read_when='late', mode='sigma', dco=Fr(1), mult=1, noabs=False, order=None):
    """Frame-free algebra of ABSORBLIFT alg_absorb.py (exact Fractions).  order in (None, 'random', 'rule'): if given, the
    X reads / absorbs / E re-adds / L second reads / direct reads form a random linear extension of the stated constraints."""
    n, G, B, C, Z = geometry(m)
    r = m
    sig, rf = pick_maps(m, seed)
    part = {t: [p for p in range(n) if (p, t) in Z] for t in range(n)}
    E = {(sig[t], t) for t in range(n)} if mode == 'sigma' else set()
    direct = {(rf[t], t) for t in range(n)}
    absd = {(p, t): rf[t] for (p, t) in Z if (p, t) not in direct and (p, t) not in {(sig[t], t) for t in range(n)}}
    rel = {k: 'R%d_%d' % k for k in Z if k not in direct and k not in absd}
    ab = {k: 'A%d_%d' % k for k in absd}
    hel = {(t, p): 'H%d_%d' % (t, p) for (t, p) in Z}
    X = ['X%d' % p for p in range(n)]
    Y = ['Y%d' % t for t in range(n)]
    pub, own = {}, {}
    for p in range(n):
        pub[X[p]] = {'x%d' % p: Fr(1)}
    for t in range(n):
        pub[Y[t]] = {'y%d' % t: Fr(1)}
    for v in list(rel.values()) + list(ab.values()) + list(hel.values()):
        pub[v] = {v: Fr(1)}
    reg = lambda nm: pub[nm] if nm in pub else own[nm]

    def add(d, c, s):
        vadd(reg(d), c, dict(reg(s)))
    U = ['U%d' % j for j in range(r)]
    L = ['L%d' % j for j in range(r)]
    for j in range(r):
        own[U[j]] = {}
        for t in range(n):
            add(U[j], B[t][j], Y[t])
    for (p, t), R in rel.items():
        add(R, -1, Y[t])
    for (p, t), A in ab.items():
        add(A, dco * Z[(absd[(p, t)], t)], Y[t])                      # absorber lump (pure y_t)
    for (t, p), H in hel.items():
        add(H, -1, Y[p])
    for t in range(n):
        own['O%d' % t] = {}
        add('O%d' % t, 1, Y[t])                                         # parked pure anchor copy
    for j in range(r):
        own[L[j]] = {}
        for s in range(n):
            add(L[j], B[s][j], X[s])
    for t in range(n):
        add(Y[t], -1, 'O%d' % t)                                        # zero-Y (park)
    for (t, p), H in hel.items():
        add(Y[t], Z[(t, p)], H)
    for j in range(r):
        for t in range(n):
            add(Y[t], C[t][j], L[j])
    for (t, p), H in hel.items():
        add(H, 1, X[p])                                                 # L helper picks up pure x_p
    # ---- the late phase as events
    ev = []
    for (p, t) in rel:
        ev.append(('read', (p, t)))
    for (p, t) in ab:
        ev.append(('read', (p, t)))
    for (p, t) in ab:
        ev.append(('abs', (p, t)))
    for (p, t) in rel:
        if (p, t) in E:
            ev.append(('readd', (p, t)))
    for k in hel:
        ev.append(('l2', k))
    for k in direct:
        ev.append(('dread', k))

    def do(e):
        k, c = e
        if k == 'read':
            p, t = c
            if c in rel:
                add(X[p], -Z[c], rel[c])
            else:
                add(X[p], Z[c] / (dco * Z[(absd[c], t)]), ab[c])
        elif k == 'abs':
            if not noabs:
                add(ab[c], dco * mult, X[absd[c]])
        elif k == 'readd':
            add(rel[c], 1, 'O%d' % c[1])
        elif k == 'l2':
            t, p = c
            add(Y[t], -Z[(t, p)], hel[c])
        elif k == 'dread':
            q, t = c
            add(X[q], Z[(q, t)], Y[t])
    if order is None:
        # ABSORBLIFT fixed schedules
        reads = [e for e in ev if e[0] == 'read']
        absl = [e for e in ev if e[0] == 'abs']
        readd = [e for e in ev if e[0] == 'readd']
        l2 = [e for e in ev if e[0] == 'l2']
        dr = [e for e in ev if e[0] == 'dread']
        seq = reads
        if abs_when == 'pre_anchor':
            seq = seq + absl + readd
        else:
            seq = seq + readd + (absl if abs_when == 'post_anchor' else [])
        if read_when == 'mid':
            seq = seq + dr
        seq = seq + l2
        if abs_when == 'late':
            seq = seq + absl
        if read_when == 'late':
            seq = seq + dr
        for e in seq:
            do(e)
    else:
        rng = random.Random(10 * seed + 7)
        done = set()

        def ready(e):
            k, c = e
            if k == 'abs':
                if ('read', c) not in done:
                    return False
                if order == 'rule':
                    rr, t = absd[c], c[1]
                    others = [('read', (rr, u)) for u in part[rr] if u != t and (rr, u) in rel or
                              u != t and (rr, u) in ab]
                    return all(o in done for o in others)
                return True
            if k == 'readd':
                return ('read', c) in done
            if k == 'dread':
                q, t = c
                return all(('abs', a) in done for a, rr in absd.items() if rr == q and a[1] == t)
            return True
        while len(done) < len(ev):
            av = [e for e in ev if e not in done and ready(e)]
            e = rng.choice(av)
            do(e)
            done.add(e)
    # settled re-adds (mode != sigma only)
    for (p, t), R in rel.items():
        if (p, t) not in E:
            add(R, 1, Y[t])
    T = {}
    for p in range(n):
        T[X[p]] = {'x%d' % p: Fr(1), 'y%d' % p: Fr(-1)}
    for t in range(n):
        T[Y[t]] = {'x%d' % t: Fr(1)}
    Vregs = X + list(rel.values()) + list(ab.values()) + list(hel.values())
    for v in Vregs[n:]:
        T[v] = {v: Fr(1)}
    arr = [pub[v] for v in Vregs] + [own[u] for u in U]
    D = rank(arr + [T[v] for v in Vregs]) - rank(arr)
    Yok = all(pub[Y[t]] == T[Y[t]] for t in range(n))
    return dict(D=D, Y=Yok, absorbed=len(ab), early=len(E), direct=len(direct), relays=len(rel), n=n, r=r)


def part2():
    for m, seeds in ((3, range(3)), (4, range(2))):
        nm = 'A%d' % m
        n_r = None
        for seed in seeds:
            for aw in ('pre_anchor', 'post_anchor', 'late'):
                o = run(m, seed, aw, 'late')
                n_r = o['n'] - o['r']
                if o['D'] != 0 or not o['Y']:
                    raise SystemExit('FAIL %s seed %d %s: %r' % (nm, seed, aw, o))
        o = run(m, 0, 'pre_anchor', 'late')
        say('ok  %s sigma-anchor schedule: D = 0, Y exact in %d/%d runs (%d absorbed / %d early / %d direct of %d cells)' % (
            nm, 3 * len(seeds), 3 * len(seeds), o['absorbed'], o['early'], o['direct'], o['absorbed'] + o['early'] + o['direct']))
        if m == 3:
            o = run(m, 0, 'pre_anchor', 'mid')
            expect('A3 direct read in the middle: D', (o['D'], o['Y']), (0, True))
            o = run(m, 0, 'pre_anchor', 'late', dco=Fr(3, 7))
            expect('A3 absorber scale d = 3/7: D', (o['D'], o['Y']), (0, True))
        o = run(m, 0, 'pre_anchor', 'late', mode='settled')
        expect('%s control no sigma (all settled): D = n - r' % nm, o['D'], n_r)
        o = run(m, 0, 'pre_anchor', 'late', noabs=True)
        expect('%s control absorb ADD dropped: D = n - r' % nm, o['D'], n_r)
        o = run(m, 0, 'pre_anchor', 'late', mult=2)
        expect('%s control absorb coefficient x2: D = n - r' % nm, o['D'], n_r)


def part3():
    dr, dl = [], []
    for seed in range(5):
        dr.append(run(3, seed, order='random')['D'])
        dl.append(run(3, seed, order='rule')['D'])
    say('random absorb time (A3 seeds 0-4): D = %r ; with last-outstanding-cell rule: D = %r' % (dr, dl))
    expect('last-outstanding-cell rule: D = 0 on 5/5 seeds', dl, [0] * 5)
    expect('random absorb time: D = n - r = 3 on 5/5 seeds', dr, [3] * 5)


def main():
    say('Part 1: absorption identity (exact, random instances)')
    part1()
    say('Part 2: FRAME-FREE ALGEBRA on toys A3/A4 (no frame legality is checked; E8 is not simulated)')
    part2()
    say('Part 3: last-outstanding-cell rule (frame-free algebra, A3)')
    part3()
    say('Quoted, NOT reproduced here: UBUS in-model U floor 4,176 -> 609 D0/call [lane LP]; ABSORBAUDIT E8 legality replay;'
        ' GLIFT n - r bill without anchors on E8 = 96 units (~25k D0/call); 23:1 splits on 4,224 of 4,992 dim-2 stops.')
    say('PASS_METHODS_ABSORPTION')


if __name__ == '__main__':
    main()
