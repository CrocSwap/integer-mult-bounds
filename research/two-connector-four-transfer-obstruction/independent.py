"""Separate matching, interval and literal dirty-column checks. Apache-2.0."""
from itertools import combinations


def matchings(n):
    def fill(slots, label):
        empty = [i for i, x in enumerate(slots) if x == -1]
        if not empty:
            yield tuple(slots)
            return
        first = empty[0]
        for second in empty[1:]:
            new = list(slots)
            new[first] = new[second] = label
            yield from fill(new, label + 1)
    yield from fill([-1] * (2 * n), 0)


def interval_masks(labels):
    """Every contiguous subword, without constructing prefix vertices."""
    result = {0}
    for first in range(len(labels)):
        counts = set()
        for last in range(first, len(labels)):
            label = labels[last]
            if label in counts:
                counts.remove(label)
            else:
                counts.add(label)
            result.add(sum(2 ** j for j in counts))
    return result


def histories(labels, ports, c_positions):
    """Literal root operations, with two independent incoming-dirt bits."""
    z = [1, 2]
    history = [tuple(z)]
    b = 0
    for pos in range(len(labels) + len(c_positions)):
        if pos in c_positions:
            z[0] ^= z[1]
        else:
            j = labels[b]
            z[(ports >> j) & 1] ^= 1 << (j + 2)
            b += 1
        history.append(tuple(z))
    return history


def masks(history):
    values = [v for state in history for v in state]
    return {(a ^ b) >> 2 for a in values for b in values
            if ((a ^ b) & 3) == 0}


def four_phase_masks(u):
    """Read pairs directly from a literal transfer history with prescribed z1."""
    z0 = 1
    rows = [z0]
    for source in u:
        z0 ^= 2 | (source << 2)
        rows.append(z0)
    return {(a ^ b) >> 2 for a in rows for b in rows
            if ((a ^ b) & 3) == 0}


def small_census(n):
    from collections import Counter
    histogram = Counter()
    candidates = restored = 0
    for word in matchings(n):
        for ports in range(1 << n):
            for positions in combinations(range(2 * n + 4), 4):
                candidates += 1
                h = histories(word, ports, positions)
                if h[-1] != (1, 2):
                    continue
                restored += 1
                histogram[len(masks(h))] += 1
    return {"candidates": candidates, "restored": restored,
            "coverage_histogram": {str(k): v for k, v in sorted(histogram.items())}}


def dense_replay(n, targets, operations, width, bank):
    """Bit-packed dense columns, independent of the formal-polynomial engine."""
    count = n + len(targets) + 2
    def matrix(label):
        kind, j = label
        code = (j + 1) * (7 if kind == "A" else 13) + 17 * bank
        # SHA256 supplies deterministic dense bits, not probabilistic evidence.
        from hashlib import sha256
        raw = sha256(f"{kind}:{code}:{width}".encode()).digest()
        return [sum(((raw[(r * width + c) // 8] >>
                      ((r * width + c) % 8)) & 1) << c
                    for c in range(width)) for r in range(width)]
    matrices = {(kind, j): matrix((kind, j))
                for kind, size in (("A", len(targets)), ("B", n))
                for j in range(size)}
    def apply(rows, value):
        return sum(((row & value).bit_count() & 1) << i
                   for i, row in enumerate(rows))
    def replay(state, ops):
        state = list(state)
        for op in ops:
            if op[0] == "C":
                state[-2] ^= state[-1]
            elif op[0] == "B":
                state[-2 + op[2]] ^= apply(matrices[("B", op[1])], state[op[1]])
            else:
                state[n + op[1]] ^= apply(matrices[("A", op[1])], state[-2 + op[2]])
        return state
    checked = 0
    for column in range(count * width):
        initial = [0] * count
        initial[column // width] = 1 << (column % width)
        expected = list(initial)
        for i, mask in enumerate(targets):
            for j in range(n):
                if (mask >> j) & 1:
                    expected[n + i] ^= apply(matrices[("A", i)],
                                             apply(matrices[("B", j)], initial[j]))
        actual = replay(initial, operations)
        if actual != expected or replay(actual, reversed(operations)) != initial:
            raise ValueError("dense dirty-column forward/inverse failure")
        checked += 1
    noncommuting = sum(apply(matrices[("A", 0)], apply(matrices[("B", 0)], 1 << j)) !=
                      apply(matrices[("B", 0)], apply(matrices[("A", 0)], 1 << j))
                      for j in range(width))
    return checked, noncommuting


def transfer_backend(width, b0, b1, bits):
    """One-head scalar-bit realization; one admitted clean scalar scratch bit.

    Each head step and each cell/register XOR is one primitive instruction.
    The tape includes arbitrary root dirt; source row z1 is read-only.
    """
    tape = list(bits)
    scratch = head = xors = steps = 0
    for k in range(width):
        for address, action in ((b1 + k, "load"), (b0 + k, "update"),
                                (b1 + k, "unload"), (0, "return")):
            steps += abs(address - head)
            head = address
            if action in ("load", "unload"):
                scratch ^= tape[head]
                xors += 1
            elif action == "update":
                tape[head] ^= scratch
                xors += 1
    if scratch != 0 or head != 0:
        raise ValueError("transfer private-bit/head restoration")
    return tape, {"cell_register_xors": xors, "head_steps": steps,
                  "primitive_dispatches": xors + steps,
                  "admitted_clean_scalar_bits": 1, "extra_dirty_row_bits": width}
