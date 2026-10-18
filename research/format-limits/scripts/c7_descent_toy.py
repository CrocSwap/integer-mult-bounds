"""Exact toy: one reader reads three terms at their point stations, paying for descents between the reads (n = 5).

Setting.  Labels live in F2^5 with the standard dot product.  Three term anchors u_a, u_b, u_c are odd and pairwise
orthogonal; a "double" reader t has an odd label u_t orthogonal to all three anchors and reads all three terms; for each
term j a "single" reader r_j reads only term j.  Term j has a source x_j stored at a 2-dimensional nondegenerate frame
f_j = <u_j, w_j> containing u_j.  The natural readers of term j are all odd vectors orthogonal to u_j; they span u_j^perp,
so the only frame orthogonal to all of them is <u_j>: the only common read frame of term j is the point station <u_j>
(checked by enumeration).  The operator (identical in all networks) is
    y_r -> T_{u_r^perp} ( l_y + sum_j q_rj l_{x_j} ),      x_j -> T_FULL l_{x_j},
with fixed dyadic Gaussian coefficients q_rj, on the 7 logical registers (x_a, x_b, x_c, y_t, y_a, y_b, y_c).
T_F is the canonical Clifford frame operator of a subspace F, d(A, B) = dim A + dim B - 2 dim(A cap B) the frame
distance; the charged rank of a step A -> B is the Clifford rank of T_B T_A^{-1} (clifford_exact.lower_child).

Networks (copy C_j of x_j is dropped f_j -> <u_j> at cost 1 each, except in STD where noted):
  STD   : nesting kept, only term a is read at a point station; C_b, C_c drop to 0 (cost 2 each); t and the single
          readers r_b, r_c read b, c at 0 first, then t climbs 0 -> <u_a> (reads a) -> u_t^perp.
  CLONE : nesting kept by clones: t climbs 0 -> <u_a> [a] -> <u_a,u_b> [b, read from a clone of C_b raised
          <u_b> -> <u_a,u_b>] -> <u_a,u_b,u_c> [c, from a clone raised <u_c> -> <u_a,u_b,u_c>] -> u_t^perp.
  DESC  : t reads at the point stations in turn: 0 -> <u_a> [a] -> <u_b> (one NON-comparable step, rank 2) [b] ->
          <u_c> (rank 2) [c] -> u_t^perp.
  DESC0 : as DESC but each descent goes through 0: <u_a> -> 0 -> <u_b> -> 0 -> <u_c>.
Checks: the whole linear map is exactly equal to the intended operator (exact Gaussian-dyadic arithmetic) on all
7 * 32 = 224 basis columns, in every network; every transition has Clifford child rank == d(A, B); the charged mass
by role is compared with the closed forms (+2 per descent between two lines, 2(k-1) for k point stations, STD vs DESC).
"""
import itertools
import random
import sys

import numpy as np

from report import check, finish, main_file

sys.path.insert(0, str(main_file('research/direct-delivery504-global/vendor/clifford/clifford_exact.py').parent))
import clifford_exact as ce  # noqa: E402  (the repository's exact Clifford compiler, unmodified)

