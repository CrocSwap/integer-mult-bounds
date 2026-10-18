"""Exact toy: a source read at its own frame, sandwiched between two non-nested frame steps (n = 4 labels over F2).

Setting.  Labels live in F2^4 with the standard dot product.  A port anchor u_a = 0111 is odd (u_a.u_a = 1).  Three
reader labels u1 = 1000, u2 = 1011, u3 = 1101 are odd and orthogonal to u_a; they span u_a^perp, so the only subspace
orthogonal to all three readers is <u_a>: the only frame that is common to the readers' natural read frames is the
point station <u_a> (asserted below).  One source x has label <w> with w not orthogonal to any reader (w.u_i = 1),
so every reader must see x across a drop.

Two networks compute the SAME linear operator on the registers (x, y1, y2, y3):
    x  ->  T_FULL l_x ,        y_i  ->  T_{u_i^perp} ( l_{y_i} + q_i l_x ) ,        q = (1, -1, 1/2),
where l is the logical content, T_F is the canonical Clifford frame operator of a subspace F, and the physical
registers hold x = T_<w> l_x and y_i = l_{y_i}.

  standard : one shared copy of x is dropped <w> -> 0 (the shared station), each reader reads it at frame 0 and then
             climbs 0 -> u_i^perp (nested).  Charged steps: copy <w> -> 0 ; y_i : 0 -> u_i^perp ; x : <w> -> FULL.
  relaxed  : no copy.  Each reader climbs 0 -> <w> (a frame that contains a vector w outside u_i^perp), reads x at x's
             own frame <w>, then takes a NON-nested step <w> -> u_i^perp.  Charged steps: y_i : 0 -> <w> and
             <w> -> u_i^perp ; x : <w> -> FULL.

Checks.
  * The operator is exact on all 4 * 16 = 64 basis columns of the 4 registers (exact Gaussian-dyadic arithmetic).
  * For every transition A -> B the Clifford child rank (clifford_exact.lower_child of T_A^-1 then T_B) equals the
    frame distance  d(A, B) = dim A + dim B - 2 dim (A cap B),  in both networks, including the non-nested steps.
  * Charged rank total: standard 13 (of which 1 is the copy), relaxed 18 = 13 + 3*2 - 1.
"""
import functools
import sys
from fractions import Fraction as Fr

from report import check, finish, main_file

sys.path.insert(0, str(main_file('research/direct-delivery504-global/vendor/clifford/clifford_exact.py').parent))
import clifford_exact as ce  # noqa: E402  (the repository's exact Clifford compiler, unmodified)

# ----------------------------------------------------------------------------------------------------------------
# Expected values (from the exact run of the toy; every one is re-derived below and compared).
EXPECTED = {
    'w_candidates': [0b1000],                  # odd w with w.u_i = 1 for all three readers: unique
    'common_reader_frame': [0, 0b0111],        # {z : z.u_i = 0 for all i} = {0, u_a}: the point station <u_a>
    'columns': 64,                             # 4 registers x 16 basis vectors, per network
    'std_total': 13, 'std_copy': 1,            # standard network: charged rank total, copy part
    'relaxed_total': 18, 'relaxed_copy': 0,    # relaxed network: 13 + 3*2 - 1 = 18
    # transitions (register, dim A, dim B, child rank, distance d)
    'std_transitions': [('copy', 1, 0, 1, 1), ('y0', 0, 3, 3, 3), ('y1', 0, 3, 3, 3), ('y2', 0, 3, 3, 3),
                        ('x', 1, 4, 3, 3)],
    'relaxed_transitions': [('y0', 0, 1, 1, 1), ('y0', 1, 3, 4, 4), ('y1', 0, 1, 1, 1), ('y1', 1, 3, 4, 4),
                            ('y2', 0, 1, 1, 1), ('y2', 1, 3, 4, 4), ('x', 1, 4, 3, 3)],
}

n = 4
N = 1 << n


def par(x):
    return bin(x).count('1') & 1


def span(vs):
    out = {0}
    for v in vs:
        out |= {o ^ v for o in out}
    return out


def perp(vs):
    return [z for z in range(N) if all(par(z & v) == 0 for v in vs)]


def basis(vs):
    b = []
    for v in vs:
        if ce.rank(b + [v]) > len(b):
            b.append(v)
    return b


def dist(A, B):
    """frame distance d(A,B) = dim A + dim B - 2 dim(A cap B)."""
    a, b = basis(A), basis(B)
    return len(a) + len(b) - 2 * (len(a) + len(b) - ce.rank(a + b))


def T(F):
    return ce.canonical_frame(n, tuple(basis(F)))


# exact complex dyadic linear algebra: a number is a pair (re, im) of Fractions
def mat(op):
    cols = []
    for bidx in range(N):
        vec, den = op.zero_state(bidx)
        cols.append([(Fr(a, 1 << den), Fr(c, 1 << den)) for a, c in vec])
    return [[cols[j][i] for j in range(N)] for i in range(N)]


def cm(a, b):
    return (a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0])


def ca(a, b):
    return (a[0] + b[0], a[1] + b[1])


Z = (Fr(0), Fr(0))


def mv(M, v):
    return [functools.reduce(ca, [cm(M[i][j], v[j]) for j in range(N)], Z) for i in range(N)]


def sc(q, v):
    return [(q * a, q * b) for a, b in v]


def add(u, v):
    return [ca(a, b) for a, b in zip(u, v)]


cache = {}


def Tm(F):
    k = tuple(sorted(span(F)))
    if k not in cache:
        cache[k] = (mat(T(F)), mat(T(F).adjoint()))
    return cache[k]


