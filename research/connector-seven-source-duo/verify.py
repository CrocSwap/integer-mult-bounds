#!/usr/bin/env python3
"""Verifier for research/connector-seven-source-duo.

Deterministic replay of the certificate and its controls. Standard library only.

Model (research/universal-connector-boundary, unchanged): a restored source word
is a closed walk q_t on F2^n whose steps have Hamming weight 1 (singleton call)
or 2 (charged DUO call); paired readouts realize D(w) = {q_s xor q_t}; the word
is universal iff D(w) = F2^n. Closure forces every label count even, so W = k + d
toggle-adds for d weight-2 steps.

Controls: the n = 5 DUO witness and the 945-word singleton census of
research/universal-connector-boundary / research/duo-toggle-connector, the Gray
construction for n = 4..7, an independent dual-coverage test, three mutation
controls, and the full all-127-row batch bill.
"""
import hashlib
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

HERE = __file__.rsplit("\\", 1)[0] if "\\" in __file__ else __file__.rsplit("/", 1)[0]


def prefixes(steps):
    q = 0
    pref = [0]
    for s in steps:
        q ^= s
        pref.append(q)
    return pref, q


def coverage(pref):
    seen = 0
    m = len(pref)
    for i in range(m):
        pi = pref[i]
        for j in range(i + 1, m):
            seen |= 1 << (pi ^ pref[j])
    seen |= 1  # 0 = q_i xor q_i
    return seen


def dual_missing(pref, n):
    S = set(pref)
    out = []
    for m in range(1 << n):
        if not any((p ^ m) in S for p in S):
            out.append(m)
    return out


def wt(x):
    return bin(x).count("1")


def rgs_words(k, alphabet):
    """All restricted-growth words of length k over consecutive labels."""
    def rec(seq, mx):
        if len(seq) == k:
            yield list(seq)
            return
        for lab in range(min(mx + 1, alphabet - 1) + 1):
            seq.append(lab)
            yield from rec(seq, max(mx, lab))
            seq.pop()
    yield from rec([0], 0)


def perfect_matching_words(n_labels, k):
    """Words of length k with each of n_labels labels used exactly twice, up to
    label renaming (restricted growth). k = 2 * n_labels."""
    out = []

    def rec(seq, counts, mx):
        if len(seq) == k:
            if all(c == 2 for c in counts):
                out.append(list(seq))
            return
        for lab in range(min(mx + 1, n_labels - 1) + 1):
            if counts[lab] < 2:
                counts[lab] += 1
                seq.append(lab)
                rec(seq, counts, max(mx, lab))
                seq.pop()
                counts[lab] -= 1
    rec([0], [1] + [0] * (n_labels - 1), 0)
    return out


def gray_steps(n):
    """Gray-cycle word: reflected Gray code on ceil(n/2) then on the rest."""
    k = (n + 1) // 2
    steps = []
    for lo, size in ((0, k), (k, n - k)):
        if size <= 0:
            continue
        g = [i ^ (i >> 1) for i in range(1 << size)]
        for i in range(len(g) - 1):
            steps.append((g[i] ^ g[i + 1]) << lo)
        steps.append(g[-1] << lo)  # return to zero
    return steps


def check_word(steps, n):
    pref, q = prefixes(steps)
    ok_closure = q == 0
    ok_weights = all(wt(s) in (1, 2) for s in steps)
    counts = [sum(1 for s in steps if (s >> i) & 1) for i in range(n)]
    ok_restore = all(c % 2 == 0 for c in counts)
    cov = coverage(pref)
    full = cov == (1 << (1 << n)) - 1
    dual = dual_missing(pref, n)
    return {
        "k": len(steps),
        "d": sum(1 for s in steps if wt(s) == 2),
        "W": sum(wt(s) for s in steps),
        "closure": ok_closure,
        "weights_ok": ok_weights,
        "restored": ok_restore,
        "label_counts": counts,
        "coverage_masks": bin(cov).count("1"),
        "universal": full,
        "dual_missing": len(dual),
    }


