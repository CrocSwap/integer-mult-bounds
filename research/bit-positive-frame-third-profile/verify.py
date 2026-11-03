"""Exact checks for the power-of-two exclusion of the profile (0,1,3,3,m).

Standard library only. Every check uses exact integer and F2 arithmetic.
Failures raise SystemExit, so the result does not depend on `assert`, and the
script behaves the same under `python -O`.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import random
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def require(condition: bool, label: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {label}")


# ---------------------------------------------------------------- F2 matrices
# A w-by-w F2 matrix is a tuple of w row bitmasks; bit j of row i is entry (i,j).

def mat_zero(w):
    return tuple(0 for _ in range(w))


def mat_id(w):
    return tuple(1 << i for i in range(w))


def mat_diag(bits, w):
    return tuple((1 << i) if (i < len(bits) and bits[i]) else 0 for i in range(w))


def mat_add(a, b):
    return tuple(x ^ y for x, y in zip(a, b))


def mat_mul(a, b):
    out = []
    for row in a:
        acc = 0
        j = 0
        while row:
            if row & 1:
                acc ^= b[j]
            row >>= 1
            j += 1
        out.append(acc)
    return tuple(out)


def mat_rank(a):
    rows = [r for r in a if r]
    rank = 0
    while rows:
        pivot = rows.pop()
        if not pivot:
            continue
        rank += 1
        low = pivot & -pivot
        rows = [r ^ pivot if r & low else r for r in rows]
        rows = [r for r in rows if r]
    return rank


def outer(x, y, w):
    """x y^T for column bitmask x and row bitmask y."""
    return tuple(y if (x >> i) & 1 else 0 for i in range(w))


def rank_one_idempotents(w):
    out = []
    for x in range(1, 1 << w):
        for y in range(1, 1 << w):
            if bin(x & y).count("1") % 2 == 1:
                out.append(outer(x, y, w))
    return out


# ------------------------------------------------- the lattice and its labels
# Lambda = Z R + Z B + Z P with R = A/m.  Exponents are integer triples in the
# basis (R, B, P).  Then A = m R and Q = A + B - P = m R + B - P.

def labels(m):
    return {
        "R": (1, 0, 0),
        "A": (m, 0, 0),
        "B": (0, 1, 0),
        "P": (0, 0, 1),
        "Q": (m, 1, -1),
    }


def vadd(*vs):
    return tuple(sum(c) for c in zip(*vs))


def target_exponents(m):
    lab = labels(m)
    return [vadd(lab["A"], lab["P"]), vadd(lab["A"], lab["Q"]),
            vadd(lab["B"], lab["P"]), vadd(lab["B"], lab["Q"])]


# ------------------------------------- exact matrices over the group algebra
# An element of M_w(F2[Lambda]) is a dict {exponent: nonzero F2 matrix}.

def ga_mul(x, y, w):
    out = {}
    for ex, mx in x.items():
        for ey, my in y.items():
            e = vadd(ex, ey)
            prod = mat_mul(mx, my)
            cur = mat_add(out.get(e, mat_zero(w)), prod)
            if any(cur):
                out[e] = cur
            else:
                out.pop(e, None)
    return out


def ga_call(exp, n, w):
    """D_N(F) = (I - N) + [F] N."""
    zero = (0, 0, 0)
    out = {}
    comp = mat_add(mat_id(w), n)
    if exp == zero:
        tot = mat_add(comp, n)
        return {zero: tot}
    if any(comp):
        out[zero] = comp
    out[exp] = n
    return out


def ga_word(calls, w):
    acc = {(0, 0, 0): mat_id(w)}
    for exp, n in calls:
        acc = ga_mul(acc, ga_call(exp, n, w), w)
    return acc


def ga_target(m, w):
    out = {}
    for i, e in enumerate(target_exponents(m)):
        out[e] = mat_add(out.get(e, mat_zero(w)), mat_diag([j == i for j in range(4)], w))
    if w > 4:
        rest = tuple((1 << i) if i >= 4 else 0 for i in range(w))
        out[(0, 0, 0)] = mat_add(out.get((0, 0, 0), mat_zero(w)), rest)
    return {e: v for e, v in out.items() if any(v)}


# -------------------------------- truncated specializations [lambda] -> (1+s)^psi
# Polynomial matrices over F2[s]/(s^K) are lists of K F2 matrices.

def binom_mod2(n, k):
    """Coefficient of s^k in (1+s)^n over F2, for every integer n."""
    if k < 0:
        return 0
    if n >= 0:
        return 1 if (k & ~n) == 0 and k <= n else 0
    # (1+s)^(-1) = sum s^j; (1+s)^n for n<0 equals C(n,k) = (-1)^k C(k-n-1,k).
    top = k - n - 1
    return 1 if (k & ~top) == 0 else 0


def unit_power(n, order):
    return [binom_mod2(n, k) for k in range(order)]


def poly_mul(x, y, w, order):
    out = [mat_zero(w) for _ in range(order)]
    for i, a in enumerate(x):
        if not any(a):
            continue
        for j in range(order - i):
            b = y[j]
            if any(b):
                out[i + j] = mat_add(out[i + j], mat_mul(a, b))
    return out


def poly_call(psi_value, n, w, order):
    coeffs = unit_power(psi_value, order)
    out = [mat_zero(w) for _ in range(order)]
    out[0] = mat_id(w)
    # I + ((1+s)^psi - 1) N
    for k in range(order):
        c = coeffs[k] ^ (1 if k == 0 else 0)
        if c:
            out[k] = mat_add(out[k], n)
    return out


def specialize_word(calls, psi, w, order):
    acc = [mat_id(w)] + [mat_zero(w) for _ in range(order - 1)]
    for exp, n in calls:
        value = sum(p * e for p, e in zip(psi, exp))
        acc = poly_mul(acc, poly_call(value, n, w, order), w, order)
    return acc


def specialize_ga(element, psi, w, order):
    out = [mat_zero(w) for _ in range(order)]
    for exp, mtx in element.items():
        value = sum(p * e for p, e in zip(psi, exp))
        for k, c in enumerate(unit_power(value, order)):
            if c:
                out[k] = mat_add(out[k], mtx)
    return out


PSI_R = (1, 0, 0)   # [R] -> 1+s, [B] -> 1, [P] -> 1
CHI_B = (0, 1, 0)   # [B] -> 1+eps, [R] -> 1, [P] -> 1


def ordered_product(mats, w):
    acc = mat_id(w)
    for x in mats:
        acc = mat_mul(acc, x)
    return acc


# ----------------------------------------------------------------- checks

def check_sources():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text())
    for row in sources["files"]:
        if row["usage"] != "input":
            continue
        data = (ROOT / row["path"]).read_bytes()
        require(hashlib.sha256(data).hexdigest() == row["sha256"], f"source hash {row['path']}")
    return sum(1 for r in sources["files"] if r["usage"] == "input")


def check_lattice(powers):
    for m in powers:
        lab = labels(m)
        # A + B = P + Q = I, and the determinant balance of the profile (0,1,3,3,m).
        require(vadd(lab["A"], lab["B"]) == vadd(lab["P"], lab["Q"]), f"A+B=P+Q m={m}")
        total = vadd(*([lab["B"]] + [lab["P"]] * 3 + [lab["Q"]] * 3 + [lab["R"]] * m))
        require(total == vadd(*target_exponents(m)), f"determinant balance m={m}")
        # psi_R values of the target exponents are (m, 2m, 0, m).
        vals = [sum(p * e for p, e in zip(PSI_R, t)) for t in target_exponents(m)]
        require(vals == [m, 2 * m, 0, m], f"psi_R target values m={m}")
        require(sum(p * e for p, e in zip(PSI_R, lab["Q"])) == m, f"psi_R(Q) m={m}")
        # (1+s)^m = 1 + s^m and (1+s)^(2m) = 1 modulo s^(m+1) when m is a power of two.
        require(unit_power(m, m + 1) == [1] + [0] * (m - 1) + [1], f"(1+s)^m m={m}")
        require(unit_power(2 * m, m + 1) == [1] + [0] * m, f"(1+s)^2m m={m}")
        # chi_B values: target (0,1,1,2), Q -> 1, R and P -> 0.
        vals = [sum(p * e for p, e in zip(CHI_B, t)) for t in target_exponents(m)]
        require(vals == [0, 1, 1, 2], f"chi_B target values m={m}")
        require([sum(p * e for p, e in zip(CHI_B, lab[k])) for k in "RBPQ"] == [0, 1, 0, 1],
                f"chi_B labels m={m}")
    return len(powers)


def random_profile_word(m, w, rng, idem):
    lab = labels(m)
    names = ["B"] + ["P"] * 3 + ["Q"] * 3 + ["R"] * m
    rng.shuffle(names)
    return [(name, lab[name], rng.choice(idem)) for name in names]


def check_lemma(rng, idem_by_w, trials):
    """The two coefficient identities behind the theorem, on random words."""
    count = 0
    for w, idem in idem_by_w.items():
        for m in (1, 2, 4, 8):
            for _ in range(trials):
                word = random_profile_word(m, w, rng, idem)
                calls = [(e, n) for _, e, n in word]
                img = specialize_word(calls, PSI_R, w, m + 1)
                es = [n for name, _, n in word if name == "R"]
                nq = [n for name, _, n in word if name == "Q"]
                sum_q = mat_zero(w)
                for x in nq:
                    sum_q = mat_add(sum_q, x)
                for j in range(1, m):
                    ej = mat_zero(w)
                    for sub in itertools.combinations(range(m), j):
                        ej = mat_add(ej, ordered_product([es[i] for i in sub], w))
                    require(img[j] == ej, f"order-{j} coefficient is e_{j}(E), m={m}, w={w}")
                expected = mat_add(ordered_product(es, w), sum_q)
                require(img[m] == expected, f"order-m coefficient, m={m}, w={w}")
                eps = specialize_word(calls, CHI_B, w, 2)
                nb = [n for name, _, n in word if name == "B"][0]
                require(eps[1] == mat_add(nb, sum_q), f"chi_B first order, m={m}, w={w}")
                count += 1
    return count


def check_homomorphism(rng, idem):
    """Specializing the exact group-algebra product equals the specialized product."""
    w = 4
    count = 0
    for m in (1, 2, 4):
        for _ in range(6):
            word = random_profile_word(m, w, rng, idem)
            calls = [(e, n) for _, e, n in word]
            exact = ga_word(calls, w)
            for psi, order in ((PSI_R, m + 1), (CHI_B, 2), ((1, 1, 1), 4), ((0, 0, 1), 3)):
                require(specialize_ga(exact, psi, w, order) == specialize_word(calls, psi, w, order),
                        f"specialization is a homomorphism, m={m}")
                count += 1
    return count


def subdivision_word(m, w, both):
    """#6089's subdivision words with R = A/m on coordinate projectors."""
    lab = labels(m)
    e = [mat_diag([j == i for j in range(4)], w) for i in range(4)]
    calls = []
    calls += [(lab["R"], e[0])] * m
    calls += [(lab["P"], e[0])]
    if both:
        calls += [(lab["R"], e[1])] * m
    else:
        calls += [(lab["A"], e[1])]
    calls += [(lab["Q"], e[1])]
    calls += [(lab["B"], e[2]), (lab["P"], e[2]), (lab["B"], e[3]), (lab["Q"], e[3])]
    return calls