# ----------------------------------------------------------------------------------------------------------------
# Expected values (from the exact run of the toy; every one is re-derived below and compared).
EXPECTED = {
    'instance': dict(anchors=[0b00111, 0b01011, 0b01110], u_t=0b01101, singles=[0b01000, 0b00100, 0b00001],
                     frames=[[0b00111, 0b01000], [0b01011, 0b00100], [0b01110, 0b00001]]),
    'readers_per_term': 8,                                    # odd vectors orthogonal to u_j
    'common_frames': [[0, 7], [0, 11], [0, 14]],              # {z : z.r = 0 for all natural readers r} = {0, u_j}
    'columns': 224,                                           # 7 registers x 32 basis vectors
    # transitions (role, dim A, dim B, child rank, distance d), source-register steps omitted (3 steps 2 -> 5, rank 3)
    'transitions': {
        'STD': [('copy-drop', 2, 1, 1, 1), ('copy-drop', 2, 0, 2, 2), ('copy-drop', 2, 0, 2, 2), ('t', 0, 1, 1, 1),
                ('t', 1, 4, 3, 3), ('single', 0, 4, 4, 4), ('single', 0, 4, 4, 4), ('single', 0, 1, 1, 1),
                ('single', 1, 4, 3, 3)],
        'CLONE': [('copy-drop', 2, 1, 1, 1), ('copy-drop', 2, 1, 1, 1), ('copy-drop', 2, 1, 1, 1), ('clone', 1, 2, 1, 1),
                  ('clone', 1, 3, 2, 2), ('t', 0, 1, 1, 1), ('t', 1, 2, 1, 1), ('t', 2, 3, 1, 1), ('t', 3, 4, 1, 1),
                  ('single', 0, 1, 1, 1), ('single', 1, 4, 3, 3), ('single', 0, 1, 1, 1), ('single', 1, 4, 3, 3),
                  ('single', 0, 1, 1, 1), ('single', 1, 4, 3, 3)],
        'DESC': [('copy-drop', 2, 1, 1, 1), ('copy-drop', 2, 1, 1, 1), ('copy-drop', 2, 1, 1, 1), ('t', 0, 1, 1, 1),
                 ('t-DESCENT', 1, 1, 2, 2), ('t-DESCENT', 1, 1, 2, 2), ('t', 1, 4, 3, 3), ('single', 0, 1, 1, 1),
                 ('single', 1, 4, 3, 3), ('single', 0, 1, 1, 1), ('single', 1, 4, 3, 3), ('single', 0, 1, 1, 1),
                 ('single', 1, 4, 3, 3)],
        'DESC0': [('copy-drop', 2, 1, 1, 1), ('copy-drop', 2, 1, 1, 1), ('copy-drop', 2, 1, 1, 1), ('t', 0, 1, 1, 1),
                  ('t-DESCENT', 1, 0, 1, 1), ('t-reclimb', 0, 1, 1, 1), ('t-DESCENT', 1, 0, 1, 1),
                  ('t-reclimb', 0, 1, 1, 1), ('t', 1, 4, 3, 3), ('single', 0, 1, 1, 1), ('single', 1, 4, 3, 3),
                  ('single', 0, 1, 1, 1), ('single', 1, 4, 3, 3), ('single', 0, 1, 1, 1), ('single', 1, 4, 3, 3)],
    },
    # charged mass by role, and total
    'mass': {
        'STD': ({'copy-drop': 5, 't': 4, 'single': 12, 'source': 9}, 30),
        'CLONE': ({'copy-drop': 3, 'clone': 3, 't': 4, 'single': 12, 'source': 9}, 31),
        'DESC': ({'copy-drop': 3, 't': 4, 't-DESCENT': 4, 'single': 12, 'source': 9}, 32),
        'DESC0': ({'copy-drop': 3, 't': 4, 't-DESCENT': 2, 't-reclimb': 2, 'single': 12, 'source': 9}, 32),
    },
    'reader_mass': {'STD': 4, 'CLONE': 4, 'DESC': 8, 'DESC0': 8},   # all roles starting with 't'
    'nested_minimum': 4,                                            # dim u_t^perp = n - 1: path 0 -> <u_a> -> u_t^perp
    'descent_mass_each': 2,                                         # one descent between two lines: direct or via 0
    'k_stations_extra': {1: 0, 2: 2, 3: 4},                         # reader at k point stations pays 2(k-1)
    'desc_vs_std': dict(cst=-2, reader=4, net=2),
}

n = 5
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


def dim(A):
    return len(basis(A))


def meet(A, B):
    sA = span(basis(A))
    return [z for z in span(basis(B)) if z in sA]


