#!/usr/bin/env python3
"""Exact reachability through three paid calls in small Q8 register models."""
import hashlib
import json
from itertools import product
from pathlib import Path

ONE = (1, 0, 0, 0)
MINUS_ONE = (-1, 0, 0, 0)
I = (0, 1, 0, 0)
MINUS_I = (0, -1, 0, 0)
J = (0, 0, 1, 0)
MINUS_J = (0, 0, -1, 0)
K = (0, 0, 0, 1)
MINUS_K = (0, 0, 0, -1)
GROUP = (ONE, MINUS_ONE, I, MINUS_I, J, MINUS_J, K, MINUS_K)
GID = {g: n for n, g in enumerate(GROUP)}


def qmul(x, y):
    a, b, c, d = x
    e, f, g, h = y
    return (a*e-b*f-c*g-d*h,
            a*f+b*e+c*h-d*g,
            a*g-b*h+c*e+d*f,
            a*h+b*g-c*f+d*e)


GMUL = tuple(tuple(GID[qmul(x, y)] for y in GROUP) for x in GROUP)


def right_delta_table(g):
    """Map x to x*([g]+[1]) in the exact F2 group algebra."""
    out = []
    for x in range(256):
        translated = 0
        for q in range(8):
            if x >> q & 1:
                translated ^= 1 << GMUL[q][g]
        out.append(x ^ translated)
    return tuple(out)


DELTA = {"i": right_delta_table(GID[I]), "j": right_delta_table(GID[J])}


def ga_mul(x, y):
    """Slow reference convolution in F2[Q8], used to check the fast update."""
    out = 0
    for a in range(8):
        if x >> a & 1:
            for b in range(8):
                if y >> b & 1:
                    out ^= 1 << GMUL[a][b]
    return out


def matrix_mul(A, B, r):
    out = bytearray(r*r)
    for i in range(r):
        for j in range(r):
            value = 0
            for k in range(r):
                value ^= ga_mul(A[i*r+k], B[k*r+j])
            out[i*r+j] = value
    return bytes(out)


def factor_matrix(factor, r):
    label, u, v = factor
    g = GID[I] if label == "i" else GID[J]
    address_delta = (1 << g) ^ 1
    return bytes((1 if i == j else 0) ^
                 (address_delta if u[i] and v[j] else 0)
                 for i in range(r) for j in range(r))


def idempotent_data(r):
    """All rank-one N=uv^T with v^T u=1; each has a unique F2 factorization."""
    vectors = tuple(v for v in product((0, 1), repeat=r) if any(v))
    data = []
    for u in vectors:
        for v in vectors:
            if sum(a*b for a, b in zip(u, v)) % 2:
                N = tuple(u[i]*v[j] for i in range(r) for j in range(r))
                data.append((N, u, v))
    assert len({N for N, _u, _v in data}) == len(data)
    assert len(data) == (2**r - 1) * 2**(r-1)
    return tuple(data)


def apply_factor(M, factor, r):
    """Right multiply M by D_N(g)=I+([g]+[1])uv^T."""
    label, u, v = factor
    delta = DELTA[label]
    out = bytearray(M)
    for row in range(r):
        row_delta = 0
        base = row*r
        for k in range(r):
            if u[k]:
                row_delta ^= delta[M[base+k]]
        if row_delta:
            for col in range(r):
                if v[col]:
                    out[base+col] ^= row_delta
    return bytes(out)


def identity(r):
    return bytes(1 if i == j else 0 for i in range(r) for j in range(r))


def target_matrix(targets):
    r = len(targets)
    return bytes((1 << GID[g]) if i == j else 0
                 for i, g in enumerate(targets)
                 for j in range(r))


def candidate_targets():
    """36 ordered triples with positive {i,j} word-length invoice 4."""
    out = set()
    for slot in range(3):
        for length_two in (MINUS_ONE, K, MINUS_K):
            remaining = [p for p in range(3) if p != slot]
            for x, y in product((I, J), repeat=2):
                target = [None, None, None]
                target[slot] = length_two
                target[remaining[0]], target[remaining[1]] = x, y
                out.add(tuple(target))
    assert len(out) == 36
    return tuple(sorted(out, key=lambda t: tuple(GID[x] for x in t)))


def direct_word(targets, r):
    """Positive alphabet direct word, using one coordinate projector per role."""
    word = []
    for slot, g in enumerate(targets):
        u = tuple(int(i == slot) for i in range(r))
        v = u
        if g == I:
            word.append(("i", u, v))
        elif g == J:
            word.append(("j", u, v))
        elif g == MINUS_ONE:
            word.extend((("i", u, v), ("i", u, v)))
        elif g == K:
            word.extend((("i", u, v), ("j", u, v)))
        elif g == MINUS_K:
            word.extend((("j", u, v), ("i", u, v)))
        elif g == ONE:
            continue
        else:
            raise ValueError("target is outside the declared positive alphabet-length domain")
    return word


