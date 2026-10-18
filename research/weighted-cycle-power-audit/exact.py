"""Exact cycle admission and a real cyclic resolvent. Python standard library.

Prepared for William Lawyer with substantial OpenAI Codex assistance.
Apache-2.0. No predecessor implementation is imported.
"""

from fractions import Fraction as F


def power_certificate(permutation, weights):
    """Return exact squared power bound, or reject a nonunit cycle product.

    (W x)[i] = weights[i] * x[permutation[i]]. A weight is a pair of
    rational real/imaginary parts. None for K2 means powers over Z are
    unbounded; invalid permutations and zero weights raise ValueError.
    """
    n = len(permutation)
    if n == 0 or sorted(permutation) != list(range(n)) or len(weights) != n:
        raise ValueError("need a nonempty permutation and one weight per row")
    magnitudes2 = [F(re) ** 2 + F(im) ** 2 for re, im in weights]
    if any(q == 0 for q in magnitudes2):
        raise ValueError("integer powers require nonzero weights")
    seen = set()
    cycles = []
    for start in range(n):
        if start in seen:
            continue
        indices, prefixes = [], [F(1)]
        i = start
        while i not in seen:
            seen.add(i)
            indices.append(i)
            prefixes.append(prefixes[-1] * magnitudes2[i])
            i = permutation[i]
        product2 = prefixes.pop()
        cycles.append({
            "indices": indices,
            "product2": product2,
            "K2": max(prefixes) / min(prefixes) if product2 == 1 else None,
        })
    bounded = all(c["product2"] == 1 for c in cycles)
    return {"cycles": cycles,
            "K2": max(c["K2"] for c in cycles) if bounded else None}


def cyclic_solve(a, weights, rhs):
    """Solve a*x[i] - weights[i]*x[i-1] = rhs[i], exactly over Q.

    Affine elimination around the cycle; no matrix inverse/geometric sum.
    """
    a = F(a)
    if a == 0 or not weights or len(weights) != len(rhs):
        raise ValueError("need a nonzero diagonal and matching nonempty vectors")
    alpha, beta = F(1), F(0)
    for w, value in zip(weights, rhs):
        alpha, beta = F(w) * alpha / a, (F(w) * beta + F(value)) / a
    if alpha == 1:
        raise ValueError("singular cycle")
    last = beta / (1 - alpha)
    x = []
    for w, value in zip(weights, rhs):
        last = (F(w) * last + F(value)) / a
        x.append(last)
    return x


def perturbation_bound(coefficients, eta, inverse_bound):
    """Sufficient Neumann guard; coefficients are nonnegative |p_j| bounds.

    Return E and B/(1-BE), or None when the strict sufficient guard fails.
    Failure of the guard makes no assertion of singularity.
    The caller must independently certify eta and B for the actual U and P;
    this arithmetic helper does not establish either input premise.
    """
    eta, inverse_bound = F(eta), F(inverse_bound)
    coefficients = [F(c) for c in coefficients]
    if eta < 0 or inverse_bound <= 0 or any(c < 0 for c in coefficients):
        raise ValueError("need eta >= 0, B > 0, and absolute coefficient bounds")
    error = sum((c * ((1 + eta) ** j - 1)
                 for j, c in enumerate(coefficients)), F(0))
    return error, (inverse_bound / (1 - inverse_bound * error)
                   if inverse_bound * error < 1 else None)


def balanced_fixture(eta, half_length, delta=None):
    eta = F(eta)
    delta = eta / 2 if delta is None else F(delta)
    if not 0 < eta < 1 or half_length < 1 or delta <= 0:
        raise ValueError("need 0 < eta < 1, delta > 0, and positive half length")
    b, a = 1 + eta, 1 + delta
    weights = [b] * half_length + [1 / b] * half_length
    return a, weights


def geometric(t, count):
    """Closed scalar finite geometric sum, including t=1."""
    t = F(t)
    return F(count) if t == 1 else (t ** count - 1) / (t - 1)


def balanced_row_formula(a, b, half_length):
    """Resolvent row at the end of the high-weight block."""
    q, r = b / a, 1 / (a * b)
    return ((geometric(q, half_length)
             + q ** half_length * geometric(r, half_length))
            / (a * (1 - a ** (-2 * half_length))))


def first_exceedance(q, target):
    """Smallest positive m with q**m > target, exact bracketing/bisection."""
    q, target = F(q), F(target)
    if q <= 1 or target < 1:
        raise ValueError("need q > 1 and target >= 1")
    lo, hi = 0, 1
    while q ** hi <= target:
        lo, hi = hi, 2 * hi
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if q ** mid > target:
            hi = mid
        else:
            lo = mid
    return hi


def sharp_local_cap(length, lower, upper):
    """Largest possible K for a balanced length-L cycle in [lower,upper].

    Returns the rational cap and an attaining real-weight cycle. This is an
    extremal consequence of the proof, not a search over possible weights.
    """
    lower, upper = F(lower), F(upper)
    if length < 1 or not 0 < lower <= 1 <= upper:
        raise ValueError("need L >= 1 and 0 < lower <= 1 <= upper")
    candidates = [min(upper ** r, lower ** (-(length - r)))
                  for r in range(length + 1)]
    cap = max(candidates)
    r = candidates.index(cap)

    def factor(target, count, ceiling):
        factors = []
        for _ in range(count):
            value = min(target, ceiling)
            factors.append(value)
            target /= value
        if target != 1:
            raise ArithmeticError("cap factorization failed")
        return factors

    weights = factor(cap, r, upper)
    weights += [1 / x for x in factor(cap, length - r, 1 / lower)]
    return cap, weights


def sharp_inverse_bound(a, length, lower, upper):
    """Sharp infinity norm for aI-W over balanced cycles in [lower,upper].

    a > 1 is real. The attaining weights use sigma(i)=i+1 mod length.
    Every prefix simultaneously attains the path-product envelope.
    """
    a, lower, upper = F(a), F(lower), F(upper)
    if a <= 1 or length < 1 or not 0 < lower <= 1 <= upper:
        raise ValueError("need a > 1, L >= 1, and 0 < lower <= 1 <= upper")
    envelope = [min(upper ** j, lower ** (j - length))
                for j in range(length + 1)]
    weights = [envelope[j + 1] / envelope[j] for j in range(length)]
    bound = sum((envelope[j] / a ** (j + 1) for j in range(length)), F(0))
    return bound / (1 - a ** -length), weights
