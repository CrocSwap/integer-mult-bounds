"""Round-seven check, part 2 (stdlib only): every frame of the reordered word, exactly over Q.

The base frames (lifted node frames M_n, late-copy intersections, root frames t_T^perp and U_c) are rebuilt from the
witness with check_lifted.py's exact machinery. The design-B frames (deferred readout frames sigma_u, V-leaf starts
s_i) are the primitive integer bases of the data file. Checked:
 X. the frame dimensions recorded in the data file (node frames, late-copy intersections) equal the exact ones; every
    slot's node list moves along slot successors of the witness (gate uses and links, for which check_lifted.py proves
    nesting), its first node is where its start says, its last node reaches its root frame directly;
 Q. sigma_u <= F0(u) (the slot's start frame); sigma_u <= t_T^perp for every target of u (Z supports, a superset of
    the F2 supports); on every y_T the deferred levels are nested in time order (readout order); t_S <= s_i <= N_i
    (the first frame of the use); every X_S chain <t_S>, early V frames, deferred V frames, F is nested in time order;
    G = I - J/9 nondegenerate on every new frame (Gram determinant nonzero mod a prime, so nonzero over Z);
 S. side lemma at check_lifted's integer point (U, V of point(h, 1), the point of check_stair.py too): every distinct
    high-rank step (2r > h) of the reordered word that check_lifted.py does not already cover (slot starts, gauged
    corners sigma_u -> F, y_T and X_S chain steps, base steps that only the new schedule uses) has the generic
    north-east pivots under both conjugations, mod 2^31-1;
 F. the child-width histogram rebuilt from the exact dimensions (Z and F2 y supports), rank sum s = W m - N + L,
    moment certificate and kappa, with the round-six and the staircase entrance corners;
 N. negative controls: reversed readout order, readouts at F0(u) instead of sigma_u, perturbed sigma frames, X_S
    chains with the deferred V gates first, side lemma with U = V = I.
Usage: python3 check_frames.py [h]"""
import sys, os, time, random
from fractions import Fraction as Fr
from math import gcd
from collections import Counter, defaultdict
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.join(HERE, '..', '..', 'scripts'), os.path.join(HERE, '..', 'two-stage-bit')]
import check_lifted as cl
import deferred as dr
from linalg import null_exact, rank_mod, inv_mod_matrix, rightmost_pivots, predicted, Q31, Echelon

T0 = time.time()
def log(*a): print('[%5.0fs]' % (time.time() - T0), *a, flush=True)
OK = {}
def report(name, ok):
    OK[name] = bool(ok); log('%-100s %s' % (name, 'PASS' if ok else 'FAIL'))


