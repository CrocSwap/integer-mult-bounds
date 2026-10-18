# SPDX-License-Identifier: Apache-2.0
"""Authenticate predecessor inputs and construct the literal A13 dispatch."""

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
PRIOR = ROOT / "research/rank7-native-half-boundary"
SCALAR = ROOT / "research/rank7-boolean-scalar-caller"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def authenticate():
    records = json.loads((PACKAGE / "SOURCES.json").read_text())["files"]
    live = [row for row in records if row["usage"] == "input"]
    require(1 <= len(live) <= 64, "bounded live source inventory")
    for row in live:
        path = ROOT / row["path"]
        require(
            not path.is_symlink() and path.stat().st_size <= 8_000_000,
            "bounded regular live input",
        )
        require(
            hashlib.sha256(path.read_bytes()).hexdigest() == row["sha256"],
            "pinned live source bytes: " + row["path"],
        )
    return len(live)


def sources():
    authenticate()
    sys.path.insert(0, str(SCALAR))
    import caller

    sys.path.insert(0, str(PRIOR))
    spec = importlib.util.spec_from_file_location(
        "_a13_native_predecessor", PRIOR / "verify.py"
    )
    require(spec is not None and spec.loader is not None, "predecessor module")
    predecessor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(predecessor)
    return predecessor, caller


def signed_permutation(rows):
    from boundary import component

    require(len(rows) == 512, "complete Gaussian monomial")
    result = []
    for row in rows:
        for imaginary in (False, True):
            real = component(row, imaginary)
            require(len(real) == 1, "one real monomial coefficient")
            index, value = next(iter(real.items()))
            require(value in (-1, 1), "Gaussian unit sign")
            result.append((index, int(value)))
    require({i for i, _ in result} == set(range(1024)), "real component bijection")
    return result


def permutation_program(permutation, offset=0):
    require(len(permutation) == 1024 and offset in (0, 1024), "owned local field")
    require({i for i, _ in permutation} == set(range(1024)), "permutation domain")
    contents, position = list(range(1024)), list(range(1024))
    program = []
    for output, (original, sign) in enumerate(permutation):
        require(sign in (-1, 1), "unit real sign")
        other = position[original]
        if other != output:
            displaced = contents[output]
            program.append(("swap", offset + output, offset + other))
            contents[output], contents[other] = original, displaced
            position[original], position[displaced] = output, other
    require(contents == [i for i, _ in permutation], "literal permutation realization")
    program += [("neg", offset + i) for i, (_, s) in enumerate(permutation) if s == -1]
    return program


def remap(instruction, fields):
    kind, target = instruction[:2]
    if kind in ("add", "swap"):
        return kind, fields[target], fields[instruction[2]], *instruction[3:]
    return kind, fields[target]


def dispatch(predecessor, columns, control=False):
    from circuits import lift

    C = predecessor.C
    old, frame = C.canonical_frame([382]), C.canonical_frame([45])
    logical = predecessor.logical_warp(columns)
    physical = predecessor.matrix(C.adjoint(old) + logical + frame)
    program = permutation_program(signed_permutation(physical), 1024)
    cut = next(i for i, gate in enumerate(frame) if gate[0] == "C")
    require(sum(g[0] == "C" for g in frame) == 1, "one actual rank-one Fourier gate")
    _, axis, sign = frame[cut]
    program += permutation_program(signed_permutation(predecessor.matrix(frame[:cut])))
    for x in range(512):
        y = x ^ axis
        if x < y:
            fields = (2 * x, 2 * x + 1, 2 * y, 2 * y + 1)
            program += [
                remap(instruction, fields) for instruction in lift(sign, control)
            ]
    program += permutation_program(
        signed_permutation(predecessor.matrix(frame[cut + 1 :]))
    )
    program += [("add", i, 1024 + i, -1, 2) for i in range(1024)]
    operators = {
        "old": predecessor.matrix(old),
        "source": predecessor.matrix(logical + frame),
        "target": predecessor.matrix(frame),
    }
    return program, operators


def evaluate_operator(rows, values):
    require(len(rows) == len(values) == 512, "complete local operator")
    require(all(len(row) <= 16 for row in rows), "bounded operator support")
    result = []
    for row in rows:
        real = imag = 0
        for x, (a, b) in row.items():
            c, d = values[x]
            real += a * c - b * d
            imag += b * c + a * d
        result.append((real, imag))
    return result


def encoded(values):
    result = [4 * value for pair in values for value in pair]
    require(
        len(result) == 1024 and all(v.denominator == 1 for v in result),
        "complete quarter-grid encoding",
    )
    return [int(v) for v in result]


def fixture(raw, operators):
    from fractions import Fraction as Q

    require(
        len(raw) == 5120 and all(type(x) is int for x in raw), "five raw complex fields"
    )
    fields = [
        [(Q(raw[1024 * f + 2 * x]), Q(raw[1024 * f + 2 * x + 1])) for x in range(512)]
        for f in range(5)
    ]
    target = [
        tuple(
            sum(sign * fields[f][x][i] for f, sign in enumerate((1, -1, 1, -1))) / 2
            for i in (0, 1)
        )
        for x in range(512)
    ]
    source_input = encoded(evaluate_operator(operators["old"], fields[4]))
    source_output = encoded(evaluate_operator(operators["source"], fields[4]))
    converted = encoded(evaluate_operator(operators["target"], target))
    require(all(v % 2 == 0 for v in source_output), "reached half-ADD source alignment")
    final = [a - b // 2 for a, b in zip(converted, source_output, strict=True)]
    return encoded(target) + source_input, final + source_output


def refresh(predecessor, work):
    result = predecessor.run(work)
    require(
        result == json.loads((PRIOR / "RESULT.json").read_text()),
        "fresh complete predecessor receipt",
    )
    inherited, _, _ = predecessor.load_parent()
    bindings = {}
    for provider in ("base", "extra"):
        directory = work / provider / "native"
        word = inherited.read(directory / "CANONICAL-WORD.json.gz")
        events = inherited.read(directory / "LOCAL-PROGRAMS.json.gz")["forward"]
        columns, event = predecessor.bind(word, events)
        bindings[provider] = {
            "columns": columns,
            "event": event,
            "program_sha256": predecessor.digest(events),
        }
    require(
        bindings["base"]["columns"] == bindings["extra"]["columns"],
        "same reached operator in both providers",
    )
    return bindings
