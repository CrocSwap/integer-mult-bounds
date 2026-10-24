#!/usr/bin/env python3
"""The monotone selected entrances cannot host the rank-8/u2 16-child cell.

The pinned ceiling engine supplies child-cost enclosures. This file recomputes
the entrance capacities from the selected local word and does not edit either
input. It claims no producer, no consumer and no new kappa.
"""
import gzip
import hashlib
import importlib.util
from collections import Counter
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORD = ROOT / "research/r480-owner-optimum/inputs/local/FULL-WORD.json.gz"
ENGINE = ROOT / "research/complex-local-word-ceiling/ceiling.py"
SELECTED = ROOT / "certificates/selected-result.json"
WORD_GZIP_SHA = "49596aa4ed4fd36cd4582fd0e8ddeb09fd80370a7d8aea1ede52a135b536d289"
WORD_RAW_SHA = "c2b294300760e1fd6eeab8c22c4d13e4633dca40e52cac8da0d68163a76e3ca8"
ENGINE_SHA = "86a1432870b3b21d8454106ec9162fddc0471472d9214c590a1420f2426cedfc"
H = 9
V = 112
HELPERS = 480
MASS = 5586
A = Fraction(1, 98)
FAMILIES = 896
CALLS = 9
CENTRE = 64
UNPAID = 2
MONOTONE = {8: 648, 5: 32, 4: 24, 1: 146}
CENTRE3 = {8: 664, 5: 32, 4: 24, 1: 18}
IDEAL = {8: 698, 2: 1}


def require(ok, why):
    if not ok:
        raise SystemExit("FAIL: " + why)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dimension(vectors):
    pivot = {}
    for value in vectors or []:
        require(isinstance(value, int) and 0 <= value < (1 << H), "frame vector outside F2^9")
        while value:
            bit = value.bit_length() - 1
            if bit in pivot:
                value ^= pivot[bit]
            else:
                pivot[bit] = value
                break
    return len(pivot)


