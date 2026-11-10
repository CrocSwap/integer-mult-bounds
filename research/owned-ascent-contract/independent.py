#!/usr/bin/env python3
"""Exact dense Gaussian-integer check without the source compiler/interpreter.

For every owned rise, compare all 512 columns of the explicit frame quotient
to its serialized two-monomial/positive-child factorization. All arithmetic
uses Python integers with a common power-of-two denominator. No floating
point, modular evaluation, tableaux or primary scientific code is used.
"""
from __future__ import annotations

from array import array
from hashlib import sha256
from pathlib import Path
import gzip
import json
import random
import sys

HERE = Path(__file__).resolve().parent
SIZE = 512


def need(condition, message):
    if not condition:
        raise ValueError(message)


def parity(value):
    return value.bit_count() & 1


def phase_at(quadratic, linear, address):
    result = sum(value for bit, value in enumerate(linear) if (address >> bit) & 1)
    for i in range(9):
        if (address >> i) & 1:
            for j in range(i + 1, 9):
                if (address >> j) & 1 and (quadratic[i] >> j) & 1:
                    result += 2
    return result % 4


def rotate(real, imaginary, phase):
    phase %= 4
    if phase == 0:
        return real, imaginary
    if phase == 1:
        return [-x for x in imaginary], real
    if phase == 2:
        return [-x for x in real], [-x for x in imaginary]
    return imaginary, [-x for x in real]


def phase_rows(data, phases):
    real, imaginary = data
    out_real, out_imaginary = [], []
    for a, b, phase in zip(real, imaginary, phases):
        c, d = rotate(a, b, phase)
        out_real.append(c); out_imaginary.append(d)
    return out_real, out_imaginary


def permute_rows(data, forward):
    real, imaginary = data
    out_real = [None] * len(forward)
    out_imaginary = [None] * len(forward)
    need(len(set(forward)) == len(forward), "address permutation is invertible")
    for source, target in enumerate(forward):
        out_real[target] = real[source]
        out_imaginary[target] = imaginary[source]
    return out_real, out_imaginary


def gaussian(data, direction, sign):
    """Integer numerator of one C gate; caller increments denominator by one."""
    real, imaginary = data
    out_real, out_imaginary = [], []
    for x, (a, b) in enumerate(zip(real, imaginary)):
        c, d = real[x ^ direction], imaginary[x ^ direction]
        out_real.append([u - sign*v + r + sign*t for u, v, r, t in zip(a, b, c, d)])
        out_imaginary.append([v + sign*u + t - sign*r for u, v, r, t in zip(a, b, c, d)])
    return out_real, out_imaginary


def frame_data(basis):
    """Direct exact frame formula; span membership replaces binary elimination."""
    rank = len(basis)
    if rank in (0, 9):
        return rank, list(range(SIZE)), list(range(SIZE)), [0] * SIZE
    columns = []
    span = {0}
    for vector in list(basis) + [1 << bit for bit in range(9)]:
        if vector not in span:
            columns.append(vector)
            span |= {x ^ vector for x in span}
    need(len(columns) == 9, "complete frame basis extension")
    forward = [0] * SIZE
    for x in range(SIZE):
        for bit in range(9):
            if (x >> bit) & 1:
                forward[x] ^= columns[bit]
    backward = [0] * SIZE
    for x, y in enumerate(forward):
        backward[y] = x
    inverse_columns = [backward[1 << bit] for bit in range(9)]
    quadratic = [sum(((i == j) ^ bool(parity(a & b))) << j for j, b in enumerate(inverse_columns))
                 for i, a in enumerate(inverse_columns)]
    linear = [(row >> i) & 1 for i, row in enumerate(quadratic)]
    phases = [phase_at(quadratic, linear, x) for x in range(SIZE)]
    return rank, forward, backward, phases


def apply_frame(data, description, sign):
    rank, forward, backward, phases = description
    data = phase_rows(data, [(-phase) % 4 for phase in phases])
    data = permute_rows(data, backward)
    for axis in range(rank):
        data = gaussian(data, 1 << axis, sign)
    data = permute_rows(data, forward)
    return phase_rows(data, phases), rank


def monomial_maps(monomial):
    forward = [sum(parity(row & x) << bit for bit, row in enumerate(monomial["matrix_rows"])) ^ monomial["offset"]
               for x in range(SIZE)]
    phases = [(monomial["phase"] + phase_at(monomial["quadratic_rows"], monomial["linear_Z4"], x)) % 4
              for x in range(SIZE)]
    return forward, phases


def apply_monomial(data, monomial):
    forward, phases = monomial_maps(monomial)
    return permute_rows(phase_rows(data, phases), forward)


