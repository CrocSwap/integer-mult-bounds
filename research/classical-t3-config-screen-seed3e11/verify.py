"""Classical rich configurations as T=3 tight-atom / counterexample candidates.

Model (DreamingOfClouds, #2111 research/three-total-decoders README section 1):
a configuration is a set of lines t = (p(t), q(t)) with p a point in Q^3 and q a
covector, p(t).q(t) != 0.  R_j = {t : p_j(t) != 0}, A_j = {s : q_j(s) != 0}.
An admissible pairing B over F2 has unit diagonal and B_ts = 1 (t != s) only where
p(t).q(s) = 0.  cost(B) = sum_j rank_F2 B[R_j, A_j], and the raw pairing cost of a
configuration is min over all admissible B.

The T=3 open core (Q <= F2) predicts cost >= v for every rank-3 configuration;
comment 18932893 item 4 of the handoffs thread names Pappus, Desargues, Reye and
D4 line arrangements as untested candidates for tight atoms (cost = v) or
counterexamples (cost < v).  This script builds the Pappus and Desargues pair
sets exactly, validates the cost engine against two pinned known-value controls
from #2111, and runs the falsifier/tight-atom census on a stated bounded domain:
every sub-configuration of size v <= 4 of each pair set, and a fixed-seed sample
of sizes v = 5..10, each priced exactly over all admissible B whenever the free
incidence count f <= 20.

Written for research/classical-t3-config-screen-seed3e11 (Aaron Wang, with help
from opencode).  Apache-2.0.  Standard library only.
"""
import itertools
import json
import os
import random
import sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
sys.stdout.reconfigure(encoding="utf-8")

EXACT_F_CAP = 20            # exact enumeration over all 2^f admissible B
CENSUS_EXHAUSTIVE_MAX = 4   # all subsets of size <= 4 of each pair set
SAMPLE_SIZES = {5: 3000, 6: 1500, 7: 300, 8: 60, 9: 20, 10: 10}
SAMPLE_SEED = 20261015
SEARCH_RESTARTS = 120       # randomized falsifier search per full pair set


# ---------------------------------------------------------------- geometry --
def cross(u, v):
    return (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])


def dot(u, v):
    return sum(a * b for a, b in zip(u, v))


def line_through(p, r):
    c = cross(p, r)
    assert c != (0, 0, 0)
    return c


def pappus():
    """Pappus configuration (9_3): A-triple, B-triple, three cross intersections."""
    A = [(F(0), F(0), F(1)), (F(1), F(0), F(1)), (F(2), F(0), F(1))]
    B = [(F(0), F(1), F(1)), (F(1), F(1), F(1)), (F(3), F(1), F(1))]
    LA = line_through(A[0], A[1])
    LB = line_through(B[0], B[1])
    Cs = []
    for i, j in ((0, 1), (0, 2), (1, 2)):
        Cs.append(cross(line_through(A[i], B[j]), line_through(A[j], B[i])))
    LC = line_through(Cs[0], Cs[1])
    assert dot(LC, Cs[2]) == 0
    pts = A + B + Cs
    lines = [LA, LB, LC] + [line_through(A[i], B[j]) for i in range(3) for j in range(3) if i != j]
    return pts, lines


def desargues():
    """Desargues configuration (10_3): two perspective triangles plus centre and axis."""
    O = (F(0), F(0), F(1))
    A = [(F(1), F(0), F(1)), (F(0), F(1), F(1)), (F(2), F(3), F(1))]
    lams = [F(2), F(3), F(5)]
    B = [tuple((1 - l) * O[k] + l * a[k] for k in range(3)) for l, a in zip(lams, A)]
    Cs = []
    for i, j in ((0, 1), (0, 2), (1, 2)):
        Cs.append(cross(line_through(A[i], A[j]), line_through(B[i], B[j])))
    axis = line_through(Cs[0], Cs[1])
    assert dot(axis, Cs[2]) == 0
    pts = A + B + [O] + Cs
    lines = ([line_through(A[i], A[j]) for i, j in ((0, 1), (0, 2), (1, 2))] +
             [line_through(B[i], B[j]) for i, j in ((0, 1), (0, 2), (1, 2))] +
             [line_through(O, A[i]) for i in range(3)] + [axis])
    return pts, lines


def check_geometry(name, pts, lines):
    inc_p = [[1 if dot(p, q) == 0 else 0 for q in lines] for p in pts]
    per_line = [sum(inc_p[p][l] for p in range(len(pts))) for l in range(len(lines))]
    per_pt = [sum(inc_p[p][l] for l in range(len(lines))) for p in range(len(pts))]
    assert set(per_line) == {3} and set(per_pt) == {3}, (name, per_line, per_pt)
    return sum(per_line)


# ------------------------------------------------------------- cost engine --
def rank2(rows):
    piv = []
    for x in rows:
        for p in piv:
            x = min(x, x ^ p)
        if x:
            piv.append(x)
            piv.sort(reverse=True)
    return len(piv)


