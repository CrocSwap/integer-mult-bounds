#!/usr/bin/env python3
"""Independent checks for the UT3(F2) = D8 central-commutator index.

Standard library only. The group is built as the eight 3x3 unitriangular
binary matrices, not from a hand-written group law, and group-algebra
elements are bitmasks over that enumeration. Nothing is imported from the
audited packages (PR1478, PR1573, PR1742).
"""
from __future__ import annotations

import itertools
import sys

# ---------------------------------------------------------------- group UT3(F2)

def mat_mul3(p, q):
    return tuple(
        tuple(sum(p[i][t] & q[t][j] for t in range(3)) & 1 for j in range(3))
        for i in range(3)
    )


def unitri(e01, e12, e02):
    return ((1, e01, e02), (0, 1, e12), (0, 0, 1))


ELEMENTS = [unitri(*bits) for bits in itertools.product((0, 1), repeat=3)]
INDEX = {m: i for i, m in enumerate(ELEMENTS)}
ONE = INDEX[unitri(0, 0, 0)]
A = INDEX[unitri(1, 0, 0)]  # I + E01
B = INDEX[unitri(0, 1, 0)]  # I + E12
MUL = [[INDEX[mat_mul3(p, q)] for q in ELEMENTS] for p in ELEMENTS]
C = MUL[MUL[MUL[A][B]][A]][B]  # abab


def sigma(i):
    """The PR1573 map (x, y, z) -> (y, x, z + x y) in matrix coordinates."""
    m = ELEMENTS[i]
    x, y, z = m[0][1], m[1][2], m[0][2]
    return INDEX[unitri(y, x, z ^ (x & y))]


# --------------------------------------------------------- group algebra F2[G]

def alg_mul(f, g):
    out = 0
    for i in range(8):
        if f >> i & 1:
            for j in range(8):
                if g >> j & 1:
                    out ^= 1 << MUL[i][j]
    return out


ALG = [[alg_mul(f, g) for g in range(256)] for f in range(256)]
UNIT = 1 << ONE


def gate_delta(g):
    """Coefficient ([g] + 1)."""
    return (1 << g) ^ UNIT


# ------------------------------------------------- r x r matrices over F2[G]

def idempotents(r):
    """All binary rank-one idempotents u v^T (v^T u = 1), as (u, v) bitmasks."""
    out = []
    for u in range(1, 1 << r):
        for v in range(1, 1 << r):
            if bin(u & v).count("1") & 1:
                out.append((u, v))
    return out


def identity(r, diag=None):
    diag = diag or [UNIT] * r
    return tuple(diag[i] if i == j else 0 for i in range(r) for j in range(r))


def apply_gate(state, r, g, u, v):
    """Return D * state with D = I + ([g]+1) u v^T (left multiplication)."""
    d = gate_delta(g)
    out = list(state)
    for col in range(r):
        acc = 0
        for row in range(r):
            if v >> row & 1:
                acc ^= state[row * r + col]
        if acc:
            add = ALG[d][acc]
            for row in range(r):
                if u >> row & 1:
                    out[row * r + col] ^= add
    return tuple(out)


def step_bytes(state, r, g, u, v):
    """Fast form of apply_gate on a bytes-encoded state (same arithmetic)."""
    row_add = ALG[gate_delta(g)]
    out = bytearray(state)
    for col in range(r):
        acc = 0
        for row in range(r):
            if v >> row & 1:
                acc ^= state[row * r + col]
        if acc:
            add = row_add[acc]
            for row in range(r):
                if u >> row & 1:
                    out[row * r + col] ^= add
    return bytes(out)


def ball_layers(start, r, gens, depth):
    """Exact left-multiplication ball of the given radius (bytes states)."""
    start = bytes(start)
    seen = {start}
    frontier = [start]
    layers = [1]
    for _ in range(depth):
        nxt = []
        for s in frontier:
            for (g, u, v) in gens:
                t = step_bytes(s, r, g, u, v)
                if t not in seen:
                    seen.add(t)
                    nxt.append(t)
        frontier = nxt
        layers.append(len(nxt))
    return seen, layers


# --------------------------------------- binary matrices for the proof's blocks

def outer(u, v, r):
    return tuple(tuple((u >> i & 1) & (v >> j & 1) for j in range(r)) for i in range(r))


