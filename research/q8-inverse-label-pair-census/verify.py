#!/usr/bin/env python3
"""Exact paid-call minima for all ordered Q8 pair targets at r = 2, under
unit-priced inverse labels and under the positive-label baseline.

Formal F2[Q8] register model (eumemic PR 288 section 1.2, as fixed by
research/bit-dihedral-commutator and research/q8-central-commutator-pair):

  * r = 2 scalar registers, both arbitrary dirty inputs, endpoint restored
    exactly as a formal group-algebra identity in M_2(F2[Q8]);
  * one paid call is D_N(g) = I + ([g] + [1]) N with N = u v^T a binary
    rank-one idempotent (v^T u = 1 mod 2) and g a paid label;
  * inverse alphabet: labels x = i, x^-1 = -i, y = j, y^-1 = -j (24 factors);
    positive alphabet: labels x = i, y = j (12 factors);
  * free scalar GL_2(F2) basis changes are free and normalized by augmentation
    (closure rechecked below), so the generator search covers arbitrary
    interleaved free mixing;
  * acceptance is equality in every coefficient of the eight-element group
    algebra, never a finite-column test.

Two independently written engines (A: bitmask convolution from a
(sign, axis) quaternion table; B: frozenset convolution from explicit
Hamilton 4-tuple quaternion products) recompute the complete BFS layers and
every witness.  Stdlib only.  Prepared by Aaron Wang, with help from opencode.
"""

import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CERT_PATH = os.path.join(HERE, "CERTIFICATE.json")
PRED_CERT = os.path.normpath(
    os.path.join(HERE, os.pardir, "q8-central-commutator-pair", "CERTIFICATE.json")
)

# Basis indices: 0:+1 1:-1 2:+i 3:-i 4:+j 5:-j 6:+k 7:-k
ELEMENTS = ["+1", "-1", "+i", "-i", "+j", "-j", "+k", "-k"]
IDX = {name: i for i, name in enumerate(ELEMENTS)}


def elem_inv(g):
    # +-1 are self-inverse; +-i, +-j, +-k swap with their negatives.
    return (0, 1, 3, 2, 5, 4, 7, 6)[g]


# ---------------------------------------------------------------- engine A
# Group product from (sign, axis) quaternion-unit arithmetic.
_AXIS = {0: (1, 0), 1: (-1, 0), 2: (1, 1), 3: (-1, 1),
         4: (1, 2), 5: (-1, 2), 6: (1, 3), 7: (-1, 3)}
# UNIT[a][b] = (sign, axis) of quaternion unit product, axes 0=1 1=i 2=j 3=k.
_UNIT = [
    [(1, 0), (1, 1), (1, 2), (1, 3)],
    [(1, 1), (-1, 0), (1, 3), (-1, 2)],
    [(1, 2), (-1, 3), (-1, 0), (1, 1)],
    [(1, 3), (1, 2), (-1, 1), (-1, 0)],
]


def _pack_sign_axis(sgn, ax):
    return 2 * ax + (0 if sgn > 0 else 1)


GROUP_A = [[0] * 8 for _ in range(8)]
for _g in range(8):
    for _h in range(8):
        s1, a1 = _AXIS[_g]
        s2, a2 = _AXIS[_h]
        s, a = _UNIT[a1][a2]
        GROUP_A[_g][_h] = _pack_sign_axis(s1 * s2 * s, a)


def _ring_tables(group):
    mul = [[0] * 256 for _ in range(256)]
    for m1 in range(256):
        for m2 in range(256):
            acc = 0
            x = m1
            while x:
                b1 = x & -x
                i1 = b1.bit_length() - 1
                y = m2
                while y:
                    b2 = y & -y
                    i2 = b2.bit_length() - 1
                    acc ^= 1 << group[i1][i2]
                    y ^= b2
                x ^= b1
            mul[m1][m2] = acc
    return mul


MUL_A = _ring_tables(GROUP_A)


