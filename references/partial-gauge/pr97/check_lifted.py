"""Release check (stdlib only) of the lifted-frame + late-copy bit side program, stacked with the staircase corner.

Input: certificates/round7/witness_<h>.json.gz: the side DAG (leaves = triples of [h], additions), outputs (c, T),
retained totals, links (donor x -> use (y, k)), the flag matrix F (integer h x h), the lift index j(n) of every
lifted addition and the late-copy decisions (early users, ordered late users) per node.

What is checked, from the witness alone:
 A. DAG semantics: disjoint supports; output (c,T) support = {S : c in S, S cap T = {c}}; retained = star(c).
 B. Compile: one slot per role, schedule order (dim span, id), links hand the donor's non-pivot slot to the linked
    use; late copies: the pivot of n climbs C_1 <= ... <= C_k (C_i = frames of users late[i:] intersected) and the
    copy for late user i is a gate (pivot, fresh slot) at C_i, placed in time as LATE as possible (just before the
    first of: its user's gate, the pivot's consumer gate, the next copy's slot). R = adds + outputs + retained - links.
 C. Dirty-scratch replay of the compiled program: word L J L^-1 V L J L^-1 V^-1 and its mirror, arbitrary scratch,
    over F2 and over Z, reads at the slot's last touch and at the end; targets must receive J L V x exactly
    (DAG values) and every slot is restored; over F2 every target also receives exactly x_T.
 D. Frames (exact over Q). Frame of addition n: M_n = span(n) + (U_n cap F_j(n)), U_n = common kernel of the root
    covectors reachable from n ((9I-J) t_T for an output to Y_T, 1 - 3 e_c for a retained use of c), F_j = first j
    rows of F. Nesting is a THEOREM given the combinatorial facts checked here:
      j(n) <= j(t) on every slot successor pair n -> t;  span(x) <= span(t) on every link pair (exact);
      span(n) <= every root frame n reaches directly (exact integer dot products);  F invertible.
    Then U_n <= U_t, so M_n <= M_t, M_n <= U_n <= every reachable root frame, and every late-copy frame C_i
    (an intersection of frames that all contain M_n) is nested. Dimensions (exact, see linalg.py):
      dim M_n = rank[span(n); F_j] - rank(K_n F_j^T)   (modular law; span(n) <= U_n; K_n spans the root covectors),
    with ranks by mod-p + Hadamard certificates, Bareiss when the mod-p rank is not full; late-copy intersections by
    exact Fraction bases. Rank of every chain step = difference of dimensions (nested), histogram vs claim.
 E. Frame reductions mod q = 2^31-1 (dimension-matched, so they are the reductions of the rational frames),
    G = I - J/9 nondegenerate on every frame of every step (Gram matrix invertible mod q => over Q), and the side
    lemma at ONE integer point (U, V of point_UV(h, 1), the random stream of independent/two-stage-bit/flag_existence.py): for every distinct step A -> B of
    rank r with 2r > h (retained copy edges 0 -> U_c included), U^T (P_B - P_A) U^-T and V^T (..) V^-T have the
    generic north-east pivots of f_r. (NE ranks mod q <= over Q <= f_r, so equality mod q proves it over Q.)
 F. Certificate: rt_histogram with the round-6 entrance corner and with the staircase corner (m-4h+2, h-2, h-5, 1^6),
    rank sum == s, moment.certify (exact), kappa = certificate_round3.evaluate(a_b, round-6 complex values).
Negative controls (CONTROL=1): see controls().
Usage: python3 check_lifted.py h [--no-generic]"""
import sys, os, json, random, time
from itertools import combinations
from collections import Counter, OrderedDict
from fractions import Fraction as Fr
from array import array
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from linalg import *

T0 = time.time()
def load_witness(h):
    import gzip
    with gzip.open(os.path.join(HERE, '..', '..', 'certificates', 'round7', 'witness_%d.json.gz' % h), 'rt') as fh:
        return json.load(fh)


def log(*a):
    print('[%5.0fs]' % (time.time() - T0), *a, flush=True)


# ----------------------------------------------------------------------------------------------- A. DAG
class Prog:
    def __init__(self, W):
        self.W = W; h = self.h = W['h']
        self.trip = list(combinations(range(h), 3)); v = self.v = len(self.trip)
        self.args = {int(n): (tuple(a) if a else None) for n, a in W['args'].items()}
        self.act = sorted(self.args)
        for n in self.act:
            if self.args[n] is None: assert 1 <= n <= v and tuple(W['leaf'][str(n)]) == self.trip[n - 1]
            else: assert all(a < n and a in self.args for a in self.args[n]), n
        self.sup = {}
        for n in self.act:
            if self.args[n] is None: self.sup[n] = 1 << (n - 1)
            else:
                a, b = self.args[n]; assert not self.sup[a] & self.sup[b], 'overlapping supports'
                self.sup[n] = self.sup[a] | self.sup[b]
        self.outputs = {(c, tuple(T)): n for c, T, n in W['outputs']}
        self.retained = {c: n for c, n in W['retained']}
        star = [sum(1 << i for i, t in enumerate(self.trip) if q in t) for q in range(h)]
        assert len(self.outputs) == 3 * v and len(self.retained) == h
        for (c, T), n in self.outputs.items():
            A, B = [q for q in T if q != c]; assert c in T and self.sup[n] == star[c] & ~star[A] & ~star[B]
        for c, n in self.retained.items(): assert self.sup[n] == star[c]
        roots = set(self.outputs.values()) | set(self.retained.values()); reach = set(); st = list(roots)
        while st:
            n = st.pop()
            if n in reach: continue
            reach.add(n)
            if self.args[n]: st.extend(self.args[n])
        assert reach == set(self.act), 'inactive nodes in witness'
        self.mL = {x: (y, k) for x, y, k in W['links']}
        self.j = {int(n): j for n, j in W['j'].items()}
        self.late = {int(n): (list(e), list(l)) for n, (e, l) in W['late'].items()}
        self.F = W['flag']


