"""Decide complete tensor identities for dyadic Clifford register programs.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
The trace interpolation proof is in PROOF.md. No tensor matrix is built.
"""
import argparse
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent / "vendor"))
from fields import Gaussian as G


def require(condition, message):
    if not condition:
        raise ValueError(message)


def conjugate(z):
    return G.pair(z.real, -z.imag)


def norm2(z):
    return z.real*z.real + z.imag*z.imag


def power(z, k):
    result = G(1)
    while k:
        if k & 1:
            result = result*z
        z = z*z
        k //= 2
    return result


def scalar(x):
    require(type(x) in (str, int), "Use an integer or an exact Gaussian string")
    return G(x)


def identity(d):
    return tuple(tuple(G(int(i == j)) for j in range(d)) for i in range(d))


def adjoint(a):
    return tuple(tuple(conjugate(a[j][i]) for j in range(len(a))) for i in range(len(a)))


def multiply(a, b):
    d = len(a)
    out = [[G(0) for _ in range(d)] for _ in range(d)]
    sparse_b = [[(j, x) for j, x in enumerate(row) if x] for row in b]
    for i, row in enumerate(a):
        for k, x in enumerate(row):
            if x:
                for j, y in sparse_b[k]:
                    out[i][j] = out[i][j] + x*y
    return tuple(tuple(row) for row in out)


def key(a):
    return tuple(tuple((z.real, z.imag) for z in row) for row in a)


def pauli(n, x, z, phase=0):
    d = 1 << n
    unit = power(G("i"), phase % 4)
    return tuple(
        tuple(unit*(-1 if (z & j).bit_count() % 2 else 1) if i == j ^ x else G(0)
              for j in range(d)) for i in range(d))


def pauli_signature(a):
    """Return the exact X/Z/phase label, or reject a non-Pauli matrix."""
    d = len(a)
    n = d.bit_length()-1
    first = [(i, row[0]) for i, row in enumerate(a) if row[0]]
    require(len(first) == 1, "Conjugated generator is not a Pauli")
    x, unit = first[0]
    units = [G(1), G("i"), G(-1), G("-i")]
    require(unit in units, "Conjugated generator has a non-Pauli phase")
    z = 0
    for j in range(n):
        value = a[x ^ (1 << j)][1 << j]
        require(value in (unit, -unit), "Conjugated generator is not a Pauli")
        if value == -unit:
            z |= 1 << j
    phase = units.index(unit)
    require(a == pauli(n, x, z, phase), "Conjugated generator is not a Pauli")
    return x, z, phase


def validate_operator(a, n):
    d = 1 << n
    require(len(a) == d and all(len(row) == d for row in a), "Operator shape")
    for row in a:
        for value in row:
            for part in (value.real, value.imag):
                den = part.denominator
                require(den & (den-1) == 0, "Operator entry is not dyadic")
    star = adjoint(a)
    require(multiply(star, a) == identity(d), "Operator is not unitary")
    return [pauli_signature(multiply(multiply(a, pauli(n, x, z)), star))
            for x, z in [(1 << j, 0) for j in range(n)] + [(0, 1 << j) for j in range(n)]]


def parse_problem(problem):
    require(type(problem) is dict and set(problem) == {"axes", "roles", "operators", "program", "reference"},
            "Problem keys")
    n, r = problem["axes"], problem["roles"]
    require(type(n) is int and n >= 0 and type(r) is int and r > 0, "Axes or roles")
    require(type(problem["operators"]) is dict, "Operators must be an object")
    matrices = {}
    for name, rows in problem["operators"].items():
        require(type(name) is str and bool(name) and type(rows) is list and
                all(type(row) is list for row in rows), "Operator format")
        a = tuple(tuple(scalar(x) for x in row) for row in rows)
        validate_operator(a, n)
        matrices[name] = a
    return n, r, matrices


