"""Price and bind only the two singleton residual endpoint groups, no word decode."""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path

ROOT = Path(__file__).resolve().parent
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CALLER = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
PINS = {
    "inputs/PR7370-SHA256.json": "ea5a3157a967c01b94fd57ca26f8ace1bfa2c6e8165271af917846eb14f9c0d9",
    "inputs/R115-PRICE.json": "c04adfb199f6dbc25806d6062562c7d707b8fda8ad73f3ed818901248d25ffbf",
    "inputs/R115-GEOMETRY.json": "c2a4406cf7130a819189e8ceefb4bb6e09edd392eb56820f9fcadb0e9415ef4e",
    "inputs/PR7375-SHA256.json": "fd334987adac93393bab7578815ec8f9a9cb16ce8dce9b6620613efddde3203d",
    "inputs/PR7375-SELECTION.json": "910c8881f31721793cb8e8cbf3b3b3789a9986415e0d48dd9c97d146d5b37bcc",
    "inputs/PR7375-PRIMARY.json": "d00281b59d994fb96e3f60cedc5c6b3b6277a7d050e8ac7bd6b4a24724219669",
    "inputs/PR7375-SECOND.json": "96bdb7a70d247a198a6777fe10e30ce51f7b2e90d4a81f9bf7fea0515f9c1ad0",
    "inputs/7334-READBACK.json": "337668788fb39ec9575887f9c5faf438a880471f78d936357dabf7deeac5de82",
    "inputs/pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
    "inputs/CHART118-CONTROL.json": "5be60a09485041744919696121ae27e57a1aa9de437a2c4494d5fc569af4cdb4",
}
GROUPS = {(712, 127): 1360, (714, 127): 1361}
EXPECTED = {
    (712, 127): [(39267, 859), (39268, 859), (41551, 859), (41552, 859),
                 (41827, 987), (41828, 987), (41829, 987)],
    (714, 127): [(41599, 875), (41600, 875), (41606, 875), (41607, 875),
                 (42113, 1001), (42114, 1001), (42115, 1001)],
}


def unique(items):
    result = dict(items)
    if len(result) != len(items):
        raise ValueError("duplicate receipt key")
    return result


def authenticated(path):
    raw = (ROOT / path).read_bytes()
    if sha256(raw).hexdigest() != PINS[path]:
        raise ValueError(f"changed dependency {path}")
    return loads(raw, object_pairs_hook=unique) if path.endswith(".json") else raw


def text(values):
    return list(map(str, values))


