"""Price one retimed public subdivision using authenticated signed stock."""
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    "inputs/BENCHMARK.json": "004331cff6ca8644489d7b7084e5c67439d74a2d283e4d64a9fdb9f88679253d",
    "inputs/R92-GEOMETRY.json": "e9f93f3271855012b2de705c70f186f78c31a369d28110e92c5f2ffadae209b3",
    "inputs/R92-PRICE.json": "05d7a5ebdd2eeedd6c8f534e8e2eeac22484daf9f387f4a6b88cc9eed22a6b8f",
}
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
WORD = "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a"


def unique(pairs):
    out = dict(pairs)
    if len(pairs) != len(out):
        raise ValueError("duplicate JSON key")
    return out


def main():
    docs = {}
    for path, expected in PINS.items():
        data = (ROOT/path).read_bytes()
        if sha256(data).hexdigest() != expected:
            raise ValueError(f"changed price dependency {path}")
        docs[path] = json.loads(data, object_pairs_hook=unique)
    bench, geo, price = docs.values()
    assert bench["head"] == geo["head"] == price["head"] == HEAD
    assert Q(bench["crossing"][1]) == Q(price["old_crossing_upper"])
    assert geo["word_sha256"] == price["word_sha256"] == WORD
    assert geo["price_sha256"] == PINS["inputs/R92-PRICE.json"]
    placements = geo["raw_placements"]
    labelled = [(p["move_clock"], p["mover"], r["chart"], p["rank"], p["quotient_representative"])
                for p in placements for r in p["labels"]]
    anchors = {p["move_clock"] for p in placements}
    assert len(anchors) == 95 and len(placements) == 285 and len(labelled) == 31
    assert len(labelled) == len(set(labelled))
    stock = len({row[0] for row in labelled})
    movers = len({row[1] for row in labelled})
    bound_stock = min(stock, movers)
    quotes = [q for q in price["quotes"] if q["key"] in ([4,1,1],[5,1,1])]
    assert len(quotes) == 2
    for q in quotes:
        assert q["paid_delta"] == {"1":34,"2":-17}
        assert q["target_delta"] == {"4":17,"5":17,"9":-17}
    old_moon_upper = min(Q(q["full_at_moonshot"][1]) - Q(q["net_at_moonshot"][0]) for q in quotes)
    per_move_upper = max(Q(q["net_incumbent"][1]) for q in quotes)
    per_move_moon_upper = max(Q(q["net_at_moonshot"][1]) for q in quotes)
    result = {
        "head": HEAD, "caller_head": price["caller_head"], "word_sha256": WORD,
        "pins": PINS, "kappa": bench["kappa"], "old_crossing_upper": price["old_crossing_upper"],
        "probe": price["probe"], "retained_bit_premise": price["retained_bit_premise"],
        "moonshot": price["moonshot"], "labelled": sorted(labelled),
        "distinct_movers": movers, "distinct_moves": stock, "distinct_optimistic_cap": bound_stock,
        "all_anchor_moves": len(anchors), "all_quotient_lines": len(placements),
        "quotes": quotes, "one_net_upper": str(per_move_upper),
        "whole_net_upper": str(bound_stock * per_move_upper),
        "whole_moonshot_margin_upper": str(old_moon_upper + bound_stock * per_move_moon_upper),
        "extra_rank_one_upper": str(max(Q(q["full_margin_with_one_extra_raw_rank_one_upper"]) for q in quotes)),
        "limits": {"event_passes":2,"events_each":76466,"quotient_lines":285,"raw_label_cuts":40000,
                   "geometry_seconds":20,"modular_cases":16,"modular_seconds":25,
                   "exact_cases":4,"exact_seconds":35,"candidate_builds":1},
        "charged_model": "One rank-two paid MOVE becomes two rank-one MOVEs on each of 17 copies. One rank-nine productive return becomes ranks four and five. Same mover and same endpoint word and caller contract. Existing chart only. No overlapping mover, chart credit, or second use of one paid debit. Zero ancillary cost is an optimistic relaxation; every introduced paid call and any ordinary/routing/precision/tape change require reconstruction.",
    }
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__ == "__main__":
    assert __debug__
    main()
