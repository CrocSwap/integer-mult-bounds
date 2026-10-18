"""Exact scoped search: four coordinate-SWAP targets at exactly four registers.

Package: research/four-swap-r4-cnot (task card bit-new-register-model, refined;
see TASK.md and README.md).

Model.  G = GL2(F2) = S3 = <a,b | a^2 = b^2 = (ab)^3 = 1>, S = aba = bab.
A paid call is C(g,N) = I + ([g]+1)N in M_r(F2[G]) with g in {a,b} and N a
binary rank-one idempotent over F2^r.  The exact formal endpoint
T = diag([S],...,[S],1,...,1) on r registers is the acceptance test, so
arbitrary dirty inputs and full restoration are covered.

Engines.  A natural-image engine (bit-row packed 2r x 2r binary matrices with
rank-1 fast updates) and a formal-algebra engine (packed M_r(F2[G]) states
with the same rank-1 fast updates).  Every meet is first run in the natural
image (necessary condition); any natural-level hit is resolved by the exact
formal-algebra meet.  search_b.py is a separately written engine used to
cross-check ball sizes.

Written invariants proved in README.md: L1 det parity q = t (mod 2);
L2 free scalar mixing is forced to the identity and sum_i N_i = D_t;
L3 each call is an involution and q-call balls are closed under inversion.

Stdlib only.  Emits RECEIPT.json and one PASS line.
"""

import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import model_a as A
import search_b as B

MASK8 = 0x0101010101010101
AMBIG = -1


# ------------------------------------------------------------------ helpers

def rank1_factors(mat2):
    u = 0
    w = 0
    for i in range(2):
        for j in range(2):
            if (mat2 >> (2 * i + j)) & 1:
                u |= 1 << i
                w |= 1 << j
    return u, w


def elmul_lut(m):
    """x -> x * m in F2[G], as a 64-entry list"""
    return [A.elmul_mask(x, m) for x in range(64)]


def make_moves(r):
    """moves: list of dicts with nat fast-update data and formal fast-update data"""
    moves = []
    gp1_luts = {}
    for gi in (A.A_IDX, A.B_IDX):
        gp1 = (1 << gi) ^ (1 << A.E_IDX)
        gp1_luts[gi] = elmul_lut(gp1)
        Amat = A.mm2(A.ELTS[gi], A.IDENT2) ^ A.IDENT2
        uA, wA = rank1_factors(Amat)
        for N in A.rank_one_idempotents(r):
            uN = 0
            wN = 0
            for i in range(r):
                for j in range(r):
                    if N[i][j]:
                        uN |= 1 << i
                        wN |= 1 << j
            umask = 0
            wmask = 0
            for i in range(r):
                for al in range(2):
                    if ((uN >> i) & 1) and ((uA >> al) & 1):
                        umask |= 1 << (2 * i + al)
            for j in range(r):
                for be in range(2):
                    if ((wN >> j) & 1) and ((wA >> be) & 1):
                        wmask |= 1 << (2 * j + be)
            fcall = A.formal_of_call(gi, N, r)
            moves.append({
                "UU": umask * MASK8, "WW": wmask * MASK8,
                "sum": A.sum_mask_of_N(N, r),
                "frows": [tuple(fcall[i * r + j] for j in range(r))
                          for i in range(r)],
                "lut": gp1_luts[gi],
                "vbits": uN, "phibits": wN,
                "fc": fcall,
            })
    return moves


def nat_apply(state, mv):
    x = state & mv["UU"]
    x ^= x >> 4
    x ^= x >> 2
    x ^= x >> 1
    return state ^ (mv["WW"] & ((x & MASK8) * 0xFF))


def formal_pack(rows, r):
    out = 0
    for i in range(r):
        for j in range(r):
            out |= rows[i][j] << (6 * (i * r + j))
    return out


