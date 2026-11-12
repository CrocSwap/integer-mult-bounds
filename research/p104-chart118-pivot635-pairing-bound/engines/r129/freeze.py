"""Authorize exactly the R128 residual keys using previously frozen complete price."""
from fractions import Fraction as Q
from hashlib import sha256
from json import dumps, loads
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    "inputs/R128-PRICE.json": "8083c540876bbc7c61fc05eaa8e5796cb96d58ea123638931f6cb60ce0507849",
    "inputs/R128-RESULT.json": "1f57b766d26d2716a4454507054f5496f2ba8642d12442d719769741dd17c4f4",
    "inputs/R89-PAIR.json": "4b8f2963ae0ef7bd357c3129e8287f79c5c1fccca6375c41e35fa01c476cb2ae",
}


def read(path):
    raw = (ROOT / path).read_bytes()
    if sha256(raw).hexdigest() != PINS[path]:
        raise ValueError(f"changed dependency {path}")
    return loads(raw)


def main():
    price, previous, pair = (read(p) for p in PINS)
    assert price["head"] == previous["head"] == pair["head"]
    assert not previous["selected_unvisited"] and previous["timeout"] is None
    done = [r["key"] for r in previous["results"]]
    assert done == [r["key"] for r in price["selected"]] == [[39701, 118], [40853, 118]]
    assert all(r["status"] == "no exact unit pairing" for r in previous["results"])
    assert price["unvisited"] == previous["unselected"]
    stock = [r for r in pair["results"] if r["key"][1] == 118 and 635 in r["pivots"]]
    assert len(stock) == len({tuple(r["key"]) for r in stock}) == 74
    assert all(r["direct_terms"] == 0 and not r["owned"] and r["disposition"] == "rank drop" for r in stock)
    remain = [r for r in stock if r["key"] not in done]
    assert len(remain) == 72 and [r["key"] for r in remain] == price["unvisited"]
    assert price["max_compatible_edits"] == 1 and price["target_delta"] == {"4":17,"5":17,"9":-17}
    assert price["paid_delta"] == {} and (price["complete_paid"],price["complete_productive"]) == (110519,22478)
    assert Q(price["complete_probe"][0]) > 0
    assert Q(price["complete_at_fixed_target"][1]) < 0 and Q(price["extra_rank_one_at_crossing_lower"][1]) < 0
    print(dumps(dict(head=price["head"], caller=price["caller"], pins=PINS, cases=remain,
        known_exact_controls=previous["results"], limits={"cases":72,"runner_seconds":35},
        pricing={k:price[k] for k in ("credit_at_crossing_upper","complete_probe","complete_at_fixed_target",
                                    "extra_rank_one_at_crossing_lower","max_compatible_edits","target_delta","paid_delta")},
        endpoint_cohort=price["endpoint_cohort"], word_sha256=price["word_sha256"],
        scope="All 72 previously unvisited chart-118 pivot635 public banks, no bank-equivalence assumption"),
        sort_keys=True,indent=2))


if __name__ == "__main__":
    main()
