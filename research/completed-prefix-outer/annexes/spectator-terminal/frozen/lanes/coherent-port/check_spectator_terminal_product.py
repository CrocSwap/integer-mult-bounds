#!/usr/bin/env python3
"""Check the exact spectator terminal product on the actual port labels."""

from fractions import Fraction as F
from pathlib import Path
import hashlib
import json


HERE = Path(__file__).resolve().parent
INTERFACE = HERE.parent / "circuit-interface" / "INTERFACE.json"
INTERFACE_SHA = "5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3"
CONTROLLER = HERE.parent / "encoded-controller" / "ORIGINAL-PAIRED-CONTROLLER.md"
CONTROLLER_SHA = "412f71ddff2294e1013033220d9eab809d37c14f1cbced36727e175c72f0d0a1"
ZERO, ONE = (F(0), F(0)), (F(1), F(0))


def need(condition, message):
    if not condition:
        raise RuntimeError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def mul(a, b):
    return (a[0] * b[0] - a[1] * b[1],
            a[0] * b[1] + a[1] * b[0])


def line(state, v, inverse=False):
    sign = -1 if inverse else 1
    coefficients = ((0, (F(1, 2), F(sign, 2))),
                    (v, (F(1, 2), F(-sign, 2))))
    out = {}
    for (x, z), value in state.items():
        for shift, coefficient in coefficients:
            key = (x ^ shift, z)
            out[key] = add(out.get(key, ZERO), mul(value, coefficient))
    return {key: value for key, value in out.items() if value != ZERO}


def involution(state, v):
    out = {}
    for (x, z), value in state.items():
        part = line({(x, z ^ 1): value}, v, inverse=(z == 0))
        for key, coefficient in part.items():
            out[key] = add(out.get(key, ZERO), coefficient)
    return {key: value for key, value in out.items() if value != ZERO}


def affine(state, total, negative, parity, inverse=False,
           omit_control=False, wrong_inverse_order=False):
    out = {}
    for (x, z), value in state.items():
        if inverse and not wrong_inverse_order:
            x ^= negative
            if z and not omit_control:
                x ^= total
            z ^= parity
        else:
            z ^= parity
            if z and not omit_control:
                x ^= total
            x ^= negative
        out[(x, z)] = value
    return out


def main():
    need(sha(INTERFACE) == INTERFACE_SHA, "Changed source interface")
    need(sha(CONTROLLER) == CONTROLLER_SHA, "Changed controller proof")
    source = json.loads(INTERFACE.read_bytes())
    ports = source["ports"]
    need(len(ports) == 112 and len(set(ports)) == 112,
         "Wrong actual port labels")
    need(all(q.bit_count() % 2 for q in ports), "Even actual port label")
    checked = entries = control_rejections = order_rejections = 0
    for q in ports:
        for m in range(1, 7):
            vectors = [q << (9 * j) for j in range(m)]
            total = negative = 0
            for j, v in enumerate(vectors):
                total ^= v
                if (m - 1 - j) % 2:
                    negative ^= v
            for z in (0, 1):
                initial = {(0, z): ONE}
                actual = initial
                for v in vectors:
                    actual = involution(actual, v)
                expected = affine(initial, total, negative, m % 2)
                for v in vectors:
                    expected = line(expected, v)
                need(actual == expected, "Whole-layer product mismatch")
                inverse = actual
                for v in vectors:
                    inverse = line(inverse, v, inverse=True)
                inverse = affine(inverse, total, negative, m % 2,
                                 inverse=True)
                need(inverse == initial, "Ordered inverse mismatch")
                omitted = affine(initial, total, negative, m % 2,
                                 omit_control=True)
                for v in vectors:
                    omitted = line(omitted, v)
                if z ^ (m % 2):
                    need(omitted != actual, "Control omission did not reject")
                    control_rejections += 1
                if m % 2:
                    wrong = actual
                    for v in vectors:
                        wrong = line(wrong, v, inverse=True)
                    wrong = affine(wrong, total, negative, m % 2,
                                   inverse=True, wrong_inverse_order=True)
                    need(wrong != initial, "Inverse order control did not reject")
                    order_rejections += 1
                checked += 1
                entries += len(actual)
    need(56 * 56 - 4 * 56 == 2912, "Wrong retained-controller witness")
    receipt = {
        "status": "PASS_SPECTATOR_TERMINAL_PRODUCT",
        "interface_sha256": sha(INTERFACE),
        "controller_proof_sha256": sha(CONTROLLER),
        "proof_sha256": sha(HERE / "SPECTATOR-TERMINAL-PRODUCT.md"),
        "checker_sha256": sha(Path(__file__)),
        "actual_ports": len(ports),
        "layer_counts": list(range(1, 7)),
        "spectator_columns_checked": checked,
        "nonzero_kernel_entries_checked": entries,
        "omitted_control_rejections": control_rejections,
        "wrong_odd_inverse_order_rejections": order_rejections,
        "inherited_controller_witness_coefficient": 2912,
        "scope": "Exact terminal operator product and controls. The inherited controller witness is proof-bound, not replayed here. Whole-layer content, native layout, cost, owner admission and full supplier improvement remain open."
    }
    (HERE / "SPECTATOR-TERMINAL-PRODUCT.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"])
    print(json.dumps({"columns": checked, "kernel entries": entries},
                     sort_keys=True))


if __name__ == "__main__":
    main()