def trow(h, S): return [int(q in S) for q in range(h)]


def spans(pr):
    """independent triple subsets (exact: 0/1 rows with three ones, every minor < 3^(h/2) < Q31) and dims."""
    h = pr.h; assert 3 ** h < Q31 ** 2
    bas = {}; dn = {}
    for n in pr.act:
        if pr.args[n] is None: bas[n] = (n - 1,); dn[n] = 1; continue
        a, b = pr.args[n]; E = Echelon(Q31); keep = []
        for i in bas[a] + bas[b]:
            if len(E) == h: break
            if E.insert(trow(h, pr.trip[i])): keep.append(i)
        bas[n] = tuple(keep); dn[n] = len(keep)
    return bas, dn


def users_of(pr, dn):
    key = lambda n: (dn[n], n); users = {n: [] for n in pr.act}
    for n in sorted(pr.act, key=key):
        if pr.args[n]:
            for pos, x in enumerate(pr.args[n]): users[x].append(('gate', n, pos))
    for (c, T), n in sorted(pr.outputs.items()): users[n].append(('out', (c, T)))
    for c, n in sorted(pr.retained.items()): users[n].append(('ret', c))
    return users


# ----------------------------------------------------------------------------------------------- B. compile
def root_key(u): return ('out',) + u[1] if u[0] == 'out' else ('ret', u[1])


def compile_(pr, dn, users, late=True, defer=True, tamper=None):
    """returns ops (scalar program), chains (frame keys per slot), reads, R. tamper: negative-control hooks."""
    key = lambda n: (dn[n], n); order = sorted(pr.act, key=key); gpos = {n: i for i, n in enumerate(order)}
    linked = {r: x for x, r in pr.mL.items()}
    chains = []; edge = {}; reads = []; ops = []; deferred = []
    def new(first): chains.append(list(first)); return len(chains) - 1
    def assign(s, n, k):
        u = users[n][k]
        if u[0] == 'gate': edge[u[1], u[2]] = s
        else:
            chains[s] += [root_key(u), ('F',)]
            reads.append((s, [u[1][1]] if u[0] == 'out' else [T for T in pr.trip if u[1] in T]))
    def ufr(n, k):
        u = users[n][k]; return ('n', u[1]) if u[0] == 'gate' else root_key(u)
    for n in order:
        if pr.args[n] is None:
            piv = new([('0',), ('n', n)]); ops.append(('src', piv, n, n))
        else:
            a, b = pr.args[n]; sa, sb = edge.pop((n, 0)), edge.pop((n, 1))
            if n in pr.mL and pr.mL[n][0] == a: sa, sb = sb, sa          # the linked operand stays on the non-pivot
            piv, oth = sa, sb
            chains[piv].append(('n', n)); chains[oth].append(('n', n)); ops.append(('add', piv, oth, n))
            if n in pr.mL: y, k = pr.mL[n]; assign(oth, y, k)
            else: chains[oth].append(('F',))
        ks = [k for k in range(len(users[n])) if (n, k) not in linked]
        if late and n in pr.late:
            early, lt = pr.late[n]; assert sorted(early + lt) == ks, ('bad late decision', n)
        else: early, lt = ks[1:], [ks[0]]
        for k in early:
            f = new([('0',), ('n', n)]); ops.append(('copy', piv, f, n)); assign(f, n, k)
        for i, k in enumerate(lt):
            Ck = ufr(n, k) if i == len(lt) - 1 else ('c', n, tuple(lt[i:]))
            if tamper == 'nointersect' and i < len(lt) - 1: Ck = ufr(n, k)
            chains[piv].append(Ck)
            if i < len(lt) - 1:
                f = new([('0',), Ck]); deferred.append((n, i, f, k, lt[-1])); assign(f, n, k)
        k = lt[-1]
        if users[n][k][0] == 'gate': edge[users[n][k][1], users[n][k][2]] = piv
        else: assign(piv, n, k)
    assert not edge
    # place deferred copies: as late as possible, in order, before the user's gate and the pivot consumer's gate
    INF = len(order); byn = {}
    for (n, i, f, k, kl) in deferred: byn.setdefault(n, []).append((i, f, k, kl))
    ins = {}
    for n, lst in byn.items():
        lst.sort(); D = []
        for i, f, k, kl in lst:
            u, ul = users[n][k], users[n][kl]
            d = min(gpos[u[1]] if u[0] == 'gate' else INF, gpos[ul[1]] if ul[0] == 'gate' else INF)
            D.append(d)
        for t in range(len(D) - 2, -1, -1): D[t] = min(D[t], D[t + 1])
        for (i, f, k, kl), d in zip(lst, D):
            if not defer: d = gpos[n] + 1                                   # immediate copy (still a valid program)
            if tamper == 'aftercons' and n == tamper_node[0] and i == 0:
                ul = users[n][kl]; d = gpos[ul[1]] + 1                       # copy AFTER the pivot was consumed
            ins.setdefault(d, []).append((n, i, f))
    pivslot = {}
    for o in ops:
        if o[0] in ('src', 'add'): pivslot[o[3]] = o[1]
    out = []
    for o in ops:
        if o[0] in ('src', 'add'):
            for (n, i, f) in sorted(ins.get(gpos[o[3]], []), key=lambda z: (gpos[z[0]], z[1])):
                out.append(('copy', pivslot[n], f, n))
        out.append(o)
    for (n, i, f) in sorted(ins.get(INF, []) + [z for d, zs in ins.items() if d > INF for z in zs], key=lambda z: (gpos[z[0]], z[1])):
        out.append(('copy', pivslot[n], f, n))
    if tamper == 'dropcopy':
        idx = next(i for i, o in enumerate(out) if o[0] == 'copy' and o[3] in pr.late); out.pop(idx)
    R = len(chains); adds = sum(1 for n in pr.act if pr.args[n])
    assert R == adds + len(pr.outputs) + len(pr.retained) - len(pr.mL), 'role count'
    return out, chains, reads, R

