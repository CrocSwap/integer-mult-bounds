#!/usr/bin/env python3
"""Separate sparse-set replay on every ADDRESS in (Z/3)^6.

Apache-2.0; substantial OpenAI Codex assistance. No code is imported from
check.py. This finite linear-operator check is not a full theorem proof.
"""

from fractions import Fraction
from itertools import product
import json
from pathlib import Path


def check_full_domain(packet):
    modulus = 3
    addresses = list(product(range(modulus), repeat=6))

    def scalar(text):
        x = Fraction(text)
        return x.numerator * pow(x.denominator, -1, modulus) % modulus

    def move(address):
        value = list(address)
        for operation in packet["address_forward"]:
            if operation["op"] == "child":
                i, j = operation["fields"]
                value[i], value[j] = value[j], value[i]
            elif operation["op"] == "affine":
                i = operation["dst"]
                value[i] = (scalar(operation["diagonal"]) * value[i]
                            + sum(scalar(c) * value[j] for j, c in operation["terms"])) % modulus
            else:
                raise ValueError("unknown ADDRESS operation")
        return tuple(value)

    # A separate closed formula, in coordinates rather than matrix helpers.
    def closed(address):
        a, b, c, d, e, f = address
        delta = (a - c - d + f) * pow(4, -1, modulus)
        return ((a + delta) % modulus, b, (c + delta) % modulus,
                (d - delta) % modulus, e, (f - delta) % modulus)

    forward = {address: move(address) for address in addresses}
    if set(forward.values()) != set(addresses):
        raise ValueError("full-domain ADDRESS map is not bijective")
    if any(forward[a] != closed(a) for a in addresses):
        raise ValueError("full-domain ADDRESS map disagrees with closed formula")
    backward = {value: key for key, value in forward.items()}

    def execute(program, state):
        rows = [set(s) for s in state]
        for operation in program:
            name = operation["op"]
            if name == "xor":
                rows[operation["dst"]].symmetric_difference_update(rows[operation["src"]])
            elif name == "copy":
                rows[operation["dst"]] = set(rows[operation["src"]])
            elif name == "clear":
                rows[operation["row"]] = set()
            elif name == "query":
                mapping = forward if operation["direction"] == 1 else backward
                row = operation["row"]
                rows[row] = {mapping[a] for a in rows[row]}
            else:
                raise ValueError("unknown BIT operation")
        return rows

    counts = {}
    for name, program in packet["programs"].items():
        checked = 0
        for row, address in product(range(4), addresses):
            state = [set() for _ in range(4)]
            state[row].add(address)
            expected = [set(s) for s in state]
            if row == 1:
                expected[0].symmetric_difference_update({address})
                expected[0].symmetric_difference_update({closed(address)})
            if name == "clean_private":
                expected[3] = set()
            actual = execute(program, state)
            if actual != expected:
                raise ValueError(f"full-domain endpoint: {name}, input row {row}, address {address}")
            restored = [set(s) for s in state]
            if name == "clean_private":
                restored[3] = set()
            if execute(program, actual) != restored:
                raise ValueError(f"full-domain completed inverse: {name}")
            checked += 1
        counts[name] = checked
    return {
        "modulus": modulus, "full_address_count": len(addresses),
        "fixed_addresses": sum(a == b for a, b in forward.items()),
        "input_basis_columns_per_program": counts,
        "endpoint_and_completed_inverse_cases": 2 * sum(counts.values()),
        "method": "individual sparse-set BIT columns on the complete six-field address domain",
    }


if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    result = check_full_domain(json.loads((root / "PROGRAM.json").read_text()))
    print(json.dumps(result, indent=2, sort_keys=True))
