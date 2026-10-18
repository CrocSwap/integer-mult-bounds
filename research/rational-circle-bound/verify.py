#!/usr/bin/env python3
"""Exact finite evidence for the rational-circle-bound note.

Python 3.10+ standard library. The analytic proof is in PROOF.md.
All checks use explicit exceptions and remain enabled under python -O.
"""
from dataclasses import dataclass
from fractions import Fraction as F
from hashlib import sha1, sha256
from itertools import product
from pathlib import Path
import argparse
import json

ROOT = Path(__file__).resolve().parent
BASE = "66849e1475c930fd7732b1a0067ffee7e1e95f60"
RADICES = (3, 4, 5, 7, 8, 9, 11, 16, 25, 27, 32, 49, 64, 71)


def need(ok, message):
    if not ok:
        raise ValueError(message)


@dataclass(frozen=True)
class C:
    """Gaussian rational; no floating-point conversions."""
    re: F = F(0)
    im: F = F(0)

    def __post_init__(self):
        object.__setattr__(self, "re", F(self.re))
        object.__setattr__(self, "im", F(self.im))

    @staticmethod
    def of(x):
        return x if isinstance(x, C) else C(x)

    def __add__(self, x):
        x = C.of(x)
        return C(self.re + x.re, self.im + x.im)

    __radd__ = __add__

    def __neg__(self):
        return C(-self.re, -self.im)

    def __sub__(self, x):
        return self + (-C.of(x))

    def __rsub__(self, x):
        return C.of(x) - self

    def __mul__(self, x):
        x = C.of(x)
        return C(self.re*x.re - self.im*x.im,
                 self.re*x.im + self.im*x.re)

    __rmul__ = __mul__

    def __truediv__(self, x):
        x = C.of(x)
        need(x.abs2() != 0, "Division by zero")
        return self * C(x.re/x.abs2(), -x.im/x.abs2())

    def __rtruediv__(self, x):
        return C.of(x) / self

    def __pow__(self, n):
        need(type(n) is int, "Integer power required")
        if n < 0:
            return (1/self)**(-n)
        out, a = C(1), self
        while n:
            if n & 1:
                out = out*a
            a, n = a*a, n//2
        return out

    def conj(self):
        return C(self.re, -self.im)

    def abs2(self):
        return self.re**2 + self.im**2

    def upper_abs(self):
        return abs(self.re) + abs(self.im)


ZERO, ONE = C(), C(1)


def trim(p):
    p = list(map(C.of, p))
    while len(p) > 1 and p[-1] == ZERO:
        p.pop()
    return p


def pmul(p, q):
    a = [ZERO]*(len(p)+len(q)-1)
    for j, x in enumerate(p):
        for k, y in enumerate(q):
            a[j+k] = a[j+k] + x*y
    return trim(a)


def peval(p, z):
    a = ZERO
    for x in reversed(p):
        a = a*z + x
    return a


def reflected(roots, leading=ONE):
    """Return P,Q,N,D,m with P=(N/D)*Q, using exact supplied roots."""
    leading = C.of(leading)
    need(leading != ZERO, "Zero polynomial has no positive circle gap")
    p, q, numer, denom, m = [leading], [leading], [ONE], [ONE], 0
    for a in roots:
        need(a.abs2() != 1, "Root on unit circle")
        factor = [-a, ONE]
        p = pmul(p, factor)
        if a.abs2() < 1:
            mirror = [ONE, -a.conj()]
            q, numer, denom = pmul(q, mirror), pmul(numer, factor), pmul(denom, mirror)
            m += 1
        else:
            q = pmul(q, factor)
    return p, q, numer, denom, m


def ident(n):
    return [[C(int(i == j)) for j in range(n)] for i in range(n)]


def madd(a, b):
    return [[x+y for x, y in zip(ar, br)] for ar, br in zip(a, b)]


def mscale(a, c):
    return [[x*c for x in row] for row in a]


