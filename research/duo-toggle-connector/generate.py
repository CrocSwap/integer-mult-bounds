"""Exact census for the DUO-toggle connector alphabet (stdlib only).

The connector interface of research/universal-connector-boundary admits only
singleton source toggles ``B_j: z += B_j x_j`` and paired readouts.  This
package adds exactly one new complete call type

    DUO_{j,k}: z += B_j x_j + B_k x_k     (j != k, one dispatch)

and enumerates restored source words.  By the prefix-difference reduction
(README section "Prefix reduction carries over"), a generic schedule is a
closed walk on F2^n with steps of weight 1 or 2, and it supports every output
mask exactly when the XOR-closure of its prefix set is all of F2^n.

generate.py emits CERTIFICATE.json: census counts, histograms, sorted-record
SHA256s and explicit witness words.  Deterministic; no randomness.

Navinor, with help from opencode.  Apache-2.0.
"""
import hashlib
import itertools
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def wt(v):
    return bin(v).count("1")


def steps(n):
    return [v for v in range(1, 1 << n) if wt(v) <= 2]


def coverage(prefixes):
    P = set(prefixes)
    return {a ^ b for a in P for b in P}


def walk_prefixes(walk):
    q = [0]
    for s in walk:
        q.append(q[-1] ^ s)
    return q


def record_hash(records):
    blob = "\n".join(",".join(str(x) for x in r) for r in sorted(records))
    return hashlib.sha256(blob.encode()).hexdigest()


# ---------------------------------------------------------------------------
# n = 3: complete walk census (smallest falsifying instance).
# ---------------------------------------------------------------------------

def census_n3(kmax=7):
    counts = {}
    best = None
    witness = None
    for k in range(2, kmax + 1):
        for walk in itertools.product(steps(3), repeat=k):
            q = walk_prefixes(walk)
            if q[-1] != 0:
                continue
            W = sum(wt(s) for s in walk)
            if len(coverage(q)) == 8:
                counts[(k, W)] = counts.get((k, W), 0) + 1
                if best is None or (k, W) < best:
                    best = (k, W)
                    witness = list(walk)
    return counts, best, witness


# ---------------------------------------------------------------------------
# Prefix-set census.  A closed walk visiting s distinct prefixes can cover all
# 2^n masks only if C(s, 2) >= 2^n - 1.  We enumerate every s-point set
# P = {0} + (s-1) nonzero points with P + P = F2^n, pruning on pair-sum
# collisions (monotone), then search its covering walks.
# ---------------------------------------------------------------------------

def cover_sets(n, s, max_coll):
    """All P = {0} + points, |P| = s, P + P = F2^n.  Complete (prune is sound)."""
    found = []
    limit = 1 << n

    def dfs(points, start, sums_mask, m):
        if m == s:
            if bin(sums_mask).count("1") == limit:
                found.append(tuple(points))
            return
        for v in range(start, limit):
            nm = sums_mask
            for p in points:
                nm |= 1 << (p ^ v)
            nm |= 1 << v
            distinct_nonzero = bin(nm).count("1") - 1
            pairs = m * (m + 1) // 2
            if pairs - distinct_nonzero > max_coll:
                continue
            points.append(v)
            dfs(points, v + 1, nm, m + 1)
            points.pop()

    dfs([0], 1, 1, 1)
    return found


def min_cover_walk(P, kmax, wmax=None):
    """Min (k, W) closed walk on the wt<=2 graph of P visiting every point.

    Returns the lexicographically smallest (k, W) with k <= kmax (and
    W <= wmax when given), or None.  Complete for the stated bounds.
    """
    P = set(P)
    total = len(P)
    edges = {u: [v for v in P if v != u and wt(u ^ v) <= 2] for u in P}
    # Any closed walk covering every vertex uses two distinct edges at each
    # vertex, so a vertex with fewer than two near neighbours rules a set out
    # at any length.
    if total > 1 and any(len(nbrs) < 2 for nbrs in edges.values()):
        return None
    best = None

    def rec(u, visited, k, W):
        nonlocal best
        if best is not None and (k, W) >= best:
            return
        if k == kmax:
            return
        for v in edges[u]:
            nw = W + wt(u ^ v)
            if wmax is not None and nw > wmax:
                continue
            nk = k + 1
            if v == 0:
                if len(visited) == total:
                    cand = (nk, nw)
                    if best is None or cand < best:
                        best = cand
                continue
            if v in visited:
                continue
            if nk + (total - len(visited) - 1) > kmax:
                continue
            rec(v, visited | {v}, nk, nw)

    rec(0, frozenset({0}), 0, 0)
    return best


