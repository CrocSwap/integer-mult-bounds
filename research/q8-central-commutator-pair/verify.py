"""Exact paid-call minima for central commutator targets in formal F2[Q8].

Model (see README): G = Q8 = {+-1, +-i, +-j, +-k}, paid labels x = i, y = j
only, paid factors D_N(g) = I + ([g]+1)N with N = u v^T, v^T u = 1, over
F2^r. Free scalar GL_r(F2) mixing is normalized by augmentation (predecessor
research/bit-dihedral-commutator argument; closure is checked below).

Engine A (BFS): formal r x r matrices over F2[Q8] with 8-bit coefficient
masks and a precomputed 256x256 convolution table. Engine B (independent):
frozenset-of-group-elements formal matrices and Hamilton 4-tuple quaternion
multiplication. Acceptance is equality in every coefficient of the full
group algebra, not equality in one finite address representation.

Stdlib only. python -I -O -B research/q8-central-commutator-pair/verify.py
"""
import hashlib
import json
import os
import sys

# ---------------------------------------------------------------- Q8, engine A
# element index = 4*sign + unit: 0=+1, 1=+i, 2=+j, 3=+k, 4=-1, 5=-i, 6=-j, 7=-k
_UNIT_MUL = [
    [0, 1, 2, 3],
    [1, 0, 3, 2],
    [2, 3, 0, 1],
    [3, 2, 1, 0],
]
_UNIT_SIGN = [
    [0, 0, 0, 0],
    [0, 1, 0, 1],
    [0, 1, 1, 0],
    [0, 0, 1, 1],
]


def qmul(a, b):
    sa, ua = divmod(a, 4)
    sb, ub = divmod(b, 4)
    s = (sa + sb + _UNIT_SIGN[ua][ub]) & 1
    return 4 * s + _UNIT_MUL[ua][ub]


G_TAB = [[qmul(a, b) for b in range(8)] for a in range(8)]

MASK_MUL = [[0] * 256 for _ in range(256)]
for _a in range(256):
    for _b in range(256):
        _r = 0
        _bb = _b
        while _bb:
            _lb = _bb & -_bb
            _h = _lb.bit_length() - 1
            _aa = _a
            while _aa:
                _la = _aa & -_aa
                _g = _la.bit_length() - 1
                _r ^= 1 << G_TAB[_g][_h]
                _aa ^= _la
            _bb ^= _lb
        MASK_MUL[_a][_b] = _r


def mat_mul(A, B, r):
    C = [0] * (r * r)
    for i in range(r):
        for k in range(r):
            a = A[i * r + k]
            if a:
                m = MASK_MUL[a]
                for j in range(r):
                    C[i * r + j] ^= m[B[k * r + j]]
    return tuple(C)


def identity_state(r):
    return tuple(1 if i == j else 0 for i in range(r) for j in range(r))


def gen_state(g, N, r):
    lab = (1 << g) | 1
    cells = [0] * (r * r)
    for idx, bit in enumerate(N):
        if bit:
            cells[idx] ^= lab
    for i in range(r):
        cells[i * r + i] ^= 1
    return tuple(cells)


def diag_state(entries, r):
    cells = [0] * (r * r)
    for i, g in enumerate(entries):
        cells[i * r + i] = 1 << g
    return tuple(cells)


# ------------------------------------------------------- rank-one idempotents
def rank_one_idempotents(r):
    out = []
    for u in range(1, 1 << r):
        for v in range(1, 1 << r):
            if (u & v).bit_count() & 1:
                N = tuple(
                    ((u >> i) & 1) * ((v >> j) & 1)
                    for i in range(r)
                    for j in range(r)
                )
                out.append((u, v, N))
    out.sort()
    return out


# -------------------------------------------------------------------- BFS
def bfs_ball(gens, r, max_depth):
    I0 = identity_state(r)
    seen = {I0: 0}
    parents = {I0: None}
    layers = [[I0]]
    frontier = [I0]
    for _d in range(1, max_depth + 1):
        nxt = []
        for s in frontier:
            for gi, g in enumerate(gens):
                t = mat_mul(g, s, r)
                if t not in seen:
                    seen[t] = _d
                    parents[t] = (s, gi)
                    nxt.append(t)
        layers.append(nxt)
        frontier = nxt
        if not frontier:
            break
    return layers, parents


