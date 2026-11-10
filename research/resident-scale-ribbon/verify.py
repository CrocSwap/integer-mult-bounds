#!/usr/bin/env python3
"""Finite exact corroboration for the resident SCALE circuit and traffic proof."""

import argparse
import gzip
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path

from ribbon import (Tape, compile_route, doubling_gates, execute,
                    normalized_baseline, require)

HERE = Path(__file__).resolve().parent
PACKAGE_FILES = ("README.md", "PROOF.md", "ENGINEERING.md", "NOTICE", "TASK.json",
                 "VERIFY.json", "SOURCES.json", "ORIGINS.json", "ribbon.py", "verify.py",
                 "inputs/cache.py", "inputs/CIRCUITS64.json.gz",
                 "inputs/CERTIFICATES.json.gz", "inputs/PR6530-PROOF.md",
                 "inputs/PR6530-NOTICE")


def sources():
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    for row in manifest["files"]:
        if row["usage"] == "input":
            raw = (HERE.parent.parent / row["path"]).read_bytes()
            require(hashlib.sha256(raw).hexdigest() == row["sha256"], "selected word pin")
            word = json.loads(gzip.decompress(raw))["program"]
            require(word[10481:10484] == [["ADD", 256, 257, "-1/2", 306],
                                         ["SCALE", 257, "2", 306],
                                         ["ADD", 257, 256, "3/2", 306]],
                    "selected resident window")
    origins = json.loads((HERE / "ORIGINS.json").read_text())
    require(len(origins["files"]) == 5, "source inventory")
    for row in origins["files"]:
        raw = (HERE / "inputs" / row["path"]).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == row["sha256"], "source hash")
        blob = b"blob " + str(len(raw)).encode() + b"\0" + raw
        require(hashlib.sha1(blob).hexdigest() == row["git_blob"], "source blob")
    gates = json.loads(gzip.decompress((HERE / "inputs/CIRCUITS64.json.gz").read_bytes()))
    certs = json.loads(gzip.decompress((HERE / "inputs/CERTIFICATES.json.gz").read_bytes()))
    selected = [i for i, row in enumerate(gates) if row[:2] == ["SCALE", "2"]]
    require(len(selected) == 1, "unique source circuit")
    index = selected[0]
    spec = importlib.util.spec_from_file_location("retained_cache", HERE / "inputs/cache.py")
    cache = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cache)
    route = cache.compile_route(64, gates[index][2], certs[index])
    require(certs[index]["total"] == 9840, "source local tariff")
    return tuple(route), gates[index][2]


def bits(value, width):
    return [(value >> bit) & 1 for bit in range(width)]


def signed(records, width):
    result = []
    for offset in range(0, len(records), width):
        value = sum(records[offset + bit] << bit for bit in range(width))
        result.append(value - (1 << width) if value >> (width - 1) else value)
    return result


def gate_oracle(gates, payload):
    answer = payload.copy()
    for gate in gates:
        answer[gate[-1]] ^= int(all(answer[wire] for wire in gate[:-1]))
    return answer


def basis_checks(source_route, gates):
    candidate = compile_route(64, 1)
    for column in range(129):
        payload = [int(column == bit) for bit in range(129)]
        old = [Tape(payload[:64]), Tape(payload[64:128]), Tape(payload[128:])]
        execute(source_route, old)
        new = Tape(payload[:128])
        execute(candidate, [new])
        require(new.bits + payload[128:] == gate_oracle(gates, payload), "new basis map")
        require([b for tape in old for b in tape.bits] == new.bits + payload[128:],
                "retained source map")
        require(all(t.head == 0 for t in old) and new.head == 0, "basis heads")
    return 129


def arithmetic_checks():
    count = 0
    for width in range(2, 7):
        bound = 1 << (width - 2)
        route = compile_route(width, 1)
        inverse = compile_route(width, 1, inverse=True)
        for real, imag in itertools.product(range(-bound, bound), repeat=2):
            payload = bits(real, width) + bits(imag, width)
            tape = Tape(payload)
            execute(route, [tape])
            require(signed(tape.bits, width) == [2 * real, 2 * imag], "signed doubling")
            execute(inverse, [tape])
            require(tape.bits == payload and tape.head == 0, "signed inverse")
            count += 1
    return count


