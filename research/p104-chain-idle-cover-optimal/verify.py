#!/usr/bin/env python3
"""Exact checks for the chain-nested root: idle cover bound, top targets, retirement scope, shape optimality.

Python 3.12, standard library only.  Run:
    python3 -I -B research/p104-chain-idle-cover-optimal/verify.py
Expected marker: PASS_CHAIN_IDLE_COVER_OPTIMAL

All failures raise ValueError (so everything stays active under -O).  Sections:
  0  retained input bytes against retained/SOURCE-PINS.json
  A  idle cover of the literal chain-nested root (Theorem 1): literal coverage, exhaustive minimum cover for
     small g, random covers against the majorization chain, the exact "no L/R spanning line" check, controls
  B  top targets (Theorem 2): literal root identity at random D, rank-one Gram, residual identity, top triple,
     the same hypotheses on the #6726 root, controls
  C  retirement and masks (Proposition 3): #6726's two witnesses give the chain gate masks, outer histograms,
     retirement census of the literal chain word, controls
  D  shape optimality (Proposition 4): ledger against literal words, exhaustive search over all compositions
     with 18 stages on the complex and binary histograms, dynamic program for 10..40 stages (scaled model)
"""
import gzip
import hashlib
import heapq
import itertools
import json
import random
import sys
from collections import Counter, defaultdict
from decimal import Decimal as Dec, getcontext
from fractions import Fraction as Q
from functools import lru_cache
from pathlib import Path

HERE = Path(__file__).resolve().parent
for sub in ('retained/pr6827', 'retained/pr6833', 'retained/pr6726', 'retained/pr6726/bit'):
    sys.path.insert(0, str(HERE / sub))
import chain_root as C  # noqa: E402
import words as W  # noqa: E402
import audit_binary_mixed as AB  # noqa: E402
from dualpair import gram_report, pair_lattices  # noqa: E402

getcontext().prec = 50
OUT = {}
CTL = {}


def need(ok, why):
    if not ok:
        raise ValueError(why)


def expect_error(fn, tag):
    try:
        fn()
    except ValueError as e:
        need(tag in str(e), ('wrong failure', tag, str(e)))
        return str(e)[:90]
    raise ValueError('control accepted: ' + tag)


def jload(rel):
    return json.loads((HERE / rel).read_text())


# ------------------------------------------------------------------------------------------------- 0 pins
def check_pins():
    pins = jload('retained/SOURCE-PINS.json')
    for p in pins:
        data = (HERE / p['local']).read_bytes()
        need(len(data) == p['bytes'], ('size', p['local']))
        need(hashlib.sha256(data).hexdigest() == p['sha256'], ('sha256', p['local']))
        need(hashlib.sha1(b'blob %d\0' % len(data) + data).hexdigest() == p['git_blob'], ('git blob', p['local']))
    OUT['retained_inputs'] = len(pins)


# ------------------------------------------------------------------------------------- shared linear algebra
def rank_of(rows):
    rows = [r[:] for r in rows if any(r)]
    rk = 0
    ncol = len(rows[0]) if rows else 0
    for c in range(ncol):
        piv = next((i for i in range(rk, len(rows)) if rows[i][c]), None)
        if piv is None:
            continue
        rows[rk], rows[piv] = rows[piv], rows[rk]
        inv = 1 / rows[rk][c]
        rows[rk] = [x * inv for x in rows[rk]]
        for i in range(len(rows)):
            if i != rk and rows[i][c]:
                f = rows[i][c]
                rows[i] = [x - f * y for x, y in zip(rows[i], rows[rk])]
        rk += 1
    return rk


def query_matrix(x, y):
    n = len(x)
    return [[(1 if i == j else 0) - 2 * x[i] * y[j] for j in range(n)] for i in range(n)]


def matvec(M, v):
    return [sum(a * b for a, b in zip(row, v)) for row in M]


def vecmat(v, M):
    return [sum(v[i] * M[i][j] for i in range(len(v))) for j in range(len(M[0]))]


def matmul(A, B):
    cols = list(zip(*B))
    return [[sum(a * b for a, b in zip(row, col)) for col in cols] for row in A]


# ======================================================================================================= A
SHAPE = ([1] * 9, [1] * 9)


def chain_data():
    S = C.sites(*SHAPE)
    full = [s for s in S if s[2] is not None]
    need(len(full) == 18 and len(S) == 21, 'chain-nested root has 18 full sites and 3 thin queries')
    return S, full


def phi_len(t, length):
    return (8 * length) ** t


def chain_bound(g, t):
    return sum(phi_len(t, s) for s in range(1, g))


def min_cover(d, phi):
    """Exact minimum of sum phi(|S|) over multisets of nonempty site sets covering site k at least d[k] times.
    Sites are interchangeable, so the state is the sorted remaining demand."""
    @lru_cache(maxsize=None)
    def f(rem):
        if not any(rem):
            return 0.0
        pos = [i for i, x in enumerate(rem) if x]
        best = float('inf')
        for mask in range(1, 1 << len(pos)):
            r = list(rem)
            cnt = 0
            for i in range(len(pos)):
                if mask >> i & 1:
                    r[pos[i]] -= 1
                    cnt += 1
            v = phi(cnt) + f(tuple(sorted(r, reverse=True)))
            if v < best:
                best = v
        return best
    return f(tuple(sorted(d, reverse=True)))


def conj(c):
    return [sum(1 for x in c if x >= j) for j in range(1, (max(c) if c else 0) + 1)]


def majorized(r, s):
    """True if r is majorized by s (equal sums, partial sums of the decreasing rearrangement)."""
    n = max(len(r), len(s))
    r = sorted(r, reverse=True) + [0] * (n - len(r))
    s = sorted(s, reverse=True) + [0] * (n - len(s))
    if sum(r) != sum(s):
        return False
    a = b = 0
    for x, y in zip(r, s):
        a += x
        b += y
        if a > b:
            return False
    return True


