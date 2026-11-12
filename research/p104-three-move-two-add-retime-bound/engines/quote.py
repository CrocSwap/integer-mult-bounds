"""Price the exact two-ADD, three-public-MOVE stock before native replay."""
from collections import Counter, defaultdict
from fractions import Fraction
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    "inputs/R100-GEOMETRY.json": "075301daf545c8021800c36af19d05517e3c4136dac4e2114cb85204d0b31c64",
    "inputs/R92-PRICE.json": "05d7a5ebdd2eeedd6c8f534e8e2eeac22484daf9f387f4a6b88cc9eed22a6b8f",
    "inputs/BENCHMARK.json": "004331cff6ca8644489d7b7084e5c67439d74a2d283e4d64a9fdb9f88679253d",
    "inputs/pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
}


def unique(pairs):
    obj = dict(pairs)
    if len(obj) != len(pairs):
        raise ValueError("duplicate JSON key")
    return obj


def authenticate(path, digest):
    data = (ROOT / path).read_bytes()
    if sha256(data).hexdigest() != digest:
        raise ValueError(f"changed input {path}")
    return data


def output():
    raw = [authenticate(path, digest) for path, digest in PINS.items()]
    geometry, price, benchmark = [loads(data, object_pairs_hook=unique) for data in raw[:3]]
    assert geometry["head"] == price["head"] == benchmark["head"] == "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
    assert geometry["timeout"] is None and geometry["first_unvisited_event"] is None
    cost = run_path(str(ROOT / "inputs/pricing.py"))["cost"]
    hist = lambda x: Counter({int(k): v for k, v in x.items()})
    target, paid = hist(price["old_targets"]), hist(price["old_paid"])
    assert sum(target.values()) == 22461 and sum(paid.values()) == 110519
    base = target.copy()
    base.subtract(paid)
    assert sum(r * count for r, count in base.items()) == 1424
    lower, upper = map(Fraction, benchmark["crossing"])
    probe, fixed = (Fraction(price[key]) for key in ("probe", "moonshot"))
    assert upper == Fraction(price["old_crossing_upper"])
    by_role = defaultdict(list)
    for row in geometry["pairs"]:
        by_role[row["key"][2]].append(row)
    candidates = []
    profiles = Counter()
    for role, pairs in sorted(by_role.items()):
        for left, right in zip(pairs, pairs[1:]):
            start, middle, _ = left["key"]
            assert middle == right["key"][0] and left["charts"][1:] == right["charts"][:2]
            end = right["key"][1]
            ops = left["contacts"] + right["contacts"]
            if len(ops) != 2 or any(op[0] != "ADD" for _, op in ops):
                continue
            ranks = [*left["ranks"][:2], right["ranks"][1]]
            delta = Counter(ranks)
            delta.subtract([sum(ranks)])
            delta = {r: 17 * v for r, v in delta.items() if v}
            assert sum(delta.values()) == 34 and sum(r * v for r, v in delta.items()) == 0
            full = base.copy()
            full.update(delta)
            assert cost(full, probe)[0] > 0 and cost(full, lower)[1] < 1
            profiles[role] += 1
            candidates.append({
                "role": role, "clocks": [start, middle, end], "charts": [*left["charts"], right["charts"][-1]],
                "contacts": ops, "old_ranks": ranks, "new_rank": sum(ranks),
                "paid_delta": {r: -v for r, v in delta.items()},
                "raw_upper": str(cost(delta, lower)[1]), "target_upper": str(cost(delta, fixed)[1]),
                "probe_lower": str(cost(full, probe)[0]),
            })
    assert dict(profiles) == {198: 1, 532: 2, 1250: 2}
    for role, count in profiles.items():
        if count == 2:
            first, second = [row for row in candidates if row["role"] == role]
            assert set(first["clocks"]) & set(second["clocks"])
    def max_per_role(field):
        return sum(max(Fraction(row[field]) for row in candidates if row["role"] == role) for role in profiles)
    return {
        "head": price["head"], "caller": price["caller_head"], "pins": PINS,
        "word_sha256": price["word_sha256"], "before_paid": 110519, "after_paid_one": 110485,
        "productive": 22461, "surplus": 1424, "compatible_cap": len(profiles),
        "gross_upper": str(max_per_role("raw_upper")),
        "fixed_target_complete_upper": str(cost(base, fixed)[1] + max_per_role("target_upper")),
        "candidates": candidates, "event_cap": 76466, "typed_cut_cap": 150000, "runner_seconds": 20,
        "old_crossing": [str(lower), str(upper)],
    }


if __name__ == "__main__":
    assert __debug__
    print(dumps(output(), indent=2, sort_keys=True))
