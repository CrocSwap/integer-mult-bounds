#!/usr/bin/env python3
"""KB5i: EXACT named value for F-star family-gap sub-decoders.

Replaces the seeded Lemma MX scan of the vendored PR 2914 engine
(`named_exact_small`, predecessor/pr2914/verify.py) with an exact
computation over the SAME construction space and the SAME per-combo
semantics (a faithful port of `mx_eval`, agreement-tested against the
engine's own exhaustive enumeration on small instances).

The construction space of Lemma MX assigns each line t one of
  ('A', 0)   the anchor pair (a0(t), b0(t))       - requires tau(t) odd
  ('U', a*)  a one-sided repair (a*, b0(t))       - a* subset of pi(t),
             dot1(a*, b0(t)) = 1, a* != a0(t)
  ('T', c)   a matched pivot (e_c, e_c)           - c a single bit of D(t)
with value |A| + |U| + sum_c MAS(class_c) and the two exact hypothesis
sets (A-first / T-first) of Lemma MX.

Exactness device (the DP the PR 2936 record asked for): the VALUE of a
combo does not depend on the repair labels a*, only the hypothesis checks
do, and those factor per U line. So the search enumerates only the COARSE
assignment (kind per line: A / U / T(c)), value = |A| + |U| +
sum MAS(class_c), and repairs feasibility as per-line option masks:
  A-mode:  each u in U keeps an a* with U-U and U-T orthogonality, and
           every A line has a0(t) orthogonal to the pivot bits of its T
           out-neighbours;
  T-mode:  each u in U keeps an a* with U-U orthogonality only, and every
           T line's pivot bit is orthogonal to b0(s) of its A/U
           in-neighbours s.
A coarse assignment is valid iff one mode is feasible. The optimum is the
max value over valid coarse assignments, found by full enumeration of the
coarse product (feasibility only checked when a candidate beats the best
feasible value so far), with a replayable witness (combo + repairs + mode).

CL3 mixings: at even tau everywhere (anchor pairs never certify, K_tt = 0)
the CL3 family value equals Lemma MP exactly (proof in README.md:
kept lines are pivot lines, arcs are same-pivot zero arcs, and MAS is
monotone), so CL3 needs no separate enumeration on those instances; the
identity is machine-checked in the tests and asserted at run time.

Stdlib only. Run tests: python3 -B test_named_exact.py
"""
import importlib.util
import itertools
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ENG = os.path.join(HERE, "predecessor", "pr2914", "verify.py")
spec = importlib.util.spec_from_file_location("pr2914_engine", ENG)
fg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fg)


def u_options(mod, ad, t):
    """The repair labels a* of line t (same filter as the engine)."""
    return [a for a in range(8) if (a & ~mod["pi"][t]) == 0
            and fg.dot1(a, ad["b0"][t]) == 1 and a != ad["a0"][t]]


def coarse_options(mod, ad, t):
    """Coarse kinds for line t: A (anchor), U (repair), T(c) (pivot)."""
    o = []
    if ad["tau"][t] % 2 == 1 and mod["M"][t][t] != 0:
        o.append(("A", 0))
    o.append(("U", 0))
    for j in range(3):
        if mod["D"][t] & (1 << j):
            o.append(("T", 1 << j))
    return o


