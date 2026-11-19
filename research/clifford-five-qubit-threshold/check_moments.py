"""Independent fixed-space census and first two full Gram moments.

Orbit counts use subspace embeddings in finite symplectic and quadratic spaces.
No character table is used to compute the expected counts or trace moments.
Prepared by apoursh with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction
from math import prod
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def injections(ambient, rank):
    """Number of ordered independent rank-tuples in a binary vector space."""
    return prod(2**ambient - 2**i for i in range(rank))


def sp_order(n):
    return 2**(n*n) * prod(4**j - 1 for j in range(1, n+1))


def refinements(n, sign):
    if n == 0:
        return int(sign == 1)
    return 2**(n-1) * (2**n + sign)


def group_order(n, sign):
    return sp_order(n) if sign == 0 else sp_order(n) // refinements(n, sign)


def orbit_count(n, r, sign):
    """Orbits on ordered independent r-tuples, classified by pullback form."""
    total = 0
    for h in range(r//2 + 1):
        t, m = r - 2*h, n - h
        if t > m:
            continue
        # Choose the radical, then choose a nonsingular alternating form on
        # the 2h-dimensional quotient. Only the radical dimension matters.
        choose_radical = injections(r, t) // injections(t, t)
        alternating = choose_radical * (injections(2*h, 2*h) // sp_order(h))
        if sign == 0:
            total += alternating
            continue
        # For a nonzero restriction to the radical, any polar-isotropic
        # t-plane containing a nonsingular vector realizes a nonzero linear
        # restriction. For the zero restriction, the complement must have
        # Witt index at least t. At t=m this forces the complement to be plus.
        nonzero = (2**t - 1) * 4**h
        zero = sum(refinements(h, delta) for delta in (-1, 1)
                   if t < m or delta == sign)
        total += alternating * (zero + nonzero)
    return total


def census(n, sign):
    order = group_order(n, sign)
    counts = [0] * (2*n + 1)
    for r in reversed(range(2*n + 1)):
        known = sum(counts[k] * injections(k, r) for k in range(r+1, 2*n+1))
        counts[r], rem = divmod(order*orbit_count(n, r, sign) - known, injections(r, r))
        require(rem == 0 and counts[r] >= 0, "nonintegral or negative fixed-space count")
    require(sum(counts) == order and counts[-1] == 1, "identity or group order")
    return counts


def small_calibration(n):
    d = 2**n
    labels = range(d*d)
    def polar(x, y):
        return (((x//d) & y).bit_count() + ((y//d) & x).bit_count()) % 2
    def form(x, sign):
        q = ((x//d) & x).bit_count() % 2
        return q if sign == 1 else q ^ polar(1+d, x)
    transvections = [tuple(x ^ (v if polar(x, v) else 0) for x in labels)
                     for v in range(1, d*d)]
    identity = tuple(labels)
    seen, pending = {identity}, [identity]
    counts = {s: Counter() for s in (-1, 0, 1)}
    while pending:
        g = pending.pop()
        fixed = sum(x == y for x, y in enumerate(g))
        require(fixed & (fixed-1) == 0, "fixed vectors form a binary subspace")
        k = fixed.bit_length()-1
        for sign in counts:
            if sign == 0 or all(form(x, sign) == form(y, sign) for x, y in enumerate(g)):
                counts[sign][k] += 1
        for t in transvections:
            product = tuple(t[y] for y in g)
            if product not in seen:
                seen.add(product)
                pending.append(product)
    for sign, histogram in counts.items():
        require([histogram[k] for k in range(2*n+1)] == census(n, sign),
                "literal small group disagrees with the embedding census")


def gram_checks(data):
    n, d = 5, 32
    full = sp_order(n) * d**2
    keys = {0: "S10(2)", 1: "O10+(2).2", -1: "O10-(2).2"}
    counts = {s: census(n, s) for s in keys}
    for s, key in keys.items():
        block = data[key]
        require(block["order"] == sum(counts[s]), "group order from embedding census")
        trivial, = [row for row in block["rows"] if row[0] == 1 and row[1:] == counts[s]]
        require(trivial[0] == 1, "trivial character projection")
    expected_nullity = {13: 6466626860503040, 14: 6954742423552, 15: 0}
    for width in (13, 14, 15):
        power = (width - 1) // 2
        twist = -1 if width in (13, 14) else 1
        mass = nullity = 0
        first = second = Fraction(0)
        for sector in ((1, -1) if width == 14 else (0,)):
            inertia = d if sector == 0 else refinements(n, sector)
            for degree, *projection in data[keys[sector]]["rows"]:
                character_sum = sum(c*(twist*2**power)**k for k,c in enumerate(projection))
                mult, rem = divmod(character_sum, group_order(n, sector))
                require(rem == 0 and mult >= 0, "bad multiplicity in tensor representation")
                irrep = inertia * degree
                weight = irrep**2
                eigenvalue = Fraction(full*mult, d**width * irrep)
                mass += weight
                first += weight*eigenvalue
                second += weight*eigenvalue**2
                if mult == 0:
                    nullity += weight
        # Direct Frobenius norm from trace magnitudes of individual Pauli
        # lifts: 2^(2n-k) lifts with squared trace 2^k above each S.
        direct = Fraction(full, d**(2*width)) * sum(
            size * 2**(2*n-k) * 2**(k*width) for k, size in enumerate(counts[0]))
        require(mass == first == full and second == direct, "Gram moment mismatch")
        require(nullity == expected_nullity[width], "rank classification mismatch")
        print(f"PASS width {width}: rank {full-nullity}, nullity {nullity}, trace and squared trace")


if __name__ == "__main__":
    for qubits in (1, 2):
        small_calibration(qubits)
    print("PASS literal small symplectic and both orthogonal censuses")
    gram_checks(json.loads((Path(__file__).parent / "PROJECTION.json").read_text()))