tamper_node = [None]


# ----------------------------------------------------------------------------------------------- C. replay
def replay(pr, ops, reads, R, ring, rng, mirror=False, midread=True):
    trip, v = pr.trip, pr.v; tid = {T: i for i, T in enumerate(trip)}
    mod = (lambda z: z & 1) if ring == 2 else (lambda z: z)
    last = {}
    for i, o in enumerate(ops):
        last[o[1]] = i
        if o[0] != 'src': last[o[2]] = i
    readers = {}
    for s, Ts in reads: readers.setdefault(last[s] if midread else len(ops) - 1, []).append((s, Ts))
    x = [rng.randrange(-10**6, 10**6) for _ in range(v)]
    a0 = [rng.randrange(-10**6, 10**6) for _ in range(R)]; y0 = [rng.randrange(-10**6, 10**6) for _ in range(v)]
    a = list(a0); y = list(y0); src = [(o[1], o[2]) for o in ops if o[0] == 'src']
    def L(sg=None):
        for i, o in enumerate(ops):
            if o[0] == 'add': a[o[1]] += a[o[2]]
            elif o[0] == 'copy': a[o[2]] += a[o[1]]
            if sg is not None:
                for s, Ts in readers.get(i, ()):
                    for T in Ts: y[tid[T]] += sg * a[s]
    def Li():
        for o in reversed(ops):
            if o[0] == 'add': a[o[1]] -= a[o[2]]
            elif o[0] == 'copy': a[o[2]] -= a[o[1]]
    def V(sg):
        for s, n in src: a[s] += sg * x[n - 1]
    if not mirror: L(-1); Li(); V(+1); L(+1); Li(); V(-1)
    else: V(+1); L(+1); Li(); V(-1); L(-1); Li()
    if any(mod(p - q) for p, q in zip(a, a0)): return False
    val = {}
    for n in pr.act: val[n] = x[n - 1] if pr.args[n] is None else val[pr.args[n][0]] + val[pr.args[n][1]]
    want = list(y0)
    for (c, T), n in pr.outputs.items(): want[tid[T]] += val[n]
    for c, n in pr.retained.items():
        for T in trip:
            if c in T: want[tid[T]] += val[n]
    if any(mod(p - q) for p, q in zip(y, want)): return False
    if ring == 2 and any(mod(y[i] - y0[i] - x[i]) for i in range(v)): return False
    return True


