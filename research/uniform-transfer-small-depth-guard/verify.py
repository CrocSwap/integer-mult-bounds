#!/usr/bin/env python3
"""Exact low-end audit of the pinned base-m recursive row splitter."""

M = 1_000_000
W = 1_873_807_244_643_542_670_000


def ceil_log(base: int, value: int) -> int:
    """Return ceil(log_base(value)) using integer multiplication only."""
    if base < 2 or value < 1:
        raise ValueError("base must be >=2 and value must be positive")
    power = 1
    exponent = 0
    while power < value:
        power *= base
        exponent += 1
    return exponent


def q0(d: int) -> int:
    if d < 1:
        raise ValueError("d must be positive")
    return ceil_log(2, W) * ceil_log(M, 2 * d)


def leaf(d: int, e: int) -> bool:
    """Pinned beta=1/2 stop predicate, compared without square roots."""
    if d < 1 or e < 1:
        raise ValueError("d and e must be positive")
    return e * e < d


def base_m_pieces(n: int) -> list[tuple[int, int]]:
    """Return (piece_size, multiplicity) from the base-M expansion."""
    if n < 0:
        raise ValueError("piece count must be nonnegative")
    pieces = []
    place = 1
    while n:
        n, digit = divmod(n, M)
        if digit:
            pieces.append((place, digit))
        place *= M
    return list(reversed(pieces))


def main() -> None:
    # Exact network constant: 2^70 < W < 2^71.
    assert 2**70 < W < 2**71
    assert ceil_log(2, W) == 71

    # The degenerate d=1 endpoint is outside the stop predicate's safe range,
    # but the retained D<=q0 fallback handles its only allowed D.
    assert q0(1) == 71
    assert not leaf(1, 1)
    assert 1 <= q0(1)

    # First nonempty remainder: a single unit piece, which is a strict leaf.
    assert q0(71) == q0(72) == 71
    assert 72 - q0(72) == 1
    assert base_m_pieces(72 - q0(72)) == [(1, 1)]
    assert leaf(72, 1)

    # Exact equality is not a leaf: this is the control for the strict '<'.
    assert not leaf(4, 2)
    assert leaf(2, 1)

    # Before d=1,000,142, the largest possible remainder is less than M:
    # q0=71 on [1,500000], and q0=142 on [500001,1000141].
    assert q0(1) == q0(500_000) == 71
    assert q0(500_001) == q0(1_000_141) == 142
    assert 500_000 - 71 == 499_929 < M
    assert 1_000_141 - 142 == 999_999 < M

    # At the first possible internal node, D=d and D-q0=M exactly.
    d = 1_000_142
    assert q0(d) == 142
    assert 2 * d > M and 2 * d < M**2
    assert d - q0(d) == M
    assert base_m_pieces(d - q0(d)) == [(M, 1)]
    assert not leaf(d, M)  # one internal node of size M
    assert M * M >= d
    assert leaf(d, 1)  # each recursive child is a leaf

    print("PASS_UNIFORM_TRANSFER_SMALL_DEPTH_GUARD")


if __name__ == "__main__":
    main()
