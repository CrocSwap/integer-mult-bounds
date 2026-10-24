"""Check finite equations with a separate feedback compiler and no elimination.

Imports only shared syntax/exact arithmetic, never the producer. A verified
failure word proves difference, not that its length is minimal.
Prepared for Krzysztof Wójt with OpenAI Codex assistance. Apache-2.0.
"""

import argparse
import json
from pathlib import Path

from syntax import exact_keys, fingerprint, validate


def require(condition, message):
    if not condition:
        raise ValueError(message)


def reconstruct(program):
    """Build sparse constant/unary equations, then forward-solve I-E.

    This deliberately differs from the producer's per-row recurrence.
    """
    f = validate(program)
    roles, alphabet = program["roles"], program["operators"]
    r = len(roles)
    definitions = [None] * r
    endpoints = []

    def combine(pairs):
        result = {}
        for scalar, expression in pairs:
            for j, value in expression.items():
                result[j] = f.add(result.get(j, f.zero), f.mul(scalar, value))
                if not result[j]:
                    del result[j]
        return result

    for side in ("left", "right"):
        registers = {name: {i: f.one} for i, name in enumerate(roles)}
        for operation in program[side]:
            destination = operation["dst"]
            if operation["op"] == "linear":
                registers[destination] = combine(
                    (f.parse(c), registers[name]) for name, c in operation["terms"])
                continue
            source = operation.get("src", destination)
            index = len(definitions)
            definitions.append((registers[source].copy(), operation["operator"], operation["direction"]))
            if operation["op"] == "apply":
                registers[destination] = {index: f.one}
            else:
                registers[destination] = combine([
                    (f.one, registers[destination]),
                    (f.parse(operation["coefficient"]), {index: f.one})])
        endpoints.append([registers[name] for name in roles])
    d = len(definitions)
    # H = (I-E)^-1, obtained by an exact triangular solve; no matrix inverse.
    h = [[f.one if i == j else f.zero for j in range(d)] for i in range(d)]
    for i in range(r, d):
        dependency, _, _ = definitions[i]
        for j, coefficient in dependency.items():
            require(j < i, "noncausal constant dependency")
            for k in range(d):
                h[i][k] = f.add(h[i][k], f.mul(coefficient, h[j][k]))
    transitions = {a: [[f.zero] * d for _ in range(d)] for a in alphabet}
    for j in range(r, d):
        dependency, a, sign = definitions[j]
        unary = dependency if sign == 1 else {j: f.neg(f.one)}
        for i in range(d):
            if h[i][j]:
                for k, coefficient in unary.items():
                    transitions[a][i][k] = f.add(transitions[a][i][k], f.mul(h[i][j], coefficient))
    u = []
    for left, right in zip(*endpoints):
        delta = combine([(f.one, left), (f.neg(f.one), right)])
        u.append([delta.get(j, f.zero) for j in range(d)])
    return f, u, transitions, [row[:r] for row in h]


def multiply(row, matrix, f, columns):
    answer = [f.zero] * columns
    for i, coefficient in enumerate(row):
        if coefficient:
            for j in range(columns):
                if matrix[i][j]:
                    answer[j] = f.add(answer[j], f.mul(coefficient, matrix[i][j]))
    return answer


def index(value, size):
    require(type(value) is int and 0 <= value < size, "index outside declared boundary")
    return value


def check(program, certificate):
    f, u, t, v = reconstruct(program)
    r, d = len(u), len(v)
    require(isinstance(certificate, dict), "certificate must be an object")
    require(certificate.get("schema") == "inverse-dirty-certificate/v1", "unknown certificate schema")
    require(certificate.get("program_sha256") == fingerprint(program), "certificate belongs to another program")

    def path_row(output, word):
        row = u[index(output, r)][:]
        require(isinstance(word, list) and len(word) < d, "path exceeds the state bound")
        for symbol in word:
            require(isinstance(symbol, str) and symbol in t, "unknown path symbol")
            row = multiply(row, t[symbol], f, d)
        return row

    verdict = certificate.get("verdict")
    common = {"schema", "program_sha256", "verdict"}
    if verdict == "different":
        exact_keys(certificate, common | {"output", "input", "word", "coefficient"})
        row = path_row(certificate["output"], certificate["word"])
        value = multiply(row, v, f, r)[index(certificate["input"], r)]
        require(value != f.zero and value == f.parse(certificate["coefficient"]), "invalid distinguishing coefficient")
        return {"verdict": "different", "states": d, "witness_dimension": len(certificate["word"]) + 1}
    require(verdict == "equal", "unknown verdict")
    exact_keys(certificate, common | {"paths", "initial", "closure"})
    paths = certificate["paths"]
    require(isinstance(paths, list) and len(paths) <= d, "too many basis rows")
    rows = []
    for path in paths:
        exact_keys(path, {"output", "word"})
        rows.append(path_row(path["output"], path["word"]))
    b = len(rows)

    def scalar_matrix(value, height, width):
        require(isinstance(value, list) and len(value) == height, "coordinate matrix height")
        result = []
        for row in value:
            require(isinstance(row, list) and len(row) == width, "coordinate matrix width")
            result.append([f.parse(x) for x in row])
        return result

    initial = scalar_matrix(certificate["initial"], r, b)
    exact_keys(certificate["closure"], set(t))
    for i in range(r):
        require(multiply(initial[i], rows, f, d) == u[i], "initial rows not in certified span")
    for row in rows:
        require(not any(multiply(row, v, f, r)), "basis row has a nonzero input projection")
    for symbol, transition in t.items():
        coordinates = scalar_matrix(certificate["closure"][symbol], b, b)
        for i, row in enumerate(rows):
            require(multiply(row, transition, f, d) == multiply(coordinates[i], rows, f, d),
                    "span is not transition-closed")
    return {"verdict": "equal", "states": d, "invariant_rows": b}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("program", type=Path)
    parser.add_argument("certificate", type=Path)
    args = parser.parse_args()
    program = json.loads(args.program.read_text(encoding="utf-8"))
    certificate = json.loads(args.certificate.read_text(encoding="utf-8"))
    print(json.dumps(check(program, certificate), sort_keys=True))


if __name__ == "__main__":
    main()
