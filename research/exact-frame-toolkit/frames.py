"""frames: frame subsolver for integer-mult-bounds provider words (exact surrogate certificate, true-moment interval).

Model (research/frame-domain-ceiling/PROOF.md, check_duals.py): event graph with a vertex per
scalar gate of A/B and immutable vertices for starts, the central cut and ends; each register
contributes directed edges between its consecutive occurrences; a vertex carries a subspace
of F2^9 and every edge must be nested (F_e <= F_f); the paid profile counts the rank of each
jump along each register chain; the recurrence moment charges a concave function of the rank.

Given the gate ORDER (the scalar program), this module chooses the frame assignment of the model below
for a per-call moment at a chosen endpoint b:
  * L/U propagation (joins forward, meets backward) gives the finite domain of every variable
    vertex (dim(U/L) <= 3 in practice);
  * chain dual decomposition: every register chain is a path, every gate vertex is shared by
    at most two chains; min-marginal averaging on the path DPs maximises the Lagrangian dual
    (= the local-polytope LP bound), a topological greedy decode gives a feasible primal, and
    an exact integer evaluation of both certifies optimality when they coincide;
  * exact variable elimination with back-pointers for small components (cross-check).

What is certified (and what is not):
  * Surrogate. Costs.c[r] = floor(2^40 * lo_r(b)), where lo_r(b) is the engines' outward lower bound of the per-child
    moment term T_r(b) = r (m/r)^b / (m W) + 32 m^(1+b) / (1e16 W). `certified` means exact optimality for these
    floored integer weights only: an integer weak-duality bound equal to the primal, computed in Python integers.
  * True moment at b. optimal_frames(..., interval=True) adds a rigorous rational interval for the minimum of
    sum_e T_rank(e)(b) over every frame assignment of the model (moment_interval): lower = exact Lagrangian bound
    with outward-floored lower weights on a 2^-224 grid; upper = the engines' upper bound of the returned assignment.
    Its width is computed, never assumed; a comparison is decided only when its interval excludes the other side.
  * Not certified: the global recursive moment root or kappa (nonlinear in the global profile; recomputed by
    kappa.py and the package chain), the ordering at another b, or any word outside this frame model.
Float64 arrays drive only the heuristic sweeps and the decode; every bound, certificate and interval is evaluated
from the exact integer weight tables, with float multipliers converted exactly after a finiteness check.
"""
import gzip, json, importlib.util, sys, time, collections, math
from fractions import Fraction as Q
from functools import lru_cache
from pathlib import Path
import numpy as np

from paths import ROOT as IMB
FDC = IMB / "research/frame-domain-ceiling"
sys.path.insert(0, str(FDC / "vendor/static44/gk"))
import gk_word as G, gk_common as C
G.V = C.V = 112; G.DATA = C.DATA = 7168
V = 112; M_DIM = 73; W_LIVE = 7168
FULL = G.FULL

def _load(n, p):
    sp = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
MOM = _load("imb_price", FDC / "engines/moment.py"); MOM2 = _load("imb_other", FDC / "engines/base_two_moment.py")

@lru_cache(None)
def span(F): return frozenset(G.span(F))
@lru_cache(None)
def basis(F): return G.basis(F)
def leq(F, H): return span(F) <= span(H)

# ---------------------------------------------------------------- costs
SCALE_BITS = 184   # 2^224-grid moment bounds scaled down to ~2^40 magnitudes (2^40 units; c[r] < 2^25 here)
FINE_BITS = 224    # integer grid of the interval certificate (the engines' dyadic grid)
FLOAT_EXACT = 1 << 53
class Costs:
    """per-child moment bounds at endpoint b (both engines, conservative fallback share).
    exact[r] / upper[r]: the outward lower / upper bound of T_r(b) (Fractions); c[r] = floor(2^unit_bits * exact[r]),
    the integer surrogate; vec: its float64 image, exact because every c[r] is checked to be below 2^53."""
    def __init__(self, b, scale_bits=SCALE_BITS):
        self.b = Q(b); self.scale_bits = scale_bits; self.unit_bits = 224 - scale_bits; self.mu_shift = 0
        fl, fu = MOM2.moment(M_DIM, W_LIVE, [(1, 32 * M_DIM * M_DIM)], self.b)
        self.exact = {0: Q(0)}; self.upper = {0: Q(0)}; self.c = {0: 0}
        for r in range(1, M_DIM):
            l, u = MOM.moment({r: 1}, M_DIM, W_LIVE, self.b, True)
            l2, u2 = MOM2.moment(M_DIM, W_LIVE, [(r, 1)], self.b); l2 += fl / Q(10 ** 16); u2 += fu / Q(10 ** 16)
            lo, hi = max(l, l2), min(u, u2)
            if not 0 < lo <= hi: raise ValueError(("moment bounds out of order", r, lo, hi))
            self.exact[r] = lo; self.upper[r] = hi
            self.c[r] = (lo.numerator << self.unit_bits) // lo.denominator
        for r in range(10):   # certify the float64 image before converting it
            if not (isinstance(self.c[r], int) and 0 <= self.c[r] < FLOAT_EXACT): raise ValueError(("weight outside the exact float64 range", r, self.c[r]))
        self.vec = np.array([self.c[r] for r in range(10)], dtype=np.float64)
        if [int(x) for x in self.vec] != [self.c[r] for r in range(10)]: raise ValueError("inexact float64 weight image")
    def profile_cost(self, H):
        return sum(n * self.c[r] for r, n in H.items())
    def moment_exact(self, H):
        """exact lower bound of the moment of a (global) profile at b, as Fraction."""
        return sum(n * self.exact[r] for r, n in H.items())
    def moment_upper(self, H):
        """exact upper bound of the moment of a profile at b, as Fraction."""
        return sum(n * self.upper[r] for r, n in H.items())
    def fine(self, bits=FINE_BITS):
        return FineCosts(self, bits)

