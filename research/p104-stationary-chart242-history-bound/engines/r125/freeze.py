"""Freeze and preprice one temporal correction at chart 242 without word access."""
from collections import Counter
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
from runpy import run_path

ROOT = Path(__file__).resolve().parent
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CALLER = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
PIVOT, CUT, CHART = 1123, 41740, 242
PINS = {
    "inputs/R96-PRICE.json": "a78be64c3e3ae8a0e532237c4dd3541aa9ad3fcbbc3c25d79c8a03fb7e07c525",
    "inputs/R96-GEOMETRY.json": "c6f9f018df8b58fcdf4f44356bd59bcac6d411b7845104ff4ad372ed4a95cfbd",
    "inputs/R97-EXACT.json": "95d34e468683aa64e19d3e4d62745b9fc1d4305b00d25054b34bb5a668639b4b",
    "inputs/R97-MODULAR.json": "6710e8711907a0c8412660696cf821e69fdc42bebf7fc24689fc3385fe7aabf3",
    "inputs/READBACK.json": "337668788fb39ec9575887f9c5faf438a880471f78d936357dabf7deeac5de82",
    "inputs/pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
}
PROTECTED = {319, 863, 1355, 1568}


def unique(items):
    result = dict(items)
    if len(result) != len(items):
        raise ValueError("duplicate JSON key")
    return result


def interval(bounds):
    return list(map(str, bounds))


def main():
    docs = {}
    for name, digest in PINS.items():
        raw = (ROOT / name).read_bytes()
        if sha256(raw).hexdigest() != digest:
            raise ValueError(f"changed dependency {name}")
        if name.endswith(".json"):
            docs[name] = json.loads(raw, object_pairs_hook=unique)
    price, geometry, exact, modular, readback = docs.values()
    assert {doc["head"] for doc in docs.values()} == {HEAD}
    assert price["caller"] == readback["caller_head"] == modular["caller"] == CALLER
    assert geometry["price_sha256"] == PINS["inputs/R96-PRICE.json"]
    cohort = price["cohort"]
    assert len(cohort) == 15 and PIVOT in cohort
    key = CUT, CHART
    row, = (r for r in exact["results"] if tuple(r["key"]) == key)
    axis = {str(PIVOT): "1"}
    assert row["prefix_pure_basis"] == [{"a": axis, "c": axis}]
    assert row["suffix_pure_basis"] == [{"b": {"30": "1"}, "d": {"361": "-1/2"}}]
    assert row["cut_pairing_matrix"] == row["endpoint_pairing_matrix"] == [["0"]]
    records = {}
    entries = [(r["key"], r) for r in geometry["selected"]]
    entries.extend((r["key"], r["prefix"]["bank"]) for r in modular["results"])
    for raw_key, bank in entries:
        bank_key = tuple(raw_key)
        if bank_key in records:
            raise ValueError(f"duplicate bank key {bank_key}")
        records[bank_key] = bank
    assert len(records) == 326 and set(records) == set(map(tuple, geometry["all_representative_keys"]))
    assert records[key]["public"] == row["public"] and not records[key]["owned"]
    banks = []
    for (t, c), bank in sorted(records.items()):
        if c == CHART and t >= CUT:
            assert not bank["owned"]
            targets = [role for role in bank["public"] if role not in PROTECTED]
            banks.append({"cut": t, "public": bank["public"], "injection_targets": targets})
    pairs = sum(len(r["injection_targets"]) for r in banks)
    assert len(banks) == 19 and pairs == 354

    paid, productive = (Counter({int(k): v for k, v in readback[name].items()})
                        for name in ("paid", "targets"))
    assert readback["copies"] == 17 and readback["empty_root_credits"] == 0
    assert (sum(paid.values()), sum(productive.values())) == (110519, 22461)
    old = productive.copy()
    old.subtract(paid)
    delta = {4: 34, 8: -17}
    assert price["paid_delta"] == {} and price["productive_delta"] == {str(k): v for k, v in delta.items()}
    new = old.copy()
    new.update(delta)
    assert sum(r*n for r,n in old.items()) == sum(r*n for r,n in new.items()) == 1424
    at, probe, moon = map(Fraction, (price["incumbent"], price["probe"], price["moonshot"]))
    cost = run_path(str(ROOT / "inputs/pricing.py"))["cost"]
    gain = cost(delta, at)
    assert interval(gain) == price["at_incumbent"]["gross_one"]
    complete = cost(new, probe)
    extra = cost(new, at)[1] - 1
    moon_upper = cost(new, moon)[1]
    assert complete[0] > 0 > extra and moon_upper < 0
    print(json.dumps({
        "head": HEAD, "caller": CALLER, "word_sha256": price["word_sha256"], "pins": PINS,
        "retirement": {"cut": CUT, "chart": CHART, "pivot": PIVOT, "prefix": axis},
        "cohort": cohort, "old_suffix": row["suffix_pure_basis"],
        "injection_banks": banks, "injection_keys": pairs, "protected": sorted(PROTECTED),
        "native_calls": 17, "paid": 110519, "productive_old": 22461, "productive_new": 22478,
        "paid_delta": {}, "productive_delta": delta, "rank_surplus": 1424, "empty_root_credits": 0,
        "crossing_upper": str(at), "probe": str(probe), "target": str(moon),
        "one_gross": interval(gain), "complete_probe": interval(complete),
        "extra_rank_one_complete_upper": str(extra), "fixed_target_complete_upper": str(moon_upper),
        "old_ordinary_headroom": readback["ordinary_headroom"], "old_precision_headroom": readback["context_headroom"],
        "old_owned_peak": readback["owned_peak"], "old_native_grid": readback["native_grid"],
        "limits": {"banks": 19, "injection_keys": pairs, "runner_seconds": 35, "events_per_pass": 76466,
                   "physical_prototypes": 1, "physical_seconds": 120, "max_literal_injections": 16},
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    assert __debug__
    main()