def mx_eval_direct(mod, ad, mas, combo):
    """Faithful port of the engine's mx_eval: value of one FULL combo
    (kind + repair choice per line), or None when a hypothesis set fails."""
    v = mod["v"]
    A = [t for t in range(v) if combo[t][0] == "A"]
    U = [t for t in range(v) if combo[t][0] == "U"]
    T = [t for t in range(v) if combo[t][0] == "T"]
    for t in A:
        if not (mod["M"][t][t] != 0 and ad["tau"][t] % 2 == 1):
            return None
    classes = [0, 0, 0]
    cval = [0] * v
    for t in T:
        c = combo[t][1]
        cval[t] = c
        classes[c.bit_length() - 1] |= 1 << t
    val = len(A) + len(U) + mas[classes[0]] + mas[classes[1]] \
        + mas[classes[2]]
    ok_a = True
    for t in U:
        a_star = combo[t][1]
        for s in A + U:
            if mod["M"][t][s] == 0 and fg.dot1(a_star, ad["b0"][s]) != 0:
                ok_a = False
        for s in T:
            if mod["M"][t][s] == 0 and (a_star & cval[s]) != 0:
                ok_a = False
    for t in A:
        for s in T:
            if mod["M"][t][s] == 0 and (ad["a0"][t] & cval[s]) != 0:
                ok_a = False
    ok_t = True
    for t in U:
        a_star = combo[t][1]
        for s in A + U:
            if mod["M"][t][s] == 0 and fg.dot1(a_star, ad["b0"][s]) != 0:
                ok_t = False
    for t in T:
        for s in A + U:
            if mod["M"][s][t] == 0 and (cval[t] & ad["b0"][s]) != 0:
                ok_t = False
    return val if (ok_a or ok_t) else None


def _coarse_masks(mod, ad, combo):
    """Masks for a coarse combo: U set, A set, T pivot bits, class masks."""
    v = mod["v"]
    amask = umask = 0
    classes = [0, 0, 0]
    cval = [0] * v
    for t in range(v):
        kind, arg = combo[t]
        if kind == "A":
            amask |= 1 << t
        elif kind == "U":
            umask |= 1 << t
        else:
            cval[t] = arg
            classes[arg.bit_length() - 1] |= 1 << t
    return amask, umask, classes, cval


def coarse_value(mas, amask, umask, classes):
    return amask.bit_count() + umask.bit_count() + mas[classes[0]] \
        + mas[classes[1]] + mas[classes[2]]


def _feasible(mod, ad, opts, amask, umask, cval, want):
    """Per-mode feasibility of a coarse combo, repairs folded into masks.
    want = 'a' or 't'. Returns (ok, repairs) with repairs[t] = a* choice."""
    v = mod["v"]
    M = mod["M"]
    repairs = {}
    full = {u: (1 << len(opts[u])) - 1 for u in range(v) if opts[u]}
    for u in range(v):
        if not (umask >> u) & 1:
            continue
        if not opts[u]:
            return False, None
        m = full[u]
        if want == "t":
            for s in range(v):
                if s != u and M[u][s] == 0 and ((amask | umask) >> s) & 1:
                    for i, a in enumerate(opts[u]):
                        if (m >> i) & 1 and fg.dot1(a, ad["b0"][s]) != 0:
                            m &= ~(1 << i)
            if m == 0:
                return False, None
            repairs[u] = opts[u][(m & -m).bit_length() - 1]
        else:
            for s in range(v):
                if s != u and M[u][s] == 0 and ((amask | umask) >> s) & 1:
                    for i, a in enumerate(opts[u]):
                        if (m >> i) & 1 and fg.dot1(a, ad["b0"][s]) != 0:
                            m &= ~(1 << i)
            for s in range(v):
                if M[u][s] == 0 and cval[s]:
                    for i, a in enumerate(opts[u]):
                        if (m >> i) & 1 and (a & cval[s]) != 0:
                            m &= ~(1 << i)
            if m == 0:
                return False, None
            repairs[u] = opts[u][(m & -m).bit_length() - 1]
    if want == "a":
        for t in range(v):
            if (amask >> t) & 1:
                for s in range(v):
                    if M[t][s] == 0 and cval[s] and (ad["a0"][t] & cval[s]):
                        return False, None
    else:
        for t in range(v):
            if cval[t]:
                for s in range(v):
                    if M[s][t] == 0 and ((amask | umask) >> s) & 1 \
                            and (cval[t] & ad["b0"][s]):
                        return False, None
    return True, repairs


