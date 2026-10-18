#!/usr/bin/env python3
"""P112 fixed-reader two-total correction at source union 48 (PR2382 OQ1).

Independent stdlib re-implementation; imports no predecessor checker.

Computes, from the pinned P112 geometry and the literal pairing rows:
  * the eight reader codes C_j and all their closed supports of size <= 48;
  * the exact geometric maximum L(U) = sum_j g_j(U) over |U| <= 47 and <= 48;
  * the maximum total retained loss of any configuration that passes the
    rank-two necessary condition N (every fully specified column subset of
    size >= 3 has exact rational rank <= 2), at caps 47 and 48;
  * an explicit two-column correction attaining retained loss 5 at |U| = 48,
    with exact pairing ranks and its complete separate-total COPY bill;
  * the PR1432/PR845 added-term price relaxation at M = 44..48;
  * negative controls (corrupted geometry pin, perturbed minor, three-column
    fake profile, corrupted receipt) which must be rejected.

Usage:  python3 -B verify.py            (compare with RESULT.json, print PASS)
        python3 -B verify.py --write P  (write a fresh receipt to new path P)

Prepared by thakrarsagar with substantial AI assistance from Claude
(Anthropic, Claude Opus 5.5). Apache-2.0.
"""
import hashlib
import itertools
import json
import os
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
GEOM_REL = "research/p112-single-lift/reference-geometry.json"
GEOM_SHA = "4f44af368e046002553d632ee90c6470990827cea3fae41f0f54018522d7a080"
NPORT = 112
NREAD = 8


class CheckFailure(Exception):
    pass


def require(cond, msg):
    if not cond:
        raise CheckFailure(msg)


def pc(x):
    return bin(x).count("1")


def load_geometry(raw):
    require(hashlib.sha256(raw).hexdigest() == GEOM_SHA, "geometry sha256 mismatch")
    return json.loads(raw.decode("utf-8"))


def par(a):
    return pc(a) & 1


def f2_rank(rows):
    basis = {}
    r = 0
    for v in rows:
        while v:
            h = v.bit_length() - 1
            if h in basis:
                v ^= basis[h]
            else:
                basis[h] = v
                r += 1
                break
    return r


def q_rank(M):
    M = [[Fraction(v) for v in row] for row in M]
    if not M:
        return 0
    r = 0
    for c in range(len(M[0])):
        p = next((i for i in range(r, len(M)) if M[i][c] != 0), None)
        if p is None:
            continue
        M[r], M[p] = M[p], M[r]
        for i in range(len(M)):
            if i != r and M[i][c] != 0:
                f = M[i][c] / M[r][c]
                M[i] = [a - f * b for a, b in zip(M[i], M[r])]
        r += 1
    return r


def mask_list(m):
    return [r for r in range(NPORT) if m >> r & 1]


class Geometry:
    def __init__(self, G):
        self.X = G["X"]
        self.lab = G["labels"]
        self.dua = G["duals"]
        require(len(self.X) == NPORT and all(len(r) == NREAD for r in self.X), "X shape")
        self.S = [[r for r in range(NPORT) if self.X[r][j] != 0] for j in range(NREAD)]
        self.SM = [sum(1 << r for r in s) for s in self.S]
        # literal pairing rows: row i of reader j is the word t -> v_i . l_t on S_j
        self.codes = []
        for j in range(NREAD):
            span = {0}
            for i in self.S[j]:
                w = 0
                for t in self.S[j]:
                    if par(self.dua[i] & self.lab[t]):
                        w |= 1 << t
                if w not in span:
                    span |= {s ^ w for s in span}
            self.codes.append(sorted(span))
        self.cut = [[self.SM[j] & self.SM[k] for k in range(NREAD)] for j in range(NREAD)]

    def beta(self, reader_support, source_support):
        """Independent engine: literal F2 rank of the pairing matrix."""
        rows = []
        for i in range(NPORT):
            if reader_support >> i & 1:
                w = 0
                for t in range(NPORT):
                    if source_support >> t & 1 and par(self.dua[i] & self.lab[t]):
                        w |= 1 << t
                rows.append(w)
        return f2_rank(rows)

    def kdim(self, j, V):
        n = sum(1 for c in self.codes[j] if c & ~V == 0)
        d = n.bit_length() - 1
        require(n == 1 << d, "kernel not a subspace")
        return d


