"""Directed complete preprice for one Type B stage-17 productive retag."""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path

ROOT = Path(__file__).resolve().parent
PINS = {
    "inputs/R92-PRICE.json": "05d7a5ebdd2eeedd6c8f534e8e2eeac22484daf9f387f4a6b88cc9eed22a6b8f",
    "inputs/pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
}
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CALLER = "07a76c5e2738882c0cb322278e56f6cae3c9885d"


def unique(items):
    result = dict(items)
    assert len(result) == len(items), "Duplicate JSON key"
    return result


def main():
    assert __debug__
    for name, digest in PINS.items():
        assert sha256((ROOT / name).read_bytes()).hexdigest() == digest
    base = loads((ROOT / "inputs/R92-PRICE.json").read_bytes(), object_pairs_hook=unique)
    assert base["head"] == HEAD and base["caller_head"] == CALLER
    paid, target = [Counter({int(r): n for r, n in base[k].items()})
                    for k in ("old_paid", "old_targets")]
    stock = target.copy()
    stock.subtract(paid)
    assert (paid.total(), target.total(), sum(r*n for r, n in stock.items())) == (110519, 22461, 1424)
    delta = {129: 8, 17: 8, 137: -8, 9: -8}
    updated = target.copy()
    updated.update(delta)
    assert updated.total() == target.total() and min(updated.values()) >= 0
    assert sum(r*n for r, n in delta.items()) == 0
    changed = stock.copy()
    changed.update(delta)
    cost = run_path(str(ROOT / "inputs/pricing.py"))["cost"]
    receipt = {}
    for name in ("old_crossing_upper", "probe", "moonshot"):
        k = Q(base[name])
        gross, previous, complete = [cost(h, k) for h in (delta, stock, changed)]
        assert gross[0] > 0
        extra = changed.copy()
        extra[1] -= 1
        with_extra = cost(extra, k)
        if name == "old_crossing_upper":
            assert previous[1] < 0 < complete[0] and with_extra[1] < 0
        if name == "probe":
            assert previous[1] < 0 < complete[0]
        receipt[name] = {
            "kappa": str(k),
            "one_edit_gross": list(map(str, gross)),
            "old_complete_margin": list(map(str, previous)),
            "new_complete_margin": list(map(str, complete)),
            "with_one_extra_paid_rank_one": list(map(str, with_extra)),
            "full_singleton_stock_relaxed_gross_upper": str(34*gross[1]),
            "stage17_relaxed_two_slot_gross_upper": str(2*gross[1]),
        }
    print(dumps({"head": HEAD, "caller": CALLER, "pins": PINS, "target_delta": delta, "paid_delta": {},
                 "rank_surplus": 1424, "paid_positions": 110519, "productive_positions": 22461,
                 "local_transfer": {"body_stage": 17, "donor_root": 0, "receiver_rail": 32, "ports": 8},
                 "full_singleton_stock_relaxation": 34, "strict_initial_scope_compatible_instances": 1,
                 "price": receipt, "scope": "Ordinary/setup/routing, exact phase and physical role bindings remain open. Grants ancillary work free in the upper."},
                 sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
