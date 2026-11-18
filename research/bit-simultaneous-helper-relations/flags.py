"""Certify the full prefix intersections and the prices charged to helper pivots."""
from collections import Counter
from dataclasses import dataclass
from hashlib import sha256

from word import require

# Zero-based terminal birth positions. Each swap lies inside one equal-price run.
TRANSPOSE_SWAPS = ((365, 156), (401, 237), (380, 200),
                   (409, 329), (296, 251), (376, 162))

# 27 times r^t when 2^t = 5/3.
PRICE = {1: 27, 2: 45, 4: 75, 8: 125}


@dataclass(frozen=True)
class Birth:
    position: int
    signal: int
    rank: int


def clean_flag(bank, mask):
    """A basis of span(bank[:j]) intersect mask, simultaneously for every j."""
    outside = {}
    births = []
    for position, bank_row in enumerate(bank):
        signal = bank_row.signal
        while signal & ~mask:
            pivot = (signal & ~mask).bit_length() - 1
            if pivot not in outside:
                outside[pivot] = signal
                break
            signal ^= outside[pivot]
        else:
            require(signal != 0, "original bank dependence")
            births.append(Birth(position, signal, bank_row.rank))
    return births


@dataclass
class Flags:
    individual: list
    all_helpers: list
    mixed_end: bool


def decompose(banks, masks):
    """Check the two sides of every possible above-unit-price birth."""
    total_mask = sum(masks)
    largest_mask = masks[0]
    result = {}
    mixed_prefix_charts = {}
    mixed_end_charts = {}
    possible_paid = Counter()
    high_births = 0
    prefix_count = 0
    for chart, bank in sorted(banks.items()):
        require(not clean_flag(bank, 0), "independent complete bank")
        whole = clean_flag(bank, total_mask)
        small = clean_flag(bank, total_mask ^ largest_mask)
        parts = [clean_flag(bank, mask) for mask in masks]
        possible_paid.update(row.rank for row in whole if row.rank > 0)
        whole_at = {row.position for row in whole}
        small_at = {row.position for row in small}
        pure_at = Counter(row.position for part in parts for row in part)
        small_pure_at = Counter(row.position for part in parts[1:] for row in part)
        defect = 0
        maximum = 0
        for j, token in enumerate(bank):
            before = defect
            defect += int(j in whole_at) - pure_at[j]
            require(defect >= 0, "negative mixed dimension")
            maximum = max(maximum, defect)
            # Increment equality at each prefix implies direct decomposition on the small blocks.
            require(int(j in small_at) == small_pure_at[j], "mixed small-block flag")
            if token.rank == 0:
                require(defect == 0, "mixed free prefix")
            elif token.rank > 1 and j in whole_at:
                require(before == defect == 0, "mixed flag at a higher-price birth")
                high_births += 1
        if maximum:
            mixed_prefix_charts[chart] = maximum
        if defect:
            require(all(row.rank == 1 for row in whole), "mixed final chart has a nonunit birth")
            mixed_end_charts[chart] = defect
        result[chart] = Flags(parts, whole, bool(defect))
        prefix_count += len(bank)
    return result, {"receiver_charts": len(banks), "bank_prefixes": prefix_count,
                    "mixed_prefix_maximum_by_chart": mixed_prefix_charts,
                    "mixed_end_dimension_by_chart": mixed_end_charts,
                    "separated_higher_rank_births": high_births,
                    "paid_omittable_with_all_helpers_zero": dict(sorted(possible_paid.items()))}


def make_decoder(ordered_signals):
    """Express an exact helper signal in the ordered basis of its own group."""
    basis = {}
    for i, signal in enumerate(ordered_signals):
        tag = 1 << i
        while signal:
            pivot = signal.bit_length() - 1
            if pivot not in basis:
                basis[pivot] = (signal, tag)
                break
            previous, coordinates = basis[pivot]
            signal ^= previous
            tag ^= coordinates
        else:
            raise ValueError("dependent helper coordinates")

    def convert(signal):
        result = 0
        while signal:
            pivot = signal.bit_length() - 1
            require(pivot in basis, "signal outside helper block")
            previous, coordinates = basis[pivot]
            signal ^= previous
            result ^= coordinates
        return result

    return convert


