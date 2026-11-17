#!/usr/bin/env python3
"""Same-image-line and same-kernel-line exclusion for the diagonal-pair word.

Standard library only.  Exact finite-field arithmetic; the group algebra is the
free group on the call positions, with words as multisets of call positions (the free abelian group), so a
vanishing group-algebra element is a coefficient-wise vanishing identity.
"""
import itertools
import json

# ---------------------------------------------------------------- fields

class PrimeField:
    def __init__(self, p):
        self.q = p
        self.elements = tuple(range(p))
        self.zero = 0
        self.one = 1

    def add(self, a, b):
        return (a + b) % self.q

    def mul(self, a, b):
        return (a * b) % self.q

    def neg(self, a):
        return (-a) % self.q

    def inv(self, a):
        for b in self.elements:
            if self.mul(a, b) == self.one:
                return b
        raise ValueError('not invertible')


class GF4:
    q = 4
    elements = (0, 1, 2, 3)
    zero = 0
    one = 1
    MUL = ((0, 0, 0, 0), (0, 1, 2, 3), (0, 2, 3, 1), (0, 3, 1, 2))

    def add(self, a, b):
        return a ^ b

    def mul(self, a, b):
        return self.MUL[a][b]

    def neg(self, a):
        return a

    def inv(self, a):
        for b in self.elements:
            if self.mul(a, b) == self.one:
                return b
        raise ValueError('not invertible')


FIELDS = (PrimeField(2), PrimeField(3), GF4(), PrimeField(5))

# ---------------------------------------------------------------- matrices

def mmul(F, A, B):
    return (F.add(F.mul(A[0], B[0]), F.mul(A[1], B[2])),
            F.add(F.mul(A[0], B[1]), F.mul(A[1], B[3])),
            F.add(F.mul(A[2], B[0]), F.mul(A[3], B[2])),
            F.add(F.mul(A[2], B[1]), F.mul(A[3], B[3])))


def madd(F, A, B):
    return tuple(F.add(x, y) for x, y in zip(A, B))


def mscale(F, c, A):
    return tuple(F.mul(c, x) for x in A)


I2 = (1, 0, 0, 1)


def projectors(F):
    out = []
    for a in F.elements:
        for b in F.elements:
            for c in F.elements:
                for d in F.elements:
                    N = (a, b, c, d)
                    if mmul(F, N, N) != N:
                        continue
                    if F.add(a, d) != F.one:
                        continue
                    out.append(N)
    return tuple(out)


def normalise(F, v):
    for x in v:
        if x != F.zero:
            inv = F.inv(x)
            return tuple(F.mul(inv, y) for y in v)
    return None


def image_line(F, N):
    a, b, c, d = N
    for v in ((a, c), (b, d)):
        w = normalise(F, v)
        if w is not None:
            return w
    raise ValueError('zero image')


def kernel_line(F, N):
    a, b, c, d = N
    for v in ((b, F.neg(a)), (d, F.neg(c))):
        w = normalise(F, v)
        if w is not None:
            # keep only vectors that really lie in the kernel
            if (F.add(F.mul(a, w[0]), F.mul(b, w[1])) == F.zero and
                    F.add(F.mul(c, w[0]), F.mul(d, w[1])) == F.zero):
                return w
    raise ValueError('no kernel vector found')

# ---------------------------------------------------------------- group algebra

def gadd(A, B, F):
    out = dict(A)
    for w, c in B.items():
        v = F.add(out.get(w, F.zero), c)
        if v == F.zero:
            out.pop(w, None)
        else:
            out[w] = v
    return out


def gmul(A, B, F):
    # commutative group algebra: words are multisets of call positions
    out = {}
    for w1, c1 in A.items():
        for w2, c2 in B.items():
            w = tuple(sorted(w1 + w2))
            v = F.add(out.get(w, F.zero), F.mul(c1, c2))
            if v == F.zero:
                out.pop(w, None)
            else:
                out[w] = v
    return out


def gscale(A, c, F):
    if c == F.zero:
        return {}
    return {w: F.mul(c, v) for w, v in A.items() if F.mul(c, v) != F.zero}


def gneg(A, F):
    return {w: F.neg(v) for w, v in A.items() if F.neg(v) != F.zero}


def expand(F, Ns):
    """Return the four entries of the product as group-algebra elements.

    Ward 0 of the dict is the empty word (the identity of the free group).
    """
    terms = {(): I2}
    for i, N in enumerate(Ns):
        nxt = {}
        for mask, C in terms.items():
            left = mmul(F, C, madd(F, I2, mscale(F, F.neg(F.one), N)))
            right = mmul(F, C, N)
            nxt[mask] = left
            nxt[mask + (i,)] = right
        terms = nxt
    entries = [{}, {}, {}, {}]
    for mask, C in terms.items():
        for e in range(4):
            if C[e] != F.zero:
                entries[e][mask] = C[e]
    return entries