def cover_cost(sets, t):
    return sum(phi_len(t, len(S)) for S in sets)


def check_cover_literal():
    S, full = chain_data()
    caller = jload('retained/pr6833/CALLER.json')
    need(caller['sL'] == [1] * 9 and caller['sR'] == [1] * 9, 'literal caller has the (9|9) shape')
    idle = [e[2] for e in caller['events'] if e[0] == 'IDLE_ONE']
    need(len(idle) == 16 and not any(e[0] == 'IDLE' for e in caller['events']), '16 single-coordinate idle jobs')
    demand = {k + 1: len(full[k][2]) - 2 for k in range(18)}
    need([demand[k] for k in range(1, 19)] == list(range(0, 9)) + list(range(8, -1, -1)), 'demand i at site i, mirrored')
    count = Counter(k for st in idle for k in st)
    need(all(count[k] == demand[k] for k in range(1, 19)), 'literal idle jobs cover every site exactly demand times')
    need(all(len(st) == len(set(st)) for st in idle), 'no stage repeated inside an idle job')
    need(all(set(st) <= set(range(1, 10)) or set(st) <= set(range(10, 19)) for st in idle), 'every literal job lies on one side')
    lens = sorted(len(st) for st in idle)
    need(lens == sorted(list(range(1, 9)) * 2), 'literal job lengths are 1..8 on each side')
    need(sorted(len(L[2]) for L in C.lines(*SHAPE)) == sorted(list(range(1, 9)) * 2), 'chain lines of the family')
    rows = []
    for t in (0.1, 0.5, 0.9, 1 - 0.0033718004754967, 0.999):
        lit = sum(phi_len(t, len(st)) for st in idle)
        need(abs(lit - 2 * chain_bound(9, t)) <= 1e-12 * lit, 'literal cost equals the bound')
        rows.append((t, lit))
    # the literal lines are the family's exact rank-one idle lines (algebra checked by chain_root)
    OUT['A_literal'] = dict(root=C.verify_root(*SHAPE), idle_jobs=16, lengths_per_side=list(range(1, 9)), t_grid=[r[0] for r in rows])
    return idle, demand


def check_cover_exhaustive():
    res = {}
    for g in range(2, 10):
        d = list(range(1, g))
        for t in (0.05, 0.3, 0.5, 0.8, 0.9966, 0.99999):
            lo = min_cover(d, lambda n, t=t: phi_len(t, n))
            hi = chain_bound(g, t)
            need(abs(lo - hi) <= 1e-9 * hi, ('minimum cover differs from chain', g, t, lo, hi))
        res[g] = 'min = sum_{s=1..g-1} (8s)^t at six exponents'
    OUT['A_exhaustive_min_cover'] = res


def check_cover_random():
    rnd = random.Random(20261107)
    trials = 0
    for _ in range(4000):
        g = rnd.randint(2, 10)
        d = list(range(1, g))
        sets = []
        cnt = [0] * (g - 1)
        for _ in range(rnd.randint(0, 5)):
            S_ = [i for i in range(g - 1) if rnd.random() < 0.5]
            if S_:
                sets.append(S_)
                for i in S_:
                    cnt[i] += 1
        while any(cnt[i] < d[i] for i in range(g - 1)):
            deficient = [i for i in range(g - 1) if cnt[i] < d[i]]
            S_ = [i for i in deficient if rnd.random() < 0.6] or [rnd.choice(deficient)]
            S_ += [i for i in range(g - 1) if i not in S_ and rnd.random() < 0.2]
            sets.append(S_)
            for i in S_:
                cnt[i] += 1
        lens = [len(S_) for S_ in sets]
        cstar = conj(cnt)
        need(majorized(lens, cstar), 'job lengths are majorized by the conjugate of the column sums')
        for t in (0.1, 0.5, 0.9, 0.9966):
            need(cover_cost(sets, t) >= chain_bound(g, t) * (1 - 1e-12), 'random cover below the chain bound')
        trials += 1
    OUT['A_random_covers'] = trials


def thin_product(S):
    n = len(S[0][0])
    Tm = [[Q(int(i == j)) for j in range(n)] for i in range(n)]
    Ti = [r[:] for r in Tm]
    for x, y, mask, kind, _ in S:
        if kind != 'Q':
            continue
        R = [[x[i] * y[j] for j in range(n)] for i in range(n)]
        Tm = matmul([[(1 if i == j else 0) - 2 * R[i][j] for j in range(n)] for i in range(n)], Tm)
        Ti = matmul(Ti, [[(1 if i == j else 0) + 2 * R[i][j] for j in range(n)] for i in range(n)])
    return Tm, Ti


def spanning_dims(sL, sR, transport=True, same_side=False):
    """Dimension of idle vectors at an L site transported through the thin queries to an idle vector at an R site."""
    S = C.sites(sL, sR)
    n = len(S[0][0])
    Tm, Ti = thin_product(S)
    if not transport:
        Tm = [[Q(int(i == j)) for j in range(n)] for i in range(n)]
        Ti = [r[:] for r in Tm]
    Ls = [s for s in S if s[3] == 'L']
    Rs = [s for s in S if s[3] == 'R']
    dims = []
    for (xi, yi, Mi, _, _) in Ls:
        for (xm, ym, Mm, _, _) in (Ls if same_side else Rs):
            # phi: supported in Mi, y_i phi = 0, T phi supported in Mm, y_m T phi = 0
            rows = [[Q(int(c == a)) for c in range(n)] for a in range(n) if a not in Mi]
            rows.append(yi[:])
            rows += [Tm[c][:] for c in range(n) if c not in Mm]
            rows.append(vecmat(ym, Tm))
            dphi = n - rank_of(rows)
            # gamma: supported in Mi, gamma x_i = 0, gamma T^-1 supported in Mm, gamma T^-1 x_m = 0
            rows = [[Q(int(c == a)) for c in range(n)] for a in range(n) if a not in Mi]
            rows.append(xi[:])
            rows += [[Ti[r][c] for r in range(n)] for c in range(n) if c not in Mm]
            rows.append(matvec(Ti, xm))
            dgam = n - rank_of(rows)
            dims.append((dphi, dgam))
    return dims


