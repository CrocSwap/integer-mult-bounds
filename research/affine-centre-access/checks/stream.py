#!/usr/bin/env python3
"""Check the signed average code on complete finite packed arrays."""

import hashlib
import json
from fractions import Fraction as F
from pathlib import Path


PACKAGE = Path(__file__).resolve().parents[1]
HERE = Path.cwd()
LANES = PACKAGE / 'evidence/lanes'
PHYS = LANES / 'residual-syndrome/physical-algebra'
BASE = "bce54fb3f895cbe5cd4c0eb477c3afeed100190f"
SOURCE_FILES = ["upstream/build/sections/02-streams.tex",
                "notes/compact-control-movement.tex",
                "notes/compact-control-layout.tex",
                "notes/batched-complex-rows.tex"]


def require(value, name):
    if not value:
        raise ValueError(name)


def inserted(value, bit, digit):
    mask = (1 << bit) - 1
    return (value & mask) | ((value & ~mask) << 1) | (digit << bit)


def selected_pairs(n, width, chunk, rho):
    half = width // 2
    return [((n * width - 1 - (i * width + j)) * chunk + rho,
             (n * width - 1 - (i * width + j + half)) * chunk + rho)
            for i in range(n) for j in range(half)]


def change_basis(values, pairs, polynomial):
    out = [F(0)] * len(values)
    for address in range(len(values) // polynomial):
        changed = address
        for left, right in pairs:
            if (address >> right) & 1:
                changed ^= 1 << left
        for j in range(polynomial):
            out[changed * polynomial + j] = values[address * polynomial + j]
    return out


def encode(values, bits, polynomial, trace):
    active = list(values)
    stack = []
    for bit in sorted(bits, reverse=True):
        addresses = len(active) // polynomial
        zero = []
        one = []
        for address in range(addresses):
            target = one if (address >> bit) & 1 else zero
            target.extend(active[address * polynomial:(address + 1) * polynomial])
        require(len(zero) == len(one), "complete split")
        first = []
        detail = []
        for u, v in zip(zero, one):
            trace.extend((u-v, u+v))
            first.append((u-v)/2)
            detail.append((u+v)/2)
        stack.append((bit, detail))
        active = first
    return active, stack


def decode(active, stack, polynomial, trace):
    for bit, detail in reversed(stack):
        require(len(active) == len(detail), "detail shape")
        out = [F(0)] * (2 * len(active))
        for address in range(len(active) // polynomial):
            for j in range(polynomial):
                a = active[address * polynomial + j]
                d = detail[address * polynomial + j]
                u, v = a+d, d-a
                trace.extend((u, v))
                out[inserted(address, bit, 0) * polynomial + j] = u
                out[inserted(address, bit, 1) * polynomial + j] = v
        active = out
    return active


def shear(x, y, pairs, polynomial, sign=1):
    trace = []
    bits = [right for _, right in pairs]
    px = change_basis(x, pairs, polynomial)
    py = change_basis(y, pairs, polynomial)
    a, source_details = encode(px, bits, polynomial, trace)
    b, target_details = encode(py, bits, polynomial, trace)
    b = [v + sign*u for u, v in zip(a, b)]
    trace.extend(b)
    decoded_target = decode(b, target_details, polynomial, trace)
    decoded_source = decode(a, source_details, polynomial, trace)
    target_details.clear()
    source_details.clear()
    require(not target_details and not source_details, "detail cleanup")
    result = (change_basis(decoded_source, pairs, polynomial),
              change_basis(decoded_target, pairs, polynomial))
    return result, trace


def direct_projector(values, pairs, polynomial):
    result = [F(0)] * len(values)
    shifts = [(0, 1)]
    for left, right in pairs:
        h = (1 << left) | (1 << right)
        shifts += [(v ^ h, -s) for v, s in shifts]
    for address in range(len(values) // polynomial):
        for shift, sign in shifts:
            for j in range(polynomial):
                result[address * polynomial + j] += (
                    sign * values[(address ^ shift) * polynomial + j] / len(shifts))
    return result


def check_case(n, width, chunk, rho, spectator_bits, polynomial):
    pairs = selected_pairs(n, width, chunk, rho)
    addresses = 1 << (n * width * chunk + spectator_bits)
    length = addresses * polynomial
    for column in range(2 * length):
        x = [F(int(j == column)) for j in range(length)]
        y = [F(int(j + length == column)) for j in range(length)]
        (xx, yy), _ = shear(x, y, pairs, polynomial)
        require(xx == x, "all-input source restoration")
        projected = direct_projector(x, pairs, polynomial)
        require(yy == [a+b for a, b in zip(y, projected)], "all-input target map")
    x = [F((17*j+3) % 19 - 9, 8) for j in range(length)]
    y = [F((11*j+5) % 23 - 11, 8) for j in range(length)]
    (xx, yy), trace = shear(x, y, pairs, polynomial)
    (back_x, back_y), _ = shear(xx, yy, pairs, polynomial, -1)
    require(back_x == x and back_y == y, "inverse shear")
    maximum = max(map(abs, x+y))
    require(max(map(abs, trace), default=F(0)) <= 2*maximum, "one magnitude bit")
    grid = 1 << (3 + len(pairs))
    require(all((v*grid).denominator == 1 for v in trace+xx+yy), "fractional guard")
    for _ in range(4):
        (y, x), _ = shear(y, x, pairs, polynomial)
        (x, y), _ = shear(x, y, pairs, polynomial, -1)
        (y, x), _ = shear(y, x, pairs, polynomial)
    require(x == back_x and y == back_y, "projected quarter turn")
    # The source and target use all polynomial and spectator coordinates.
    return {"n": n, "tensor_width": width, "chunk_bits": chunk,
            "selected_offset": rho, "spectator_bits": spectator_bits,
            "polynomial_coefficients": polynomial,
            "complete_input_columns": 2*length, "projector_codimension": len(pairs),
            "additional_fractional_bits": len(pairs),
            "maximum_magnitude_ratio": str(max(map(abs, trace))/maximum)}


def frame_check(n, half):
    width = 2*half
    support = []
    omega = (1 << n)-1
    for address in range(1 << (n*width)):
        columns = [sum(((address >> (i*width+j)) & 1) << i for i in range(n))
                   for j in range(width)]
        if all(columns[j] ^ columns[j+half] == omega for j in range(half)):
            support.append(columns)
    require(len(support) == 1 << (n*half), "affine support rank")
    line_checks = translation_checks = 0
    for columns in support:
        for q in range(1, 1 << n):
            if q.bit_count() % 2:
                require(sum((q & x).bit_count() % 2 for x in columns) % 4 == half % 4,
                        "all odd line phases")
                line_checks += 1
        for delta in range(1 << n):
            require(sum((delta & x).bit_count() % 2 for x in columns) % 2
                    == (half * delta.bit_count()) % 2, "tensor translation phase")
            translation_checks += 1
    return {"n": n, "half_width": half, "range_dimension": len(support),
            "line_equalities": line_checks, "translation_equalities": translation_checks}


def main():
    source_pins = {}
    repo = PACKAGE / "sources/upstream"
    for name in SOURCE_FILES:
        content = (repo / name).read_bytes()
        source_pins[name] = hashlib.sha256(content).hexdigest()
    cases = [check_case(*case) for case in
             ((2,2,1,0,1,2), (2,2,2,0,0,1), (2,2,2,1,0,1),
              (2,4,1,0,0,1), (3,2,1,0,0,2))]
    phases = [frame_check(n, half) for n, half in ((2,1),(2,2),(3,1),(3,2))]
    receipt = {"status": "PASS_SIGNED_PROJECTOR_STREAM",
               "source_base": BASE, "source_files": source_pins,
               "cases": cases, "completed_frame_checks": phases,
               "scope": "Exact full finite maps and guards. The general fixed-tape cost and owner interface are proved in STREAM.md. No supplier or controller claim."}
    (HERE / "STREAM.json").write_text(json.dumps(receipt, indent=2, sort_keys=True)+"\n")
    print(receipt["status"])


if __name__ == "__main__":
    main()
