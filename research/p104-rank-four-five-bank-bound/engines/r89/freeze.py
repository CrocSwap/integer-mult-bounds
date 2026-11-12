"""Freeze the R87 unresolved public-bank keys without decoding the native word."""
from collections import Counter
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import sys

HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
PINS = {
    "inputs/PRICE.json": "b4bf8e00a8289f03b1da731fb3ab563a771d88d875e0da73acf70954df2f2c56",
    "inputs/GEOMETRY.json": "238135413a5646cb39b34dd65dad73b3032f28352f114da9d67b854ffff39250",
    "inputs/7334-WORD.json.gz": "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
    "lead/RESULT.json": "a3505dd0cfd3ee9e242f804e12e3c4705ea6548080d537f597cec355f358e92c",
    "lead/SELECTION.json": "a4877749084f276d00917c137fda2b2593894daca1e10629a4a27de7914b4574",
    "lead/EXACT.json": "6c89dc61732e9f3dd0bd6bf7b3653c0aae555543959919b6955c3d49e8caf3c6",
}


def unique(pairs):
    result = dict(pairs)
    if len(result) != len(pairs):
        raise ValueError("duplicate JSON key")
    return result


def checked(root, path):
    raw = (root / path).read_bytes()
    if sha256(raw).hexdigest() != PINS[path]:
        raise ValueError(f"changed dependency: {path}")
    if path.endswith(".gz"):
        return None
    return json.loads(raw, object_pairs_hook=unique)


def price_at_cap(one_split, count):
    base_lo, base_hi = map(Fraction, one_split["old_complete_margin"])
    credit_lo, credit_hi = map(Fraction, one_split["gross_credit"])
    return {"gross_ceiling": str(count * credit_hi),
            "complete_margin_upper": str(base_hi + count * credit_hi),
            "one_edit_credit": list(map(str, (credit_lo, credit_hi))),
            "old_margin": list(map(str, (base_lo, base_hi)))}


def main():
    root = Path(sys.argv[1])
    prior = {path: checked(root, path) for path in PINS}
    price, geom = prior["inputs/PRICE.json"], prior["inputs/GEOMETRY.json"]
    primary = prior["lead/RESULT.json"]
    selection, exact = prior["lead/SELECTION.json"], prior["lead/EXACT.json"]
    assert all(r["head"] == HEAD for r in (price, geom, primary, exact))
    assert geom["price_sha256"] == PINS["inputs/PRICE.json"]
    assert price["word_sha256"] == PINS["inputs/7334-WORD.json.gz"]
    assert primary["pins"]["inputs/GEOMETRY.json"] == PINS["inputs/GEOMETRY.json"]
    assert selection["modular_sha256"] == PINS["lead/RESULT.json"]
    assert exact["pins"]["lead/SELECTION.json"] == PINS["lead/SELECTION.json"]
    assert primary["status"] == "EXHAUSTED" and not primary["unvisited"]
    assert len(primary["results"]) == 4183
    assert [r["key"] for r in primary["results"]] == geom["unvisited_keys"]
    drops = [r for r in primary["results"] if r["disposition"] == "rank drop"]
    assert len(drops) == 2134 and [r["key"] for r in drops] == primary["rank_drops"]
    assert exact["counts"] == {"no nonzero pure suffix": 4, "no unit pairing": 2}
    assert not exact["selected_unresolved"]
    earlier = {tuple(r["key"]) for r in exact["results"]}
    assert len(earlier) == 6 and earlier == {tuple(r["key"]) for r in selection["selected"]}
    remaining = [r for r in drops if tuple(r["key"]) not in earlier]
    assert len(remaining) == len({tuple(r["key"]) for r in remaining}) == 2128
    assert [r["key"] for r in remaining] == selection["unselected"] == exact["unselected"]
    allowed = set(price["endpoint_cohort"])
    assert len(allowed) == 615
    for r in remaining:
        assert r["pivots"] and set(r["pivots"]) == set(r["public"]) & allowed
    pivots = sorted({r for case in remaining for r in case["pivots"]})
    count = min(price["cohort_cap"], len(pivots))
    receipt = {
        "head": HEAD,
        "source_sha256": PINS,
        "scope": "public cochart basis with unchanged paid itinerary; same chart-3 to chart-127 endpoint cohort",
        "cases": len(remaining),
        "charts": len({r["key"][1] for r in remaining}),
        "cuts": len({r["key"][0] for r in remaining}),
        "bank_size_histogram": dict(sorted(Counter(len(r["public"]) for r in remaining).items())),
        "presence_of_unmodified_owned_rows": sum(bool(r["owned"]) for r in remaining),
        "possible_literal_pivots": pivots,
        "one_split_per_literal_pivot_cap": count,
        "at_incumbent": price_at_cap(price["one_split"], count),
        "at_moonshot": price_at_cap(price["one_split_at_moonshot"], count),
        "moonshot_target": price["moonshot"],
        "moonshot_minimum_edits_necessary": price["moonshot_minimum_edits_necessary"],
        "reverse_case_cap": 2128,
        "reverse_runner_seconds_cap": 35,
        "exact_case_cap": 6,
        "exact_runner_seconds_cap": 35,
        "keys": remaining,
        "controls": exact["results"],
    }
    print(json.dumps(receipt, separators=(",", ":"), sort_keys=True))


if __name__ == "__main__":
    main()
