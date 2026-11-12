"""Reconcile independent owner-incidence evidence with the forward pass."""

from hashlib import sha256
from json import dumps, loads
from pathlib import Path
import sys

ROOT = Path(sys.argv[1])
PINS = {
    "lead/RESULT.json": "db293c67c896f54788681b7a8a9fec5f13da0e31fe5b3dd65fbe30e370ff1d2e",
    "independent/RESULT.json": "12c31ae16b9a364fd84c16d2f76cee873ab279984eb88e1cf1568be905c8f010",
}


def load(name):
    raw = (ROOT / name).read_bytes()
    assert sha256(raw).hexdigest() == PINS[name], name

    def unique(pairs):
        data = dict(pairs)
        assert len(data) == len(pairs)
        return data

    return loads(raw, object_pairs_hook=unique)


def main():
    assert __debug__
    lead = load("lead/RESULT.json")
    independent = load("independent/RESULT.json")
    assert lead["status"] == "EXHAUSTED" and independent["complete"]
    for name in ("head", "word_sha256", "price_sha256", "case_cap"):
        assert lead[name] == independent[name], name
    assert lead["paid_owned_rank"] == independent["owned_paid_by_rank"]
    assert lead["total_events"] == lead["visited_events"] == independent["literal_events"]
    assert not lead["remaining"] and not independent["unvisited_geometry"]
    assert independent["unvisited_literal_interval"] is None
    assert not lead["eligible_turns"] and not independent["survivor_keys"]
    forward = {tuple(row["key"]): row for row in lead["consecutive_same_lifetime_pairs"]}
    reverse = {
        (row["key"][2], row["lifetime"][0], *row["key"][:2]): row
        for row in independent["pairs"]
    }
    assert forward.keys() == reverse.keys()
    assert len(forward) == len(reverse) == independent["neighbor_pairs"] == 9
    records = []
    for key in sorted(forward, key=lambda k: k[-1]):
        f, r = forward[key], reverse[key]
        assert f["frames"] == r["charts"]
        directions = ["up" if y > x else "down" for x, y in zip(r["ranks"], r["ranks"][1:])]
        assert f["directions"] == directions
        assert f["turn"] == r["opposite_direction"]
        assert not r["opposite_direction"]
        clock, instruction = f["blocker"]
        access = "destination" if instruction[1] == key[0] else "source"
        assert instruction[1 if access == "destination" else 2] == key[0]
        assert [clock, instruction[0], access] == r["barriers"][0]
        assert f["scales"] == r["scales"] == []
        records.append({
            "key_owner_birth_first_second": key, "chart_path": r["charts"], "directions": directions,
            "first_binary_contact": r["barriers"][0], "all_binary_contacts": r["barriers"],
        })
    print(dumps({
        "input_sha256": PINS, "matched": records, "strict_opposite": 0,
        "unresolved": 0, "compatible_price": "0",
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