def group_basis(roles, terminal, physical_coordinates, swaps=()):
    require(len(terminal) == len(roles) and all(row.rank > 0 for row in terminal),
            "complete paid terminal flag")
    if physical_coordinates:
        return [1 << i for i in roles], [max(row.rank for row in terminal)] * len(roles)
    signals = [row.signal for row in terminal]
    ranks = [row.rank for row in terminal]
    for i, j in swaps:
        require(0 <= min(i, j) <= max(i, j) < len(ranks), "terminal swap bounds")
        require(len(set(ranks[min(i, j):max(i, j) + 1])) == 1, "terminal tariff run")
        signals[i], signals[j] = signals[j], signals[i]
    return signals, ranks


def signal_prices(rows, mask=None):
    """List every small-space signal and its chronological price.

    On a projected mixed receiver, the entire space has unit price. Projections
    can repeat or vanish. Every original clean flag consists of independent births.
    """
    values = {0: 0}
    for row in rows:
        v = row.signal
        if mask is not None:
            require(row.rank == 1, "projected nonunit bank")
            v &= mask
        if v in values:
            require(mask is not None, "dependent original clean basis")
            continue
        addition = {x ^ v: row.rank for x in values}
        values.update(addition)
    del values[0]
    return values


def charge_group(number, boundary, roles, masks, flags, frames, transpose):
    a, d = boundary
    target_rank = abs(frames[a] - frames[d])
    largest = number == 0
    physical = largest and not transpose
    swaps = TRANSPOSE_SWAPS if largest and transpose else ()
    basis, terminal_prices = group_basis(roles, flags[d].individual[number], physical, swaps)
    convert = make_decoder(basis)
    charges = [[r] for r in terminal_prices]
    largest_local_dimension = 0
    for chart, receiver in flags.items():
        if chart in (a, d):
            require(not receiver.mixed_end, "mixed boundary would require a separate charge")
            continue
        if largest and receiver.mixed_end:
            prices = signal_prices(receiver.all_helpers, masks[0])
        else:
            prices = signal_prices(receiver.individual[number])
        largest_local_dimension = max(largest_local_dimension, len(prices).bit_length())
        by_pivot = {}
        for signal, price in prices.items():
            require(price > 0, "nonterminal paid rank")
            pivot = convert(signal).bit_length() - 1
            by_pivot[pivot] = max(by_pivot.get(pivot, 0), price)
        for pivot, price in by_pivot.items():
            charges[pivot].append(price)

    profiles = [tuple(sorted(profile)) for profile in charges]
    counts = Counter(profiles)
    require(all(0 < r <= target_rank for profile in profiles for r in profile), "normalized price monotonicity")
    if target_rank == 6:
        require(len(roles) == 1 and counts == {(1, 4): 1}, "unique exceptional rank-six tariff")
        max_price = None
    else:
        max_price = max(sum(PRICE[r] for r in profile) for profile in profiles)
        require(max_price <= PRICE[target_rank], "coordinate price exceeds its target")
        if largest:
            require(max_price < PRICE[target_rank], "strict charge on large helper block")
    neutral = [i for i, profile in enumerate(profiles) if profile == (target_rank,)]
    if target_rank != 6:
        require(all(sum(PRICE[r] for r in profile) < PRICE[target_rank]
                    for i, profile in enumerate(profiles) if i not in neutral), "strict nonneutral tariff")
    ordered = "".join(",".join(map(str, profile)) + "\n" for profile in profiles)
    return {"ordered_profiles_sha256": sha256(ordered.encode("ascii")).hexdigest(),
            "entrance": a, "exit": d, "dimension": len(roles), "target_rank": target_rank,
            "neutral_pivot_indices": neutral,
            "nonterminal_dimension_max": largest_local_dimension,
            "max_numerator_over_27": max_price,
            "profile_counts": {",".join(map(str, p)): n for p, n in sorted(counts.items())}}


def charge_orientation(banks, groups, frames, transpose):
    masks = [sum(1 << i for i in roles) for roles in groups.values()]
    require(sorted(map(len, groups.values())) == [1, 1, 2, 2, 3, 5, 6, 7, 410],
            "all 437 helpers in the nine boundary groups")
    flags, result = decompose(banks, masks)
    result["groups"] = [charge_group(i, boundary, roles, masks, flags, frames, transpose)
                        for i, (boundary, roles) in enumerate(groups.items())]
    return result
