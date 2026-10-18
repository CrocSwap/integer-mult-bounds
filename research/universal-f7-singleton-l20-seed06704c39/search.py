#!/usr/bin/env python3
"""Deterministic search campaign for the KB3b f(7) continuation (PR943 model).

Two complementary landscapes, both exact-integer and standard library only:

* WORD side: restored words (closed hypercube walks).  Universality is the
  interval-XOR condition D(w) = {q_s xor q_t} = F2^n.  Steepest-ascent
  iterated local search (transpositions + segment reversals + kicks).
* SET side: k-point sets P with 0 in P, objective |P + P|.  Steepest-ascent
  over point swaps.  Covers found here are then tested for walk
  realizability (a closed walk through P needs min induced degree >= 2, and
  at length |P| exactly a Hamiltonian cycle).

The campaign is deterministic given the seeds below (CPython `random`
Mersenne Twister).  `main` prints one marker per stage and writes
SEARCH.json.  This is a heuristic search: a ceiling attained here is a
search failure, not an exclusion.
"""
import json
import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from engine import hamiltonian_cycle, word_is_universal

N = 7


# ------------------------------------------------------------- word utilities

def word_pts(word):
    q = 0
    pts = [0]
    for j in word:
        q ^= 1 << j
        pts.append(q)
    return pts


def cov_pts(pts):
    m = 0
    for i in range(len(pts)):
        a = pts[i]
        for k in range(i, len(pts)):
            m |= 1 << (a ^ pts[k])
    return m


def word_cov(word):
    return cov_pts(word_pts(word))


def missing_masks(pts):
    m = cov_pts(pts)
    return [x for x in range(128) if not (m >> x) & 1]


def patterns(n, L):
    """All even-count patterns (each label used, count >= 2, sum L)."""
    out = []

    def rec(rem, cap, acc):
        if rem == 0:
            out.append(list(acc))
            return
        for x in range(2, min(rem, cap) + 1, 2):
            rec(rem - x, x, acc + [x])

    rec(L - 2 * n, L - 2 * n, [])
    return [sorted([2 + e for e in p] + [2] * (n - len(p)), reverse=True) for p in out]


# ------------------------------------------------------------------ word ILS

def climb_word(word, L, evals):
    """Steepest ascent over transpositions and segment reversals."""
    cur = word_cov(word).bit_count()
    while True:
        best = cur
        move = None
        for i in range(L):
            for k in range(i + 1, L):
                word[i], word[k] = word[k], word[i]
                v = word_cov(word).bit_count()
                word[i], word[k] = word[k], word[i]
                evals[0] += 1
                if v > best:
                    best, move = v, ("swap", i, k)
        for i in range(L):
            for k in range(i + 2, L):
                word[i:k + 1] = reversed(word[i:k + 1])
                v = word_cov(word).bit_count()
                word[i:k + 1] = reversed(word[i:k + 1])
                evals[0] += 1
                if v > best:
                    best, move = v, ("rev", i, k)
        if move is None:
            return cur
        if move[0] == "swap":
            _, i, k = move
            word[i], word[k] = word[k], word[i]
        else:
            _, i, k = move
            word[i:k + 1] = reversed(word[i:k + 1])
        cur = best
        if cur == 128:
            return cur


def word_search(L, seed, restarts, kick):
    """Deterministic ILS over restored words of length L at n = 7."""
    R = random.Random(seed)
    pats = patterns(N, L)
    best = (0, None)
    evals = [0]
    for r in range(restarts):
        counts = [2] * N
        for i, e in enumerate(R.choice(pats)):
            counts[i] = e
        word = []
        for j, c in enumerate(counts):
            word += [j] * c
        R.shuffle(word)
        c = climb_word(word, L, evals)
        it = 0
        while c < 128 and it < 40:
            it += 1
            for _ in range(kick):
                i, k = R.randrange(L), R.randrange(L)
                word[i], word[k] = word[k], word[i]
            c2 = climb_word(word, L, evals)
            if c2 >= c:
                c = c2
            if c > best[0]:
                best = (c, word[:])
        if c == 128:
            break
    return dict(best=best[0], word=best[1], evals=evals[0])


# ------------------------------------------------------------------- set ILS