def check_cross_side():
    res = {}
    for g in (3, 4, 9):
        dims = spanning_dims([1] * g, [1] * g)
        need(all(d == (0, 0) for d in dims), ('a transported idle line exists', g))
        res['g=%d' % g] = '%d (L site, R site) pairs, both line spaces zero' % len(dims)
    OUT['A_no_spanning_line'] = res
    # control: without transport and at one site the same computation reports a nonzero space
    pos = spanning_dims([1] * 4, [1] * 4, transport=False, same_side=True)
    need(any(d[0] > 0 and d[1] > 0 for d in pos), 'control: untransported same-side vectors exist')
    CTL['A_spanning_scan_is_sensitive'] = 'same computation, no thin queries, same side: dimensions %s' % sorted(set(pos))[-1:]


def check_cover_controls(idle):
    # 1. convex price: the chain stops being optimal (hypothesis 0<t<1)
    t = 1.5
    d = [1, 2, 3]
    cv = min_cover(d, lambda n: phi_len(t, n))
    need(cv < chain_bound(4, t) - 1e-9, 'control: convex price must break the bound')
    CTL['A_convex_price'] = 'g=4, exponent 1.5: minimum %.3f < chain %.3f' % (cv, chain_bound(4, t))
    # 2. jobs allowed to span both sides: cheaper than two one-sided chains
    t = 0.5
    joint = min_cover([1, 2, 3, 1, 2, 3], lambda n: phi_len(t, n))
    need(joint < 2 * chain_bound(4, t) - 1e-9, 'control: spanning jobs must lower the minimum')
    CTL['A_spanning_jobs_allowed'] = 'g=4, exponent 0.5: joint minimum %.3f < 2 x %.3f' % (joint, chain_bound(4, t))
    # 3. active part of rank 3 instead of 2: demand drops by one and so does the bound
    d3 = [k - 1 for k in range(1, 4)]
    lo = min_cover([x for x in d3 if x], lambda n: phi_len(t, n))
    need(lo < chain_bound(4, t) - 1e-9, 'control: rank-3 active part must lower the minimum')
    CTL['A_active_rank_three'] = 'demands %s: minimum %.3f < chain %.3f' % (d3, lo, chain_bound(4, t))
    # 4. literal word: delete one idle job and the coverage count fails
    S, full = chain_data()
    demand = {k + 1: len(full[k][2]) - 2 for k in range(18)}

    def covered(jobs):
        cnt = Counter(k for st in jobs for k in st)
        need(all(cnt[k] == demand[k] for k in range(1, 19)), 'coverage')
    covered(idle)
    for i in (0, 5, 15):
        expect_error(lambda i=i: covered(idle[:i] + idle[i + 1:]), 'coverage')
    CTL['A_deleted_literal_job'] = 'deleting any of three tested idle jobs breaks coverage'
    # 5. the Schur step is not vacuous: a non-chain cover of the same demand costs strictly more
    t = 0.5
    alt = [[0, 1, 2], [1, 2], [2]]
    need(abs(cover_cost(alt, t) - chain_bound(4, t)) < 1e-12, 'control: the chain itself')
    alt2 = [[1, 2], [1, 2], [0, 2]]
    need(cover_cost(alt2, t) > chain_bound(4, t) + 1e-9, 'control: other lengths cost more at 0<t<1')
    CTL['A_other_lengths_cost_more'] = 'lengths (2,2,2) instead of (3,2,1), exponent 0.5: %.3f > %.3f' % (cover_cost(alt2, t), chain_bound(4, t))


# ======================================================================================================= B
def random_D(rnd, ks):
    return {k: Q(rnd.randint(2, 9), rnd.randint(2, 9)) for k in ks}


def root_product(vecs, masks, D, n):
    """Product of Delta_k T_k in time order; vecs[k]=(x,y), masks[k]=set or None, D[k] variable."""
    K = [[Q(int(i == j)) for j in range(n)] for i in range(n)]
    for k, (x, y) in enumerate(vecs):
        yK = vecmat(y, K)
        K = [[K[i][j] - 2 * x[i] * yK[j] for j in range(n)] for i in range(n)]
        if masks[k] is not None:
            for i in masks[k]:
                K[i] = [D[k] * v for v in K[i]]
    return K


def delta_total(masks, D, n):
    out = [Q(1)] * n
    for k, m in enumerate(masks):
        if m is not None:
            for i in m:
                out[i] *= D[k]
    return out


def check_root_identity(vecs, masks, n, rnd, trials=3, tag=''):
    for _ in range(trials):
        D = random_D(rnd, [k for k, m in enumerate(masks) if m is not None])
        K = root_product(vecs, masks, D, n)
        dt = delta_total(masks, D, n)
        need(all(K[i][j] == (-dt[i] if i == j else 0) for i in range(n) for j in range(n)),
             'product of stages is minus the target diagonal ' + tag)


def gram_objects(vecs, masks, D, n):
    """Z = I + 2L - G for the conjugated rank-one factors (Lemma 3.1 of PROOF.md)."""
    N = len(vecs)
    dpre = []
    cur = [Q(1)] * n
    for k in range(N):
        dpre.append(cur[:])
        if masks[k] is not None:
            cur = [cur[i] * (D[k] if i in masks[k] else 1) for i in range(n)]
    xh = [[vecs[k][0][i] / dpre[k][i] for i in range(n)] for k in range(N)]
    yh = [[vecs[k][1][i] * dpre[k][i] for i in range(n)] for k in range(N)]
    g = [[sum(a * b for a, b in zip(yh[k], xh[l])) for l in range(N)] for k in range(N)]
    Z = [[Q(1) if k == l else (g[k][l] if k > l else -g[k][l]) for l in range(N)] for k in range(N)]
    return Z