def premises(g):
    out = {}
    wd = []
    for j in range(NREAD):
        c = g.codes[j]
        require(len(c) == 256, "code size")
        dist = {}
        for w in c:
            dist[pc(w)] = dist.get(pc(w), 0) + 1
        wd.append(sorted(dist.items()))
        # dual span of reader j has F2 dimension 8, so u -> c_u is a bijection
        require(f2_rank([g.dua[i] for i in g.S[j]]) == 8, "dual span dim")
    require(all(w == wd[0] for w in wd), "weight distributions differ")
    require(wd[0] == [(0, 1), (24, 63), (28, 128), (32, 63), (56, 1)], "weights")
    out["code_weights_all_readers"] = [list(x) for x in wd[0]]
    margins = set()
    for j in range(NREAD):
        for k in range(NREAD):
            if j == k:
                continue
            cjk = g.cut[j][k]
            require(pc(cjk) == 24, "cut size")
            require(cjk in g.codes[j] and cjk in g.codes[k], "cut word")
            inside = [c for c in g.codes[k] if c and c & ~g.SM[j] == 0]
            require(inside == [cjk], "unique word of C_k inside S_j")
            margins.add(min(pc(c & ~g.SM[j]) for c in g.codes[k] if c and c != cjk))
    require(margins == {12}, "outside margin")
    out["ordered_pairs_with_unique_cut_word_and_margin_12"] = 56
    # distinct source labels, so |supp z_h| active ports give |supp z_h| labels
    require(len(set(g.lab)) == NPORT, "source labels not distinct")
    out["distinct_source_labels"] = NPORT
    # sign balance of x_j x_k on every cut (used for the 4+1 support remark)
    for j in range(NREAD):
        for k in range(j + 1, NREAD):
            pr = [g.X[r][j] * g.X[r][k] for r in mask_list(g.cut[j][k])]
            require(sorted(set(pr)) == [-1, 1] and pr.count(1) == 12 and pr.count(-1) == 12,
                    "cut sign balance")
    out["cuts_with_sign_balance_12_12"] = 28
    return out


def closed_supports(g, cap):
    """All unions of codewords of C_j of size <= cap, with dim K_j(V)."""
    res = []
    for j in range(NREAD):
        words = [c for c in g.codes[j] if c and pc(c) <= cap]
        seen = set(words)
        fr = list(seen)
        while fr:
            nf = []
            for V in fr:
                for c in words:
                    W = V | c
                    if W != V and W not in seen and pc(W) <= cap:
                        seen.add(W)
                        nf.append(W)
            fr = nf
        res.append({V: g.kdim(j, V) for V in seen})
    return res


class NCheck:
    """Necessary condition for a rank-<=2 correction W = Z A^t with
    W[r,k] = X[r,k] on pattern rows P_k: every column subset K with |K| >= 3
    has exact rational rank X[intersection of P_k, K] <= 2."""

    def __init__(self, X):
        self.X = X
        self.cache = {}

    def rk(self, rows, cols):
        key = (rows, tuple(cols))
        v = self.cache.get(key)
        if v is None:
            rl = mask_list(rows)
            v = q_rank([[self.X[r][c] for c in cols] for r in rl]) if len(rl) >= 3 else len(rl)
            self.cache[key] = v
        return v

    def ok_add(self, cfg, newk):
        others = [k for k in cfg if k != newk]
        for s in range(2, len(others) + 1):
            for sub in itertools.combinations(others, s):
                R = cfg[newk]
                for k in sub:
                    R &= cfg[k]
                if pc(R) >= 3 and self.rk(R, tuple(sorted(sub + (newk,)))) >= 3:
                    return False
        return True

    def first_violation(self, cfg):
        ks = sorted(cfg)
        for s in range(3, len(ks) + 1):
            for sub in itertools.combinations(ks, s):
                R = (1 << NPORT) - 1
                for k in sub:
                    R &= cfg[k]
                if pc(R) >= 3 and self.rk(R, sub) >= 3:
                    return R, sub
        return None