def prim(r):
    r = [Fr(x) for x in r]; den = 1
    for x in r: den = den * x.denominator // gcd(den, x.denominator)
    z = [int(x * den) for x in r]; g = 0
    for x in z: g = gcd(g, x)
    return [x // g for x in z] if g else z


class ModQ7(cl.ModQ):
    """check_lifted's mod-q frames, extended by the design-B frames ('sigma', s) and ('v', s) (integer bases)."""
    def __init__(self, fr, ld, extra, control=False):
        super().__init__(fr, ld, control); self.extra = extra

    def basis(self, key):
        if key[0] in ('sigma', 'v') and key not in self.bcache:
            E = Echelon(self.q)
            for r in self.extra[key]: E.insert([x % self.q for x in r])
            if len(E.rows) != len(self.extra[key]): self.dimfail += 1
            self.bcache[key] = E.rows
        return super().basis(key)


def main(h=23):
    W, D = dr.load(h); S = dr.Schedule(W, D); trip = S.trip; tv = lambda T: [int(q in T) for q in range(h)]
    FULL = [[int(i == j) for j in range(h)] for i in range(h)]
    pr = cl.Prog(W); bas, dn = cl.spans(pr); users = cl.users_of(pr, dn)
    fr = cl.Frames(pr, dn, bas, users); fr.cobases(); d, _ = fr.dims(); ld, _ = cl.late_frames(fr, pr, users)
    log('exact base frames: %d node frames (%d lifted), %d late-copy intersections' % (len(d), len(pr.j), len(ld)))

    # ------------------------------------------------------------------ X. recorded dims, slot paths
    okd = all(S.node_dims[n] == d[n] for n in pr.act) and len(S.node_dims) == len(pr.act)
    okd &= all(S.late_dims[n, lt] == ld[('c', n, lt)] for (n, lt) in S.late_dims) and len(S.late_dims) == len(ld)
    report('X. recorded frame dims == exact dims (%d node frames, %d late-copy intersections)' % (len(d), len(ld)), okd)
    def ukey(n, k):
        u = users[n][k]; return ('n', u[1]) if u[0] == 'gate' else cl.root_key(u)
    badp = 0
    for s in range(S.R):
        hl = S.hold[s]
        for a, b in zip(hl, hl[1:]): badp += b not in fr.succ[a]
        root = [k for k in S.chain_keys(s) if k[0] in ('out', 'ret')]
        if root: badp += fr.rid[root[0]] not in fr.droots[hl[-1]]
        st = S.start[s]
        if st[0] == 'fresh':                                          # a copy starts at the use it serves
            nxt = ('n', hl[1]) if len(hl) > 1 else root[0]
            badp += ukey(hl[0], st[2]) != nxt
    report('X. every slot moves along slot successors of the witness, starts at its use, ends at its root (%d slots)' % S.R,
           badp == 0)

    # ------------------------------------------------------------------ exact frames
    _eb = {}
    def exact(key):
        if key not in _eb:
            k = key[0]
            if k == 'sigma': B = S.sigma[key[1]]
            elif k == 'v': B = S.vstart[key[1]]
            elif k == '0': B = []
            elif k == 'F': B = FULL
            elif k == 'c':
                n, lt = key[1], key[2]
                B = exact(ukey(n, lt[-1]))
                for kk in reversed(lt[:-1]): B = fr.intersect_exact(exact(ukey(n, kk)), B)
                B = [prim(r) for r in B]; assert len(B) == ld[key]
            else: B = [prim(r) for r in fr.exact_basis(key)]
            _eb[key] = B
        return _eb[key]
    _nz = {}
    def nullZ(B):
        kb = tuple(map(tuple, B))
        if kb not in _nz: _nz[kb] = [prim(z) for z in null_exact(B, h)] if B else FULL
        return _nz[kb]
    def inside(A, B):
        if not A or len(B) == h: return True
        return all(sum(a * z for a, z in zip(ra, rz)) == 0 for ra in A for rz in nullZ(B))
    def nondeg(B, p=Q31):                 # det(9 B G B^T) != 0 mod p  =>  != 0 over Z
        if not B or len(B) == h: return True
        sm = [sum(b) for b in B]
        Gr = [[9 * sum(x * y for x, y in zip(a, b)) - sa * sb for b, sb in zip(B, sm)] for a, sa in zip(B, sm)]
        return rank_mod(Gr, p) == len(B)
    gout = {T: [9 * x - 3 for x in tv(T)] for T in trip}
    tperp = lambda T: ('out', T[0], T)                    # t_T^perp is the root frame of every output (c, T)

    # ------------------------------------------------------------------ Q. exact facts
    indep = all(rank_mod(B, Q31) == len(B) for B in list(S.sigma.values()) + list(S.vstart.values()))
    report('Q. sigma_u and s_i bases independent (rank mod 2^31-1 == row count; %d + %d frames, max |entry| %d)' % (
        len(S.sigma), len(S.vstart), max(abs(x) for B in list(S.sigma.values()) + list(S.vstart.values()) for r in B for x in r)), indep)
    sel = S.readout; F0 = {s: S.start_key(s) for s in range(S.R)}
    report('Q. sigma_u <= F0(u) exactly (%d deferred slots)' % len(sel), all(inside(S.sigma[s], exact(F0[s])) for s in sel))
    CZ = S.adjoint(); CF = [{t: 1 for t, x in dd.items() if x % 2} for dd in CZ]
    capbad = sum(1 for s in sel for t in CZ[s] if any(sum(a * g for a, g in zip(r, gout[trip[t]])) for r in S.sigma[s]))
    report('Q. sigma_u <= t_T^perp exactly for every Z-support target (a superset of the F2 targets)', capbad == 0)
    def ychains(co, order, frame=lambda s: S.sigma[s], limit=None):
        byT = defaultdict(list)
        for s in order:
            for t in co[s]: byT[t].append(s)
        bad = 0; levels = {}
        for t, ss in list(byT.items())[:limit]:
            seq = [frame(s) for s in ss]
            for A, B in zip(seq, seq[1:]):
                if A is B: continue
                if len(A) > len(B) or not inside(A, B): bad += 1
            lv = []
            for s in ss:
                if not lv or S.f[lv[-1]] != S.f[s]: lv.append(s)
            levels[t] = lv
        return bad, levels
    bZ, levZ = ychains(CZ, sel); bF, levF = ychains(CF, sel)
    report('Q. deferred levels on every y_T nested in time order, exactly (Z targets %d bad, F2 targets %d bad)' % (bZ, bF),
           bZ == 0 and bF == 0)
    nd = sum(1 for B in list(S.sigma.values()) + list(S.vstart.values()) if not nondeg(B))
    report('Q. G nondegenerate on every sigma_u and s_i (Gram det != 0 mod 2^31-1 => over Z)', nd == 0)
    bad_t = bad_n = 0
    for s, n in S.srcop.items():
        bad_t += not inside([tv(trip[n - 1])], S.vstart[s])
        N1 = S.chain_keys(s)[2]                                       # first frame of the use after its start
        bad_n += not inside(S.vstart[s], exact(N1))
    report('Q. V leaves exactly: t_S <= s_i (%d bad), s_i <= N_i, the first frame of the use (%d bad), %d slots' % (
        bad_t, bad_n, len(S.srcop)), bad_t == bad_n == 0)
    def xchains(order_fn):
        bad = 0; steps = []
        for n, us in S.xs:
            seq = [[tv(trip[n - 1])]] + [S.vstart[s] for s in order_fn(us)] + [FULL]
            keys = [('n', n)] + [('v', s) for s in order_fn(us)] + [('F',)]
            for (A, ka), (B, kb) in zip(zip(seq, keys), zip(seq[1:], keys[1:])):
                if len(A) > len(B) or not inside(A, B): bad += 1
            steps.append(keys)
        return bad, steps
    bx, xkeys = xchains(lambda us: us)
    report('Q. X_S chains nested exactly in time order (<t_S>, early V gates, deferred V gates, F; %d leaves)' % len(S.xs), bx == 0)

    # ------------------------------------------------------------------ S. side lemma on the new high-rank steps
    ops0, chains0, _, R0 = cl.compile_(pr, dn, users)
    def dimof0(k):
        if k == ('0',): return 0
        if k == ('F',): return h
        if k[0] in ('out', 'ret'): return h - 1
        if k[0] == 'c': return ld[k]
        return d[k[1]]
    _, base_steps = cl.chain_steps(chains0, dimof0, h)
    base_frames = {k for e in base_steps for k in e}
    def dimx(k): return len(exact(k)) if k[0] in ('sigma', 'v') else dimof0(k)
    new = {}
    def add_chain(keys, kind):
        prev = keys[0]; pd = dimx(prev)
        for k in keys[1:]:
            dk = dimx(k)
            if dk > pd:
                if (prev, k) not in base_steps and 2 * (dk - pd) > h: new.setdefault((prev, k), (dk - pd, kind))
                prev, pd = k, dk
            else: prev = k
    for s in range(S.R):
        add_chain(S.chain_keys(s), 'slot')
        if S.f[s]: add_chain([('sigma', s), ('F',)], 'corner')
    for t, lv in levZ.items():
        add_chain([('0',)] + [('sigma', s) for s in lv] + [tperp(trip[t])], 'ydata')
    for t, lv in levF.items():
        add_chain([('0',)] + [('sigma', s) for s in lv] + [tperp(trip[t])], 'ydata')
    for keys in xkeys: add_chain(keys, 'xdata')
    extra = {('sigma', s): B for s, B in S.sigma.items()}; extra.update({('v', s): B for s, B in S.vstart.items()})
    mq = ModQ7(fr, ld, extra)
    used = {k for e in new for k in e} - base_frames
    ndq = sum(1 for k in used if not mq.nondeg(k))
    report('S. frames used only by the new steps: %d, G-degenerate mod 2^31-1 %d, reduction dimension mismatches %d' % (
        len(used), ndq, mq.dimfail), ndq == 0 and mq.dimfail == 0)
    pr_ = predicted(h); q = mq.q
    def lemma(items, m):
        bad = 0
        for (A, B), (r, _) in items:
            QA, QB = m.conjugated(A), m.conjugated(B)
            for t in range(2):
                a, b = QA[t], QB[t]
                M = [[(b[i * h + c] - a[i * h + c]) % q for c in range(h)] for i in range(h)]
                if rightmost_pivots(M, q) != pr_[r]: bad += 1
        return bad
    items = sorted(new.items(), key=lambda e: (str(e[0][1]), str(e[0][0])))
    badL = lemma(items, mq)
    report('S. side lemma (generic NE pivots, both conjugations, mod 2^31-1) on all %d new high-rank steps %s' % (
        len(items), dict(Counter(k for _, k in new.values()))), badL == 0)

    # ------------------------------------------------------------------ F. histogram from exact dims
    import moment
    from certificate_round3 import evaluate
    def dim_exact(k): return dimx(k)
    rk = dr.chain_ranks(S, dim_exact)
    xd = S.xdata(lambda s: len(exact(('v', s))))
    okx = all(sum(x) == h - 1 for x in xd)
    ylZ = S.ylevels(CZ); ylF = {t: sorted({S.f[s] for s in sel if t in CF[s]}) for t in range(S.v)}
    res = {}
    for corner_name, corner in (('round-six corner', dr.ROUND6_CORNER(h)), ('staircase corner', dr.STAIRCASE_CORNER(h))):
        for yname, yl in (('Z', ylZ), ('F2', ylF)):
            c = dr.histogram(S, rk, yl, xd, corner)
            rs = sum(w * n for w, n in c['hist'].items())
            a, _ = moment.certify(c)
            k = evaluate(a, Fr(36926111, 5 * 10**11), Fr(1, 1000), 'crude', m_c=576, s_c=119453132304)
            res[corner_name, yname] = (a, k['kappa'], k['ok'], rs == c['s'] and max(c['hist']) < c['m'])
    for corner_name in ('round-six corner', 'staircase corner'):
        (aZ, kZ, oZ, sZ), (aF, kF, oF, sF) = res[corner_name, 'Z'], res[corner_name, 'F2']
        report('F. %s: rank sum == s (Z and F2 y supports), a_b = %s (%.6e), kappa = %s (%.7e) ok=%s, F2 a_b = %s' % (
            corner_name, aZ, float(aZ), kZ, float(kZ), oZ, aF), sZ and sF and oZ and oF and okx)
    report('F. claims: a_b 12599/200000000, kappa 6299103187973/10^17; staircase a_b 31987/500000000, kappa 1599247689723/(2.5*10^16)',
           res['round-six corner', 'Z'][:2] == (Fr(12599, 200000000), Fr(6299103187973, 10**17)) and
           res['staircase corner', 'Z'][:2] == (Fr(31987, 500000000), Fr(1599247689723, 25 * 10**15)))

    # ------------------------------------------------------------------ N. negative controls
    bZr, _ = ychains(CZ, list(reversed(sel)))
    report('N. NEG reversed readout order breaks the y_T chains (%d bad)' % bZr, bZr > 0)
    bF0, _ = ychains(CF, sorted(sel, key=lambda s: (dimx(F0[s]), s)), frame=lambda s: exact(F0[s]), limit=300)
    report('N. NEG readouts at F0(u) instead of sigma_u break the y_T chains (%d breaks on 300 targets)' % bF0, bF0 > 0)
    rng = random.Random(5); pert = tot = 0
    for s in [s for s in sel if dimx(F0[s]) < h][:200]:
        B = [r[:] for r in S.sigma[s]]; B[0] = [x + rng.randint(1, 3) for x in B[0]]; tot += 1
        pert += not inside(B, exact(F0[s]))
    report('N. NEG perturbed sigma frames fail sigma <= F0 (%d / %d)' % (pert, tot), tot and pert >= 0.9 * tot)
    early = set(S.srcop) - S.sel
    bxr, _ = xchains(lambda us: [s for s in us if s not in early] + [s for s in us if s in early])
    report('N. NEG deferred V gates before the early ones break the X_S chains (%d bad)' % bxr, bxr > 0)
    mq0 = ModQ7(fr, ld, extra, control=True)
    badc = lemma(items[:300], mq0)
    report('N. NEG side lemma with U = V = I fails (%d / %d)' % (badc, 2 * min(300, len(items))), badc > 0)
    log('ALL %s' % ('PASS' if all(OK.values()) else 'FAIL: ' + str([k for k, x in OK.items() if not x])))
    return all(OK.values())


if __name__ == '__main__':
    sys.exit(0 if main(int(sys.argv[1]) if len(sys.argv) > 1 else 23) else 1)
