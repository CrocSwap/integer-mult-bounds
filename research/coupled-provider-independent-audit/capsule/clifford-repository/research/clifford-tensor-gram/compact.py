"""Certify complete native programs with quadratic sums and bitwise witnesses.

Program support can grow exponentially. No base or tensor matrix is built.
Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import certify as c
from check_witness import word_endpoint, add_term
from quadratic import Paths, partial_inner, inverse_circuit


def decision_widths(n):
    if n == 0:
        return list(range(1, 5))
    if n == 1:
        return list(range(5, 9))
    return list(range(8*n-3, 8*n+5))


def validate(problem):
    c.require(type(problem) is dict and set(problem) == {"axes", "roles", "operators", "program", "reference"},
              "Native problem keys")
    n, roles = problem["axes"], problem["roles"]
    c.require(type(n) is int and n >= 0 and type(roles) is int and roles > 0, "Axes or roles")
    c.require(type(problem["operators"]) is dict, "Native operators")
    bank = {}
    for name, circuit in problem["operators"].items():
        c.require(type(name) is str and bool(name) and type(circuit) is list, "Native operator format")
        Paths(n, circuit)
        bank[name, False] = circuit
        bank[name, True] = inverse_circuit(n, circuit)
    allowed = {"add": {"op", "src", "dst", "coefficient"},
               "scale": {"op", "dst", "coefficient"}, "swap": {"op", "src", "dst"},
               "apply": {"op", "dst", "symbol", "inverse"},
               "query": {"op", "src", "dst", "symbol", "inverse", "coefficient"}}
    for instructions in (problem["program"], problem["reference"]):
        c.require(type(instructions) is list, "Native instruction list")
        for op in instructions:
            c.require(type(op) is dict and op.get("op") in allowed, "Instruction object")
            kind = op["op"]
            c.require(set(op) <= allowed[kind], "Instruction keys")
            c.require(type(op.get("dst")) is int and 0 <= op["dst"] < roles, "Destination role")
            if kind in ("add", "query", "swap"):
                c.require(type(op.get("src")) is int and 0 <= op["src"] < roles, "Source role")
            if kind in ("query", "apply"):
                c.require(type(op.get("symbol")) is str and op["symbol"] in problem["operators"] and
                          type(op.get("inverse", False)) is bool, "Operator reference")
            if kind == "scale":
                c.require("coefficient" in op, "Scale coefficient")
            if "coefficient" in op:
                c.scalar(op["coefficient"])
    return bank


def merge_terms(coefficients, paths):
    """For unitary matrices, normalized inner product one means equality."""
    d = 1 << paths[0].n
    inner = [[partial_inner(a, b)/d for b in paths] for a in paths]
    representatives, merged = [], []
    for j, coefficient in enumerate(coefficients):
        i = next((i for i, k in enumerate(representatives) if inner[k][j] == 1), None)
        if i is None:
            representatives.append(j)
            merged.append(coefficient)
        else:
            merged[i] = merged[i]+coefficient
    keep = [i for i, coefficient in enumerate(merged) if coefficient]
    indices = [representatives[i] for i in keep]
    return ([merged[i] for i in keep], [paths[j] for j in indices],
            [[inner[i][j] for j in indices] for i in indices])


def residuals(problem):
    bank = validate(problem)
    n = problem["axes"]
    paths = {}
    out = []
    for input_role in range(problem["roles"]):
        left = word_endpoint(problem, problem["program"], input_role)
        right = word_endpoint(problem, problem["reference"], input_role)
        for output_role, (a, b) in enumerate(zip(left, right)):
            words = a.copy()
            for word, coefficient in b.items():
                add_term(words, word, -coefficient)
            if not words:
                continue
            for word in words:
                if word not in paths:
                    circuit = [gate for letter in reversed(word) for gate in bank[letter]]
                    paths[word] = Paths(n, circuit)
            coefficients, operators, inner = merge_terms(list(words.values()), [paths[word] for word in words])
            if coefficients:
                out.append((output_role, input_role, coefficients, operators, inner))
    return out


def entry_witness(coefficients, paths, inner, width):
    """Choose each coordinate bit from two exact conditional norms."""
    n, d = paths[0].n, 1 << paths[0].n
    initial = c.energy(coefficients, inner, width)
    c.require(initial > 0, "Positive residual norm")
    current = list(coefficients)
    output, inputs = [], []
    partial_cache = {}

    def score(x, y, remaining):
        key = tuple(x), tuple(y)
        if key not in partial_cache:
            partial_cache[key] = [[partial_inner(a, b, x, y) for b in paths] for a in paths]
        partial = partial_cache[key]
        value = sum((c.conjugate(a)*b*partial[i][j]*c.power(inner[i][j], remaining)
                     for i, a in enumerate(current) for j, b in enumerate(current)), c.G(0))
        c.require(value.imag == 0 and value.real >= 0, "Conditional squared norm")
        return value.real

    for remaining in range(width-1, -1, -1):
        x, y = [], []
        parent = d*c.energy(current, inner, remaining+1)
        for coordinate in (x, y):
            for _ in range(n):
                children = []
                for bit in (0, 1):
                    coordinate.append(bit)
                    children.append(score(x, y, remaining))
                    coordinate.pop()
                c.require(sum(children) == parent, "Conditional norm split")
                bit = int(children[1] > children[0])
                coordinate.append(bit)
                parent = children[bit]
                c.require(parent > 0, "Conditional witness vanished")
        a, b = sum(bit << j for j, bit in enumerate(x)), sum(bit << j for j, bit in enumerate(y))
        output.append(a)
        inputs.append(b)
        current = [coefficient*path.entry(a, b) for coefficient, path in zip(current, paths)]
    value = sum(current, c.G(0))
    c.require(c.norm2(value)*d**width >= initial, "Compact entry lower bound")
    return {"width": width, "output_tuple": output, "input_tuple": inputs, "discrepancy": str(value)}


def analyze(n, coefficients, paths, inner):
    polynomial = c.cutoff_polynomial(n)
    mass = sum(c.norm2(a) for a in coefficients)
    norms = c.bucket_energies(c.trace_buckets(coefficients, inner), 8*n+4)
    c.require(sum(b*v for b, v in zip(polynomial[1:], norms)) == mass, "Compact trace interpolation")
    c.require(max(norms) >= Q(75, 76)*mass, "Improved stable separation")
    c.require(any(norms[f-1] for f in decision_widths(n)), "Reduced width criterion")
    width = 1+max(range(len(norms)), key=norms.__getitem__)
    return {"support": len(paths), "coefficient_norm_squared": str(mass),
            "normalized_squared_norms": [str(x) for x in norms],
            "witness": entry_witness(coefficients, paths, inner, width)}


def certify(problem):
    entries = residuals(problem)
    n = problem["axes"]
    result = {"schema": "clifford-tensor-gram/native-v1", "axes": n,
              "problem_sha256": hashlib.sha256(json.dumps(problem, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
              "cutoff": 8*n+4, "decision_widths": decision_widths(n),
              "equivalent_at_all_positive_widths": not entries, "nonzero_endpoint_entries": len(entries)}
    if entries:
        output, input_role, coefficients, paths, inner = entries[0]
        result["failure"] = {"output_role": output, "input_role": input_role,
                             **analyze(n, coefficients, paths, inner)}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("problem", type=Path)
    args = parser.parse_args()
    print(json.dumps(certify(json.loads(args.problem.read_text())), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