def check_chain_top():
    rnd = random.Random(7)
    S, full = chain_data()
    n = len(S[0][0])
    vecs = [(s[0], s[1]) for s in S]
    masks = [s[2] for s in S]
    check_root_identity(vecs, masks, n, rnd, tag='(chain)')
    D = random_D(rnd, [k for k, m in enumerate(masks) if m is not None])
    Z = gram_objects(vecs, masks, D, n)
    N = len(Z)
    need(all(Z[k][l] * Z[l][k] == 1 for k in range(N) for l in range(N) if k != l), 'Z_kl Z_lk = 1')
    need(all(Z[i][k] == Z[i][j] * Z[j][k] for i in range(N) for j in range(N) for k in range(N)), 'Z is rank one (cocycle)')
    fullidx = [k for k, m in enumerate(masks) if m is not None]
    first, last = fullidx[0], fullidx[-1]
    prod = Q(1)
    for h in fullidx[:-1]:
        prod *= D[h]
    need(Z[last][first] == prod, 'Z_{last,first} is the product of all D except the last')
    # field data: masks as sets of full-site positions
    pos = defaultdict(set)
    for p, k in enumerate(fullidx):
        for f in masks[k]:
            pos[f].add(p)
    allf = [f for f in range(n) if len(pos[f]) == 18]
    need(allf == [0], 'exactly one field lies in all 18 full masks')
    ranks = sorted((8 * len(pos[f]) + 1 for f in range(n)), reverse=True)
    need(ranks[:3] == [145, 73, 73] and sum(ranks[:3]) == 291, 'top three targets')
    # residual identity: for every ordered pair of full sites, the fields whose masks contain the whole interval
    # carry exactly the sign Gram value; the other fields' monomials cancel (checked at random D below)
    for a in range(18):
        for b in range(18):
            if a == b:
                continue
            lo, hi = min(a, b), max(a, b)
            ka, kb = fullidx[a], fullidx[b]
            tot = sum(vecs[ka][1][f] * vecs[kb][0][f] for f in range(n) if set(range(lo, hi + 1)) <= pos[f])
            need(tot == (1 if a > b else -1), 'interval-covering fields carry the sign Gram value')
    res = {}
    for l in range(1, 17):
        cand = [f for f in range(1, n) if set(range(0, l + 1)) <= pos[f] or set(range(l, 18)) <= pos[f]]
        need(cand, ('middle site without a prefix or suffix field', l))
        res[l] = cand[:1]
    covers = {}
    prefix = [f for f in range(1, n) if 0 in pos[f] and max(pos[f]) >= 8 and set(range(0, 9)) <= pos[f]]
    suffix = [f for f in range(1, n) if set(range(9, 18)) <= pos[f]]
    need(prefix and suffix, 'a prefix field and a suffix field exist')
    OUT['B_chain'] = dict(top_three=ranks[:3], all_field=allf, middle_sites_checked=16,
                          prefix_field_sites=len(pos[prefix[0]]), suffix_field_sites=len(pos[suffix[0]]),
                          rank_one_Z_entries=N * N)
    # controls
    bad = [(x[:], y[:]) for x, y in vecs]
    bad[7][0][1] += 1
    expect_error(lambda: check_root_identity(bad, masks, n, rnd, 1, 'ctl'), 'product of stages')
    CTL['B_perturbed_query'] = 'one query vector changed: root identity rejected'
    flip = [row[:] for row in Z]
    flip[5][2] = -flip[5][2]
    need(not all(flip[k][l] * flip[l][k] == 1 for k in range(N) for l in range(N) if k != l), 'control')
    CTL['B_flipped_gram_sign'] = 'one sign changed: Z_kl Z_lk = 1 fails'
    return vecs, masks, n


def triple_lemma():
    """Six residual-free pairs among sites i<l<m force a contradiction in characteristic not two."""
    vals = [Q(a, b) for a in range(-4, 5) for b in range(1, 4) if a]
    vals = sorted(set(vals))
    solutions = 0
    ctl_solutions = 0
    for ai in vals:
        # b_i a_l = -1, b_i a_m = -1, b_m a_l = 1, b_m a_i = 1, b_l a_i = 1, b_l a_m = -1
        for al in vals:
            for am in vals:
                bi = -1 / al
                bm = 1 / al
                bl = 1 / ai
                ok = (bi * am == -1 and bm * ai == 1 and bl * am == -1)
                solutions += ok
                ok2 = (bi * am == -1 and bm * ai == 1 and bl * am == 1)  # one sign flipped: control
                ctl_solutions += ok2
    need(solutions == 0, 'the six sign equations have a solution')
    need(ctl_solutions > 0, 'control: flipped sign pattern must be solvable')
    OUT['B_triple_lemma'] = 'no solution on a grid of %d rational values per unknown' % len(vals)
    CTL['B_triple_flipped_sign'] = 'with one right-hand side sign flipped the same grid has %d solutions' % ctl_solutions