def bmat_add(p, q):
    return tuple(tuple(a ^ b for a, b in zip(rp, rq)) for rp, rq in zip(p, q))


def bmat_mul(p, q):
    n = len(p)
    return tuple(
        tuple(sum(p[i][t] & q[t][j] for t in range(n)) & 1 for j in range(n))
        for i in range(n)
    )


def zero(r):
    return tuple(tuple(0 for _ in range(r)) for _ in range(r))


def rep_matrix(elem_mask, rho):
    """Image of a group-algebra element under a 3x3 representation rho."""
    acc = ((0, 0, 0), (0, 0, 0), (0, 0, 0))
    for i in range(8):
        if elem_mask >> i & 1:
            acc = bmat_add(acc, rho(i))
    return acc


def natural(i):
    return ELEMENTS[i]


def natural_sigma(i):
    return ELEMENTS[sigma(i)]


def blocks(state, r, rho):
    """3x3 grid of r x r binary blocks of the 3r x 3r image of state."""
    images = [rep_matrix(state[k], rho) for k in range(r * r)]
    return tuple(
        tuple(
            tuple(tuple(images[i * r + j][p][q] for j in range(r)) for i in range(r))
            for q in range(3)
        )
        for p in range(3)
    )


def predicted_blocks(word, r, first, second):
    """Proof prediction: identity diagonal, sums of N on 01/12, ordered pair sum on 02."""
    s01, s12, s02 = zero(r), zero(r), zero(r)
    for idx, (g, u, v) in enumerate(word):
        n = outer(u, v, r)
        if g == first:
            s01 = bmat_add(s01, n)
        else:
            s12 = bmat_add(s12, n)
            # Calls act by left multiplication, so the matrix product is
            # D_last ... D_first and a later call sits to the LEFT. Block 02
            # collects (later `first` call) x (earlier `second` call), i.e.
            # PR1573's sum over i<j with g_i=first, g_j=second in its
            # left-to-right matrix order.
            for (g2, u2, v2) in word[idx + 1:]:
                if g2 == first:
                    s02 = bmat_add(s02, bmat_mul(outer(u2, v2, r), n))
    eye = tuple(tuple(int(i == j) for j in range(r)) for i in range(r))
    z = zero(r)
    return ((eye, s01, s02), (z, eye, s12), (z, z, eye))


def run_word(word, r):
    state = identity(r)
    for (g, u, v) in word:
        state = apply_gate(state, r, g, u, v)
    return state


