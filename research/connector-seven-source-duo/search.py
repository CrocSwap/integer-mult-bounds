"""Search v2 for short universal seven-source words in the singleton+DUO alphabet.

Improvements over v1: (1) shrink heuristic - start from a known full cover and
try to replace two points by one while keeping P+P = F2^7; (2) cycle search with
tight weight-2 budgets first, with a degree/connectivity precheck and recorded
diagnostics; (3) controls on known small witnesses.

Usage: python3 search.py  (writes SEARCH-RESULT.json)
"""
import json
import random
import time

N = 7
NB = 1 << N
FULLMASK = (1 << NB) - 1


def cov_mass(P):
    seen = 1  # 0 = p ^ p is always realized
    s = len(P)
    for i in range(s):
        pi = P[i]
        for j in range(i + 1, s):
            seen |= 1 << (pi ^ P[j])
    return seen.bit_count(), seen


def covers(P):
    return cov_mass(P)[1] == FULLMASK


def hamiltonian_cycle(P, max_weight2, node_cap=4_000_000):
    s = len(P)
    adj1 = [0] * s
    adj2 = [0] * s
    deg = [0] * s
    for i in range(s):
        for j in range(i + 1, s):
            w = (P[i] ^ P[j]).bit_count()
            if w == 1:
                adj1[i] |= 1 << j
                adj1[j] |= 1 << i
                deg[i] += 1
                deg[j] += 1
            elif w == 2:
                adj2[i] |= 1 << j
                adj2[j] |= 1 << i
                deg[i] += 1
                deg[j] += 1
    if min(deg) < 2:
        return None, {"reason": "min-degree<2"}
    full = (1 << s) - 1
    found = []
    nodes = [0]

    def rec(cur, used, path, d):
        if found:
            return
        nodes[0] += 1
        if nodes[0] > node_cap:
            return
        if used == full:
            if (adj1[cur] & 1) and d <= max_weight2:
                found.append((path[:], d))
            elif d < max_weight2 and (adj2[cur] & 1):
                found.append((path[:], d + 1))
            return
        cand = []
        nxt = adj1[cur] & ~used
        while nxt:
            b = nxt & -nxt
            nxt ^= b
            v = b.bit_length() - 1
            cand.append((0, v))
        if d < max_weight2:
            nxt = adj2[cur] & ~used
            while nxt:
                b = nxt & -nxt
                nxt ^= b
                v = b.bit_length() - 1
                cand.append((1, v))
        cand.sort()
        for dw, v in cand:
            # forward check: v must have an unused neighbour unless it is last
            unused = full & ~used & ~(1 << v)
            if unused and not ((adj1[v] | adj2[v]) & unused):
                continue
            rec(v, used | (1 << v), path + [v], d + dw)

    rec(0, 1, [0], 0)
    if found:
        return found[0], {"nodes": nodes[0]}
    return None, {"reason": "exhausted-or-cap", "nodes": nodes[0]}


def cycle_to_word(P, cycle):
    order, d = cycle
    k = len(order)
    return [P[order[i]] ^ P[order[(i + 1) % k]] for i in range(k)]


def two_subspace_basis():
    P = set(range(16))
    for y in range(8):
        P.add(y << 4)
    return sorted(P)


def try_cycle(P, s):
    """Try increasing weight-2 budgets (parity d == s mod 2)."""
    diag = {}
    start = 0 if s % 2 == 0 else 1
    for mw in range(start, 10, 2):
        cyc, info = hamiltonian_cycle(P, mw)
        diag[str(mw)] = info
        if cyc:
            return cyc, diag
    cyc, info = hamiltonian_cycle(P, s)
    diag["max"] = info
    return cyc, diag


def shrink(P, rng):
    """Greedy: replace two points by one, keeping full coverage."""
    P = sorted(P)
    improved = True
    while improved and len(P) > 16:
        improved = False
        pairs = [(i, j) for i in range(len(P)) for j in range(i + 1, len(P))]
        rng.shuffle(pairs)
        for i, j in pairs:
            base = [p for t, p in enumerate(P) if t not in (i, j)]
            for v in range(NB):
                if v in base:
                    continue
                cand = sorted(base + [v])
                if covers(cand):
                    P = cand
                    improved = True
                    break
            if improved:
                break
    return P


