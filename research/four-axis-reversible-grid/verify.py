"""Finite certificate and independent endpoint checks. Writes only stdout.

Produced by Nick Petalas. Apache-2.0.
"""
import hashlib
import json
from itertools import product
from pathlib import Path
import struct
import sys

from construction import build_tables, need
from kernel import block

ROOT = Path(__file__).resolve().parent


def direct_walsh(values):
    return tuple(sum((-1) ** ((j & k).bit_count()) * values[k]
                     for k in range(16)) for j in range(16))


def representatives():
    result = {}
    for t in range(4):
        for bits in product((0, 1), repeat=4):
            value = [0] * 16
            value[0] = t - sum(bits)
            for j, bit in enumerate(bits):
                value[1 << j] = bit
            key = tuple(v % 4 for v in direct_walsh(value))
            need(key not in result, "Independent quotient representatives")
            result[key] = tuple(value)
    return result


def certify(tables):
    forward, backward = tables
    reps = representatives()
    need(set(forward) == set(backward) == set(reps), "Complete table keys")
    targets = set()
    maximum = 0
    for key, value in sorted(forward.items()):
        need(len(value) == 16 and all(type(v) is int for v in value), "Offset format")
        need(all((a + b) % 4 == 0 for a, b in zip(key, value)), "Offset residues")
        image = direct_walsh(value)
        need(all(v % 4 == 0 for v in image), "Integral inverse offset")
        target = tuple((v // 4) % 4 for v in image)
        need(target not in targets, "Distinct quotient targets")
        targets.add(target)
        inverse = tuple(-v // 4 for v in image)
        need(backward[target] == inverse, "Paired inverse offset")
        for offset in (value, inverse):
            norm = sum(v * v for v in offset)
            need(norm <= 64, "Uniform real squared error at most four")
            maximum = max(maximum, norm)
            real = sum((1, 0, -1, 0)[j.bit_count() % 4] * v
                       for j, v in enumerate(offset))
            imag = sum((0, -1, 0, 1)[j.bit_count() % 4] * v
                       for j, v in enumerate(offset))
            need(real == imag == 0, "Preserved complex sum")
    need(targets == set(reps), "Surjective quotient matching")
    need(forward[(0,) * 16] == backward[(0,) * 16] == (0,) * 16, "Zero fixed")
    need(maximum == 64, "Sharp real error attained")
    return reps


def ideal_numerator(values, inverse=False):
    """Four times C^tensor4 / (1+i)^4, directly from Hamming distance."""
    output = []
    phases = ((1, 0), (0, 1), (-1, 0), (0, -1))
    for r in range(16):
        real = imag = 0
        for s, (a, b) in enumerate(values):
            exponent = 4 - (r ^ s).bit_count()
            c, d = phases[(-exponent if inverse else exponent) % 4]
            real -= c * a - d * b
            imag -= d * a + c * b
        output.append((real, imag))
    return tuple(output)


def gaussian_sum(values):
    return sum(z[0] for z in values), sum(z[1] for z in values)


def endpoint_case(values, tables):
    original = tuple(values)
    worst = 0
    for inverse in (False, True):
        output = block(values, tables, inverse)
        need(block(output, tables, not inverse) == original, "Literal inverse")
        need(gaussian_sum(output) == gaussian_sum(values), "Endpoint sum")
        numerator = ideal_numerator(values, inverse)
        error = sum((4 * a - c) ** 2 + (4 * b - d) ** 2
                    for (a, b), (c, d) in zip(output, numerator))
        need(error <= 128, "Sharp Gaussian squared error at most eight")
        worst = max(worst, error)
    need(tuple(values) == original, "Input preservation")
    return worst


def endpoint_checks(reps, tables):
    cases = 0
    worst = 0
    for real in reps.values():
        for imag in reps.values():
            values = tuple(zip(real, imag))
            worst = max(worst, endpoint_case(values, tables))
            cases += 1
    for number in range(64):
        values = tuple((((j + 1) * (number + 3) << (number % 31)) - 17,
                        (j - 7) * (number + 1) * (-1) ** j) for j in range(16))
        worst = max(worst, endpoint_case(values, tables))
        cases += 1
    for bits in (128, 1024, 4090):
        values = tuple(((-1) ** j * ((1 << bits) + j),
                        (-1) ** (j // 2) * ((1 << bits) - j)) for j in range(16))
        worst = max(worst, endpoint_case(values, tables))
        cases += 1
    witness = ((2, 2),) + ((0, 0),) * 15
    need(all(a % 4 == b % 4 == 2 for a, b in ideal_numerator(witness)),
         "Every real component is half integral at the lower-bound witness")
    need(endpoint_case(witness, tables) == 128, "Sharp Gaussian error attained")
    return cases + 1, worst


def rejection_controls(tables):
    controls = []
    key = (0,) * 16
    missing = (dict(tables[0]), dict(tables[1]))
    del missing[0][key]
    controls.append(lambda: certify(missing))
    for coordinate, delta in ((0, 1), (0, 4), (3, 12)):
        changed = (dict(tables[0]), dict(tables[1]))
        value = list(changed[0][key])
        value[coordinate] += delta
        changed[0][key] = tuple(value)
        controls.append(lambda changed=changed: certify(changed))
    changed = (dict(tables[0]), dict(tables[1]))
    changed[1][key] = (4,) + (0,) * 15
    controls.append(lambda: certify(changed))
    for invalid in ((), ((0, 0),) * 15, ((0, 0, 0),) * 16,
                    ((True, 0),) * 16, ((1 << 4096, 0),) * 16):
        controls.append(lambda invalid=invalid: block(invalid, tables))
    for check in controls:
        try:
            check()
        except ValueError:
            continue
        raise ValueError("A malformed certificate or input was accepted")
    return len(controls)


def main():
    need(len(sys.argv) == 1, "No verifier arguments")
    tables = build_tables()
    reps = certify(tables)
    cases, worst = endpoint_checks(reps, tables)
    controls = rejection_controls(tables)
    payload = b"".join(struct.pack("16B32b", *key, *tables[0][key], *tables[1][key])
                       for key in sorted(reps))
    need(len(payload) == 3072, "Shared real table payload")
    receipt = {
        "status": "PASS_FOUR_AXIS_REVERSIBLE_GRID",
        "claim_type": "scoped written proof and finite construction certificate",
        "real_classes": len(reps), "gaussian_class_pairs": len(reps) ** 2,
        "table_payload_bytes": len(payload), "table_sha256": hashlib.sha256(payload).hexdigest(),
        "endpoint_fixtures": cases, "directions_per_fixture": 2,
        "maximum_squared_error_times_16": worst, "rejection_controls": controls,
        "files_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                         for p in sorted(ROOT.iterdir()) if p.is_file()},
    }
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