def main():
    assert __debug__
    docs = {path: authenticated(path) for path in PINS}
    def get(name):
        return docs[f"inputs/{name}.json"]
    a, b = get("PR7370-SHA256"), get("PR7375-SHA256")
    for name in ("R115-PRICE.json", "R115-GEOMETRY.json"):
        assert a[name] == PINS[f"inputs/{name}"]
    for name in ("SELECTION.json", "PRIMARY.json", "SECOND.json"):
        assert b[name] == PINS[f"inputs/PR7375-{name}"]
    price, geom, old = get("R115-PRICE"), get("R115-GEOMETRY"), get("7334-READBACK")
    selection, primary, second = (get(f"PR7375-{s}") for s in ("SELECTION", "PRIMARY", "SECOND"))
    assert all(item["head"] == HEAD for item in (price,geom,old,selection,primary,second))
    assert price["caller"] == selection["caller"] == old["caller_head"] == CALLER
    assert geom["status"] == "EXHAUSTED" and not geom["timeout"] and geom["visited_events"] == 76466
    assert geom["selected_group"] == [3,241] and len(geom["candidate_rows"]) == 68
    assert selection["selected_group"] == [3,233] and len(selection["selected"]) == 17
    assert primary["counts"] == {"prefix exclusion": 17}
    assert len(second["rows"]) == 17
    groups = {tuple(row["endpoints"]): row for row in geom["groups"]}
    cases = []
    for endpoints, pivot in GROUPS.items():
        group = groups[endpoints]
        assert group["roles"] == [pivot] and group["banks"] == 7
        rows = [r for r in geom["candidate_rows"] if tuple(r["key"][2:]) == endpoints]
        assert [tuple(r["key"][:2]) for r in rows] == EXPECTED[endpoints]
        for row in rows:
            assert row["pivots"] == [pivot] and not row["owned"]
            assert row["key"][1] in group["labels"] and pivot in row["public"]
            assert len(row["public"]) in (2,3)
            cases.append(row | {"productive_parent_rank":5,"productive_child_ranks_sorted":[2,3]})
    assert sorted(row["key"] for row in cases) == sorted(selection["unselected"])
    assert len(cases) == len({tuple(r["key"]) for r in cases}) == 14

    earlier = get("CHART118-CONTROL")
    vectors = {k:{r:Q(v) for r,v in earlier[k].items()} for k in "abcd"}
    def dot(u, v):
        return sum(value*v.get(r,0) for r,value in u.items())
    assert dot(vectors["a"],vectors["b"]) == dot(vectors["c"],vectors["d"]) == 1
    assert old["copies"] == 17 and old["empty_root_credits"] == 0
    paid = Counter({int(r):n for r,n in old["paid"].items()})
    targets = Counter({int(r):n for r,n in old["targets"].items()})
    net = targets.copy()
    net.subtract(paid)
    assert (sum(paid.values()),sum(targets.values()),sum(r*n for r,n in net.items())) == (110519,22461,1424)
    delta = Counter({2:17,3:17,5:-17})
    assert price["productive_delta"] == {str(r):n for r,n in delta.items()} and price["paid_delta"] == {}
    lo, hi = map(Q,old["new_raw_interval"])
    probe = Q(price["probe"])
    assert probe == hi+Q(1,10**9)
    target, bit = Q(price["moonshot"]),Q(old["bit_premise"])
    cost = run_path(str(ROOT/"inputs/pricing.py"))["cost"]
    one, two, extra = net.copy(), net.copy(), net.copy()
    one.update(delta)
    two.update({r:2*n for r,n in delta.items()})
    extra.update(delta)
    extra[1] -= 1
    gross = cost(delta,hi)
    assert text(gross) == price["at_incumbent"]["gross_one"]
    assert cost(one,probe)[0] > 0 and cost(two,target)[1] < 0 and cost(extra,lo)[1] < 0
    print(dumps({
        "head":HEAD,"caller":CALLER,"pins":PINS,"word_sha256":price["word_sha256"],
        "sources":{"#7370":"a41edc3ae92332a7a1f1ba90e9ea4901d0530185",
                   "#7375":"2bf6a806bac491c69182ce366230c1fa7a646fec"},
        "cases":cases,"cohorts":[{"endpoints":list(e),"pivot":p} for e,p in GROUPS.items()],
        "case_count":14,"max_distinct_compatible_edits":2,"paid_delta":{},
        "productive_delta_per_edit":delta,"complete_paid":110519,
        "complete_productive_old":22461,"complete_productive_one":22478,"complete_productive_two":22495,
        "rank_surplus":1424,"empty_root_credits":0,
        "old_crossing":text((lo,hi)),"higher_probe":str(probe),"fixed_target":str(target),"retained_BIT":str(bit),
        "one_gross_at_old_upper":text(gross),"whole_gross_upper_at_old_upper":str(2*gross[1]),
        "complete_one_probe":text(cost(one,probe)),"complete_two_probe":text(cost(two,probe)),
        "complete_one_target":text(cost(one,target)),"complete_two_target":text(cost(two,target)),
        "one_with_one_additional_rank_one_at_old_lower":text(cost(extra,lo)),
        "control":"Historical chart118 pivot635: local and endpoint exact pairing both one",
        "caps":{"initial_cases":14,"initial_seconds":25,"exact_followup_cases":4,"exact_followup_seconds":35},
        "literal_decode":False,
    },indent=2,sort_keys=True))


if __name__ == "__main__":
    main()