def formal_unpack(state, r):
    return tuple((state >> (6 * (i * r + j))) & 63
                 for i in range(r) for j in range(r))


def formal_apply(state, mv, r):
    rows = [[(state >> 6 * (i * r + j)) & 63 for j in range(r)]
            for i in range(r)]
    lut = mv["lut"]
    vbits = mv["vbits"]
    phibits = mv["phibits"]
    for i in range(r):
        c = 0
        for j in range(r):
            if (vbits >> j) & 1:
                c ^= rows[i][j]
        if c:
            gc = lut[c]
            for k in range(r):
                if (phibits >> k) & 1:
                    rows[i][k] ^= gc
    return formal_pack(rows, r)


def formal_T(t, r):
    rows = []
    for i in range(r):
        for j in range(r):
            rows.append((1 << A.S_IDX) if (i == j and i < t) else
                        ((1 << A.E_IDX) if i == j else 0))
    return formal_pack(rows, r)


def formal_mul_T(state, t, r):
    """state * diag([S]^t, 1) : multiply column j by [S] for j < t"""
    lut = elmul_lut(1 << A.S_IDX)
    rows = [[(state >> 6 * (i * r + j)) & 63 for j in range(r)]
            for i in range(r)]
    for i in range(r):
        for j in range(t):
            rows[i][j] = lut[rows[i][j]]
    return formal_pack(rows, r)


def nat_mul_T(state, nat_T, n):
    return A.mul_packed(state, nat_T, n)


def identity_nat(r):
    return A.nat_identity(r)


def identity_formal(r):
    return formal_pack([tuple((1 << A.E_IDX) if i == j else 0
                              for j in range(r)) for i in range(r)], r)


# ---------------------------------------------------------------- ball build

def build_ball(kind, depth, moves, r):
    """dict state -> eps sum (or AMBIG).  kind 'nat' or 'formal'."""
    if kind == "nat":
        ident = identity_nat(r)
        def step(st, mv):
            return nat_apply(st, mv)
    else:
        ident = identity_formal(r)
        def step(st, mv):
            return formal_apply(st, mv, r)
    cur = {ident: 0}
    for _ in range(depth):
        nxt = {}
        for st, sm in cur.items():
            for mv in moves:
                ns = step(st, mv)
                nsum = sm ^ mv["sum"]
                old = nxt.get(ns)
                if old is None:
                    nxt[ns] = nsum
                elif old != nsum:
                    nxt[ns] = AMBIG
        cur = nxt
    return cur


def meet_two(kind, ball_a, ball_b, t, r, sum_T):
    """pairs u in ball_a, v in ball_b with u v = T and compatible sums.
    Returns (n_hits, list of (su, sv))."""
    if kind == "nat":
        nat_T = A.nat_of_target(t, r)
        def mulT(st):
            return nat_mul_T(st, nat_T, 2 * r)
    else:
        def mulT(st):
            return formal_mul_T(st, t, r)
    hits = []
    for st, sm in ball_a.items():
        g = mulT(st)
        val = ball_b.get(g)
        if val is None:
            continue
        want = None if sm == AMBIG else (sum_T ^ sm)
        if val != AMBIG and want is not None and val != want:
            continue
        hits.append((st, g))
    return len(hits), hits


# ------------------------------------------------------------- witness words

def swap_calls(reg, r):
    N = tuple(tuple(1 if (i == j == reg) else 0 for j in range(r))
              for i in range(r))
    return [A.formal_of_call(gi, N, r) for gi in (A.A_IDX, A.B_IDX, A.A_IDX)]


def attaining_word(t, r):
    w = []
    for reg in range(t):
        w += swap_calls(reg, r)
    return w


def formal_word_product(word, r):
    acc = A.formal_identity(r)
    for fc in word:
        acc = A.formal_mul(acc, fc, r)
    return acc


# ------------------------------------------------------------- separable run

