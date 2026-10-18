#!/usr/bin/env python3
"""Finite semantic audit of the retained Lean HPE pairs. Apache-2.0.

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.
The source engine is a differential-test subject, not the independent kernel
oracle. No source verifier or packed equality algorithm is imported.
"""
import argparse
import ast
import copy
import hashlib
import json
from pathlib import Path
import re
import sys
import types

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
EXACT = "research/hyperplane-end-lean/HyperplaneEnd/Exact.lean"
CLIFFORD = "research/split-centres-global/vendor/clifford_exact.py"
ADAPTERS = "research/complex-571-hpeq5/code/hpe_adapters_local.py"
N = 512
ZERO = (0, 0)
UNITS = ((1, 0), (0, 1), (-1, 0), (0, -1))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical_json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def digest(value):
    return hashlib.sha256(canonical_json(value).encode()).hexdigest()


def validate_receipt(path, actual):
    def unique_object(pairs):
        out = {}
        for key, value in pairs:
            require(key not in out, "duplicate receipt key: " + key)
            out[key] = value
        return out

    expected = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object)
    # Python equality identifies True, 1 and 1.0; JSON evidence must not.
    require(canonical_json(expected) == canonical_json(actual), "receipt mismatch")


def check_sources(root=ROOT, package=PACKAGE):
    manifest = json.loads((package / "SOURCES.json").read_text(encoding="utf-8"))
    result = {}
    for row in manifest["files"]:
        if row["usage"] != "input":
            continue
        path = Path(row["path"])
        require(not path.is_absolute() and ".." not in path.parts, "invalid input path")
        data = (root / path).read_bytes()
        require(hashlib.sha256(data).hexdigest() == row["sha256"], "source drift: " + row["path"])
        result[row["path"]] = row["sha256"]
    return result


def declaration(text, name, kind):
    matches = list(re.finditer(r"^def " + re.escape(name) + r" : " + re.escape(kind)
                              + r" :=\s*", text, re.M))
    require(len(matches) == 1, "missing/duplicate declaration: " + name)
    start = matches[0].end()
    end = text.find("\n\n", start)
    require(end >= 0, "unterminated declaration: " + name)
    return text[start:end].strip()


def literal_data(text):
    """Closed grammar for source literals; no arbitrary Lean evaluation."""
    pairs, circuits = [], {}
    for i in range(1, 4):
        raw = declaration(text, f"pair{i}", "Pair")
        require(re.fullmatch(r"[0-9\s,\[\]⟨⟩]+", raw) is not None, "nonliteral pair")
        pair = ast.literal_eval(raw.replace("⟨", "[").replace("⟩", "]"))
        require(len(pair) == 4 and len(pair[0]) == 1 and len(pair[1]) == 8, "unexpected pair shape")
        pairs.append(pair)
        for prefix in ("fE", "fU", "wL", "wR", "lhsLit", "rhsLit"):
            name = f"{prefix}{i}"
            raw = declaration(text, name, "List Gate")
            require(raw.startswith("[") and raw.endswith("]"), "nonlist circuit")
            parts = re.split(r"\.(pm|dg|cg|xg|ph)\s+", raw[1:-1])
            require(not parts[0].strip() and len(parts) % 2 == 1, "unparsed circuit content")
            gates = []
            for tag, args in zip(parts[1::2], parts[2::2]):
                args = args.strip().removesuffix(",").strip()
                if tag in ("pm", "dg"):
                    m = re.fullmatch(r"(\[[0-9,\s]*\])\s+(\[[0-9,\s]*\])", args)
                    require(m is not None, "bad two-list gate")
                    gate = [tag, ast.literal_eval(m[1]), ast.literal_eval(m[2])]
                elif tag == "cg":
                    m = re.fullmatch(r"([0-9]+)\s+(true|false)", args)
                    require(m is not None, "bad C gate")
                    gate = [tag, int(m[1]), m[2] == "true"]
                else:
                    require(re.fullmatch(r"[0-9]+", args) is not None, "bad scalar gate")
                    gate = [tag, int(args)]
                gates.append(gate)
            require(gates, "empty literal circuit")
            circuits[name] = gates
    return pairs, circuits


def mul(a, b):
    return a[0]*b[0] - a[1]*b[1], a[0]*b[1] + a[1]*b[0]


