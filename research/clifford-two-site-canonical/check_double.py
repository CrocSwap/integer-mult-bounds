"""Verify the phase, normalization and group convolution on literal width-13 Choi columns."""
from fractions import Fraction
from functools import cache
from double_readout import P, prepare
from bell_reads import transvection
from compile_row import apply, compose, inverse

mul = P.Q.multiply
D = 4**13


def power(value, exponent):
    result = (1, 0)
    for _ in range(exponent):
        result = mul(result, value)
    return result


def sym(axes):
    S = P.IDENTITY
    for axis in axes:
        S = tuple(transvection(axis, v) for v in S)
    return S


def raw_weight(L, u, X, w):
    return Fraction(-1, 32)**P.distance(L, X)/D if u == w else Fraction(0)


def direct(S, p, row, col, terms, left=P.IDENTITY, right=P.IDENTITY):
    def at(r, c):
        return P.conjugate(P.transition(S, p, r, c, left, right))
    base = power(at(row, col), 11)
    real = imag = Fraction(0)
    for i, k, m, n, scalar in terms:
        a, b = mul(mul(at(i, k), at(m, n)), scalar)
        real += a
        imag += b
    a, b = mul((real, imag), base)
    return a/D, b/D


def check_raw():
    left, right = sym((19, 138, 73)), sym((17, 8, 82, 35))
    nonzero = set()
    complex_seen = False
    for j in range(5):
        relative = sym(tuple(17 << i for i in range(j)))
        for L, R in ((P.IDENTITY, P.IDENTITY), (left, right)):
            S = compose(L, compose(relative, inverse(R)))
            terms = [(3^1, 1, 3, 1^1, (2,-3)), (3,1^1,3^1,1,(-1,2)),
                     (3,1,3,1,(0,11)), (5,12,10,6,(Fraction(1,5), Fraction(-7,13)))]
            read = prepare(S, 3, 1, terms, raw_weight, L, R)
            for p in (0, 1, 3, 16, 32, 35, 48, 80, 130, 199, 255):
                expected = direct(S, p, 3, 1, terms, L, R)
                P.require(expected == read(p), "literal 11+2 tensor and flag expansion differ")
                if expected != (0,0):
                    nonzero.add(j)
                    complex_seen |= all(expected)
    P.require(nonzero == set(range(5)) and complex_seen, "insufficient nonzero phase controls")


def embedded():
    generators = [sym((1,)), sym((16,))]
    group = [P.IDENTITY]
    for S in group:
        for T in generators:
            U = compose(S, T)
            if U not in group:
                group.append(U)
    P.require(len(group) == 6, "expected the one-qubit symplectic group")
    return group


def inverse_gram_column(group):
    # Invert the genuine principal group block, with all 256 Pauli translates kept.
    rhs = [int(S == P.IDENTITY) for S in group]
    F = {}
    for S in group:
        fixed = sum(apply(S, v) == v for v in range(256))
        F[S] = Fraction((-64)**(fixed.bit_length()-1), 16**12)
    A = [[F[compose(inverse(S), T)] for T in group] + [c]
         for S, c in zip(group, rhs, strict=True)]
    for i in range(len(A)):
        scale = A[i][i]
        P.require(scale != 0, "nonpositive principal pivot")
        A[i] = [x/scale for x in A[i]]
        for j in range(len(A)):
            if i != j:
                scale = A[j][i]
                A[j] = [x-scale*y for x,y in zip(A[j], A[i], strict=True)]
    return {S: row[-1] for S, row in zip(group, A, strict=True)}


def trace_slices(S, T):
    # Frobenius inner products Tr(U_S^* W_h U_T). All entries outside the
    # explicitly retained sparse list are checked to have zero trace.
    from canonical import unitary
    a, e = unitary(S)
    b, f = unitary(T)
    overlaps = []
    for h in range(256):
        x, z = divmod(h,16)
        real = imag = 0
        for j, av in enumerate(a):
            if av == (0,0):
                continue
            bv = b[j^x]
            sign = -1 if (z & (j^x)).bit_count()%2 else 1
            re, im = mul(P.conjugate(av), bv)
            real += sign*re
            imag += sign*im
        if real or imag:
            den = 16 << (e+f)
            overlaps.append((h, power((Fraction(real,den), Fraction(imag,den)), 13)))
    return overlaps


def check_subdictionary():
    group = embedded()
    H = inverse_gram_column(group)
    actions = {a: [apply(a,v) for v in range(256)] for a in group}

    @cache
    def restricted(L, u, X, w):
        total = Fraction(0)
        pts = [v for v in range(256) if (X >> v) & 1]
        for a, kernel in H.items():
            action = actions[a]
            if action[w] == u:
                image = sum(1 << action[v] for v in pts)
                total += kernel * raw_weight(L, u, image, u)
        return total

    terms = [(1,0,0,1,(3,2)), (0,1,1,1,(0,-3)),
             (1,1,1,0,(Fraction(1,5),2)), (0,0,1,1,(1,0))]
    coeffs = {}
    for S in group:
        read = prepare(S, 0, 0, terms, restricted)
        coeffs[S] = [read(p) for p in range(256)]
    changed = result_nonzero = count = 0
    for S in group:
        outputs = [[Fraction(0), Fraction(0)] for _ in range(256)]
        for T in group:
            for h, overlap in trace_slices(S,T):
                for p in range(256):
                    sign = -1 if ((p & 15) & (h >> 4)).bit_count()%2 else 1
                    a,b = mul(overlap, coeffs[T][p ^ h])
                    outputs[p][0] += sign*a
                    outputs[p][1] += sign*b
        for p, output in enumerate(outputs):
            truth = direct(S,p,0,0,terms)
            P.require(tuple(output) == truth, "literal normal equation on six complete Pauli fibres")
            result_nonzero += coeffs[S][p] != (0,0)
            changed += truth != coeffs[S][p]
            count += 1
    P.require(count == 1536 and result_nonzero and changed, "vacuous restricted Gram")
    print("PASS literal 1,536-column Choi Gram times decoded vector equals the raw adjoint;",
          result_nonzero, "nonzero canonical entries.")


if __name__ == '__main__':
    check_raw()
    check_subdictionary()
