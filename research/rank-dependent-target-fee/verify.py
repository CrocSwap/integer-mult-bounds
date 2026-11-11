#!/usr/bin/env python3
"""Exact checks for the rank-dependent target-fee theorems.

The all-rank statements are the written proof. This file checks the closed
forms against every integer partition on a finite grid, checks the explicit
witnesses, and runs hypothesis-failure controls. Nothing here is a search
for a better kappa.
"""

from fractions import Fraction


R_MAX = 18
D_VALUES = (
    Fraction(-2),
    Fraction(-1),
    Fraction(-1, 2),
    Fraction(-1, 3),
    Fraction(0),
    Fraction(1, 2),
    Fraction(1),
    Fraction(3, 2),
    Fraction(2),
)
C_VALUES = tuple(Fraction(n, 2) for n in range(0, 7))
NEGATIVE_D = tuple(d for d in D_VALUES if d < 0)


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def partitions(rank):
    """Nondecreasing positive integer partitions of rank."""
    out = []

    def rec(remain, max_part, acc):
        if remain == 0:
            out.append(tuple(acc))
            return
        for part in range(1, min(max_part, remain) + 1):
            acc.append(part)
            rec(remain - part, part, acc)
            acc.pop()

    rec(rank, rank, [])
    return out


def harmonic(n):
    return sum((Fraction(1, k) for k in range(1, n + 1)), Fraction(0))


def identity(n):
    return Fraction(n)


def cap3(n):
    return Fraction(min(n, 3))


def bow(n, scale=R_MAX):
    return Fraction(n * (2 * scale - n))


def saturating(n):
    return Fraction(n, n + 1)


TARIFFS = {
    "identity": identity,
    "harmonic": harmonic,
    "cap3": cap3,
    "bow": bow,
    "saturating": saturating,
}


def is_concave_nondecreasing(phi, rank):
    values = [phi(n) for n in range(rank + 1)]
    if values[0] != 0:
        return False
    diffs = [values[i + 1] - values[i] for i in range(rank)]
    return all(delta >= 0 for delta in diffs) and all(
        diffs[i + 1] <= diffs[i] for i in range(rank - 1)
    )


def balanced_parts(rank, pieces):
    quotient, remainder = divmod(rank, pieces)
    parts = (quotient + 1,) * remainder + (quotient,) * (pieces - remainder)
    return tuple(sorted(parts, reverse=True))


def extreme_parts(rank, pieces):
    return (rank - pieces + 1,) + (1,) * (pieces - 1)


def phi_sum(phi, parts):
    return sum((phi(part) for part in parts), Fraction(0))


def delta_symmetric(phi, parts, slope, fee):
    """Every piece, including the unsplit target, pays fee + slope * phi."""
    rank = sum(parts)
    total = phi_sum(phi, parts)
    return (1 - slope) * (total - phi(rank)) - (len(parts) - 1) * fee


def delta_extra(phi, parts, slope, fee):
    """Only the k-1 extra pieces pay; the free piece is chosen optimally."""
    rank = sum(parts)
    total = phi_sum(phi, parts)
    values = [phi(part) for part in parts]
    free = max(values) if slope >= 0 else min(values)
    return (1 - slope) * total + slope * free - (len(parts) - 1) * fee - phi(rank)


def balanced_phi_sum(phi, rank, pieces):
    quotient, remainder = divmod(rank, pieces)
    return remainder * phi(quotient + 1) + (pieces - remainder) * phi(quotient)


def symmetric_prediction(phi, rank, slope, fee):
    if slope >= 1:
        return Fraction(0)
    scale = 1 - slope

    def scaled(n, scale=scale):
        return scale * phi(n)

    pieces = 1
    while pieces < rank and (
        balanced_phi_sum(scaled, rank, pieces + 1) - balanced_phi_sum(scaled, rank, pieces) > fee
    ):
        pieces += 1
    return balanced_phi_sum(scaled, rank, pieces) - scaled(rank) - (pieces - 1) * fee