def add(a, b):
    return a[0] + b[0], a[1] + b[1]


def rotate(z, p):
    a, b = z
    return ((a, b), (-b, a), (-a, -b), (b, -a))[p % 4]


def normalize(vector, exponent):
    vector = {x: z for x, z in vector.items() if z != ZERO}
    while exponent and all(a % 2 == 0 and b % 2 == 0 for a, b in vector.values()):
        vector = {x: (a // 2, b // 2) for x, (a, b) in vector.items()}
        exponent -= 1
    return vector, exponent


def packed_column(vector):
    v, e = normalize(*vector)
    return [e, [[x, *v[x]] for x in sorted(v)]]


def assert_column(actual, expected, context):
    a, b = normalize(*actual), normalize(*expected)
    if a != b:
        x = next((x for x in range(N)
                  if tuple(c * 2**b[1] for c in a[0].get(x, ZERO))
                  != tuple(c * 2**a[1] for c in b[0].get(x, ZERO))), None)
        raise ValueError(f"operator mismatch: {context}; output={x}")


# Literal evaluator: row-mask pullbacks and term-by-term gate application.
def literal_mv(rows, x):
    return sum(((r & x).bit_count() % 2) << i for i, r in enumerate(rows))


def literal_q(rows, linear, x):
    return (sum(linear[i] for i in range(9) if (x >> i) & 1)
            + 2 * sum(((rows[i] >> (i + 1)) & (x >> (i + 1))).bit_count()
                      for i in range(9) if (x >> i) & 1)) % 4


def adjoint(circuit):
    out = []
    for g in reversed(circuit):
        if g[0] == "pm":
            out.append(["pm", g[2], g[1]])
        elif g[0] == "dg":
            out.append(["dg", g[1], [(-a) % 4 for a in g[2]]])
        elif g[0] == "cg":
            out.append(["cg", g[1], not g[2]])
        elif g[0] == "ph":
            out.append(["ph", (-g[1]) % 4])
        else:
            out.append(copy.deepcopy(g))
    return out


def compile_literal(circuit):
    out = []
    for g in circuit:
        if g[0] == "pm":
            require(len(g[1]) == len(g[2]) == 9, "bad permutation shape")
            forward = [literal_mv(g[1], x) for x in range(N)]
            backward = [literal_mv(g[2], x) for x in range(N)]
            require(sorted(forward) == list(range(N)) and
                    all(backward[forward[x]] == x for x in range(N)), "bad permutation inverse")
            out.append(("pull", backward))
        elif g[0] == "dg":
            require(len(g[1]) == len(g[2]) == 9, "bad diagonal shape")
            out.append(("phase", [literal_q(g[1], g[2], x) for x in range(N)]))
        elif g[0] == "xg":
            require(0 <= g[1] < N, "bad translation")
            out.append(("pull", [x ^ g[1] for x in range(N)]))
        elif g[0] == "ph":
            out.append(("phase", [g[1] % 4] * N))
        elif g[0] == "cg":
            require(0 <= g[1] < N and type(g[2]) is bool, "bad C gate")
            out.append(("C", (g[1], 1 if g[2] else -1)))
        else:
            raise ValueError("unknown gate")
    return out


def run_literal(compiled, basis):
    vec, exponent = {basis: (1, 0)}, 0
    for tag, data in compiled:
        if tag == "pull":
            vec = {x: vec[y] for x, y in enumerate(data) if y in vec}
        elif tag == "phase":
            vec = {x: rotate(z, data[x]) for x, z in vec.items()}
        else:
            q, sign = data
            result = {}
            for x in vec.keys() | {x ^ q for x in vec}:
                a, b = vec.get(x, ZERO)
                c, d = vec.get(x ^ q, ZERO)
                z = (a - sign*b + c + sign*d, b + sign*a + d - sign*c)
                if z != ZERO:
                    result[x] = z
            vec, exponent = result, exponent + 1
    return normalize(vec, exponent)


# Independent kernels: enumerate charts by XORing columns, without producer
# Gaussian elimination; phases sum over pairs of set coordinates.
def coordinate_chart(frame):
    require(len(set(frame)) == len(frame) and all(0 < u < N for u in frame), "invalid frame vectors")
    columns, image = [], [0]
    for u in list(frame) + [2**i for i in range(9)]:
        if u not in image:
            columns.append(u)
            image += [v ^ u for v in image]
    require(len(columns) == 9 and len(image) == N and len(set(image)) == N, "incomplete chart")
    require(columns[:len(frame)] == list(frame), "dependent frame")
    coordinate = [0] * N
    for z, x in enumerate(image):
        coordinate[x] = z
    inverse_columns = [coordinate[2**i] for i in range(9)]
    phases = []
    for x in range(N):
        bits = [i for i in range(9) if x & 2**i]
        linear = sum(1 - inverse_columns[i].bit_count() % 2 for i in bits)
        cross = sum((inverse_columns[i] & inverse_columns[j]).bit_count() % 2
                    for pos, i in enumerate(bits) for j in bits[pos+1:])
        phases.append((linear + 2 * cross) % 4)
    return image, coordinate, phases


def gaussian_power(z, n):
    out = (1, 0)
    for _ in range(n):
        out = mul(out, z)
    return out


def fourier_weights(rank, inverse=False):
    sign = -1 if inverse else 1
    return [mul(gaussian_power((1, sign), rank - w),
                gaussian_power((1, -sign), w)) for w in range(rank + 1)]


def frame_kernel(frame, inverse=False):
    rank = len(frame)
    image, coordinate, phases = coordinate_chart(frame)
    weights = fourier_weights(rank, inverse)

    def column(x):
        vec = {}
        for delta in range(2**rank):
            y = image[coordinate[x] ^ delta]
            vec[y] = mul(UNITS[(phases[y] - phases[x]) % 4], weights[delta.bit_count()])
        return normalize(vec, rank)

    return column


def monomial_kernel(record, inverse=False):
    Q, linear, rows, offset, phase = record
    require(len(Q) == len(linear) == len(rows) == 9, "bad monomial shape")
    require(all(0 <= x < N for x in Q + rows) and 0 <= offset < N, "monomial mask out of range")
    columns = [sum(((rows[j] // 2**i) % 2) * 2**j for j in range(9)) for i in range(9)]
    images, factors = [], []
    for x in range(N):
        bits = [i for i in range(9) if x & 2**i]
        y = offset
        for i in bits:
            y ^= columns[i]
        q = phase + sum(linear[i] for i in bits)
        q += 2 * sum((Q[i] // 2**j) % 2 for k, i in enumerate(bits) for j in bits[k+1:])
        images.append(y)
        factors.append(UNITS[q % 4])
    require(sorted(images) == list(range(N)), "noninvertible monomial")
    if inverse:
        preimage = [0] * N
        for x, y in enumerate(images):
            preimage[y] = x
        return lambda y: ({preimage[y]: (factors[preimage[y]][0], -factors[preimage[y]][1])}, 0)
    return lambda x: ({images[x]: factors[x]}, 0)


def fourier_kernel(rank=7, inverse=False):
    weights = fourier_weights(rank, inverse)
    return lambda x: normalize({x ^ d: weights[d.bit_count()] for d in range(2**rank)}, rank)


def compose_columns(first, second, x):
    av, ae = first(x)
    rows = [(a, second(y)) for y, a in av.items()]
    exponent = max((ae + be for _, (_, be) in rows), default=0)
    out = {}
    for a, (bv, be) in rows:
        scale = 2**(exponent - ae - be)
        for z, b in bv.items():
            c = mul(a, b)
            out[z] = add(out.get(z, ZERO), (scale*c[0], scale*c[1]))
    return normalize(out, exponent)


def composed(*operators):
    def column(x):
        def step(k, y):
            if k == 0:
                return operators[0](y)
            return compose_columns(lambda z: step(k-1, z), operators[k], y)
        return step(len(operators)-1, x)
    return column


def source_subject(root=ROOT):
    module = types.ModuleType("hpe_binding_source_subject")
    sys.modules[module.__name__] = module
    exec(compile((root / CLIFFORD).read_text(encoding="utf-8"), CLIFFORD, "exec"), module.__dict__)
    # Extract the pure decoder only; do not execute unrelated path/env setup.
    tree = ast.parse((root / ADAPTERS).read_text(encoding="utf-8"))
    functions = [node for node in tree.body if isinstance(node, ast.FunctionDef)
                 and node.name == "monomial_op"]
    require(len(functions) == 1, "source monomial decoder inventory")
    namespace = dict(module.__dict__, n=9)
    exec(compile(ast.Module(body=functions, type_ignores=[]), ADAPTERS, "exec"), namespace)
    return module, namespace["monomial_op"]


def source_circuit(circuit, source):
    out = []
    for g in circuit:
        if g[0] == "P":
            out.append(["pm", list(g[1]), list(source.inv(g[1], 9))])
        elif g[0] == "D":
            out.append(["dg", list(g[1]), list(g[2])])
        elif g[0] == "C":
            require(g[2] in (-1, 1), "source C sign")
            out.append(["cg", g[1], g[2] == 1])
        elif g[0] == "X":
            out.append(["xg", g[1]])
        elif g[0] == "phase":
            out.append(["ph", g[1]])
        else:
            raise ValueError("unknown source gate")
    return out


def source_record(mono):
    return dict(zip(("quadratic_rows", "linear_Z4", "matrix_rows", "offset", "phase"), mono, strict=True))


def compare_operator(name, circuit, oracle, source_op=None):
    compiled = compile_literal(circuit)
    fingerprint, nonzero, denominators = hashlib.sha256(), 0, set()
    for x in range(N):
        expected = oracle(x)
        assert_column(run_literal(compiled, x), expected, f"{name}, input={x}")
        if source_op is not None:
            vec, exponent = source_op.zero_state(x)
            assert_column(({i: z for i, z in enumerate(vec) if z != ZERO}, exponent),
                          expected, f"source {name}, input={x}")
        fingerprint.update((canonical_json(packed_column(expected)) + "\n").encode())
        v, e = normalize(*expected)
        nonzero += len(v)
        denominators.add(e)
    return {"name": name, "columns": N, "entries": N*N, "nonzero_entries": nonzero,
            "denominator_exponents": sorted(denominators), "matrix_sha256": fingerprint.hexdigest(),
            "source_executor_checked": source_op is not None}


def first_difference(circuit, oracle):
    compiled = compile_literal(circuit)
    for x in range(N):
        actual, expected = run_literal(compiled, x), oracle(x)
        if normalize(*actual) != normalize(*expected):
            a, ae = normalize(*actual)
            b, be = normalize(*expected)
            y = next(y for y in range(N)
                     if tuple(v * 2**be for v in a.get(y, ZERO))
                     != tuple(v * 2**ae for v in b.get(y, ZERO)))
            return {"input": x, "output": y, "actual": [*a.get(y, ZERO), ae],
                    "expected": [*b.get(y, ZERO), be]}
    raise ValueError("semantic mutation was not rejected")


def semantic_controls(pairs, circuits):
    controls = []
    for i, (_, _, L, R) in enumerate(pairs, 1):
        expected = composed(monomial_kernel(R), fourier_kernel(), monomial_kernel(L))
        base, mutants = circuits[f"rhsLit{i}"], {}
        v = copy.deepcopy(base); v[-1][1] = (v[-1][1] + 1) % 4
        mutants["global_phase"] = v
        v = copy.deepcopy(base)
        k = next(k for k, g in enumerate(v) if g[0] == "xg"); v[k][1] ^= 1
        mutants["translation"] = v
        v = copy.deepcopy(base)
        k = next(k for k, g in enumerate(v) if g[0] == "pm"); v[k][1], v[k][2] = v[k][2], v[k][1]
        mutants["permutation_direction"] = v
        v = copy.deepcopy(base)
        k = next(k for k, g in enumerate(v) if g[0] == "dg"); v[k][2][0] = (v[k][2][0] + 2) % 4
        mutants["input_character"] = v
        v = copy.deepcopy(base)
        k = next(k for k, g in enumerate(v) if g[0] == "cg"); v[k][2] = not v[k][2]
        mutants["C_sign"] = v
        v = copy.deepcopy(base)
        k = next(k for k, g in enumerate(v) if g[0] == "cg"); v[k][1] = 128
        mutants["spectator_axis"] = v
        mutants["sides_swapped"] = (copy.deepcopy(circuits[f"wL{i}"])
                                      + [["cg", 2**k, True] for k in range(7)]
                                      + copy.deepcopy(circuits[f"wR{i}"]))
        mutants["reversed_order"] = list(reversed(copy.deepcopy(base)))
        mutants["entrance_not_inverted"] = circuits[f"fE{i}"] + circuits[f"fU{i}"]
        for name, mutant in mutants.items():
            controls.append({"pair": i, "mutation": name, "witness": first_difference(mutant, expected)})
    return controls


def audit(root=ROOT):
    sources = check_sources(root)
    pairs, circuits = literal_data((root / EXACT).read_text(encoding="utf-8"))
    source, decoder = source_subject(root)
    checks, composition, mapping = [], [], []
    for i, (E, U, L, R) in enumerate(pairs, 1):
        require(E[0] in coordinate_chart(U)[0][:256], "entrance not contained in terminal")
        objects = [("fE", E, source.canonical_frame(9, tuple(E)), frame_kernel),
                   ("fU", U, source.canonical_frame(9, tuple(U)), frame_kernel),
                   ("wL", L, decoder(source_record(L)), monomial_kernel),
                   ("wR", R, decoder(source_record(R)), monomial_kernel)]
        for prefix, data, op, kernel in objects:
            name = f"{prefix}{i}"
            require(source_circuit(op.circuit, source) == circuits[name],
                    "source constructor differs from Lean literal: " + name)
            mapping.append({"name": name, "literal_gates": len(circuits[name]),
                            "literal_sha256": digest(circuits[name])})
            for inverse in (False, True):
                c = adjoint(circuits[name]) if inverse else circuits[name]
                sop = op.adjoint() if inverse else op
                checks.append(compare_operator(name + ("_inverse" if inverse else ""),
                                               c, kernel(data, inverse), sop))
        require(circuits[f"lhsLit{i}"] == adjoint(circuits[f"fE{i}"]) + circuits[f"fU{i}"],
                "lhs literal composition")
        require(circuits[f"rhsLit{i}"] == circuits[f"wR{i}"]
                + [["cg", 2**k, True] for k in range(7)] + circuits[f"wL{i}"], "rhs literal composition")
        lhs = composed(frame_kernel(E, True), frame_kernel(U))
        rhs = composed(monomial_kernel(R), fourier_kernel(), monomial_kernel(L))
        left = compare_operator(f"lhsLit{i}", circuits[f"lhsLit{i}"], lhs)
        right = compare_operator(f"rhsLit{i}", circuits[f"rhsLit{i}"], rhs)
        require(left["matrix_sha256"] == right["matrix_sha256"], "factorization digest mismatch")
        # Acceptance uses exact equality too; hashes are only compact receipts.
        for x in range(N):
            assert_column(lhs(x), rhs(x), f"pair{i} exact factorization input={x}")
        composition.append({"pair": i, "entrance": E, "terminal": U, "left": left, "right": right})
    controls = semantic_controls(pairs, circuits)
    return {"schema_version": 1, "status": "PASS_HPE_LEAN_SEMANTIC_BINDING",
            "kind": "independent finite semantic binding audit", "source_inputs": sources,
            "pairs": 3, "primitive_operator_checks": checks, "literal_bindings": mapping,
            "factorizations": composition, "semantic_controls": controls,
            "new_lean_build": False, "new_kappa": False}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-receipt", type=Path,
                        help="create a receipt exclusively; normal replay is read-only")
    parser.add_argument("--receipt", type=Path, default=PACKAGE / "RESULT.json")
    args = parser.parse_args(argv)
    if args.write_receipt:
        require(not args.write_receipt.exists(), "refusing to overwrite receipt")
    result = audit()
    if args.write_receipt:
        with args.write_receipt.open("x", encoding="utf-8") as handle:
            handle.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        validate_receipt(args.receipt, result)
    count = len(result["primitive_operator_checks"])
    print(f"PASS_HPE_LEAN_SEMANTIC_BINDING pairs=3 operators={count} "
          f"operator_columns={count*N} factorizations=3 controls={len(result['semantic_controls'])} "
          "no_new_lean_build no_new_kappa")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, SyntaxError) as exc:
        raise SystemExit("FAIL_HPE_LEAN_SEMANTIC_BINDING: " + str(exc)) from exc
