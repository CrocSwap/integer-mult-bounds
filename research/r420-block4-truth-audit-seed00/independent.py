"""Direct Boolean and positive-norm checks for a fixed XOR circuit."""

from hashlib import sha256
import json


def need(value, message):
    if not value:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def digest(raw):
    return sha256(raw).hexdigest()


def local_operations(events, wires, frame):
    lookup = {wire: index for index, wire in enumerate(wires)}
    need(len(lookup) == len(wires), "unique physical input wires")
    result = []
    for event in events:
        need(len(event) == 3 and event[0] == frame and len(event[2]) == 1,
             "single-source XOR gate at the pinned frame")
        target, source = event[1], event[2][0]
        need(target in lookup and source in lookup and target != source,
             "gate endpoints lie on distinct local wires")
        result.append((lookup[target], lookup[source]))
    return result


def linear_rows(operations, n):
    rows = [1 << index for index in range(n)]
    for target, source in operations:
        rows[target] ^= rows[source]
    return rows


def positive_cost(operations, n):
    """Peak nonnegative integer weight over the forward word and its reverse."""
    weights = [1] * n
    peak = max(weights)
    for target, source in list(operations) + list(reversed(operations)):
        weights[target] += weights[source]
        peak = max(peak, weights[target])
    return peak


def truth_table(operations, output_to_wire, target_rows, n):
    """Exhaust every Boolean input; return the first counterexample if any."""
    for input_bits in range(1 << n):
        values = [(input_bits >> index) & 1 for index in range(n)]
        for target, source in operations:
            values[target] ^= values[source]
        for output, row in enumerate(target_rows):
            expected = (row & input_bits).bit_count() & 1
            actual = values[output_to_wire[output]]
            if actual != expected:
                return {"checked_inputs": input_bits + 1, "first_mismatch": {
                    "input": input_bits, "output": output,
                    "expected": expected, "actual": actual}}
    return {"checked_inputs": 1 << n, "first_mismatch": None}
