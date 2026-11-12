"""Directed paid-only preprice of both frozen chart-32 triads."""
from collections import Counter
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
from runpy import run_path

ROOT = Path(__file__).resolve().parent
PINS = {
    "inputs/R100-GEOMETRY.json": "075301daf545c8021800c36af19d05517e3c4136dac4e2114cb85204d0b31c64",
    "inputs/R100-INDEPENDENT.json": "5462d132a6610dc8953332cadcad0c9b2096fa7db2bc131af3dbd80614b52d25",
    "inputs/R92-PRICE.json": "05d7a5ebdd2eeedd6c8f534e8e2eeac22484daf9f387f4a6b88cc9eed22a6b8f",
    "inputs/BENCHMARK.json": "004331cff6ca8644489d7b7084e5c67439d74a2d283e4d64a9fdb9f88679253d",
    "inputs/pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
}
KEYS = ((31303, 38665, 319), (31360, 37214, 1081))


def unique(items):
    result = dict(items)
    if len(items) != len(result):
        raise ValueError("duplicate JSON key")
    return result


def spans(cost, hist, at):
    return [str(bound) for bound in cost(hist, at)]


def main():
    docs = []
    for path, expected in PINS.items():
        data = (ROOT / path).read_bytes()
        if sha256(data).hexdigest() != expected:
            raise ValueError(f"changed dependency {path}")
        if path.endswith(".json"):
            docs.append(json.loads(data, object_pairs_hook=unique))
    lead, independent, source, benchmark = docs
    assert lead["head"] == independent["head"] == source["head"] == benchmark["head"]
    old_paid = Counter({int(k): v for k, v in source["old_paid"].items()})
    targets = Counter({int(k): v for k, v in source["old_targets"].items()})
    old = targets.copy()
    old.subtract(old_paid)
    assert (sum(old_paid.values()), sum(targets.values()), sum(r*n for r, n in old.items())) == (110519, 22461, 1424)
    at = Fraction(source["old_crossing_upper"])
    probe = Fraction(source["probe"])
    target = Fraction(source["moonshot"])
    assert at == Fraction(benchmark["crossing"][1]) < probe < Fraction(source["retained_bit_premise"]) < target
    cost = run_path(str(ROOT / "inputs/pricing.py"))["cost"]
    stock = []
    for key in KEYS:
        row, = (r for r in lead["pairs"] if tuple(r["key"]) == key)
        reverse, = (r for r in independent["pairs"] if tuple(r["key"]) == key)
        assert row["charts"] == reverse["charts"] == [3, 32, 355]
        assert row["ranks"] == reverse["ranks"] == [1, 1, 2]
        assert row["contacts"] == [[c["clock"], c["event"]] for c in reverse["contacts"]]
        stock.append({k: row[k] for k in ("key", "charts", "contacts")})
    # Relax peer ranks to p+q<=9. Both site choices are granted independent compatibility.
    profiles = []
    for side, shift in (("A", -1), ("C", 1)):
        for p in range(10):
            for q in range(10 - p):
                new_ranks = (1 + shift, 1 - shift, p + shift, q - shift)
                if min(new_ranks) < 0 or max(new_ranks) > 9:
                    continue
                old_ranks = (1, 1, p, q)
                change = Counter(r for r in old_ranks if r)
                change.subtract(r for r in new_ranks if r)
                gain = Counter({r: 17*n for r, n in change.items() if n})
                assert sum(r*n for r, n in gain.items()) == 0
                new = old.copy()
                new.update(gain)
                assert all(old_paid[r] >= n for r, n in gain.items())
                profiles.append({"side": side, "peer_old": [p, q], "paid_delta": {r: -n for r, n in gain.items()},
                                 "paid_after": 110519 - sum(gain.values()), "gross": spans(cost, gain, at),
                                 "target_gross": spans(cost, gain, target), "complete_probe": spans(cost, new, probe)})
    upper = max(Fraction(r["gross"][1]) for r in profiles)
    at_target = max(Fraction(r["target_gross"][1]) for r in profiles)
    result = {
        "head": benchmark["head"], "caller_head": source["caller_head"], "kappa": benchmark["kappa"],
        "word_sha256": source["word_sha256"], "pins": PINS, "stock": stock,
        "old_crossing_upper": str(at), "probe": str(probe), "fixed_moonshot": str(target),
        "old_complete": spans(cost, old, at), "productive_count": sum(targets.values()), "rank_surplus": 1424,
        "profiles": profiles, "one_site_upper": str(upper), "compatible_two_site_upper": str(2*upper),
        "compatible_two_site_with_extra_rank_one_complete_upper": str(cost(old, at)[1]+2*upper-1),
        "complete_moonshot_upper": str(cost(old, target)[1]+2*at_target),
        "runner_limits": {"literal_events": 76466, "windows": 2, "coframes": 4, "seconds": 20,
                          "physical_prototypes": 1, "prototype_seconds": 120},
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    assert __debug__
    main()