def lead_search(g, closed, cap, nc):
    """All configurations whose largest closed support V (at lead reader j)
    has size >= 36, i.e. dimension >= 2."""
    st = {"geo_max": 0, "real_max": 0, "geo_wit": None}
    geo_hist = {}
    real_shapes = {}
    small = [sorted((W, dw) for W, dw in closed[k].items() if pc(W) <= 36) for k in range(NREAD)]
    for j in range(NREAD):
        others = [k for k in range(NREAD) if k != j]
        for V in sorted(closed[j]):
            d = closed[j][V]
            s = pc(V)
            if s > cap or s < 36:
                continue
            if s > 36 or cap - 36 < 12:
                # Budget < 12 outside V: by the margin-12 premise only cut words
                # C_jk fit; U = V u cuts is then a closed support of C_j itself.
                gl = d + sum(1 for k in others if g.cut[j][k] & ~V == 0)
                geo_hist[gl] = geo_hist.get(gl, 0) + 1
                if gl > st["geo_max"]:
                    st["geo_max"] = gl
                    st["geo_wit"] = (j, V)

                def dfs(idx, U, cfg, K):
                    tot = d + len(K)
                    st["real_max"] = max(st["real_max"], tot)
                    if tot >= 5:
                        shp = "+".join(map(str, sorted([d] + [1] * len(K), reverse=True)))
                        real_shapes[shp] = real_shapes.get(shp, 0) + 1
                    for t in range(idx, len(others)):
                        k = others[t]
                        U2 = U | g.cut[j][k]
                        if pc(U2) > cap:
                            continue
                        cfg[k] = g.cut[j][k]
                        if nc.ok_add(cfg, k):
                            dfs(t + 1, U2, cfg, K + [k])
                        del cfg[k]

                dfs(0, V, {j: V}, [])
            else:
                # s == 36 with a 12-port budget: enumerate all other supports
                cand = {k: [(W, dw) for W, dw in small[k] if pc(W & ~V) <= cap - 36]
                        for k in others}

                def dfs2(idx, U, cfg, dims, okN):
                    L = sum(g.kdim(k, U & g.SM[k]) for k in range(NREAD))
                    geo_hist[L] = geo_hist.get(L, 0) + 1
                    if L > st["geo_max"]:
                        st["geo_max"] = L
                        st["geo_wit"] = (j, U)
                    if okN:
                        tot = sum(dims)
                        st["real_max"] = max(st["real_max"], tot)
                        if tot >= 5:
                            shp = "+".join(map(str, sorted(dims, reverse=True)))
                            real_shapes[shp] = real_shapes.get(shp, 0) + 1
                    for t in range(idx, len(others)):
                        k = others[t]
                        for W, dw in cand[k]:
                            U2 = U | W
                            if pc(U2) > cap:
                                continue
                            cfg[k] = W
                            ok2 = okN and nc.ok_add(cfg, k)
                            dfs2(t + 1, U2, cfg, dims + [dw], ok2)
                            del cfg[k]

                dfs2(0, V, {j: V}, [d], True)
    return st["geo_max"], st["real_max"], geo_hist, real_shapes, st["geo_wit"]