# ---------------------------------------------------------------- engine B
# Group product from explicit Hamilton 4-tuple integer quaternion products.
_H = {0: (1, 0, 0, 0), 1: (-1, 0, 0, 0), 2: (0, 1, 0, 0), 3: (0, -1, 0, 0),
      4: (0, 0, 1, 0), 5: (0, 0, -1, 0), 6: (0, 0, 0, 1), 7: (0, 0, 0, -1)}
_HIDX = {v: k for k, v in _H.items()}


def _ham(u, v):
    a0, a1, a2, a3 = u
    b0, b1, b2, b3 = v
    return (
        a0 * b0 - a1 * b1 - a2 * b2 - a3 * b3,
        a0 * b1 + a1 * b0 + a2 * b3 - a3 * b2,
        a0 * b2 - a1 * b3 + a2 * b0 + a3 * b1,
        a0 * b3 + a1 * b2 - a2 * b1 + a3 * b0,
    )


GROUP_B = [[_HIDX[_ham(_H[g], _H[h])] for h in range(8)] for g in range(8)]


def _ring_mul_b(m1, m2):
    acc = 0
    x = m1
    while x:
        b1 = x & -x
        i1 = b1.bit_length() - 1
        y = m2
        while y:
            b2 = y & -y
            i2 = b2.bit_length() - 1
            acc ^= 1 << GROUP_B[i1][i2]
            y ^= b2
        x ^= b1
    return acc


# ------------------------------------------------------------- matrices r=2
# State: tuple (m00, m01, m10, m11) of 8-bit ring masks.  Packed to 32 bits.

IDENT = (1, 0, 0, 1)


def pack(M):
    return M[0] | (M[1] << 8) | (M[2] << 16) | (M[3] << 24)


def unpack(p):
    return (p & 255, (p >> 8) & 255, (p >> 16) & 255, (p >> 24) & 255)


def mat_mul(P, Q, mul):
    a00, a01, a10, a11 = P
    b00, b01, b10, b11 = Q
    return (
        mul[a00][b00] ^ mul[a01][b10],
        mul[a00][b01] ^ mul[a01][b11],
        mul[a10][b00] ^ mul[a11][b10],
        mul[a10][b01] ^ mul[a11][b11],
    )


def apply_right(M, g, u, v, mul):
    """M <- M * (I + ([g]+1) u v^T); u, v are 2-bit nonzero binary masks."""
    m00, m01, m10, m11 = M
    mu0 = (m00 if u & 1 else 0) ^ (m01 if u & 2 else 0)
    mu1 = (m10 if u & 1 else 0) ^ (m11 if u & 2 else 0)
    a = (1 << g) | 1
    # Noncommutative ring: M*(I + aN) = M + ((M a) N); entries of M are
    # right-multiplied by a = [g]+1 (matrix-product order matters in F2[Q8]).
    t0 = mul[mu0][a]
    t1 = mul[mu1][a]
    return (
        m00 ^ (t0 if v & 1 else 0),
        m01 ^ (t0 if v & 2 else 0),
        m10 ^ (t1 if v & 1 else 0),
        m11 ^ (t1 if v & 2 else 0),
    )


def apply_right_b(M, g, u, v):
    m00, m01, m10, m11 = M
    mu0 = _xorb((m00 if u & 1 else 0), (m01 if u & 2 else 0))
    mu1 = _xorb((m10 if u & 1 else 0), (m11 if u & 2 else 0))
    a = (1 << g) | 1
    t0 = _ring_mul_b(mu0, a)
    t1 = _ring_mul_b(mu1, a)
    return (
        _xorb(m00, t0 if v & 1 else 0),
        _xorb(m01, t0 if v & 2 else 0),
        _xorb(m10, t1 if v & 1 else 0),
        _xorb(m11, t1 if v & 2 else 0),
    )


def _xorb(*masks):
    acc = 0
    for m in masks:
        acc ^= m
    return acc