# ----------------------------------------------------------------------------------------------- D. frames
class Frames:
    def __init__(self, pr, dn, bas, users):
        self.pr = pr; self.dn = dn; self.bas = bas; self.users = users; h = self.h = pr.h
        self.rootcov = {}
        for (c, T) in pr.outputs: self.rootcov[('out', c, T)] = [9 * int(q in T) - 3 for q in range(h)]
        for c in pr.retained: self.rootcov[('ret', c)] = [1 - 3 * int(q == c) for q in range(h)]
        rid = {k: i for i, k in enumerate(sorted(self.rootcov))}; self.rkeys = sorted(self.rootcov)
        self.rid = rid
        # slot successors (same for base and late compile: every free use of n is reached by one slot from n,
        # a donor's non-pivot slot goes on to its linked use) and direct roots
        linked = {r: x for x, r in pr.mL.items()}
        self.succ = {n: set() for n in pr.act}; self.droots = {n: set() for n in pr.act}
        def to(n, use):
            if use[0] == 'gate': self.succ[n].add(use[1])
            else: self.droots[n].add(rid[root_key(use)])
        for n in pr.act:
            for k, u in enumerate(users[n]):
                if (n, k) not in linked: to(n, u)
            if n in pr.mL: y, k = pr.mL[n]; to(n, users[y][k])

    def check_structure(self):
        """combinatorial / exact facts behind the nesting theorem."""
        pr, h = self.pr, self.h; bad_j = bad_link = bad_root = 0
        J = lambda n: self.pr.j.get(n, 0)
        for n in pr.act:
            if pr.args[n] is None: assert J(n) == 0
            for t in self.succ[n]:
                if J(n) > J(t): bad_j += 1
        for x, (y, k) in pr.mL.items():                                   # span(x) <= span(linked use target)
            u = self.users[y][k]
            if u[0] == 'gate':
                t = u[1]; E = Echelon(Q31)
                for i in self.bas[t]: E.insert(trow(h, pr.trip[i]))
                if not all(E.contains(trow(h, pr.trip[i])) for i in self.bas[x]): bad_link += 1
        for n in pr.act:                                                  # span(n) <= direct root frames
            for r in self.droots[n]:
                g = self.rootcov[self.rkeys[r]]
                if any(sum(gq * tq for gq, tq in zip(g, trow(h, pr.trip[i]))) for i in self.bas[n]): bad_root += 1
        # F invertible over Q (a nonzero determinant mod a prime)
        F_ok = rank_mod(self.pr.F, Q31) == h
        return bad_j, bad_link, bad_root, F_ok

    def cobases(self):
        """K_n: independent subset of the root covectors reachable from n, spanning all of them over Q
        (selection mod M127, valid by the Hadamard certificate on root covectors)."""
        pr, h = self.pr, self.h
        rows = [self.rootcov[k] for k in self.rkeys]
        mx = max(sum(x * x for x in r) for r in rows); assert mx ** h < M127 ** 2, 'Hadamard bound for K'
        key = lambda n: (self.dn[n], n); K = {}
        for n in sorted(pr.act, key=key, reverse=True):
            cand = sorted(self.droots[n]); srcs = sorted((K[t] for t in self.succ[n]), key=len, reverse=True)
            cap = h - self.dn[n]                                          # span(n) <= U_n
            if not cand and len(srcs) == 1: K[n] = srcs[0]; continue
            E = Echelon(M127); keep = []
            seq = list(srcs[0]) if srcs else []
            for r in seq: E.insert(rows[r]); keep.append(r)                # srcs[0] is already independent
            for lst in [cand] + srcs[1:]:
                for r in lst:
                    if len(keep) >= cap: break
                    if E.insert(rows[r]): keep.append(r)
            K[n] = tuple(keep)
        self.K = K
        return K

    def dims(self):
        """exact dim of every addition frame M_n."""
        pr, h = self.pr, self.h; F = pr.F; d = dict(self.dn); stats = Counter()
        rows = [self.rootcov[k] for k in self.rkeys]
        self.KF = {}
        for n, j in pr.j.items():
            Fj = F[:j]; K = [rows[r] for r in self.K[n]]
            KF = [[sum(a * b for a, b in zip(kr, fr)) for fr in Fj] for kr in K]
            SF = [trow(h, pr.trip[i]) for i in self.bas[n]] + Fj
            r1 = self._rank(SF, min(len(SF), h), stats, 'SF'); r2 = self._rank(KF, min(len(K), j), stats, 'KF')
            d[n] = r1 - r2; self.KF[n] = (r2, KF)
            assert self.dn[n] <= d[n] <= h - len(K)
        self.d = d
        return d, stats

    @staticmethod
    def _rank(M, full, stats, tag):
        if not M or full == 0: return 0
        r = rank_mod(M, Q31)
        if r == full: stats[tag + ' full mod q'] += 1; return r          # rank mod q <= rank over Q <= full
        if hadamard_ok(M, M521): stats[tag + ' M521'] += 1; return rank_mod(M, M521)
        stats[tag + ' Bareiss'] += 1; return rank_exact(M)

    # exact rational bases, used for the late-copy intersections
    def exact_basis(self, key):
        pr, h = self.pr, self.h
        if key[0] in ('out', 'ret'):
            return null_exact([self.rootcov[key]], h)
        n = key[1]
        S = [trow(h, pr.trip[i]) for i in self.bas[n]]
        j = pr.j.get(n, 0)
        if not j: return S
        _, KF = self.KF[n]; F = pr.F[:j]
        X = null_exact(KF, j) if KF else [[int(i == t) for t in range(j)] for i in range(j)]
        vecs = S + [[sum(c * F[i][q] for i, c in enumerate(x)) for q in range(h)] for x in X]
        # independent subset: rows independent mod q are independent over Q; d of them span M_n (dim M_n = d exactly)
        E = Echelon(Q31); out = []
        for vv in vecs:
            if E.insert(vv): out.append(vv)
        assert len(out) == self.d[n], ('exact basis dim', n, len(out), self.d[n])
        return out

    def intersect_exact(self, A, B):
        h = self.h
        if not A or not B: return []
        # z = (x, y): x A = y B  <=>  [A; -B]^T z = 0
        M = [[A[i][q] for i in range(len(A))] + [-B[i][q] for i in range(len(B))] for q in range(h)]
        Z = null_exact(M, len(A) + len(B))
        # A and B are bases, so z -> x A is injective on the null space: the images are a basis of A cap B
        return [[sum(z[i] * A[i][q] for i in range(len(A))) for q in range(h)] for z in Z]


