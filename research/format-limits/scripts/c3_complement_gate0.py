"""Exact checks for complement (oblique) sinks: the sink hyperplane w^perp with w odd and w.u = 1 for a rank-1 source <u>.

Notation.  Labels are vectors of F2^n with the standard dot product; u is odd (u.u = 1).  For a subspace F, T_F is the
canonical Clifford frame operator of F (T_0 = identity, T_FULL = F = the Fourier transform on all n axes, "C^(x)n"),
and  d(A, B) = dim A + dim B - 2 dim(A cap B)  is the frame distance.  The Clifford rank of an operator is the rank
reported by clifford_exact.lower_child (rank of the Fourier part of its normal form).  A monomial operator is an
address-linear permutation times a Z4 diagonal phase times a translation times a global phase.  A weight-odd vector w
is a COMPLEMENT of u when w.u = 1, i.e. u is not in w^perp, so that F2^n = <u> (+) w^perp.

(E) Endpoint.  For every odd w with w.u = 1 the route R = T_{w^perp} T_<u>^{-1} has Clifford rank n, and
    R = Lmon . F . Rmon  with Lmon, Rmon monomial (Rmon acts first): the explicit check is
    Lmon^{-1} R Rmon^{-1} == F  on the Clifford tableau and on every basis column (n <= 6; 6 sampled columns at n = 9).
    Controls: w = u (the format's own sink u^perp) has the same property; a non-complement w (w.u = 0, so u is in
    w^perp) gives rank n - 2.  The wrapper class of each monomial is reported as 'id' or 'perm' (trivial or nontrivial
    address map) plus '+quad' if its phase has an off-diagonal (quadratic) part: Lmon is always 'perm+quad', Rmon has
    trivial address map ('id', or 'id+quad').
(P) Port price.  A target (Y) climbing 0 -> w^perp costs n - 1 = d(0, w^perp), the same as 0 -> u^perp; a source (X)
    climbing <u> -> FULL costs n - 1.  A detour station G (Y: 0 -> G -> w^perp) costs +0 exactly when G <= w^perp and
    exactly +2 otherwise (exhaustive over all subspaces G, n = 3, 4, 5).
(N) Newly lossless corrector.  A source with label s, s.u = 1 and s.w = 0 cannot be read drop-free by the sink u^perp
    (s is not in u^perp) but lies on the geodesic of the sink w^perp.  Network on two registers: the target y climbs
    0 -> <s> (read c * x there, c = 1/2) -> w^perp ; the source x climbs <s> -> FULL.  The operator is
    x -> T_FULL l_x ,  y -> T_{w^perp}(l_y + c l_x)  (exact on every basis column of x and sampled columns of y, with
    exact Gaussian-dyadic arithmetic), and every step's child rank equals d(A, B) (n = 3, 4, 5).
"""
import random
import sys
from fractions import Fraction as Fr

from report import check, finish, main_file

sys.path.insert(0, str(main_file('research/direct-delivery504-global/vendor/clifford/clifford_exact.py').parent))
import clifford_exact as ce  # noqa: E402  (the repository's exact Clifford compiler, unmodified)

# ----------------------------------------------------------------------------------------------------------------
# Expected values (from the exact run; every one is re-derived below and compared).
# ENDPOINT[n]: histogram of (kind, Clifford rank, tableau equal to F, columns equal to F, Lmon class, Rmon class) over
# the odd w tested (kind 'compl': w.u = 1, 'noncompl': w.u = 0, 'u': w = u).  For n <= 6 every odd w is tested;
# for n = 9 a sample of 160 vectors w (random.Random(1), same draw sequence as the run below) plus w = u is tested, so
# the counts at n = 9 (41 complements, 50 non-complements, w = u drawn twice) are properties of that seeded sample.

def _hist(n, n_id, n_idq, n_non, n_u):
    h = {('compl', n, True, True, 'perm+quad', 'id'): n_id, ('compl', n, True, True, 'perm+quad', 'id+quad'): n_idq,
         ('u', n, True, True, 'perm+quad', 'id+quad'): n_u}
    if n_non:
        h[('noncompl', n - 2, None, None, None, None)] = n_non     # control w.u = 0: rank n - 2
    return h


ENDPOINT = {3: _hist(3, 1, 2, 0, 1), 4: _hist(4, 1, 2, 4, 1), 5: _hist(5, 1, 6, 8, 1), 6: _hist(6, 1, 14, 16, 1),
            9: _hist(9, 1, 40, 50, 2)}
