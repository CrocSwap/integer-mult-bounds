"""Optimistic whole-word price of independently synthesizable BIT arrivals."""

from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction
import json
from pathlib import Path
import runpy
from time import monotonic

HERE = Path(__file__).resolve().parent
TARGET = Fraction(10018846261809, 2500000000000000)


def support(library, target):
    """Return one exact destination-slot XOR witness, or None."""
    pivots = {}
    for slot, row in library:
        certificate = 1 << slot
        while row:
            p = row.bit_length() - 1
            if p not in pivots:
                pivots[p] = (row, certificate)
                break
            u, s = pivots[p]
            row ^= u
            certificate ^= s
    certificate = 0
    while target:
        p = target.bit_length() - 1
        if p not in pivots:
            return None
        row, s = pivots[p]
        target ^= row
        certificate ^= s
    return [i for i in range(certificate.bit_length()) if certificate & (1 << i)]


def control():
    basis = [(3, 0b011), (5, 0b101)]
    assert support(basis, 0b110) == [3, 5]
    assert support(basis, 0b1000) is None
    assert support([], 0) == []


def run(root, seconds, cases):
    started = monotonic()
    audit = runpy.run_path(str(HERE / "trace_price.py"))
    word, invoice, pins = audit["read_inputs"](root)
    move_ids = [i for i, event in enumerate(word["program"]) if event[0] == "MOVE"]
    assert len(move_ids) == 2871
    ranks = {int(frame): x["dim"] for frame, x in word["frames"].items()}
    visited, eligible = 0, []

    def inspect(clock, slot, src, dst, row, slots):
        nonlocal visited
        if visited >= cases or monotonic() - started >= seconds:
            raise TimeoutError
        assert clock == move_ids[visited]
        visited += 1
        witness = support([(j, s[2]) for j, s in enumerate(slots)
                           if j != slot and s[1] == dst], row)
        if witness is None:
            return
        reconstruct = 0
        for j in witness:
            assert slots[j][1] == dst
            reconstruct ^= slots[j][2]
        assert reconstruct == row
        eligible.append({
            "clock": clock, "slot": slot, "from": src, "to": dst,
            "rank": abs(ranks[src] - ranks[dst]), "xor": witness,
        })

    try:
        moves, _, _ = audit["walk"](word, inspect)
    except TimeoutError:
        return {
            "status": "INCOMPLETE_CAP", "cases_visited": visited,
            "unvisited_move_ids": move_ids[visited:], "eligible_so_far": eligible,
            "pins": pins, "physical_sites": 0,
        }
    native = Counter(abs(ranks[src] - ranks[dst]) for src, dst, _ in moves.values())
    signed, copies = audit["profile"](invoice, native, word, ranks)
    saved = Counter(e["rank"] for e in eligible)
    lo, hi = audit["cost"]({r: copies*n for r, n in saved.items()}, TARGET)
    blo, bhi = audit["cost"](signed, TARGET)
    return {
        "status": "PASS_GLOBAL_DESTINATION_SPAN_UPPER",
        "target": str(TARGET), "cases_visited": visited, "native_instances": copies,
        "eligible_paid_moves": len(eligible), "all_eligible": eligible,
        "removed_rank_counts": dict(saved), "saving_interval": [str(lo), str(hi)],
        "raw_comparator_net": [str(blo), str(bhi)],
        "net_after_free_synthesis": [str(blo+lo), str(bhi+hi)],
        "decision": "PIVOT_NEGATIVE_UPPER" if bhi+hi < 0 else "EXACT_PHYSICAL_GATE_NEEDED",
        "seconds_cap": seconds, "cases_cap": cases, "pins": pins, "physical_sites": 0,
    }


def main():
    p = ArgumentParser(description=__doc__)
    p.add_argument("input_root", type=Path, nargs="?")
    p.add_argument("--seconds", type=int, default=240)
    p.add_argument("--cases", type=int, default=2871)
    p.add_argument("--self-test", action="store_true")
    args = p.parse_args()
    assert __debug__
    control()
    if args.self_test:
        print("PASS XOR reconstruction, missing coordinate and empty-value controls")
        return
    if args.input_root is None or not 1 <= args.seconds <= 240 or not 1 <= args.cases <= 2871:
        p.error("input root and caps of 240 seconds and 2,871 cases required")
    print(json.dumps(run(args.input_root, args.seconds, args.cases), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
