# SPDX-License-Identifier: Apache-2.0
"""Independent finite dual certificate for the pinned PR2930 packing model.

No predecessor implementation is imported.  Powers use a positive binomial
series with directed integer rounding, rather than logarithms/exponentials.
All acceptance checks remain active when Python is run with -O.
"""

from collections import Counter
from fractions import Fraction
from functools import lru_cache
import hashlib
import json
import re


Q = Fraction
WIDTHS = (4, 5, 7, 8, 9)
CAPACITIES = (8, 16, 32, 48)
QUOTAS = (672, 448, 448, 448)
CALLS = 9
REPLICAS = 74
BASE = 73
LIVE = 896
MASS = 65088
SCALE = 10**50
TERMS = 192


def require(condition, message):
    if not condition:
        raise ValueError(message)


def integer(value, label, minimum=0):
    require(type(value) is int and value >= minimum, label + ": integer domain")
    return value


def rational(value, label):
    """Parse only an integer or a canonical nonnegative rational string."""
    require(type(value) in (int, str), label + ": rational type")
    if type(value) is str:
        require(re.fullmatch(r"(?:0|[1-9][0-9]*)(?:/[1-9][0-9]*)?", value)
                is not None, label + ": rational spelling")
    result = Q(value)
    require(result >= 0, label + ": nonnegative rational")
    return result


def histogram(raw, label, allowed):
    require(type(raw) is dict and raw, label + ": nonempty object")
    result = {}
    for key, count in raw.items():
        require(type(key) is str and re.fullmatch(r"[1-9][0-9]*", key)
                is not None, label + ": canonical rank key")
        rank = int(key)
        require(rank in allowed, label + ": rank domain")
        result[rank] = integer(count, label + ": positive multiplicity", 1)
    return result