def dist(A, B):
    """frame distance d(A,B) = dim A + dim B - 2 dim(A cap B)."""
    return dim(A) + dim(B) - 2 * dim(meet(A, B))


def nondeg(F):
    b = basis(F)
    G = [[par(x & y) for y in b] for x in b]
    rows = [sum(G[i][j] << j for j in range(len(b))) for i in range(len(b))]
    return ce.rank(rows) == len(b)


def T(F):
    return ce.canonical_frame(n, tuple(basis(F)))


# ---- exact Gaussian-dyadic matrices: (Re int array, Im int array, exponent e), value = (Re + i Im) / 2^e
def mat(op):
    E = 0
    raw = []
    for bidx in range(N):
        vec, den = op.zero_state(bidx)
        raw.append((vec, den))
        E = max(E, den)
    R = np.zeros((N, N), dtype=object)
    I = np.zeros((N, N), dtype=object)
    for j, (vec, den) in enumerate(raw):
        s = 1 << (E - den)
        for i, (a, c) in enumerate(vec):
            R[i, j] = a * s
            I[i, j] = c * s
    return (R, I, E)


def norm(M):
    R, I, E = M
    while E > 0 and all(int(v) % 2 == 0 for v in R.flat) and all(int(v) % 2 == 0 for v in I.flat):
        R = R // 2
        I = I // 2
        E -= 1
    return (R, I, E)


def mm(A, B):
    (a, b, e), (c, d, f) = A, B
    return norm((a.dot(c) - b.dot(d), a.dot(d) + b.dot(c), e + f))


def madd(A, B):
    (a, b, e), (c, d, f) = A, B
    E = max(e, f)
    return norm((a * (1 << (E - e)) + c * (1 << (E - f)), b * (1 << (E - e)) + d * (1 << (E - f)), E))


def scal(q, A):             # q = (re, im, exp) is the dyadic Gaussian number (re + i im) / 2^exp
    (qr, qi, qe) = q
    (a, b, e) = A
    return norm((qr * a - qi * b, qr * b + qi * a, e + qe))


def eq(A, B):
    A = norm(A)
    B = norm(B)
    return A[2] == B[2] and (A[0] == B[0]).all() and (A[1] == B[1]).all()


ZERO = (np.zeros((N, N), dtype=object), np.zeros((N, N), dtype=object), 0)
ID = (np.eye(N, dtype=object) * 1, np.zeros((N, N), dtype=object), 0)
cache = {}


def Tm(F):
    k = tuple(sorted(span(basis(F))))
    if k not in cache:
        cache[k] = (mat(T(F)), mat(T(F).adjoint()))
    return cache[k]


# ---- instance search (deterministic, seeded): anchors odd and pairwise orthogonal, u_t odd orthogonal to all of them,
# one single reader per term, f_j = <u_j, w_j> nondegenerate
odd = [v for v in range(1, N) if par(v)]
inst = None
rng = random.Random(24)
trip = list(itertools.combinations(odd, 3))
rng.shuffle(trip)
for ua, ub, uc in trip:
    if any(bin(u).count('1') == 1 for u in (ua, ub, uc)):
        continue                                                # avoid coordinate anchors
    if par(ua & ub) or par(ua & uc) or par(ub & uc):
        continue
    ts = [t for t in odd if not par(t & ua) and not par(t & ub) and not par(t & uc)]
    if not ts:
        continue
    ut = ts[0]

    def single(u, others):
        c = [r for r in odd if not par(r & u) and all(par(r & o) for o in others)]
        return c[0] if c else None
    ra, rb, rc = single(ua, [ub, uc]), single(ub, [ua, uc]), single(uc, [ua, ub])
    if None in (ra, rb, rc):
        continue
    ok = True
    for u in (ua, ub, uc):
        R = [r for r in odd if not par(r & u)]                  # the full natural reader set of the term
        if set(perp(R)) != {0, u}:
            ok = False
    if not ok:
        continue
    fs = []
    for u in (ua, ub, uc):
        w = [w for w in range(1, N) if w not in span([ua, ub, uc]) and nondeg([u, w]) and dim([u, w]) == 2]
        fs.append([u, w[0]])
    inst = (ua, ub, uc, ut, ra, rb, rc, fs)
    break
