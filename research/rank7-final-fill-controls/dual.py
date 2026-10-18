# SPDX-License-Identifier: Apache-2.0
"""Independent packing lower bound; integer square roots enclose tariffs.

No optimizer, predecessor interval engine, or numerical root search is used.
Vectors below express dual potentials as rational linear combinations of
t_r = r**(1-a). Their constraints are checked on every admissible pattern.
"""

from collections import Counter
from fractions import Fraction as F
from math import isqrt

from allocation import digest
from local import need

BITS = 256
EXPONENT_BITS = 128
Q = 1 << BITS
WIDTHS = (4, 5, 6, 7, 8, 9)
CAPACITIES = (8, 16, 32, 48)


def ceil_div(n, d):
    return -(-n // d)


def ceil_sqrt(n):
    root = isqrt(n)
    return root + (root * root != n)


def tariff(rank, saving):
    """Return integer bounds divided by Q for rank**(1-saving)."""
    need(type(rank) is int and 0 <= rank <= 73, "tariff rank bound")
    need(F(0) <= saving < F(1), "tariff saving domain")
    if rank == 0:
        return 0, 0
    scaled = saving * (1 << EXPONENT_BITS)
    exponent = scaled.numerator // scaled.denominator
    low = high = Q
    root_low = root_high = rank * Q
    for j in range(EXPONENT_BITS):
        root_low = isqrt(root_low * Q)
        root_high = ceil_sqrt(root_high * Q)
        if exponent & (1 << (EXPONENT_BITS - 1 - j)):
            low = low * root_low // Q
            high = ceil_div(high * root_high, Q)
    if scaled != exponent:
        high = ceil_div(high * root_high, Q)
    return rank * Q * Q // high, ceil_div(rank * Q * Q, low)


def linear(*terms):
    """Sum (rational coefficient, sparse tariff vector) terms."""
    result = Counter()
    for coefficient, vector in terms:
        for rank, value in vector.items():
            result[rank] += F(coefficient) * value
    return {r: q for r, q in result.items() if q}


def unit(rank):
    return {rank: F(1)} if rank else {}


def interval(vector, tariffs):
    lower = upper = F(0)
    for rank, coefficient in vector.items():
        lo, hi = tariffs[rank]
        lower += coefficient * (lo if coefficient > 0 else hi) / Q
        upper += coefficient * (hi if coefficient > 0 else lo) / Q
    return lower, upper


def potentials():
    # These solve the ten source basis equalities. The verification below
    # checks those equalities symbolically, as well as every inequality.
    p9 = linear((F(1, 5), unit(3)), (-F(1, 5), unit(48)))
    p8 = linear((F(3, 4), p9), (-F(1, 4), unit(5)))
    p7 = linear((2, p8), (-1, p9))
    p6 = linear((3, p8), (-2, p9))
    p5 = linear((-1, unit(5)))
    p4 = linear((1, unit(1)), (4, p8), (-3, p9))
    alpha = {8: linear((-1, p8)), 16: linear((-2, p8)),
             32: linear((-4, p8)), 48: unit(48)}
    return alpha, {4: p4, 5: p5, 6: p6, 7: p7, 8: p8, 9: p9}


def patterns(capacity):
    # Finite dynamic enumeration of the established six-width alphabet.
    states = [(0, ())]
    for width in WIDTHS:
        states = [(used + count * width, old + (count,))
                  for used, old in states
                  for count in range((capacity - used) // width + 1)]
    return states


def check(source, local_profile, inventory, windows, saving):
    need(source["local_per_call"] == {str(k): v for k, v in local_profile.items()},
         "cap certificate local binding")
    need(source["inventory_per_call"] == {str(k): v for k, v in inventory.items()},
         "cap certificate width binding")
    tariffs = {r: tariff(r, saving) for r in range(74)}
    alpha, pi = potentials()
    tight, strict_lowers, records = [], [], []
    for capacity in CAPACITIES:
        for used, counts in patterns(capacity):
            slack = linear((1, unit(capacity - used)), (-1, alpha[capacity]),
                           *((-n, pi[w]) for w, n in zip(WIDTHS, counts, strict=True)))
            record = [capacity, list(counts)]
            records.append(record)
            if not slack:
                tight.append(record)
            else:
                lo, _hi = interval(slack, tariffs)
                need(lo > 0, "dual inequality on every packing pattern")
                strict_lowers.append(lo)
    need(len(records) == source["patterns"] == 2551, "complete fixed pattern domain")
    need(len(tight) == source["tight_patterns"] == 12, "symbolically tight patterns")
    for row in source["basis_patterns"]:
        capacity = row["capacity"]
        counts = Counter(row["widths"])
        slack = linear((1, unit(capacity - sum(row["widths"]))), (-1, alpha[capacity]),
                       *((-n, pi[w]) for w, n in counts.items()))
        need(not slack, "literal source basis is tight for these potentials")
    total_capacities = Counter(cap for cap, _start, _stop in windows.values())
    bins_per_replica = {cap: F(n * 112, 74) for cap, n in total_capacities.items()}
    need(set(bins_per_replica) == set(CAPACITIES), "same bin alphabet")
    lower_bill = linear(*((count, alpha[cap]) for cap, count in bins_per_replica.items()),
                        *((9 * count, pi[w]) for w, count in inventory.items()),
                        *((9 * count, unit(r)) for r, count in local_profile.items()))
    margin = linear((1, lower_bill), (-896, unit(73)))
    change = linear((1, unit(1)), (1, pi[8]), (-1, pi[7]))
    split = {1: F(1), 3: F(1, 20), 5: F(1, 4), 48: -F(1, 20)}
    need(change == split, "symbolic terminal-widening cost direction")
    cases = []
    for widened in range(5):
        lo, hi = interval(linear((1, margin), (9 * widened, change)), tariffs)
        if widened:
            need(lo > 0, "control fails even the complete packing relaxation")
        else:
            need(hi < 0, "baseline relaxation has headroom at the actual claim")
        record = dict(widened_count=widened, lower=str(lo), upper=str(hi),
                      all_packings_rejected=lo > 0)
        if widened:
            bound = 1 + lo / (896 * F(tariffs[73][1], Q))
            record["complete_moment_lower_bound"] = str(bound)
            scaled = bound.numerator * 10**12 // bound.denominator
            record["complete_moment_lower_decimal"] = f"{scaled // 10**12}.{scaled % 10**12:012d}"
        cases.append(record)
    # Bind the displayed fractional primal to the actual bin and helper totals.
    actual = Counter()
    for row in source["basis_patterns"]:
        count = F(row["count_per_replica"])
        need(count >= 0, "nonnegative source basis counts")
        actual[row["capacity"]] += count
    need(dict(actual) == bins_per_replica, "source primal bin totals")
    widths = Counter()
    for row in source["basis_patterns"]:
        for width in row["widths"]:
            widths[width] += F(row["count_per_replica"])
    need(widths == Counter({w: 9 * n for w, n in inventory.items()}),
         "source primal helper totals")
    return dict(saving=str(saving), interval_method="integer square roots; 256-bit tariff grid, 128 exponent bits",
                pattern_count=len(records), tight_patterns=tight,
                patterns_sha256=digest(records), minimum_strict_slack_lower=str(min(strict_lowers)),
                bins_per_replica={str(k): str(v) for k, v in sorted(bins_per_replica.items())},
                cost_direction={str(r): str(q) for r, q in sorted(change.items())},
                per_occurrence_extra_cost_interval=[str(v) for v in interval(change, tariffs)],
                per_replica_excess_over_896_times_73_power=cases)


def check_actual_bill(profile, saving):
    tariffs = {r: tariff(r, saving) for r in set(profile) | {73}}
    margin = linear(*((F(n, 74), unit(r)) for r, n in profile.items()),
                    (-896, unit(73)))
    lo, hi = interval(margin, tariffs)
    need(hi < 0, "actual baseline complete moment passes at the source saving")
    return [str(lo), str(hi)]
