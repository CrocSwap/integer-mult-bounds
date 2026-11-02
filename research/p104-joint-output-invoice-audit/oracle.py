#!/usr/bin/env python3
"""Independent finite invoice and one-point signed-moment oracle.

Only standard-library arithmetic is used. Frozen author files are data and are
never imported. The declared native rank tariff is a premise, not proved here.
"""
import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction
from functools import lru_cache
import gzip
from hashlib import sha1, sha256
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
KAPPA = Fraction(315057, 100000000)
GRID = 10 ** 30
LOG_GRID = 10 ** 40
LOG_TERMS = 48
EXP_EVEN_DEGREE = 16
PINNED = {
    "sources/INPUT-WORD.json.gz": ("1415a62059ed62d0b4657db91f7ec01b23c117f5f2744746d93c880bd777be92", "f21f7ac451c3f2e1ae8d5ca1dcad839a0b0d844f"),
    "sources/OUTPUT-WORD.json.gz": ("0c83c1f1dee8c9442558719510a61b89f38c2dbfc8fb565ba035660d2a68d928", "03ea7690285d4cda72815f962d5710ab96e08490"),
    "sources/CONTROLLER.json": ("6fd67eaabe659956d6694471d3fd7d2824c0a4a79cf3b8f22922f7189b11b91f", "1f2e375b24aba5fb25580dfea7fab7a2049f3eb8"),
    "sources/controller-source.py": ("8067ade84815b54d539cbaef9885db9fa4d7a23fdde2e683451d317038a8477c", "3b4bf82eba05d57ef4bb1fd934e8ca65780425c1"),
    "sources/AUTHOR-RESULT.json": ("4c9b2d2b4f0df1ed852250b6815fce62a174ce297fed04801298183afd55c7b7", "f5fc1f595607837531d0aee8c6835f55a2e2ab98"),
    "sources/NOTICE": ("6c5f4a452f7d65ef8ca0980992dce279938b0a1139f6c067f91de78bf8ecb7bd", "e6cae17f778e8e31b7c294ff2890c545978931c0"),
    "sources/tariff-source.py": ("7201df8e32f5c99f7403150e8664042322037906088bc754c67293a241368597", "b7be846b10c4c54a4e1558d7b563bc8c3a170223"),
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == ".gz" else raw)


def authenticate():
    pins = read_json(HERE / "SOURCE-PINS.json")
    require(type(pins) is list and len(pins) == 7, "seven source pins")
    require({p["file"]: (p["sha256"], p["git_blob"]) for p in pins} == PINNED,
            "independently fixed source pins")
    for filename, (digest, blob) in PINNED.items():
        raw = (HERE / filename).read_bytes()
        require(sha256(raw).hexdigest() == digest, "source SHA256: " + filename)
        require(sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest() == blob,
                "source Git blob: " + filename)


def binary_rank(vectors):
    pivots = {}
    for vector in vectors:
        require(type(vector) is int and 0 < vector < 512, "binary nine-axis vector")
        reduced = vector
        while reduced:
            pivot = (reduced & -reduced).bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = reduced
                break
            reduced ^= pivots[pivot]
    return len(pivots)


def local_profiles(word):
    public, owned = word["public"], word["owned_fields"]
    require(type(public) is int and public == 770 and type(owned) is int and owned == 29,
            "fixed public and owned role counts")
    frames = word["frames"]
    dimensions = [binary_rank(frame) for frame in frames]
    require(all(rank == len(frame) for rank, frame in zip(dimensions, frames)), "independent frame bases")
    require(len(word["initial"]) == len(word["final"]) == public, "public frame boundaries")
    active = dict(enumerate(word["initial"]))
    paid = Counter()
    for event in word["program"]:
        op, role = event[:2]
        require(type(role) is int and 0 <= role < public + owned, "literal role")
        if op == "MOVE":
            _, role, start, end, private = event
            require(type(private) is bool and private == (role >= public), "literal MOVE ownership")
            require(active.get(role) == start, "literal MOVE source frame")
            require(type(start) is int and type(end) is int and
                    0 <= start < len(frames) and 0 <= end < len(frames), "literal MOVE frame indices")
            a, b = dimensions[start], dimensions[end]
            require(binary_rank(frames[start] + frames[end]) == max(a, b), "nested MOVE subspaces")
            require(b < a if private else a < b, "strict MOVE rank direction")
            paid[abs(a - b)] += 1
            active[role] = end
        elif op == "INIT":
            require(role >= public and role not in active, "owned INIT lifetime")
            active[role] = event[2]
        elif op == "CLEAR":
            require(role >= public and active.get(role) == event[2], "owned CLEAR lifetime")
            del active[role]
        elif op in ("ADD", "COPY", "SCALE"):
            require(active.get(role) == event[-1], "scalar destination frame")
            if op != "SCALE":
                require(event[2] in active and active[event[2]] == event[-1], "scalar source frame")
        else:
            raise ValueError("unrecognized literal opcode")
    require(active == dict(enumerate(word["final"])), "literal final frames and retired owned roles")
    mains = set(word["live"]) | {role + 112 for role in word["live"]}
    require(len(word["live"]) == len(word["ports"]) == 104 and len(mains) == 208, "104 disjoint main pairs")
    increments = {dimensions[word["final"][r]] - dimensions[word["initial"][r]] for r in mains}
    require(increments == {8}, "common declared main-stage rank increment")
    targets = Counter(dimensions[word["final"][r]] - dimensions[word["initial"][r]]
                      for r in range(public) if r not in mains)
    require(min(targets) > 0 and sum(targets.values()) == 562, "562 positive helper targets")
    return paid, targets, 104, 8