assert inst, 'no instance found'
ua, ub, uc, ut, ra, rb, rc, fs = inst
U = [ua, ub, uc]
FULL = list(range(1, N))

# ---- C7.c0-station
common = []
n_read = []
for u in U:
    R = [r for r in odd if not par(r & u)]
    n_read.append(len(R))
    common.append(sorted(perp(R)))
inst_got = dict(anchors=U, u_t=ut, singles=[ra, rb, rc], frames=fs)
frames_ok = all(nondeg(F) for F in [[ua], [ub], [uc], [ua, ub], [ua, ub, uc], perp([ut])] + fs)
orth_ok = (all(par(u) == 1 for u in U + [ut]) and not par(ua & ub) and not par(ua & uc) and not par(ub & uc)
           and all(not par(ut & u) for u in U))
check('C7.c0-station',
      common == EXPECTED['common_frames'] and n_read == [EXPECTED['readers_per_term']] * 3 and orth_ok and frames_ok
      and inst_got == EXPECTED['instance'],
      'anchors %s, u_t %s; each term has %d natural readers whose common read frames are %s = {0, u_j}: only the point '
      'station <u_j>' % ([format(u, '05b') for u in U], format(ut, '05b'), n_read[0], common))

# ---- the four networks
regs = ['x0', 'x1', 'x2', 'yt', 'ya', 'yb', 'yc']
reads = {'yt': [0, 1, 2], 'ya': [0], 'yb': [1], 'yc': [2]}
ulab = {'yt': ut, 'ya': ra, 'yb': rb, 'yc': rc}
Q = {('yt', 0): (1, 0, 0), ('yt', 1): (-1, 0, 0), ('yt', 2): (1, 1, 1), ('ya', 0): (3, 0, 1), ('yb', 1): (0, 1, 0),
     ('yc', 2): (-1, 2, 2)}                                     # dyadic Gaussian q = (re + i im) / 2^e