def minor(F, entries):
    A = [dict(entries[e]) for e in range(4)]
    A[0] = gadd(A[0], {(): F.neg(F.one)}, F)
    A[3] = gadd(A[3], {(): F.neg(F.one)}, F)
    return gadd(gmul(A[0], A[3], F), gneg(gmul(A[1], A[2], F), F), F)

# ---------------------------------------------------------------- main

def require(cond, msg):
    if not cond:
        raise SystemExit('FAIL ' + msg)


def same_class(projector_list, key):
    classes = {}
    for N in projector_list:
        classes.setdefault(key(N), []).append(N)
    return classes


def main():
    report = {}
    for F in FIELDS:
        q = F.q
        inv = projectors(F)
        require(len(inv) == q * (q + 1),
                'projector inventory %d for q=%d' % (len(inv), q))
        require(all(mmul(F, N, N) == N for N in inv), 'idempotence')
        require(all(F.add(N[0], N[3]) == F.one for N in inv), 'trace one')

        by_image = same_class(inv, lambda N: image_line(F, N))
        by_kernel = same_class(inv, lambda N: kernel_line(F, N))
        require(len(by_image) == q + 1, 'image line count')
        require(len(by_kernel) == q + 1, 'kernel line count')
        require(all(len(v) == q for v in by_image.values()), 'image class size')
        require(all(len(v) == q for v in by_kernel.values()), 'kernel class size')

        pairs = 0
        for cls in by_image.values():
            for X in cls:
                for Y in cls:
                    require(mmul(F, X, Y) == Y, 'image collapse')
                    pairs += 1
        for cls in by_kernel.values():
            for X in cls:
                for Y in cls:
                    require(mmul(F, X, Y) == X, 'kernel collapse')
                    pairs += 1

        # subset collapse and vanishing minors, bounded by tuple length
        max_len = 5 if q <= 3 else 4
        tuples = 0
        subs = 0
        minors = 0
        for cls in by_image.values():
            for k in range(1, max_len + 1):
                for Ns in _product(cls, k):
                    tuples += 1
                    for mask in range(1, 1 << k):
                        prod = I2
                        last = None
                        for i in range(k):
                            if mask >> i & 1:
                                prod = mmul(F, prod, Ns[i])
                                last = Ns[i]
                        require(prod == last, 'subset collapse to last')
                        subs += 1
                    M = minor(F, expand(F, Ns))
                    require(M == {}, 'same-image minor did not vanish')
                    minors += 1
        for cls in by_kernel.values():
            for k in range(1, max_len + 1):
                for Ns in _product(cls, k):
                    tuples += 1
                    for mask in range(1, 1 << k):
                        prod = I2
                        first = None
                        for i in range(k):
                            if mask >> i & 1:
                                prod = mmul(F, prod, Ns[i])
                                if first is None:
                                    first = Ns[i]
                        require(prod == first, 'subset collapse to first')
                        subs += 1
                    M = minor(F, expand(F, Ns))
                    require(M == {}, 'same-kernel minor did not vanish')
                    minors += 1

        # two-call normal form: with N1 = E00, diag(diag([g1],1) (I+t2 N2))
        # forces N2 diagonal, checked in the free group on two letters.
        E00 = (1, 0, 0, 0)
        t2 = {(): F.one, (1,): F.one}
        two_call = 0
        for N2 in inv:
            entries = expand(F, (E00, N2))   # free group on two letters
            diag_q = (entries[1] == {} and entries[2] == {})
            diag_n = (N2[1] == F.zero and N2[2] == F.zero)
            require(diag_q == diag_n, 'two-call diagonal forcing')
            two_call += 1

        report[q] = {
            'projectors': len(inv),
            'ordered_collapse_pairs': pairs,
            'same_line_tuples': tuples,
            'subset_collapses': subs,
            'vanishing_minors': minors,
            'two_call_projectors': two_call,
            'max_tuple_length': max_len,
        }

    _controls()
    print('PASS_DIAGONAL_PAIR_LINE_SEPARATION ' +
          json.dumps(report, sort_keys=True))


def _product(cls, k):
    return itertools.product(cls, repeat=k)


def _controls():
    F = PrimeField(2)
    E00 = (1, 0, 0, 0)
    E11 = (0, 0, 0, 1)
    # six-call F2 word: diag([g1 g2 g3], [g4 g5 g6]); the minor is nonzero
    w = (E00, E00, E00, E11, E11, E11)
    M = minor(F, expand(F, w))
    require(M != {}, 'six-call positive control minor vanished')
    expected = {(0, 1, 2): 1, (3, 4, 5): 1, (0, 1, 2, 3, 4, 5): 1, (): 1}
    require(M == expected, 'six-call minor coefficients')
    # mixing image lines can give a nonzero minor: E00 then E11 is diagonal
    # with two distinct targets, so (P-I) has rank two there.
    require(image_line(F, E11) != image_line(F, E00), 'control lines coincide')
    require(minor(F, expand(F, (E00, E11))) != {}, 'mixed-line control vanished')
    # a same-image pair does vanish (already covered above, repeat explicitly)
    require(minor(F, expand(F, (E00, E00))) == {}, 'same-image control')


if __name__ == '__main__':
    main()
