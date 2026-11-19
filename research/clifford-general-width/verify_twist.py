"""Literal exact Gaussian-rational matrices test the two singleton corrections."""
from fractions import Fraction
from functools import cache, reduce
from itertools import product
from operator import xor


def require(ok, why):
    if not ok:
        raise ValueError(why)


zero = (0, 0)
one = (1, 0)
minus = (-1, 0)
imag = (0, 1)
units = (one, imag, minus, (0, -1))


def add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def mul(a, b):
    return (a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0])


@cache
def scale(h, a):
    return tuple(mul(h, v) for v in a)


@cache
def matmul(a, b):
    return tuple(add(mul(a[2*i], b[j]), mul(a[2*i+1], b[j+2]))
                 for i in range(2) for j in range(2))


def transpose(a):
    return (a[0], a[2], a[1], a[3])


def conjugate(a):
    return tuple((v[0], -v[1]) for v in a)


def tables():
    ident = (one, zero, zero, one)
    x = (zero, one, one, zero)
    z = (one, zero, zero, minus)
    weyl = (ident, x, z, matmul(x, z))
    h = scale((Fraction(1, 2), Fraction(1, 2)), (one, one, one, minus))
    phase = (one, zero, zero, imag)
    lifted = [ident]
    seen = {ident}
    for a in lifted:
        for gate in [h, phase]:
            b = matmul(gate, a)
            if b not in seen:
                seen.add(b)
                lifted.append(b)
    require(len(lifted) == 96, "one-qubit lifts")

    lookup = {scale(phase, w): (j, i)
              for j, w in enumerate(weyl) for i, phase in enumerate(units)}
    ordinary, bell = {}, {}
    for u in lifted:
        ordinary[u] = [lookup[matmul(matmul(u, w), transpose(conjugate(u)))] for w in weyl]
        bell[u] = [lookup[matmul(matmul(u, w), transpose(u))] for w in weyl]
    return weyl, lifted, ordinary, bell


def main():
    weyl, lifted, ordinary, bell = tables()
    all_checks = odd_checks = wrong_plain = wrong_even = 0
    reps, descents = {}, {}
    for u in lifted:
        symplectic = tuple(t for t, _ in ordinary[u])
        reps[symplectic] = u
        for k in (1, 2, 3, 4):
            for source in product(range(4), repeat=k):
                output = tuple(bell[u][v][0] for v in source)
                phase = sum(bell[u][v][1] for v in source) % 4
                w = reduce(xor, source, 0)
                wp = reduce(xor, output, 0)
                if k % 2:
                    require(wp == bell[u][w][0], "odd affine sum")
                    corrected = matmul(matmul(transpose(weyl[wp]), u), weyl[w])
                    sigma = (phase + bell[u][w][1]) % 4
                    target = conjugate(u)
                    odd_checks += 1
                    wrong_plain += int(scale(units[sigma], target) != scale(units[sigma], u))
                else:
                    require(wp == ordinary[u][w][0], "even linear sum")
                    corrected = matmul(matmul(weyl[wp], u), transpose(weyl[w]))
                    sigma = (phase - ordinary[u][w][1]) % 4
                    target = u
                    wrong_even += int(scale(units[sigma], target) != scale(units[phase], u))
                require(scale(units[phase], corrected) == scale(units[sigma], target),
                        "matrix singleton correction")
                key = (symplectic, source)
                value = (output, sigma)
                if key in descents:
                    require(descents[key] == value, "phase depends on the chosen Pauli/scalar lift")
                else:
                    descents[key] = value
                all_checks += 1

    cocycles = 0
    for a in reps:
        for b in reps:
            ab = tuple(a[v] for v in b)
            for k in (1, 2, 3, 4):
                for source in product(range(4), repeat=k):
                    mid, right = descents[b, source]
                    end, left = descents[a, mid]
                    require(descents[ab, source] == (end, (left + right) % 4), "cocycle")
                    cocycles += 1

    # All 24 projective representatives have independently chosen scalar lifts.
    # Use a nonreal coefficient in every term. Extract the complete corrected
    # blocks from exact matrix sums and compare to the linear conjugate-fibre
    # prediction. Conjugating the observed mixture would conjugate coefficients.
    def msum(matrices):
        out = (zero,) * 4
        for a in matrices:
            out = tuple(add(x, y) for x, y in zip(out, a))
        return out

    chosen = []
    rays = set()
    for u in lifted:
        if u not in rays:
            rays |= {scale(z, u) for z in units}
            chosen.append(scale(units[len(chosen) % 4], u))
    require(len(chosen) == 24, "projective calibration")
    sources = (0, 1, 2)
    w = reduce(xor, sources)
    grouped = {}
    for j, u in enumerate(chosen):
        output, sigma = descents[tuple(t for t, _ in ordinary[u]), sources]
        phase = sum(bell[u][v][1] for v in sources) % 4
        c = (2 * j - 13, j + 1)
        if output not in grouped:
            grouped[output] = ([], [], [])
        observed, predicted, erroneous = grouped[output]
        observed.append(scale(mul(c, units[phase]), u))
        predicted.append(scale(mul(c, units[sigma]), conjugate(u)))
        erroneous.append(scale(mul((c[0], -c[1]), units[sigma]), conjugate(u)))
    bad_mixtures = 0
    for output, (observed, predicted, erroneous) in grouped.items():
        actual = matmul(matmul(transpose(weyl[reduce(xor, output)]), msum(observed)), weyl[w])
        require(actual == msum(predicted), "complex mixture")
        bad_mixtures += int(actual != msum(erroneous))

    require(wrong_plain and wrong_even and bad_mixtures, "mutation controls did not discriminate")
    print(f"PASS lifts=96 tuples={all_checks} odd={odd_checks} cocycles={cocycles}")
    print(f"PASS complex-mixture blocks={len(grouped)}; wrong plain singleton={wrong_plain}, "
          f"omitted even correction={wrong_even}, conjugated coefficient blocks={bad_mixtures}")


if __name__ == "__main__":
    main()
