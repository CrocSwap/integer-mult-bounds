"""Count and price the entire quiet paired-IDLE family of the retained caller."""
import argparse
from collections import Counter, defaultdict
from fractions import Fraction
import gzip
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from itertools import product
import json
from pathlib import Path

PINS = {
    "check.py": "460ed9a77d66264b00c31d0a7f8dab1db9aab21ec4cc0eaf0452bd4be4ef585e",
    "EFREE-CALLER.json.gz": "757b3523798f840bdb02028b23708c3416627a99ea09e7a3c4bcdc5cd0c7ce4b",
    "EFREE-RESULT.json": "a46b6c6040f75184cab5467656811ad988c216e3bc8e44d595a5015b6e49620b",
    "independent/interval_gate.py": "8dc2bc4c64cba3f83c664373984a075f1a14b4d53958084091345c8cab189dec",
}
TARGET = Fraction("0.0040075385047236")
TRIAL = Fraction("0.004008162992724")


def read(path, key):
    data = (path / key).read_bytes()
    if sha256(data).hexdigest() != PINS[key]:
        raise ValueError(f"SHA-256 mismatch: {key}")
    return data


def load(path):
    spec = spec_from_file_location(path.stem, path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def touches(event):
    op, *args = event
    if op in ("ADD", "SWAP", "QUERY"):
        return set(args)
    if op == "LOCAL":
        return set(args[1:])
    if op == "IDLE_ONE":
        return {args[0]}
    raise ValueError(op)


def census(caller, invoice):
    events = caller["events"]
    masks = defaultdict(list)
    for i, event in enumerate(events):
        if event[0] == "IDLE_ONE":
            masks[tuple(event[2])].append((i, event[1]))
    assert len(masks) == 16 and all(len(rows) == 2 for rows in masks.values())
    assert invoice["event_counts"]["IDLE_ONE"] == 32
    ports, body = caller["ports"], caller["body_rank"]
    assert (ports, body, caller["ambient_rank"]) == (111, 7, 127)
    pairs = []
    for mask, ((lo, a), (hi, b)) in sorted(masks.items()):
        assert a != b and lo < hi
        contacts = [i for i in range(lo + 1, hi) if touches(events[i]) & {a, b}]
        pairs.append({"events": [lo, hi], "roles": [a, b], "mask": mask, "rank": len(mask) * body,
                      "ports": ports, "intervening_contacts": contacts})
    quiet = [p for p in pairs if not p["intervening_contacts"]]
    assert len(quiet) == 7 and sorted(p["rank"] for p in quiet) == list(range(14, 57, 7))
    assert len({i for pair in pairs for i in pair["events"]}) == 32
    windows = sorted(pair["events"] for pair in quiet)
    assert all(left[1] < right[0] for left, right in zip(windows, windows[1:]))
    assert [p["events"] for p in quiet if p["rank"] == 56] == [[19, 24]]
    paid = {int(r): n for r, n in invoice["paid"].items()}
    idle_profile = Counter()
    for pair in pairs:
        idle_profile[pair["rank"]] += 2 * ports
    assert all(paid[r] >= n for r, n in idle_profile.items())
    return pairs, quiet, idle_profile


def commute_pairs(events, pairs):
    ordered = list(enumerate(events))
    swaps = []
    for pair in sorted(pairs, key=lambda row: row["events"][0]):
        lo, hi = pair["events"]
        a = next(i for i, (old, _) in enumerate(ordered) if old == lo)
        b = next(i for i, (old, _) in enumerate(ordered) if old == hi)
        assert a < b and ordered[b][1][0] == "IDLE_ONE"
        for j in range(b, a + 1, -1):
            old, intervening = ordered[j - 1]
            assert not touches(ordered[j][1]) & touches(intervening)
            swaps.append([hi, old])
            ordered[j - 1], ordered[j] = ordered[j], ordered[j - 1]
    positions = {old: i for i, (old, _) in enumerate(ordered)}
    assert len(positions) == len(events)
    assert len(swaps) == 243
    assert all(positions[row["events"][1]] == positions[row["events"][0]] + 1 for row in pairs)
    return swaps, [event for _, event in ordered]


def mask_address(z, axes, q):
    return tuple((-v) % q if i in axes else v for i, v in enumerate(z))


def binary_rank(rows):
    basis = {}
    for row in rows:
        while row:
            pivot = row.bit_length() - 1
            if pivot not in basis:
                basis[pivot] = row
                break
            row ^= basis[pivot]
    return len(basis)


def finite_control(q):
    # Two labels exchange axes 1 and 2. Targets depend on the output label.
    # A one-child bypass may use either label and still may not change
    # the physical input address before its sole child.
    child1 = [{0}, {0}]
    child2 = [{1}, {2}]
    targets = [{0, 1}, {0, 2}]
    labels = range(2)
    good = Counter()
    for z in product(range(q), repeat=3):
        bypass = {z, *(mask_address(z, r, q) for r in child1 + child2)}
        good[z] = sum(mask_address(z, targets[g], q) not in bypass for g in labels)
        for g in labels:
            assert mask_address(mask_address(z, child1[g], q), child2[g], q) == mask_address(z, targets[g], q)
    selected = (1, 1, 1)
    assert good[selected] == 2
    assert sum(good.values()) == 2 * q * (q - 1) ** 2

    # Work at the common physical input address. One field per cover
    # after intake x_g + y_(g xor 1) gives just two independent values.
    # With both fields preserved, the required four cells have rank four.
    intake = [0b1001, 0b0110]
    assert binary_rank(intake) == 2
    assert binary_rank([1, 2, 4, 8]) == 4
    # Releasing to either cover can expose the two values repeatedly but
    # can never separate the four original fields.
    assert binary_rank([intake[0], intake[1], intake[1], intake[0]]) == 2
    # A fictitious ordinary address-changing bypass to the target would
    # invalidate the cut, so the scope assumption is load-bearing.
    assert mask_address(selected, targets[0], q) not in {selected, *(mask_address(selected, r, q) for r in child1 + child2)}
    return {"digit_cardinality": q, "physical_addresses": q ** 3, "good_label_address_pairs": sum(good.values()),
            "common_input": list(selected), "bank_rank": 2, "target_rank": 4,
            "independent_two_child_address_match": True}


def directed_price(gate, invoice, pairs, quiet, kappa):
    paid = {int(r): n for r, n in invoice["paid"].items()}
    targets = {int(r): n for r, n in invoice["targets"].items()}
    deficit = gate.sub(gate.moment(paid, kappa), gate.moment(targets, kappa))
    assert deficit[0] > 0
    aggregate = gate.exact(0)
    quiet_total = gate.exact(0)
    quiet_keys = {tuple(pair["events"]) for pair in quiet}
    minima = {}
    for pair in pairs:
        a = pair["rank"]
        # By monotonicity and concavity, among proper positive ranks with
        # r+s>=a the minimum is attained at (1,a-1).
        debit = gate.moment({1: 2, a - 1: 2, a: -2}, kappa)
        assert debit[0] > 0
        full_debit = gate.mul(gate.exact(pair["ports"]), debit)
        aggregate = gate.add(aggregate, full_debit)
        if tuple(pair["events"]) in quiet_keys:
            quiet_total = gate.add(quiet_total, full_debit)
        minima[a] = gate.show(debit)
    r49 = gate.moment({49: 4, 56: -2}, kappa)
    assert aggregate[0] > 0 and r49[0] > 0
    return {"kappa": str(kappa), "unchanged_full_raw_deficit": gate.show(deficit),
            "min_surcharge_by_target_rank": minima,
            "min_surcharge_if_all_quiet_pairs_replaced": gate.show(quiet_total),
            "min_surcharge_if_all_reordered_pairs_replaced": gate.show(aggregate),
            "rank49_rank49_surcharge_per_rank56_pair": gate.show(r49),
            "optimistic_total_saving_optional_replacement": ["0", "0"]}


def main():
    if not __debug__:
        raise RuntimeError("Run with assertions enabled")
    p = argparse.ArgumentParser(description=__doc__)
    root = Path(__file__).resolve().parents[2]
    p.add_argument("--bit-package", type=Path, default=root / "research/paired-query-only-bit")
    p.add_argument("--expected", type=Path)
    a = p.parse_args()
    caller = json.loads(gzip.decompress(read(a.bit_package, "EFREE-CALLER.json.gz")))
    invoice = json.loads(read(a.bit_package, "EFREE-RESULT.json"))
    gate_path = a.bit_package / "independent/interval_gate.py"
    read(a.bit_package, "independent/interval_gate.py")
    gate = load(gate_path)
    pairs, quiet, profile = census(caller, invoice)
    swaps, reordered = commute_pairs(caller["events"], pairs)
    read(a.bit_package, "check.py")
    checker = load(a.bit_package / "check.py")
    forward = checker.forward({**caller, "events": reordered})
    assert forward == checker.forward(caller) == 1444
    result = {
        "adjacent_disjoint_reorder": swaps, "reordered_pair_placements": 16 * 111,
        "reordered_formal_forward_coefficients": forward,
        "pins": PINS, "pairs": pairs, "nominal_same_mask_pair_placements": 16 * 111,
        "quiet_pair_placements": 7 * 111, "contacting_before_reorder_placements": 9 * 111,
        "nominal_rank56_pairs": 2 * 111, "quiet_rank56_pairs": 111,
        "idle_paid_profile": dict(profile),
        "controls": [finite_control(q) for q in (3, 5, 9)],
        "directed_prices": [directed_price(gate, invoice, pairs, quiet, k) for k in (TARGET, TRIAL)],
    }
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if a.expected is not None and a.expected.read_text(encoding="utf-8") != encoded:
        raise ValueError("Frozen exact receipt mismatch")
    print(encoded, end="")
    if a.expected is not None:
        print("PASS_BIT_FULL_COVER_VOLUME_CUT quiet_pairs=777 reordered_pairs=1776 aggregate_credit=0 no_new_kappa")


if __name__ == "__main__":
    main()