def record_action(records, address, width, wrong_global_phase=False):
    result, phase = address, 0
    for record in records:
        kind = record[0]
        if kind == "I":
            phase += 1 if wrong_global_phase else width
            continue
        for column in range(width):
            offset = 9 * column
            i = record[1] + offset
            if kind == "NOT":
                result ^= 1 << i
            elif kind == "XROW":
                result ^= ((result >> (record[2] + offset)) & 1) << i
            elif kind == "S":
                phase += (result >> i) & 1
            elif kind == "CZ":
                phase += 2 * ((result >> i) & 1) * ((result >> (record[2] + offset)) & 1)
            else:
                raise ValueError("unknown record type")
    return result, phase % 4


def run():
    word = json.load(gzip.open(HERE / "retained/native-word.json.gz", "rt"))
    recipes = json.loads((HERE / "RECIPES.json").read_text())
    identity = ([[int(row == column) for column in range(SIZE)] for row in range(SIZE)],
                [[0] * SIZE for _ in range(SIZE)])
    frames = {}
    digest = sha256()
    columns = coefficients = record_cases = 0
    rng = random.Random(676902)
    maximum_denominator_bits = 0
    controls = {}
    for recipe in recipes:
        event = word["program"][recipe["event"]]
        need(event == ["MOVE", recipe["role"], recipe["start"], recipe["end"], True], "literal rise binding")
        for frame in (recipe["start"], recipe["end"]):
            if frame not in frames:
                frames[frame] = frame_data(word["frames"][frame])
        source, first_den = apply_frame(identity, frames[recipe["start"]], -1)
        source, second_den = apply_frame(source, frames[recipe["end"]], 1)
        source_den = first_den + second_den
        before_left = apply_monomial(identity, recipe["right"])
        for axis in range(recipe["rank"]):
            before_left = gaussian(before_left, 1 << axis, 1)
        actual = apply_monomial(before_left, recipe["left"])
        actual_den = recipe["rank"]
        need(source_den >= actual_den, "nested denominator comparison")
        scale = 1 << (source_den - actual_den)
        for reference_component, actual_component in zip(source, actual):
            for reference_row, actual_row in zip(reference_component, actual_component):
                need(reference_row == [scale * value for value in actual_row], "all exact Gaussian columns match")
                encoded = array("i", actual_row)
                need(encoded.itemsize == 4, "canonical 32-bit digest representation")
                if sys.byteorder != "little":
                    encoded.byteswap()
                digest.update(encoded.tobytes())
        columns += SIZE
        coefficients += SIZE * SIZE
        maximum_denominator_bits = max(maximum_denominator_bits, source_den)
        if not controls:
            wrong_left = dict(recipe["left"], phase=(recipe["left"]["phase"] + 2) % 4)
            controls["global_phase"] = apply_monomial(before_left, wrong_left) != actual
            wrong = apply_monomial(identity, recipe["right"])
            for axis in range(recipe["rank"]):
                wrong = gaussian(wrong, 1 << axis, -1)
            controls["child_adjoint_confusion"] = apply_monomial(wrong, recipe["left"]) != actual
            del wrong
        for side in ("left", "right"):
            monomial, records = recipe[side], recipe[side + "_records"]
            forward, phases = monomial_maps(monomial)
            for width, addresses in ((1, range(SIZE)), (2, [rng.randrange(1 << 18) for _ in range(64)]),
                                     (3, [rng.randrange(1 << 27) for _ in range(64)])):
                for address in addresses:
                    spectator = rng.randrange(1 << 11) << (9 * width)
                    value = address | spectator
                    wanted = spectator
                    wanted_phase = 0
                    for column in range(width):
                        x = (address >> (9 * column)) & 511
                        wanted |= forward[x] << (9 * column)
                        wanted_phase += phases[x]
                    need(record_action(records, value, width) == (wanted, wanted_phase % 4), "exact repeated record and tensor absolute phase")
                    if record_action(records, value, width, wrong_global_phase=True) != (wanted, wanted_phase % 4):
                        controls["missing_tensor_global_phase"] = True
                    record_cases += 1
        del source, actual, before_left
    need(len(controls) == 3 and all(controls.values()), "all global-phase/adjoint controls distinguish")
    result = dict(complete_rise_operators=len(recipes), exact_basis_columns=columns,
                  exact_complex_matrix_entries=coefficients, exact_record_addresses=record_cases,
                  largest_unreduced_denominator_bits=maximum_denominator_bits,
                  matrix_sha256=digest.hexdigest(), controls=controls)
    expected = HERE / "RESULT.json"
    if expected.exists():
        saved = json.loads(expected.read_text()).get("independent")
        if saved is not None:
            need(result == saved, "complete frozen independent result")
    print(json.dumps(result, sort_keys=True))
    print("PASS_INDEPENDENT_OWNED_ASCENT")
    return result


if __name__ == "__main__":
    try:
        run()
    except Exception as error:
        print("FAIL_INDEPENDENT_OWNED_ASCENT:", error, file=sys.stderr)
        raise SystemExit(1) from error
