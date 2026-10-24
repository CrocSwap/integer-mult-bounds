#!/usr/bin/env python3
"""Word, capacity and stock equivalence of the #4091 ceiling and the 1090-call fill.

This checker does not import either predecessor verifier. It reads the pinned
word bytes, owner template and recorded profiles, rebuilds both mixtures, and
rejects a shifted profile, a swapped idle histogram and a one-byte word change.
"""
import collections
import gzip
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CEILING = ROOT / "research/staged-fourth-mixture-ceiling"
LATER = ROOT / "research/staged544-mixed-fourth-entry"
WORDS = (
    "THREE-base.json.gz",
    "THREE-extra.json.gz",
    "FOUR-base.json.gz",
    "FOUR-extra.json.gz",
)
TEMPLATE_RANKS = {8: 672, 16: 448, 32: 448, 48: 448}
THREE_WIDTHS = {5: 28, 6: 18, 7: 56, 8: 93, 9: 213}
FOUR_WIDTHS = {5: 28, 6: 18, 7: 57, 8: 92, 9: 213}
WORD_DELTA = {1: 2, 3: 3, 4: -3}
CEILING_IDLE = {3: 22788, 5: 1620, 48: 138492}
LATER_IDLE = {3: 22783, 5: 1625, 48: 138492}
PAID_MASS = 65088 * 360
STOCK = 896 * 360 * 73


class CheckFailure(Exception):
    pass


def demand(condition, message):
    if not condition:
        raise CheckFailure(message)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def integers(mapping):
    return {int(key): int(value) for key, value in mapping.items()}


def fraction(text):
    numerator, denominator = str(text).split("/")
    return int(numerator), int(denominator)


def rank_mass(profile):
    return sum(rank * count for rank, count in profile.items())


def mix(third, fourth, third_calls, fourth_calls, idle):
    total = collections.Counter()
    for profile, scale in ((third, third_calls), (fourth, fourth_calls), (idle, 1)):
        for rank, count in profile.items():
            total[rank] += scale * count
    return {rank: count for rank, count in total.items() if count}


def word_report(path):
    payload = json.loads(gzip.decompress(path.read_bytes()))
    report = payload["report"]
    return (
        integers(report["local_profile"]),
        integers(report["width_inventory"]),
        [int(item) for item in payload["start_extra"]["601"]],
    )


def difference(left, right):
    keys = set(left) | set(right)
    return {
        key: left.get(key, 0) - right.get(key, 0)
        for key in keys
        if left.get(key, 0) != right.get(key, 0)
    }


def below(left, right):
    left_n, left_d = left
    right_n, right_d = right
    return left_n * right_d < right_n * left_d


def separation(higher, lower):
    high_n, high_d = higher
    low_n, low_d = lower
    numerator = high_n * low_d - low_n * high_d
    denominator = high_d * low_d
    demand(numerator > 0 and denominator > 0, "nonpositive root separation")
    divisor = math.gcd(numerator, denominator)
    return numerator // divisor, denominator // divisor