def mmul(a, b):
    n = len(a)
    out = [[ZERO]*n for _ in range(n)]
    for i in range(n):
        for k in range(n):
            if a[i][k] != ZERO:
                for j in range(n):
                    if b[k][j] != ZERO:
                        out[i][j] = out[i][j] + a[i][k]*b[k][j]
    return out


def inverse(a):
    """Gauss-Jordan oracle, separate from the geometric inverse formula."""
    n = len(a)
    aug = [row[:] + unit for row, unit in zip(a, ident(n))]
    for j in range(n):
        pivot = next((i for i in range(j, n) if aug[i][j] != ZERO), None)
        need(pivot is not None, "Singular matrix")
        aug[j], aug[pivot] = aug[pivot], aug[j]
        v = aug[j][j]
        aug[j] = [x/v for x in aug[j]]
        for i in range(n):
            if i != j and aug[i][j] != ZERO:
                c = aug[i][j]
                aug[i] = [x-c*y for x, y in zip(aug[i], aug[j])]
    need([row[:n] for row in aug] == ident(n), "Elimination residual")
    return [row[n:] for row in aug]


def cyclic(n, stride, phase):
    need(type(n) is int and n >= 1, "Positive cyclic length required")
    need(phase.abs2() == 1, "Unit phase required")
    a = [[ZERO]*n for _ in range(n)]
    for i in range(n):
        a[i][(i-stride) % n] = phase
    return a


def mpowers(a, count):
    p = [ident(len(a))]
    for _ in range(count):
        p.append(mmul(p[-1], a))
    return p


def polynomial_matrix(p, powers):
    out = [[ZERO]*len(powers[0]) for _ in powers[0]]
    for c, a in zip(p, powers):
        out = madd(out, mscale(a, c))
    return out


def geometric_inverse(root, phase, powers):
    """(U-aI)^-1 using U^L=phase^L I, valid also for noncoprime strides."""
    length = len(powers[0])
    denom = phase**length-root**length
    need(denom != ZERO, "Singular geometric closure")
    out = [[ZERO]*length for _ in range(length)]
    for j in range(length):
        out = madd(out, mscale(powers[j], root**(length-1-j)/denom))
    return out


def prime_power(r):
    need(type(r) is int and r >= 3, "Inherited budget requires integer r>=3")
    p = next(d for d in range(2, r+1) if r % d == 0)
    rest, exponent = r, 0
    while rest % p == 0:
        rest //= p
        exponent += 1
    need(rest == 1, "Inherited circle budget only admits prime powers")
    return p, exponent


def ceil_log2(x):
    need(type(x) is int and x > 0, "Positive integer budget required")
    return (x-1).bit_length()