class Instance:
    """A configuration given as lists of integer point and covector triples."""

    def __init__(self, P, Q):
        assert len(P) == len(Q) and len(P) >= 1
        self.v = len(P)
        self.P = [tuple(map(int, p)) for p in P]
        self.Q = [tuple(map(int, q)) for q in Q]
        for t in range(self.v):
            if dot(self.P[t], self.Q[t]) == 0:
                raise ValueError("ill-formed line: p(t).q(t) = 0")
        self.R = [[t for t in range(self.v) if self.P[t][j] != 0] for j in range(3)]
        self.A = [[s for s in range(self.v) if self.Q[s][j] != 0] for j in range(3)]
        rs = [set(r) for r in self.R]
        aa = [set(a) for a in self.A]
        self.free = [(t, s) for t in range(self.v) for s in range(self.v)
                     if t != s and dot(self.P[t], self.Q[s]) == 0
                     and any(t in rs[j] and s in aa[j] for j in range(3))]
        self.f = len(self.free)
        self.idx = {e: i for i, e in enumerate(self.free)}
        self.blocks = []
        for j in range(3):
            rows, cols = self.R[j], self.A[j]
            fixed = [(ti, cols.index(t)) for ti, t in enumerate(rows) if t in aa[j]]
            bits = [(ti, si, self.idx[(t, s)])
                    for ti, t in enumerate(rows) for si, s in enumerate(cols)
                    if t != s and (t, s) in self.idx]
            self.blocks.append((len(rows), fixed, bits))

    def block_ranks(self, g):
        out = []
        for nr, fixed, bits in self.blocks:
            rr = [0] * nr
            for ti, si in fixed:
                rr[ti] ^= 1 << si
            for ti, si, b in bits:
                if (g >> b) & 1:
                    rr[ti] ^= 1 << si
            out.append(rank2(rr))
        return out

    def cost(self, g):
        return sum(self.block_ranks(g))

    def exact_min(self, cap=EXACT_F_CAP):
        """Exhaustive minimum over all 2^f admissible B, with early abort per g."""
        if self.f > cap:
            return None, None, None
        best = 10 ** 9
        best_g = None
        nm = 0
        for g in range(1 << self.f):
            tot = 0
            for nr, fixed, bits in self.blocks:
                rr = [0] * nr
                for ti, si in fixed:
                    rr[ti] ^= 1 << si
                for ti, si, b in bits:
                    if (g >> b) & 1:
                        rr[ti] ^= 1 << si
                tot += rank2(rr)
                if tot >= best:
                    break
            if tot < best:
                best, best_g, nm = tot, g, 1
            elif tot == best:
                nm += 1
        return best, best_g, nm

    def search_best(self, restarts, rng):
        """Randomized single-bit descent; returns (best cost, best g)."""
        best = 10 ** 9
        best_g = 0
        for _ in range(restarts):
            g = rng.randrange(1 << self.f) if self.f else 0
            c = self.cost(g)
            improved = True
            while improved:
                improved = False
                order = list(range(self.f))
                rng.shuffle(order)
                for b in order:
                    h = g ^ (1 << b)
                    ch = self.cost(h)
                    if ch < c:
                        g, c, improved = h, ch, True
                        break
            if c < best:
                best, best_g = c, g
        return best, best_g


def load_fixture(path):
    d = json.load(open(path, encoding="utf-8"))
    if len(d) in (2, 3) and isinstance(d[0][0], list) and isinstance(d[0][0][0], int):
        return list(zip(d[0], d[1]))
    return [tuple((tuple(l[0]), tuple(l[1]))) for l in d]


def make_instance(pts, lines, V, comb):
    P = [pts[V[t][0]] for t in comb]
    Q = [lines[V[t][1]] for t in comb]
    return Instance(P, Q)