def general_checks():
    count = 0
    for width in range(2, 65):
        for dimension in (1, 2, 3, 4):
            payload = [int((bit * 7 + bit // 3) % 11 < 5)
                       for bit in range(2 * dimension * width)]
            tape = Tape(payload)
            execute(compile_route(width, dimension), [tape])
            require(tape.traffic() == (dimension * (18 * width - 12),
                                      dimension * (6 * width - 4),
                                      28 * dimension * (width - 1) - 2),
                    "exact general traffic")
            execute(compile_route(width, dimension, inverse=True), [tape])
            require(tape.bits == payload and tape.head == 0, "arbitrary-bit inverse")
            count += 1
    return count


def baseline_formula(evictions, acquisitions):
    """Each affine pair represents A*D+B, with width fixed at 64."""
    fields, head, a, b = (256, 257), 256, 0, 0
    for bank in evictions:
        delta = fields[bank] - head - 1
        a += 128 * abs(delta) + 1152
        b += (1 if delta >= 0 else -1) - 3
        head = fields[bank]
    delta = 257 - head - 1
    a += 128 * abs(delta) + 2688 + 9840
    b += (1 if delta >= 0 else -1) - 267
    head = 257
    for bank in acquisitions:
        delta = fields[bank] - head - 1
        a += 128 * abs(delta) + 1152
        b += (1 if delta >= 0 else -1) - 3
        head = fields[bank]
    a += 128 * abs(head - 256)
    return a, b


def fixture(dimension, variant):
    length = 128 * dimension
    values = [(13 * j - 17 + variant, 29 * j + 11 - variant)
              for j in range(dimension)]
    target = [b for pair in values for v in pair for b in bits(v, 64)]
    other = [int((j * 7 + variant) % 13 < 6) for j in range(length)]
    owner_bits = [int((j * 3 + variant) % 17 < 8) for j in range(258 * length)]
    owner_bits[256 * length:258 * length] = [0] * (2 * length)
    return owner_bits, other, target, values


def physical_checks(source_route):
    rows = []
    for evictions, acquisitions in itertools.product(((0, 1), (1, 0)), repeat=2):
        a, b = baseline_formula(evictions, acquisitions)
        for dimension, variant in itertools.product((1, 2, 3), (0, 1)):
            owner_bits, other, target, values = fixture(dimension, variant)
            head = 257 * 128 * dimension - 1
            owner = Tape(owner_bits, head)
            ribbons, carry = [Tape(other), Tape(target)], Tape([0])
            normalized_baseline(owner, ribbons, carry, (256, 257), 257, 64,
                                dimension, source_route, evictions, acquisitions)
            total = sum(sum(t.traffic()) for t in [owner, *ribbons, carry])
            require(total == a * dimension + b, "complete baseline affine bill")
            expected = [2 * v for pair in values for v in pair]
            require(signed(ribbons[1].bits, 64) == expected, "complete baseline output")
            require(owner.bits == owner_bits and ribbons[0].bits == other and
                    carry.bits == [0] and owner.head == head and
                    all(t.head == 0 for t in [*ribbons, carry]), "complete baseline state")
            new_owner, new_other = Tape(owner_bits, head), Tape(other)
            candidate = Tape(target)
            execute(compile_route(64, dimension), [candidate])
            require(candidate.bits == ribbons[1].bits and candidate.head == 0,
                    "normalized endpoint equality")
            require(new_owner.bits == owner_bits and new_other.bits == other and
                    new_owner.traffic() == new_other.traffic() == (0, 0, 0),
                    "spectator preservation")
            rows.append({"dimension": dimension, "variant": variant,
                         "evictions": evictions, "acquisitions": acquisitions,
                         "baseline": total, "candidate": sum(candidate.traffic())})
    return rows


def controls():
    trials = [lambda: compile_route(1, 1), lambda: compile_route(65, 1),
              lambda: compile_route(64, 0), lambda: compile_route(64, 65),
              lambda: execute((("bad", 0, 0),), [Tape([0])]),
              lambda: execute((("xor", 0, 0),), [Tape([1])]),
              lambda: execute((("move", 0, -1),), [Tape([0])])]
    for trial in trials:
        try:
            trial()
        except ValueError:
            continue
        raise ValueError("negative control accepted")
    # The negative boundary distinguishes the final sign-clearing CNOT.
    width, payload = 4, bits(-4, 4) + bits(0, 4)
    tape = Tape(payload)
    route = compile_route(width, 1)
    execute(route, [tape])
    require(signed(tape.bits, width) == [-8, 0], "signed boundary positive control")
    gates = doubling_gates(width, 1)
    omitted = gates[:9] + gates[10:]
    require(gate_oracle(omitted, payload) != tape.bits, "omitted sign clear")
    reversed_rotation = [(a, b) for a, b in reversed(gates[:9])] + list(gates[9:])
    require(gate_oracle(reversed_rotation, payload) != tape.bits,
            "reversed rotation discriminator")
    require(gate_oracle(((0, 1), (1, 0), (0, 1)), [0, 1]) == [1, 0],
            "swap orientation control")
    return len(trials) + 3


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    source_route, gates = sources()
    result = {"claim_type": "scoped circuit construction and written traffic proof",
              "basis_columns": basis_checks(source_route, gates),
              "signed_pairs": arithmetic_checks(),
              "width_dimension_roundtrips": general_checks(),
              "physical_comparisons": physical_checks(source_route),
              "controls": controls(), "new_all_D_cost": [3284, -2],
              "baseline_all_D_paths": [baseline_formula(a, b)
                                       for a, b in itertools.product(((0, 1), (1, 0)), repeat=2)]}
    result["package_sha256"] = {
        name: hashlib.sha256((HERE / name).read_bytes()).hexdigest()
        for name in PACKAGE_FILES}
    if args.receipt:
        args.receipt.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, sort_keys=True))
    print("PASS_RESIDENT_SCALE_RIBBON")


if __name__ == "__main__":
    main()