def check_controls():
    """Attained profiles pass the same two identities; only B-count 1 breaks the rank step."""
    out = 0
    for w in (4, 5):
        for m in (1, 2, 4):
            for both in (False, True):
                calls = subdivision_word(m, w, both)
                require(ga_word(calls, w) == ga_target(m, w), f"subdivision word exact m={m} w={w}")
                img = specialize_word(calls, PSI_R, w, m + 1)
                require(img == specialize_ga(ga_target(m, w), PSI_R, w, m + 1),
                        f"psi_R control m={m} w={w}")
                require(img[m] == mat_diag([1, 0, 0, 1], w), f"psi_R order-m control m={m} w={w}")
                eps = specialize_word(calls, CHI_B, w, 2)
                require(eps[1] == mat_diag([0, 1, 1, 0], w), f"chi_B control m={m} w={w}")
                out += 1
    # A mutated control must fail exactness.
    calls = subdivision_word(2, 4, False)
    calls[0] = (labels(2)["P"], calls[0][1])
    require(ga_word(calls, 4) != ga_target(2, 4), "mutated label rejected")
    return out


def check_rank_step():
    """Exhaustive at w = 4, 5: D_w is never N + X with N rank one and rank X <= 1."""
    out = 0
    for w in (4, 5):
        d = mat_diag([1, 1, 1, 1], w)
        rank_le_one = {mat_zero(w)}
        for x in range(1, 1 << w):
            for y in range(1, 1 << w):
                rank_le_one.add(outer(x, y, w))
        for x in rank_le_one:
            require(mat_rank(mat_add(d, x)) >= 3, f"rank(D_w + X) >= 3, w={w}")
            out += 1
    return out


def main():
    rng = random.Random(6089)
    n_sources = check_sources()
    powers = [2 ** k for k in range(0, 11)]
    n_lattice = check_lattice(powers)
    idem_by_w = {4: rank_one_idempotents(4), 5: rank_one_idempotents(5)}
    require(len(idem_by_w[4]) == 120 and len(idem_by_w[5]) == 496, "rank-one idempotent counts")
    n_lemma = check_lemma(rng, idem_by_w, 200)
    n_hom = check_homomorphism(rng, idem_by_w[4])
    n_ctrl = check_controls()
    n_rank = check_rank_step()
    print(json.dumps({
        "source_inputs": n_sources,
        "powers_of_two_checked": n_lattice,
        "random_lemma_words": n_lemma,
        "homomorphism_checks": n_hom,
        "attained_profile_controls": n_ctrl,
        "rank_step_cases": n_rank,
    }, sort_keys=True))
    print("PASS_POSITIVE_FRAME_THIRD_PROFILE_POWERS_OF_TWO")


if __name__ == "__main__":
    main()