class FineCosts:
    """lower weights of the interval certificate: c[r] = floor(2^bits * (exact[r] - lam*r)) <= 2^bits (T_r(b) - lam*r).
    lam = exact[1]; any rational lam is admissible because along every register chain the ranks telescope to
    dim(end) - dim(start): lam*rank adds the same constant to every frame assignment (and to every chain segment).
    vec is a float64 image in 2^unit_bits units, used only by the sweeps; mu_shift converts its multipliers exactly."""
    def __init__(self, costs, bits=FINE_BITS):
        self.parent = costs; self.bits = bits; self.lam = costs.exact[1]; self.unit_bits = costs.unit_bits
        self.mu_shift = bits - costs.unit_bits
        if self.mu_shift < 0: raise ValueError("interval grid coarser than the surrogate")
        sh = [costs.exact[r] - self.lam * r for r in range(10)]
        self.c = {r: (x.numerator << bits) // x.denominator for r, x in enumerate(sh)}
        self.vec = np.array([float(x * (1 << self.unit_bits)) for x in sh], dtype=np.float64)
        if not np.all(np.isfinite(self.vec)): raise ValueError("non-finite float image")

def entropy(H, m=M_DIM): return sum(n * r * math.log(m / r) for r, n in H.items())
def solve_b(H, m=M_DIM, W=W_LIVE):
    lo, hi = 0.0, 0.02
    for _ in range(100):
        mid = (lo + hi) / 2
        if sum(n * r * (m / r) ** mid for r, n in H.items()) < m * W: lo = mid
        else: hi = mid
    return lo

# ---------------------------------------------------------------- word io
def load_word(path):
    return json.load(gzip.open(path))
def R_of(w): return w["report"]["R"] if "report" in w else w["R"]

def from_canonical(w):
    """convert a CANONICAL-WORD (frames by id; start/final per register; optional HPE 'tail') into the inline
    representation used by Graph.  Centre descents at the cut are the constant part of the paid profile."""
    frames = [tuple(f) for f in w["frames"]]
    def inl(e):
        e = list(e)
        if e[-1] is not None: e[-1] = list(frames[e[-1]])
        return e
    out = dict(A=[inl(e) for e in w["A"]], B=[inl(e) for e in w["B"]], cut=[inl(e) for e in w["cut"]],
               ports=list(w["ports"]), centers=list(w["centers"]), center_frames=[list(frames[i]) for i in w["center_frames"]],
               target_levels={t: list(frames[i]) for t, i in w.get("target_levels", {}).items()},
               report=dict(R=w["R"], local_profile=w.get("local_profile")), R=w["R"],
               _start_frames=[frames[i] for i in w["start"]], _final_frames=[frames[i] for i in w["final"]],
               _tail=[inl(e) for e in w.get("tail", [])])
    # constant centre descents (served levels), as in hpe_audit_and_transport.py
    levels = {int(t): frames[i] for t, i in w.get("target_levels", {}).items()}
    centre = collections.Counter()
    for r, fi in zip(w["centers"], w["center_frames"]):
        served = {levels.get(e[1] - V, ()) for e in w["cut"] if e[2] == r}
        old = frames[fi]
        for f in sorted(served, key=lambda f: -len(f)):
            if old != f: centre[len(old) - len(f)] += 1; old = f
    out["_centre_descents"] = dict(centre)
    return out

def to_canonical(w_inline, assign_graph=None):
    """inverse of from_canonical for the gate sections (frames re-indexed); used to export improved words."""
    raise NotImplementedError

def regs_of(g): return [g[1]] + ([g[2]] if g[0] == "add" else [])

def commute(g1, g2):
    """exact commutation of two scalar gates as linear maps."""
    if g1[0] == "scale" and g2[0] == "scale": return True
    if g1[0] == "scale": return g1[1] not in (g2[1], g2[2])
    if g2[0] == "scale": return g2[1] not in (g1[1], g1[2])
    return g1[1] != g2[2] and g2[1] != g1[2]

# ---------------------------------------------------------------- event graph
class Infeasible(Exception):
    pass

class Graph:
    def __init__(self, w, check_literal=True, tail_mutable=False, caps=None, cut_equality=False):
        """check_literal=False: ignore the stored A/B gate frames (reordered word); frames come from L/U only.
        tail_mutable=True: the early-cleanup (tail) frames are variables too (gauge44 lineage: build_promotion.apply accepts 'T' changes).
        Raises Infeasible when the fixed boundaries cannot be nested under this gate order."""
        self.w = w; R = R_of(w); N = 2 * V + R; self.N = N; self.check_literal = check_literal; self.tail_mutable = tail_mutable
        caps = caps or {}; self.caps = caps; self.cut_equality = cut_equality   # caps: register -> subspace cap on its end-of-B frame (cones)
        nodes = []; chains = [[] for _ in range(N)]; mutable = []
        start_frames = w.get("_start_frames"); final_frames = w.get("_final_frames"); tail = w.get("_tail", [])
        def node(regs, F, sec, index=None):
            k = len(nodes); nodes.append((tuple(regs), basis(tuple(F)), sec, index))
            for r in regs: chains[r].append(k)
            if sec in ("A", "B") or (sec == "tail" and tail_mutable): mutable.append(k)
        for r in range(N):
            if start_frames is not None: F = start_frames[r]
            else: F = [w["ports"][r]] if r < V else w.get("start_extra", {}).get(str(r), []) if r >= 2 * V else w.get("target_levels", {}).get(str(r - V), [])
            node([r], F, "start")
        for sec in ("A", "B"):
            if sec == "B":
                for r, F in zip(w["centers"], w["center_frames"]): node([r], F, "cut")
                for t in range(V): node([V + t], w.get("target_levels", {}).get(str(t), []), "cut")
            for i, e in enumerate(w[sec]): node(regs_of(e), e[-1], sec, i)
        for i, e in enumerate(tail): node(regs_of(e), e[-1], "tail", i)      # HPE early-cleanup gates: fixed common frames
        for r in range(N):
            if final_frames is not None: F = final_frames[r]
            else: F = FULL if r < V or r >= 2 * V else G.perp(w["ports"][r - V])
            node([r], F, "end")
        self.nodes = nodes; self.chains = chains; self.mutable = mutable
        prev = {}; nxt = {}
        for r, ch in enumerate(chains):
            for p, q in zip(ch, ch[1:]):
                prev[q, r] = p; nxt[p, r] = q
                if check_literal and not leq(nodes[p][1], nodes[q][1]): raise ValueError(("frame violation on register", r, p, q))
        self.prev = prev; self.nxt = nxt
        # L / U propagation
        allowed = set(mutable); lower = {}; upper = {}
        for k, (regs, F0, sec, idx) in enumerate(nodes):
            lower[k] = basis(tuple(x for r in regs for x in lower[prev[k, r]])) if k in allowed else F0
            if cut_equality and k in allowed and sec == "A":   # the frame after the last A event must equal the cut frame (audit: center frame / target level)
                for r in regs:
                    j = nxt.get((k, r))
                    if j is not None and nodes[j][2] == "cut": lower[k] = basis(tuple(lower[k]) + tuple(nodes[j][1]))
        for k in reversed(range(len(nodes))):
            regs, F0, sec, idx = nodes[k]
            if k in allowed:
                U = set(span(FULL))
                for r in regs: U.intersection_update(span(upper[nxt[k, r]]))
                for r in regs:
                    if r in caps and nodes[nxt[k, r]][2] in ("tail", "end"): U.intersection_update(span(caps[r]))   # end-of-B cone cap
                upper[k] = basis(tuple(U))
                if not leq(lower[k], upper[k]): raise Infeasible(("L not inside U at mutable vertex", k, sec, idx))
                if check_literal and not (leq(lower[k], F0) and leq(F0, upper[k])): raise ValueError(("literal frame outside [L,U]", k))
            else:
                upper[k] = F0
                if not leq(lower[k], F0): raise Infeasible(("fixed vertex below its forced lower frame", k, sec, idx))
                for r in regs:
                    if (k, r) in nxt and not leq(F0, upper[nxt[k, r]]): raise Infeasible(("fixed vertex above its successor cap", k, sec, idx))
        self.lower = lower; self.upper = upper
        if not check_literal:   # mutable vertices with L == U are forced: give them that frame
            nodes = [((regs, lower[k], sec, idx) if (k in allowed and lower[k] == upper[k]) else (regs, F0, sec, idx)) for k, (regs, F0, sec, idx) in enumerate(nodes)]
            self.nodes = nodes
        self.var = [k for k in mutable if lower[k] != upper[k]]; self.varset = set(self.var)
        self.dom = {k: self._domain(k) for k in self.var}
        self.didx = {k: {F: i for i, F in enumerate(d)} for k, d in self.dom.items()}
        # components of the var-var adjacency
        adj = collections.defaultdict(set)
        for (k, r), j in prev.items():
            if k in self.varset and j in self.varset: adj[k].add(j); adj[j].add(k)
        self.adj = adj
        comps = []; remaining = set(self.var)
        while remaining:
            root = min(remaining); stack = [root]; remaining.remove(root); comp = []
            while stack:
                k = stack.pop(); comp.append(k)
                for j in adj[k] & remaining: remaining.remove(j); stack.append(j)
            comps.append(sorted(comp))
        self.components = sorted(comps, key=lambda z: (-len(z), min(z)))
    def _domain(self, k):
        L, U = self.lower[k], self.upper[k]; extras = []; current = L
        for v in U:
            if v not in span(current): extras.append(v); current = basis(tuple(current) + (v,))
        d = len(extras)
        if d > 5: raise ValueError(("domain too large", k, d))
        spaces = {()}
        frontier = [()]
        while frontier:   # all subspaces of F2^d by closure under adding one vector
            nxt = []
            for S in frontier:
                sp = set(G.span(S))
                for v in range(1, 1 << d):
                    if v not in sp:
                        T = basis(S + (v,))
                        if T not in spaces: spaces.add(T); nxt.append(T)
            frontier = nxt
        def lift(v):
            z = 0
            for i, x in enumerate(extras):
                if v >> i & 1: z ^= x
            return z
        return sorted({basis(tuple(L) + tuple(lift(v) for v in S)) for S in spaces})
    def literal(self):
        return {k: self.nodes[k][1] for k in self.var}
    def profile(self, assign):
        """paid profile of A/B climbs for an assignment of the variable vertices (fixed vertices literal)."""
        F = lambda k: assign[k] if k in self.varset else self.nodes[k][1]
        H = collections.Counter()
        for (k, r), j in self.prev.items():
            d = len(F(k)) - len(F(j))
            if d: H[d] += 1
        return H
    def edge_list(self):
        return [((j, k), r) for (k, r), j in self.prev.items()]

# ---------------------------------------------------------------- chain dual decomposition
class ChainDD:
    """Lagrangian dual over register chains (segments of consecutive variable vertices)."""
    def __init__(self, g: Graph, costs: Costs, var_subset=None):
        """costs: Costs (surrogate) or FineCosts; costs.c is the exact integer weight table, costs.vec its float image."""
        self.g = g; self.costs = costs; self.mu_shift = getattr(costs, "mu_shift", 0)
        V_ = set(var_subset) if var_subset is not None else g.varset
        self.vars = sorted(V_)
        cvec = costs.vec
        # segments: maximal runs of variable vertices along each register chain
        segs = []   # each: dict(reg, nodes[list], E[list of (dp x dq) matrices], u0[list of unary arrays])
        self.seg_of = collections.defaultdict(list)   # vertex -> [(seg index, position)]
        for r, ch in enumerate(g.chains):
            i = 0
            while i < len(ch):
                if ch[i] not in V_: i += 1; continue
                j = i
                while j + 1 < len(ch) and ch[j + 1] in V_: j += 1
                nodes = ch[i:j + 1]
                unary = []
                for pos, k in enumerate(nodes):
                    d = g.dom[k]; u = np.zeros(len(d))
                    if pos == 0:
                        pj = g.prev[k, r]; Fj = g.nodes[pj][1] if pj not in V_ else None
                        assert Fj is not None
                        for a, F in enumerate(d): u[a] += cvec[len(F) - len(Fj)]
                    if pos == len(nodes) - 1:
                        nk = g.nxt[k, r]; Fn = g.nodes[nk][1]
                        for a, F in enumerate(d): u[a] += cvec[len(Fn) - len(F)]
                    unary.append(u)
                E = []
                for p, q in zip(nodes, nodes[1:]):
                    dp, dq = g.dom[p], g.dom[q]; m = np.full((len(dp), len(dq)), np.inf)
                    for a, F in enumerate(dp):
                        for b_, H in enumerate(dq):
                            if leq(F, H): m[a, b_] = cvec[len(H) - len(F)]
                    E.append(m)
                si = len(segs); segs.append(dict(reg=r, nodes=nodes, E=E, u0=unary))
                for pos, k in enumerate(nodes): self.seg_of[k].append((si, pos))
                i = j + 1
        self.segs = segs
        self.mu = {k: np.zeros(len(g.dom[k])) for k in self.vars if len(self.seg_of[k]) == 2}
    def _unaries(self, s):
        seg = self.segs[s]; out = []
        for pos, k in enumerate(seg["nodes"]):
            u = seg["u0"][pos].copy()
            if k in self.mu:
                (s1, _), (s2, _) = self.seg_of[k]
                u += self.mu[k] if s == s1 else -self.mu[k]
            out.append(u)
        return out
    def _minmarg(self, s):
        seg = self.segs[s]; U = self._unaries(s); n = len(U)
        f = [None] * n; b = [None] * n
        f[0] = U[0].copy()
        for i in range(1, n): f[i] = (f[i - 1][:, None] + seg["E"][i - 1]).min(axis=0) + U[i]
        b[n - 1] = np.zeros_like(U[n - 1])
        for i in range(n - 2, -1, -1): b[i] = (seg["E"][i] + (U[i + 1] + b[i + 1])[None, :]).min(axis=1)
        mm = [f[i] + b[i] for i in range(n)]
        return mm, float(f[n - 1].min())
    def dual_value(self):
        return sum(self._minmarg(s)[1] for s in range(len(self.segs)))
    def _fb(self, s):
        """forward/backward messages of segment s with the current multipliers (cached until invalidated)."""
        c = self._cache.get(s)
        if c is not None: return c
        seg = self.segs[s]; U = self._unaries(s); n = len(U)
        f = [None] * n; b = [None] * n
        f[0] = U[0].copy()
        for i in range(1, n): f[i] = (f[i - 1][:, None] + seg["E"][i - 1]).min(axis=0) + U[i]
        b[n - 1] = np.zeros_like(U[n - 1])
        for i in range(n - 2, -1, -1): b[i] = (seg["E"][i] + (U[i + 1] + b[i + 1])[None, :]).min(axis=1)
        self._cache[s] = (f, b); return f, b
    def sweep(self, alpha=None):
        """exact block-coordinate ascent: for each shared vertex v, mu_v <- (b - a)/2 where a, b are the two
        chains' min-marginals at v with mu_v removed.  The dual never decreases."""
        if not hasattr(self, "_cache"): self._cache = {}
        for k in self.vars:
            if k not in self.mu: continue
            (s1, p1), (s2, p2) = self.seg_of[k]
            f1, b1 = self._fb(s1); f2, b2 = self._fb(s2)
            m1 = f1[p1] + b1[p1]; m2 = f2[p2] + b2[p2]
            a = m1 - self.mu[k]; bb = m2 + self.mu[k]
            new = (bb - a) / 2.0
            ok = np.isfinite(new)
            if not ok.any(): continue
            new = np.where(ok, new, self.mu[k])
            if np.array_equal(new, self.mu[k]): continue
            self.mu[k] = new
            self._cache.pop(s1, None); self._cache.pop(s2, None)
        return
    def decode(self):
        """topological greedy primal: choose the label minimising the sum of min-marginals among labels
        nested over the already decided predecessors on both registers."""
        g = self.g; mms = [self._minmarg(s)[0] for s in range(len(self.segs))]
        score = {}
        for k in self.vars:
            sc = np.zeros(len(g.dom[k]))
            for (s, p) in self.seg_of[k]: sc += mms[s][p]
            score[k] = sc
        assign = {}
        for k in self.vars:   # node ids are a topological order
            best = None
            for a, F in enumerate(g.dom[k]):
                ok = True
                for r in g.nodes[k][0]:
                    pj = g.prev[k, r]; Fj = assign[pj] if pj in assign else (g.nodes[pj][1] if pj not in g.varset else None)
                    if Fj is None: continue
                    if not leq(Fj, F): ok = False; break
                if ok and (best is None or score[k][a] < best[0]): best = (score[k][a], F)
            assign[k] = best[1]
        return assign
    def primal_cost(self, assign):
        g = self.g; c = self.costs.c; tot = 0
        for s, seg in enumerate(self.segs):
            nodes = seg["nodes"]; r = seg["reg"]
            Fprev = g.nodes[g.prev[nodes[0], r]][1]
            for k in nodes:
                F = assign[k]
                if not leq(Fprev, F): return None
                tot += c[len(F) - len(Fprev)]; Fprev = F
            Fn = g.nodes[g.nxt[nodes[-1], r]][1]
            if not leq(Fprev, Fn): return None
            tot += c[len(Fn) - len(Fprev)]
        return tot
    def exact_multipliers(self):
        """the float multipliers as exact integers on the 2^mu_shift grid (Python ints, no int64 cast).
        Any finite integer multipliers give a valid bound: each shared vertex enters its two segments with opposite signs."""
        out = {}
        for k, v in self.mu.items():
            if not np.all(np.isfinite(v)): raise ValueError(("non-finite multiplier", k))
            out[k] = [round(Q(float(x)) * (1 << self.mu_shift)) for x in v]   # Fraction(float) is exact; round = rint
        return out
    def dual_bound_exact(self, mu_int=None):
        """exact integer weak-duality bound: unary and edge costs are taken from the integer table costs.c (never from
        the float arrays) and the multipliers from exact_multipliers(); all arithmetic is in Python integers."""
        g = self.g; wi = self.costs.c; total = 0
        mu_int = self.exact_multipliers() if mu_int is None else mu_int
        for s, seg in enumerate(self.segs):
            nodes = seg["nodes"]; r = seg["reg"]; f = None
            for pos, k in enumerate(nodes):
                dom = g.dom[k]; u = [0] * len(dom)
                if pos == 0:
                    dj = len(g.nodes[g.prev[k, r]][1]); u = [wi[len(F) - dj] for F in dom]
                if pos == len(nodes) - 1:
                    dn = len(g.nodes[g.nxt[k, r]][1]); u = [x + wi[dn - len(F)] for x, F in zip(u, dom)]
                if k in mu_int:
                    (s1, _), (s2, _) = self.seg_of[k]; m = mu_int[k]
                    u = [x + m[a] for a, x in enumerate(u)] if s == s1 else [x - m[a] for a, x in enumerate(u)]
                if f is None: f = u; continue
                dp = g.dom[nodes[pos - 1]]; nf = []
                for b_, H in enumerate(dom):
                    best = None
                    for a, F in enumerate(dp):
                        if f[a] is not None and leq(F, H):
                            v = f[a] + wi[len(H) - len(F)]
                            if best is None or v < best: best = v
                    nf.append(None if best is None else best + u[b_])
                f = nf
            total += min(x for x in f if x is not None)
        return total
    def solve(self, max_sweeps=400, alpha=None, tol=0.0, verbose=False, time_limit=None, check_every=3, gap_tol=None):
        """gap_tol=None: the surrogate rule (stop when the integer primal is within rounding slack of the float dual).
        gap_tol=x: stop when primal/2^mu_shift - dual <= x float units (interval certificates), or on a stall."""
        t0 = time.time(); best_assign = None; best_cost = None; last = -np.inf; hist = []; stall = 0
        self._cache = {}
        for it in range(max_sweeps):
            self.sweep()
            if it % check_every == check_every - 1 or it == max_sweeps - 1:
                dv = self.dual_value(); assign = self.decode(); pc = self.primal_cost(assign)
                if pc is not None and (best_cost is None or pc < best_cost): best_cost, best_assign = pc, assign
                hist.append((it, dv, pc))
                pu = None if best_cost is None else best_cost / (1 << self.mu_shift)
                if verbose: print(f"  sweep {it:4d} dual={dv:.6f} primal={pu} gap={None if pu is None else pu - dv:.6g}")
                if gap_tol is None:
                    if best_cost is not None and best_cost - dv <= tol + 0.51 * len(self.vars): break   # rounding slack
                elif pu is not None and pu - dv <= gap_tol: break
                stall = stall + 1 if dv - last < 1e-6 else 0
                last = dv
                if stall >= 3: break
                if time_limit and time.time() - t0 > time_limit: break
        db = self.dual_bound_exact()
        return dict(assign=best_assign, primal=best_cost, dual_exact=db, certified=(best_cost is not None and best_cost == db),
                    gap=(None if best_cost is None else best_cost - db), sweeps=it + 1, seconds=round(time.time() - t0, 2), history=hist)

# ---------------------------------------------------------------- exact VE with back-pointers (small components)
def solve_component_ve(g: Graph, costs: Costs, comp, max_tuples=30_000_000):
    """min-sum variable elimination over a component; returns (min cost, assignment) or None if too wide."""
    cset = set(comp); c = costs.c
    factors = []
    for (k, r), j in g.prev.items():
        if k in cset and j in cset:
            tab = {}
            for F in g.dom[j]:
                for H in g.dom[k]:
                    if leq(F, H): tab[(F, H)] = c[len(H) - len(F)]
            factors.append(([j, k], tab))
        elif k in cset:
            Fj = g.nodes[j][1]; factors.append(([k], {(F,): c[len(F) - len(Fj)] for F in g.dom[k]}))
        elif j in cset:
            Fk = g.nodes[k][1]; factors.append(([j], {(F,): c[len(Fk) - len(F)] for F in g.dom[j]}))
    # min-fill order
    adj = {k: set() for k in comp}
    for s, _ in factors:
        if len(s) == 2: adj[s[0]].add(s[1]); adj[s[1]].add(s[0])
    gg = {v: set(nb) for v, nb in adj.items()}; order = []
    def fill(v):
        nb = list(gg[v]); cnt = 0
        for i in range(len(nb)):
            for j in range(i + 1, len(nb)):
                if nb[j] not in gg[nb[i]]: cnt += 1
        return cnt
    while gg:
        v = min(gg, key=lambda x: (fill(x), len(gg[x]), x)); nb = list(gg[v])
        for i in range(len(nb)):
            for j in range(i + 1, len(nb)): gg[nb[i]].add(nb[j]); gg[nb[j]].add(nb[i])
        for u in nb: gg[u].discard(v)
        del gg[v]; order.append(v)
    active = [(list(s), dict(f)) for s, f in factors]; back = []
    for v in order:
        group = [(s, f) for s, f in active if v in s]; rest = [(s, f) for s, f in active if v not in s]
        scope = []
        for s, _ in group:
            for x in s:
                if x not in scope: scope.append(x)
        # enumerate joint table sparsely: start from the first factor, join others by shared keys
        cs, cf = list(group[0][0]), dict(group[0][1])
        for s, f in group[1:]:
            common = [x for x in s if x in cs]; new = [x for x in s if x not in cs]
            idx_s = {x: i for i, x in enumerate(s)}; idx_c = {x: i for i, x in enumerate(cs)}
            byc = collections.defaultdict(list)
            for key, val in f.items(): byc[tuple(key[idx_s[x]] for x in common)].append((tuple(key[idx_s[x]] for x in new), val))
            nf = {}
            for key, val in cf.items():
                for nk, nv in byc.get(tuple(key[idx_c[x]] for x in common), ()): nf[key + nk] = val + nv
            cs, cf = cs + new, nf
            if len(cf) > max_tuples: return None
        vi = cs.index(v); ns = cs[:vi] + cs[vi + 1:]; best = {}; arg = {}
        for key, val in cf.items():
            ctx = key[:vi] + key[vi + 1:]
            if ctx not in best or val < best[ctx]: best[ctx] = val; arg[ctx] = key[vi]
        back.append((v, ns, arg)); active = rest + ([(ns, best)] if ns else [([], {(): min(best.values())})])
    total = sum(f.get((), 0) for s, f in active if not s)
    assign = {}
    for v, ns, arg in reversed(back): assign[v] = arg[tuple(assign[x] for x in ns)]
    return total, assign

# ---------------------------------------------------------------- top-level
def moment_interval(g: Graph, costs: Costs, assign, bits=FINE_BITS, max_sweeps=600, ve_tuples=5_000_000, gap_tol=1e-9):
    """rigorous rational interval for the per-call moment at costs.b over every frame assignment of the model g.

    lower: Lagrangian (chain dual) or exact elimination bound on the FineCosts lower weights, in Python integers, plus
           lam * (total rank, constant) and the fixed boundary edges; lower <= min_x sum_e T_rank(e)(b).
    upper: the engines' upper bound of `assign` (sum_r H_r upper[r]); `assign`'s own lower bound is reported too.
    The fine solves are independent of the surrogate; their decoded assignment is reported (fine_profile, fine_upper)
    so that a surrogate optimum which is not the true optimum shows up as fine_upper < assignment_lower."""
    fr = lambda k: assign[k] if k in g.varset else g.nodes[k][1]
    if set(assign) != g.varset or not all(leq(fr(j), fr(k)) for (k, reg), j in g.prev.items()): raise ValueError("assignment is not a nested frame assignment of g")
    fc = costs.fine(bits); lb = 0; fine_assign = {}; parts = []
    for comp in g.components:
        res = solve_component_ve(g, fc, comp, max_tuples=ve_tuples) if len(comp) <= 600 else None
        if res is not None:
            cost, a = res; lb += cost; fine_assign.update(a); parts.append(("ve", len(comp))); continue
        dd = ChainDD(g, fc, var_subset=comp); r = dd.solve(max_sweeps=max_sweeps, gap_tol=gap_tol)
        lb += r["dual_exact"]; fine_assign.update(r["assign"])
        parts.append(("dd", len(comp), float(Q(r["gap"], 1 << bits) * (1 << costs.unit_bits)), r["sweeps"]))
    for (k, reg), j in g.prev.items():   # boundary edges between fixed vertices
        if k not in g.varset and j not in g.varset: lb += fc.c[len(g.nodes[k][1]) - len(g.nodes[j][1])]
    mass = sum(len(g.nodes[ch[-1]][1]) - len(g.nodes[ch[0]][1]) for ch in g.chains if ch)
    H, Hf = g.profile(assign), g.profile(fine_assign)
    if sum(r * n for r, n in H.items()) != mass or sum(r * n for r, n in Hf.items()) != mass: raise ValueError("rank mass does not telescope")
    lower = Q(lb, 1 << bits) + fc.lam * mass
    upper, a_lower = costs.moment_upper(H), costs.moment_exact(H)
    if lower > upper: raise ValueError("interval certificate inconsistent")
    unit = 1 << costs.unit_bits
    return dict(b=costs.b, lam=fc.lam, bits=bits, rank_mass=mass, lower=lower, upper=upper, assignment_lower=a_lower,
                width_units=float((upper - lower) * unit), fine_profile=dict(sorted(Hf.items())), fine_upper=costs.moment_upper(Hf),
                surrogate_not_minimal=costs.moment_upper(Hf) < a_lower, parts=parts)

def optimal_frames(w, costs: Costs, verbose=False, max_sweeps=300, ve_tuples=5_000_000, check_literal=True, graph=None, interval=False):
    """optimal frames of the integer surrogate for the fixed gate order of w. Returns dict(cost, profile, assign, certified,
    parts); with interval=True also 'interval' (moment_interval: rigorous bounds for the true per-call moment at b)."""
    g = graph if graph is not None else Graph(w, check_literal=check_literal); parts = []; assign = {}; total = 0; certified = True
    if check_literal: lit = g.literal(); lit_cost = costs.profile_cost(g.profile(lit))
    else: lit = None; lit_cost = None
    for comp in g.components:
        res = solve_component_ve(g, costs, comp, max_tuples=ve_tuples) if len(comp) <= 600 else None
        if res is not None:
            cost, a = res; assign.update(a); total += cost; parts.append(("ve", len(comp), cost, True)); continue
        dd = ChainDD(g, costs, var_subset=comp); r = dd.solve(max_sweeps=max_sweeps, verbose=verbose)
        assign.update(r["assign"]); total += r["primal"]; certified &= r["certified"]
        parts.append(("dd", len(comp), r["primal"], r["certified"], r["dual_exact"], r["sweeps"], r["seconds"]))
    H = g.profile(assign)
    # boundary edges between fixed vertices
    fixed = 0
    for (k, r), j in g.prev.items():
        if k not in g.varset and j not in g.varset: fixed += costs.c[len(g.nodes[k][1]) - len(g.nodes[j][1])]
    cost = total + fixed
    if cost != costs.profile_cost(H): raise ValueError(("component accounting mismatch", cost, costs.profile_cost(H)))
    out = dict(graph=g, cost=cost, profile=H, assign=assign, certified=certified, parts=parts,
               literal_profile=(g.profile(lit) if lit is not None else None), literal_cost=lit_cost,
               gain=(lit_cost - cost if lit_cost is not None else None))
    if interval: out["interval"] = moment_interval(g, costs, assign, ve_tuples=ve_tuples)
    return out

# ---------------------------------------------------------------- reorderings
def move_window(gates, i):
    """[lo, hi]: positions gate i may be moved to by commuting adjacent swaps."""
    lo = i
    while lo > 0 and commute(gates[lo - 1], gates[i]): lo -= 1
    hi = i
    while hi + 1 < len(gates) and commute(gates[hi + 1], gates[i]): hi += 1
    return lo, hi

def moved(gates, i, j):
    """new list with gate i moved to position j (caller guarantees commutation)."""
    g = list(gates); x = g.pop(i); g.insert(j, x); return g

def replay_map(w, sections=("A", "cut", "B")):
    """exact composed linear map of the listed sections as sparse Fraction rows (register -> {col: coef})."""
    N = 2 * V + R_of(w); rows = [{r: Q(1)} for r in range(N)]
    for sec in sections:
        for e in w[sec]: G.apply_op(e, rows)
    return rows

def apply_frames(w, g: Graph, assign):
    """write an assignment back into a copy of the word's A/B gate frames."""
    import copy
    w2 = copy.deepcopy(w)
    for k, F in assign.items():
        regs, F0, sec, idx = g.nodes[k]; w2[sec][idx][-1] = list(F)
    return w2

def full_profile(w):
    """independent recount (gk_word.profile): A/B climbs + centre descents."""
    return dict(G.profile(w))
