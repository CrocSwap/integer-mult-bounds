"""Directed price for two paid rank-two subdivisions funding one 4+5 split."""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
from runpy import run_path

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    "inputs/BENCHMARK.json": "004331cff6ca8644489d7b7084e5c67439d74a2d283e4d64a9fdb9f88679253d",
    "inputs/R92-GEOMETRY.json": "e9f93f3271855012b2de705c70f186f78c31a369d28110e92c5f2ffadae209b3",
    "inputs/R92-PRICE.json": "05d7a5ebdd2eeedd6c8f534e8e2eeac22484daf9f387f4a6b88cc9eed22a6b8f",
    "inputs/pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
}


def unique(pairs):
    result = dict(pairs)
    if len(result) != len(pairs):
        raise ValueError("duplicate JSON key")
    return result


def hist(document):
    return Counter({int(key): value for key, value in document.items()})


def main():
    docs = []
    for path,pin in PINS.items():
        raw = (ROOT/path).read_bytes()
        if sha256(raw).hexdigest() != pin:
            raise ValueError(f"changed dependency {path}")
        if path.endswith(".json"):
            docs.append(json.loads(raw,object_pairs_hook=unique))
    bench,geo,prior = docs
    assert bench["head"] == geo["head"] == prior["head"] == "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
    assert geo["word_sha256"] == prior["word_sha256"]
    assert geo["price_sha256"] == PINS["inputs/R92-PRICE.json"]
    placement = geo["raw_placements"]
    anchors = {r["move_clock"] for r in placement}
    roles = {r["mover"] for r in placement}
    assert len(anchors) == 95 and len(placement) == 285
    stock = min(len(anchors),len(roles))//2
    paid = hist(prior["old_paid"])
    target = hist(prior["old_targets"])
    assert sum(paid.values()) == 110519 and sum(target.values()) == 22461
    old = target.copy()
    old.subtract(paid)
    assert sum(r*n for r,n in old.items()) == 1424
    new_paid = paid.copy()
    paid_delta = {1:68, 2:-34}
    new_paid.update(paid_delta)
    new_target = target.copy()
    target_delta = {4:17,5:17,9:-17}
    new_target.update(target_delta)
    new = new_target.copy()
    new.subtract(new_paid)
    assert sum(r*n for r,n in new.items()) == 1424
    assert sum(new_paid.values()) == 110553 and sum(new_target.values()) == 22478
    change = new.copy()
    change.subtract(old)
    cost = run_path(str(ROOT/"inputs/pricing.py"))["cost"]
    at = Q(prior["old_crossing_upper"])
    probe = Q(prior["probe"])
    bit = Q(prior["retained_bit_premise"])
    moon = Q(prior["moonshot"])
    assert at == Q(bench["crossing"][1]) and at < probe < bit < moon
    net = cost(change,at)
    complete_probe = cost(new,probe)
    extra_child = cost(new,at)[1]-1
    moon_net = cost(change,moon)
    moon_complete = cost(old,moon)[1] + stock * max(Q(0),moon_net[1])
    assert complete_probe[0] > 0 and extra_child < 0 and moon_complete < 0
    data = {
        "head": bench["head"],"caller_head":prior["caller_head"],"word_sha256":prior["word_sha256"],
        "pins":PINS,"kappa":bench["kappa"],"old_crossing_upper":str(at),"probe":str(probe),
        "moonshot":str(moon),"retained_bit_premise":str(bit),"anchors":len(anchors),"roles":len(roles),
        "compatibility_cap_before_geometry":stock,"paid_delta":paid_delta,"target_delta":target_delta,
        "new_paid":new_paid,"new_targets":new_target,"one_net_at_crossing":list(map(str,net)),
        "whole_net_upper":str(stock*net[1]),"complete_probe":list(map(str,complete_probe)),
        "complete_upper_with_one_added_rank_one":str(extra_child),
        "one_moonshot_net_upper":str(moon_net[1]),"whole_moonshot_complete_upper":str(moon_complete),
        "limits":{"event_passes":2,"events_each":76466,"placement_count":285,"pair_comparisons":2000,
                  "raw_pair_cuts":40000,"geometry_seconds":20,"modular_cases":16,"modular_seconds":25,
                  "exact_cases":4,"exact_seconds":35,"candidate_builds":1},
        "scope":"Two distinct unprotected cohort roles and two distinct paid rank-two anchors. Each MOVE is replaced by two rank-one MOVEs; one 4+5 target split. Distinct anchors and roles consumed once. Zero ancillary and zero chart-synthesis overhead gives an optimistic upper; no ordinary, routing, ownership or precision/tape credit.",
    }
    print(json.dumps(data,indent=2,sort_keys=True))


if __name__ == "__main__":
    assert __debug__
    main()