def enumerate_patterns():
    """Recursively spend capacity on each width; every count tuple occurs once."""
    result = []

    def extend(capacity, index, remaining, counts):
        if index == len(WIDTHS):
            result.append((capacity, tuple(counts), remaining))
            return
        width = WIDTHS[index]
        for count in range(remaining // width + 1):
            extend(capacity, index + 1, remaining - width * count,
                   counts + [count])

    for capacity in CAPACITIES:
        extend(capacity, 0, capacity, [])
    return result


def column(pattern):
    capacity, counts, _ = pattern
    return [Q(capacity == c) for c in CAPACITIES] + list(map(Q, counts))


def invert(matrix):
    size = len(matrix)
    require(size > 0 and all(len(row) == size for row in matrix), "square matrix")
    rows = [[Q(v) for v in row] + [Q(i == j) for j in range(size)]
            for i, row in enumerate(matrix)]
    for j in range(size):
        pivot = next((i for i in range(j, size) if rows[i][j]), None)
        require(pivot is not None, "basis matrix is singular")
        rows[j], rows[pivot] = rows[pivot], rows[j]
        divisor = rows[j][j]
        rows[j] = [value / divisor for value in rows[j]]
        for i in range(size):
            if i != j and rows[i][j]:
                multiplier = rows[i][j]
                rows[i] = [a - multiplier * b for a, b in zip(rows[i], rows[j])]
    return [row[size:] for row in rows]


def _ceil_ratio(numerator, denominator):
    return -(-numerator // denominator)


def _unit_binomial(base, exponent):
    """Enclose (1-z)^(-b), 0<=z<=1/2, 0<=b<=1, in SCALE units.

    The nth term is (b)_n*z^n/n!.  Every term is nonnegative.  Directed
    recurrence bounds each term; the ratio of successive true terms is at
    most z, so the first omitted term divided by 1-z bounds the full tail.
    """
    require(Q(1) <= base <= 2 and 0 <= exponent <= 1, "unit binomial domain")
    z = 1 - 1 / base
    lower = upper = low_term = high_term = SCALE
    for n in range(1, TERMS + 1):
        numerator = (exponent.numerator + (n - 1) * exponent.denominator) * z.numerator
        denominator = exponent.denominator * n * z.denominator
        low_term = low_term * numerator // denominator
        high_term = _ceil_ratio(high_term * numerator, denominator)
        lower += low_term
        upper += high_term
    numerator = (exponent.numerator + TERMS * exponent.denominator) * z.numerator
    denominator = exponent.denominator * (TERMS + 1) * z.denominator
    next_upper = _ceil_ratio(high_term * numerator, denominator)
    upper += _ceil_ratio(next_upper * z.denominator, z.denominator - z.numerator)
    return lower, upper


def binomial_power(base, exponent):
    """Exact rational enclosure of base**exponent for base>=1, 0<=exponent<=1."""
    require(type(base) in (int, Q) and type(exponent) in (int, Q), "power argument type")
    base, exponent = Q(base), Q(exponent)
    require(1 <= base <= BASE and 0 <= exponent <= 1, "power argument domain")
    return _cached_binomial_power(base, exponent)


@lru_cache(maxsize=None)
def _cached_binomial_power(base, exponent):
    twos = 0
    while base > 2:
        base /= 2
        twos += 1
    low, high = _unit_binomial(base, exponent)
    if twos:
        low_two, high_two = _unit_binomial(Q(2), exponent)
        for _ in range(twos):
            low = low * low_two // SCALE
            high = _ceil_ratio(high * high_two, SCALE)
    return Q(low, SCALE), Q(high, SCALE)


def h_interval(rank, lower, upper):
    """Monotonicity gives an enclosure valid for every b in [lower,upper]."""
    integer(rank, "child rank", 1)
    require(rank < BASE and 0 <= lower <= upper <= 1, "H interval domain")
    return (rank * binomial_power(Q(BASE, rank), lower)[0],
            rank * binomial_power(Q(BASE, rank), upper)[1])


def _basis_model(cert):
    require(type(cert) is dict, "certificate object")
    local = histogram(cert.get("local_per_call"), "local profile", set(range(1, BASE)))
    inventory = histogram(cert.get("inventory_per_call"), "helper inventory", set(WIDTHS))
    require(set(inventory) == set(WIDTHS), "complete width domain")
    require(sum(inventory.values()) == 408, "408 helpers per call")
    lower = rational(cert.get("cap_lower"), "lower endpoint")
    upper = rational(cert.get("cap_upper"), "upper endpoint")
    require(0 < lower < upper < 1, "ordered positive root interval")
    raw_basis = cert.get("basis_patterns")
    require(type(raw_basis) is list and len(raw_basis) == 9, "nine basis patterns")
    basis, declared = [], []
    for entry in raw_basis:
        require(type(entry) is dict, "basis entry object")
        capacity = integer(entry.get("capacity"), "basis capacity", 1)
        require(capacity in CAPACITIES, "basis capacity domain")
        widths = entry.get("widths")
        require(type(widths) is list, "basis widths list")
        require(all(type(w) is int and w in WIDTHS for w in widths), "basis width domain")
        require(sum(widths) <= capacity, "basis capacity exceeded")
        basis.append((capacity, tuple(widths.count(w) for w in WIDTHS), capacity - sum(widths)))
        declared.append(rational(entry.get("count_per_replica"), "basis multiplicity"))
    require(len(set(basis)) == len(basis), "duplicate basis pattern")
    vectors = [column(pattern) for pattern in basis]
    matrix = [list(row) for row in zip(*vectors)]
    inverse = invert(matrix)
    rhs = list(map(Q, QUOTAS)) + [Q(CALLS * inventory[w]) for w in WIDTHS]
    counts = [sum(a * b for a, b in zip(row, rhs)) for row in inverse]
    require(all(count >= 0 for count in counts), "nonnegative basis solution")
    require(counts == declared, "declared basis counts differ from inventory solution")
    require(all(sum(matrix[i][j] * counts[j] for j in range(9)) == rhs[i]
                for i in range(9)), "nine primal inventory equalities")
    dual = []
    for i in range(9):
        prices = Counter()
        for j, pattern in enumerate(basis):
            if pattern[2]:
                prices[pattern[2]] += inverse[j][i]
        dual.append({r: value for r, value in prices.items() if value})
    return local, inventory, lower, upper, basis, counts, dual


def reduced_costs(cert):
    """Return the independently derived symbolic dual and every reduced cost."""
    model = _basis_model(cert)
    dual = model[-1]
    result = []
    for pattern in enumerate_patterns():
        coeff = Counter({pattern[2]: Q(1)}) if pattern[2] else Counter()
        for multiplicity, prices in zip(column(pattern), dual):
            for rank, price in prices.items():
                coeff[rank] -= multiplicity * price
        result.append((pattern, {rank: value for rank, value in coeff.items() if value}))
    return model, result


def _pattern_json(pattern):
    capacity, counts, residual = pattern
    return {"capacity": capacity, "counts": list(counts), "residual": residual}


def _fractions_json(values):
    return {str(key): str(value) for key, value in sorted(values.items())}


def verify_certificate(cert, profile, *, details=False):
    """Certify the supplied source-bound model; return deterministic JSON data."""
    model, costs = reduced_costs(cert)
    local, inventory, lower, upper, basis, counts, dual = model
    require(len(costs) == 1163 and len({row[0] for row in costs}) == 1163,
            "complete 1163-pattern domain")
    idle = Counter()
    for pattern, count in zip(basis, counts):
        if pattern[2] and count:
            idle[pattern[2]] += count
    require(all(count.denominator == 1 for count in counts), "integral per-replica basis")
    if "idle_per_replica" in cert:
        declared_idle = cert["idle_per_replica"]
        require(type(declared_idle) is dict, "idle profile object")
        require(all(type(k) is str and re.fullmatch(r"[1-9][0-9]*", k)
                    is not None and int(k) in range(1, BASE) for k in declared_idle),
                "idle profile rank domain")
        require({int(k): rational(v, "idle multiplicity") for k, v in declared_idle.items()}
                == dict(idle), "declared idle profile")
    expected = Counter({r: Q(CALLS * REPLICAS * n) for r, n in local.items()})
    for rank, count in idle.items():
        expected[rank] += REPLICAS * count
    actual = histogram(profile, "complete profile", set(range(1, BASE)))
    require(dict(expected) == actual, "literal complete profile equals primal profile")
    capacity_mass = sum(c * n for c, n in zip(CAPACITIES, QUOTAS))
    helper_mass = CALLS * sum(w * n for w, n in inventory.items())
    local_mass = CALLS * sum(r * n for r, n in local.items())
    idle_mass = sum(r * n for r, n in idle.items())
    require(capacity_mass - helper_mass == idle_mass, "idle rank-mass conservation")
    require(local_mass + idle_mass == MASS, "per-replica rank-mass identity")
    require(sum(r * n for r, n in actual.items()) == REPLICAS * MASS,
            "complete rank-mass identity")

    all_ranks = {r for _, coeff in costs for r in coeff}
    bounds = {r: h_interval(r, lower, upper) for r in all_ranks}
    signature, tight, strict = [], [], []
    for pattern, coeff in costs:
        row = _pattern_json(pattern)
        row["coefficients"] = _fractions_json(coeff)
        if not coeff:
            row["uniform_lower_bound"] = "0"
            tight.append(_pattern_json(pattern))
        else:
            bound = sum(value * bounds[rank][0 if value > 0 else 1]
                        for rank, value in coeff.items())
            require(bound > 0, "uniform reduced-cost sign: " + str(pattern))
            row["uniform_lower_bound"] = str(bound)
            strict.append((bound, pattern))
        signature.append(row)
    require(len(tight) == 11 and len(strict) == 1152, "eleven exact tight patterns")
    for key, expected_value in (("patterns", len(costs)), ("tight_patterns", len(tight)),
                                ("strict_patterns", len(strict))):
        if key in cert:
            require(type(cert[key]) is int and cert[key] == expected_value,
                    "declared " + key)

    endpoint_moments = {}
    for label, exponent in (("lower", lower), ("upper", upper)):
        weighted_low = weighted_high = Q(0)
        for rank, count in actual.items():
            h_low, h_high = h_interval(rank, exponent, exponent)
            weighted_low += count * h_low
            weighted_high += count * h_high
        denominator = BASE * LIVE * REPLICAS
        low, high = weighted_low / denominator, weighted_high / denominator
        require(high < 1 if label == "lower" else low > 1,
                label + " root endpoint sign")
        endpoint_moments[label] = {"exponent": str(exponent),
                                   "moment_lower": str(low), "moment_upper": str(high),
                                   "gap_lower": str(low - 1), "gap_upper": str(high - 1)}

    minimum, weakest = min(strict)
    require(minimum > Q(1, 250), "uniform slack exceeds the stated simple margin")
    receipt = {
        "status": "PASS_UNIFORM_PAIRED_CAP_OPTIMALITY",
        "model": {"widths": list(WIDTHS), "capacities": list(CAPACITIES),
                  "capacity_quotas": list(QUOTAS), "calls_per_replica": CALLS,
                  "replicas": REPLICAS, "live_per_replica": LIVE, "base": BASE,
                  "local_profile": {str(r): n for r, n in sorted(local.items())},
                  "helper_inventory": {str(w): n for w, n in sorted(inventory.items())}},
        "interval": {"lower": str(lower), "upper": str(upper)},
        "arithmetic": {"method": "positive binomial series with directed integer rounding",
                       "scale": str(SCALE), "terms": TERMS},
        "primal": {"basis": [dict(_pattern_json(pattern), count=str(count))
                              for pattern, count in zip(basis, counts)],
                   "idle_per_replica": _fractions_json(idle),
                   "complete_profile": {str(r): n for r, n in sorted(actual.items())},
                   "capacity_mass": capacity_mass, "helper_mass": helper_mass,
                   "local_mass": local_mass, "idle_mass": str(idle_mass),
                   "complete_rank_mass": REPLICAS * MASS},
        "dual": [{"row": ("capacity:" + str(CAPACITIES[i]) if i < 4
                          else "width:" + str(WIDTHS[i - 4])),
                  "coefficients": _fractions_json(prices)} for i, prices in enumerate(dual)],
        "patterns": len(costs), "tight_count": len(tight), "strict_count": len(strict),
        "tight_patterns": tight,
        "minimum_uniform_slack_lower": str(minimum),
        "simple_uniform_slack_lower": "1/250",
        "weakest_pattern": _pattern_json(weakest),
        "endpoint_moments": endpoint_moments,
        "reduced_cost_signature_sha256": hashlib.sha256(
            json.dumps(signature, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
    }
    if details:
        receipt["reduced_costs"] = signature
    return receipt
