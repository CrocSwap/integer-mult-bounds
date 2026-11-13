"""Verify the shared-bank graph, its output contract and persistent reuse."""
from pathlib import Path
import hashlib
import json
import platform
import random
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from machine import Tape, run
from shared import authenticate, compile_shared, need, validate

MAX_CELLS = 50000


def multiply(a, b):
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]


def rotate(value, phase):
    return multiply(value, ((1, 0), (0, 1), (-1, 0), (0, -1))[phase % 4])


def truncate(value, divisor):
    return (1 if value >= 0 else -1) * (abs(value) // divisor)


def encode(values, width):
    need(1 <= width <= 64, "fixture component width")
    need(1 <= len(values) <= 256, "fixture coefficient capacity")
    need(all(-(1 << (width - 1)) <= x < 1 << (width - 1)
             for value in values for x in value), "signed fixture range")
    return "".join(format(x % (1 << width), f"0{width}b")
                   for value in values for x in value)


def decode(tape, count, width):
    need(1 <= count <= 256 and 1 <= width <= 64, "decode capacity")
    values = []
    for k in range(2 * count):
        bits = "".join(tape.cells.get(tape.origin + k * width + j, "_")
                       for j in range(width))
        need(set(bits) <= {"0", "1"}, "complete output field")
        value = int(bits, 2)
        values.append(value - (1 << width) if bits[0] == "1" else value)
    return list(zip(values[::2], values[1::2], strict=True))


def header(parameters):
    need(len(parameters) == 9 and all(type(x) is int and 1 <= x <= 32
                                     for x in parameters), "fixture header domain")
    return "".join("0" * (x.bit_length() - 1) + bin(x)[2:] for x in parameters)


def geometry(parameters):
    p, d, r, dimension, outer, spectator, block, rho1, width = parameters
    need(dimension <= d and rho1 <= block and width >= p + 2, "valid layer header")
    length = dimension * block
    count = outer * (1 << length) * spectator * r
    need(count <= 256 and d <= 8, "finite fixture geometry")
    positions = tuple(j * block + rho1 - 1 for j in range(dimension))
    return count, positions


def phases(values, parameters):
    _, _, r, _, _, spectator, _, _, _ = parameters
    _, positions = geometry(parameters)
    return [rotate(value, sum(((k // (r * spectator)) >> j) & 1 for j in positions))
            for k, value in enumerate(values)]


def central(values, parameters, kind):
    _, d, r, dimension, outer, spectator, block, _, _ = parameters
    _, positions = geometry(parameters)
    q = 1 << (dimension * block)
    mask = sum(1 << j for j in positions)
    result = []
    for a in range(outer):
        for destination in range(q):
            for s in range(spectator):
                for coefficient in range(r):
                    total = (0, 0)
                    for word in range(1 << dimension):
                        address = destination & ~mask
                        kernel = (1, 0)
                        for j, position in enumerate(positions):
                            x, y = (word >> j) & 1, (destination >> position) & 1
                            address |= x << position
                            factor = ((1, 1 if x == y else -1) if kind == "C"
                                      else ((-1 if x and y else 1), 0))
                            kernel = multiply(kernel, factor)
                        k = ((a * q + address) * spectator + s) * r + coefficient
                        term = multiply(kernel, values[k])
                        total = total[0] + term[0], total[1] + term[1]
                    if kind == "C":
                        result.append(tuple(x * (1 << (d - dimension)) for x in total))
                    else:
                        result.append(tuple(truncate(x, 1 << dimension) for x in total))
    return result


def normalize(values, parameters):
    _, d, _, dimension, _, _, _, _, _ = parameters
    factor = (1, 0)
    for _ in range(dimension):
        factor = multiply(factor, (1, -1))
    return [tuple(truncate(x, 1 << (d + dimension))
                  for x in multiply(factor, value)) for value in values]


def initial_tapes():
    return [Tape({100 + 17 * i - 2: "1", 100 + 17 * i + MAX_CELLS: "|"},
                 100 + 17 * i) for i in range(20)]


def install(tape, bits):
    need(len(bits) < MAX_CELLS, "supplied packet reserve")
    need(tape.head == tape.origin, "supplied owner at its origin")
    # Explicit outside input/C service, not an instruction of the new graph.
    for position in tuple(tape.cells):
        if tape.origin <= position < tape.origin + MAX_CELLS:
            del tape.cells[position]
    tape.cells.update({tape.origin + j: bit for j, bit in enumerate(bits)})


def execute(code, tapes, entry, histories):
    identities = tuple(id(t) for t in tapes)
    private = [dict(t.cells) for t in tapes[2:]]
    public_header = dict(tapes[0].cells)
    steps, visits = run(code, tapes, entry, 20000000)
    need(tuple(id(t) for t in tapes) == identities, "physical identity retention")
    need(all(t.head == t.origin for t in tapes), "all heads return")
    need([dict(t.cells) for t in tapes[2:]] == private, "shared private bank retirement")
    need(tapes[0].cells == public_header, "complete header preservation")
    for i, (tape, visited) in enumerate(zip(tapes, visits, strict=True)):
        need(all(tape.origin - 1 <= x < tape.origin + MAX_CELLS for x in visited),
             "opaque exterior is never visited")
        histories[i].update(visited)
        need((tape.low, tape.high) == (min(histories[i]), max(histories[i])),
             "historical union retained across component and call changes")
        need(tape.cells[tape.origin - 2] == "1" and
             tape.cells[tape.origin + MAX_CELLS] == "|", "opaque exterior preservation")
    return steps, visits


def check_case(code, entry_phase, tapes, histories, parameters, seed):
    count, _ = geometry(parameters)
    p, d, _, _, _, _, _, _, width = parameters
    rng = random.Random(seed)
    radius = 1 << p
    disk = [(a, b) for a in range(-radius, radius + 1)
            for b in range(-radius, radius + 1) if a * a + b * b <= radius * radius]
    source = [rng.choice(disk) for _ in range(count)]
    install(tapes[0], header(parameters))
    install(tapes[1], encode(source, width))
    first_steps, first_visits = execute(code, tapes, entry_phase, histories)
    need(decode(tapes[1], count, width) == phases(source, parameters), "entry phase result")
    # Test-only C producer and format obligation, explicitly outside scope.
    supplied = central(phases(source, parameters), parameters, "C")
    input_width = p + 2 * d + 4
    install(tapes[1], encode(supplied, input_width))
    exit_steps, exit_visits = execute(code, tapes, 0, histories)
    actual = decode(tapes[1], count, width)
    need(actual == phases(normalize(supplied, parameters), parameters), "new exit result")
    need(actual == central(source, parameters, "H"), "whole boundary tensor identity")
    need(all(tapes[1].cells.get(tapes[1].origin + j, "_") == "_"
             for j in range(2 * count * width, 2 * count * input_width + 1)),
         "common-grid old tail retired before final phase")
    shared = sum(bool(first_visits[i] & exit_visits[i]) for i in range(2, 18))
    need(shared == 16, "all sixteen egress private roles share phase histories")
    return {"parameters": parameters, "coefficients": count,
            "entry_steps": first_steps, "exit_steps": exit_steps,
            "shared_private_roles": shared}


def rejection_controls(code, entry_phase):
    controls = 0
    bad = list(code)
    bad[0] = ("goto", len(code))
    for function in (lambda: validate(bad, 20),
                     lambda: validate((("emit", "hidden"),), 20),
                     lambda: run(code, [initial_tapes()[0]] * 20, 0, 100),
                     lambda: run(code, initial_tapes(), entry_phase, 1)):
        try:
            function()
        except ValueError:
            controls += 1
        else:
            raise ValueError("rejecting control accepted")
    # A wrong bridge is structurally valid but loses the final phase.
    bad = list(code)
    bridges = [i for i, op in enumerate(code[:entry_phase]) if op == ("goto", entry_phase)]
    need(len(bridges) == 1, "one successful egress-to-phase bridge")
    bad[bridges[0]] = ("halt",)
    tapes = initial_tapes()
    histories = [{t.origin} for t in tapes]
    try:
        check_case(bad, entry_phase, tapes, histories, (2, 2, 1, 2, 1, 1, 1, 1, 4), 174)
    except ValueError as error:
        need(str(error) in ("new exit result", "whole boundary tensor identity"), "bridge control cause")
        controls += 1
    else:
        raise ValueError("missing final phase accepted")
    return controls


def main():
    code, entry_phase = compile_shared()
    need(len(code) == 19960 and entry_phase == 17814, "exact fixed graph sizes")
    tapes = initial_tapes()
    histories = [{t.origin} for t in tapes]
    parameters = [(p, dimension + p % 2, 1, dimension, 1, 1, 1, 1, p + 2)
                  for p in (1, 2, 3) for dimension in range(1, 5)]
    parameters += [(2, 3, 2, 2, 2, 2, 2, rho + 1, 4) for rho in (0, 1)]
    parameters += [parameters[i] for i in (0, 11, 1, 10, 0)]
    rows = [check_case(code, entry_phase, tapes, histories, value, 711 + i)
            for i, value in enumerate(parameters)]
    controls = rejection_controls(code, entry_phase)
    sources = authenticate()
    package_hashes = {str(p.relative_to(HERE)): hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in sorted(HERE.rglob("*")) if p.is_file() and
                      "__pycache__" not in p.parts}
    receipt = {"status": "PASS_SHARED_PHASE_EGRESS_BANK", "physical_tapes": 20,
               "locations": len(code), "entry_phase": entry_phase, "calls": len(rows),
               "coefficients": sum(row["coefficients"] for row in rows),
               "literal_steps": sum(row["entry_steps"] + row["exit_steps"] for row in rows),
               "rejection_controls": controls, "source_files": len(sources),
               "private_visited_interval_cells": sum(t.high - t.low + 1 for t in tapes[2:]),
               "graph_sha256": hashlib.sha256(json.dumps(code, sort_keys=True,
                                                        separators=(",", ":")).encode()).hexdigest(),
               "python": platform.python_version(), "rows": rows,
               "package_sha256": package_hashes}
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
