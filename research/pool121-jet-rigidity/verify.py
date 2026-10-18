"""Replay: first-order jet rigidity of the #2111 121-line pool (#1166 OPEN ENDS item 5b).
Usage (from the repository root): python3 -I -B research/pool121-jet-rigidity/verify.py [--full]
--full also re-runs the exhaustive 5-line enumeration (~70 s) and the CR2 DFS on its orbits (~7 min; 534 s total measured).
Exit 0 and a final 'PASS' line iff every check passes and every negative control fails as it must.
Stdlib only; no compiler needed (the exact minimum costs are recomputed in Python, independently of c/enumall.c).
Written for this package (thakrarsagar, with AI assistance from Claude Opus 5.5). Apache-2.0."""
import hashlib, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'lib'))
import jet as A  # implementation A (bitmask)  # noqa: E402
import indep as B  # implementation B (sparse sets), does not import jet  # noqa: E402
import cr2  # vendored from #2162  # noqa: E402
import order2 as O  # rigidity modulo trivial motions, #2162 order-2 test  # noqa: E402
import small  # exhaustive 4-line check  # noqa: E402

FAIL = []


def check(name, cond, detail=''):
    print(('PASS ' if cond else 'FAIL ') + name + ((' : ' + detail) if detail else ''), flush=True)
    if not cond:
        FAIL.append(name)


def sha(path):
    return hashlib.sha256(open(os.path.join(HERE, path), 'rb').read()).hexdigest()


def load(name):
    return json.load(open(os.path.join(HERE, 'data', name)))


def tup(lines):
    return [(tuple(p), tuple(q)) for p, q in lines]