def load_engine():
    require(digest(ENGINE) == ENGINE_SHA, "ceiling.py sha256 differs from the package pin")
    spec = importlib.util.spec_from_file_location("pinned_ceiling", ENGINE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    require(module.max_idle_rank(73) == 51, "halving cap is not 51")
    return module


def load_word():
    require(digest(WORD) == WORD_GZIP_SHA, "selected word gzip sha256 changed")
    raw = gzip.decompress(WORD.read_bytes())
    require(hashlib.sha256(raw).hexdigest() == WORD_RAW_SHA, "selected word content hash changed")
    word = json_loads(raw)
    report = word["report"]
    profile = {int(rank): count for rank, count in report["local_profile"].items()}
    require(profile == {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}, "published local profile")
    require(sum(rank * count for rank, count in profile.items()) == MASS, "published mass")
    require((report["h"], report["v"], report["R"]) == (H, V, HELPERS), "word dimensions")
    return word


def json_loads(raw):
    import json
    return json.loads(raw)


def capacities(word):
    """Maximum monotone climb on each register.

    Sources start on their port line and may end at FULL. Targets start empty
    and may end on the port parity hyperplane. Helpers start at the pinned
    entrance and may end at FULL. A monotone chain has room dim(exit)-dim(entrance).
    """
    count = 2 * V + HELPERS
    start = [1] * V + [0] * (V + HELPERS)
    for key, frame in word.get("start_extra", {}).items():
        register = int(key)
        require(2 * V <= register < count, "entrance is not a helper")
        start[register] = dimension(frame)
    ports = word["ports"]
    require(len(ports) == V, "port count")
    for port in ports:
        require(isinstance(port, int) and 0 < port < (1 << H), "port line is not a nonzero F2^9 vector")
    caps = []
    for register, entrance in enumerate(start):
        if register < V:
            limit = H
        elif register < 2 * V:
            limit = H - 1
        else:
            limit = H
        require(limit >= entrance, "entrance does not sit in the maximum exit")
        caps.append(limit - entrance)
    centres = [int(register) for register in word["centers"]]
    require(len(centres) == len(set(centres)) == 8, "eight distinct centres")
    require(all(0 <= register < count for register in centres), "centre register")
    return caps, centres


def pack(caps, mass=MASS):
    remaining = list(caps)
    histogram = Counter()
    need = mass
    for part in range(8, 0, -1):
        for index, _room in enumerate(remaining):
            while remaining[index] >= part and need >= part:
                remaining[index] -= part
                histogram[part] += 1
                need -= part
                if need == 0:
                    require(sum(rank * count for rank, count in histogram.items()) == mass, "packer mass")
                    return dict(histogram)
    raise SystemExit("FAIL: packer left mass " + str(need))


def pooled_moment(engine, per_call, extra):
    histogram = Counter({51: 272, 46: 1})
    for rank, count in per_call.items():
        histogram[rank] += CALLS * count
    if extra:
        histogram[1] += extra
    low = high = Fraction(0)
    for rank, count in histogram.items():
        left, right = engine.child_cost(int(rank), 73, A)
        require(left <= right, "cost enclosure inverted")
        low += count * left
        high += count * right
    total = (73 - UNPAID) * FAMILIES + CENTRE * CALLS
    paid = CALLS * MASS
    require(total - paid == 51 * 272 + 46, "pooled idle is not the u=2 remainder")
    require(sum(rank * count for rank, count in histogram.items()) == total + extra, "moment mass")
    return engine.down(low / FAMILIES), engine.up(high / FAMILIES)


def sign(bounds):
    low, high = bounds
    if high < 1:
        return "LT"
    if low > 1:
        return "GT"
    return "UNK"


def certify_exchanges(engine):
    """Strict concavity on 1..8: merging, and moving mass onto the larger part, lowers cost."""
    cost = {}
    for rank in range(1, 9):
        cost[rank] = engine.child_cost(rank, 73, A)

    def below(left_ranks, right_ranks):
        left = sum((cost[rank][1] for rank in left_ranks), Fraction(0))
        right = sum((cost[rank][0] for rank in right_ranks), Fraction(0))
        require(left < right, "enclosure does not separate " + str(left_ranks) + " from " + str(right_ranks))

    for left in range(1, 8):
        for right in range(1, 9 - left):
            below((left + right,), (left, right))
    for small in range(1, 8):
        for large in range(small, 8):
            donor = () if small == 1 else (small - 1,)
            below(donor + (large + 1,), (small, large))
    # Gathering any composition of 8 into one part lowers the certified cost.
    compositions = [[]]

    def grow(parts, used):
        start = parts[-1] if parts else 1
        for part in range(start, 9 - used):
            grow(parts + [part], used + part)
        if used == 8 and len(parts) >= 2:
            compositions.append(parts)

    grow([], 0)
    require(len(compositions) > 2, "composition list")
    for parts in compositions[1:]:
        below((8,), tuple(parts))


def main():
    engine = load_engine()
    word = load_word()
    caps, centres = capacities(word)
    counts = Counter(caps)
    require(counts == Counter({9: 288, 8: 360, 5: 32, 4: 24}), "entrance capacity census changed")
    require(sum(1 for cap in caps if cap >= 8) == 648, "rank-8 slot count")
    require(all(caps[register] >= 8 for register in centres), "a centre has no rank-8 slot")
    monotone = pack(caps)
    require(monotone == MONOTONE, "monotone optimum histogram changed")
    centre_caps = list(caps)
    for register in centres:
        centre_caps[register] = 24
    centre3 = pack(centre_caps)
    require(centre3 == CENTRE3, "three-step centre histogram changed")
    certify_exchanges(engine)
    monotone_sign = sign(pooled_moment(engine, monotone, 0))
    centre_bare = sign(pooled_moment(engine, centre3, 0))
    centre_one = sign(pooled_moment(engine, centre3, 1))
    ideal_16 = sign(pooled_moment(engine, IDEAL, 16))
    ideal_17 = sign(pooled_moment(engine, IDEAL, 17))
    require(monotone_sign == "GT", "monotone optimum no longer fails at zero surcharge")
    require(centre_bare == "LT" and centre_one == "GT", "centre comparison room is no longer zero")
    require(ideal_16 == "LT" and ideal_17 == "GT", "published 16/17 boundary moved")
    # A histogram with 649 eights does not fit these caps.
    overflow = dict(monotone)
    overflow[8] += 1
    overflow[1] -= 8
    require(overflow[1] > 0, "overflow control")
    require(sum(1 for cap in caps if cap >= 8) < overflow[8], "649 eights were accepted")
    import json
    selected = json.loads(SELECTED.read_text(encoding="utf-8"))
    require(selected["kappa"] == "60403/20000000", "selected kappa record changed")
    print(
        "PASS_RANK8_U2_ENTRANCE_OBSTRUCTION"
        " slots=648"
        " monotone=GT/0"
        " centre3=LT/0/GT/1"
        " ideal=LT/16/GT/17"
        " no_new_kappa"
    )


if __name__ == "__main__":
    main()
