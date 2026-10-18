"""Exact constant-row shear family for the historical complex center.

Apache-2.0. Ross Richardson, with substantial OpenAI Codex assistance.
The original factor and cost convention are Douglas R. Colkitt's work.
"""
from collections import Counter
from fractions import Fraction
from itertools import combinations
from math import comb


def require(ok, message):
    if not ok:
        raise ValueError(message)


def choose(n, k):
    return comb(n, k) if 0 <= k <= n else 0


def factor(h, pivot, anchor):
    require(type(h) is int and h >= 8 and h % 2 == 0, "even h >= 8 required")
    require(type(pivot) is int and 0 <= pivot < h, "invalid pivot")
    require(all(type(i) is int and 0 <= i < h and i != pivot for i in anchor),
            "invalid anchor coordinate")
    require(len(set(anchor)) == len(anchor), "duplicate anchor coordinate")
    b = set(anchor)
    triples = list(combinations(range(h), 3))
    gather, scatter = [], []
    for triple in triples:
        s = set(triple)
        sp = int(pivot in s)
        gather.append(tuple(1 if i == pivot else int(i in s) - int(i in b)
                            for i in range(h)))
        scatter.append(tuple((3-len(b))*sp + len(s & b)-1 if i == pivot
                             else int(i in s)-sp for i in range(h)))
    return {"h": h, "pivot": pivot, "anchor": sorted(b), "triples": triples,
            "gather": gather, "scatter": scatter}


def classify_integral_anchor(h, pivot, offsets):
    """V_i=t_i-b_i is in {0,+1,-1} for both t_i values iff b_i in {0,1}."""
    require(type(h) is int and h >= 8 and h % 2 == 0, "even h >= 8 required")
    require(type(pivot) is int and 0 <= pivot < h, "invalid pivot")
    require(len(offsets) == h and offsets[pivot] == 0, "invalid anchor shape")
    require(all(type(b) is int for b in offsets), "integral anchor required")
    require(all(b in (0, 1) for b in offsets), "gather alphabet exceeded")
    return tuple(i for i, b in enumerate(offsets) if b)


def histograms(f):
    return (Counter(x for row in f["gather"] for x in row),
            Counter(x for row in f["scatter"] for x in row))


def literal_price(f, original_alphabet=False):
    v, u = histograms(f)
    require(set(v) <= {-1, 0, 1}, "gather alphabet exceeded")
    allowed = {-1, 0, 1, 2} if original_alphabet else {-2, -1, 0, 1, 2}
    require(set(u) <= allowed, "scatter alphabet exceeded")
    return {"G": v[-1]+v[1], "H": 2*(u[-1]+u[1])+u[-2]+u[2]}


def orbit(h, k):
    """Exact subset-count formula; never price an out-of-alphabet numerator."""
    require(type(h) is int and h >= 8 and h % 2 == 0, "even h >= 8 required")
    require(type(k) is int and 0 <= k < h, "invalid anchor cardinality")
    u0 = Counter()
    for sp in (0, 1):
        for j in range(4-sp):
            multiplicity = choose(k, j)*choose(h-1-k, 3-sp-j)
            if multiplicity:
                u0[(3-k)*sp+j-1] += multiplicity
    n, d, e = choose(h, 3), choose(h-1, 2), choose(h-2, 2)
    require(sum(u0.values()) == n, "orbit multiplicity incomplete")
    g = n+(h-1)*d+k*(n-2*d)
    admissible = set(u0) <= {-2, -1, 0, 1, 2}
    hp = None
    if admissible:
        hp = 4*(h-1)*e + sum(m*(0 if w == 0 else 1 if abs(w) == 2 else 2)
                              for w, m in u0.items())
    return {"k": k, "anchors": choose(h-1, k), "G": g, "H": hp,
            "G_plus_H": g+hp if hp is not None else None,
            "admissible": admissible, "original_alphabet": set(u0) <= {-1, 0, 1, 2},
            "pivot_numerators": {str(w): m for w, m in sorted(u0.items())}}


def affine_identity(f):
    """Check U V = intersection-1 modulo sum(t_i)=3, as affine forms.

    This checks coefficients, not sampled triple pairs. The written proof
    explains why the one relation suffices for every triple input.
    """
    h, p, b = f["h"], f["pivot"], set(f["anchor"])
    triples = list(combinations(range(h), 3))
    require(f["triples"] == triples and len(f["gather"]) == len(f["scatter"]) == len(triples),
            "incomplete factor dimensions")
    require(all(len(row) == h and all(type(a) is int for a in row)
                for rows in (f["gather"], f["scatter"]) for row in rows),
            "invalid factor row")
    for triple, u in zip(f["triples"], f["scatter"]):
        s = set(triple)
        constant = u[p]-sum(u[i] for i in b)
        coefficients = [0 if i == p else u[i] for i in range(h)]
        delta = [coefficients[i]-int(i in s) for i in range(h)]
        require(len(set(delta)) == 1 and constant+1 == -3*delta[0],
                "central affine identity failed")
    # Bind the actually supplied V to the affine forms used above.
    for triple, v in zip(f["triples"], f["gather"]):
        require(v == tuple(1 if i == p else int(i in triple)-int(i in b)
                           for i in range(h)), "gather form mismatch")
    return len(f["triples"])


