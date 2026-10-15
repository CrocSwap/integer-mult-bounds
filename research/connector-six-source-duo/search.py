"""Six-source DUO universal-path search + exact controls.

Model (research/universal-connector-boundary + research/duo-toggle-connector):
a source word is a closed walk on F2^6 starting at 0; steps have Hamming
weight 1 (singleton call B_j) or 2 (DUO call B_jk). k = number of calls,
W = sum of step weights (source adds). Prefixes q_0..q_{k-1}; the available
row masks are D(w) = {q_s xor q_t}; universal means |D(w)| = 64.

This script: exact controls, exact counting exclusions, then a seeded
hill-climbing search over closed walks for universal words with k <= 15.
Writes CERTIFICATE.json. Search is heuristic; witnesses are replayed exactly.
"""
import itertools
import json
import random
import sys
import time

N = 6
FULL = (1 << (1 << N)) - 1  # not used directly; masks live in 0..63


def weight(v):
    return v.bit_count()


SINGLE = [1 << i for i in range(N)]
DUOS = [(1 << i) | (1 << j) for i in range(N) for j in range(i + 1, N)]
STEPS = SINGLE + DUOS


def prefixes_of(steps):
    q = 0
    prefs = [0]
    for s in steps:
        q ^= s
        prefs.append(q)
    return prefs, q


def coverage_mask(prefixes):
    """Bit i set iff mask i is in D(w) = pairwise XORs of prefixes."""
    cov = 0
    m = len(prefixes)
    for a in range(m):
        pa = prefixes[a]
        for b in range(a + 1, m):
            cov |= 1 << (pa ^ prefixes[b])
    cov |= 1  # 0 = p xor p
    return cov


def cov_size(prefixes):
    return bin(coverage_mask(prefixes)).count("1")


def word_stats(steps):
    prefs, q = prefixes_of(steps)
    closed = q == 0
    wsum = sum(weight(s) for s in steps)
    interior = prefs[:-1] if closed else prefs
    distinct = len(set(interior))
    return {
        "k": len(steps),
        "W": wsum,
        "closed": closed,
        "distinct_prefixes": distinct,
        "coverage": cov_size(interior),
    }


# ---------------- exact controls ----------------

def controls():
    out = {}
    # duo-toggle-connector in-tree witnesses (n=3,4,5)
    out["duo_n3"] = word_stats([1, 2, 1, 4, 6])
    out["duo_n4"] = word_stats([1, 4, 9, 6, 8, 2])
    out["duo_n5"] = word_stats([1, 2, 8, 18, 12, 16, 1, 2, 4, 2])
    # singleton six-source Gray word (universal-connector-six-source README)
    g = [1, 2, 1, 4, 1, 2, 1, 4, 8, 16, 8, 32, 8, 16, 8, 32]
    out["singleton_n6_gray16"] = word_stats(g)
    # non-subspace six-source word from that README (labels -> bits)
    ns = [1 << i for i in [3, 4, 5, 0, 3, 2, 3, 4, 5, 4, 1, 2, 3, 0, 4, 1]]
    out["singleton_n6_nonsubspace16"] = word_stats(ns)
    return out


def rgs_words(total, max_mult):
    """Restricted-growth words on labels with given multiplicity profile.

    For the singleton census at k=12 all labels appear twice; label words up
    to renaming by first occurrence == restricted-growth strings whose
    multiplicities are all 2.  We enumerate by assigning positions.
    """
    raise NotImplementedError


def singleton_census_k12():
    """Complete canonical census of six-source singleton words of length 12.

    Each label occurs exactly twice. Renaming by first occurrence means we
    enumerate restricted-growth strings of length 12 with all multiplicities
    2 (i.e. RGS whose symbol counts are (2,2,2,2,2,2)); canonical words are
    those RGS. Count = 10,395 per research/universal-connector-six-source.
    """
    words = []

    def rec(seq, counts, maxlabel):
        if len(seq) == 12:
            if maxlabel == 5 and all(c == 2 for c in counts):
                words.append(tuple(seq))
            return
        for lab in range(min(maxlabel + 2, 6)):
            if counts[lab] < 2:
                counts[lab] += 1
                seq.append(lab)
                rec(seq, counts, max(maxlabel, lab))
                seq.pop()
                counts[lab] -= 1

    rec([], [0] * 6, -1)
    best = 0
    hist = {}
    for w in words:
        steps = [1 << lab for lab in w]
        prefs, q = prefixes_of(steps)
        assert q == 0
        c = cov_size(prefs[:-1])
        hist[c] = hist.get(c, 0) + 1
        if c > best:
            best = c
    return {"words": len(words), "max_coverage": best,
            "histogram": {str(k): v for k, v in sorted(hist.items())}}


# ---------------- counting exclusions (exact, by argument + check) ----------------