def single_word_search(g, cap_hi, caps, nc):
    """All configurations of single codewords (closed supports of size <= 32)
    from distinct readers with union <= cap."""
    W = []
    R = []
    for j in range(NREAD):
        for c in g.codes[j]:
            if c and pc(c) <= 32:
                W.append(c)
                R.append(j)
    n = len(W)
    compat = [0] * n
    for a in range(n):
        m = 0
        for b in range(a + 1, n):
            if R[b] > R[a] and pc(W[a] | W[b]) <= cap_hi:
                m |= 1 << b
        compat[a] = m
    rmask = [sum(1 << i for i in range(n) if R[i] == j) for j in range(NREAD)]
    unions = {cap: {} for cap in caps}
    tuples = {cap: {} for cap in caps}
    passing = {cap: {} for cap in caps}
    wit = {}

    def dfs(U, cand, cfg, okN):
        m = len(cfg)
        u = pc(U)
        rs = tuple(sorted(cfg))
        for cap in caps:
            if u <= cap:
                unions[cap].setdefault(rs, set()).add(U)
                tuples[cap][m] = tuples[cap].get(m, 0) + 1
                if okN:
                    passing[cap][m] = passing[cap].get(m, 0) + 1
                    if m >= 5 and (cap, m) not in wit:
                        wit[(cap, m)] = dict(cfg)
        c = cand
        while c:
            b = c & -c
            i = b.bit_length() - 1
            c ^= b
            U2 = U | W[i]
            if pc(U2) <= cap_hi:
                k = R[i]
                cfg[k] = W[i]
                ok2 = okN and nc.ok_add(cfg, k)
                dfs(U2, cand & compat[i] & ~((1 << (i + 1)) - 1) & ~rmask[k], cfg, ok2)
                del cfg[k]

    for a in range(n):
        dfs(W[a], compat[a], {R[a]: W[a]}, True)
    out = {}
    for cap in caps:
        ucount = {}
        for rs, us in unions[cap].items():
            ucount[len(rs)] = ucount.get(len(rs), 0) + len(us)
        out[cap] = {
            "distinct_unions_by_reader_subset_size": {str(k): v for k, v in sorted(ucount.items())},
            "word_tuples_by_size": {str(k): v for k, v in sorted(tuples[cap].items())},
            "N_passing_tuples_by_size": {str(k): v for k, v in sorted(passing[cap].items())},
            "geometric_max_readers": max(tuples[cap]),
            "N_passing_max": max(passing[cap]),
        }
    return out, wit


def price(m):
    r = 1
    while m > 2 ** (r + 1):
        r += 1
    return r


def price_min(M):
    best = None
    for m1 in range(1, M + 1):
        for m2 in range(m1, M + 1):
            if m1 + m2 >= M:
                v = price(m1) + price(m2)
                best = v if best is None else min(best, v)
    return best


def realize(g, cols):
    """Correction W with W[:,k] = x_k on pattern rows cols[k], zero elsewhere.
    Returns retained losses (exact F2 pairing ranks of x_k against
    y_k = x_k - w_k), the exact rational rank of W, W and Y."""
    X = g.X
    Wm = [[0] * NREAD for _ in range(NPORT)]
    for k, P in cols.items():
        for r in mask_list(P):
            Wm[r][k] = X[r][k]
    Y = [[X[r][c] - Wm[r][c] for c in range(NREAD)] for r in range(NPORT)]
    losses = []
    for k in range(NREAD):
        ysup = sum(1 << r for r in range(NPORT) if Y[r][k] != 0)
        losses.append(8 - g.beta(g.SM[k], ysup))
    return losses, q_rank(Wm), Wm, Y


def first_4plus1(g, closed, need=1):
    for j in range(NREAD):
        for V in sorted(closed[j]):
            if closed[j][V] == 4 and pc(V) == 48:
                ks = [k for k in range(NREAD) if k != j and g.cut[j][k] & ~V == 0]
                if len(ks) >= need:
                    return (j, V) + tuple(ks[:need])
    return None


def check_witness(g, j, V, k):
    X = g.X
    losses, rW, Wm, Y = realize(g, {j: V, k: g.cut[j][k]})
    Z = [[Wm[r][j], Wm[r][k]] for r in range(NPORT)]
    A = [[0, 0] for _ in range(NREAD)]
    A[j] = [1, 0]
    A[k] = [0, 1]
    require(q_rank(Z) == 2 and q_rank(A) == 2, "full-rank factors")
    U = sum(1 << r for r in range(NPORT) if Z[r][0] != 0 or Z[r][1] != 0)
    XA = [[sum(X[r][c] * A[c][h] for c in range(NREAD)) for h in range(2)] for r in range(NPORT)]
    for a in range(NPORT):
        for b in range(NPORT):
            lhs = sum(X[a][c] * X[b][c] for c in range(NREAD))
            rhs = (sum(X[a][c] * Y[b][c] for c in range(NREAD))
                   + sum(XA[a][h] * Z[b][h] for h in range(2)))
            require(lhs == rhs, "decoder identity")
    added = []
    for h in range(2):
        dsup = sum(1 << r for r in range(NPORT) if XA[r][h] != 0)
        zsup = sum(1 << r for r in range(NPORT) if Z[r][h] != 0)
        added.append(g.beta(dsup, zsup))
    retained = [8 - l for l in losses]
    return {
        "reader_j": j,
        "reader_k": k,
        "U_ports": mask_list(U),
        "U_size": pc(U),
        "kernel_dim_at_j_via_code": g.kdim(j, V),
        "z_support_sizes": [pc(V), pc(g.cut[j][k])],
        "rank_Z": 2,
        "rank_A": 2,
        "rank_W": rW,
        "retained_losses": losses,
        "retained_copy_ranks": retained,
        "retained_sum": sum(retained),
        "added_copy_ranks": added,
        "total_copy_bill": sum(retained) + sum(added),
        "rank_X_Z": q_rank([X[r] + Z[r] for r in range(NPORT)]),
        "identity_pairs_checked": NPORT * NPORT,
    }