def check_pr6726_root():
    root = jload('retained/pr6726/ROOT.json')
    n = root['fields']
    full = root['full_sites']
    masks_bits = root['masks']
    sizes = root['child_sizes']
    need(n == 8 and len(full) == 6 and sizes == [4, 4, 1, 1, 4, 4], 'shape of the #6726 root')
    Rs = [[[Q(x) for x in row] for row in M] for M in root['queries']]
    need(len(Rs) == 9, 'nine queries')
    masks = []
    vecs = []
    for k, R in enumerate(Rs):
        j = next(c for c in range(n) if any(R[r][c] for r in range(n)))
        x = [R[r][j] for r in range(n)]
        i = next(r for r in range(n) if x[r])
        y = [R[i][c] / x[i] for c in range(n)]
        need(all(R[r][c] == x[r] * y[c] for r in range(n) for c in range(n)), 'rank-one query')
        need(sum(a * b for a, b in zip(x, y)) == 0, 'square-zero query')
        vecs.append((x, y))
        if k in full:
            m = {f for f in range(n) if masks_bits[full.index(k)] >> f & 1}
            need(all(not x[f] and not y[f] for f in range(n) if f not in m), 'query inside its support')
            masks.append(m)
        else:
            masks.append(None)
    rnd = random.Random(11)
    check_root_identity(vecs, masks, n, rnd, 3, '(#6726)')
    pos = defaultdict(list)
    for p, k in enumerate(full):
        for f in masks[k]:
            pos[f].append(p)
    rank = {f: 8 * sum(sizes[p] for p in pos[f]) + 1 for f in range(n)}
    top = sorted(rank.values(), reverse=True)
    allf = [f for f in range(n) if len(pos[f]) == 6]
    need(allf == [0] and top[:3] == [145, 73, 73] and sum(top[:3]) == 291, 'top triple of the #6726 root')
    for l in range(1, 5):
        cand = [f for f in range(1, n) if set(range(0, l + 1)) <= set(pos[f]) or set(range(l, 6)) <= set(pos[f])]
        need(cand, ('#6726 middle site', l))
    OUT['B_pr6726_root'] = dict(target_ranks=sorted(rank.values(), reverse=True), all_field=allf)
    return root, masks, full, sizes


# ======================================================================================================= C
def incidence(masks_by_site, n):
    return tuple(frozenset(f for f in range(n) if f in m) for m in masks_by_site)


def isomorphic(inc1, inc2, n):
    for perm in itertools.permutations(range(n)):
        if all(frozenset(perm[f] for f in a) == b for a, b in zip(inc1, inc2)):
            return perm
    return None


def outer_hist(w):
    T, P = Counter(), Counter()
    for e in w['events']:
        if e[0] == 'QUERY':
            P[1] += 1
        elif e[0] == 'IDLE':
            P[8 * len(e[3])] += 2
        elif e[0] == 'IDLE_ONE':
            P[8 * len(e[2])] += 1
    for t in w['diagonal']:
        T[int(t[0] % 2) + 8 * sum(t[2:])] += 1
    return T, P


def census(w):
    rows, n, width, cols = W.init(w)
    cls = defaultdict(list)
    for r in range(n):
        cls[tuple(w['diagonal'][r])].append(r)
    hits, gaps = [], []
    for k, e in enumerate(w['events']):
        W.step(rows, e, width, cols)
        if e[0] in ('ADD', 'SCALE', 'SWAP'):
            continue
        P = lambda i: {j: rows[i][j] for j in range(n) if rows[i][j]}  # noqa: E731
        for tg, G in cls.items():
            for m, kd in W.candidates(rows, G, n):
                trivial = ((m[0] % 4 == 0 and not any(m[1:])) or
                           ((m[0] - tg[0]) % (4 if kd == 0 else 2) == 0 and list(m[1:]) == list(tg[1:])))
                if trivial:
                    continue
                V, A, ds, Gram = pair_lattices(P, range(n), G, range(n), W.sdef(m, kd))
                if V and A:
                    rep = gram_report(Gram)
                    if rep['rank']:
                        (hits if rep['units'] else gaps).append((k, tuple(G), m[0], kd, rep['units'], rep['rank']))
    return hits, gaps


def check_retirement(root):
    n = root['fields']
    full = root['full_sites']
    sizes = root['child_sizes']
    bits = root['masks']
    wit = jload('retained/pr6726/RETIREMENT-WITNESSES.json')
    unret = jload('retained/pr6726/CALLER-UNRETIRED.json')
    final = jload('retained/pr6726/CONTROLLER.json')
    need([(w['pivot'], tuple(w['prefix_stages'])) for w in wit] == [(6, (5, 6, 7, 8)), (4, (10,))], 'two witnesses')
    # stage numbering: site p owns the next sizes[p] stages
    stages = []
    s = 1
    for z in sizes:
        stages.append(list(range(s, s + z)))
        s += z
    masks = [{f for f in range(n) if bits[p] >> f & 1} for p in range(6)]
    # witness 1 retires the part of field 6 at stages 5..8 = site 1; witness 2 retires field 4's part at stage block of site 4
    # old and new targets are read from the literal callers
    old6 = {k for k in range(1, 19) if unret['diagonal'][6][1 + k]}
    need(old6 == set(stages[1]) | set(stages[2]), 'field 6 target before retirement: sites 1 and 2')
    removed = [(6, 1), (4, 4)]
    need(set(wit[0]['prefix_stages']) == set(stages[1]), 'first witness prefix is the stage block of site 1')
    old4 = {k for k in range(1, 19) if unret['diagonal'][4][1 + k]}
    need(old4 == set(stages[3]) | set(stages[4]), 'field 4 target before retirement: sites 3 and 4')
    need(set(range(11, 15)) == set(stages[4]) and set(wit[1]['prefix_stages']) == set(stages[3]), 'second witness keeps site 3 (stage 10) and releases site 4')
    reduced = [set(m) for m in masks]
    for f, p in removed:
        need(f in reduced[p], 'removed field is in the mask')
        reduced[p].discard(f)
    need([len(m) for m in reduced] == [2, 3, 4, 4, 3, 2], 'reduced stage ranks (2,3,4,4,3,2)')
    gate_sites = [s for s in C.sites([4, 4, 1], [1, 4, 4]) if s[2] is not None]
    gate = [s[2] for s in gate_sites]
    perm = isomorphic(incidence(reduced, n), incidence(gate, n), n)
    need(perm is not None, 'reduced #6726 masks are the chain gate masks up to relabelling of fields')
    wrong = [set(m) for m in masks]
    wrong[2].discard(6)
    wrong[4].discard(4)
    need(isomorphic(incidence(wrong, n), incidence(gate, n), n) is None, 'control: wrong sites removed')
    CTL['C_wrong_masks_removed'] = 'removing field 6 at site 2 instead of site 1: not the chain gate masks'
    # outer histograms of the literal words
    g = outer_hist(C.build([4, 4, 1], [1, 4, 4]))
    tf, pf = outer_hist(final)
    dT = Counter(tf)
    dT.subtract(g[0])
    dP = Counter(pf)
    dP.subtract(g[1])
    need({k: v for k, v in dT.items() if v} == {32: 2} and {k: v for k, v in dP.items() if v} == {32: 2},
         '#6726 final caller = gate histograms + one cancelling pair of rank-32 jobs')
    tu, pu = outer_hist(unret)
    dT = Counter(tu)
    dT.subtract(g[0])
    need({k: v for k, v in dT.items() if v} == {41: 2, 9: -2}, 'unretired caller: two targets 41 where the gate has 9 and 32')
    OUT['C_masks'] = dict(reduced=[sorted(m) for m in reduced], gate_isomorphism=list(perm))
    OUT['C_outer_histograms'] = 'gate = #6726 final caller minus {T32:2, P32:2}'
    # census on the literal chain word; sensitivity control on the unretired #6726 caller
    caller = jload('retained/pr6833/CALLER.json')
    rows, nn, width, cols = W.init(caller)
    W.run(rows, caller['events'], width, cols)
    W.endpoint_is_diagonal(caller, rows, nn)
    hits, gaps = census(caller)
    need(not hits and not gaps, ('retirement candidates in the chain word', hits, gaps))
    h26, g26 = census(unret)
    need(h26 == [(158, (6, 7), 0, 0, 1, 1), (383, (4, 5), 1, -1, 1, 1), (392, (4, 5), 1, -1, 1, 1)] and not g26,
         ('census of the unretired caller', h26))
    OUT['C_census'] = dict(chain_word_events=len(caller['events']), chain_word_hits=0,
                           unretired_pr6726_hits=[list(map(str, h)) for h in h26])
    CTL['C_census_sensitivity'] = 'same census on the unretired #6726 caller finds its three known cuts'