def complete_profiles(word, caller):
    local_paid, local_targets, ports, increment = local_profiles(word)
    paid, targets = Counter(), Counter()
    local_stages, queries, idles = [], 0, []
    for event in caller["events"]:
        op = event[0]
        if op == "LOCAL":
            local_stages.append(event[1])
            paid.update(local_paid)
            targets.update(local_targets)
        elif op == "QUERY":
            require(event[3] in (-1, 1), "unit central thin query")
            paid[1] += ports
            queries += 1
        elif op == "IDLE":
            stages = event[3]
            require(len(stages) == len(set(stages)) and stages and
                    all(type(s) is int and 1 <= s <= caller["stages"] for s in stages), "idle stage set")
            paid[increment * len(stages)] += 2 * ports
            idles.append(len(stages))
        else:
            require(op in ("ADD", "SCALE", "SWAP", "Q_POWER"), "declared ordinary caller opcode")
    require(sorted(local_stages) == list(range(1, caller["stages"] + 1)), "each local native stage exactly once")
    require(caller["stages"] == 19 and caller["roles"] == len(caller["diagonal"]) == 34,
            "fixed nineteen-stage caller interface")
    for row in caller["diagonal"]:
        require(len(row) == caller["stages"] + 2 and row[0] in (-1, 1) and row[1] == 0 and
                all(type(bit) is int and bit in (0, 1) for bit in row[2:]), "literal target monomial")
        rank = abs(row[0]) + increment * sum(row[2:])
        targets[rank] += ports
    return paid, targets, {"local_stages": len(local_stages), "queries": queries,
                           "idle_stage_sizes": sorted(idles)}


