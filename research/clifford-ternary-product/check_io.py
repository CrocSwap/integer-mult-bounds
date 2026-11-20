"""Independent finite checks of recognition, signed delivery and character pairing."""

from itertools import product
from pathlib import Path
from random import Random
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from delivery import deliver
from operand import cantor_flags, recognise_sparse


def check(ok, reason):
    if not ok:
        raise AssertionError(reason)


def positions(m):
    return [sum(3 ** i for i in range(m) if (x >> i) & 1) for x in range(1 << m)]


def bit_value(bits):
    return sum(bit << i for i, bit in enumerate(bits))


def bits_of(value, size):
    return bytes((value >> i) & 1 for i in range(size))


def check_recognition():
    # This oracle enumerates all affine supports and every degree-two ANF.
    catalogues = {}
    total = accepted = 0
    for m in range(4):
        entries = 1 << m
        full = (1 << entries) - 1
        site = positions(m)
        check([i for i,v in enumerate(cantor_flags(m)) if v] == site, "ternary enumeration")
        affine = {full, 0}
        for linear in range(1, entries):
            cuts = [sum(1 << x for x in range(entries) if (linear & x).bit_count() % 2 == rhs)
                    for rhs in (0, 1)]
            affine.update(A & cut for A in tuple(affine) for cut in cuts)
        monomials = [k for k in range(entries) if k.bit_count() <= 2]
        quadratics = {0}
        for mask in monomials:
            poly = sum(1 << x for x in range(entries) if (mask & x) == mask)
            quadratics.update(k ^ poly for k in tuple(quadratics))
        expected = {A & q for A in affine for q in quadratics}
        catalogues[m] = expected
        for table in range(1 << entries):
            raw = bytearray(3 ** m)
            for x, p in enumerate(site):
                raw[p] = (table >> x) & 1
            result = recognise_sparse(raw, m)
            check((result is not None) == (table in expected), "exact recognition class")
            if result is not None:
                observable = sum(result.value(x) << x for x in range(entries))
                check(observable == table, "descriptor truth table")
                accepted += 1
            total += 1
    trials = 0
    for length in range(9):
        m = 0
        while 3 ** m < length:
            m += 1
        site = positions(m)
        keep = set(site)
        for integer in range(1 << length):
            raw = bits_of(integer, length)
            invalid = any(z and i not in keep for i,z in enumerate(raw))
            word = sum(raw[p] << j for j,p in enumerate(site) if p < length)
            expected = not invalid and word in catalogues[m]
            actual = recognise_sparse(raw, m)
            check((actual is not None) == expected, "literal padding or hole membership")
            if actual is not None:
                check(sum(actual.value(j) << j for j in range(1 << m)) == word,
                      "partial literal descriptor")
            trials += 1
    rng = Random(641)
    for m in range(4, 10):
        pts = positions(m)
        raw = bytearray(3 ** m)
        u, v = rng.randrange(1 << m), rng.randrange(1 << m)
        for x,p in enumerate(pts):
            raw[p] = int(((u & x).bit_count() % 2) == 1) & (
                1 ^ ((v & x).bit_count() % 2) ^ int((x & 3) == 3))
        d = recognise_sparse(raw,m)
        check(d is not None and bytes(d.value(x) for x in range(1 << m)) ==
              bytes(raw[i] for i in pts), "higher-dimensional literal recognition")
        cube = bytearray(3 ** m)
        for x,p in enumerate(pts):
            cube[p] = int((x & 7) != 7)
        check(recognise_sparse(cube, m) is None, "nonquadratic rejected")
        raw[2] = 1
        check(recognise_sparse(raw, m) is None, "mixed literal holes")
    print("Recognition:",total,"Boolean tables,",accepted,"accepted;",trials,"literal-length cases")


def check_delivery():
    # A hostile sign pattern repeats over the same long run of binary ones.
    high = 191
    trials = ["+" * (1 << 8), (">+" * high) + ("<" * high) + ("+-" * 991) + "+"]
    for moves in trials:
        head = number = 0
        for c in moves:
            if c == ">":
                head += 1
            elif c == "<":
                head -= 1
            else:
                number += (1 << head) * (1 if c == "+" else -1)
        tally = {}
        result = deliver([moves]*4, stats=tally)
        check(bit_value(result) == number, "signed ripple")
        check(tally["ripple"] <= tally["emits"], "independent carry bound")
    for malformed in (("<", "", "", ""), ("+", "", "", ""), ("-",)*4,
                      ("x", "", "", ""), ("",)*3, ("",)*5):
        try:
            deliver(malformed)
        except ValueError:
            pass
        else:
            raise AssertionError("Malformed signed transcript was accepted")
    print("Delivery: sign cancellation, deep carries, head restoration and six rejection cases")


def brute_pass(A, B, u, v):
    # Enumerate all witness pairs only for this test.
    pts = positions(A.m)
    coefficients = {}
    for x, px in enumerate(pts):
        if any((x & k).bit_count() % 2 != rhs for k,rhs in A.equations):
            continue
        for y, py in enumerate(pts):
            if any((y & k).bit_count() % 2 != rhs for k,rhs in B.equations):
                continue
            parity = (u * (A.value(x) + 1) + v * (B.value(y) + 1)) % 2
            address = px + py
            coefficients[address] = coefficients.get(address, 0) + (1 if not parity else -1)
    head = 0
    for address, c in sorted(coefficients.items()):
        if not c:
            continue
        w = abs(c)
        check(w & (w-1) == 0, "quadratic fibre magnitude")
        pos = address + w.bit_length()-1
        yield from (">" if pos >= head else "<") * abs(pos-head)
        yield "+" if c>0 else "-"
        head = pos


def check_product():
    trials = 0
    for m in range(1,5):
        pts = positions(m)
        span = (3 ** m + 1) // 2
        variants = []
        for variant in range(8):
            x = bytearray(min(3 ** m, span + (variant % 3)))
            for j,p in enumerate(pts):
                support = int((j & (variant >> 1)).bit_count() % 2 == int(variant < 4))
                phase = int((j & 3) == 3) ^ (j.bit_count() % 2) ^ (variant % 2)
                x[p] = support & phase
            variants.append(bytes(x))
        for a,b in product(variants, repeat=2):
            A, B = recognise_sparse(a, m), recognise_sparse(b, m)
            check(A is not None and B is not None, "known input failed admission")
            result = deliver(brute_pass(A,B,u,v) for u,v in product((0,1),repeat=2))
            check(bit_value(result) == bit_value(a)*bit_value(b), "literal product")
            trials += 1
    print("End-to-end I/O:", trials,"sparse literal products")


if __name__ == "__main__":
    check_recognition()
    check_delivery()
    check_product()
    print("PASS_CANTOR_LITERAL_IO")