def step(h, A, B, log, who):
    """apply T_B T_A^-1 to the physical vector h and record (register, dim A, dim B, child rank, distance)."""
    op = T(A).adjoint().then(T(B)) if basis(A) else T(B)
    r = ce.lower_child(op)[0]['rank']
    dd = dist(A, B)
    log.append((who, len(basis(A)), len(basis(B)), r, dd))
    return mv(Tm(B)[0], mv(Tm(A)[1], h))


ua = 0b0111
U = [0b1000, 0b1011, 0b1101]
q = [Fr(1), Fr(-1), Fr(1, 2)]

# ---- C1.c0-station: the readers' labels span u_a^perp, hence the only common reader frame is <u_a>
labels_ok = par(ua & ua) == 1 and all(par(u & u) == 1 and par(u & ua) == 0 for u in U)
spans_perp = span(U) == set(perp([ua])) and ce.rank(U) == n - 1
common = sorted(perp(U))
cands = [w for w in range(1, N) if par(w & w) == 1 and all(par(w & u) == 1 for u in U)]
check('C1.c0-station',
      labels_ok and spans_perp and common == EXPECTED['common_reader_frame'] and cands == EXPECTED['w_candidates'],
      'readers odd and orthogonal to u_a; span(u1,u2,u3) = u_a^perp (dim %d); frames orthogonal to all readers = %s; '
      'source label w = %s (unique odd w with w.u_i = 1 for all i)'
      % (ce.rank(U), [format(z, '04b') for z in common], [format(c, '04b') for c in cands]))
w = EXPECTED['w_candidates'][0]
FULL = list(range(1, N))
W = [w]


def run(mode, hx, hy):
    """hx: physical source (frame <w>); hy: physical targets (frame 0).  Returns final x, final ys, transition log."""
    log = []
    ys = list(hy)
    if mode == 'standard':
        C = list(hx)                                   # copy of x taken at its own frame <w>
        C = step(C, W, [], log, 'copy')                # shared station: <w> -> 0
        for i in range(3):
            ys[i] = add(ys[i], sc(q[i], C))            # read at frame 0
            ys[i] = step(ys[i], [], perp([U[i]]), log, 'y%d' % i)   # nested climb 0 -> u_i^perp
        x = step(hx, W, FULL, log, 'x')
    else:
        for i in range(3):
            ys[i] = step(ys[i], [], W, log, 'y%d' % i)  # 0 -> <w>: frame containing a vector outside u_i^perp
            ys[i] = add(ys[i], sc(q[i], hx))           # read x at x's own frame, no copy
            ys[i] = step(ys[i], W, perp([U[i]]), log, 'y%d' % i)    # non-nested step <w> -> u_i^perp
        x = step(hx, W, FULL, log, 'x')
    return x, ys, log


def expect(lx, ly):
    ex = mv(Tm(FULL)[0], lx)
    ey = [mv(Tm(perp([U[i]]))[0], add(ly[i], sc(q[i], lx))) for i in range(3)]
    return ex, ey


zero = [Z] * N


def e(b):
    v = [Z] * N
    v[b] = (Fr(1), Fr(0))
    return v


results = {}
for mode in ('standard', 'relaxed'):
    good = 0
    logs = []
    for reg in range(4):
        for b in range(N):
            l = [zero] * 4
            l[reg] = e(b)                              # logical input: one basis vector of one register
            hx = mv(Tm(W)[0], l[0])                    # physical source = T_<w> l_x
            hy = [l[1], l[2], l[3]]                    # physical targets start at frame 0
            x, ys, log = run(mode, hx, hy)
            ex, ey = expect(l[0], l[1:])
            good += (x == ex and ys == ey)
            logs.append(log)
    assert all(lg == logs[0] for lg in logs)           # the transition costs do not depend on the input column
    log = logs[0]
    total = sum(r for *_, r, _ in log)
    copy = sum(r for who, *_, r, _ in log if who == 'copy')
    results[mode] = dict(cols=good, log=log, total=total, copy=copy)

std, rel = results['standard'], results['relaxed']

check('C1.std-exact',
      std['cols'] == EXPECTED['columns'] and std['total'] == EXPECTED['std_total']
      and std['copy'] == EXPECTED['std_copy'] and std['log'] == EXPECTED['std_transitions'],
      'standard network exact on %d/%d columns; charged rank %d (copy part %d)'
      % (std['cols'], EXPECTED['columns'], std['total'], std['copy']))

check('C1.relaxed-exact',
      rel['cols'] == EXPECTED['columns'] and rel['total'] == EXPECTED['relaxed_total']
      and rel['copy'] == EXPECTED['relaxed_copy'] and rel['log'] == EXPECTED['relaxed_transitions']
      and rel['total'] == std['total'] + 3 * 2 - 1,
      'relaxed network exact on %d/%d columns; charged rank %d = %d + 3*2 - 1 (copy part %d)'
      % (rel['cols'], EXPECTED['columns'], rel['total'], std['total'], rel['copy']))


# the relaxed network's final reader steps <w> -> u_i^perp (dim 1 -> 3) are not nested: w is not orthogonal to u_i
nonnested_ok = all(w not in perp([u]) for u in U)
n_nonnested = sum(1 for who, a, b, r, dd in rel['log'] if who != 'x' and (a, b) == (1, 3))
all_eq = all(r == dd for m in results.values() for _, _, _, r, dd in m['log'])
n_steps = sum(len(m['log']) for m in results.values())
check('C1.child-eq-d', all_eq and nonnested_ok and n_nonnested == 3,
      'lower_child rank == d(A,B) on all %d transitions of both networks (including %d non-nested steps <w> -> u_i^perp, '
      'rank 4 = d)' % (n_steps, n_nonnested))

finish()
