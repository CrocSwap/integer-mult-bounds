"""Check the binary stage rank bound by ordered polynomial multiplication."""

from itertools import product

type Matrix = tuple[int, ...]


def identity(n: int) -> Matrix:
    return tuple(1 << i for i in range(n))


def add(a: Matrix, b: Matrix) -> Matrix:
    return tuple(x ^ y for x, y in zip(a, b, strict=True))


def multiply(a: Matrix, b: Matrix) -> Matrix:
    rows = []
    for row in a:
        value = 0
        for i, donor in enumerate(b):
            if row & (1 << i):
                value ^= donor
        rows.append(value)
    return tuple(rows)


def rank(a: Matrix) -> int:
    pivots = [0] * len(a)
    dimension = 0
    for row in a:
        for i in reversed(range(len(a))):
            if row & (1 << i):
                if not pivots[i]:
                    pivots[i] = row
                    dimension += 1
                    break
                row ^= pivots[i]
    return dimension


def stage_product(a: Matrix, b: Matrix, c: Matrix) -> bool:
    if add(add(a, b), c) != identity(len(a)):
        return False
    ab = multiply(a, b)
    quadratic = add(add(ab, multiply(a, c)), multiply(b, c))
    return not any(quadratic) and not any(multiply(ab, c))


def valuation(a: Matrix) -> int:
    # In a successful factor the 1-primary summand is semisimple.
    return len(a) - rank(add(identity(len(a)), a))


def bound(n: int, r: int, b: int, c: int) -> int:
    return n + r + max(0, r - b) + max(0, r - c)


def attaining_blocks(
    n: int, p: int, r: int, b: int
) -> tuple[Matrix, Matrix, Matrix]:
    a = [0] * n
    middle = [0] * n
    last = [0] * n
    for i in range(p):
        a[i] = 1 << i

    c = n - p - b
    left_only = max(0, r - c)
    right_only = max(0, r - b)
    for block in range(r):
        i = p + 2 * block
        j = i + 1
        a[i] = 1 << j
        if block < left_only:
            middle[i], middle[j] = 1 << i, 1 << j
            last[i] = 1 << j
        elif block < left_only + right_only:
            middle[i] = 1 << j
            last[i], last[j] = 1 << i, 1 << j
        else:
            middle[i] = 1 << i
            last[i], last[j] = 1 << j, 1 << j

    left_singletons = b - r - left_only + right_only
    for i in range(p + 2 * r, n):
        if i < p + 2 * r + left_singletons:
            middle[i] = 1 << i
        else:
            last[i] = 1 << i
    return tuple(a), tuple(middle), tuple(last)


def check_attainment() -> int:
    checked = 0
    for n in range(1, 11):
        for p in range(n + 1):
            for r in range((n - p) // 2 + 1):
                for b in range(n - p + 1):
                    a, middle, last = attaining_blocks(n, p, r, b)
                    c = n - p - b
                    if not stage_product(a, middle, last):
                        raise ValueError(f"endpoint failed at {(n, p, r, b)}")
                    if (valuation(a), valuation(middle), valuation(last)) != (p, b, c):
                        raise ValueError(f"valuation split failed at {(n, p, r, b)}")
                    expected = (p + r, max(b, r), max(c, r))
                    if (rank(a), rank(middle), rank(last)) != expected:
                        raise ValueError(f"rank tuple failed at {(n, p, r, b)}")
                    checked += 1
    return checked


def check_exhaustive() -> tuple[int, int]:
    candidates = 0
    valuation_fibers = 0
    for n in range(1, 4):
        unit = identity(n)
        matrices = tuple(product(range(1 << n), repeat=n))
        for a in matrices:
            square = multiply(a, a)
            if square == a:
                continue
            p = rank(square)
            r = rank(add(a, square))
            minima: dict[int, int] = {}
            for b in matrices:
                c = add(add(unit, a), b)
                candidates += 1
                if stage_product(a, b, c):
                    middle = valuation(b)
                    if valuation(a) != p or valuation(c) != n - p - middle:
                        raise ValueError(f"valuation partition failed at {(a, b, c)}")
                    total = rank(a) + rank(b) + rank(c)
                    minima[middle] = min(minima.get(middle, total), total)

            expected = {}
            if multiply(a, square) == square:
                expected = {
                    b: bound(n, r, b, n - p - b) for b in range(n - p + 1)
                }
            if minima != expected:
                raise ValueError(f"minimum ranks differ at {a}: {minima} != {expected}")
            valuation_fibers += len(minima)
    return candidates, valuation_fibers


def main() -> None:
    a, b, c = attaining_blocks(2, 0, 1, 1)
    if stage_product(a, c, b):
        raise ValueError("reversed companion order was accepted")

    candidates, fibers = check_exhaustive()
    witnesses = check_attainment()
    print(
        "PASS_PAIRED_STAR_FACTOR_RANK "
        f"pairs={candidates} fibers={fibers} witnesses={witnesses} controls=1"
    )


if __name__ == "__main__":
    main()
