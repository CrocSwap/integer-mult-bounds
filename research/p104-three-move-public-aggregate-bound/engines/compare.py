"""Compare the exact backwards aggregate and forward lead bank certificates."""
from fractions import Fraction
from hashlib import sha256
from json import dumps, loads
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PINS = {
    "RESULT.json": "f37d69043b875cec3ab87485e1e29beddd65d7aaa4cfa8475c237f3a524e8816",
    "inputs/R131-LEAD.json": "bae7703a911ed5b48ebee9b734bdb9cea9d1218309b0d4c619e94d035b120740",
    "inputs/R131-PRICE.json": "5e1ec82297c1c37cc72d87925486c7307010203ff51545c8536f027154715094",
}


def unique(items):
    result = dict(items)
    if len(result) != len(items):
        raise ValueError("duplicate JSON key")
    return result


def read(path):
    raw = (ROOT/path).read_bytes()
    if sha256(raw).hexdigest() != PINS[path]:
        raise ValueError(f"changed dependency {path}")
    return loads(raw, object_pairs_hook=unique)


def main():
    assert __debug__
    independent, lead, price = map(read,PINS)
    assert independent["head"] == lead["head"] == price["head"]
    assert independent["caller"] == lead["caller"] == price["caller"]
    assert independent["aggregate"] == lead["aggregate"] and len(independent["aggregate"]) == 26
    assert lead["price"] == price and lead["pins"] == price["pins"]
    assert independent["unresolved"] == [] and lead["unvisited"] == []
    assert price["selected_banks"] == [r["key"] for r in lead["rows"]]
    assert Fraction(price["candidate"]["probe_lower"])>0
    checks = []
    for local,original in zip(independent["results"],lead["rows"],strict=True):
        assert local["status"] == "excluded" and original["decision"] == "outside donor span"
        assert [local["cut"],local["chart"],independent["mover"]] == original["key"]
        assert local["public"] == original["bank_roles"]
        assert local["dual"] == original["separator"] == {"27":"1"}
        assert local["dual_on_aggregate"] == original["separator_value"] == independent["aggregate"]["27"] == "1"
        checks.append(dict(key=original["key"],public=local["public"],owned_excluded=local["owned_excluded"],
            common_separator=local["dual"],value=local["dual_on_aggregate"]))
    assert len(checks)==2 and "outside" in lead["role198_status"]
    print(dumps(dict(head=price["head"],caller=price["caller"],pins=PINS,aggregate_coordinates=26,banks=checks,
        unresolved_in_scope=0,role198="outside this two-bank scope"),indent=2,sort_keys=True))


if __name__ == "__main__":
    main()