def hill_climb_cover(s, restarts, climb_steps, rng, time_cap):
    t0 = time.time()
    best = 0
    for _ in range(restarts):
        if time.time() - t0 > time_cap:
            break
        P = [0] + rng.sample(range(1, NB), s - 1)
        _, seen = cov_mass(P)
        mass = seen.bit_count()
        stuck = 0
        for _ in range(climb_steps):
            if mass == NB:
                return P
            i = rng.randrange(1, s)
            new = rng.randrange(1, NB)
            if new in P:
                continue
            old = P[i]
            P[i] = new
            nmass = cov_mass(P)[0]
            if nmass >= mass:
                mass = nmass
                stuck = 0
            elif stuck > 300 and nmass >= mass - 2:
                # bounded annealing escape from a plateau
                mass = nmass
                stuck = 0
            else:
                P[i] = old
                stuck += 1
            if mass > best:
                best = mass
    return None


def main():
    rng = random.Random(20261015)
    out = {"N": N, "seed": 20261015, "controls": {}, "results": {}}
    t0 = time.time()

    # Control: the n=5 DUO witness of research/duo-toggle-connector must be
    # universal for F2^5 and its recorded prefixes must match.
    w5 = [1, 2, 8, 18, 12, 16, 1, 2, 4, 2]
    q = 0
    pref = [0]
    for st in w5:
        q ^= st
        pref.append(q)
    exp_pref = [0, 1, 3, 11, 25, 21, 5, 4, 6, 2, 0]
    seen5 = 0
    for i in range(len(pref)):
        for j in range(len(pref)):
            seen5 |= 1 << (pref[i] ^ pref[j])
    out["controls"]["n5_duo_witness"] = {
        "prefixes_match": pref == exp_pref,
        "closes": q == 0,
        "coverage_nonzero": bin(seen5).count("1") - 1,
        "expect_31": bin(seen5).count("1") - 1 == 31,
    }

    # Control: two-subspace basis covers F2^7.
    fb = two_subspace_basis()
    out["controls"]["two_subspace_basis"] = {
        "size": len(fb), "covers": covers(fb),
    }

    found = None

    # Phase 1: shrink from the 23-point basis (cheap, deterministic-ish).
    P = shrink(list(fb), rng)
    out["results"]["shrink"] = {"size": len(P), "P": P, "covers": covers(P)}
    print("shrink ->", len(P), "covers", covers(P), flush=True)

    # Phase 2: hill-climb at sizes 22, 21, 20 if shrink stopped early.
    for s, resteps, steps in ((22, 150, 8000), (21, 150, 8000), (20, 150, 8000)):
        P2 = hill_climb_cover(s, resteps, steps, rng, time_cap=180.0)
        if P2 is not None:
            out["results"]["climb%d" % s] = {"P": sorted(P2), "covers": True}
            P = shrink(list(P2), rng)
            out["results"]["shrink2_%d" % s] = {"size": len(P), "P": P, "covers": covers(P)}
            print("climb found cover s=%d -> shrink %d" % (s, len(P)), flush=True)
            break
        else:
            print("climb s=%d: no cover in budget" % s, flush=True)

    # Phase 3: cycle on the smallest cover found.
    cands = []
    for key, v in out["results"].items():
        if isinstance(v, dict) and v.get("covers") and v.get("P"):
            cands.append((len(v["P"]), key, v["P"]))
    cands.sort()
    Pbest = cands[0][2] if cands else None
    out["results"]["candidates"] = [{"key": k, "size": sz} for sz, k, _ in cands]
    if Pbest is not None:
        cyc, diag = try_cycle(Pbest, len(Pbest))
        out["results"]["cycle_diag"] = diag
        if cyc:
            word = cycle_to_word(Pbest, cyc)
            d = cyc[1]
            out["results"]["final"] = {
                "P": sorted(Pbest), "cycle_order": cyc[0], "weight2_edges": d,
                "word": word, "k": len(Pbest), "W": len(Pbest) + d,
            }
            print("CYCLE k=%d W=%d d=%d" % (len(Pbest), len(Pbest) + d, d), flush=True)
        else:
            print("no cycle; diag", diag, flush=True)
        # If the best cover has no cycle or a poor one, try the other covers too.
        for sz, key, Pk in cands[1:]:
            if "final" in out["results"]:
                break
            cyc, diag = try_cycle(Pk, len(Pk))
            out["results"]["cycle_diag_" + key] = diag
            if cyc:
                word = cycle_to_word(Pk, cyc)
                d = cyc[1]
                out["results"]["final"] = {
                    "P": sorted(Pk), "cycle_order": cyc[0], "weight2_edges": d,
                    "word": word, "k": len(Pk), "W": len(Pk) + d,
                }
                print("CYCLE (alt %s) k=%d W=%d d=%d" % (key, len(Pk), len(Pk) + d, d), flush=True)

    out["elapsed_s"] = round(time.time() - t0, 1)
    with open("SEARCH-RESULT.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    print("elapsed", out["elapsed_s"])


if __name__ == "__main__":
    main()