def extract_walk(P, kmax):
    """One concrete min-(k, W) covering walk on P, as a list of steps."""
    P = set(P)
    total = len(P)
    edges = {u: [v for v in P if v != u and wt(u ^ v) <= 2] for u in P}
    target = min_cover_walk(P, kmax)
    found = None

    def rec(u, visited, k, W, path):
        nonlocal found
        if found is not None:
            return
        if k > target[0] or W > target[1]:
            return
        for v in edges[u]:
            nw = W + wt(u ^ v)
            nk = k + 1
            if v == 0:
                if len(visited) == total and (nk, nw) == target:
                    found = path + [u]  # the return step back to 0
                continue
            if v in visited:
                continue
            if nk + (total - len(visited) - 1) > kmax:
                continue
            rec(v, visited | {v}, nk, nw, path + [u ^ v])

    rec(0, frozenset({0}), 0, 0, [])
    return target, found


# ---------------------------------------------------------------------------
# Predecessor control: the 945 singleton pairings of the frozen alphabet
# (research/universal-connector-boundary, Ross Richardson,
# CrocSwap/integer-mult-bounds#943).
# ---------------------------------------------------------------------------

def singleton_945():
    """All 10-call words over 5 labels used exactly twice (labelled in order
    of first occurrence).  Returns (count, max coverage, histogram)."""
    def matchings(items):
        if not items:
            yield ()
            return
        a = items[0]
        for i in range(1, len(items)):
            b = items[i]
            rest = items[1:i] + items[i + 1:]
            for m in matchings(rest):
                yield ((a, b),) + m

    pairs = list(matchings(tuple(range(10))))
    hist = {}
    maxcov = 0
    for m in pairs:
        word = [0] * 10
        label = 0
        for a, b in m:
            word[a] = word[b] = label
            label += 1
        q = [0]
        for lab in word:
            q.append(q[-1] ^ (1 << lab))
        cov = len(coverage(q))
        hist[cov] = hist.get(cov, 0) + 1
        maxcov = max(maxcov, cov)
    return len(pairs), maxcov, dict(sorted(hist.items()))


# ---------------------------------------------------------------------------
# Readout placement: one boundary pair per requested mask.
# ---------------------------------------------------------------------------

def placement(walk, n):
    q = walk_prefixes(walk)
    where = {}
    for s, val in enumerate(q):
        where.setdefault(val, s)
    out = {}
    for mask in range(1, 1 << n):
        for a in range(len(q)):
            for b in range(len(q)):
                if (q[a] ^ q[b]) == mask:
                    out[mask] = (a, b)
                    break
            if mask in out:
                break
    return q, out


def batch_word(walk, placements, n):
    """Full 62+10-call batch word: source calls + two readouts per output."""
    readouts = {}
    for mask, (a, b) in placements.items():
        readouts.setdefault(a, []).append(mask)
        readouts.setdefault(b, []).append(mask)
    word = []
    for boundary in range(len(walk) + 1):
        for mask in readouts.get(boundary, []):
            word.append(["A", mask])
        if boundary < len(walk):
            step = walk[boundary]
            js = [j for j in range(n) if step >> j & 1]
            word.append(["B", js[0]] if len(js) == 1 else ["DUO", js[0], js[1]])
    return word


# ---------------------------------------------------------------------------