PORT_PRICE = {n: n - 1 for n in (3, 4, 5, 6, 9)}        # Y 0->w^perp, Y 0->u^perp, X <u>->FULL all cost n - 1
INTERVAL_SUBSPACES = {3: 16, 4: 67, 5: 374}              # number of subspaces of F2^n, all with zero violations
CORRECTOR = {3: dict(s=0b010, charged=4), 4: dict(s=0b0010, charged=6), 5: dict(s=0b00010, charged=8)}  # charged = 2(n-1)


def par(x):
    return bin(x).count('1') & 1


def basis(vs, n):
    b = []
    for v in vs:
        if ce.rank(b + [v]) > len(b):
            b.append(v)
    return b


def perp(vs, n):
    return [z for z in range(1, 1 << n) if all(par(z & v) == 0 for v in vs)]


def hyper(w, n):
    """a basis of w^perp."""
    return basis(perp([w], n), n)


def T(n, U):
    return ce.canonical_frame(n, tuple(U))


def d(A, B):
    a, b = len(A), len(B)
    return a + b - 2 * (a + b - ce.rank(A + B))


def opstep(n, A, B):
    """the operator T_B T_A^{-1} (T_A^{-1} is applied first)."""
    return (T(n, A).adjoint().then(T(n, B))) if A else T(n, B)


def rk(op):
    return ce.lower_child(op)[0]['rank']


def lower_ops(op):
    """clifford_exact.lower_child, but also returning the monomial operators:
    op == rmon.then(fourier(n, range(r))).then(lmon)  (rmon acts first); returns (r, lmon, rmon, lrec, rrec)."""
    n = op.n
    Bcols = [x for x, z, p in op.tab[n:]]
    r = ce.rank(Bcols)
    G = ce.transpose(ce.basis_extend(Bcols, n), n)
    A = ce.inv(G, n)
    PA = ce.perm(n, A)
    part = op.then(PA)
    Bcols = [x for x, z, p in part.tab[n:]]
    Dcols = [z for x, z, p in part.tab[n:]]
    picks = []
    sel = []
    for j, x in enumerate(Bcols):
        if ce.rank(sel + [x]) > len(sel):
            picks.append(j)
            sel.append(x)
    Br = ce.transpose(sel, r)
    Bi = ce.inv(Br, r)
    Dr = ce.transpose([Dcols[j] & ((1 << r) - 1) for j in picks], r)
    Qs = tuple(sum(ce.parity(row & col) << j for j, col in enumerate(ce.transpose(Bi, r))) for row in Dr)
    DQ = ce.diag(n, Qs + (0,) * (n - r))
    V = part.then(DQ).then(ce.hadamard(n, range(r)))
    Vmon, _ = ce.monomial(V)
    S = ce.diag(n, tuple(1 << i if i < r else 0 for i in range(n)))
    left = S.adjoint().then(DQ.adjoint()).then(PA.adjoint())
    right = Vmon.then(S.adjoint()).then(ce.xgate(n, (1 << r) - 1))
    lmon, lrec = ce.monomial(left)
    rmon, rrec = ce.monomial(right)
    comp = rmon.then(ce.fourier(n, range(r))).then(lmon)
    assert comp.tab == op.tab and comp.zero_state() == op.zero_state()
    return r, lmon, rmon, lrec, rrec


def cols_equal(A, B, n, cols):
    return all(A.zero_state(c) == B.zero_state(c) for c in cols)


def endpoint(n, u, w, ncol, rng):
    U = [u]
    V = hyper(w, n)
    R = opstep(n, U, V)
    r, lmon, rmon, lrec, rrec = lower_ops(R)
    assert r == rk(R)                                  # agrees with lower_child
    out = dict(rank=r)
    if r == n:
        fixed = rmon.adjoint().then(R).then(lmon.adjoint())      # Lmon^{-1} R Rmon^{-1}
        F = ce.fourier(n)
        cols = list(range(1 << n)) if ncol is None else rng.sample(range(1 << n), ncol)
        out['tab_eq'] = fixed.tab == F.tab
        out['cols_eq'] = cols_equal(fixed, F, n, cols)

        def cls(rec):   # is the address map trivial?  is there a quadratic (off-diagonal) phase part?
            Gid = tuple(rec['matrix_rows']) == tuple(1 << i for i in range(n))
            Qoff = any((rec['quadratic_rows'][i] & ~(1 << i)) for i in range(n))
            return ('perm' if not Gid else 'id') + ('+quad' if Qoff else '')
        out['Lclass'] = cls(lrec)
        out['Rclass'] = cls(rrec)
    return out