def late_frames(fr, pr, users):
    """exact dims of every late-copy intersection frame ('c', n, late users)."""
    cache = {}; dims = {}
    def eb(k):
        if k not in cache: cache[k] = fr.exact_basis(k)
        return cache[k]
    def ufr(n, k):
        u = users[n][k]; return ('n', u[1]) if u[0] == 'gate' else root_key(u)
    for n, (early, lt) in pr.late.items():
        for i in range(len(lt) - 1):
            B = eb(ufr(n, lt[-1]))
            for k in reversed(lt[i:-1]): B = fr.intersect_exact(eb(ufr(n, k)), B)
            dims[('c', n, tuple(lt[i:]))] = len(B)
    return dims, cache


def chain_steps(chains, dimof, h):
    rk = Counter(); steps = {}
    for ch in chains:
        prev = ch[0]; pd = dimof(prev)
        for k in ch[1:]:
            dk = dimof(k)
            assert dk >= pd, ('decreasing chain', prev, k, pd, dk)
            if dk > pd: rk[dk - pd] += 1; steps[prev, k] = dk - pd; prev, pd = k, dk
            else: prev = k                                                 # equal dims, nested => equal frames
        assert pd == h
    return rk, steps


# ----------------------------------------------------------------------------------------------- E. mod-q frames, side lemma
def point_UV(h, seed):
    """the U, V drawn by independent/two-stage-bit/flag_existence.py with this seed (same random stream)."""
    CR = 10**6; rng = random.Random(seed)
    nz = lambda: rng.choice([-1, 1]) * rng.randint(1, CR)
    for b in range(h):
        for i in range(h):
            for jj in range(h):
                if i <= b and jj <= b: nz()
    for b in range(h):
        for i in range(h):
            for jj in range(h):
                if i >= b and jj >= b: nz()
    U = [[rng.randint(-CR, CR) for _ in range(h)] for _ in range(h)]
    V = [[rng.randint(-CR, CR) for _ in range(h)] for _ in range(h)]
    return U, V


class ModQ:
    def __init__(self, fr, latedims, control=False):
        self.fr = fr; self.h = h = fr.h; self.q = q = Q31; self.latedims = latedims
        U, V = point_UV(h, 1)
        if control: U = [[int(i == k) for k in range(h)] for i in range(h)]; V = [r[:] for r in U]
        self.conj = []
        for A in (U, V):
            Ai = inv_mod_matrix(A, q); assert Ai is not None
            self.conj.append(([list(c) for c in zip(*A)], Ai))          # columns of A, rows of A^-1
        self.inv9 = pow(9, q - 2, q); self.bcache = {}; self.qcache = OrderedDict(); self.cap = 6000
        self.degenerate = 0; self.dimfail = 0

    def basis(self, key):
        if key in self.bcache: return self.bcache[key]
        fr, h, q = self.fr, self.h, self.q; pr = fr.pr
        if key == ('0',): B = []
        elif key == ('F',): B = [[int(i == t) for t in range(h)] for i in range(h)]
        elif key[0] in ('out', 'ret'): B = null_mod([fr.rootcov[key]], h, q)
        elif key[0] == 'c':
            n, lt = key[1], key[2]
            B = None
            for k in lt:
                u = fr.users[n][k]; kk = ('n', u[1]) if u[0] == 'gate' else root_key(u)
                Bk = self.basis(kk)
                B = Bk if B is None else self._cap(B, Bk)
            if len(B) != self.latedims[key]: self.dimfail += 1
        else:
            n = key[1]; S = [trow(h, pr.trip[i]) for i in fr.bas[n]]; j = pr.j.get(n, 0)
            E = Echelon(q)
            for r in S: E.insert(r)
            if j:
                r2, KF = fr.KF[n]
                if KF and rank_mod(KF, q) != r2: self.dimfail += 1
                X = null_mod(KF, j, q) if KF else [[int(i == t) for t in range(j)] for i in range(j)]
                Fj = pr.F[:j]
                for x in X: E.insert([sum(c * Fj[i][t] for i, c in enumerate(x)) % q for t in range(h)])
            B = E.rows
            if len(B) != fr.d[n]: self.dimfail += 1
        self.bcache[key] = B
        return B

    def _cap(self, A, B):
        q, h = self.q, self.h
        if not A or not B: return []
        M = [[A[i][t] for i in range(len(A))] + [(-B[i][t]) % q for i in range(len(B))] for t in range(h)]
        Z = null_mod(M, len(A) + len(B), q); E = Echelon(q)
        for z in Z: E.insert([sum(z[i] * A[i][t] for i in range(len(A))) % q for t in range(h)])
        return E.rows

    def gram_inv(self, B):
        q = self.q; BG = [[(x - sum(b) * self.inv9) % q for x in b] for b in B]
        Gr = [[sum(x * y for x, y in zip(bg, c)) % q for c in B] for bg in BG]
        return BG, inv_mod_matrix(Gr, q)

    def nondeg(self, key):
        B = self.basis(key)
        if not B or len(B) == self.h: return True
        return self.gram_inv(B)[1] is not None

    def conjugated(self, key):
        """(U^T P U^-T, V^T P V^-T) for the G-orthogonal projector P onto the frame, flattened."""
        if key in self.qcache: self.qcache.move_to_end(key); return self.qcache[key]
        h, q = self.h, self.q; B = self.basis(key)
        if not B: out = (array('q', [0] * h * h),) * 2
        elif len(B) == h: I = array('q', [int(i == t) for i in range(h) for t in range(h)]); out = (I, I)
        else:
            BG, Gi = self.gram_inv(B)
            if Gi is None: raise ZeroDivisionError(key)
            res = []
            for Acols, Ai in self.conj:
                LU = [[sum(x * y for x, y in zip(ac, b)) % q for b in B] for ac in Acols]       # A^T B^T  (h x d)
                RU = [[sum(x * y for x, y in zip(bg, ai)) % q for ai in Ai] for bg in BG]      # B G A^-T (d x h)
                Mi = matmul(Gi, RU, q)
                Mt = list(zip(*Mi))
                res.append(array('q', [sum(x * y for x, y in zip(l, c)) % q for l in LU for c in Mt]))
            out = tuple(res)
        self.qcache[key] = out
        if len(self.qcache) > self.cap: self.qcache.popitem(last=False)
        return out