def run(raw_geom):
    g = Geometry(load_geometry(raw_geom))
    res = {"geometry": {"path": GEOM_REL, "sha256": GEOM_SHA}}
    res["premises"] = premises(g)
    closed = closed_supports(g, 48)
    census = []
    for j in range(NREAD):
        c = {}
        for V, d in closed[j].items():
            key = "dim%d_size%d" % (d, pc(V))
            c[key] = c.get(key, 0) + 1
        census.append(c)
    require(all(c == census[0] for c in census), "closed census differs by reader")
    res["closed_support_census_each_reader_cap48"] = dict(sorted(census[0].items()))
    nc = NCheck(g.X)
    bands = {}
    sw, swwit = single_word_search(g, 48, (47, 48), nc)
    for cap in (47, 48):
        gm, rm, gh, rs, gw = lead_search(g, closed, cap, nc)
        bands[str(cap)] = {
            "lead_dim_ge2": {
                "geometric_max": gm,
                "N_passing_max": rm,
                "geometric_value_histogram": {str(k): v for k, v in sorted(gh.items())},
                "N_passing_config_shapes_total_ge5": dict(sorted(rs.items())),
            },
            "single_words": sw[cap],
            "geometric_max_L": max(gm, sw[cap]["geometric_max_readers"]),
            "two_column_retained_loss_upper_bound": max(rm, sw[cap]["N_passing_max"]),
            "price_min": price_min(cap),
        }
        if cap == 48:
            j, U = gw
            vec = [g.kdim(k, U & g.SM[k]) for k in range(NREAD)]
            vec2 = [8 - g.beta(g.SM[k], g.SM[k] & ~U) for k in range(NREAD)]
            require(vec == vec2, "two loss engines disagree")
            require(sum(vec) == bands["48"]["geometric_max_L"], "geometric witness")
            cfgV = {}
            for k in range(NREAD):
                if vec[k] > 0:
                    acc = 0
                    for c in g.codes[k]:
                        if c & ~U == 0:
                            acc |= c
                    cfgV[k] = acc
            viol = nc.first_violation(cfgV)
            require(viol is not None, "geometric maximum configuration should violate N")
            R, sub = viol
            bands["48"]["geometric_witness"] = {
                "lead_reader": j, "U_ports": mask_list(U), "U_size": pc(U),
                "loss_vector": vec,
                "N_violation": {"rows": mask_list(R), "cols": list(sub), "rank": nc.rk(R, sub)}}
            if (48, 5) in swwit:
                bands["48"]["single_word_five_tuple_passing_N_example"] = {
                    str(k): mask_list(v) for k, v in sorted(swwit[(48, 5)].items())}
    res["bands"] = bands
    res["price_min_by_M"] = {str(M): price_min(M) for M in range(44, 49)}
    w = first_4plus1(g, closed, 1)
    require(w is not None, "no 4+1 witness")
    wit = check_witness(g, *w)
    require(sum(wit["retained_losses"]) == 5 and wit["rank_W"] == 2 and wit["U_size"] == 48,
            "two-column witness does not attain loss 5 at 48")
    res["two_column_loss5_witness"] = wit
    f48 = 64 - bands["48"]["two_column_retained_loss_upper_bound"] + price_min(48)
    f47 = 64 - bands["47"]["two_column_retained_loss_upper_bound"] + price_min(47)
    res["floors"] = {
        "full_rank_two_total_copy_floor_cap47": f47,
        "full_rank_two_total_copy_floor_at_48": f48,
        "relaxation_floor_attained_by_loss_bound_at_48": (
            sum(wit["retained_losses"]) == bands["48"]["two_column_retained_loss_upper_bound"]),
    }
    # ---- negative controls (each must be rejected) ----
    ncs = {}
    bad = bytearray(raw_geom)
    pos = bad.index(b'"X"') + 10
    bad[pos:pos + 1] = b"7" if bad[pos:pos + 1] != b"7" else b"8"
    try:
        load_geometry(bytes(bad))
        ncs["corrupted_geometry_pin"] = "ACCEPTED"
    except CheckFailure:
        ncs["corrupted_geometry_pin"] = "rejected"
    viol = bands["48"]["geometric_witness"]["N_violation"]
    M = [[g.X[r][c] for c in viol["cols"]] for r in viol["rows"]]
    Mp = [row[:2] + [row[0] + row[1]] + row[3:] for row in M]
    ncs["perturbed_minor"] = {"original_rank": q_rank(M), "perturbed_rank": q_rank(Mp),
                              "status": "rejected" if q_rank(M) >= 3 and q_rank(Mp) <= 2 else "ACCEPTED"}
    fake = first_4plus1(g, closed, 2)
    require(fake is not None, "no fake profile")
    j, V, k, l = fake
    losses, rW, _, _ = realize(g, {j: V, k: g.cut[j][k], l: g.cut[j][l]})
    bound = bands["48"]["two_column_retained_loss_upper_bound"]
    ncs["three_column_fake_profile"] = {
        "readers": [j, k, l], "retained_loss": sum(losses), "rank_W": rW,
        "status": "rejected" if (rW >= 3 and sum(losses) > bound) else "ACCEPTED"}
    res["negative_controls"] = ncs
    return res