def all_subspace_bases(n):
    """bases of all subspaces of F2^n (closure enumeration)."""
    layer = {frozenset({0})}
    seen = set(layer)
    while layer:
        nxt = set()
        for S in layer:
            for v in range(1, 1 << n):
                if v not in S:
                    t = frozenset(S | {x ^ v for x in S})
                    if t not in seen:
                        seen.add(t)
                        nxt.add(t)
        layer = nxt
    return [basis(sorted(S), n) for S in seen]


def interval(n, w, Gs):
    """number of violations of: Y family 0 -> G -> w^perp has excess 0 iff G <= w^perp, else exactly 2."""
    V = hyper(w, n)
    bad = 0
    n_inside = 0
    for G in Gs:
        ex = d([], G) + d(G, V) - d([], V)
        inside = all(par(g & w) == 0 for g in G)
        n_inside += inside
        if ex != (0 if inside else 2):
            bad += 1
    return bad, n_inside


def network(n, u, w, s, rng):
    """Roles x (source, label <s>, ends FULL) and y (target, 0 -> <s> -> w^perp); gate y += c x at frame <s>.
    Expected operator: x -> T_FULL l_x ; y -> T_V (l_y + c l_x) with l = T_start^{-1} h.  Exact on every basis column
    of x (and 3 sampled columns of y per column of x)."""
    V = hyper(w, n)
    N = 1 << n
    c = Fr(1, 2)

    def mat(op):                       # exact matrix from the columns op.zero_state(b)
        cols = []
        for bi in range(N):
            vec, den = op.zero_state(bi)
            cols.append([(Fr(a, 1 << den), Fr(b, 1 << den)) for a, b in vec])
        return [[cols[j][i] for j in range(N)] for i in range(N)]

    def cm(a, b):
        return (a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0])

    def mv(M, v):
        out = []
        for i in range(N):
            re = im = Fr(0)
            for j in range(N):
                pr = cm(M[i][j], v[j])
                re += pr[0]
                im += pr[1]
            out.append((re, im))
        return out

    def add(a, b, k=Fr(1)):
        return [(x[0] + k * y[0], x[1] + k * y[1]) for x, y in zip(a, b)]

    S = [s]
    FULL = [1 << i for i in range(n)]
    steps = [('y', [], S), ('x', S, FULL), ('y', S, V)]
    charged = 0
    ok_rank = True
    for who, A, B in steps:
        r = rk(opstep(n, A, B))
        dd = d(A, B)
        charged += r
        ok_rank &= (r == dd)
    Ty_s = mat(T(n, S))
    Ty_V_from_S = mat(opstep(n, S, V))
    Tx_full_from_S = mat(opstep(n, S, FULL))
    TSinv = mat(T(n, S).adjoint())
    TV = mat(T(n, V))
    TF = mat(T(n, FULL))
    good = True
    for bx in range(N):
        for by in rng.sample(range(N), 3):
            hx = [(Fr(int(i == bx)), Fr(0)) for i in range(N)]       # physical x stored in frame <s>
            hy = [(Fr(int(i == by)), Fr(0)) for i in range(N)]       # physical y at frame 0
            y1 = mv(Ty_s, hy)                  # y climbs 0 -> <s>
            y1 = add(y1, hx, c)                # gate at the common frame <s>
            x1 = mv(Tx_full_from_S, hx)        # x climbs <s> -> FULL
            y2 = mv(Ty_V_from_S, y1)           # y climbs <s> -> w^perp
            lx = mv(TSinv, hx)                 # expected: logical content l_x = T_<s>^{-1} h_x
            ex_x = mv(TF, lx)
            ex_y = mv(TV, add(hy, lx, c))
            good &= (x1 == ex_x) and (y2 == ex_y)
    return charged, ok_rank, good