def run_search(r, triples):
    targets = tuple(tuple(t) + (ONE,) * (r - 3) for t in triples)
    target_map = {target_matrix(t): t for t in targets}
    assert len(target_map) == len(triples)
    factors = tuple((label, u, v)
                    for label in ("i", "j")
                    for _N, u, v in idempotent_data(r))
    assert len(factors) == 2 * (2**r - 1) * 2**(r-1)

    # Check the optimized rank-one update against full coefficient convolution
    # for every paid factor on several arbitrary formal matrix states.
    samples = [identity(r)]
    for seed in range(1, 5):
        samples.append(bytes((seed*37 + cell*53 + r) & 255
                             for cell in range(r*r)))
    for M in samples:
        for factor in factors:
            assert apply_factor(M, factor, r) == matrix_mul(M, factor_matrix(factor, r), r)

    # Every endpoint has its explicit 4-call direct control.
    for t in targets:
        assert len(direct_word(t, r)) == 4
        M = identity(r)
        for factor in direct_word(t, r):
            M = matrix_mul(M, factor_matrix(factor, r), r)
        assert M == target_matrix(t)

    # All exact-depth states at depths one and two. State merging is sound:
    # every suffix acts deterministically on a group-algebra matrix.
    states = {identity(r): ()}
    level_counts = []
    found = {}
    for depth in (1, 2):
        nxt = {}
        for M, prefix in states.items():
            for index, factor in enumerate(factors):
                P = apply_factor(M, factor, r)
                if P not in nxt:
                    nxt[P] = prefix + (index,)
        level_counts.append(len(nxt))
        for P, word in nxt.items():
            if P in target_map:
                found.setdefault(target_map[P], (depth, word))
        states = nxt
        print(f"r={r} depth={depth} states={len(nxt)} target_hits={len(found)}")

    # Positive engine control at depth two.
    easy = (I, J, ONE) + (ONE,) * (r - 3)
    easy_target = target_matrix(easy)
    assert easy_target in states
    M = identity(r)
    for factor in direct_word(easy, r):
        M = matrix_mul(M, factor_matrix(factor, r), r)
    assert M == easy_target

    # Stream every extension of every distinct depth-two state. This is
    # complete for all depth-three words but does not retain a huge third layer.
    transitions = 0
    depth_three_hits = {}
    for M, prefix in states.items():
        for index, factor in enumerate(factors):
            P = apply_factor(M, factor, r)
            transitions += 1
            if P in target_map:
                depth_three_hits.setdefault(target_map[P], prefix + (index,))
    found.update({t: (3, w) for t, w in depth_three_hits.items() if t not in found})
    print(f"r={r} depth=3 transitions={transitions} target_hits={len(depth_three_hits)}")

    # Dropping a call from the illustrative direct path changes its endpoint.
    example = (I, J, K) + (ONE,) * (r - 3)
    example_target = target_matrix(example)
    direct = direct_word(example, r)
    partial = identity(r)
    for factor in direct[:-1]:
        partial = apply_factor(partial, factor, r)
    assert partial != example_target
    wrong = target_matrix((I, J, MINUS_K) + (ONE,) * (r - 3))
    assert wrong != example_target
    assert wrong in target_map
    assert wrong not in {target_matrix(t) for t in found}

    return level_counts, transitions, found


def main():
    assert len(GROUP) == 8 and len(GID) == 8
    assert len({qmul(x, y) for x in GROUP for y in GROUP}) == 8
    assert all(qmul(qmul(x, y), z) == qmul(x, qmul(y, z))
               for x in GROUP for y in GROUP for z in GROUP)
    assert qmul(I, I) == MINUS_ONE and qmul(J, J) == MINUS_ONE
    assert qmul(I, J) == K and qmul(J, I) == MINUS_K
    assert qmul(K, K) == MINUS_ONE

    triples = candidate_targets()
    expected = json.loads(Path(__file__).with_name("EXPECTED.json").read_text())
    names = {ONE: "1", MINUS_ONE: "-1", I: "i", MINUS_I: "-i",
             J: "j", MINUS_J: "-j", K: "k", MINUS_K: "-k"}
    named_triples = [[names[g] for g in t] for t in triples]
    encoded = json.dumps(named_triples, separators=(",", ":")).encode()
    assert len(named_triples) == expected["target_count"] == 36
    assert named_triples == expected["target_triples"]
    assert hashlib.sha256(encoded).hexdigest() == expected["target_triples_sha256"]
    abelianization = {ONE: (0, 0), MINUS_ONE: (0, 0),
                      I: (1, 0), MINUS_I: (1, 0),
                      J: (0, 1), MINUS_J: (0, 1),
                      K: (1, 1), MINUS_K: (1, 1)}
    noncentral = [t for t in triples if K in t or MINUS_K in t]
    central = [t for t in triples if MINUS_ONE in t]
    assert len(noncentral) == expected["structural_split"]["k_or_minus_k"] == 24
    assert len(central) == expected["structural_split"]["minus_one"] == 12
    rank_profile = {}
    for t in noncentral:
        rank_x = sum(abelianization[g][0] for g in t)
        rank_y = sum(abelianization[g][1] for g in t)
        assert rank_x == 1 + sum(g == I for g in t)
        assert rank_y == 1 + sum(g == J for g in t)
        assert rank_x + rank_y == 4
        key = f"{rank_x},{rank_y}"
        rank_profile[key] = rank_profile.get(key, 0) + 1
    assert rank_profile == expected["structural_split"]["rank_profiles"]
    three_results = run_search(3, triples)
    four_results = run_search(4, triples)
    assert not three_results[2]
    assert not four_results[2]
    assert three_results[0] == [56, 2324]
    assert three_results[1] == 2324 * 56
    assert four_results[0] == [240, 41800]
    assert four_results[1] == 10_032_000
    for key, actual in (("r3", three_results), ("r4", four_results)):
        assert actual[0] == [expected[key]["depth1_states"], expected[key]["depth2_states"]]
        assert actual[1] == expected[key]["depth3_transitions"]
        assert expected[key]["target_hits"] == 0
    print("PASS_Q8_MIXED_TUPLES targets=36 factors_r3=56 factors_r4=240 "
          f"states_r3={three_results[0]} transitions_r3={three_results[1]} "
          f"states2_r4={four_results[0]} transitions_r4={four_results[1]} "
          "min_calls_r3_r4=4 full_convolution_crosscheck=PASS positive_control=2 "
          "dropped_call=REJECTED wrong_target=REJECTED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