def side_lemma(mq, steps, h, retained):
    q = mq.q; pr_ = predicted(h); E = dict((k, r) for k, r in steps.items() if 2 * r > h)
    for c in retained: E[('0',), ('ret', c)] = h - 1                    # retained copy edges 0 -> U_c
    keys = sorted(E, key=lambda e: (str(e[1]), str(e[0])))              # group by target frame (cache reuse)
    bad = 0; n = 0
    for (A, B) in keys:
        r = E[A, B]; QA, QB = mq.conjugated(A), mq.conjugated(B)
        for t in range(2):
            a, b = QA[t], QB[t]
            M = [[(b[i * h + c] - a[i * h + c]) % q for c in range(h)] for i in range(h)]
            if rightmost_pivots(M, q) != pr_[r]: bad += 1
        n += 1
        if n % 5000 == 0: log('   side lemma %d/%d, failures %d' % (n, len(keys), bad))
    return bad, len(keys)


# ----------------------------------------------------------------------------------------------- F. certificate
K_REPO = os.path.normpath(os.path.join(HERE, '..', '..'))
sys.path[:0] = [K_REPO + '/scripts', K_REPO + '/independent/two-stage-bit']


def inner_children(r, h): return [1] * (h - r) + [2 * r - h] if 2 * r > h else [1] * r


def rt_histogram(h, R, rk, corner):
    """cert_rt.rt_histogram with the data-entrance corner profile 'corner' (round six: [h-2] + [1]*(h+1))."""
    from math import comb
    v, m = comb(h, 3), h * h; N = v * v; A = v * R; H = Counter()
    assert sum(r * n for r, n in rk.items()) == h * R and sum(corner) == 2 * h - 1
    for _ in range(2):
        H[m - 2 * h] += A; H[h] += A
        for r, n in rk.items():
            for w in inner_children(r, h): H[w] += v * n
        for w in inner_children(h - 1, h): H[w] += v * h
    H[m - 4 * h + 2] += 2 * N
    for w in corner: H[w] += 2 * N
    for _ in range(2): H[h - 2] += 2 * N; H[1] += 2 * N
    H[1] += N
    W = 2 * N + 2 * A; L = 2 * v * h * (h - 1); s = W * m - N + L
    H = {w: c for w, c in H.items() if c}
    assert sum(w * c for w, c in H.items()) == s and max(H) <= m - 1
    return dict(h=h, m=m, v=v, N=N, W=W, L=L, s=s, R=R, hist=H)


def certificate(h, R, rk):
    import moment
    from certificate_round3 import evaluate
    out = {}
    for name, corner in (('round6 corner', [h - 2] + [1] * (h + 1)), ('staircase', [h - 2, h - 5] + [1] * 6)):
        c = rt_histogram(h, R, rk, corner)
        if c['W'] * c['m'] <= c['s']: out[name] = ('no deficit', c['s']); continue
        a, root = moment.certify(c)
        k = evaluate(a, Fr(36926111, 5 * 10**11), Fr(1, 1000), 'crude', m_c=576, s_c=119453132304)
        out[name] = (a, root, c['s'], c['W'], k['kappa'], k['ok'])
    return out