def accumulate(out, label, coefficient):
    value = out.get(label, G(0)) + coefficient
    if value:
        out[label] = value
    else:
        out.pop(label, None)


def compile_difference(problem):
    """Keep phases in matrix keys and keep scalar coefficients outside them."""
    n, roles, operators = parse_problem(problem)
    eye = identity(1 << n)
    bank = {key(eye): eye}
    products = {}

    def execute(instructions):
        require(type(instructions) is list, "Instruction list")
        rows = [{(i, key(eye)): G(1)} for i in range(roles)]
        for instruction in instructions:
            require(type(instruction) is dict, "Instruction object")
            kind = instruction.get("op")
            allowed = {"add": {"op", "src", "dst", "coefficient"},
                       "scale": {"op", "dst", "coefficient"},
                       "swap": {"op", "src", "dst"},
                       "apply": {"op", "dst", "symbol", "inverse"},
                       "query": {"op", "src", "dst", "symbol", "inverse", "coefficient"}}
            require(kind in allowed and set(instruction) <= allowed[kind], "Instruction keys")
            dst = instruction.get("dst")
            require(type(dst) is int and 0 <= dst < roles, "Destination role")
            src = instruction.get("src", dst)
            require(type(src) is int and 0 <= src < roles, "Source role")
            if kind in ("add", "query", "swap"):
                require("src" in instruction, "Missing source role")
            if kind == "swap":
                rows[src], rows[dst] = rows[dst], rows[src]
                continue
            if kind == "scale":
                coefficient = scalar(instruction["coefficient"])
                rows[dst] = {k: coefficient*v for k, v in rows[dst].items() if coefficient*v}
                continue
            image = rows[src].copy()
            if kind in ("apply", "query"):
                symbol = instruction.get("symbol")
                inverse = instruction.get("inverse", False)
                require(type(inverse) is bool and type(symbol) is str and symbol in operators, "Operator reference")
                a = adjoint(operators[symbol]) if inverse else operators[symbol]
                image = {}
                for (i, old), coefficient in rows[src].items():
                    cache_key = symbol, inverse, old
                    if cache_key not in products:
                        product = multiply(a, bank[old])
                        new = key(product)
                        bank[new] = product
                        products[cache_key] = new
                    accumulate(image, (i, products[cache_key]), coefficient)
            if kind == "apply":
                rows[dst] = image
            else:
                coefficient = scalar(instruction.get("coefficient", 1))
                updated = rows[dst].copy()
                for label, value in image.items():
                    accumulate(updated, label, coefficient*value)
                rows[dst] = updated
        return rows

    left, right = execute(problem["program"]), execute(problem["reference"])
    result = []
    for output, (a, b) in enumerate(zip(left, right)):
        row = a.copy()
        for label, coefficient in b.items():
            accumulate(row, label, -coefficient)
        for input_role in range(roles):
            terms = [(coefficient, bank[operator]) for (i, operator), coefficient in row.items() if i == input_role]
            if terms:
                result.append((output, input_role, terms))
    return n, result


def cutoff_polynomial(n):
    require(type(n) is int and n >= 0, "Nonnegative axis count")
    coefficients, denominator = [1], 1
    for j in range(1, 2*n+1):
        scale, sign = 4**j, (-1)**j
        new = [0]*(len(coefficients)+1)
        for degree, coefficient in enumerate(coefficients):
            new[degree] -= sign*coefficient
            new[degree+1] += scale*coefficient
        coefficients = new
        denominator *= scale-sign
    return [Q(0)]+[Q(a, 4*denominator) for a in coefficients for _ in range(4)]


def gram(matrices):
    d = len(matrices[0])
    return [[sum((conjugate(a)*b for row_a, row_b in zip(left, right)
                  for a, b in zip(row_a, row_b)), G(0))/d
             for right in matrices] for left in matrices]