def run(mode):
    log = []
    # state: register -> {input register: matrix}; physical x_j = T_{f_j} l_{x_j}; targets start at frame 0
    S = {r: {} for r in regs}
    for j in range(3):
        S['x%d' % j] = {'x%d' % j: Tm(fs[j])[0]}
    for y in ('yt', 'ya', 'yb', 'yc'):
        S[y] = {y: ID}

    def step(reg, A, B, who):
        if basis(A) == basis(B) and span(basis(A)) == span(basis(B)):
            return
        op = T(A).adjoint().then(T(B)) if basis(A) else T(B)
        r = ce.lower_child(op)[0]['rank']
        dd = dist(A, B)
        log.append((who, dim(A), dim(B), r, dd))
        M = mm(Tm(B)[0], Tm(A)[1])
        S[reg] = {k: mm(M, v) for k, v in S[reg].items()}

    def addto(dst, src, q):
        for k, v in S[src].items():
            S[dst][k] = madd(S[dst].get(k, ZERO), scal(q, v))

    def copy(new, src):
        S[new] = {k: v for k, v in S[src].items()}

    for j in range(3):
        copy('cp%d' % j, 'x%d' % j)
    if mode == 'STD':
        step('cp0', fs[0], [ua], 'copy-drop')                    # term a cheap
        step('cp1', fs[1], [], 'copy-drop')
        step('cp2', fs[2], [], 'copy-drop')
        addto('yt', 'cp1', Q[('yt', 1)])                         # reads of b, c at frame 0
        addto('yt', 'cp2', Q[('yt', 2)])
        addto('yb', 'cp1', Q[('yb', 1)])
        addto('yc', 'cp2', Q[('yc', 2)])
        step('yt', [], [ua], 't')
        addto('yt', 'cp0', Q[('yt', 0)])
        step('yt', [ua], perp([ut]), 't')
        step('yb', [], perp([rb]), 'single')
        step('yc', [], perp([rc]), 'single')
    else:
        for j, u in enumerate(U):
            step('cp%d' % j, fs[j], [u], 'copy-drop')
        if mode in ('DESC', 'DESC0'):
            step('yt', [], [ua], 't')
            addto('yt', 'cp0', Q[('yt', 0)])
            if mode == 'DESC':
                step('yt', [ua], [ub], 't-DESCENT')
            else:
                step('yt', [ua], [], 't-DESCENT')
                step('yt', [], [ub], 't-reclimb')
            addto('yt', 'cp1', Q[('yt', 1)])
            if mode == 'DESC':
                step('yt', [ub], [uc], 't-DESCENT')
            else:
                step('yt', [ub], [], 't-DESCENT')
                step('yt', [], [uc], 't-reclimb')
            addto('yt', 'cp2', Q[('yt', 2)])
            step('yt', [uc], perp([ut]), 't')
        elif mode == 'CLONE':
            copy('K1', 'cp1')
            copy('K2', 'cp2')                                    # clones at the bottom frame (equal-frame copy, no drop)
            step('K1', [ub], [ua, ub], 'clone')
            step('K2', [uc], [ua, ub, uc], 'clone')
            step('yt', [], [ua], 't')
            addto('yt', 'cp0', Q[('yt', 0)])
            step('yt', [ua], [ua, ub], 't')
            addto('yt', 'K1', Q[('yt', 1)])
            step('yt', [ua, ub], [ua, ub, uc], 't')
            addto('yt', 'K2', Q[('yt', 2)])
            step('yt', [ua, ub, uc], perp([ut]), 't')
        step('yb', [], [ub], 'single')
        addto('yb', 'cp1', Q[('yb', 1)])
        step('yb', [ub], perp([rb]), 'single')
        step('yc', [], [uc], 'single')
        addto('yc', 'cp2', Q[('yc', 2)])
        step('yc', [uc], perp([rc]), 'single')
    step('ya', [], [ua], 'single')
    addto('ya', 'cp0', Q[('ya', 0)])
    step('ya', [ua], perp([ra]), 'single')
    for j in range(3):
        step('x%d' % j, fs[j], FULL, 'source')
    return S, log


def expected():
    E = {}
    for j in range(3):
        E['x%d' % j] = {'x%d' % j: Tm(FULL)[0]}
    for y, js in reads.items():
        P = Tm(perp([ulab[y]]))[0]
        dct = {y: P}
        for j in js:
            dct['x%d' % j] = scal(Q[(y, j)], P)
        E[y] = dct
    return E


EXP = expected()
res = {}
for mode in ('STD', 'CLONE', 'DESC', 'DESC0'):
    S, log = run(mode)
    # column (input register k, basis vector) is exact iff every output register's block for k matches the intended
    # operator (blocks absent from the intended operator must be zero)
    ncols = 0
    for k in regs:
        if all(eq(S[r].get(k, ZERO), EXP[r].get(k, ZERO)) for r in regs):
            ncols += N
    by = {}
    for who, a, b, r, dd in log:
        by[who] = by.get(who, 0) + r
    res[mode] = dict(cols=ncols, log=log, by=by, total=sum(by.values()),
                     shown=[x for x in log if x[0] != 'source'],
                     reader=sum(v for k, v in by.items() if k.startswith('t')))
    check('C7.exact-%s' % mode.lower(), ncols == EXPECTED['columns'],
          '%s: whole operator equals the intended one on %d/%d basis columns of the 7 logical registers'
          % (mode, ncols, EXPECTED['columns']))

