#!/usr/bin/env python3
"""Code-disjoint concrete F2 matrix/dirty-state replay of the credited root word.

Eight-factor expansion is rebuilt independently; verify.py is not imported.
Prepared for Adam Gall with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import hashlib
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def read_pinned(path):
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
    entry = next(item for item in manifest["files"] if item["path"] == path)
    payload = (ROOT / path).read_bytes()
    need(hashlib.sha256(payload).hexdigest() == entry["sha256"], "source hash mismatch")
    return json.loads(payload)


def act(matrix, value):
    return sum(((row & value).bit_count() % 2) << i for i, row in enumerate(matrix))


def common_b(value, bank):
    for j in range(8):
        value = act(bank[f"B{j}"], value)
    return value


def matrix_bank(width):
    identity = [1 << j for j in range(width)]
    bank = {}
    for j in range(8):
        rows = list(identity)
        if width > 1:
            target = j % width
            source = (target + 1 + (j // width) % (width - 1)) % width
            rows[target] ^= rows[source]
        bank[f"B{j}"] = rows
    for mask in range(1, 32):
        if width == 1:
            bank[f"A{mask}"] = [1]
        else:
            bank[f"A{mask}"] = [((mask + 7 * row) * 29 ^ (mask << row)) & ((1 << width) - 1)
                                 for row in range(width)]
    return bank


def emit_product(factors, source, target, level=0, inverse=False):
    if len(factors) == 1:
        yield source, target, factors[0]
        return
    scratch = 37 + level
    middle = len(factors) // 2
    children = [(factors[:middle], source, scratch, False),
                (factors[middle:], scratch, target, False),
                (factors[:middle], source, scratch, True),
                (factors[middle:], scratch, target, True)]
    if inverse:
        children = [(f, s, t, not inv) for f, s, t, inv in reversed(children)]
    for factors2, source2, target2, inverse2 in children:
        yield from emit_product(factors2, source2, target2, level + 1, inverse2)


def expand(word):
    leaves = []
    for event in word:
        if event[0] == "Q":
            leaves.extend(emit_product(tuple(f"B{j}" for j in range(8)), event[1], 36))
        elif event[0] == "R":
            leaves.append((36, 4 + event[1], f"A{event[1]}"))
        elif event[0] == "X":
            leaves.append((event[1], event[2], None))
        else:
            raise ValueError("unknown event")
    return leaves


def run_leaves(leaves, initial, bank):
    state = list(initial)
    for source, target, operator in leaves:
        need(source != target, "aliased ports")
        state[target] ^= state[source] if operator is None else act(bank[operator], state[source])
    return state


def run_root(word, initial, bank):
    state = list(initial)
    for event in word:
        if event[0] == "X":
            state[event[2]] ^= state[event[1]]
        elif event[0] == "Q":
            state[36] ^= common_b(state[event[1]], bank)
        else:
            state[4 + event[1]] ^= act(bank[f"A{event[1]}"], state[36])
    return state


def wanted(initial, bank):
    state = list(initial)
    for mask in range(1, 32):
        total = 0
        for j in range(5):
            if mask >> j & 1:
                total ^= initial[j]
        state[4 + mask] ^= act(bank[f"A{mask}"], common_b(total, bank))
    return state


def inputs(width):
    for wire in range(40):
        for bit in range(width):
            state = [0] * 40
            state[wire] = 1 << bit
            yield state
    for probe in range(16):
        yield [((wire + 3) * (probe + 5) ^ (wire << (probe % 3))) & ((1 << width) - 1)
               for wire in range(40)]


def compute():
    certificate = read_pinned("research/mutable-source-minimum-queries/CERTIFICATE.json")
    word = certificate["schedules"]["minimum_queries"]["word"]
    leaves = expand(word)
    need(len(leaves) == 488, "literal eight-factor leaf/X count")
    pairs = 0
    trace = hashlib.sha256()
    for width in (1, 2, 3):
        bank = matrix_bank(width)
        for initial in inputs(width):
            expected = wanted(initial, bank)
            direct = run_root(word, initial, bank)
            actual = run_leaves(leaves, initial, bank)
            need(direct == actual == expected, "concrete dirty forward mismatch")
            need(run_leaves(leaves[::-1], actual, bank) == initial, "concrete dirty inverse mismatch")
            trace.update(bytes([width] + actual))
            pairs += 1
    controls = []
    for label, tag in (("missing_source_uncompute", "X"),
                       ("missing_closing_query", "Q"),
                       ("missing_dirty_readout", "R")):
        damaged = list(word)
        at = max(i for i, event in enumerate(damaged) if event[0] == tag)
        del damaged[at]
        bad_leaves = expand(damaged)
        detected = any(run_leaves(bad_leaves, state, matrix_bank(width)) != wanted(state, matrix_bank(width))
                       for width in (1, 2, 3) for state in inputs(width))
        need(detected, "concrete mutation not detected: " + label)
        controls.append(label)
    damaged = list(leaves)
    first_q = next(i for i, event in enumerate(word) if event[0] == "Q")
    cleanup = len(expand(word[:first_q])) + len(expand([word[first_q]])) - 1
    need(damaged[cleanup][1] >= 37, "control is not a private uncompute leaf")
    del damaged[cleanup]
    need(any(run_leaves(damaged, state, matrix_bank(width)) != wanted(state, matrix_bank(width))
             for width in (1, 2, 3) for state in inputs(width)), "private uncompute mutation not detected")
    controls.append("missing_private_uncompute")
    # Multiplication order genuinely matters on a concrete bank, not just formally.
    order_witnesses = []
    for width in (2, 3):
        bank = matrix_bank(width)
        for value in range(1 << width):
            reverse = value
            for j in reversed(range(8)):
                reverse = act(bank[f"B{j}"], reverse)
            if reverse != common_b(value, bank):
                order_witnesses.append([width, value, common_b(value, bank), reverse])
    need(order_witnesses, "matrix banks do not detect factor order")
    controls.append("factor_order")
    return {"schema_version": 1, "widths": [1, 2, 3], "dirty_rows": 40,
            "map_leaves": 480, "source_XORs": 8, "forward_inverse_pairs": pairs,
            "direct_root_comparisons": pairs, "endpoint_digest": trace.hexdigest(),
            "semantic_controls": controls, "factor_order_counterexamples": order_witnesses}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    receipt = compute()
    path = PACKAGE / "DENSE.json"
    if args.write:
        path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    else:
        need(receipt == json.loads(path.read_text()), "DENSE.json mismatch")
    print(f"PASS_CONNECTIVITY_DENSE pairs={receipt['forward_inverse_pairs']} "
          f"controls={len(receipt['semantic_controls'])} dirty_rows=40")


if __name__ == "__main__":
    main()