def mat_mul_b(P, Q):
    a00, a01, a10, a11 = P
    b00, b01, b10, b11 = Q
    return (
        _xorb(_ring_mul_b(a00, b00), _ring_mul_b(a01, b10)),
        _xorb(_ring_mul_b(a00, b01), _ring_mul_b(a01, b11)),
        _xorb(_ring_mul_b(a10, b00), _ring_mul_b(a11, b10)),
        _xorb(_ring_mul_b(a10, b01), _ring_mul_b(a11, b11)),
    )


def replay(word, mul):
    M = IDENT
    for (g, u, v) in word:
        M = apply_right(M, g, u, v, mul)
    return M


def replay_b(word):
    M = IDENT
    for (g, u, v) in word:
        M = apply_right_b(M, g, u, v)
    return M


# ------------------------------------------------------------- idempotents
def idempotents():
    out = []
    for u in (1, 2, 3):
        for v in (1, 2, 3):
            if bin(u & v).count("1") % 2 == 1:
                out.append((u, v))
    return out


N_LIST = idempotents()  # 6 entries


def generators(labels):
    return [(g, u, v) for g in labels for (u, v) in N_LIST]


# ------------------------------------------------------------------- BFS
def bfs(gens, cap, apply_fn):
    dist = {pack(IDENT): 0}
    parent = {}
    frontier = [IDENT]
    layers = [1]
    for d in range(1, cap + 1):
        nxt = []
        for M in frontier:
            pm = pack(M)
            for gen in gens:
                M2 = apply_fn(M, *gen)
                p = pack(M2)
                if p not in dist:
                    dist[p] = d
                    parent[p] = (pm, gen)
                    nxt.append(M2)
        layers.append(len(nxt))
        frontier = nxt
        if not frontier:
            break
    return layers, dist, parent


def shortest_word(p, parent):
    word = []
    while p in parent:
        prev, gen = parent[p]
        word.append(gen)
        p = prev
    word.reverse()
    return word


def ball_digest(dist):
    h = hashlib.sha256()
    for p in sorted(dist):
        h.update(p.to_bytes(4, "little"))
        h.update(bytes([dist[p]]))
    return h.hexdigest()


# --------------------------------------------------------------- targets
def target(g1, g2):
    return (1 << g1, 0, 0, 1 << g2)


def geodesic(labels):
    """Shortest label word for each group element under the label set."""
    words = {0: []}
    frontier = [0]
    while frontier:
        nxt = []
        for h in frontier:
            for lab in labels:
                g = GROUP_A[h][lab]
                if g not in words:
                    words[g] = words[h] + [lab]
                    nxt.append(g)
        frontier = nxt
    return words


def direct_word(g1, g2, words):
    return ([(g, 1, 1) for g in words[g1]] + [(g, 2, 2) for g in words[g2]])


# ---------------------------------------------------------------- controls
def gl2():
    mats = []
    for a in (0, 1):
        for b in (0, 1):
            for c in (0, 1):
                for d in (0, 1):
                    if (a * d - b * c) % 2 == 1:
                        mats.append((a, b, c, d))
    return mats


def conj_n(S, u, v):
    """S N S^-1 over F2 for N = u v^T, returned as (u', v') bit masks."""
    a, b, c, d = S
    det = (a * d - b * c) % 2
    if det != 1:
        raise ValueError("not invertible")
    Sinv = (d, b, c, a)  # over F2, inverse of [[a,b],[c,d]] with det 1
    uv = (1 if u & 1 else 0, 1 if u & 2 else 0)
    vv = (1 if v & 1 else 0, 1 if v & 2 else 0)
    u1 = ((a * uv[0] + b * uv[1]) % 2, (c * uv[0] + d * uv[1]) % 2)
    # N' = S N S^-1 = (S u) (S^-T v)^T
    w1 = ((Sinv[0] * vv[0] + Sinv[2] * vv[1]) % 2,
          (Sinv[1] * vv[0] + Sinv[3] * vv[1]) % 2)
    up = (1 if u1[0] else 0) | (2 if u1[1] else 0)
    vp = (1 if w1[0] else 0) | (2 if w1[1] else 0)
    return up, vp