def receipt_matches(rec, res):
    return rec == res


def main(argv):
    if len(argv) >= 2 and argv[0] == "--write":
        require(not os.path.exists(argv[1]), "refusing to overwrite")
    raw = open(os.path.join(ROOT, GEOM_REL), "rb").read()
    res = json.loads(json.dumps(run(raw), sort_keys=True))
    ncs = res["negative_controls"]
    require(ncs["corrupted_geometry_pin"] == "rejected", "NC1 corrupted pin accepted")
    require(ncs["perturbed_minor"]["status"] == "rejected", "NC2 perturbed minor accepted")
    require(ncs["three_column_fake_profile"]["status"] == "rejected", "NC3 fake profile accepted")
    if len(argv) >= 2 and argv[0] == "--write":
        with open(argv[1], "w") as f:
            json.dump(res, f, indent=1, sort_keys=True)
            f.write("\n")
        print("WROTE", argv[1])
        return
    rec = json.load(open(os.path.join(HERE, "RESULT.json")))
    require(receipt_matches(rec, res), "RESULT.json mismatch")
    # NC4: the same comparison function must reject a receipt whose floor is altered.
    bad = json.loads(json.dumps(rec))
    bad["floors"]["full_rank_two_total_copy_floor_at_48"] += 1
    require(not receipt_matches(bad, res), "NC4 corrupted receipt accepted")
    b = res["bands"]
    print("PASS_P112_TWO_TOTAL_UNION48 geometric_max_47=%d geometric_max_48=%d "
          "two_column_loss_bound_47=%d two_column_loss_bound_48=%d loss5_witness_bill=%d "
          "full_rank_copy_floor_48=%d no_new_kappa" % (
              b["47"]["geometric_max_L"], b["48"]["geometric_max_L"],
              b["47"]["two_column_retained_loss_upper_bound"],
              b["48"]["two_column_retained_loss_upper_bound"],
              res["two_column_loss5_witness"]["total_copy_bill"],
              res["floors"]["full_rank_two_total_copy_floor_at_48"]))


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except CheckFailure as e:
        print("FAIL", e)
        sys.exit(1)