rng = random.Random(1)
for n in (3, 4, 5, 6, 9):
    u = 0b111 if n < 9 else 0b000011111          # odd weight (3 / 5)
    stats = {}
    ws = list(range(1, 1 << n))
    if n == 9:
        ws = rng.sample(ws, 160) + [u]
    for w in ws:
        if not par(w):
            continue                           # even w: w^perp contains w, frame labels would be degenerate
        kind = 'u' if w == u else ('compl' if par(w & u) else 'noncompl')
        e = endpoint(n, u, w, None if n <= 6 else 6, rng)
        key = (kind, e['rank'], e.get('tab_eq'), e.get('cols_eq'), e.get('Lclass'), e.get('Rclass'))
        stats[key] = stats.get(key, 0) + 1

    # --- endpoint claims
    compl = {k: v for k, v in stats.items() if k[0] == 'compl'}
    non = {k: v for k, v in stats.items() if k[0] == 'noncompl'}
    ctl_u = {k: v for k, v in stats.items() if k[0] == 'u'}
    n_compl = sum(compl.values())
    exp = ENDPOINT[n]
    ok_c = (all(k[1] == n and k[2] is True and k[3] is True and k[4] == 'perm+quad' and k[5] in ('id', 'id+quad')
                for k in compl) and n_compl > 0
            and {k: v for k, v in exp.items() if k[0] == 'compl'} == compl)
    cols_txt = 'all %d basis columns' % (1 << n) if n <= 6 else '6 sampled columns each'
    check('C3g.complement-n%d' % n, ok_c,
          '%d complement w (odd, w.u=1)%s: route T_{w^perp} T_<u>^-1 has Clifford rank %d; Lmon^-1 R Rmon^-1 == F on the '
          'tableau and on %s; wrapper classes (Lmon perm+quad; Rmon id: %d, id+quad: %d)'
          % (n_compl, '' if n <= 6 else ' (seeded sample)', n, cols_txt,
             compl.get(('compl', n, True, True, 'perm+quad', 'id'), 0),
             compl.get(('compl', n, True, True, 'perm+quad', 'id+quad'), 0)))
    ok_u = (all(k[1] == n and k[2] is True and k[3] is True for k in ctl_u)
            and {k: v for k, v in exp.items() if k[0] == 'u'} == ctl_u)
    check('C3g.format-sink-n%d' % n, ok_u,
          'control w = u (sink u^perp, %d draw%s): rank %d, exact (tableau and columns)'
          % (sum(ctl_u.values()), '' if sum(ctl_u.values()) == 1 else 's', n))
    if n >= 4:
        ok_n = (non and all(k[1] == n - 2 for k in non) and {k: v for k, v in exp.items() if k[0] == 'noncompl'} == non)
        check('C3g.noncomplement-n%d' % n, bool(ok_n),
              'control w.u=0 (%d odd w): Clifford rank n-2 = %d' % (sum(non.values()), n - 2))
    else:
        check('C3g.noncomplement-n%d' % n, not non, 'no odd w with w.u=0 exists at n=3 (control vacuous)')

    # --- port price: first odd complement w != u
    w = next(w for w in range(1, 1 << n) if par(w) and par(w & u) and w != u)
    V = hyper(w, n)
    Uperp = hyper(u, n)
    FULL = [1 << i for i in range(n)]
    rY, dY, rYu, rX = rk(T(n, V)), d([], V), rk(T(n, Uperp)), rk(opstep(n, [u], FULL))
    check('C3g.port-price-n%d' % n, (rY, dY, rYu, rX) == (PORT_PRICE[n],) * 4,
          'Y: 0 -> w^perp rank %d (d %d), 0 -> u^perp rank %d; X: <u> -> FULL rank %d; all n-1 = %d'
          % (rY, dY, rYu, rX, n - 1))

    if n <= 5:
        Gs = all_subspace_bases(n)
        bad, n_inside = interval(n, w, Gs)
        check('C3g.interval-n%d' % n, bad == 0 and len(Gs) == INTERVAL_SUBSPACES[n] and 0 < n_inside < len(Gs),
              'Y: 0 -> G -> w^perp excess 0 iff G <= w^perp (%d of %d subspaces) else exactly 2: violations %d'
              % (n_inside, len(Gs), bad))
        s = next((s for s in range(1, 1 << n) if par(s) and par(s & w) == 0 and par(s & u) == 1), None)
        ch, okr, good = network(n, u, w, s, rng)
        exp_c = CORRECTOR[n]
        check('C3g.corrector-n%d' % n, s == exp_c['s'] and ch == exp_c['charged'] == 2 * (n - 1) and okr and good,
              's=%s (s.u=1, s.w=0): charged %d = d-sum 2(n-1), child rank == d at every step %s, operator exact on '
              'columns %s' % (format(s, '0%db' % n), ch, okr, good))

finish()
