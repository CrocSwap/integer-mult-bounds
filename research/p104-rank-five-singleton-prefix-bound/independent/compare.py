"""Compare the 14 independent nonzero rational-rank certificates to lead."""
from hashlib import sha256
from json import dumps, loads
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    "lead/RESULT.json": "aa3e2a52214451c4bd99c231a3a30823a8017f53e5e9e2705ed884335c705a7a",
    "independent/RESULT.json": "76f6d7b38943b457ad70942cacc530ce531ceec6e4defe6ef425cacb68bd409b",
}


def read(path):
    raw = (ROOT/path).read_bytes()
    if sha256(raw).hexdigest() != PINS[path]:
        raise ValueError(f"changed dependency {path}")
    return loads(raw)


def main():
    lead, independent = map(read,PINS)
    assert all(lead[k] == independent[k] for k in ("head","caller","case_cap"))
    assert not lead["unvisited"] and not lead["survivors"] and not independent["unresolved"]
    a = {tuple(r["key"]):r for r in lead["tested"]}
    b = {tuple(r["key"]):r for r in independent["rows"]}
    assert a.keys() == b.keys() and len(a) == 14
    for key, left in a.items():
        right = b[key]
        assert left["bank"] == right["public"] and not right["owned"]
        assert left["pivot"] == right["pivot"] and left["child_ranks"] == right["ordered_child_ranks"]
        assert left["disposition"] == "absent pure prefix direction"
        assert right["disposition"] == "exact full prefix rank"
        assert left["prefix_exterior_rank"] == right["prefix_minor"]["rank"] == len(left["bank"])
        assert right["prefix_minor"]["determinant"] and not right["prefix_minor"]["kernel"]
    print(dumps({"pins":PINS,"case_agreements":len(a),"suffix_required":0,"unresolved":0},
                indent=2,sort_keys=True))


if __name__ == "__main__":
    main()