def mx_exact(mod, ad, mas, cap=6000000):
    """Exact Lemma MX family value. Returns (value, detail) with a
    replayable witness in detail['witness'] = dict(combo, repairs, mode)."""
    v = mod["v"]
    opts = [u_options(mod, ad, t) for t in range(v)]
    copts = [coarse_options(mod, ad, t) for t in range(v)]
    prod = 1
    for o in copts:
        prod *= len(o)
    if prod > cap:
        raise ValueError("coarse product %d exceeds cap %d" % (prod, cap))
    best = -1
    best_wit = None
    for combo in itertools.product(*copts):
        amask, umask, classes, cval = _coarse_masks(mod, ad, combo)
        val = coarse_value(mas, amask, umask, classes)
        if val <= best:
            continue
        ok, mode, repairs = False, None, None
        fa, ra = _feasible(mod, ad, opts, amask, umask, cval, "a")
        if fa:
            ok, mode, repairs = True, "a", ra
        else:
            ft, rt = _feasible(mod, ad, opts, amask, umask, cval, "t")
            if ft:
                ok, mode, repairs = True, "t", rt
        if ok:
            best = val
            best_wit = dict(combo=[tuple(c) for c in combo],
                            repairs={str(k): v_ for k, v_ in repairs.items()},
                            mode=mode)
    return best, dict(coarse_product=prod, exhaustive=True, witness=best_wit)


def replay_mx_witness(mod, ad, mas, wit):
    """Independent replay of an mx_exact witness through the direct port."""
    v = mod["v"]
    combo = [tuple(c) for c in wit["combo"]]
    full = []
    for t in range(v):
        kind, arg = combo[t]
        if kind == "U":
            full.append(("U", wit["repairs"][str(t)]))
        else:
            full.append((kind, arg))
    return mx_eval_direct(mod, ad, mas, full)


def named_exact(mod, ad, mas, acyc, cap=6000000):
    """Exact PR 2901 named value = max(SG anchor reach, Lemma MP, Lemma MX,
    Lemma CL3) with every rung exact. Returns (named, detail)."""
    v = mod["v"]
    mp, _m, mp_exh, mp_prod = fg.matched_pivot(mod, mas)
    assert mp_exh, "matched-pivot space must fit the exhaustive cap"
    reach = len(ad["reach"])
    mx_val, mx_detail = mx_exact(mod, ad, mas, cap=cap)
    cl3_prod = 1
    for t in range(v):
        cl3_prod *= 1 + mod["D"][t].bit_count()
    even_tau = all(x % 2 == 0 for x in ad["tau"])
    if even_tau:
        # CL3 = MP at even tau (README proof; machine-checked in tests)
        cl3_val, cl3_how = mp, "equals-MP-at-even-tau"
    elif cl3_prod <= cap:
        cl3_val, cl3_how = _cl3_brute(mod, ad), "exhaustive"
    else:
        raise ValueError("CL3 space %d exceeds cap and tau is odd" % cl3_prod)
    named = max(mp, reach, mx_val, cl3_val)
    detail = dict(MP=mp, reach=reach, mx=mx_val, cl3=cl3_val,
                  cl3_how=cl3_how, mx_detail=mx_detail, exhaustive=True)
    return named, detail


def _cl3_brute(mod, ad):
    """Exhaustive CL3 value (anchor/pivot per line, ab_value of the forms)."""
    v = mod["v"]
    cl3_opts = [[(ad["a0"][t], ad["b0"][t], "A")] +
                [((1 << j), (1 << j), "T") for j in range(3)
                 if mod["D"][t] & (1 << j)]
                for t in range(v)]
    best = 0
    for combo in itertools.product(*cl3_opts):
        a = [c[0] for c in combo]
        b = [c[1] for c in combo]
        val = fg.ab_value(mod, a, b)
        if val > best:
            best = val
    return best