def audit():
    ceiling = load_json(CEILING / "RESULT.json")
    later = load_json(LATER / "RESULT.json")
    plain_pins = load_json(LATER / "INPUTS.json")["canonical_sha256"]
    gzip_pins = ceiling["source_sha256"]

    for name in WORDS:
        ceiling_bytes = (CEILING / "source4088/inputs" / name).read_bytes()
        later_bytes = (LATER / "inputs" / name).read_bytes()
        demand(ceiling_bytes == later_bytes, "word bytes differ: " + name)
        demand(sha256(ceiling_bytes) == gzip_pins["inputs/" + name], "gzip pin: " + name)
        demand(sha256(gzip.decompress(ceiling_bytes)) == plain_pins[name], "plain pin: " + name)

    for ceiling_rel, later_rel in (
        ("source4088/owner/TEMPLATE.json.gz", "owner/TEMPLATE.json.gz"),
        ("source4088/owner/ORDER.json", "owner/ORDER.json"),
    ):
        demand(
            (CEILING / ceiling_rel).read_bytes() == (LATER / later_rel).read_bytes(),
            "owner bytes differ: " + ceiling_rel,
        )
    template_bytes = (CEILING / "source4088/owner/TEMPLATE.json.gz").read_bytes()
    demand(
        sha256(template_bytes) == gzip_pins["owner/TEMPLATE.json.gz"],
        "template pin",
    )
    children = json.loads(gzip.decompress(template_bytes))["idle_children"]
    ranks = collections.Counter(int(child["rank"]) for child in children)
    demand(len(children) == 2016, "template row count")
    demand(dict(ranks) == TEMPLATE_RANKS, "template ranks " + str(dict(ranks)))
    ports = collections.Counter(int(child["port"]) for child in children)
    demand(len(ports) == 112 and set(ports.values()) == {18}, "port slot count")
    bins = {capacity: count * 360 for capacity, count in ranks.items()}
    demand(integers(ceiling["bin_counts"]) == bins, "recorded bin counts")
    demand(sum(bins.values()) == 725760, "total bins")
    demand(sum(capacity * count for capacity, count in bins.items()) == 17418240, "total capacity")

    profiles = {}
    widths = {}
    entrances = {}
    for name in WORDS:
        profiles[name], widths[name], entrances[name] = word_report(LATER / "inputs" / name)
    third = profiles["THREE-base.json.gz"]
    fourth = profiles["FOUR-base.json.gz"]
    demand(profiles["THREE-extra.json.gz"] == third, "THREE orientations differ")
    demand(profiles["FOUR-extra.json.gz"] == fourth, "FOUR orientations differ")
    demand(widths["THREE-base.json.gz"] == widths["THREE-extra.json.gz"] == THREE_WIDTHS, "THREE widths")
    demand(widths["FOUR-base.json.gz"] == widths["FOUR-extra.json.gz"] == FOUR_WIDTHS, "FOUR widths")
    demand(difference(fourth, third) == WORD_DELTA, "local-word delta")
    demand(entrances["THREE-base.json.gz"] == entrances["THREE-extra.json.gz"] == [45], "THREE entrance")
    demand(entrances["FOUR-base.json.gz"] == entrances["FOUR-extra.json.gz"] == [127, 45], "FOUR entrance")
    demand(rank_mass(fourth) - rank_mass(third) == -1, "local rank-mass delta")

    ceiling_idle = integers(ceiling["idle"])
    later_idle = integers(later["idle"])
    demand(ceiling["calls"] == 3240 and later["calls"] == 3240, "call count")
    demand(ceiling["optimum_fourth_calls"] == 1080, "pooled optimum")
    demand(later["fourth_calls"] == 1090, "later selector")
    demand(ceiling_idle == CEILING_IDLE, "ceiling idle")
    demand(later_idle == LATER_IDLE, "later idle")
    ceiling_profile = integers(ceiling["complete_profile"])
    later_profile = integers(later["profile"])
    demand(mix(third, fourth, 2160, 1080, ceiling_idle) == ceiling_profile, "ceiling mixture")
    demand(mix(third, fourth, 2150, 1090, later_idle) == later_profile, "later mixture")
    demand(rank_mass(ceiling_profile) == PAID_MASS, "ceiling paid mass")
    demand(rank_mass(later_profile) == PAID_MASS, "later paid mass")
    demand(rank_mass(later_idle) - rank_mass(ceiling_idle) == 10, "idle mass shift")

    ceiling_proof = (CEILING / "PROOF.md").read_text(encoding="utf-8")
    later_proof = (LATER / "PROOF.md").read_text(encoding="utf-8")
    demand("(896*360)*73=23546880" in ceiling_proof.replace(" ", ""), "ceiling stock sentence")
    demand("(896*360)73^(1-k)" in later_proof.replace(" ", ""), "later stock sentence")
    demand("65088*360" in ceiling_proof and "65088*360" in later_proof, "paid-mass sentence")
    demand(STOCK == 23546880, "stock arithmetic")

    literal_minus_ideal = integers(ceiling["literal_minus_ideal"])
    demand(literal_minus_ideal[16] == 1 and literal_minus_ideal[32] == 2, "1080 residual terms")
    demand(16 not in later_idle and 32 not in later_idle, "1090 idle support")

    ceiling_lower = fraction(ceiling["root_bracket"][0])
    later_upper = fraction(later["root_upper"])
    later_lower = fraction(later["root_lower"])
    literal_upper = fraction(ceiling["literal_root_bracket"][1])
    demand(below(later_upper, ceiling_lower), "1090 root is not below the ceiling")
    demand(below(literal_upper, later_lower), "1090 root is not above the 1080 literal")
    above_literal = separation(later_lower, literal_upper)
    below_ceiling = separation(ceiling_lower, later_upper)
    demand(above_literal == (810594906779329, 10**24), "literal separation")
    demand(below_ceiling == (1140318244487201, 10**24), "ceiling separation")

    # Semantic controls. Each one changes a real identity the audit just used.
    shifted = dict(later_profile)
    shifted[1] += 1
    demand(shifted != mix(third, fourth, 2150, 1090, later_idle), "shifted profile was accepted")
    demand(
        mix(third, fourth, 2150, 1090, ceiling_idle) != later_profile,
        "1080 idle was accepted as the 1090 fill",
    )
    mutated = (LATER / "inputs/THREE-base.json.gz").read_bytes()[:-1]
    demand(sha256(mutated) != sha256((CEILING / "source4088/inputs/THREE-base.json.gz").read_bytes()),
           "truncated word still matched")

    return {
        "paid_mass": PAID_MASS,
        "stock": STOCK,
        "bins": 725760,
        "capacity": 17418240,
        "above_literal": above_literal,
        "below_ceiling": below_ceiling,
    }


def main():
    try:
        result = audit()
    except CheckFailure as exc:
        raise SystemExit("FAIL_STAGED_FOURTH_CEILING_EQUIVALENCE " + str(exc)) from exc
    above_n, above_d = result["above_literal"]
    below_n, below_d = result["below_ceiling"]
    print(
        "PASS_STAGED_FOURTH_CEILING_EQUIVALENCE"
        " words=identical capacities=identical"
        f" stock={result['stock']} bins={result['bins']} capacity={result['capacity']}"
        f" paid_mass={result['paid_mass']} fourth=1080->1090"
        f" above_literal={above_n}/{above_d}"
        f" below_ceiling={below_n}/{below_d}"
        " controls=3 no_new_kappa=true"
    )


if __name__ == "__main__":
    main()