def state_digest(layers):
    h = hashlib.sha256()
    for layer in layers:
        for s in sorted(layer):
            h.update(bytes(s))
    return h.hexdigest()


def word_to(parents, target):
    """Application-order generator index list, or None if outside the ball."""
    if target not in parents:
        return None
    word = []
    s = target
    while parents[s] is not None:
        s, gi = parents[s]
        word.append(gi)
    return list(reversed(word))


def product_equals(gens, word, r, T):
    acc = identity_state(r)
    for gi in word:
        acc = mat_mul(gens[gi], acc, r)
    return acc == T


# ------------------------------------------------- engine B (independent replay)
def ham_mul(a, b):
    aw, ax, ay, az = a
    bw, bx, by, bz = b
    return (
        aw * bw - ax * bx - ay * by - az * bz,
        aw * bx + ax * bw + ay * bz - az * by,
        aw * by - ax * bz + ay * bw + az * bx,
        aw * bz + ax * by - ay * bx + az * bw,
    )


_HAM = [
    (1, 0, 0, 0),
    (0, 1, 0, 0),
    (0, 0, 1, 0),
    (0, 0, 0, 1),
    (-1, 0, 0, 0),
    (0, -1, 0, 0),
    (0, 0, -1, 0),
    (0, 0, 0, -1),
]
_HAM_TO_IDX = {t: i for i, t in enumerate(_HAM)}


def ham_index(a, b):
    return _HAM_TO_IDX[ham_mul(_HAM[a], _HAM[b])]


def b_mat_mul(A, B, r):
    C = [set() for _ in range(r * r)]
    for i in range(r):
        for k in range(r):
            if A[i * r + k]:
                for j in range(r):
                    if B[k * r + j]:
                        base = C[i * r + j]
                        for ga in A[i * r + k]:
                            for gb in B[k * r + j]:
                                gh = ham_index(ga, gb)
                                if gh in base:
                                    base.remove(gh)  # F2 addition: pairs cancel
                                else:
                                    base.add(gh)
    return tuple(frozenset(s) for s in C)


def b_state(g, N, r):
    lab = {g, 0}
    cells = [set() for _ in range(r * r)]
    for idx, bit in enumerate(N):
        if bit:
            cells[idx] ^= lab
    for i in range(r):
        cells[i * r + i] ^= {0}
    return tuple(frozenset(s) for s in cells)


def b_diag(entries, r):
    cells = [frozenset() for _ in range(r * r)]
    for i, g in enumerate(entries):
        cells[i * r + i] = frozenset({g})
    return tuple(cells)


def replay_word(gens_b, word, r):
    acc = identity_state(r)
    acc = tuple(frozenset({0}) if i == j else frozenset()
                for i in range(r) for j in range(r))
    for gi in word:
        acc = b_mat_mul(gens_b[gi], acc, r)
    return acc


# ------------------------------------------------------- GL_r(F2) normalisation
def det2(M, r):
    if r == 2:
        return M[0] * M[3] ^ M[1] * M[2]
    d = 0
    d ^= M[0] * (M[4] * M[8] ^ M[5] * M[7])
    d ^= M[1] * (M[3] * M[8] ^ M[5] * M[6])
    d ^= M[2] * (M[3] * M[7] ^ M[4] * M[6])
    return d


def gl_elements(r):
    out = []
    for bits in range(1 << (r * r)):
        M = tuple((bits >> t) & 1 for t in range(r * r))
        if det2(M, r):
            out.append(M)
    return out


def gl_invert(M, r):
    a = [list(M[i * r:(i + 1) * r]) for i in range(r)]
    inv = [[1 if i == j else 0 for j in range(r)] for i in range(r)]
    for col in range(r):
        piv = next(rw for rw in range(col, r) if a[rw][col])
        a[col], a[piv] = a[piv], a[col]
        inv[col], inv[piv] = inv[piv], inv[col]
        for rw in range(r):
            if rw != col and a[rw][col]:
                for k in range(r):
                    a[rw][k] ^= a[col][k]
                    inv[rw][k] ^= inv[col][k]
    return tuple(x for row in inv for x in row)


