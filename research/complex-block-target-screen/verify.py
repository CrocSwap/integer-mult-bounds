#!/usr/bin/env python3
"""Conditional late-block target screen. Apache-2.0.

Jose Manuel (@jmbarrancoml), with substantial OpenAI Codex assistance.
The 99th-root oracle imports no predecessor arithmetic. Default replay is read-only.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from functools import lru_cache
from hashlib import sha256
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BLOCK = "research/complex-block-rank-optimum/"
CEILING = "research/complex-local-word-ceiling/"
TARGET = Q(1, 99)
M, FAMILIES, STAGES, CENTRE, CAP = 73, 896, 9, 64, 51
W = Q(FAMILIES, STAGES)
TOTAL = (M-1)*W + CENTRE
MINIMA = {4: {1: 24, 2: 8, 3: 4}, 5: {1: 32, 4: 4}}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def mass(profile):
    return sum(r*n for r, n in profile.items())


def integer_profile(raw):
    require(isinstance(raw, dict), "Profile must be a dictionary")
    result = {}
    for r, n in raw.items():
        require(isinstance(r, str) and r.isdecimal() and str(int(r)) == r,
                "Noncanonical rank")
        require(type(n) is int and n >= 0, "Count must be a nonnegative integer")
        result[int(r)] = n
    return result


def check_pins():
    sources = json.loads((HERE / "SOURCES.json").read_text())
    for item in sources["files"]:
        if item["usage"] == "input":
            require(sha256((ROOT / item["path"]).read_bytes()).hexdigest() == item["sha256"],
                    "Source drift: " + item["path"])


def read_inputs(certificate, planning):
    sources = [s for s in certificate["sources"] if s["file"] == "inputs/selected.json.gz"]
    require(len(sources) == 1, "Missing or duplicate selected source")
    selected = sources[0]
    require(selected["source_sha256"] == "4ddb29fb9bc6f27e0c0fbfcf19a2a93a3496ad900d0f6d89059d0305c9576c0c",
            "Wrong selected word")
    counts, combined, seen = Counter(), Counter(), set()
    for block in selected["blocks"]:
        u = block["common_rank"]
        require(type(u) is int and u in MINIMA, "Unsupported common rank")
        require(block["base"] not in seen, "Repeated block")
        seen.add(block["base"])
        low, high = block["low"], block["high"]
        require(len(low) == len(high) == 4 and not set(low).intersection(high)
                and sorted(low + high) == list(range(block["base"], block["base"]+8)),
                "Wrong eight-array split")
        profile = integer_profile(block["profile"])
        require(profile == MINIMA[u], "Block minimum profile changed")
        require(mass(profile) == 4*(9-1)+4*(9-u), "Non-telescoping block mass")
        combined.update(profile)
        counts[u] += 1
    require(counts == {4: 7, 5: 5}, "Wrong selected block inventory")
    require(dict(combined) == integer_profile(selected["total_profile"]), "Wrong aggregate block profile")
    contract = certificate["orientation_contract"]
    require(contract["contract"] == "same-order-inverse-transpose-from-one-canonical-word",
            "Orientation contract changed")
    require(contract["equal_climb_events"] == 3486, "Orientation climb binding changed")
    local = integer_profile(planning["selected"]["local_profile_per_call"])
    require(local == integer_profile(contract["equal_complete_profile"]), "Local profile sources disagree")
    model = planning["model"]
    require((model["m"], model["stages"], model["centre_per_call"], model["idle_rank_cap"])
            == (M, STAGES, CENTRE, CAP), "Planning model changed")
    require(Q(model["live_families_per_call"]) == W, "Live-family normalization changed")
    require(local[8] == 8 and mass(local) == 5586 and mass(combined) == 604,
            "Selected local or centre invoice changed")
    require(TOTAL == 7232 and Q(planning["selected"]["idle_mass_per_call"]) == TOTAL-mass(local),
            "Coverage mass disagrees")
    return dict(counts)


def profile(i, j, centres=True):
    result = Counter({8: 8} if centres else {})
    for u, count in ((4, i), (5, j)):
        result.update({r: count*n for r, n in MINIMA[u].items()})
    return {r: n for r, n in result.items() if n}


@lru_cache(None)
def root_cost(rank, bits=160):
    """Exact enclosure of (rank/73)^(98/99), using integer powers only."""
    require(type(rank) is int and 1 <= rank < M, "Rank outside root oracle domain")
    require(type(bits) is int and bits > 0, "Invalid precision")
    scale = 1 << bits
    target = (scale**99)*(rank**98)
    denominator = M**98
    lo, hi = 0, scale
    while hi-lo > 1:
        mid = (lo+hi)//2
        if (mid**99)*denominator <= target:
            lo = mid
        else:
            hi = mid
    require(lo**99*denominator <= target < hi**99*denominator,
            "Invalid integer-root enclosure")
    return Q(lo, scale), Q(hi, scale)


def oracle(local, centre=CENTRE, extra=None):
    remainder = (M-1)*W + centre - mass(local)
    require(remainder >= 0, "Negative residual mass")
    lo = hi = Q(0)
    for r, n in local.items():
        a, b = root_cost(r)
        lo += n*a
        hi += n*b
    a, b = root_cost(CAP)
    lo += (remainder/CAP)*a
    hi += (remainder/CAP)*b
    # Extra work outside the coverage law is additive, with no residual credit.
    for r, n in (extra or {}).items():
        require(type(n) is int and n >= 0, "Invalid extra call count")
        a, b = root_cost(r)
        lo += n*a
        hi += n*b
    return lo/W, hi/W


def verdict(bounds):
    lo, hi = bounds
    require(lo <= hi, "Reversed bounds")
    if lo > 1:
        return "excluded"
    if hi < 1:
        return "open-relaxation"
    raise ValueError("Unresolved threshold comparison")


def rounded(bounds):
    """Outward decimal-grid rationals, not floating-point acceptance."""
    scale = 10**12
    lo = (bounds[0].numerator*scale)//bounds[0].denominator
    hi = -((-bounds[1].numerator*scale)//bounds[1].denominator)
    return [str(Q(lo, scale)), str(Q(hi, scale))]


def rejection(fn, message):
    try:
        fn()
    except (ValueError, KeyError):
        return
    raise ValueError("Control escaped: " + message)


def main():
    check_pins()
    certificate = json.loads((ROOT / BLOCK / "CERTIFICATE.json").read_text())
    planning = json.loads((ROOT / CEILING / "RESULT.json").read_text())
    counts = read_inputs(certificate, planning)
    spec = importlib.util.spec_from_file_location("pinned_ceiling", ROOT / CEILING / "ceiling.py")
    engine = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(engine)

    table = []
    for i in range(counts[4]+1):
        for j in range(counts[5]+1):
            local = profile(i, j)
            direct = oracle(local)
            inherited = engine.relax(local, M, FAMILIES, STAGES, CENTRE, TARGET)
            require(max(direct[0], inherited[0]) <= min(direct[1], inherited[1]),
                    "Independent moment enclosures disagree")
            status = verdict(direct)
            require(status == verdict(inherited), "Engines disagree on target")
            require(status == ("excluded" if i+j >= 5 else "open-relaxation"),
                    "Eight-interface boundary failed")
            table.append({"retained_u4": i, "retained_u5": j,
                          "moment": rounded(direct), "status": status})

    # Strict ordering relative to rank-51 replacement supports the count-only
    # implication, independent of exhaustive enumeration of the 48 cells.
    base = oracle(profile(0, 0))
    one4, one5 = oracle(profile(1, 0)), oracle(profile(0, 1))
    excess4 = (one4[0]-base[1], one4[1]-base[0])
    excess5 = (one5[0]-base[1], one5[1]-base[0])
    require(excess4[0] > excess5[1] > 0, "Block-excess order failed")
    cheapest_five, dearest_four = oracle(profile(0, 5)), oracle(profile(4, 0))
    require(cheapest_five[0] > 1 and dearest_four[1] < 1, "Critical count boundary failed")
    all_blocks = oracle(profile(7, 5))
    low, high = engine.ceiling(profile(7, 5), M, FAMILIES, STAGES, CENTRE)
    require(engine.relax(profile(7, 5), M, FAMILIES, STAGES, CENTRE, low)[1] < 1
            and engine.relax(profile(7, 5), M, FAMILIES, STAGES, CENTRE, high)[0] > 1,
            "Full-inventory ceiling bracket failed")

    # Metadata/premise rejection controls operate on independent in-memory copies.
    controls = 0
    for mutation in ("missing", "duplicate", "rank", "profile", "split", "float", "orientation"):
        altered = deepcopy(certificate)
        selected = next(s for s in altered["sources"] if s["file"] == "inputs/selected.json.gz")
        if mutation == "missing":
            selected["blocks"].pop()
        elif mutation == "duplicate":
            selected["blocks"][1] = deepcopy(selected["blocks"][0])
        elif mutation == "rank":
            selected["blocks"][0]["common_rank"] = 6
        elif mutation == "profile":
            selected["blocks"][0]["profile"]["1"] -= 1
        elif mutation == "split":
            selected["blocks"][0]["low"][0] = selected["blocks"][0]["high"][0]
        elif mutation == "float":
            selected["blocks"][0]["profile"]["1"] = 24.0
        else:
            altered["orientation_contract"]["contract"] = "independent-backward-word"
        rejection(lambda: read_inputs(altered, planning), mutation)
        controls += 1
    rejection(lambda: engine.model(profile(7, 5), M, FAMILIES, STAGES, CENTRE, R=52), "rank cap")
    rejection(lambda: verdict((Q(99, 100), Q(101, 100))), "ambiguous interval")
    controls += 2
    # Removing centre work changes the hypothesis and opens this relaxation.
    require(oracle(profile(7, 5, centres=False), centre=0)[1] < 1,
            "Centre-free scope sensitivity failed")
    # One additional rank-one call outside the coverage identity closes the
    # marginal four-block screen. Crediting its mass against idle is invalid.
    extra = oracle(profile(4, 0), extra={1: 1})
    wrong_credit = oracle({**profile(4, 0), 1: profile(4, 0)[1]+1})
    require(extra[0] > 1 and wrong_credit[1] < 1, "Unpaid extra-work control failed")
    controls += 2

    print(json.dumps({
        "status": "PASS_COMPLEX_BLOCK_TARGET_SCREEN", "target_a": str(TARGET),
        "total_rank_mass_per_call": str(TOTAL), "mandatory_block_mass": 604,
        "retained_all_moment": rounded(all_blocks),
        "cheapest_five_moment": rounded(cheapest_five),
        "dearest_four_moment": rounded(dearest_four),
        "full_inventory_a_bracket": [str(low), str(high)],
        "full_inventory_kappa_upper": str(high/(1+high)),
        "count_pairs": len(table), "excluded": sum(t["status"] == "excluded" for t in table),
        "minimum_interfaces_to_escape": 8, "controls": controls,
        "extra_rank_one_moment": rounded(extra),
        "invalid_idle_credit_moment": rounded(wrong_credit),
        "table": table, "kappa": "unchanged"
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
