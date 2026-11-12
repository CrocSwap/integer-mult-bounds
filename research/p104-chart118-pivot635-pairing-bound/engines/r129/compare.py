"""Match every certified chart-118 alias with the direct exact dispositions."""
from hashlib import sha256
from json import dumps, loads
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PINS = {
    "RESULT.json": "9f455feb6a5a793afdced371d2c17645e45f78fac2ae169076a567ba1098fc7d",
    "inputs/R128-RESULT.json": "1f57b766d26d2716a4454507054f5496f2ba8642d12442d719769741dd17c4f4",
    "inputs/R129-RESULT.json": "f591968fff3fd9d6abde0e07c9429ac950af218df2903a05a46db26cc32703f9",
}


def unique(items):
    obj = dict(items)
    if len(obj) != len(items):
        raise ValueError("duplicate JSON key")
    return obj


def read(name):
    data = (ROOT / name).read_bytes()
    if sha256(data).hexdigest() != PINS[name]:
        raise ValueError(f"changed dependency {name}")
    return loads(data, object_pairs_hook=unique)


def main():
    assert __debug__
    independent, original, direct = map(read, PINS)
    assert len({r["head"] for r in (independent,original,direct)}) == 1
    assert len({r["caller"] for r in (independent,original,direct)}) == 1
    assert not original["timeout"] and not direct["timeout"]
    assert not original["selected_unvisited"] and not direct["unvisited"] and not direct["provisional"]
    direct_rows = {tuple(r["key"]):r for r in original["results"] + direct["results"]}
    assert len(direct_rows) == len(original["results"]) + len(direct["results"]) == 74
    alias_rows = {}
    for row in independent["results"]:
        for key in row["keys"]:
            key = tuple(key)
            assert key not in alias_rows
            alias_rows[key] = row
    assert set(direct_rows) == set(alias_rows)
    for key, exact in direct_rows.items():
        row = alias_rows[key]
        assert exact["status"] == "no exact unit pairing" and row["status"] == "zero pairing"
        assert exact["bank"] == row["bank"] and exact["pivot635_present"]
        assert exact["prefix_dimension"] == len(row["pure_prefix"]) == 1
        assert exact["suffix_dimension"] == len(row["pure_suffix"]) == 1
        assert exact["local_pairing_matrix"] == row["local"] == [["0"]]
        assert exact["endpoint_pairing_matrix"] == row["endpoint"] == [["0"]]
    assert independent["excluded"] == 74 and independent["unresolved"] == 0
    print(dumps(dict(pins=PINS,head=independent["head"],caller=independent["caller"],
        matches=[list(key) for key in sorted(direct_rows)],count=74,unresolved=0,
        alias_counts=[len(r["keys"]) for r in independent["results"]]),indent=2,sort_keys=True))


if __name__ == "__main__":
    main()