def main():
    cert = json.load(open(HERE + "/CERTIFICATE.json", encoding="utf-8"))
    fails = []

    def expect(cond, name):
        if not cond:
            fails.append(name)

    # Control 1: the n = 5 DUO witness of research/duo-toggle-connector.
    w5 = cert["controls"]["n5_duo_witness"]["steps"]
    pref5, q5 = prefixes(w5)
    expect(q5 == 0, "n5 witness closure")
    expect(pref5 == cert["controls"]["n5_duo_witness"]["prefixes"], "n5 witness prefixes")
    expect(bin(coverage(pref5)).count("1") == 32, "n5 witness universal")

    # Control 2: the 945-word n = 5 singleton census histogram, independently
    # recomputed; compare with the merged table of
    # research/universal-connector-boundary (size of D(w), including 0).
    words = perfect_matching_words(5, 10)
    expect(len(words) == 945, "945 canonical words")
    hist = {}
    for w in words:
        pref, q = prefixes([1 << lab for lab in w])
        if q != 0:
            continue
        sz = bin(coverage(pref)).count("1")
        hist[str(sz)] = hist.get(str(sz), 0) + 1
    expect(hist == cert["controls"]["n5_singleton_histogram"]["size_of_D_including_0"],
           "945-word histogram")

    # Control 3: the Gray construction covers F2^n for n = 4..7 (and the merged
    # six-source literal word covers F2^6).
    for n in (4, 5, 6, 7):
        pref, q = prefixes(gray_steps(n))
        expect(q == 0 and coverage(pref) == (1 << (1 << n)) - 1, "gray n=%d" % n)
    lit6 = cert["controls"]["n6_gray_literal"]["steps"]
    pref6, q6 = prefixes(lit6)
    expect(q6 == 0 and coverage(pref6) == (1 << 64) - 1, "n6 literal gray")
    expect(bin(coverage(pref6)).count("1") == 64, "n6 literal coverage 64")

    # Side row: a (21, 26) word found by the same search. It is incomparable
    # with (22, 24); neither word has a proved global Pareto-optimality claim.
    side = check_word(cert["side_row_21_26"]["steps"], 7)
    expect(side["universal"] and side["closure"] and side["restored"], "side row 21,26")
    expect(side["k"] == 21 and side["d"] == 5 and side["W"] == 26, "side row bill")

    # Headline: the (22, 24) word.
    main_res = check_word(cert["headline_22_24"]["steps"], 7)
    expect(main_res["closure"], "headline closure")
    expect(main_res["weights_ok"], "headline step weights <= 2")
    expect(main_res["restored"], "headline restored")
    expect(main_res["universal"], "headline universal")
    expect(main_res["dual_missing"] == 0, "headline dual test")
    expect(main_res["k"] == 22 and main_res["d"] == 2 and main_res["W"] == 24,
           "headline bill")

    # Complete all-127-row batch bill, charged in full.
    rows = 127
    queries = main_res["k"] + 2 * rows
    adds = main_res["W"] + 2 * rows
    base_q, base_a = 24 + 2 * rows, 24 + 2 * rows
    expect(queries == 276 and adds == 278, "batch bill")
    expect(base_q == 278 and base_a == 278, "baseline bill")
    expect(queries < base_q and adds == base_a, "strict Pareto improvement")

    # Mutation controls: each corruption must break closure, restoration,
    # weights or universality.
    steps = list(cert["headline_22_24"]["steps"])
    mut = steps[:-1]  # delete one call
    r = check_word(mut, 7)
    expect(not (r["closure"] and r["universal"]), "mutation: deleted call")
    mut = list(steps)
    mut[3] = 16  # shrink one DUO step to a singleton
    r = check_word(mut, 7)
    expect(not (r["closure"] and r["restored"] and r["universal"]), "mutation: shrunk DUO")
    mut = list(steps)
    mut[0] ^= 2  # retarget one label
    r = check_word(mut, 7)
    expect(not (r["closure"] and r["universal"]), "mutation: retargeted call")

    # Certificate digest over the canonical words.
    digest_src = json.dumps({
        "headline_22_24": cert["headline_22_24"]["steps"],
        "side_row_21_26": cert["side_row_21_26"]["steps"],
    }, sort_keys=True)
    digest = hashlib.sha256(digest_src.encode("utf-8")).hexdigest()
    expect(digest == cert["search_provenance"]["words_sha256"], "certificate digest")

    if fails:
        raise SystemExit("FAIL_SEVEN_SOURCE_DUO " + ";".join(fails))
    print("PASS_SEVEN_SOURCE_DUO k=22 W=24 queries=276 adds=278 "
          "universal=128/128 controls=945+gray+side+mutations")


if __name__ == "__main__":
    main()