def main():
    out = {}
    # 1. group facts
    assert len(set(ELEMENTS)) == 8
    assert MUL[A][A] == ONE and MUL[B][B] == ONE and MUL[C][C] == ONE
    assert C == INDEX[unitri(0, 0, 1)]
    assert all(MUL[C][g] == MUL[g][C] for g in range(8)), "c central"
    assert MUL[A][B] != MUL[B][A]
    for g in range(8):
        for h in range(8):
            assert sigma(MUL[g][h]) == MUL[sigma(g)][sigma(h)], "sigma hom"
        assert sigma(sigma(g)) == g
    assert sigma(A) == B and sigma(B) == A and sigma(C) == C
    # control: the plain coordinate swap without the xy correction is NOT a hom
    def swap_plain(i):
        m = ELEMENTS[i]
        return INDEX[unitri(m[1][2], m[0][1], m[0][2])]
    assert any(swap_plain(MUL[g][h]) != MUL[swap_plain(g)][swap_plain(h)]
               for g in range(8) for h in range(8))
    out["group"] = "UT3 order 8, sigma automorphism, plain swap rejected"

    # 2. the proof's block identities, exhaustively on short words
    checked = 0
    for r, maxlen in ((2, 4), (3, 3)):
        gens = [(g, u, v) for g in (A, B) for (u, v) in idempotents(r)]
        for length in range(1, maxlen + 1):
            for word in itertools.product(gens, repeat=length):
                state = run_word(word, r)
                # natural rep: a -> block 01, b -> block 12, E02 gets (b after a)
                assert blocks(state, r, natural) == predicted_blocks(word, r, A, B)
                # sigma companion: b -> block 01, a -> block 12
                assert blocks(state, r, natural_sigma) == predicted_blocks(word, r, B, A)
                checked += 1
    out["block_identity_words"] = checked

    # 3. a rank-s factor is s same-label rank-one factors: ([g]+1)^2 = 0
    r = 3
    rank_one = [(u, v) for u in range(1, 8) for v in range(1, 8)]
    pairs = 0
    for g in (A, B):
        assert ALG[gate_delta(g)][gate_delta(g)] == 0
        for (u1, v1), (u2, v2) in itertools.product(rank_one, repeat=2):
            two = apply_gate(apply_gate(identity(r), r, g, u2, v2), r, g, u1, v1)
            summed = tuple(
                UNIT * (i == j)
                ^ ALG[gate_delta(g)][((u1 >> i & v1 >> j) ^ (u2 >> i & v2 >> j)) & 1]
                for i in range(r) for j in range(r)
            )
            assert two == summed
            pairs += 1
    out["rank_sum_pairs"] = pairs

    # 4. censuses: radius-3 balls from identity and from the k=2 target
    radii = (2, 3, 4) if "--r4" in sys.argv else (2, 3)
    for r in radii:
        gens = [(g, u, v) for g in (A, B) for (u, v) in idempotents(r)]
        ident = identity(r)
        target = identity(r, [1 << C, 1 << C] + [UNIT] * (r - 2))
        single = identity(r, [1 << C] + [UNIT] * (r - 1))
        ib, ilayers = ball_layers(ident, r, gens, 3)
        tb, tlayers = ball_layers(target, r, gens, 3)
        out[f"r{r}_gates"] = len(gens)
        out[f"r{r}_identity_layers"] = ilayers
        out[f"r{r}_identity_states"] = len(ib)
        out[f"r{r}_target_layers"] = tlayers
        out[f"r{r}_meet_k2"] = len(ib & tb)
        # control: the one-target endpoint (distance 4) must be detected
        sb, _ = ball_layers(single, r, gens, 3)
        out[f"r{r}_meet_k1_control"] = len(ib & sb)
        assert out[f"r{r}_meet_k1_control"] > 0
        assert bytes(target) not in ib and bytes(single) not in ib
        del ib, tb, sb
        # direct witness a b a b on each data role has length 8
        word = []
        for role in range(2):
            e = 1 << role
            word += [(A, e, e), (B, e, e), (A, e, e), (B, e, e)]
        assert run_word(word, r) == target, "direct word"
        for drop in range(8):
            assert run_word(word[:drop] + word[drop + 1:], r) != target
    return out


def wrong_order_detected():
    """Control: predicting block 02 with the factor order reversed must fail."""
    r = 2
    gens = [(g, u, v) for g in (A, B) for (u, v) in idempotents(r)]
    for word in itertools.product(gens, repeat=2):
        reversed_prediction = predicted_blocks(word[::-1], r, A, B)
        if blocks(run_word(word, r), r, natural) != reversed_prediction:
            return True
    return False


EXPECTED = {
    "r2_identity_states": 565,  # PR1478 r=2 state count
    "r3_identity_layers": [1, 56, 1750, 45424],  # PR1742 layer counts
    "r3_identity_states": 47231,  # PR1478 r=3 state count
    "r2_meet_k2": 0,
    "r3_meet_k2": 0,
}
EXPECTED_R4 = {
    "r4_identity_layers": [1, 240, 32650, 3644000],
    "r4_meet_k2": 0,
}


def check_source():
    """The indexed open question must still be present in the frozen package."""
    from pathlib import Path
    root = Path(__file__).resolve().parents[2]
    text = (root / "research/bit-dihedral-commutator/README.md").read_text()
    return "Does a restored third dirty register help for the same D8 central target?" in text


if __name__ == "__main__":
    res = main()
    res["wrong_order_control_rejected"] = wrong_order_detected()
    res["source_question_present"] = check_source()
    for k, v in res.items():
        print(f"{k}: {v}")
    want = dict(EXPECTED)
    if "--r4" in sys.argv:
        want.update(EXPECTED_R4)
    ok = all(res.get(k) == v for k, v in want.items())
    ok = ok and res["wrong_order_control_rejected"] and res["source_question_present"]
    print("PASS_UT3_CENTRAL_COMMUTATOR_INDEX" if ok else "FAIL_UT3_CENTRAL_COMMUTATOR_INDEX")
    sys.exit(0 if ok else 1)