# ----------------------------------------------------------------------------------------------- main
def main(h, generic=True, control=False):
    W = load_witness(h)
    pr = Prog(W); log('h=%d: A. DAG semantics OK (%d nodes, %d additions, %d links, %d lifted, %d late)' % (
        h, len(pr.act), sum(1 for n in pr.act if pr.args[n]), len(pr.mL), len(pr.j), len(pr.late)))
    bas, dn = spans(pr); users = users_of(pr, dn)
    ops, chains, reads, R = compile_(pr, dn, users)
    log('B. compiled: R=%d (claimed %d), ops %d, late copies %d' % (R, W['claimed']['R'], len(ops),
        sum(len(l) - 1 for _, l in pr.late.values())))
    assert R == W['claimed']['R']
    rng = random.Random(h)
    res = {(ring, mir, mid): all(replay(pr, ops, reads, R, ring, rng, mir, mid) for _ in range(2))
           for ring in (2, 0) for mir in (False, True) for mid in (True, False)}
    log('C. dirty-scratch replay (F2/Z x word/mirror x midread/endread): %s' % ('ALL OK' if all(res.values()) else res))
    fr = Frames(pr, dn, bas, users)
    bj, bl, br, Fok = fr.check_structure()
    log('D. nesting facts: j-monotone failures %d, link span failures %d, root containment failures %d, F invertible %s'
        % (bj, bl, br, Fok))
    fr.cobases(); log('   co-bases K_n done')
    d, st = fr.dims(); log('   lifted frame dims exact: %s' % dict(st))
    nU = sum(1 for n in pr.j if d[n] == h - len(fr.K[n]))
    log('   every lifted frame is the largest admissible frame U_n: %s (%d / %d; the flag only switches span -> U_n)'
        % (nU == len(pr.j), nU, len(pr.j)))
    ld, ecache = late_frames(fr, pr, users); log('   late-copy intersections exact: %d frames' % len(ld))
    def dimof(k):
        if k == ('0',): return 0
        if k == ('F',): return h
        if k[0] in ('out', 'ret'): return h - 1
        if k[0] == 'c': return ld[k]
        return d[k[1]]
    rk, steps = chain_steps(chains, dimof, h)
    claimed = Counter({int(r): c for r, c in W['claimed']['rk'].items()})
    log('   chain steps: sum of ranks %d = h R %d: %s; histogram equals claim: %s; distinct steps %d (2r>h: %d)' % (
        sum(r * c for r, c in rk.items()), h * R, sum(r * c for r, c in rk.items()) == h * R, rk == claimed,
        len(steps), sum(1 for r in steps.values() if 2 * r > h)))
    out = dict(h=h, R=R, replay=all(res.values()), struct=(bj, bl, br, Fok), hist_ok=rk == claimed, rk=rk)
    if generic:
        mq = ModQ(fr, ld, control)
        frames_used = {k for e in steps for k in e} | {('ret', c) for c in pr.retained}
        nd = sum(1 for k in frames_used if not mq.nondeg(k))
        log('E. frames used %d: G-degenerate %d, reduction dimension mismatches %d' % (len(frames_used), nd, mq.dimfail))
        bad, ne = side_lemma(mq, steps, h, pr.retained)
        log('   side lemma at one integer point%s: failures %d over %d distinct high-rank steps x 2 conjugations' % (
            ' (CONTROL U=V=I)' if control else '', bad, ne))
        out.update(degenerate=nd, dimfail=mq.dimfail, side_bad=bad, side_n=ne)
    for name, val in certificate(h, R, rk).items():
        if val[0] == 'no deficit': log('F. %s: no deficit at this h (s=%d), certificate n/a' % (name, val[1])); continue
        a, root, s, Wr, kap, ok = val
        log('F. %s: s=%d W=%d a_b=%s (%.6e, root %.6e) kappa=%s (%.7e) ok=%s' % (name, s, Wr, a, float(a), root, kap,
            float(kap), ok))
        out[name] = (a, kap, ok)
    return out, pr, dn, users