def central_replay(f, inverse=False, omit=None, billed=None):
    """Literal exact replay on independent source, target and dirty-center rows."""
    n, h = len(f["triples"]), f["h"]
    x = [{i: Fraction(1)} for i in range(n)]
    y = [{n+i: Fraction(1)} for i in range(n)]
    c = [{2*n+i: Fraction(1)} for i in range(h)]
    paid = 0

    def add(target, source, scale):
        for i, a in source.items():
            target[i] = target.get(i, 0)+scale*a
            if not target[i]:
                del target[i]

    def gather(sign):
        nonlocal paid
        for i, row in enumerate(f["gather"]):
            for j, a in enumerate(row):
                if a:
                    require(abs(a) == 1, "unpriced gather coefficient")
                    paid += 1
                    add(c[j], x[i], sign*a)

    def scatter(sign):
        nonlocal paid
        for i, row in enumerate(f["scatter"]):
            for j, a in enumerate(row):
                if a:
                    require(abs(a) in (1, 2), "unpriced scatter coefficient")
                    paid += 2 if abs(a) == 1 else 1
                    add(y[i], c[j], Fraction(sign*a, 2))

    ops = [("compensate", scatter, -1), ("prepare", gather, 1),
           ("deliver", scatter, 1), ("restore", gather, -1)]
    if inverse:
        ops = [(name, op, -sign) for name, op, sign in reversed(ops)]
    for name, op, sign in ops:
        if name != omit:
            op(sign)
    require(c == [{2*n+i: Fraction(1)} for i in range(h)], "dirty centers not restored")
    sign = -1 if inverse else 1
    sets = [set(t) for t in f["triples"]]
    for i, s in enumerate(sets):
        expected = {n+i: Fraction(1)}
        for j, t in enumerate(sets):
            value = Fraction(sign*(len(s & t)-1), 2)
            if value:
                expected[j] = value
        require(y[i] == expected, "dirty target shear failed")
    if billed is not None:
        require(type(billed) is int and paid == billed, "executed central bill mismatch")
    return {"input_columns": 2*n+h, "executed_central_primitives": paid}


# Polynomials are coefficient tuples in x=h-10, using exact rationals.
def padd(a, b):
    return tuple((a[i] if i < len(a) else 0)+(b[i] if i < len(b) else 0)
                 for i in range(max(len(a), len(b))))


def pscale(a, scale):
    return tuple(scale*x for x in a)


def pmul(a, b):
    out = [Fraction(0)]*(len(a)+len(b)-1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i+j] += x*y
    return tuple(out)


def pchoose(offset, k):
    """Polynomial binom(x+offset,k), for fixed nonnegative k."""
    out = (Fraction(1),)
    for j in range(k):
        out = pscale(pmul(out, (offset-j, 1)), Fraction(1, j+1))
    return out


def difference_polynomial(k):
    # Terms common to every anchor cancel. Remaining gather difference:
    out = pscale(padd(pchoose(10, 3), pscale(pchoose(9, 2), -2)), k)
    for size, sign in ((k, 1), (0, -1)):
        for sp in (0, 1):
            for j in range(4-sp):
                multiplicity = choose(size, j)
                if not multiplicity:
                    continue
                weight = (3-size)*sp+j-1
                require(abs(weight) <= 2, "polynomial outside priced alphabet")
                price = 0 if weight == 0 else 1 if abs(weight) == 2 else 2
                term = pscale(pchoose(9-size, 3-sp-j), sign*price*multiplicity)
                out = padd(out, term)
    return out


def check_positive_certificate(rows):
    require(type(rows) is list and len(rows) == 4, "four polynomial certificates required")
    for k, row in enumerate(rows, 1):
        require(type(row) is list and len(row) == 4 and all(type(a) is int for a in row),
                "invalid polynomial certificate")
        require(row[0] > 0 and all(a >= 0 for a in row), "nonpositive certificate")
        reconstructed = (Fraction(0),)*4
        for j, a in enumerate(row):
            reconstructed = padd(reconstructed, pscale(pchoose(0, j), a))
        require(reconstructed == difference_polynomial(k), "polynomial identity failed")
    return True