def climb_set(P, k, evals):
    cur = cov_pts(sorted(P)).bit_count()
    pool = [v for v in range(128) if v not in set(P)]
    while True:
        best = cur
        move = None
        for a in range(k):
            for v in pool:
                old = P[a]
                P[a] = v
                val = cov_pts(sorted(P)).bit_count()
                P[a] = old
                evals[0] += 1
                if val > best:
                    best, move = val, (a, v)
        if move is None:
            return cur
        a, v = move
        pool.remove(v)
        pool.append(P[a])
        P[a] = v
        cur = best
        if cur == 128:
            return cur


def set_search(k, seed, restarts):
    """Deterministic ILS over k-point sets; returns best set and cover count."""
    R = random.Random(seed)
    best = (0, None)
    covers = 0
    first_cover = None
    evals = [0]
    for r in range(restarts):
        P = [0] + R.sample(range(1, 128), k - 1)
        c = climb_set(P, k, [0])
        evals[0] += 1
        if c == 128:
            covers += 1
            if first_cover is None:
                first_cover = sorted(P)
        if c > best[0]:
            best = (c, sorted(P))
        if c == 128 and first_cover is not None:
            # keep searching to measure the cover rate, not just one hit
            pass
    return dict(best=best[0], covers=covers, first_cover=first_cover)


def induced_degrees(P, n=7):
    S = set(P)
    return sorted(sum(1 for b in range(n) if (v ^ (1 << b)) in S) for v in P)


# --------------------------------------------------------------- the campaign

CAMPAIGN = {
    "word_L24_control": dict(L=24, seed=5, restarts=30, kick=6),
    "word_L22": dict(L=22, seed=21, restarts=40, kick=8),
    "word_L20": dict(L=20, seed=22, restarts=40, kick=8),
    "set_k20": dict(k=20, seed=11, restarts=30),
    "set_k22": dict(k=22, seed=12, restarts=30),
}

EXTENDED = {
    "word_L24_control": dict(L=24, seed=5, restarts=30, kick=6),
    "word_L22": dict(L=22, seed=21, restarts=600, kick=8),
    "word_L20": dict(L=20, seed=22, restarts=600, kick=8),
    "set_k20": dict(k=20, seed=11, restarts=300),
    "set_k22": dict(k=22, seed=12, restarts=300),
}


def run_campaign(table=None):
    table = table or CAMPAIGN
    out = {}
    t0 = time.time()

    p = table["word_L24_control"]
    r = word_search(p["L"], p["seed"], p["restarts"], p["kick"])
    assert r["best"] == 128 and word_is_universal(r["word"], 7), "L=24 control failed"
    out["word_L24_control"] = {"coverage": 128, "word": r["word"]}
    print(f"SEARCH word L=24 control coverage=128 word={r['word']}")

    for name in ("word_L22", "word_L20"):
        p = table[name]
        r = word_search(p["L"], p["seed"], p["restarts"], p["kick"])
        pts = word_pts(r["word"])
        out[name] = {
            "coverage": r["best"],
            "word": r["word"],
            "missing": missing_masks(pts),
            "evals": r["evals"],
        }
        print(f"SEARCH word L={p['L']} coverage={r['best']}/128 "
              f"missing={out[name]['missing']} evals={r['evals']}")

    for name in ("set_k20", "set_k22"):
        p = table[name]
        r = set_search(p["k"], p["seed"], p["restarts"])
        entry = {"best": r["best"], "covers": r["covers"]}
        if r["first_cover"]:
            entry["first_cover"] = r["first_cover"]
            entry["first_cover_degrees"] = induced_degrees(r["first_cover"])
            entry["first_cover_hamiltonian_cycle"] = (
                hamiltonian_cycle(r["first_cover"], 7) is not None)
        out[name] = entry
        print(f"SEARCH set k={p['k']} best={r['best']} covers={r['covers']} "
              f"degrees={entry.get('first_cover_degrees')}")

    out["seconds"] = round(time.time() - t0, 1)
    return out


def main():
    extended = "--extended" in sys.argv[1:]
    out = run_campaign(EXTENDED if extended else None)
    name = "SEARCH-EXTENDED.json" if extended else "SEARCH.json"
    (Path(__file__).resolve().parent / name).write_text(
        json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    print("PASS_F7_L20_SEARCH "
          f"L20={out['word_L20']['coverage']} L22={out['word_L22']['coverage']} "
          f"L24={out['word_L24_control']['coverage']} "
          f"setk20_covers={out['set_k20']['covers']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