# -------------------------------------------------------------------- main --
def main():
    result = {"marker": "CLASSICAL_T3_CONFIG_SCREEN",
              "model": "three-total-decoders #2111 research/three-total-decoders README section 1",
              "exact_f_cap": EXACT_F_CAP,
              "exhaustive_max_v": CENSUS_EXHAUSTIVE_MAX,
              "sample_sizes": SAMPLE_SIZES, "sample_seed": SAMPLE_SEED}

    # 1. Positive controls: pinned #2111 configurations with documented exact minima.
    controls = [
        ("data/cex_wholeTS_v9.json", 18, [7, 4, 7], 16),
        ("data/cex_joint_v7.json", 12, [4, 4, 4], None),
    ]
    ctrl_out = []
    for rel, want_cost, want_ranks, want_nm in controls:
        lines = load_fixture(os.path.join(HERE, rel))
        inst = Instance([p for p, q in lines], [q for p, q in lines])
        best, g, nm = inst.exact_min()
        assert best == want_cost, (rel, best, want_cost)
        ranks = inst.block_ranks(g)
        assert sorted(ranks) == sorted(want_ranks), (rel, ranks, want_ranks)
        if want_nm is not None:
            assert nm == want_nm, (rel, nm, want_nm)
        ctrl_out.append({"control": rel, "v": inst.v, "f": inst.f, "min_cost": best,
                         "witness_block_ranks": ranks, "minimisers": nm})
    result["controls"] = ctrl_out

    # 2. Failure controls.
    rejected = 0
    for P, Q in (([(1, 0, 0)], [(0, 1, 0)]),      # p.q = 0 must be rejected
                 ([(1, 1, 1)], [(1, -1, 0)])):   # p.q = 0 must be rejected
        try:
            Instance(P, Q)
        except ValueError:
            rejected += 1
    assert rejected == 2
    lines = load_fixture(os.path.join(HERE, "data/cex_wholeTS_v9.json"))
    tampered = list(lines)
    p0, q0 = tampered[0]
    tampered[0] = ((p0[0] + 1, p0[1], p0[2]), q0)
    if dot(tampered[0][0], tampered[0][1]) == 0:
        tampered[0] = ((p0[0] - 1, p0[1], p0[2]), q0)
    ti = Instance([p for p, q in tampered], [q for p, q in tampered])
    tbest, _, _ = ti.exact_min()
    assert tbest != 18, "tamper control did not change the optimum"
    inst9 = Instance([p for p, q in lines], [q for p, q in lines])
    disallowed = [(t, s) for t in range(inst9.v) for s in range(inst9.v)
                  if t != s and (t, s) not in inst9.idx]
    assert len(disallowed) > 0
    result["failure_controls"] = {"ill_formed_rejected": rejected,
                                  "tampered_min_cost": tbest,
                                  "disallowed_positions": len(disallowed)}

    # 3. Geometries and pair sets.
    geoms = {}
    for name, fn in (("Pappus", pappus), ("Desargues", desargues)):
        pts, lines = fn()
        inc = check_geometry(name, pts, lines)
        V = [(p, q) for p in range(len(pts)) for q in range(len(lines))
             if dot(pts[p], lines[q]) != 0]
        geoms[name] = (pts, lines, V, inc)

    # 4. Census and full-pair-set falsifier search.
    for name, (pts, lines, V, inc) in geoms.items():
        rec = {"geometric_incidences": inc, "valid_pairs": len(V)}
        full = make_instance(pts, lines, V, tuple(range(len(V))))
        rng = random.Random(SAMPLE_SEED)
        dense_cost = full.cost((1 << full.f) - 1)
        identity_cost = full.cost(0)
        best, bg = full.search_best(SEARCH_RESTARTS, rng)
        rec["full_pair_set"] = {
            "v": full.v, "f": full.f,
            "dense_cost": dense_cost, "identity_cost": identity_cost,
            "search_best_cost": best, "search_best_block_ranks": full.block_ranks(bg),
            "search_restarts": SEARCH_RESTARTS,
            "falsifier_found": best < full.v}
        assert not rec["full_pair_set"]["falsifier_found"], name

        sizes = {}
        rng = random.Random(SAMPLE_SEED + 1)
        universe = list(range(len(V)))
        for v in range(1, 11):
            if v <= CENSUS_EXHAUSTIVE_MAX:
                combos = itertools.combinations(universe, v)
            else:
                combos = [tuple(sorted(rng.sample(universe, v)))
                          for _ in range(SAMPLE_SIZES[v])]
            tested = exact = tight = fals = skipped = 0
            min_seen = 10 ** 9
            for comb in combos:
                ci = make_instance(pts, lines, V, comb)
                tested += 1
                best, g, _ = ci.exact_min()
                if best is None:
                    skipped += 1
                    continue
                exact += 1
                min_seen = min(min_seen, best)
                if best < v:
                    fals += 1
                if best == v:
                    tight += 1
            sizes[v] = {"tested": tested, "exact": exact, "skipped_f_cap": skipped,
                        "falsifiers": fals, "tight": tight,
                        "min_cost_seen": None if exact == 0 else min_seen}
            assert fals == 0, (name, v)
        rec["census"] = sizes
        result.setdefault("census", {})[name] = rec

    with open(os.path.join(HERE, "RESULT.json"), "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=1, sort_keys=True)

    c0, c1 = ctrl_out[0], ctrl_out[1]
    P = result["census"]["Pappus"]
    D = result["census"]["Desargues"]
    p_exact = sum(s["exact"] for s in P["census"].values())
    d_exact = sum(s["exact"] for s in D["census"].values())
    p_tight = sum(s["tight"] for s in P["census"].values())
    d_tight = sum(s["tight"] for s in D["census"].values())
    print("PASS_CLASSICAL_T3_CONFIG_SCREEN "
          f"controls={c0['min_cost']}/{c1['min_cost']} "
          f"pappus_exact={p_exact} pappus_tight={p_tight} "
          f"desargues_exact={d_exact} desargues_tight={d_tight} "
          f"falsifiers=0 full_best={P['full_pair_set']['search_best_cost']}/"
          f"{D['full_pair_set']['search_best_cost']} no_new_kappa")


if __name__ == "__main__":
    main()