all_eq = all(r == dd for m in res.values() for _, _, _, r, dd in m['log'])
shown_ok = all(m['shown'] == EXPECTED['transitions'][mode] for mode, m in res.items())
n_trans = sum(len(m['log']) for m in res.values())
# the two descents of DESC are steps between two distinct lines <u_a> -> <u_b> -> <u_c>: non-comparable, child rank 2
noncomp = [x for x in res['DESC']['log'] if x[0] == 't-DESCENT']
lines_meet_zero = all(len(meet([a], [b])) == 1 for a, b in ((ua, ub), (ub, uc)))
check('C7.child-eq-d', all_eq and shown_ok and len(noncomp) == 2 and lines_meet_zero
      and all((a, b, r, dd) == (1, 1, 2, 2) for _, a, b, r, dd in noncomp),
      'lower_child rank == d(A,B) on all %d transitions of the four networks, including the %d non-comparable '
      'line-to-line descents (dim 1 -> 1, meet 0) of rank 2' % (n_trans, len(noncomp)))

# ---- descents: +2 per line-to-line descent, direct or through 0
per_desc = {'DESC': sum(r for w_, a, b, r, dd in res['DESC']['log'] if w_ == 't-DESCENT') // 2,
            'DESC0': sum(r for w_, a, b, r, dd in res['DESC0']['log'] if w_ in ('t-DESCENT', 't-reclimb')) // 2}
check('C7.descent-mass',
      per_desc == {'DESC': EXPECTED['descent_mass_each'], 'DESC0': EXPECTED['descent_mass_each']},
      '+%d data mass per rank-1 descent <u_i> -> <u_j>: direct %d (one rank-2 step), via 0 %d (two rank-1 steps), identical'
      % (EXPECTED['descent_mass_each'], per_desc['DESC'], per_desc['DESC0']))


# ---- a reader at k point stations pays 2(k-1) beyond the nested minimum
def path_mass(stations):
    tot = 0
    for A, B in zip(stations, stations[1:]):
        op = T(A).adjoint().then(T(B)) if basis(A) else T(B)
        r = ce.lower_child(op)[0]['rank']
        assert r == dist(A, B)
        tot += r
    return tot


extra = {}
for k in (1, 2, 3):
    path = [[]] + [[u] for u in U[:k]] + [perp([ut])]
    extra[k] = path_mass(path) - EXPECTED['nested_minimum']
check('C7.reader-stations',
      extra == EXPECTED['k_stations_extra'] and res['DESC']['reader'] == EXPECTED['nested_minimum'] + extra[3]
      and all(extra[k] == 2 * (k - 1) for k in extra),
      'reader path 0 -> <u_1> -> ... -> <u_k> -> u_t^perp costs %d + 2(k-1): extra %s for k = 1, 2, 3 (DESC: %d = %d + 4)'
      % (EXPECTED['nested_minimum'], extra, res['DESC']['reader'], EXPECTED['nested_minimum']))

# ---- charged mass by role; DESC vs STD
mass_ok = all((m['by'], m['total']) == EXPECTED['mass'][mode] for mode, m in res.items())
reader_ok = {mode: m['reader'] for mode, m in res.items()} == EXPECTED['reader_mass']
cst = res['DESC']['by']['copy-drop'] - res['STD']['by']['copy-drop']
rd = res['DESC']['reader'] - res['STD']['reader']
check('C7.desc-vs-std',
      mass_ok and reader_ok and (cst, rd, cst + rd) == tuple(EXPECTED['desc_vs_std'][k] for k in ('cst', 'reader', 'net')),
      'charged totals STD %d, CLONE %d, DESC %d, DESC0 %d; reader path mass %s; DESC vs STD: copy-drop mass %+d, reader '
      '%+d, net %+d (2 cheap terms earned, 2 descents paid)'
      % (res['STD']['total'], res['CLONE']['total'], res['DESC']['total'], res['DESC0']['total'],
         {m: v['reader'] for m, v in res.items()}, cst, rd, cst + rd))

finish()
