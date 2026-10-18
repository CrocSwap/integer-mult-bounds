#!/usr/bin/env python3
"""Bounded common-sum factoring of the pinned, arbitrary-input frame-509 block.

Only advance an existing d ^= s gate across an interval that writes neither
register. Conjugate each intervening read of d, then cancel equal XOR gates
separated solely by commuting gates. All candidates retain ordered registers.
This finite family is not a minimum-circuit or general impossibility claim.
Prepared for anudeepadi with substantial OpenAI Codex assistance; Apache-2.0.
"""

import argparse
import gzip
import hashlib
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"
SOURCE_SHA256 = "e3e301e62bc2b41dbf1ceac0acf3d35824ebeab1848c5a2142d4577b109da52f"
SEED = 7
START, STOP, FRAME = 283, 314, 509


def need(condition, message):
    if not condition:
        raise ValueError(message)


def transfer(ops, n, positive=False):
    """Rows of the ordered transfer over F2, or nonnegative integers."""
    rows = [[int(i == j) for j in range(n)] for i in range(n)]
    for d, s in ops:
        need(0 <= d < n and 0 <= s < n and d != s, "Invalid XOR gate")
        rows[d] = [a + b if positive else a ^ b
                   for a, b in zip(rows[d], rows[s])]
    return rows


def dominated(a, b):
    return all(x <= y for row_a, row_b in zip(a, b)
               for x, y in zip(row_a, row_b))


def commute(a, b):
    return a[0] != b[1] and b[0] != a[1]


def cancel(ops):
    """Remove identical gates only if every intervening gate commutes."""
    result = []
    for gate in ops:
        for index in range(len(result) - 1, -1, -1):
            if result[index] == gate:
                del result[index]
                break
            if not commute(gate, result[index]):
                result.append(gate)
                break
        else:
            result.append(gate)
    return result


def advance(ops, pivot, insertion):
    """Return exact conjugated candidate, or None outside the search family."""
    d, s = ops[pivot]
    interval = ops[insertion:pivot]
    if any(target in (d, s) for target, _ in interval):
        return None
    middle = []
    for target, source in interval:
        middle.append((target, source))
        if source == d:
            # After advancing d ^= s, old d is reconstructed as new d + s.
            middle.append((target, s))
    return cancel(ops[:insertion] + [(d, s)] + middle + ops[pivot + 1:])


def synthesize():
    compressed = (ROOT / SOURCE).read_bytes()
    need(hashlib.sha256(compressed).hexdigest() == SOURCE_SHA256,
         "Source hash mismatch")
    source = json.loads(gzip.decompress(compressed))
    block = source["B"][START:STOP]
    need(len(block) == 31, "Unexpected source block length")
    need(all(frame == FRAME and len(inputs) == 1
             for frame, _, inputs in block), "Unexpected source gate")
    registers = sorted({wire for _, target, inputs in block
                        for wire in [target] + inputs})
    need(registers == [17, 22, 33, 38, 50, 60, 67, 77, 87, 92, 468],
         "Unexpected source register identities")
    positions = {wire: i for i, wire in enumerate(registers)}
    original = [(positions[target], positions[inputs[0]])
                for _, target, inputs in block]
    n = len(registers)
    target = transfer(original, n)
    forward = transfer(original, n, positive=True)
    reverse = transfer(original[::-1], n, positive=True)
    attempts = [(pivot, insertion) for pivot in range(1, len(original))
                for insertion in range(pivot)]
    random.Random(SEED).shuffle(attempts)
    best = original
    eligible = exact = admissible = 0
    minimum_exact = len(original)
    winning_move = None
    for pivot, insertion in attempts:
        candidate = advance(original, pivot, insertion)
        if candidate is None:
            continue
        eligible += 1
        # Full matrix equality includes the arbitrary initial carrier bit.
        need(transfer(candidate, n) == target, "Candidate ordered map differs")
        exact += 1
        minimum_exact = min(minimum_exact, len(candidate))
        if not (dominated(transfer(candidate, n, positive=True), forward)
                and dominated(transfer(candidate[::-1], n, positive=True), reverse)):
            continue
        admissible += 1
        if len(candidate) < len(best):
            best = candidate
            winning_move = {"pivot_local_index": pivot,
                            "insertion_local_index": insertion,
                            "gate_registers": [registers[w] for w in original[pivot]]}
    need(len(best) == 26, "Unexpected synthesis result length")
    need(transfer(best, n) == target, "Selected candidate ordered map differs")
    recipe = {
        "phase": "B", "start": START, "stop": STOP, "frame": FRAME,
        "registers": registers,
        "replacement_local_ops": [list(op) for op in best],
        "source": SOURCE, "source_sha256": SOURCE_SHA256,
        "assignment_seed": SEED,
        "method": "Advance one existing XOR across an interval writing neither of its registers; conjugate reads and cancel commuting equal gates.",
        "baseline_operations": len(original), "replacement_operations": len(best),
        "search": {
            "attempted_pivot_insertion_pairs": len(attempts),
            "eligible_pairs": eligible, "exact_candidates": exact,
            "positive_transfer_admissible_candidates": admissible,
            "minimum_operations_in_examined_family": minimum_exact,
            "winning_move": winning_move,
            "stopping_rule": "Exhaust all 465 pivot/insertion pairs of the 31-operation source block once; no iterative resynthesis.",
            "optimality_claim": False,
        },
    }
    return recipe


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Write recipe.json instead of checking it.")
    args = parser.parse_args()
    recipe = synthesize()
    path = Path(__file__).with_name("recipe.json")
    if args.write:
        path.write_text(json.dumps(recipe, indent=2) + "\n")
    else:
        need(json.loads(path.read_text()) == recipe,
             "recipe differs; rerun with --write")
    print(json.dumps({"baseline_operations": recipe["baseline_operations"],
                      "replacement_operations": recipe["replacement_operations"],
                      "search": recipe["search"]}, sort_keys=True))


if __name__ == "__main__":
    main()