def two_split_gain(phi, rank, slope):
    """Best c-free gain of a 2-split under the extra-piece rule, slope >= 0."""
    best = None
    for small in range(1, rank // 2 + 1):
        gain = phi(rank - small) + (1 - slope) * phi(small) - phi(rank)
        if best is None or gain > best:
            best = gain
    return best


def check_grid():
    partition_rows = 0
    comparisons = 0
    for name, phi in TARIFFS.items():
        require(is_concave_nondecreasing(phi, R_MAX), name + " is not an allowed tariff")
        cache = {rank: partitions(rank) for rank in range(1, R_MAX + 1)}
        for rank, rows in cache.items():
            partition_rows += len(rows)
            by_pieces = {}
            sums = {}
            for parts in rows:
                sums[parts] = phi_sum(phi, parts)
                by_pieces.setdefault(len(parts), []).append(parts)
            for pieces, group in by_pieces.items():
                total_values = [sums[parts] for parts in group]
                require(
                    max(total_values) == sums[balanced_parts(rank, pieces)],
                    f"balanced sum is not maximal: {name} R={rank} k={pieces}",
                )
                require(
                    min(total_values) == sums[extreme_parts(rank, pieces)],
                    f"extreme sum is not minimal: {name} R={rank} k={pieces}",
                )
                if pieces >= 3:
                    largest = max(extreme_parts(rank, pieces))
                    for parts in group:
                        ordered = tuple(sorted(parts))
                        charged = ordered[:-1]
                        require(
                            all(part <= (rank - 1) // 2 for part in charged),
                            f"charged part exceeds (R-1)/2: {name} {parts}",
                        )
                        windows = sum((phi(rank) - phi(rank - part) for part in charged), Fraction(0))
                        require(
                            windows <= phi(rank) - phi(ordered[-1]),
                            f"suffix windows exceed the tail: {name} {parts}",
                        )
                    del largest
            for slope in D_VALUES:
                symmetric_by_parts = {
                    parts: delta_symmetric(phi, parts, slope, 0) for parts in rows
                }
                extra_by_parts = {
                    parts: delta_extra(phi, parts, slope, 0) for parts in rows
                }
                for fee in C_VALUES:
                    comparisons += 1
                    symmetric = [
                        symmetric_by_parts[parts] - (len(parts) - 1) * fee for parts in rows
                    ]
                    require(
                        max(symmetric) == symmetric_prediction(phi, rank, slope, fee),
                        f"symmetric closed form mismatch: {name} R={rank} d={slope} c={fee}",
                    )
                    if slope < 1:
                        for pieces, group in by_pieces.items():
                            best = max(
                                symmetric_by_parts[parts] - (pieces - 1) * fee for parts in group
                            )
                            predicted = delta_symmetric(
                                phi, balanced_parts(rank, pieces), slope, fee
                            )
                            require(
                                best == predicted,
                                f"symmetric k-split is not balanced: {name} R={rank} k={pieces} d={slope}",
                            )
                    else:
                        require(
                            max(symmetric) <= 0,
                            f"d>=1 symmetric split pays: {name} R={rank} d={slope} c={fee}",
                        )
                    if slope >= 0 and rank >= 2:
                        extra = [
                            extra_by_parts[parts] - (len(parts) - 1) * fee for parts in rows
                        ]
                        pays = max(extra) > 0
                        predicted_pays = two_split_gain(phi, rank, slope) > fee
                        require(
                            pays == predicted_pays,
                            f"extra-piece halving test mismatch: {name} R={rank} d={slope} c={fee}",
                        )
                        if slope >= 1:
                            require(
                                max(extra) <= 0,
                                f"d>=1 extra-piece split pays: {name} R={rank} d={slope} c={fee}",
                            )
            for slope in NEGATIVE_D:
                if rank < 3:
                    continue
                two = max(delta_extra(phi, parts, slope, 0) for parts in rows if len(parts) == 2)
                threshold = max(two, Fraction(0))
                for parts in rows:
                    pieces = len(parts)
                    if pieces < 3:
                        continue
                    cap = delta_extra(phi, parts, slope, 0) / (pieces - 1)
                    require(
                        cap <= threshold,
                        f"negative-slope census gap: {name} R={rank} d={slope} parts={parts}",
                    )
    return partition_rows, comparisons


def check_witnesses():
    # Reading B, positive slope: balanced is strictly worse than an extreme split.
    linear_balanced = delta_extra(identity, (2, 2, 2), Fraction(1, 2), 0)
    linear_extreme = delta_extra(identity, (4, 1, 1), Fraction(1, 2), 0)
    require(linear_balanced == -2 and linear_extreme == -1, "linear balanced witness moved")
    require(linear_extreme > linear_balanced, "linear witness does not separate balanced")

    # Same rule, negative slope.
    rebate_balanced = delta_extra(identity, (2, 2, 2), -1, 0)
    rebate_extreme = delta_extra(identity, (4, 1, 1), -1, 0)
    require(rebate_balanced == 4 and rebate_extreme == 5, "negative-slope witness moved")

    # Harmonic: the best extra-piece split is not a 2-split, but a 2-split still pays.
    unbalanced = delta_extra(harmonic, (4, 1, 1), Fraction(1, 2), 0)
    balanced = delta_extra(harmonic, (2, 2, 2), Fraction(1, 2), 0)
    pair = delta_extra(harmonic, (4, 2), Fraction(1, 2), 0)
    require(unbalanced == Fraction(19, 30), "harmonic (4,1,1) gain moved")
    require(balanced == Fraction(11, 20), "harmonic balanced gain moved")
    require(pair == Fraction(23, 60), "harmonic (4,2) gain moved")
    require(unbalanced > pair > 0 and unbalanced > balanced, "harmonic comparison failed")

    # Reading A, slope > 1: the extreme split loses strictly less than the balanced split.
    loss_balanced = delta_symmetric(harmonic, (2, 2, 2), 2, 0)
    loss_extreme = delta_symmetric(harmonic, (4, 1, 1), 2, 0)
    require(loss_balanced == Fraction(-41, 20), "symmetric balanced loss moved")
    require(loss_extreme == Fraction(-49, 30), "symmetric extreme loss moved")
    require(loss_extreme > loss_balanced, "extreme is not the smaller symmetric loss")
    require(loss_extreme < 0 and loss_balanced < 0, "d>1 losses must stay negative")


def check_failure_controls():
    def bumpy(n):
        return Fraction((0, 0, 1, 1, 1, 1, 2)[n])

    require(not is_concave_nondecreasing(bumpy, 6), "bumpy control became concave")
    # Halving gain is 0, but the balanced three-way split gains 1 when d=c=0.
    halving = bumpy(3) + bumpy(3) - bumpy(6)
    three = delta_symmetric(bumpy, (2, 2, 2), 0, 0)
    require(halving == 0 and three == 1, "nonconcave control no longer separates the halving test")

    # A negative flat fee lets a d>=1 split pay, so c>=0 is necessary.
    # Reading B needs a more negative fee: its d>=1 gain is -(k-1)(d+c)
    # on the identity tariff.
    paid = delta_symmetric(identity, (1, 3), 2, -1)
    extra_paid = delta_extra(identity, (1, 3), 2, -3)
    require(paid == 1 and extra_paid == 1, "negative-fee control no longer pays")


def main():
    check_witnesses()
    check_failure_controls()
    partition_rows, comparisons = check_grid()
    print(
        "PASS_RANK_DEPENDENT_TARGET_FEE"
        f" partitions={partition_rows} comparisons={comparisons}"
        f" R<={R_MAX} tariffs={len(TARIFFS)}"
    )


if __name__ == "__main__":
    main()