# ------------------------------------------------------------------- checks
def expect(name, cond, msg=""):
    if not cond:
        print("FAIL", name, msg)
        raise SystemExit(1)


ELEM = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7}


def group_laws():
    for a in range(8):
        for b in range(8):
            for c in range(8):
                expect("assoc", qmul(qmul(a, b), c) == qmul(a, qmul(b, c)))
    for a in range(8):
        for b in range(8):
            expect("ham-agree", ham_index(a, b) == qmul(a, b))
    x, y, z = 1, 2, 4  # i, j, -1
    expect("x2=z", qmul(x, x) == z)
    expect("y2=z", qmul(y, y) == z)
    expect("xyxy=z", qmul(qmul(qmul(x, y), x), y) == z)
    expect("z2=e", qmul(z, z) == 0)
    for a in range(8):
        expect("z-central", qmul(z, a) == qmul(a, z))
    xi, yi = 5, 6  # -i, -j
    expect("commutator", qmul(qmul(qmul(x, y), xi), yi) == z)
    expect("k2=z", qmul(3, 3) == z)


def main():
    group_laws()
    idem2 = rank_one_idempotents(2)
    idem3 = rank_one_idempotents(3)
    expect("idem2-count", len(idem2) == 6, str(len(idem2)))
    expect("idem3-count", len(idem3) == 28, str(len(idem3)))
    for u, v, N in idem2 + idem3:
        r = 2 if len(N) == 4 else 3
        expect("idempotent", mat_mul(N, N, r) == N)

    x, y, z = 1, 2, 4
    here = os.path.dirname(os.path.abspath(__file__))
    cert_path = os.path.join(here, "CERTIFICATE.json")

    results = {}
    for r, idem, depth in ((2, idem2, 3), (3, idem3, 3)):
        gen_triples = [[g, u, v] for g in (x, y) for (u, v, N) in idem]
        gens = [gen_state(g, N, r) for g in (x, y) for (u, v, N) in idem]
        expect("gen-count", len(gens) == (12 if r == 2 else 56))
        for (g_lbl, u, v) in gen_triples:
            N = next(N for (u2, v2, N) in idem if (u2, v2) == (u, v))
            expect(
                "D-square",
                mat_mul(gen_state(g_lbl, N, r), gen_state(g_lbl, N, r), r)
                == gen_state(qmul(g_lbl, g_lbl), N, r),
            )
        gls = gl_elements(r)
        gen_set = set(gens)
        for S in gls:
            Sinv = gl_invert(S, r)
            SD = mat_mul(S, gens[0], r)  # warm path only
            for g in gens:
                conj = mat_mul(mat_mul(S, g, r), Sinv, r)
                expect("gl-closure", conj in gen_set)
        layers, parents = bfs_ball(gens, r, depth)
        results[r] = dict(
            generators=gen_triples,
            layer_sizes=[len(L) for L in layers],
            ball_sha256=state_digest(layers),
            gl_order=len(gls),
            parents=parents,
            gens=gens,
            idem=idem,
        )

    T1 = diag_state([z, z], 2)
    T3 = diag_state([qmul(x, y), qmul(y, x)], 2)
    T2 = diag_state([z, z, 0], 3)
    C0 = identity_state(2)
    Cx = diag_state([x, 0], 2)
    Cz = diag_state([z, 0], 2)

    p2 = results[2]["parents"]
    p3 = results[3]["parents"]
    expect("control-I", word_to(p2, C0) == [])
    w_Cx = word_to(p2, Cx)
    w_Cz = word_to(p2, Cz)
    expect("control-x", w_Cx is not None and len(w_Cx) == 1, str(w_Cx))
    expect("control-z", w_Cz is not None and len(w_Cz) == 2, str(w_Cz))

    def direct_pair(entries, r):
        word = []
        gen_triples = results[r]["generators"]
        idx = {tuple(t): i for i, t in enumerate(gen_triples)}
        letters = {
            z: [x, x],
            x: [x],
            y: [y],
            qmul(x, y): [x, y],
            qmul(y, x): [y, x],
        }
        for pos, g in enumerate(entries):
            if g == 0:
                continue
            u = v = 1 << pos
            for let in letters[g]:
                word.append(idx[(let, u, v)])
        return list(reversed(word))

    direct = {
        "diag_z_z_r2": direct_pair([z, z], 2),
        "diag_xy_yx_r2": direct_pair([qmul(x, y), qmul(y, x)], 2),
        "diag_z_z_e_r3": direct_pair([z, z, 0], 3),
    }
    targets = {"diag_z_z_r2": (T1, 2), "diag_xy_yx_r2": (T3, 2), "diag_z_z_e_r3": (T2, 3)}

    endpoints = {}
    for name, (T, r) in targets.items():
        expect("direct-" + name,
               product_equals(results[r]["gens"], direct[name], r, T))
        w = word_to(results[r]["parents"], T)
        if w is None:
            minimum = len(direct[name])
            witness_word = direct[name]
            proven = "complete BFS to depth 3 excludes words of length <= 3"
        else:
            minimum = len(w)
            witness_word = w
            proven = "BFS distance is exact"
        endpoints[name] = dict(
            minimum=minimum,
            witness=witness_word,
            direct=direct[name],
            proven=proven,
            registers=r,
        )
        gens_b = [b_state(g, N, r) for g in (x, y) for (u, v, N) in results[r]["idem"]]
        Tb = b_diag([g for g in ([z, z] if name == "diag_z_z_r2" else
                                 ([qmul(x, y), qmul(y, x)] if name == "diag_xy_yx_r2"
                                  else [z, z, 0]))], r)
        expect("indep-witness", replay_word(gens_b, witness_word, r) == Tb, name)
        expect("indep-direct", replay_word(gens_b, direct[name], r) == Tb, name)
        for pos in range(len(witness_word)):
            sub = witness_word[:pos] + witness_word[pos + 1:]
            expect("omission", not product_equals(results[r]["gens"], sub, r, T),
                   f"{name} del {pos}")

    mut = list(T1)
    mut[0] ^= 1
    mut = tuple(mut)
    expect("mutated-not-target", mut != T1)
    expect("mutated-witness-fails",
           not product_equals(results[2]["gens"], endpoints["diag_z_z_r2"]["witness"], 2, mut))

    out = dict(
        status="PASS_Q8_CENTRAL_COMMUTATOR",
        group_order=8,
        endpoints=endpoints,
        r2_layers=results[2]["layer_sizes"],
        r3_layers=results[3]["layer_sizes"],
        r2_ball_sha256=results[2]["ball_sha256"],
        r3_ball_sha256=results[3]["ball_sha256"],
        r2_generators=results[2]["generators"],
        r3_generator_count=len(results[3]["generators"]),
        gl2_order=results[2]["gl_order"],
        gl3_order=results[3]["gl_order"],
        omission_controls=sum(len(v["witness"]) for v in endpoints.values()),
        controls=4,
        independent_engine_b=True,
        new_kappa=False,
    )

    if "--emit" in sys.argv:
        with open(cert_path, "w", encoding="utf-8") as fh:
            json.dump(out, fh, indent=2, sort_keys=True)
            fh.write("\n")
        print("EMITTED", cert_path)

    with open(cert_path, "r", encoding="utf-8") as fh:
        cert = json.load(fh)
    for key, val in out.items():
        expect("cert-" + key, cert.get(key) == val,
               f"{key}: cert={cert.get(key)!r} got={val!r}")

    print(
        "PASS_Q8_CENTRAL_COMMUTATOR",
        " ".join(f"{k}:{v['minimum']}" for k, v in endpoints.items()),
        f"r2_layers={results[2]['layer_sizes']}",
        f"r3_layers={results[3]['layer_sizes']}",
        "no_new_kappa",
    )


if __name__ == "__main__":
    main()