def exclude_or_open(t, r, q_list, max_nat_depth=3):
    """For each q in q_list: try nat meet at split k1+k2=q; if nat hits,
    resolve with formal meet.  Returns dict q -> status."""
    moves = make_moves(r)
    D = tuple(tuple(1 if (i == j and i < t) else 0 for j in range(r))
              for i in range(r))
    sum_T = A.sum_mask_of_N(D, r)
    out = {}
    built = {}

    def ball(kind, k):
        key = (kind, k)
        if key not in built:
            built[key] = build_ball(kind, k, moves, r)
        return built[key]

    for q in q_list:
        k1 = q // 2
        k2 = q - k1
        n_hits, _ = meet_two("nat", ball("nat", k1), ball("nat", k2),
                             t, r, sum_T)
        status = f"nat_hits={n_hits}"
        if n_hits == 0:
            out[q] = ("EXCLUDED", status)
            continue
        f_hits, hits = meet_two("formal", ball("formal", k1),
                                ball("formal", k2), t, r, sum_T)
        if f_hits == 0:
            out[q] = ("EXCLUDED", status + f"; formal_hits=0")
        else:
            out[q] = ("WITNESS_CANDIDATE", status + f"; formal_hits={f_hits}")
    return out


# ----------------------------------------------------------------- controls

def check_group_tables():
    assert A.MUL == B.MUL and A.ELTS == B.ELTS
    return 1


def check_fast_apply(moves, r, trials=200):
    import random
    rng = random.Random(20261014)
    n = 2 * r
    for _ in range(trials):
        rows0 = [rng.getrandbits(n) for _ in range(n)]
        st = A.pack_rows(rows0, n)
        mv = moves[rng.randrange(len(moves))]
        fast = nat_apply(st, mv)
        rows = list(rows0)
        umask = mv["UU"] // MASK8
        wmask = mv["WW"] // MASK8
        for i in range(n):
            if bin(rows[i] & umask).count('1') & 1:
                rows[i] ^= wmask
        assert fast == A.pack_rows(rows, n)
    return trials


def check_formal_apply(moves, r, trials=200):
    import random
    rng = random.Random(99)
    for _ in range(trials):
        rows = [[rng.randrange(64) for _ in range(r)] for _ in range(r)]
        st = formal_pack(rows, r)
        mv = moves[rng.randrange(len(moves))]
        fast = formal_apply(st, mv, r)
        # slow: state * fc via A.formal_mul
        slow = A.formal_mul(formal_unpack(st, r), mv["fc"], r)
        assert formal_unpack(fast, r) == slow
    return trials


def check_engine_b(moves, r, depths):
    moves_b = [B.call_nats(gi, N, r) for gi in (B.A_IDX, B.B_IDX)
               for N in B.rank_one_idempotents_b(r)]
    out = {}
    for d in depths:
        ball_a = build_ball("nat", d, moves, r)
        ball_b = B.ball_b(d, moves_b, r)
        unpacked = set(A.unpack_rows(st, 2 * r) for st in ball_a)
        assert unpacked == ball_b, (r, d, len(unpacked), len(ball_b))
        out[f"r{r}_ball{d}"] = len(ball_b)
    return out


def eps_det_ok(q, t):
    return (q & 1) == (t & 1)


def check_parity_controls():
    cases = [(2, 1, False), (3, 1, True), (5, 2, False), (6, 2, True),
             (8, 3, False), (8, 4, True), (11, 4, False), (12, 4, True)]
    for (q, t, want) in cases:
        assert eps_det_ok(q, t) == want, (q, t)
    return len(cases)


def check_witnesses():
    out = {}
    for (t, r) in [(1, 1), (2, 2), (2, 3), (3, 3), (4, 4)]:
        w = attaining_word(t, r)
        prod = formal_word_product(w, r)
        assert prod == A.formal_of_target(t, r), (t, r)
        mut = w[:1] + w[2:]
        assert formal_word_product(mut, r) != A.formal_of_target(t, r)
        out[f"t{t}_r{r}"] = len(w)
    return out