def counting_exclusions():
    """Verify the small exhaustive parts of the counting arguments.

    (a) A closed k=10 walk with W=10 has all steps of weight 1 (since
        W = sum weights >= k with equality iff all weight 1).  Enumerating
        all-unit closed words of length 10 on six... no: on FIVE sources the
        canonical count is 945 and max coverage is 31 (PR943 / duo-toggle).
    (b) k=12, W=12 on six sources => all-unit => covered by the k=12 census.
    """
    out = {}
    # five-source singleton k=10 census: 945 canonical words, max coverage 31.
    words = []

    def rec(seq, counts, maxlabel):
        if len(seq) == 10:
            if maxlabel == 4 and all(c == 2 for c in counts):
                words.append(tuple(seq))
            return
        for lab in range(min(maxlabel + 2, 5)):
            if counts[lab] < 2:
                counts[lab] += 1
                seq.append(lab)
                rec(seq, counts, max(maxlabel, lab))
                seq.pop()
                counts[lab] -= 1

    rec([], [0] * 5, -1)
    best = 0
    for w in words:
        steps = [1 << lab for lab in w]
        prefs, q = prefixes_of(steps)
        assert q == 0
        best = max(best, cov_size(prefs[:-1]))
    out["singleton_n5_k10"] = {"words": len(words), "max_coverage": best}
    return out


# ---------------- heuristic search ----------------

def random_closed_walk(k, n_duos, rng):
    """Random closed walk of length k with exactly n_duos weight-2 steps."""
    n_singles = k - n_duos
    steps = [rng.choice(SINGLE) for _ in range(n_singles)] + [
        rng.choice(DUOS) for _ in range(n_duos)]
    rng.shuffle(steps)
    parity = 0
    for s in steps:
        parity ^= s
    if parity != 0:
        # repair: find two steps whose replacement preserves closure
        for _ in range(200):
            i = rng.randrange(k)
            j = rng.randrange(k)
            if i == j:
                continue
            old = steps[i] ^ steps[j]
            a = rng.choice(SINGLE if rng.random() < 0.5 else STEPS)
            b = a ^ old
            if b in STEPS and weight(a) + weight(b) == weight(steps[i]) + weight(steps[j]):
                steps[i], steps[j] = a, b
                parity = 0
                for s in steps:
                    parity ^= s
                if parity == 0:
                    break
        else:
            return None
    parity = 0
    for s in steps:
        parity ^= s
    return steps if parity == 0 else None


def score(steps):
    prefs, q = prefixes_of(steps)
    if q != 0:
        return -1
    return cov_size(prefs[:-1])


def hillclimb(k, n_duos, rng, deadline, target=64):
    best_overall = None
    best_score = -1
    while time.time() < deadline:
        w = random_closed_walk(k, n_duos, rng)
        if w is None:
            continue
        cur = score(w)
        it = 0
        while time.time() < deadline and it < 4000:
            it += 1
            i = rng.randrange(k)
            j = rng.randrange(k)
            if i == j:
                continue
            old = w[i] ^ w[j]
            a = rng.choice(SINGLE if rng.random() < 0.5 else STEPS)
            b = a ^ old
            if b not in STEPS:
                continue
            if weight(a) + weight(b) != weight(w[i]) + weight(w[j]):
                continue
            oi, oj = w[i], w[j]
            w[i], w[j] = a, b
            s = score(w)
            if s >= cur:
                cur = s
            else:
                w[i], w[j] = oi, oj
            if cur > best_score:
                best_score = cur
                best_overall = list(w)
            if best_score == target:
                return best_overall, target
    return best_overall, best_score


def main():
    rng = random.Random(20261014)
    t0 = time.time()
    cert = {"model": "closed walks on F2^6, steps weight 1 (B_j) or 2 (DUO B_jk)",
            "seed": 20261014}
    cert["controls"] = controls()
    cert["counting"] = counting_exclusions()
    cert["singleton_k12_census"] = singleton_census_k12()
    print("controls/counting done at", round(time.time() - t0, 1), "s")

    budget = float(sys.argv[1]) if len(sys.argv) > 1 else 150.0
    deadline = t0 + budget
    results = []
    # priority order: beat singleton (16,16) with W <= 16
    plan = [(12, 2), (12, 4), (13, 1), (13, 3), (14, 2), (15, 1), (14, 4), (15, 3)]
    for (k, nd) in plan:
        if time.time() > deadline:
            break
        sub = min(deadline, time.time() + budget / len(plan))
        w, s = hillclimb(k, nd, rng, sub)
        rec = {"k": k, "n_duos": nd, "W": k + nd, "best_coverage": s}
        if w is not None and s == 64:
            rec["witness_steps"] = w
            rec["witness_prefixes"] = prefixes_of(w)[0][:-1]
        results.append(rec)
        print("search k=%d n_duos=%d -> best %d" % (k, nd, s))
        if s == 64:
            # keep searching smaller k only; larger k cannot Pareto-improve
            deadline = min(deadline, time.time())
    cert["search"] = {"time_budget_s": budget, "results": results,
                      "note": "heuristic search; a missing word is a scoped search failure, not an exclusion"}
    with open("CERTIFICATE.json", "w", encoding="utf-8") as f:
        json.dump(cert, f, indent=1)
    print("wrote CERTIFICATE.json")


if __name__ == "__main__":
    main()