def budget(r):
    p, exponent = prime_power(r)
    n, d, h = r-1, r-r//p, 2**r-1
    need(d % 2 == 0, "Totient parity")
    a = 2*r*n*h**(n*d-1)
    x = n*h**(n*d//2)
    old = a + 2*F(n*h, r)*a*a
    need(old.denominator == 1, "Old bound integrality")
    old, previous, new = int(old), a*(1+4*x), a*(1+4*n)**2
    need(old == a*(1+4*x*x), "Original formula mismatch")
    need(h >= 2*n+1 and h**(n*d//2) > 4*n+2, "Universal comparison witness")
    need(new < previous < old, "Strict bound comparison")
    bits = [ceil_log2(v) for v in (old, previous, new)]
    for value, b in zip((old, previous, new), bits):
        need(2**(b-1) < value <= 2**b, "Binary ceiling enclosure")
    return {"r": r, "prime": p, "prime_exponent": exponent,
            "n": n, "D": d, "old_bits": bits[0], "previous_bits": bits[1],
            "new_bits": bits[2], "saved_vs_previous": bits[1]-bits[2],
            "saved_vs_original": bits[0]-bits[2]}


PHASES = (ONE, C(0, 1), C(F(3, 5), F(4, 5)))
POINTS = PHASES + (-ONE, C(0, -1), C(F(5, 13), F(12, 13)))
ATOMS = (ZERO, C(F(1, 2)), C(F(-1, 2)), C(2), C(-2),
         C(F(3, 10), F(2, 5)), C(F(6, 5), F(8, 5)),
         C(F(31, 32)), C(F(33, 32)))


def families():
    out = [(), (ZERO,), (ZERO, ZERO), (C(F(1, 2)),), (C(2),),
           (C(F(1, 2)), C(2)), (C(F(1, 2)),)*3, (C(2),)*3,
           (C(F(31, 32)), C(F(33, 32))),
           (C(F(3, 10), F(2, 5)), C(F(6, 5), F(8, 5))),
           (ZERO, C(-2), C(F(1, 2))),
           (C(F(-1, 2)), C(2), C(F(3, 10), F(2, 5))),
           (ZERO, ZERO, C(F(1, 2)), C(2))]
    out.extend(tuple(a) for a in product(ATOMS, repeat=2))
    # A declared deterministic family, not an open-ended randomized search.
    for i in range(32):
        out.append(tuple(ATOMS[(i*7+j*j+3*j) % len(ATOMS)] for j in range(3+i % 4)))
    return out


def reflection_checks():
    cases, point_checks, inner, outer, zero, repeated = 0, 0, 0, 0, 0, 0
    for roots in families():
        p, q, num, den, m = reflected(roots)
        need(len(p)-1 == len(roots), "Multiplicity/degree mismatch")
        need(pmul(p, den) == pmul(num, q), "Reflection identity P*D=N*Q")
        need(len(q)-1 <= len(roots), "Reflected degree bound")
        need(m == sum(a.abs2() < 1 for a in roots), "Inner multiplicity count")
        for a in roots:
            if 0 < a.abs2() < 1:
                need((1/a.conj()).abs2() > 1, "Reflected pole outside disk")
        for z in POINTS:
            pv, qv, nv, dv = (peval(f, z) for f in (p, q, num, den))
            need(dv != ZERO and qv != ZERO, "Unexpected boundary zero")
            need(pv.abs2() == qv.abs2(), "Circle modulus preservation")
            need(nv.abs2() == dv.abs2(), "Blaschke modulus one")
            need(1/pv == (nv/dv).conj()/qv, "Conjugate reciprocal identity")
            point_checks += 1
        cases += 1
        inner += int(m == len(roots) and bool(roots))
        outer += int(m == 0 and bool(roots))
        zero += int(ZERO in roots)
        repeated += int(len(set(roots)) < len(roots))
    return {"families": cases, "boundary_points": point_checks,
            "all_inner": inner, "all_outer": outer, "contains_zero": zero,
            "contains_repetition": repeated}


def cycle_checks():
    cases, entry_comparisons, zero_stride, noncoprime = 0, 0, 0, 0
    chosen = families()[:13]
    for roots in chosen:
        p, q, num, den, m = reflected(roots)
        for length in (1, 2, 3, 4, 6):
            for stride in sorted({-1 % length, 0, 1 % length, 2 % length}):
                for phase in PHASES:
                    u = cyclic(length, stride, phase)
                    powers = mpowers(u, max(length, len(p)))
                    need(powers[length] == mscale(ident(length), phase**length), "Cyclic closure")
                    matrix = polynomial_matrix(p, powers)
                    exact = inverse(matrix)
                    factored = ident(length)
                    for a in roots:
                        factored = mmul(factored, geometric_inverse(a, phase, powers))
                    need(exact == factored, "Dense / geometric inverse disagreement")
                    need(mmul(matrix, factored) == ident(length), "Left inverse residual")
                    need(mmul(factored, matrix) == ident(length), "Right inverse residual")
                    # Direct coefficient evaluation using the entry map, independent of matrix powers.
                    direct = [[ZERO]*length for _ in range(length)]
                    for j, c in enumerate(p):
                        for row in range(length):
                            col = (row-j*stride) % length
                            direct[row][col] = direct[row][col] + c*phase**j
                    need(direct == matrix, "Polynomial matrix / entry-map disagreement")
                    cases += 1
                    entry_comparisons += length*length
                    zero_stride += int(stride == 0)
                    from math import gcd
                    noncoprime += int(stride != 0 and gcd(stride, length) > 1)
    return {"cases": cases, "inverse_entries": entry_comparisons,
            "zero_stride_cases": zero_stride, "nonzero_noncoprime_cases": noncoprime}


def hilbert_checks():
    vectors = tuple(product((0, 1, 2), repeat=4))
    norms = {v: sum(x*x for x in v) for v in vectors}
    kernel = [[F(1, j+k+1) for k in range(4)] for j in range(4)]
    count = 0
    for a in vectors:
        weighted = [sum((a[j]*kernel[j][k] for j in range(4)), F(0)) for k in range(4)]
        for b in vectors:
            lhs = sum((weighted[k]*b[k] for k in range(4)), F(0))
            need(lhs*lhs <= 16*norms[a]*norms[b], "Finite Hilbert inequality")
            count += 1
    # More frequencies with exact rational coefficients; use squared comparisons.
    for length in (8, 16, 32, 64):
        a = [F(1, j+1) for j in range(length)]
        b = [F(1, 2*j+1) for j in range(length)]
        lhs = sum((a[j]*b[k]/(j+k+1) for j in range(length) for k in range(length)), F(0))
        need(lhs*lhs <= 16*sum(x*x for x in a)*sum(x*x for x in b), "Long Hilbert inequality")
        count += 1
    return {"comparisons": count, "exhaustive_vectors_each_side": len(vectors),
            "exhaustive_length": 4, "long_lengths": [8, 16, 32, 64]}


def near_circle_checks():
    for k in range(1, 129):
        eps = F(1, 2**k)
        a = 1-eps
        # R=eps/(1-a*z): positive coefficients and exact infinite geometric tail.
        partial = sum((eps*a**j for j in range(17)), F(0))
        tail = a**17
        need(partial+tail == 1, "Exact one-pole Wiener norm")
        need(eps/(1-a) == 1, "One-pole circle maximum")
        need(eps*a/(1-a)**2 == 2**k-1, "Diverging pointwise derivative")
        # Elementary Blaschke factor b_a=(z-a)/(1-a*z).
        first = a + sum(((1-a*a)*a**(j-1) for j in range(1, 18)), F(0))
        rest = (1+a)*a**17
        need(first+rest == 1+2*a <= 5, "Exact Blaschke norm and degree-one bound")
        # P_eps=z-(1+eps) has exact circle gap eps and inverse at U=I of size 1/eps.
        outer = 1+eps
        need(abs(1-outer) == eps and abs(1/(1-outer)) == 2**k,
             "Necessary inverse-gap exponent witness")
    return {"families": 128, "epsilon": "2^-k, 1<=k<=128",
            "one_pole_W_norm": "1", "pointwise_derivative_at_1": "2^k-1",
            "necessary_gap_power": "P=z-(1+epsilon), gap=epsilon, inverse at U=I has norm 2^k"}


def expect_failure(fn, label):
    try:
        fn()
    except (ValueError, ZeroDivisionError):
        return label
    raise ValueError("Control did not fail: "+label)


def controls():
    rejected = []
    for r in (0, 1, 2, 6, 10, 12, 15, 18, True, F(3)):
        rejected.append(expect_failure(lambda r=r: budget(r), "inadmissible inherited radix "+str(r)))
    for root in (ONE, C(0, 1), PHASES[2]):
        rejected.append(expect_failure(lambda root=root: reflected((root,)), "unit-circle root "+str(root)))
    rejected.append(expect_failure(lambda: reflected((), ZERO), "zero polynomial"))
    rejected.append(expect_failure(lambda: cyclic(2, 1, C(2)), "nonunit phase"))
    rejected.append(expect_failure(lambda: cyclic(0, 1, ONE), "zero cycle length"))
    # A missing conjugation breaks modulus preservation for a nonreal root.
    root, z = C(0, F(1, 2)), C(0, 1)
    need((z-root).abs2() != (1-root*z).abs2(), "Wrong-conjugation control failed")
    rejected.append("reflection without conjugation")
    # Omitting the inner factor loses a sign already at z=-1.
    p, q, num, den, m = reflected((C(F(1, 2)),))
    need(1/peval(p, -ONE) != 1/peval(q, -ONE), "Missing inner factor control failed")
    rejected.append("omit Blaschke factor")
    # Taylor coefficients of 1/(z-1/2) about zero diverge at z=1.
    taylor_at_1 = -sum((F(2)**(j+1) for j in range(17)), F(0))
    residual = F(1, 2)*taylor_at_1-1
    need(abs(residual) == 2**17, "Interior-pole Taylor control failed")
    rejected.append("Taylor expansion across an interior pole")
    # Hilbert norm constant one is false: vector (1,1) on both sides.
    need(F(7, 3)**2 > 4, "Hilbert constant-one control failed")
    rejected.append("replace Hilbert constant four by one")
    # Scalar circle information alone is not an induced infinity-norm bound.
    p = [ONE, C(F(1, 2)), C(F(1, 2))]
    mat = polynomial_matrix(p, mpowers(cyclic(3, 1, ONE), 3))
    inv = inverse(mat)
    expected = [[C(F(3, 2) if i == j else F(-1, 2)) for j in range(3)] for i in range(3)]
    need(inv == expected, "Spectral-shortcut witness inverse")
    need(F(7, 32) > F(7, 15)**2, "Spectral-shortcut circle lower bound")
    need(sum(abs(x.re) for x in inv[0]) == F(5, 2) > F(15, 7), "Spectral-shortcut strict witness")
    rejected.append("equate scalar maximum with induced infinity norm")
    return rejected


def blob(data):
    return sha1(b"blob "+str(len(data)).encode("ascii")+b"\0"+data).hexdigest()


def check_sources():
    obj = json.loads((ROOT/"SOURCES.json").read_text(encoding="utf-8"))
    need(obj["base_commit"] == BASE, "Base pin mismatch")
    for entry in obj["files"]:
        data = (ROOT/entry["local_path"]).read_bytes()
        need(sha256(data).hexdigest() == entry["sha256"], "Source SHA-256 mismatch: "+entry["local_path"])
        need(blob(data) == entry["git_blob"], "Source Git-blob mismatch: "+entry["local_path"])
    selected = json.loads((ROOT/"vendor/selected-result.json").read_text(encoding="utf-8"))
    need(selected["kappa"] == "51110230636731/31250000000000000", "Selected context mismatch")
    return len(obj["files"])


def evidence():
    return {"schema": 1, "status": "PASS_RATIONAL_CIRCLE_BOUND", "base": BASE,
            "source_files": check_sources(), "budgets": [budget(r) for r in RADICES],
            "reflection": reflection_checks(), "cyclic_inverses": cycle_checks(),
            "hilbert": hilbert_checks(), "near_circle": near_circle_checks(),
            "controls": controls(), "new_kappa_claim": False,
            "scope": "Exact finite checks; analytic all-length proof is PROOF.md, not formalized."}


def check_manifest():
    obj = json.loads((ROOT/"MANIFEST.json").read_text(encoding="utf-8"))
    for path, digest in obj["sha256"].items():
        need(sha256((ROOT/path).read_bytes()).hexdigest() == digest, "Package hash mismatch: "+path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", type=Path, help="Write evidence to a new file; refuse any overwrite")
    args = parser.parse_args()
    if args.emit:
        need(not args.emit.exists(), "Refusing to overwrite evidence")
    else:
        check_manifest()
    obj = evidence()
    if args.emit:
        with args.emit.open("x", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(obj, indent=2)+"\n")
    else:
        want = json.loads((ROOT/"EXPECTED.json").read_text(encoding="utf-8"))
        need(obj == want, "Expected evidence mismatch")
    print(obj["status"])
    print(json.dumps({"reflection": obj["reflection"], "cyclic_inverses": obj["cyclic_inverses"],
                      "hilbert": obj["hilbert"], "near_circle_families": obj["near_circle"]["families"],
                      "controls": len(obj["controls"]), "radix_budgets": len(obj["budgets"])}, sort_keys=True))


if __name__ == "__main__":
    main()