def main():
    cert = {
        "package": "research/duo-toggle-connector",
        "claim": (
            "In the DUO alphabet {B_j} U {DUO_{j,k}} the five-source universal "
            "source word has unique Pareto profile (k, W) = (10 calls, 12 "
            "toggle-adds); the frozen singleton alphabet needs (12, 12)."),
        "model": {
            "steps": "nonzero vectors of weight 1 or 2 over F2^n",
            "word": "closed walk q_0 = 0, q_k = 0, steps s_t, q_t = q_{t-1} + s_t",
            "W": "sum of step weights (= total source touches)",
            "coverage": "D(w) = {q_a + q_b} over prefix pairs; full iff = F2^n",
            "prices": "root query = one complete call; toggle-add = one source add",
        },
        "lower_bounds": {
            "k >= 10 (n=5)": (
                "C(s,2) >= 31 for s distinct prefixes gives s >= 9; k >= s; "
                "the complete s=9 census finds zero difference covers, so "
                "s >= 10 and k >= 10."),
            "W >= 12 (n=5)": (
                "Each source is touched an even number of times, so W is even "
                "and W >= 2n = 10. W = 10 forces k <= 10 and leaves only the "
                "all-unit k=10 words (the frozen 945 pairings, max coverage "
                "31) or k <= 9 words, which need s <= 9 covers that do not "
                "exist. Hence W >= 12."),
        },
    }

    counts3, best3, wit3 = census_n3()
    cert["n3"] = {
        "counts": {"k%dW%d" % t: c for t, c in sorted(counts3.items())},
        "pareto": list(best3),
        "witness_walk": wit3,
        "witness_prefixes": walk_prefixes(wit3),
        "singleton_baseline": [6, 6],
    }

    # n = 4 side row (the card targets n=3 and n=5; this is scoped as such).
    sets4 = cover_sets(4, 6, 0)
    rows4 = []
    for P in sets4:
        mw = min_cover_walk(P, 8)
        if mw is not None:
            rows4.append((mw, P))
    rows4.sort()
    wit4 = extract_walk(rows4[0][1], 8)
    cert["n4_side_row"] = {
        "scope": "side row; the card's instances are n=3 and n=5",
        "cover_sets_s6": len(sets4),
        "walkable": len(rows4),
        "pareto_rows": [{"kW": list(mw), "P": list(P)} for mw, P in rows4[:5]],
        "witness_walk": wit4[1],
        "witness_prefixes": walk_prefixes(wit4[1]),
        "singleton_baseline": [8, 8],
    }

    sets9 = cover_sets(5, 9, 5)
    cert["n5_s9_cover_sets"] = len(sets9)

    sets10 = cover_sets(5, 10, 14)
    hist = {}
    best = None
    best_P = None
    for P in sets10:
        mw = min_cover_walk(P, 10)
        if mw is None:
            continue
        hist[mw] = hist.get(mw, 0) + 1
        if best is None or mw < best:
            best, best_P = mw, P
    cert["n5_s10"] = {
        "cover_sets": len(sets10),
        "walkable_sets": sum(hist.values()),
        "walk_histogram": {"k%dW%d" % t: c for t, c in sorted(hist.items())},
        "sorted_set_record_sha256": record_hash(sets10),
        "pareto": list(best),
    }

    walk = extract_walk(best_P, 10)
    wit_steps = walk[1]
    q = walk_prefixes(wit_steps)
    assert q[-1] == 0 and len(wit_steps) == best[0]
    assert sum(wt(s) for s in wit_steps) == best[1]
    assert len(coverage(q)) == 32
    q, place = placement(wit_steps, 5)
    cert["n5_witness"] = {
        "walk": wit_steps,
        "k": best,
        "W": sum(wt(s) for s in walk[1]),
        "prefixes": q,
        "placement": {str(m): list(t) for m, t in sorted(place.items())},
        "batch_word": batch_word(wit_steps, place, 5),
    }

    p945 = singleton_945()
    cert["predecessor_945_control"] = {
        "pairings": p945[0],
        "max_coverage": p945[1],
        "histogram": p945[2],
        "source": "research/universal-connector-boundary (CrocSwap/integer-mult-bounds#943, Ross Richardson)",
    }

    cert["pricing"] = {
        "baseline_74": {"root_queries": 74, "toggle_adds": 74,
                        "source_calls": 12, "readouts": 62},
        "duo_72": {"root_queries": 72, "toggle_adds": 74,
                   "source_calls": 10, "readouts": 62},
        "saving": "2 root queries, 0 toggle-adds; equals 2 per-call overheads o "
                  "in the model c_B = o + p, c_DUO = o + 2p, c_A = o + p. "
                  "Strictly better for every o > 0; adds unchanged.",
    }

    out = os.path.join(HERE, "CERTIFICATE.json")
    blob = json.dumps(cert, indent=1, sort_keys=True) + "\n"
    if "--check" in sys.argv:
        with open(out, encoding="utf-8") as f:
            on_disk = f.read()
        if on_disk != blob:
            print("FAIL: CERTIFICATE.json drift from deterministic regeneration")
            return 1
        print("PASS_DUO_TOGGLE_GENERATE deterministic (matches CERTIFICATE.json)")
    else:
        with open(out, "w", encoding="utf-8") as f:
            f.write(blob)
        print("WROTE", out)
    print("n3 pareto", best3, "witness", wit3)
    print("n4 cover sets", len(sets4), "walkable", len(rows4), "rows", rows4[:3])
    print("n5 s9 cover sets", len(sets9))
    print("n5 s10 cover sets", len(sets10), "hist", cert["n5_s10"]["walk_histogram"])
    print("n5 witness", walk[1], "prefixes", q)
    print("945 control: pairings", p945[0], "max", p945[1], "hist", p945[2])
    return 0


if __name__ == "__main__":
    sys.exit(main())