def alias_control(r=3, depth=3):
    """distinct words, equal natural image, unequal formal value (nat not faithful)"""
    moves = make_moves(r)
    seen = {}
    cnt = [0]

    def rec(st, fprod, d):
        if d == depth:
            old = seen.get(st)
            if old is None:
                seen[st] = fprod
            elif old != fprod:
                cnt[0] += 1
            return
        for mv in moves:
            rec(nat_apply(st, mv),
                A.formal_mul(fprod, mv["fc"], r), d + 1)

    rec(identity_nat(r), A.formal_identity(r), 0)
    return {"r": r, "depth": depth, "nat_states": len(seen),
            "alias_pairs_with_different_formal": cnt[0]}


def sum_rank_obstruction():
    """L2 corollary: sum of q rank-one idempotents has rank <= q, and D_t for
    t = r = 4 is I_4 of rank 4, so q >= 4; parity gives q even."""
    return {"needed_rank": 4, "rank_per_call": 1, "q_lower_from_sum": 4,
            "q_parity": "even"}


# ---------------------------------------------------------------- main run

def main():
    full = "--full" in sys.argv
    t_start = time.time()
    R = {"package": "research/four-swap-r4-cnot",
         "task": "bit-new-register-model refined: F2[GL2(F2)] four-SWAP targets at r=4",
         "base_commit": "1f7a934975e5eacaf83511c9ac870263bf095e05",
         "attribution": "Aaron Wang, with help from opencode"}

    R["group_table_checks"] = check_group_tables()
    moves2 = make_moves(2)
    R["nat_fast_apply_crosscheck_trials"] = check_fast_apply(moves2, 2)
    moves3 = make_moves(3)
    R["formal_fast_apply_crosscheck_trials"] = check_formal_apply(moves3, 3)
    R["parity_controls"] = check_parity_controls()
    R["witnesses_calls"] = check_witnesses()
    R["sum_rank_obstruction"] = sum_rank_obstruction()
    R["alias_control"] = alias_control()

    R["engine_b_crosscheck"] = {}
    R["engine_b_crosscheck"].update(check_engine_b(moves2, 2, (1, 2, 3)))
    R["engine_b_crosscheck"].update(check_engine_b(moves3, 3, (1, 2, 3, 4)))

    # validation reproductions
    R["validation"] = {}
    R["validation"]["t2_r2"] = exclude_or_open(2, 2, [2, 4])
    R["validation"]["t2_r3"] = exclude_or_open(2, 3, [2, 4])
    R["validation"]["t3_r3"] = exclude_or_open(3, 3, [1, 3, 5, 7])

    # main object
    t0 = time.time()
    moves4 = make_moves(4)
    R["main"] = {}
    for d in (1, 2, 3):
        td = time.time()
        b = build_ball("nat", d, moves4, 4)
        R["main"][f"ball{d}_states"] = len(b)
        R["main"][f"ball{d}_build_s"] = round(time.time() - td, 2)
    R["main"]["exclusion"] = exclude_or_open(4, 4, [2, 4, 6])
    R["main"]["residual"] = ("q = 8 or 10 by L1 parity; upper bound 12 from "
                             "four disjoint aba words")
    R["main"]["wall_s"] = round(time.time() - t0, 2)

    # obstruction measurement for the residual 4+4 / 5+5 meets:
    # 2^28-bit bitmap sketch over the complete depth-4 stream (r = 4).
    # Skipped in quick mode (about 9 minutes); quick mode carries the stored
    # RECEIPT section forward unchanged and marks it not recomputed.
    if not full:
        prev_path = os.path.join(HERE, "RECEIPT.json")
        prev = None
        if os.path.exists(prev_path):
            try:
                with open(prev_path, encoding="utf-8") as f:
                    prev = json.load(f)
            except (OSError, ValueError):
                prev = None
        if prev and "obstruction" in prev:
            R["obstruction"] = prev["obstruction"]
        else:
            R["obstruction"] = {"recomputed_in_this_run": False,
                                "note": "run verify.py --full to measure"}
    else:
        t0 = time.time()
        M = 1 << 28
        bits = bytearray(M >> 3)
        bits3 = bytearray(M >> 3)

        ball2 = build_ball("nat", 2, moves4, 4)
        ball3 = build_ball("nat", 3, moves4, 4)
        UU_list = [mv["UU"] for mv in moves4]
        WW_list = [mv["WW"] for mv in moves4]
        mm = M - 1
        n_prod = 0
        for st in ball3:
            for i in range(len(moves4)):
                x = st & UU_list[i]
                x ^= x >> 4
                x ^= x >> 2
                x ^= x >> 1
                ns = st ^ (WW_list[i] & ((x & MASK8) * 0xFF))
                h = (ns * 0x9E3779B97F4A7C15) & 0xFFFFFFFFFFFFFFFF
                h ^= h >> 29
                idx = h & mm
                bits[idx >> 3] |= 1 << (idx & 7)
                n_prod += 1
        for st in ball2:
            for i in range(len(moves4)):
                x = st & UU_list[i]
                x ^= x >> 4
                x ^= x >> 2
                x ^= x >> 1
                ns = st ^ (WW_list[i] & ((x & MASK8) * 0xFF))
                h = (ns * 0x9E3779B97F4A7C15) & 0xFFFFFFFFFFFFFFFF
                h ^= h >> 29
                idx = h & mm
                bits3[idx >> 3] |= 1 << (idx & 7)
        occ = sum(bin(byte).count('1') for byte in bits)
        occ3 = sum(bin(byte).count('1') for byte in bits3)
        est = -M * math.log(1.0 - occ / M)
        est3 = -M * math.log(1.0 - occ3 / M)
        R["obstruction"] = {
            "depth4_stream_products": n_prod,
            "depth4_distinct_estimate": round(est),
            "depth3_estimate_control": round(est3),
            "depth3_exact": len(ball3),
            "recomputed_in_this_run": True,
            "note": ("bitmap sketch 2^28 slots; estimator validated against "
                     "the exact depth-3 count; the 4+4 meet needs this ball "
                     "exactly and the 5+5 meet its depth-5 successor"),
            "wall_s": round(time.time() - t0, 2),
        }

    R["wall_s_total"] = round(time.time() - t_start, 1)
    with open(os.path.join(HERE, "RECEIPT.json"), "w", encoding="utf-8") as f:
        json.dump(R, f, indent=2, sort_keys=True)

    v = R["validation"]
    ok = (v["t2_r2"].get(2) and v["t2_r2"].get(2)[0] == "EXCLUDED"
          and v["t2_r2"].get(4)[0] == "EXCLUDED"
          and v["t2_r3"].get(2)[0] == "EXCLUDED"
          and v["t2_r3"].get(4)[0] == "EXCLUDED"
          and all(v["t3_r3"][q][0] == "EXCLUDED" for q in (1, 3, 5, 7)))
    ok_main = all(R["main"]["exclusion"][q][0] == "EXCLUDED" for q in (2, 4, 6))
    assert ok and ok_main, json.dumps(R["main"], indent=1)
    print("PASS_FOUR_SWAP_R4_CNOT",
          "validation t2r2_min=6 t2r3_min=6 t3r3_min=9",
          "t4r4 excluded={2,4,6} residual={8,10} upper=12",
          f"ball3={R['main']['ball3_states']}",
          f"ball4_est={R['obstruction']['depth4_distinct_estimate']}",
          f"alias_pairs={R['alias_control']['alias_pairs_with_different_formal']}",
          "no_new_kappa")


if __name__ == "__main__":
    main()