def main():
    src = json.load(open(os.path.join(HERE, 'SOURCES.json')))
    for v in src['vendored']:
        check('V0 vendored %s sha256' % v['path'], sha(v['path']) == v['sha256'])

    # G1/G2: the pool, its incidences and the order-0 collapse
    PA, PB = A.pool(), B.the_pool()
    JA = A.Jet(PA)
    incB = B.incidences(PB)
    check('G1 pool: 13 vectors, 121 lines, same list in A and B', len(A.prim()) == 13 and len(PA) == 121 and
          PA == PB)
    check('G1 30 harmonic lines (A = B), 0 wild incidences, every incidence binomial (#2111 Lemma 1.1)',
          JA.harm == B.harmonic(PB) and len(JA.harm) == 30 and not JA.wild and
          all(len(D) == 2 for (_, _, D) in incB))
    ok0 = all(len(D) % 2 == 0 for (_, _, D) in incB) and all(
        (len(A.supp(p) & A.supp(q)) % 2 == 0) == (t in JA.harm) for t, (p, q) in enumerate(PA))
    check('G2 order 0: the forced collapse phi(+-1)=1 preserves all 2646 incidences; diagonal vanishes exactly on '
          'the 30 harmonic lines', ok0 and len(incB) == 2646)

    # G3: rank of (J1), two implementations
    rA = JA.eliminate()
    SB = B.Sparse([B.eq(*e) for e in incB])
    check('G3 (J1): 2646 rows, 510 unknowns, F2 rank 266 (A bitmask = B sparse)',
          len(JA.inc) == 2646 and JA.n == 510 == len(B.unknowns(PB)) and rA == 266 == SB.rank)

    # G4: solution space = explicit gauge + torus; delta'_t vanishes on it -> 30/30 immovable for every phi
    G = JA.gauge_torus()
    rowsA = JA.rows()
    annA = all(bin(r & g).count('1') % 2 == 0 for g in G for r in rowsA)
    names = {i: k for k, i in JA.var.items()}
    GB = [frozenset((('x' if names[i][0] == 'X' else 'y'), names[i][1], names[i][2])
                    for i in range(JA.n) if g >> i & 1) for g in G]
    annB = all(len(g & B.eq(*e)) % 2 == 0 for g in GB for e in incB)
    rG = A.rank_of(G)
    check('G4 the 2v+3 = 245 trivial motions (per-object scalings, torus F2^3) span dimension 244 = 510 - 266 '
          'and satisfy (J1) (A and B): solution space of (J1) = gauge + torus exactly',
          rG == 244 == B.Sparse(GB).rank and annA and annB and JA.n - rA == rG)
    dvan = all(bin(JA.delta(t) & g).count('1') % 2 == 0 for t in JA.harm for g in G)
    immA, immB = JA.immovable(), B.immovable(PB)
    check('G4 delta\'_t vanishes on gauge + torus for all 30 harmonic t; immovable 30/30 (A = B): Corollary J '
          'fails on the pool for every admissible phi and every field of characteristic 2',
          dvan and immA == immB == JA.harm)

    # G5: explicit Lemma F flows (dual witnesses, no elimination needed)
    fl = load('flows.json')['flows']
    okf = sorted(map(int, fl)) == JA.harm and all(
        B.flow_ok(PB, int(t), [tuple(e) for e in E]) and len(E) % 2 == 0 for t, E in fl.items())
    sizes = sorted(len(E) for E in fl.values())
    check('G5 30 Lemma F flows: every edge an incidence of the pool, rows sum to delta\'_t, even edge count',
          okf, 'flow sizes %d..%d' % (sizes[0], sizes[-1]))

    # G6: inclusion-minimal immovable atoms
    at = load('atoms.json')
    atoms = at['atoms']
    poolset = set(PA)
    canons = set()
    rows = []
    cr2_runs = 0
    bd_total = [0, 0]
    for a in atoms:
        L = tup(a['lines'])
        c = A.canon(L)
        new = c not in canons
        canons.add(c)
        inpool = all(l in poolset for l in L) and [PA.index(l) for l in L] == a['pool_lines']
        Ja = A.Jet(L)
        imm = Ja.immovable()
        immb = B.immovable(L)
        flows_ok = sorted(map(int, a['flow'])) == imm and all(
            B.flow_ok(L, int(t), [tuple(e) for e in E]) for t, E in a['flow'].items())
        minimal = all(not A.Jet(L[:u] + L[u + 1:]).immovable() and not B.immovable(L[:u] + L[u + 1:])
                      for u in range(len(L)))
        mins = []
        mc = B.min_cost(L, keep=mins)
        for on in mins:  # B-dependent first-order jet (VCR2 with E = supp B): (J1) only on the incidences in supp B
            bd_total[0] += 1
            sub = [r for (t, s, D), r in zip(Ja.inc, Ja.rows()) if (t, s) in on]
            if all(A.rank_of(sub + [Ja.delta(t)]) > A.rank_of(sub) for t in Ja.harm):
                bd_total[1] += 1
        cr = True
        if a['cr2'] == 'none over GF(2),GF(4),GF(8),GF(16)':
            pi = [A.supp(p) for p, q in L]
            sg = [A.supp(q) for p, q in L]
            E = {(t, s) for (t, s, D) in Ja.inc}
            for k in (1, 2, 3, 4):
                cr2_runs += 1
                if cr2.realise(pi, sg, E, k=k, limit=2 * 10 ** 6) is not None:
                    cr = False
        else:
            cr = False
        good = (new and inpool and imm and imm == immb == a['immovable'] and Ja.v == a['v'] and
                len(Ja.inc) == a['free_incidences'] and flows_ok and minimal and cr and
                mc == (a['min_cost'], a['num_minimisers']) and mc[0] >= Ja.v)
        rows.append((Ja.v, len(Ja.inc), len(Ja.harm), len(imm), a['orbit_size'], mc[0], mc[1], good))
        if not good:
            check('G6 atom %s' % a['pool_lines'], False)
    print('    atom table (v, free incidences, harmonic, immovable, orbit size, exact min cost, #minimisers):')
    by = {}
    for r in rows:
        by.setdefault(r[:7], 0)
        by[r[:7]] += 1
    for k in sorted(by):
        print('     v=%-2d f=%-2d harm=%d imm=%d orbit=%-2d mincost=%-2d (v+%d) minimisers=%-5d x%d' % (
            k[0], k[1], k[2], k[3], k[4], k[5], k[5] - k[0], k[6], by[k]))
    check('G6 %d distinct orbits (order-48 group) of inclusion-minimal immovable unit atoms: immovable (A = B, '
          'stored flows check), every one-line deletion jet-certifiable (A and B), not CR2 over GF(2),GF(4),GF(8),'
          'GF(16) (%d exhaustive DFS runs), exact min cost recomputed in Python = stored enumall value, min cost > v'
          % (len(atoms), cr2_runs), all(r[-1] for r in rows) and len(atoms) == at['meta']['distinct_orbits'] and
          all(r[5] > r[0] for r in rows), 'smallest v=%d, min(cost - v)=%d' % (
              min(r[0] for r in rows), min(r[5] - r[0] for r in rows)))

    check('G9 B-dependent first-order jet (#2162 VCR2 on E = supp B, as #2162 section 5) passes on every exact '
          'minimiser of every atom (%d of %d)' % (bd_total[1], bd_total[0]), bd_total[0] == bd_total[1] > 0)

    # G12: exhaustive smallest immovable sub-configurations
    reps, tested, bad = small.check_small(4)
    ex = at['meta']['exhaustive_size4']
    four = [a for a in atoms if a['v'] == 4]
    orbit4 = {A.canon([PA[i] for i in S]) for S in bad}
    harm_cover = len({pm[h] for h in reps for pm in small.harmonic_orbit_reps(PA, JA.harm)[1]}) == 30
    check('G12 exhaustive: all %d 4-subsets of the pool through one representative of each of the %d harmonic-line '
          'orbits tested; immovable ones: %s, one orbit = the stored v=4 atom; so no sub-configuration with <= 3 lines '
          'is immovable and the minimum size of a jet-immovable sub-configuration of the pool is 4' % (
              tested, len(reps), [list(b) for b in bad]),
          harm_cover and tested == ex['subsets_tested'] and [list(b) for b in bad] == ex['immovable'] and
          len(four) == 1 and orbit4 == {A.canon(tup(four[0]['lines']))})

    # G13: exhaustive classification of inclusion-minimal immovable 5-line sub-configurations (data/size5.json)
    s5 = load('size5.json')
    canon5 = set()
    ok5 = True
    dist = {}
    bdep = [0, 0]
    t5 = 0
    for o in s5['orbits']:
        L = [PA[i] for i in o['pool_lines']]
        c = A.canon(L)
        ok5 &= c not in canon5
        canon5.add(c)
        Jo = A.Jet(L)
        imm = Jo.immovable()
        ok5 &= bool(imm) and imm == B.immovable(L) == o['immovable'] and len(Jo.inc) == o['free_incidences']
        ok5 &= all(not A.Jet(L[:u] + L[u + 1:]).immovable() and not B.immovable(L[:u] + L[u + 1:]) for u in range(5))
        mins = []
        mc = B.min_cost(L, keep=mins)
        ok5 &= mc == (o['min_cost'], o['num_minimisers']) and mc[0] >= 5
        dist[mc[0] - 5] = dist.get(mc[0] - 5, 0) + 1
        if mc[0] == 5:
            t5 += 1
            for on in mins:
                sub = [r for (t, s, D), r in zip(Jo.inc, Jo.rows()) if (t, s) in on]
                bdep[0] += 1
                bdep[1] += all(A.rank_of(sub + [Jo.delta(t)]) > A.rank_of(sub) for t in Jo.harm)
        ok5 &= o['cr2'] == 'none over GF(2),GF(4),GF(8),GF(16)'
    check('G13 size-5 classification (data/size5.json): %d orbits, distinct, immovable (A = B), inclusion-minimal '
          '(A and B), exact min cost recomputed in Python = stored enumall value, all >= v; distribution of '
          'min cost - v: %s; %d tight orbits (cost = v = 5), B-dependent jet passes on %d of %d of their minimisers (consistency only, not a certificate); '
          'completeness and non-CR2 labels are recomputed only with --full'
          % (len(s5['orbits']), dict(sorted(dist.items())), t5, bdep[1], bdep[0]),
          ok5 and len(canon5) == len(s5['orbits']) and t5 > 0 and bdep[0] == bdep[1])
    check('G13 consistency: the greedy v=5 atoms of data/atoms.json are among the classified orbits',
          all(A.canon(tup(a['lines'])) in canon5 for a in atoms if a['v'] == 5))
    if '--full' in sys.argv:
        reps5, tested5, bad5 = small.check_small(5, minimal_only=True)
        orbs = {A.canon([PA[i] for i in S]) for S in bad5}
        check('G13 --full: exhaustive re-enumeration of all %d 5-subsets through the harmonic-orbit representatives '
              'gives exactly the stored %d orbits' % (tested5, len(orbs)),
              tested5 == s5['subsets_tested'] and orbs == canon5 and len(bad5) == s5['minimal_immovable_subsets'])
        ncr = 0
        for o in s5['orbits']:
            L = [PA[i] for i in o['pool_lines']]
            Jo = A.Jet(L)
            E = {(t, s) for (t, s, D) in Jo.inc}
            pi = [A.supp(p) for p, q in L]
            sg = [A.supp(q) for p, q in L]
            ncr += all(cr2.realise(pi, sg, E, k=k, limit=2 * 10 ** 6) is None for k in (1, 2, 3, 4))
        check('G13 --full: none of the %d orbits is CR2 over GF(2),GF(4),GF(8),GF(16) (exhaustive DFS)' % ncr,
              ncr == len(s5['orbits']))

    # G10/G11: rigidity modulo trivial motions (premise of Proposition R) and the #2162 section-5 order-2 test
    V = O.nullspace(rowsA, JA.n)
    check('G10 explicit F2 nullspace of (J1) on the pool: %d vectors, independent, all satisfy (J1)' % len(V),
          len(V) == 244 == A.rank_of(V) and all(bin(r & x).count('1') % 2 == 0 for x in V for r in rowsA))
    rig, o2, ctl = 0, 0, 0
    for a in atoms:
        Ja = A.Jet(tup(a['lines']))
        t = Ja.immovable()[0]
        rig += O.rigid(Ja)
        o2 += O.order2_vanishes(Ja, t)[0]
        ctl += not O.order2_vanishes(Ja, t, drop_diagonal=True)[0]
    check('G10 rigid atoms (solution space of (J1) = gauge + torus): %d of %d; Proposition R applies to these and to '
          'the pool' % (rig, len(atoms)), rig == 17 and O.rigid(JA))
    check('G11 order-2 test (#2162 section 5): Q_t vanishes identically on V for the immovable line of every atom '
          '(%d of %d), so order-2 jets fail on all atoms' % (o2, len(atoms)), o2 == len(atoms))
    check('N5 control: the same test with the X1(t).Y1(t) term dropped sees a nonzero form on %d of %d atoms'
          % (ctl, len(atoms)), ctl == len(atoms))
    check('G11 order-2 test on the pool: Q_t vanishes identically on V for all 30 harmonic lines (as Proposition R '
          'predicts)', all(O.order2_vanishes(JA, t, V=V)[0] for t in JA.harm))

    # G7: Q4 (search) and the exact all-non-harmonic statement
    q4 = load('q4.json')
    S = q4['best']
    LS = [PA[i] for i in S]
    certA, certB = not A.Jet(LS).immovable(), not B.immovable(LS)
    check('G7 Q4: stored S (|S| = %d, %d harmonic) has every harmonic line movable (A and B), so Corollary J gives '
          'cost(pool) >= cost(S) >= %d (restriction of an admissible B is admissible); below Theorem U 106 and MCC '
          '119; failed search for larger S' % (len(S), q4['best_harmonic'], len(S)), certA and certB and
          len(S) == 103)
    S2 = [PA[i] for i in range(121) if PA[i][0] not in ((0, 1, -1), (0, 1, 1))]
    check('G7 a second certifiable 103-line sub-pool: all lines whose point is not (0,1,-1) or (0,1,1) (A and B)',
          len(S2) == 103 and not A.Jet(S2).immovable() and not B.immovable(S2))
    NH = [t for t in range(121) if t not in JA.harm]
    check('G7 exact: the 91 non-harmonic lines are certifiable, but adding any one of the 30 harmonic lines makes '
          'that line immovable (A)', not A.Jet([PA[i] for i in NH]).immovable() and all(
              A.Jet([PA[i] for i in sorted(NH + [h])]).immovable() for h in JA.harm))

    # G8: positive control tied_min (#2111/#2162 Theorem T') is movable
    TM = [(A.normalise(tuple(p)), A.normalise(tuple(q))) for p, q in load('tied_min.json')]
    check('G8 positive control: tied_min = 12 pool lines, all harmonic, all movable (A and B) -> Corollary J '
          'applies (#2162 Theorem T\')', all(l in poolset for l in TM) and len(A.Jet(TM).harm) == 12 and
          not A.Jet(TM).immovable() and not B.immovable(TM))

    # Negative controls: each must make its check FAIL
    t0 = JA.harm[0]
    E0 = [tuple(e) for e in fl[str(t0)]]
    check('N1 control: flow of line %d with one edge dropped is rejected' % t0, not B.flow_ok(PB, t0, E0[1:]))
    a0, b0 = E0[0]
    bad = next(s for s in range(121) if A.dot(PA[a0][0], PA[s][1]) != 0 and s != a0)
    check('N2 control: flow with incidence (%d,%d) replaced by the non-incidence (%d,%d) is rejected' % (
        a0, b0, a0, bad), not B.flow_ok(PB, t0, [(a0, bad)] + E0[1:]))
    PC = list(PA)
    PC[JA.harm[0]] = (PA[JA.harm[0]][0], A.normalise((PA[JA.harm[0]][1][0], PA[JA.harm[0]][1][1], 0))
                      if PA[JA.harm[0]][1][2] else PA[JA.harm[0]][1])
    rC = A.Jet(PC).eliminate()
    check('N2 control: corrupted pool (q of line %d changed %s -> %s) changes the (J1) rank (%d != 266) or the flow '
          'check' % (JA.harm[0], PA[JA.harm[0]][1], PC[JA.harm[0]][1], rC),
          rC != 266 or not B.flow_ok(PC, t0, E0))
    F4 = cr2.GF(2)
    psi = {1: 1, -1: 2, 0: 0}  # psi(-1) = omega in GF(4): not a homomorphism (omega^2 != 1)
    broken = [(t, s) for (t, s, D) in incB if
              F4.dot([psi[x] for x in PA[t][0]], [psi[x] for x in PA[s][1]]) != 0]
    check('N3 control: wrong phi (psi(-1) = omega in GF(4)) breaks the order-0 incidences (%d of 2646 not preserved)'
          % len(broken), len(broken) > 0)
    L0 = tup(atoms[0]['lines'])
    check('N4 control: atom 0 with its first line deleted is jet-movable (no immovable line)',
          not A.Jet(L0[1:]).immovable() and not B.immovable(L0[1:]))

    if FAIL:
        print('FAIL (%d): %s' % (len(FAIL), FAIL))
        sys.exit(1)
    print('PASS pool121 jet rigidity: (J1) rank 266 / solution dim 244 (= gauge + torus) / 30 of 30 harmonic lines '
          'immovable with Lemma F flows; %d minimal immovable atom orbits (v %d..%d), all non-CR2 (GF(2..16)) with '
          'exact min cost >= v + 1, order-2 jets fail on all; minimum immovable size 4 (one orbit); %d minimal '
          '5-line orbits, all cost >= v, %d tight (cost = v); Q4 search best certifiable S = %d < 106 <= 119' % (
              len(atoms), min(r[0] for r in rows), max(r[0] for r in rows), len(s5['orbits']), t5, len(S)))


if __name__ == '__main__':
    main()
