"""Cross-check the frozen pairs using exact prefix minors and full suffix supports."""
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import combinations
from json import dumps, loads
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PINS = {
    "R140-PRICE.json": "47a1e9f2a704bfe98f16cf4e36f1f592789595db211f6bb149dc77c026b6fb20",
    "R137-RESULT.json": "a109deda97d3b4f5ceb52814a50186035ea44ac1bdaf47281f564dcc2da239db",
    "R139-INDEPENDENT-RESULT.json": "ad45f533e423dbd1edffa84c3848ed1beaf2cd9b7e32feb5ce2f4a3deb84eddc",
    "R140-LEAD-RESULT.json": "2d07bdb7d32b1a50eb23e8af75eed40585f181fe924641298c1089518e6763b2",
}


def load(name):
    raw = (ROOT/"inputs"/name).read_bytes()
    if sha256(raw).hexdigest() != PINS[name]:
        raise ValueError("changed dependency "+name)
    return loads(raw)


def minor(left, right):
    """Return coordinates with a nonzero 2x2 minor, if one exists."""
    assert left and right
    x = min(left)
    a, b = left[x], right.get(x, 0)
    for y in sorted(left.keys() | right.keys()):
        value = a * right.get(y,0) - b * left.get(y,0)
        if value:
            return [x,y,str(value)]
    return None


def column(row):
    return {("public",r):Fraction(v) for r,v in row["final_public"]} | {
        ("COPY guard",t):Fraction(v) for t,_,v in row["copy_guards"]}


def main():
    assert __debug__
    assert minor({1:2,2:3},{1:-2,2:-3}) is None
    assert minor({1:2,2:3},{1:-2,2:-4}) == [1,2,"-2"]
    price, prefix, suffix, lead = map(load, PINS)
    assert all((x["head"],x["caller"])==(price["head"],price["caller"])
               for x in (prefix,suffix,lead))
    assert not prefix["unvisited"] and not suffix["unvisited"] and not lead["unresolved"]
    pre = {r["move_clock"]:{int(i):Fraction(v) for i,v in r["row"].items()}
           for r in prefix["records"]}
    post = {r["move_clock"]:column(r) for r in suffix["cases"]}
    expected = {tuple(r["clocks"]):r["disposition"] for r in lead["cases"]}
    assert pre.keys() == post.keys() and len(pre) == 47
    assert all(pre.values()) and all(post.values())
    assert len(expected) == price["case_cap"] == 1081
    counts = Counter()
    rank_witnesses = []
    for i,j in combinations(sorted(pre),2):
        m = minor(pre[i],pre[j])
        decision = expected.pop((i,j))
        if m:
            assert decision == "independent prefix rows"
        else:
            assert decision == "different guarded suffix support"
            symmetric_difference = sorted(post[i].keys() ^ post[j].keys())
            assert symmetric_difference
            k = symmetric_difference[0]
            assert bool(post[i].get(k)) != bool(post[j].get(k))
            rank_witnesses.append({"clocks":[i,j], "observable":list(k),
                "coefficients":[str(c.get(k,0)) for c in (post[i],post[j])],
                "support_sizes":[len(c) for c in (post[i],post[j])]})
        counts[decision] += 1
    assert not expected
    print(dumps({"head":price["head"],"caller":price["caller"],"pins":PINS,
        "cases":sum(counts.values()),"counts":counts,"exact_suffix_witnesses":rank_witnesses,
        "unresolved":[]},indent=2,sort_keys=True))


if __name__ == "__main__":
    main()