# ======================================================================================================= D
class Params:
    def __init__(self, R, U, native_p, native_t, kappa_hint):
        self.R, self.U, self.np, self.nt, self.hint = R, U, native_p, native_t, kappa_hint
        self.cache = {}

    def rp(self, r, k):
        if not r:
            return Dec(0)
        key = (r, k)
        v = self.cache.get(key)
        if v is None:
            v = (Dec(r).ln() * (1 - k)).exp()
            self.cache[key] = v
        return v

    def nat(self, k):
        return sum((Dec(self.nt.get(r, 0)) - Dec(self.np.get(r, 0))) * self.rp(r, k) for r in set(self.nt) | set(self.np))


def entries(sL, sR, balanced=True):
    """Outer target and paid entries (m, off): rank = R*m + off; every entry is one job."""
    T, P = Counter(), Counter()

    def nodes(m):
        if m == 1:
            return
        T[(m, 1)] += 2
        P[(m, 0)] += 2
        nodes(m // 2)
        nodes(m - m // 2)
    for m in list(sL) + list(sR):
        nodes(m)
    N = sum(sL) + sum(sR)
    T[(N, 1)] += 1
    for i in range(len(sL)):
        T[(sum(sL[i:]), 1)] += 1
        if i >= 1:
            P[(sum(sL[i:]), 0)] += 1
    for m in range(len(sR)):
        T[(sum(sR[:m + 1]), 1)] += 1
        if m < len(sR) - 1:
            P[(sum(sR[:m + 1]), 0)] += 1
    gL, gR = len(sL), len(sR)
    if (1 + gL + gR) % 2:
        T[(0, 1)] += 1
    nth = 3 if (gL % 2) == (gR % 2) else 2
    P[(0, 1)] += nth + sum(m - 1 for m in list(sL) + list(sR))
    return T, P


def ledger(p, sL, sR, k, calls):
    T, P = entries(sL, sR)
    tot = Dec(0)
    for key, c in T.items():
        tot += p.U * c * p.rp(p.R * key[0] + key[1], k)
    for key, c in P.items():
        tot -= p.U * c * p.rp(p.R * key[0] + key[1], k)
    return tot + calls * p.nat(k)


def crossing(f, lo=Dec('0.001'), hi=Dec('0.006')):
    flo = f(lo)
    need(flo > 0 and f(hi) < 0, 'crossing bracket')
    for _ in range(170):
        mid = (lo + hi) / 2
        if f(mid) > 0:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def side_values(p, k, C_tree, amax):
    """All compositions of a (as cut sets), each with value and parity; keep the three best per (a, parity)."""
    AT = [p.U * p.rp(p.R * c + 1, k) if c else Dec(0) for c in range(amax + 1)]
    AP = [p.U * p.rp(p.R * c, k) if c else Dec(0) for c in range(amax + 1)]
    best = {}
    for a in range(1, amax + 1):
        heaps = {0: [], 1: []}
        cnt = 0
        # choose the set of inner cumulative sums among 1..a-1
        for mask in range(1 << (a - 1)):
            cum = [c for c in range(1, a) if mask >> (c - 1) & 1] + [a]
            prev = 0
            v = Dec(0)
            for c in cum:
                v += AT[c] + C_tree[c - prev]
                prev = c
            for c in cum[:-1]:
                v -= AP[c]
            par = len(cum) % 2
            h = heaps[par]
            item = (v, tuple(cum))
            if len(h) < 3:
                heapq.heappush(h, item)
            elif item[0] > h[0][0]:
                heapq.heapreplace(h, item)
            cnt += 1
        need(cnt == 2 ** (a - 1), 'all compositions enumerated')
        best[a] = {par: sorted(h, reverse=True) for par, h in heaps.items()}
    return best


def tree_costs(p, k, mmax):
    w = lambda m: 2 * p.U * (p.rp(p.R * m + 1, k) - p.rp(p.R * m, k)) - p.U  # noqa: E731
    Cb = {1: Dec(0)}
    for m in range(2, mmax + 1):
        Cb[m] = max(Cb[a] + Cb[m - a] for a in range(1, m // 2 + 1)) + w(m)
    return Cb, w


def all_trees_best(w, m):
    """Best total over every binary tree with m leaves, by explicit enumeration of the splits (independent of the table)."""
    @lru_cache(maxsize=None)
    def go(m):
        if m == 1:
            return [Dec(0)]
        out = []
        for a in range(1, m):
            for x in go(a):
                for y in go(m - a):
                    out.append(x + y + w(m))
        return out
    return max(go(m))


def exhaustive_shapes(p, k, calls=18, N=18):
    Cb, w = tree_costs(p, k, N)
    for m in range(2, 8):
        need(all_trees_best(w, m) == Cb[m], 'tree table equals explicit enumeration')
    best = side_values(p, k, Cb, N)
    nk = calls * p.nat(k)
    top = []
    for aL in range(0, N + 1):
        aR = N - aL
        for pL in (0, 1):
            for pR in (0, 1):
                Ls = [(Dec(0), ())] if aL == 0 and pL == 0 else (best[aL].get(pL, []) if aL else [])
                Rs = [(Dec(0), ())] if aR == 0 and pR == 0 else (best[aR].get(pR, []) if aR else [])
                for vl, cl in Ls:
                    for vr, cr in Rs:
                        t = 3 if pL == pR else 2
                        v = vl + vr + p.U * p.rp(p.R * N + 1, k) - p.U * t + (p.U if t == 3 else 0) + nk
                        top.append((v, cl, cr))
    top.sort(key=lambda x: -x[0])
    return top, Cb


def shape_from_cuts(cum):
    prev = 0
    out = []
    for c in cum:
        out.append(c - prev)
        prev = c
    return out


def dp_best(p, k, N, scale):
    """Dynamic program of the same ledger; native histogram scaled by `scale` calls (model when scale != 18)."""
    Cb, w = tree_costs(p, k, N)
    NEG = Dec(-10 ** 9)
    E = [[NEG, NEG] for _ in range(N + 1)]
    E[0][0] = Dec(0)
    for a in range(1, N + 1):
        for s in range(1, a + 1):
            for par in (0, 1):
                pv = E[a - s][1 - par]
                if pv <= NEG / 2:
                    continue
                idle = p.U * p.rp(p.R * (a - s), k) if a - s > 0 else 0
                v = pv - idle + p.U * p.rp(p.R * a + 1, k) + Cb[s]
                if v > E[a][par]:
                    E[a][par] = v
    res = None
    for aL in range(0, N + 1):
        aR = N - aL
        for pL in (0, 1):
            for pR in (0, 1):
                if (aL == 0 and pL) or (aR == 0 and pR):
                    continue
                vL, vR = E[aL][pL], E[aR][pR]
                if vL < NEG / 2 or vR < NEG / 2:
                    continue
                t = 3 if pL == pR else 2
                v = vL + vR + p.U * p.rp(p.R * N + 1, k) - p.U * t + (p.U if t == 3 else 0) + scale * p.nat(k)
                if res is None or v > res[0]:
                    res = (v, aL, aR)
    return res


def native_complex():
    res = jload('retained/pr6833/RESULT.json')['local']
    return ({int(r): c for r, c in res['paid'].items()}, {int(r): c for r, c in res['helpers'].items()})


def native_bit():
    w = json.loads(gzip.decompress((HERE / 'retained/pr6726/bit/BIT-NATIVE-WORD.json.gz').read_bytes()))
    paid, helpers, _ = AB.source_audit(w)
    return dict(paid), dict(helpers)


def check_shapes():
    rnd = random.Random(5)
    # 1. ledger against the family's formula and against literal words
    for _ in range(60):
        gL, gR = rnd.randint(1, 4), rnd.randint(1, 4)
        sL = [rnd.randint(1, 5) for _ in range(gL)]
        sR = [rnd.randint(1, 5) for _ in range(gR)]
        T, P = entries(sL, sR)
        t, pp = C.outer_formula(sL, sR)
        need(Counter({8 * m + o: c for (m, o), c in T.items()}) == Counter(t) and
             Counter({8 * m + o: c for (m, o), c in P.items()}) == Counter(pp), 'ledger entries equal the chain-root formula')
    for sh in ([4, 4, 1], [1, 4, 4]), ([3, 2], [5, 1, 1]), ([2, 3, 1, 1], [7]), ([1] * 9, [1] * 9):
        w = C.build(*sh)
        T, P = entries(*sh)
        lt, lp = outer_hist(w)
        need(Counter({8 * m + o: c for (m, o), c in T.items()}) == lt and
             Counter({8 * m + o: c for (m, o), c in P.items()}) == lp, ('ledger equals literal word', sh))
    OUT['D_ledger'] = 'entries() equals chain_root.outer_formula on 60 random shapes and the literal events of 4 built words'
    caller = jload('retained/pr6833/CALLER.json')
    lt, lp = outer_hist(caller)
    T, P = entries([1] * 9, [1] * 9)
    need(Counter({8 * m + o: c for (m, o), c in T.items()}) == lt and Counter({8 * m + o: c for (m, o), c in P.items()}) == lp,
         'ledger equals the literal CALLER.json')
    # 2. complex histogram: crossing of the literal word, then the exhaustive search
    npaid, nhelp = native_complex()
    pc = Params(8, 104, npaid, nhelp, None)
    Tl, Pl = lt, lp
    nat_calls = 18

    def F_lit(k):
        s = Dec(0)
        for r, c in Tl.items():
            s += 104 * c * pc.rp(r, k)
        for r, c in Pl.items():
            s -= 104 * c * pc.rp(r, k)
        return s + nat_calls * pc.nat(k)
    k0 = crossing(F_lit)
    need(Dec('0.0033718004754') < k0 < Dec('0.0033718004755'), 'crossing of the literal chain word')
    need(abs(ledger(pc, [1] * 9, [1] * 9, k0, 18) - F_lit(k0)) < Dec('1e-30'), 'ledger equals the literal invoice at the crossing')
    top, Cb = exhaustive_shapes(pc, k0)
    need(top[0][1] == tuple(range(1, 10)) and top[0][2] == tuple(range(1, 10)), 'best complex shape is (9|9)')
    need(abs(top[0][0]) < Dec('1e-9'), 'best complex value is the crossing')
    need(all(v < Dec('-0.1') for v, _, _ in top[1:]), 'every other complex shape is strictly worse')
    dpv = dp_best(pc, k0, 18, 18)
    need(abs(dpv[0] - top[0][0]) < Dec('1e-30') and (dpv[1], dpv[2]) == (9, 9), 'dynamic program agrees with the exhaustive search')
    h = Dec('1e-9')
    dF = (ledger(pc, [1] * 9, [1] * 9, k0 + h, 18) - ledger(pc, [1] * 9, [1] * 9, k0 - h, 18)) / (2 * h)
    need(dF < 0, 'F decreases through the crossing')
    OUT['D_complex_first_order_kappa_shift_of_runner_up'] = float(top[1][0] / (-dF))
    OUT['A_per_side_bound_at_crossing'] = chain_bound(9, 1 - float(k0))
    OUT['D_complex'] = dict(kappa_crossing=str(k0)[:20], best=[shape_from_cuts(top[0][1]), shape_from_cuts(top[0][2])],
                            best_value=float(top[0][0]), runner_up=[shape_from_cuts(top[1][1]), shape_from_cuts(top[1][2]), float(top[1][0])],
                            compositions_enumerated='all 2^17 side compositions of every side total up to 18')
    scaled = {}
    for N in range(10, 41):
        v = dp_best(pc, k0, N, N)
        scaled[N] = float(v[0])
    need(max(scaled, key=scaled.get) == 18 and all(v < -1e-3 for N, v in scaled.items() if N != 18), 'scaled-native model, complex')
    OUT['D_complex_scaled_model'] = {str(N): round(v, 4) for N, v in scaled.items() if N in (16, 17, 18, 19, 20)}
    # 3. binary histogram
    bp, bh = native_bit()
    pb = Params(7, 111, bp, bh, None)

    def F_bit(k):
        return ledger(pb, [1] * 9, [1] * 9, k, 18)
    kb = crossing(F_bit, Dec('0.001'), Dec('0.008'))
    need(Dec('0.0038525393934') < kb < Dec('0.0038525393935'), 'binary crossing of the (9|9) word')
    topb, _ = exhaustive_shapes(pb, kb)
    need(topb[0][1] == tuple(range(1, 10)) and topb[0][2] == tuple(range(1, 10)), 'best binary shape is (9|9)')
    need(abs(topb[0][0]) < Dec('1e-9') and all(v < Dec('-0.1') for v, _, _ in topb[1:]), 'binary margins')
    dpb = dp_best(pb, kb, 18, 18)
    need(abs(dpb[0] - topb[0][0]) < Dec('1e-30') and (dpb[1], dpb[2]) == (9, 9), 'binary dynamic program agrees')
    scaledb = {N: float(dp_best(pb, kb, N, N)[0]) for N in range(10, 41)}
    need(max(scaledb, key=scaledb.get) == 18 and all(v < -1e-3 for N, v in scaledb.items() if N != 18), 'scaled-native model, binary')
    dFb = (ledger(pb, [1] * 9, [1] * 9, kb + h, 18) - ledger(pb, [1] * 9, [1] * 9, kb - h, 18)) / (2 * h)
    need(dFb < 0, 'binary F decreases through the crossing')
    OUT['D_binary_first_order_kappa_shift_of_runner_up'] = float(topb[1][0] / (-dFb))
    OUT['D_binary'] = dict(kappa_crossing=str(kb)[:20], best=[shape_from_cuts(topb[0][1]), shape_from_cuts(topb[0][2])],
                           runner_up=[shape_from_cuts(topb[1][1]), shape_from_cuts(topb[1][2]), float(topb[1][0])])
    OUT['D_binary_scaled_model'] = {str(N): round(v, 4) for N, v in scaledb.items() if N in (16, 17, 18, 19, 20)}
    # controls
    wrong = Params(8, 104, npaid, nhelp, None)
    wrong.nt = dict(nhelp)
    wrong.nt[9] = nhelp[9] + 2
    kk = crossing(lambda k: ledger(wrong, [1] * 9, [1] * 9, k, 18))
    need(abs(kk - k0) > Dec('1e-6'), 'control: changing the native histogram moves the crossing')
    CTL['D_native_histogram_changed'] = 'two extra helper targets of rank 9 per call move the crossing by %.2e' % float(abs(kk - k0))
    bad = Counter({8 * m + o: c for (m, o), c in entries([9], [9])[0].items()})
    need(bad != lt, 'control: a different shape is not the literal word')
    CTL['D_other_shape_differs'] = 'ledger of (9|9) with two size-9 children differs from the literal word'
    lo_t = C.outer_formula([1] * 9, [1] * 9)
    need(Counter({8 * m + o: c for (m, o), c in entries([1] * 8, [1] * 10)[0].items()}) != Counter(lo_t[0]), 'control')
    CTL['D_shape_8_10_differs'] = '(8|10) ledger differs from the (9|9) literal histogram'


def main():
    check_pins()
    idle, _ = check_cover_literal()
    check_cover_exhaustive()
    check_cover_random()
    check_cross_side()
    check_cover_controls(idle)
    triple_lemma()
    check_chain_top()
    root, masks, full, sizes = check_pr6726_root()
    check_retirement(root)
    check_shapes()
    OUT['controls'] = CTL
    print(json.dumps(OUT, indent=1, sort_keys=True, default=str))
    print('PASS_CHAIN_IDLE_COVER_OPTIMAL')


if __name__ == '__main__':
    main()
