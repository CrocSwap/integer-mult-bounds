#!/usr/bin/env python3
"""Exact checks for the dyadic aligned-window guard (PROOF.md).

Standard library only.  Scoped finite certificate for one source-geometry statement;
no kappa, no supplier admission.  Produced by Nick Petalas.  Apache-2.0.

The independent oracle is a literal coordinate walk of the source rule
q(j) = j + floor(e*j/S + 1/2).  Every closed form below is compared with it, and
every mutated closed form must be rejected by the same oracle.
"""
import hashlib
import importlib.util
import json
import os
import sys
from bisect import bisect_left

PKG = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(PKG))
MARK = "PASS_DYADIC_ALIGNED_WINDOW_GUARD"


def need(ok, message):
    """Explicit check that stays active under python -O."""
    if not ok:
        raise SystemExit("FAIL: " + message)


# ---------------------------------------------------------------- literal oracle
def literal_selected(S, e):
    """Boolean list over target coordinates: True where some j has q(j) = coordinate."""
    N = S + e
    sel = [False] * N
    for j in range(S):
        sel[j + (2 * e * j + S) // (2 * S)] = True  # floor(e*j/S + 1/2) = (2ej+S)//(2S)
    return sel


def literal_run(sel, a, length):
    """Longest run of selected coordinates inside [a, a+length), by direct scan."""
    best = cur = 0
    for t in range(a, a + length):
        cur = cur + 1 if sel[t] else 0
        if cur > best:
            best = cur
    return best


# ------------------------------------------------------------------ closed forms
def hole_positions(N, e):
    """Lemma 1: H_c = floor(((2c-1)N + e - 1) / (2e)), c = 1..e."""
    return [((2 * c - 1) * N + e - 1) // (2 * e) for c in range(1, e + 1)]


def odd_part(e):
    j = 0
    while e % 2 == 0:
        e //= 2
        j += 1
    return j, e


def run_from_holes(H, a, length):
    """Lemma 2: longest selected run of the window [a, a+length) from the hole list H."""
    lo = bisect_left(H, a)
    hi = bisect_left(H, a + length)
    if lo == hi:
        return length
    best = max(H[lo] - a, a + length - 1 - H[hi - 1])
    for k in range(lo + 1, hi):
        d = H[k] - H[k - 1] - 1
        if d > best:
            best = d
    return best


def aligned_min_run(H, N, length):
    """Minimum over the aligned windows [kL, (k+1)L) of the longest selected run."""
    best = None
    i = 0
    e = len(H)
    for a in range(0, N, length):
        b = a + length
        j = i
        while j < e and H[j] < b:
            j += 1
        if j == i:
            m = length
        else:
            m = max(H[i] - a, b - 1 - H[j - 1])
            for k in range(i + 1, j):
                d = H[k] - H[k - 1] - 1
                if d > m:
                    m = d
        i = j
        if best is None or m < best:
            best = m
    return best


def band_prediction(H, length, W):
    """Theorem 1: with S >= e(6W+1), all aligned windows are good iff L >= 6W+1 and
    no hole offset modulo L lies in [L-1-6W, 6W]."""
    if length < 6 * W + 1:
        return False
    lo, hi = length - 1 - 6 * W, 6 * W
    return not any(lo <= h % length <= hi for h in H)


def classify(n, e, ell, W):
    """Theorem 2: are all aligned windows of length 2^ell good, for N = 2^n and e,
    under the hypothesis N >= e(6W+2)?  (Closed form in the odd part t of e.)"""
    length = 1 << ell
    j, t = odd_part(e)
    m = n - j
    if ell > m:                       # case I: every window holds two whole blocks
        return True
    if ell == m:                      # case II: windows are the blocks
        return t >= 3 or length >= 12 * W + 2
    return (t + 1) * length > t * (12 * W + 3)   # case III


def classify_mutants():
    """Deliberately wrong closed forms; each must disagree with the oracle somewhere."""
    def m_const(n, e, ell, W):                  # 12W+2 in place of 12W+3
        j, t = odd_part(e)
        m = n - j
        L = 1 << ell
        if ell > m:
            return True
        if ell == m:
            return t >= 3 or L >= 12 * W + 2
        return (t + 1) * L > t * (12 * W + 2)

    def m_no_block(n, e, ell, W):               # case II treated as case III
        j, t = odd_part(e)
        m = n - j
        L = 1 << ell
        if ell > m:
            return True
        return (t + 1) * L > t * (12 * W + 3)

    def m_use_e(n, e, ell, W):                  # e in place of its odd part
        j, t = odd_part(e)
        m = n - j
        L = 1 << ell
        if ell > m:
            return True
        if ell == m:
            return t >= 3 or L >= 12 * W + 2
        return (e + 1) * L > e * (12 * W + 3)

    def m_uniform(n, e, ell, W):                # only the uniform length guard
        return (1 << ell) >= 12 * W + 2

    def m_block_free(n, e, ell, W):             # case II declared always admissible
        j, t = odd_part(e)
        m = n - j
        L = 1 << ell
        if ell >= m:
            return True
        return (t + 1) * L > t * (12 * W + 3)

    return {"threshold 12W+2": m_const, "case II merged": m_no_block,
            "odd part replaced by e": m_use_e, "uniform guard only": m_uniform,
            "case II always admissible": m_block_free}


# ------------------------------------------------------------------------ checks
def check_pinned_source():
    """Bind the fidelity cross-check to the exact pinned #6972 file bytes."""
    with open(os.path.join(PKG, "SOURCES.json"), "rb") as f:
        pins = json.load(f)["files"]
    rows = {p["path"]: p for p in pins}
    rel = "research/core-production-nonempty/guard.py"
    need(rel in rows and rows[rel]["usage"] == "input", "guard.py is a declared live input")
    with open(os.path.join(ROOT, rel), "rb") as f:
        data = f.read()
    need(hashlib.sha256(data).hexdigest() == rows[rel]["sha256"], "guard.py bytes match their pin")
    spec = importlib.util.spec_from_file_location("pinned_guard", os.path.join(ROOT, rel))
    mod = importlib.util.module_from_spec(spec)
    sys.modules["pinned_guard"] = mod       # dataclass resolution needs the module registered
    spec.loader.exec_module(mod)
    return mod


def check_oracle_against_cited_formula(guard, smax=22):
    """Fidelity control for the oracle: the literal walk reproduces #6972's closed-form
    longest run on every ordinary window.  This checks our model of M, not their theorem."""
    windows = 0
    for S in range(2, smax + 1):
        for e in range(1, S):
            N = S + e
            sel = literal_selected(S, e)
            for a in range(N):
                for b in range(a + 1, N + 1):
                    want = guard.longest_run(guard.Window(S, e, a, b - a))["maximum"]
                    need(literal_run(sel, a, b - a) == want,
                         "literal run equals the cited formula at S=%d e=%d a=%d b=%d" % (S, e, a, b))
                    windows += 1
    return windows


def check_lemma_holes_and_runs(smax=40):
    """Lemma 1 and Lemma 2 against the literal walk on every S <= smax with S >= 2e."""
    pairs = windows = 0
    for S in range(2, smax + 1):
        for e in range(1, S):
            if S < 2 * e:
                continue
            N = S + e
            sel = literal_selected(S, e)
            lit_holes = [t for t in range(N) if not sel[t]]
            H = hole_positions(N, e)
            need(H == lit_holes, "hole formula at S=%d e=%d" % (S, e))
            cells = {H[i + 1] - H[i] - 1 for i in range(len(H) - 1)}
            need(cells <= {S // e, -(-S // e)}, "cell lengths are floor/ceil of S/e at S=%d e=%d" % (S, e))
            for a in range(N):
                for b in range(a + 1, N + 1):
                    need(run_from_holes(H, a, b - a) == literal_run(sel, a, b - a),
                         "Lemma 2 run at S=%d e=%d a=%d b=%d" % (S, e, a, b))
                    windows += 1
            pairs += 1
    return pairs, windows


def check_periodicity(nmax=12):
    """Lemma P for every e < N, N = 2^n: H_{c+t} = H_c + N/2^j."""
    cases = 0
    for n in range(1, nmax + 1):
        N = 1 << n
        for e in range(1, N):
            j, t = odd_part(e)
            g = N >> j
            H = hole_positions(N, e)
            for c in range(e - t):
                need(H[c + t] == H[c] + g, "periodicity at N=%d e=%d c=%d" % (N, e, c))
            cases += 1
    return cases


def check_literal_aligned(nmax=8):
    """Theorems 1 and 2 against the literal walk: all e and all aligned windows for
    N = 2^n <= 2^nmax, every W allowed by the hypothesis N >= e(6W+2)."""
    cases = bad = 0
    for n in range(1, nmax + 1):
        N = 1 << n
        for e in range(1, N):
            S = N - e
            if N < 8 * e:               # no width W >= 1 satisfies the hypothesis
                continue
            sel = literal_selected(S, e)
            H = hole_positions(N, e)
            for ell in range(0, n + 1):
                L = 1 << ell
                m_al = min(literal_run(sel, a, L) for a in range(0, N, L))
                for W in range(1, (N - 2 * e) // (6 * e) + 1):
                    exact = m_al > 6 * W
                    need(band_prediction(H, L, W) == exact, "band criterion at N=%d e=%d L=%d W=%d" % (N, e, L, W))
                    need(classify(n, e, ell, W) == exact, "classification at N=%d e=%d L=%d W=%d" % (N, e, L, W))
                    cases += 1
                    bad += (not exact)
    return cases, bad


def check_hole_array_aligned(nmin, nmax):
    """Same comparison from the validated hole list, for larger N.  Returns counts,
    including the cases where an aligned length below 12W+2 is exactly admissible."""
    cases = bad = gain = 0
    sharp_by_class = {}
    for n in range(nmin, nmax + 1):
        N = 1 << n
        for e in range(1, N // 8 + 1):
            H = hole_positions(N, e)
            wmax = (N - 2 * e) // (6 * e)
            if wmax < 1:
                continue
            j, t = odd_part(e)
            for ell in range(0, n + 1):
                L = 1 << ell
                m_al = aligned_min_run(H, N, L)
                for W in range(1, wmax + 1):
                    exact = m_al > 6 * W
                    need(band_prediction(H, L, W) == exact, "band criterion at N=%d e=%d L=%d W=%d" % (N, e, L, W))
                    need(classify(n, e, ell, W) == exact, "classification at N=%d e=%d L=%d W=%d" % (N, e, L, W))
                    cases += 1
                    bad += (not exact)
                    if exact and L < 12 * W + 2:
                        gain += 1
                        key = "t=1" if t == 1 else "t>=3"
                        sharp_by_class[key] = sharp_by_class.get(key, 0) + 1
    return cases, bad, gain, sharp_by_class


def check_mutants_rejected(nmax=11):
    """Each wrong closed form must contradict the oracle on at least one case."""
    results = {}
    mutants = classify_mutants()
    for name in mutants:
        results[name] = 0
    for n in range(1, nmax + 1):
        N = 1 << n
        for e in range(1, N // 8 + 1):
            H = hole_positions(N, e)
            wmax = (N - 2 * e) // (6 * e)
            for ell in range(0, n + 1):
                L = 1 << ell
                m_al = aligned_min_run(H, N, L)
                for W in range(1, wmax + 1):
                    exact = m_al > 6 * W
                    for name, fn in mutants.items():
                        if fn(n, e, ell, W) != exact:
                            results[name] += 1
    for name, count in results.items():
        need(count > 0, "mutant '%s' was not rejected" % name)
    # band mutants: lower end off by one in either direction
    for shift in (-1, 1):
        wrong = 0
        for n in range(1, 9):
            N = 1 << n
            for e in range(1, N // 8 + 1):
                H = hole_positions(N, e)
                for ell in range(0, n + 1):
                    L = 1 << ell
                    m_al = aligned_min_run(H, N, L)
                    for W in range(1, (N - 2 * e) // (6 * e) + 1):
                        lo, hi = L - 1 - 6 * W + shift, 6 * W
                        pred = L >= 6 * W + 1 and not any(lo <= h % L <= hi for h in H)
                        if pred != (m_al > 6 * W):
                            wrong += 1
        results["band end shifted by %+d" % shift] = wrong
        need(wrong > 0, "band mutant shift %+d was not rejected" % shift)
    return results


def check_sharpness(wmax=64):
    """Theorem 3: for every W and every dyadic L <= 12W there is a dyadic instance with
    N >= e(6W+2) whose aligned windows of length L are all bad."""
    families = 0
    for W in range(1, wmax + 1):
        ell = 1
        while (1 << ell) <= 12 * W:
            L = 1 << ell
            if L >= 6 * W + 2:
                n = ell + 3                      # e = N / L = 8
                N = 1 << n
                e = N // L
                need(N >= e * (6 * W + 2), "hypothesis holds on the e = N/L family")
                S = N - e
                sel = literal_selected(S, e)
                runs = {literal_run(sel, a, L) for a in range(0, N, L)}
                need(runs == {L // 2}, "every aligned window has longest run L/2 at W=%d L=%d" % (W, L))
                need(L // 2 <= 6 * W, "L/2 <= 6W")
                need(N - L >= W, "complementary gap holds")
            else:                                # L <= 6W + 1, so L <= 6W for a power of two
                need(L <= 6 * W, "L = 6W+1 is odd, hence not a power of two")
                n = max(ell, (6 * W + 2).bit_length())
                N = 1 << n
                e = 1
                need(N >= e * (6 * W + 2), "hypothesis holds for e = 1")
                sel = literal_selected(N - e, e)
                need(max(literal_run(sel, a, L) for a in range(0, N, L)) <= L <= 6 * W,
                     "windows no longer than 6W are bad")
            families += 1
            ell += 1
        # the smallest dyadic length meeting the uniform guard is exactly admissible
        ell = (12 * W + 2 - 1).bit_length()
        need((1 << ell) >= 12 * W + 2 and (1 << (ell - 1)) < 12 * W + 2, "least dyadic L >= 12W+2")
    return families


def check_parity_remark(wmax=200):
    """Neither sharpness family of #6972 is dyadic: L = 12W+1 is odd, N = 18W+5 is odd,
    and N = 18W+6 = 3(6W+2) is divisible by 3."""
    for W in range(1, wmax + 1):
        need((12 * W + 1) % 2 == 1, "family one has odd length")
        need((18 * W + 5) % 2 == 1, "family two has odd period")
        need((18 * W + 6) % 3 == 0, "family one period has factor 3")
    # In a dyadic instance S = e(6W+1)-1 would force N = e(6W+2)-1 odd.
    for n in range(1, 13):
        N = 1 << n
        for e in range(1, N):
            for W in range(1, 40):
                need(N - e != e * (6 * W + 1) - 1, "S = e(6W+1)-1 is never dyadic")
    return wmax


def threshold_table(wmax=6, tmax=15):
    """Least dyadic L (case III) for each W and odd t, beside the uniform guard's dyadic L."""
    header = ["W", "uniform 12W+2"] + ["t=%d" % t for t in range(1, tmax + 1, 2)]
    rows = []
    for W in range(1, wmax + 1):
        row = [W]
        L = 1
        while L < 12 * W + 2:
            L *= 2
        row.append(L)
        for t in range(1, tmax + 1, 2):
            L = 1
            while (t + 1) * L <= t * (12 * W + 3):
                L *= 2
            row.append(L)
        rows.append(row)
    return {"header": header, "rows": rows}


def main():
    cert = {}
    guard = check_pinned_source()
    cert["pinned_guard_bytes"] = True
    cert["oracle_vs_cited_formula_windows"] = check_oracle_against_cited_formula(guard)
    pairs, windows = check_lemma_holes_and_runs()
    cert["lemma_pairs"], cert["lemma_windows"] = pairs, windows
    cert["periodicity_cases"] = check_periodicity()
    cases, bad = check_literal_aligned()
    cert["literal_aligned_cases"], cert["literal_aligned_bad"] = cases, bad
    cases2, bad2, gain, by_class = check_hole_array_aligned(9, 12)
    cert["hole_array_cases"], cert["hole_array_bad"] = cases2, bad2
    cert["gain_cases_below_uniform_length"] = gain
    cert["gain_by_odd_part"] = by_class
    cert["mutant_mismatch_counts"] = check_mutants_rejected()
    cert["sharpness_families"] = check_sharpness()
    cert["parity_remark_W_values"] = check_parity_remark()
    cert["threshold_table"] = threshold_table()
    if "--json" in sys.argv:
        print(json.dumps(cert, indent=1, sort_keys=True))
    else:
        print("oracle agrees with the cited longest-run formula on %d windows" % cert["oracle_vs_cited_formula_windows"])
        print("Lemma 1/2: %d (S,e) pairs, %d windows" % (pairs, windows))
        print("Lemma P periodicity: %d (N,e) cases up to N=4096" % cert["periodicity_cases"])
        print("literal aligned check (N<=256): %d cases, %d bad, band and closed form agree" % (cases, bad))
        print("hole-array aligned check (512<=N<=4096): %d cases, %d bad, band and closed form agree" % (cases2, bad2))
        print("exactly admissible aligned lengths below 12W+2: %d cases %s" % (gain, by_class))
        print("mutants rejected: %s" % cert["mutant_mismatch_counts"])
        print("sharpness families checked: %d" % cert["sharpness_families"])
    print(MARK)


if __name__ == "__main__":
    main()