def outward(value, grid, upper=False):
    numerator = value.numerator * grid
    rounded = -((-numerator) // value.denominator) if upper else numerator // value.denominator
    return Fraction(rounded, grid)


def atanh_log(z):
    require(0 <= z <= Fraction(1, 3), "positive reduced logarithm argument")
    square, power, partial = z * z, z, Fraction(0)
    for index in range(LOG_TERMS):
        partial += power / (2 * index + 1)
        power *= square
    lower = 2 * partial
    tail = 2 * power / ((2 * LOG_TERMS + 1) * (1 - square))
    return lower, lower + tail


@lru_cache(None)
def logarithm_bounds(rank):
    require(type(rank) is int and rank >= 1, "positive integer tariff rank")
    exponent = rank.bit_length() - 1
    power = 1 << exponent
    reduced = Fraction(rank - power, rank + power)
    lo2, hi2 = atanh_log(Fraction(1, 3))
    lo, hi = atanh_log(reduced)
    return outward(exponent * lo2 + lo, LOG_GRID), outward(exponent * hi2 + hi, LOG_GRID, True)


def alternating_exp_minus(value, degree):
    require(0 <= value <= 1, "alternating exponential decreasing-term range")
    total, term = Fraction(1), Fraction(1)
    for index in range(1, degree + 1):
        term *= -value / index
        total += term
    return total


@lru_cache(None)
def power_bounds(rank):
    lo, hi = logarithm_bounds(rank)
    # exp(-x) is decreasing. Odd Taylor partials are lower bounds and even
    # partials are upper bounds for 0 <= x <= 1.
    lower = rank * alternating_exp_minus(KAPPA * hi, EXP_EVEN_DEGREE + 1)
    upper = rank * alternating_exp_minus(KAPPA * lo, EXP_EVEN_DEGREE)
    require(lower <= upper, "ordered power enclosure")
    return outward(lower, GRID), outward(upper, GRID, True)


def moment(paid, targets):
    signed = Counter(targets)
    signed.subtract(paid)
    lower, upper = Fraction(0), Fraction(0)
    for rank, coefficient in signed.items():
        lo, hi = power_bounds(rank)
        lower += coefficient * (lo if coefficient >= 0 else hi)
        upper += coefficient * (hi if coefficient >= 0 else lo)
    require(lower <= upper, "ordered signed-moment interval")
    return lower, upper


def encoded_profile(profile):
    return {str(rank): count for rank, count in sorted(profile.items()) if count}


def difference(after, before):
    result = Counter(after)
    result.subtract(before)
    return result


def encoded_interval(interval):
    return [str(endpoint) for endpoint in interval]


def rejected(action):
    try:
        action()
    except ValueError as error:
        return str(error)
    raise ValueError("invalid control accepted")


def run():
    authenticate()
    source = read_json(HERE / "sources/INPUT-WORD.json.gz")
    final = read_json(HERE / "sources/OUTPUT-WORD.json.gz")
    caller = read_json(HERE / "sources/CONTROLLER.json")
    old_local_paid, old_local_targets, _, _ = local_profiles(source)
    new_local_paid, new_local_targets, _, _ = local_profiles(final)
    old_paid, old_targets, counts = complete_profiles(source, caller)
    new_paid, new_targets, new_counts = complete_profiles(final, caller)
    require(counts == new_counts, "unchanged fixed caller events")
    old_margin, new_margin = moment(old_paid, old_targets), moment(new_paid, new_targets)
    require(new_margin[0] > 0, "new formal bill positive at the one fixed saving")
    require(old_margin[1] < 0, "same-caller source formal bill fails at the fixed saving")
    bad = deepcopy(final)
    bad["final"][703] = 127
    debit_control = rejected(lambda: local_profiles(bad))
    ranks = sorted(set(old_paid) | set(old_targets) | set(new_paid) | set(new_targets))
    return {
        "schema_version": 1,
        "scope": "complete formal nineteen-stage signed invoice and one fixed-saving moment only",
        "saving": str(KAPPA),
        "old_local_paid": encoded_profile(old_local_paid),
        "new_local_paid": encoded_profile(new_local_paid),
        "local_paid_delta": encoded_profile(difference(new_local_paid, old_local_paid)),
        "old_local_targets": encoded_profile(old_local_targets),
        "new_local_targets": encoded_profile(new_local_targets),
        "local_target_delta": encoded_profile(difference(new_local_targets, old_local_targets)),
        "old_complete_paid": encoded_profile(old_paid),
        "new_complete_paid": encoded_profile(new_paid),
        "old_complete_targets": encoded_profile(old_targets),
        "new_complete_targets": encoded_profile(new_targets),
        "complete_paid_delta": encoded_profile(difference(new_paid, old_paid)),
        "complete_target_delta": encoded_profile(difference(new_targets, old_targets)),
        "complete_paid_jobs": sum(new_paid.values()),
        "complete_productive_fields": sum(new_targets.values()),
        "complete_rank_mass_surplus": sum(r * n for r, n in new_targets.items()) - sum(r * n for r, n in new_paid.items()),
        "caller_event_counts": counts,
        "rank_power_intervals": {str(rank): encoded_interval(power_bounds(rank)) for rank in ranks},
        "old_margin_interval": encoded_interval(old_margin),
        "new_margin_interval": encoded_interval(new_margin),
        "interval_method": {"log_atanh_terms": LOG_TERMS, "log_grid": str(LOG_GRID),
                            "exp_lower_degree": EXP_EVEN_DEGREE + 1, "exp_upper_degree": EXP_EVEN_DEGREE,
                            "power_grid": str(GRID)},
        "controls": {"missing_rank5_output_debit_rejected": debit_control,
                     "same_caller_source_fails_fixed_saving": old_margin[1] < 0},
        "limits": ["The source native rank tariff and declared independent-stage dimension contract are premises.",
                   "This is not native-operator, Laurent-caller, physical-contact or ordinary-work admission.",
                   "No crossing search, kappa admission, uniform compiler or rounded multiplication theorem is claimed."],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="emit fresh JSON without retained-receipt comparison")
    options = parser.parse_args()
    result = run()
    if not options.emit:
        retained = HERE / "ORACLE.json"
        require(retained.is_file(), "retained ORACLE.json receipt must exist")
        canonical = lambda value: json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        require(canonical(read_json(retained)) == canonical(result), "exact typed retained ORACLE.json receipt")
    print(json.dumps(result, sort_keys=True, indent=2))
