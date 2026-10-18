"""The 104-line unit P104 = E8 minus two orthogonal frames F0, F1 and the #968-style frame-pair decoder (rebuilt from scratch with exact
Fractions and the dense pairing B): 8 terms (alpha_k, beta_k) with alpha_k . beta_l = 0 (k != l) and odd for k = l; every alpha_k and beta_k is a
dead (punctured) root, all of them in F0 u F1; A^T B = 2 I, hence P Q^T = 2 Gram on the 104 live lines.  Deterministic: first admissible F1."""
import itertools
from fractions import Fraction as Fr
from units import E8, gram, bmasks, block_rank, dot, true


def coord_frame():
    idx = {r: i for i, r in enumerate(E8)}

    def find(v):
        if v in idx:
            return idx[v]
        return idx[tuple(-x for x in v)]
    F0 = []
    for a in range(4):
        for s in (1, -1):
            v = [0] * 8
            v[2 * a] = 2
            v[2 * a + 1] = 2 * s
            F0.append(find(tuple(v)))
    return F0


def frames_in_pool(G, pool, size=8):
    out = []

    def rec(cur, cand):
        if len(cur) == size:
            out.append(tuple(cur))
            return
        for j in cand:
            rec(cur + [j], [k for k in cand if k > j and G[j][k] == 0])
    rec([], pool)
    return out


def pair_solutions(G, F0, F1):
    """All ways to pair the 16 lines of F0 u F1 into 8 (alpha, beta) with alpha_k.beta_l = 0 off the diagonal, alpha_k.beta_k odd,
    alpha_k in F0 for k in S and in F1 otherwise, beta the partner in the other frame (the structure found in #968)."""
    out = []
    for sm in range(256):
        S = [F0[j] for j in range(8) if sm >> j & 1]
        need = 8 - len(S)
        part = {f: [g for g in F1 if [x for x in S if G[g][x]] == [f]] for f in S}
        if any(not v for v in part.values()):
            continue
        for ch in itertools.product(*[part[f] for f in S]):
            if len(set(ch)) != len(S):
                continue
            Ts = [g for g in F1 if g not in ch]
            if len(Ts) != need:
                continue
            rest = [f for f in F0 if f not in S]
            p2 = {g: [f for f in rest if [x for x in Ts if G[f][x]] == [g]] for g in Ts}
            if any(not v for v in p2.values()):
                continue
            for ch2 in itertools.product(*[p2[g] for g in Ts]):
                if len(set(ch2)) != len(Ts):
                    continue
                out.append(list(zip(S, ch)) + list(zip(Ts, ch2)))
    return out


def build():
    G = gram(E8)
    F0 = coord_frame()
    assert all(G[a][b] == 0 for a in F0 for b in F0 if a != b)
    pool = [i for i in range(120) if i not in F0]
    frames = frames_in_pool(G, pool)
    for F1 in frames:
        sols = pair_solutions(G, F0, F1)
        if sols:
            return G, F0, frames, F1, sols
    raise RuntimeError('no admissible F1')


def cost_of_pairs(G, pairs, dead):
    live = [t for t in range(120) if t not in dead]
    Br = bmasks(G)
    P = [[Fr(dot(true(E8[t]), true(E8[a]))) for a, b in pairs] for t in live]
    Q = [[Fr(dot(true(E8[t]), [2 * G[a][b] * x for x in true(E8[b])]), 2) for a, b in pairs] for t in live]
    ok = all(sum(P[i][k] * Q[j][k] for k in range(8)) == G[live[i]][live[j]] for i in range(len(live)) for j in range(len(live)))
    ranks = []
    for k in range(8):
        R = [t for t in live if P[live.index(t)][k] != 0]
        A = [t for t in live if Q[live.index(t)][k] != 0]
        ranks.append(block_rank(Br, R, A))
    return ok, ranks, live