# ----------------------------------------------------------------------------------------------- negative controls
def controls(h, nsample=40):
    """Each must FAIL (or differ) for the check to have teeth:
     (a) one late copy moved to just after its pivot's consumer gate: replay must fail;
     (b) one late copy dropped: replay must fail;
     (c) pivot chain without intersections (C_i := frame of user i alone): exhibit non-nested consecutive pivot frames;
     (d) M_n rebuilt from an independent flag F' on targets strictly between span and U (vacuous for this
         witness: every lifted frame equals U_n, so the flag is only a switch and nesting needs no common flag);
     (e) side lemma at U = V = I on the first high-rank steps: generic pivots must fail;
     (f) no late copies (lifted frames only): histogram must change."""
    W = load_witness(h)
    pr = Prog(W); bas, dn = spans(pr); users = users_of(pr, dn); rng = random.Random(7)
    key = lambda n: (dn[n], n); linked = {r: x for x, r in pr.mL.items()}
    cand = [n for n, (e, lt) in pr.late.items() if users[n][lt[-1]][0] == 'gate']
    fails = 0; tried = 0
    for n in cand[:nsample]:
        tamper_node[0] = n; ops, ch, rd, R = compile_(pr, dn, users, tamper='aftercons')
        ok = all(replay(pr, ops, rd, R, ring, rng) for ring in (2, 0)); tried += 1; fails += not ok
    log('(a) late copy moved after the pivot consumer: replay failed %d / %d (must be all)' % (fails, tried))
    ops, ch, rd, R = compile_(pr, dn, users, tamper='dropcopy')
    log('(b) one late copy dropped: replay correct %s (must be False)' % all(replay(pr, ops, rd, R, ring, rng) for ring in (2, 0)))
    fr = Frames(pr, dn, bas, users); fr.cobases(); d, _ = fr.dims(); d = dict(d); ld, _ = late_frames(fr, pr, users)
    mq = ModQ(fr, ld)
    def inside(A, B):
        E = Echelon(mq.q)
        for r in mq.basis(B): E.insert(r)
        return all(E.contains(r) for r in mq.basis(A))
    def ufr(n, k):
        u = users[n][k]; return ('n', u[1]) if u[0] == 'gate' else root_key(u)
    bad = tot = 0
    for n, (e, lt) in pr.late.items():
        for i in range(len(lt) - 1):
            tot += 1; bad += not inside(ufr(n, lt[i]), ufr(n, lt[i + 1]))
    log('(c) pivot chain through user frames without intersections: non-nested consecutive frames %d / %d '
        '(the intersections are needed)' % (bad, tot))
    # (d) the common flag is essential: rebuild M_n with an independent flag F' (same j(n)) and test M_n <= M_t
    pairs = [(n, t) for n in pr.j for t in fr.succ[n] if pr.j.get(t, 0) > 0 and dn[t] < d[t] < h - len(fr.K[t])]
    rng.shuffle(pairs); bad = tot = 0; r2 = random.Random(99)
    Fp = [[r2.randint(-50, 50) for _ in range(h)] for _ in range(h)]
    for n, t in pairs[:nsample]:
        j = pr.j[n]; K = [fr.rootcov[fr.rkeys[r]] for r in fr.K[n]]
        KF = [[sum(a * b for a, b in zip(kr, fl)) for fl in Fp[:j]] for kr in K]
        if KF and rank_mod(KF, mq.q) != fr._rank(KF, min(len(K), j), Counter(), 'KF'): continue
        X = null_mod(KF, j, mq.q) if KF else [[int(i == c) for c in range(j)] for i in range(j)]
        E = Echelon(mq.q)
        for r in mq.basis(('n', t)): E.insert(r)
        vecs = [[sum(c * Fp[i][q] for i, c in enumerate(x)) % mq.q for q in range(h)] for x in X]
        tot += 1; bad += not all(E.contains(v) for v in vecs)
    log("(d) M_n rebuilt with an independent flag F': M_n not inside M_t on %d / %d lifted successor pairs (targets strictly between span and U)" % (bad, tot))
    ops, chains, reads, R = compile_(pr, dn, users)
    fr2 = Frames(pr, dn, bas, users); fr2.cobases(); d2, _ = fr2.dims(); ld2, _ = late_frames(fr2, pr, users)
    dimof = lambda k: 0 if k == ('0',) else h if k == ('F',) else h - 1 if k[0] in ('out', 'ret') else ld2[k] if k[0] == 'c' else d2[k[1]]
    rk, steps = chain_steps(chains, dimof, h)
    mqs = ModQ(fr2, ld2); smp = list(steps); random.Random(5).shuffle(smp); nb = 0
    for A, B in smp[:3000]:
        E = Echelon(mqs.q)
        for r in mqs.basis(B): E.insert(r)
        nb += not all(E.contains(r) for r in mqs.basis(A))
    log('(g) sanity (positive): 3000 sampled chain steps A -> B with A inside B mod q: failures %d' % nb)
    mq0 = ModQ(fr2, ld2, control=True); pr_ = predicted(h); hi = [(e, r) for e, r in steps.items() if 2 * r > h][:300]
    nb = 0
    for (A, B), r in hi:
        QA, QB = mq0.conjugated(A), mq0.conjugated(B)
        M = [[(QB[0][i * h + c] - QA[0][i * h + c]) % mq0.q for c in range(h)] for i in range(h)]
        nb += rightmost_pivots(M, mq0.q) != pr_[r]
    log('(e) side lemma with U = V = I: failures %d / %d (must be most)' % (nb, len(hi)))
    ops, chains0, reads, R = compile_(pr, dn, users, late=False)
    rk0, _ = chain_steps(chains0, dimof, h)
    log('(f) without late copies: histogram differs %s; certificate %s' % (rk0 != rk, {k: v[0] for k, v in certificate(h, R, rk0).items()}))


if __name__ == '__main__':
    h = int(sys.argv[1])
    if '--controls' in sys.argv: controls(h)
    else:
        out = main(h, generic='--no-generic' not in sys.argv)[0]
        ok = out['replay'] and out['struct'][:3] == (0, 0, 0) and out['struct'][3] and out['hist_ok']
        ok &= out.get('degenerate', 0) == 0 and out.get('dimfail', 0) == 0 and out.get('side_bad', 0) == 0
        ok &= all(v[2] for k, v in out.items() if k in ('round6 corner', 'staircase'))
        log('ALL %s' % ('PASS' if ok else 'FAIL'))
        sys.exit(0 if ok else 1)