def energy(coefficients, inner, width):
    value = sum((conjugate(a)*b*power(inner[i][j], width)
                 for i, a in enumerate(coefficients) for j, b in enumerate(coefficients)), G(0))
    require(value.imag == 0 and value.real >= 0, "Invalid squared residual norm")
    return value.real


def trace_buckets(coefficients, inner):
    out = {}
    for i, a in enumerate(coefficients):
        for j, b in enumerate(coefficients):
            value = inner[i][j]
            accumulate(out, (value.real, value.imag), conjugate(a)*b)
    return out


def bucket_energies(buckets, cutoff):
    powers = {label: G(1) for label in buckets}
    answer = []
    for _ in range(cutoff):
        for label in powers:
            powers[label] = powers[label]*G.pair(*label)
        value = sum((coefficient*powers[label] for label, coefficient in buckets.items()), G(0))
        require(value.imag == 0 and value.real >= 0, "Invalid bucket norm")
        answer.append(value.real)
    return answer


def tensor_entry(coefficients, matrices, output, input_tuple):
    answer = G(0)
    for coefficient, a in zip(coefficients, matrices):
        value = coefficient
        for x, y in zip(output, input_tuple):
            value = value*a[x][y]
        answer = answer+value
    return answer


def entry_witness(coefficients, matrices, inner, width):
    """Choose an entry by exact conditional squared norms."""
    d = len(matrices[0])
    initial = energy(coefficients, inner, width)
    require(initial > 0, "The requested width has zero residual")
    current = list(coefficients)
    output, input_tuple = [], []
    for remaining in range(width-1, -1, -1):
        best = None
        for x in range(d):
            for y in range(d):
                candidate = [c*a[x][y] for c, a in zip(current, matrices)]
                value = energy(candidate, inner, remaining)
                if best is None or value > best[0]:
                    best = value, x, y, candidate
        require(best[0] > 0, "Conditional tensor norm lost the witness")
        _, x, y, current = best
        output.append(x)
        input_tuple.append(y)
    value = sum(current, G(0))
    require(norm2(value)*d**width >= initial, "Tensor entry lower bound")
    return {"width": width, "output_tuple": output, "input_tuple": input_tuple,
            "discrepancy": str(value)}


def analyze(n, terms):
    """Analyze distinct validated Clifford matrices with nonzero coefficients."""
    coefficients, matrices = zip(*terms)
    require(len(set(key(a) for a in matrices)) == len(matrices), "Merge equal exact operators first")
    inner = gram(matrices)
    polynomial = cutoff_polynomial(n)
    buckets = trace_buckets(coefficients, inner)
    energies = bucket_energies(buckets, len(polynomial)-1)
    mass = sum(norm2(c) for c in coefficients)
    require(sum(b*v for b, v in zip(polynomial[1:], energies)) == mass, "Trace interpolation failed")
    require(max(energies) >= Q(14, 15)*mass, "Stable separation failed")
    width = 1 + max(range(len(energies)), key=energies.__getitem__)
    witness = entry_witness(coefficients, matrices, inner, width)
    return {"support": len(terms), "trace_buckets": len(buckets), "coefficient_norm_squared": str(mass),
            "normalized_squared_norms": [str(x) for x in energies],
            "first_nonzero_width": 1+next(i for i, x in enumerate(energies) if x),
            "witness": witness}


def certify(problem):
    n, residuals = compile_difference(problem)
    digest = hashlib.sha256(json.dumps(problem, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    result = {"schema": "clifford-tensor-gram/v1", "problem_sha256": digest,
              "axes": n, "cutoff": 8*n+4, "equivalent_at_all_positive_widths": not residuals,
              "nonzero_endpoint_entries": len(residuals)}
    if residuals:
        output, input_role, terms = residuals[0]
        result["failure"] = {"output_role": output, "input_role": input_role, **analyze(n, terms)}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("problem", type=Path)
    args = parser.parse_args()
    result = certify(json.loads(args.problem.read_text(encoding="utf-8")))
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