def main():
    write_mode = "--write" in sys.argv
    checks = []

    def ck(name, cond):
        checks.append((name, bool(cond)))
        if not cond:
            print("FAIL:", name)

    # 1. group tables agree; group laws
    ck("engine_tables_agree", GROUP_A == GROUP_B)
    assoc = all(
        GROUP_A[GROUP_A[g][h]][k] == GROUP_A[g][GROUP_A[h][k]]
        for g in range(8) for h in range(8) for k in range(8)
    )
    ck("associativity_512_triples", assoc)
    x, y, z = IDX["+i"], IDX["+j"], IDX["-1"]
    ck("x_squared_is_z", GROUP_A[x][x] == z)
    ck("y_squared_is_z", GROUP_A[y][y] == z)
    ck("xy_is_plus_k", GROUP_A[x][y] == IDX["+k"])
    ck("yx_is_minus_k", GROUP_A[y][x] == IDX["-k"])
    ck("z_central", all(GROUP_A[z][g] == GROUP_A[g][z] for g in range(8)))
    ck("z_squared_is_one", GROUP_A[z][z] == 0)
    xyxy = GROUP_A[GROUP_A[x][y]][GROUP_A[x][y]]
    ck("commutator_xyxy_is_z", xyxy == z)
    ck("inverses", all(GROUP_A[g][elem_inv(g)] == 0 and GROUP_A[elem_inv(g)][g] == 0
                       for g in range(8)))

    # 2. idempotents
    ck("six_rank_one_idempotents", len(N_LIST) == 6)
    ok = True
    for (u, v) in N_LIST:
        # N^2 = u (v^T u) v^T = N when v^T u = 1
        if bin(u & v).count("1") % 2 != 1:
            ok = False
    ck("idempotents_vTu_one", ok)
    total_pairs = sum(1 for u in (1, 2, 3) for v in (1, 2, 3))
    ck("idempotent_completeness_9_pairs", total_pairs == 9 and len(N_LIST) == 6)

    # 3. generator identities (both alphabets, engine B)
    inv_labels = [IDX["+i"], IDX["-i"], IDX["+j"], IDX["-j"]]
    pos_labels = [IDX["+i"], IDX["+j"]]
    gen_ok = True
    for labels in (inv_labels, pos_labels):
        for gen in generators(labels):
            g, u, v = gen
            D = apply_right_b(IDENT, g, u, v)
            Dg2 = apply_right_b(IDENT, GROUP_A[g][g], u, v)
            if mat_mul_b(D, D) != Dg2:
                gen_ok = False
            Dinv = apply_right_b(IDENT, elem_inv(g), u, v)
            if mat_mul_b(D, Dinv) != IDENT or mat_mul_b(Dinv, D) != IDENT:
                gen_ok = False
    ck("generator_square_and_inverse_identities", gen_ok)

    # 4. GL_2 conjugation closure of the idempotent list
    gl = gl2()
    ck("gl2_order_6", len(gl) == 6)
    nset = set(N_LIST)
    clo = all(conj_n(S, u, v) in nset for S in gl for (u, v) in N_LIST)
    ck("gl2_conjugation_closure", clo)

    # 5. complete BFS, both engines
    caps = {"inverse": 3, "positive": 5}
    alphabets = {"inverse": inv_labels, "positive": pos_labels}
    data = {}
    engines_agree = True
    for name, labels in alphabets.items():
        gens = generators(labels)
        layersA, distA, parentA = bfs(gens, caps[name], lambda M, g, u, v: apply_right(M, g, u, v, MUL_A))
        layersB, distB, _ = bfs(gens, caps[name], apply_right_b)
        if layersA != layersB or distA.keys() != distB.keys():
            engines_agree = False
        data[name] = {"labels": labels, "gens": gens,
                      "layers": layersA, "dist": distA, "parent": parentA,
                      "digest": ball_digest(distA),
                      "digest_b": ball_digest(distB),
                      "words": geodesic(labels)}
    ck("engines_agree_on_all_layers_and_balls", engines_agree)

    # 6. calibration with the merged predecessor (positive alphabet, r = 2)
    pred = json.load(open(PRED_CERT, encoding="utf-8"))
    ck("pred_layer_calibration_1_12_110_936",
       data["positive"]["layers"][:4] == [1, 12, 110, 936] == pred["r2_layers"])

    # 7. minima for all 64 ordered pairs, both alphabets
    records = {}
    replay_ok = True
    omission_total = 0
    omission_ok = True
    mutated_ok = True
    known_ok = True
    for g1 in range(8):
        for g2 in range(8):
            T = target(g1, g2)
            pk = pack(T)
            entry = {}
            for name in ("inverse", "positive"):
                D = data[name]
                bill = len(D["words"][g1]) + len(D["words"][g2])
                word = direct_word(g1, g2, D["words"])
                got = replay(word, MUL_A)
                if got != T or replay_b(word) != T:
                    replay_ok = False
                d = D["dist"].get(pk)
                if d is not None and d <= bill:
                    minimum = d
                    witness = shortest_word(pk, D["parent"])
                    proven = ("complete BFS to depth %d finds distance %d, at or "
                              "below the direct bill %d" % (caps[name], d, bill))
                else:
                    minimum = bill
                    witness = word
                    proven = ("complete BFS to depth %d excludes every word of "
                              "length <= %d; the direct word attains %d"
                              % (caps[name], caps[name], bill))
                entry[name] = {
                    "bill": bill,
                    "minimum": minimum,
                    "word": [[g, u, v] for (g, u, v) in witness],
                    "proven": proven,
                }
                # omission controls: delete each call of the attaining word
                for i in range(len(witness)):
                    if len(witness) < 2:
                        continue
                    cut = witness[:i] + witness[i + 1:]
                    omission_total += 1
                    if replay(cut, MUL_A) == T:
                        omission_ok = False
            # monotonicity: inverse minimum <= positive minimum
            if entry["inverse"]["minimum"] > entry["positive"]["minimum"]:
                known_ok = False
            records["diag_%s_%s" % (ELEMENTS[g1].replace("+", "p").replace("-", "m"),
                                    ELEMENTS[g2].replace("+", "p").replace("-", "m"))] = entry

    ck("all_attaining_words_replay", replay_ok)
    ck("omission_controls", omission_ok and omission_total > 0)
    ck("alphabet_monotonicity", known_ok)

    # mutated-target failure control: flip one coefficient of diag([+i],[+j])
    T = target(IDX["+i"], IDX["+j"])
    word = direct_word(IDX["+i"], IDX["+j"], data["positive"]["words"])
    bad = (T[0] ^ 1, T[1], T[2], T[3])
    if replay(word, MUL_A) == bad:
        mutated_ok = False
    ck("mutated_target_rejected", mutated_ok)

    # known-distance controls
    kd = data["inverse"]["dist"]
    kp = data["positive"]["dist"]
    ck("known_distance_identity_0", kd.get(pack(IDENT)) == 0 and kp.get(pack(IDENT)) == 0)
    ck("known_distance_diag_i_e_1",
       kd.get(pack(target(IDX["+i"], 0))) == 1 and kp.get(pack(target(IDX["+i"], 0))) == 1)
    ck("known_distance_diag_z_e_2",
       kd.get(pack(target(IDX["-1"], 0))) == 2 and kp.get(pack(target(IDX["-1"], 0))) == 2)

    # predecessor endpoint minima reproduced in the positive alphabet
    pz = records["diag_m1_m1"]["positive"]["minimum"]
    pxy = records["diag_pk_mk"]["positive"]["minimum"]
    ck("pred_endpoint_diag_z_z_is_4", pz == pred["endpoints"]["diag_z_z_r2"]["minimum"] == 4)
    ck("pred_endpoint_diag_xy_yx_is_4", pxy == pred["endpoints"]["diag_xy_yx_r2"]["minimum"] == 4)

    # summary counts
    comp_inv = sorted(k for k, e in records.items()
                      if e["inverse"]["minimum"] < e["inverse"]["bill"])
    comp_pos = sorted(k for k, e in records.items()
                      if e["positive"]["minimum"] < e["positive"]["bill"])

    cert = {
        "status": "PASS_Q8_INVERSE_LABEL_CENSUS",
        "new_kappa": False,
        "model": {
            "group": "Q8", "registers": 2,
            "paid_call": "I + ([g]+1) N, N = u v^T binary rank-one idempotent",
            "inverse_labels": [ELEMENTS[g] for g in inv_labels],
            "positive_labels": [ELEMENTS[g] for g in pos_labels],
            "free_mixing": "GL_2(F2), normalized by augmentation",
            "acceptance": "coefficientwise equality in F2[Q8]",
        },
        "group_table": [ELEMENTS[g] for g in range(8)],
        "group_table_sha256": hashlib.sha256(
            bytes(GROUP_A[g][h] for g in range(8) for h in range(8))).hexdigest(),
        "idempotents_uv": [[u, v] for (u, v) in N_LIST],
        "gl2_order": 6,
        "inverse_generators": 24,
        "positive_generators": 12,
        "inverse_layers": data["inverse"]["layers"],
        "inverse_ball_sha256": data["inverse"]["digest"],
        "inverse_ball_sha256_engine_b": data["inverse"]["digest_b"],
        "positive_layers": data["positive"]["layers"],
        "positive_ball_sha256": data["positive"]["digest"],
        "positive_ball_sha256_engine_b": data["positive"]["digest_b"],
        "independent_engine_b": True,
        "predecessor_calibration": {
            "source": "research/q8-central-commutator-pair/CERTIFICATE.json",
            "r2_layers": pred["r2_layers"],
            "diag_z_z_r2_minimum": pred["endpoints"]["diag_z_z_r2"]["minimum"],
            "diag_xy_yx_r2_minimum": pred["endpoints"]["diag_xy_yx_r2"]["minimum"],
        },
        "endpoints": records,
        "compressed_pairs_inverse": comp_inv,
        "compressed_pairs_positive": comp_pos,
        "omission_controls": omission_total,
        "controls": sum(1 for _, ok in checks if ok),
        "checks_failed": [n for n, ok in checks if not ok],
    }

    if write_mode:
        with open(CERT_PATH, "w", encoding="utf-8") as f:
            json.dump(cert, f, indent=1, sort_keys=True)
        print("WROTE", CERT_PATH)
    else:
        stored = json.load(open(CERT_PATH, encoding="utf-8"))
        if stored != cert:
            diffs = [k for k in set(stored) | set(cert) if stored.get(k) != cert.get(k)]
            print("FAIL: certificate mismatch in", diffs)
            checks.append(("certificate_equality", False))
        else:
            checks.append(("certificate_equality", True))

    failed = [n for n, ok in checks if not ok]
    if failed:
        print("FAILED_CHECKS", failed)
        raise SystemExit(1)
    print(
        "PASS_Q8_INVERSE_LABEL_CENSUS",
        "pairs=64",
        "inv_layers=%s" % (data["inverse"]["layers"],),
        "pos_layers=%s" % (data["positive"]["layers"],),
        "compressed_inv=%d" % len(comp_inv),
        "compressed_pos=%d" % len(comp_pos),
        "omission_controls=%d" % omission_total,
        "no_new_kappa",
    )


if __name__ == "__main__":
    main()
