#!/usr/bin/env python3
"""Exact two-cut audit of the pinned balanced dirty dispatcher.

Hanson Sun (@bbMisk), with substantial OpenAI Codex assistance. Apache-2.0.
The finite free-algebra census supports the parametric proof in README.md;
it is not a rounded-kernel execution or a formal multiplication proof.
"""
import argparse
import ast
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
DISPATCHER = "research/dirty-cubic-precision/vendor/628/dirty.py"
SEED = 64
MARKER = "PASS_DIRTY_INTERVAL_PROPAGATOR_AUDIT"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def bindings(root=ROOT):
    """Live inputs are authenticated; historical provenance is checked by the hook."""
    sources = json.loads((PACKAGE / "SOURCES.json").read_text())
    checked = []
    for row in sources["files"]:
        if row["usage"] != "input":
            continue
        data = (root / row["path"]).read_bytes()
        require(hashlib.sha256(data).hexdigest() == row["sha256"],
                "source SHA256 drift: " + row["path"])
        blob = b"blob " + str(len(data)).encode() + b"\0" + data
        require(hashlib.sha1(blob).hexdigest() == row["git_blob"],
                "source Git-blob drift: " + row["path"])
        checked.append({key: row[key] for key in ("path", "git_blob", "sha256")})
    require(DISPATCHER in {r["path"] for r in checked}, "dispatcher is not pinned")
    return {"base_commit": sources["base_commit"], "inputs": checked}


def emit(n, sign=1):
    """Independent iterative expansion; ports 0=x, 1=y, 2+d=scratch[d]."""
    require(type(n) is int and n > 0, "positive factor count")
    require(sign in (-1, 1), "signed word")
    pending = [(0, n, 0, 1, 0, sign)]
    out = []
    while pending:
        lo, count, src, dst, depth, direction = pending.pop()
        if count == 1:
            out.append((src, dst, lo, direction))
            continue
        left = count // 2
        middle = depth + 2
        u = (lo, left, src, middle, depth + 1)
        v = (lo + left, count - left, middle, dst, depth + 1)
        blocks = [(*u, 1), (*v, 1), (*u, -1), (*v, -1)]
        if direction == -1:
            blocks = [(*b[:-1], -b[-1]) for b in reversed(blocks)]
        pending.extend(reversed(blocks))
    return out


def source_emitter(source):
    """Execute only the byte-pinned compose AST, recording each literal leaf.

    No top-level predecessor imports, analytic factors or numerical routines
    are executed. All compose admission checks run with distinct unit arrays.
    """
    tree = ast.parse(source)
    functions = [node for node in tree.body
                 if isinstance(node, ast.FunctionDef) and node.name == "compose"]
    require(len(functions) == 1, "one source compose function required")
    unit = ast.Module(body=functions, type_ignores=[])
    code = compile(ast.fix_missing_locations(unit), DISPATCHER, "exec")

    def run(n, sign):
        arrays = [[0] for _ in range((n - 1).bit_length() + 2)]
        identities = {id(array): i for i, array in enumerate(arrays)}
        out = []

        def leaf(x, y, factor, phases, beta, bits, direction, sgn, stats):
            out.append((identities[id(x)], identities[id(y)], factor, sgn))

        namespace = {"c": SimpleNamespace(need=require, norm2=lambda x: x * x),
                     "leaf": leaf}
        exec(code, namespace)
        namespace["compose"](arrays[0], arrays[1], list(range(n)), arrays[2:],
                             [1], F(1, 2), 64, 1, sign)
        return out

    return run


def symbolic_identity(size):
    return [[{(): 1} if i == j else {} for j in range(size)] for i in range(size)]


def symbolic_step(matrix, operation):
    src, dst, factor, sign = operation
    require(src != dst, "a shear has distinct ports")
    for column, poly in enumerate(matrix[src]):
        target = matrix[dst][column]
        for word, coefficient in poly.items():
            new = (factor,) + word
            target[new] = target.get(new, 0) + sign * coefficient
            if target[new] == 0:
                del target[new]


def symbolic_interval(operations, start, end, size):
    matrix = symbolic_identity(size)
    for operation in operations[start:end]:
        symbolic_step(matrix, operation)
    return matrix


def ordered(word):
    return all(a > b for a, b in zip(word, word[1:]))


def polynomial(poly):
    return [[list(word), coefficient] for word, coefficient in sorted(poly.items())]


def census():
    rows = []
    first_general = None
    first_leaf = None
    for n in range(1, 9):
        size = (n - 1).bit_length() + 2
        item = dict(factors=n, leaves=len(emit(n)), intervals=0,
                    leaf_supported_intervals=0, unordered_intervals=0,
                    unordered_leaf_supported_intervals=0, max_row_coefficient_l1=0,
                    max_degree=0, repeated_factor_terms=0, nonunit_coefficients=0)
        for sign in (1, -1):
            operations = emit(n, sign)
            for start in range(len(operations)):
                matrix = symbolic_identity(size)
                injection = operations[start - 1][1] if start else None
                for end in range(start + 1, len(operations) + 1):
                    symbolic_step(matrix, operations[end - 1])
                    item["intervals"] += 1
                    item["leaf_supported_intervals"] += injection is not None
                    bad = False
                    leaf_bad = False
                    for row_index, row in enumerate(matrix):
                        item["max_row_coefficient_l1"] = max(
                            item["max_row_coefficient_l1"],
                            sum(abs(c) for p in row for c in p.values()))
                        for column, poly in enumerate(row):
                            for word, coefficient in poly.items():
                                item["max_degree"] = max(item["max_degree"], len(word))
                                item["repeated_factor_terms"] += len(set(word)) < len(word)
                                item["nonunit_coefficients"] += abs(coefficient) != 1
                                if not ordered(word):
                                    bad = True
                                    leaf_bad |= column == injection
                                    witness = dict(factors=n, sign=sign, start=start,
                                                   end=end, row=row_index, column=column,
                                                   polynomial=polynomial(poly))
                                    if first_general is None:
                                        first_general = witness
                                    if first_leaf is None and column == injection:
                                        first_leaf = witness
                    item["unordered_intervals"] += bad
                    item["unordered_leaf_supported_intervals"] += leaf_bad
        rows.append(item)
    require(first_general["factors"] == 4, "first arbitrary-input order failure")
    require(first_leaf["factors"] == 7, "first leaf-supported order failure")
    return {"domain": "n=1..8; both signs; every 0<=start<end<=leaf_count",
            "intervals": sum(r["intervals"] for r in rows),
            "leaf_supported_intervals": sum(r["leaf_supported_intervals"] for r in rows),
            "rows": rows, "first_arbitrary_input": first_general,
            "first_leaf_destination_input": first_leaf}


def identity(n):
    return [[F(i == j) for j in range(n)] for i in range(n)]


def zero(n):
    return [[F(0) for _ in range(n)] for _ in range(n)]


def multiply(a, b):
    return [[sum((x * y for x, y in zip(row, column)), F(0))
             for column in zip(*b)] for row in a]


def inverse(a):
    """Gauss-Jordan inverse, independent of the shear word."""
    n = len(a)
    matrix = [list(row) + unit for row, unit in zip(a, identity(n))]
    for column in range(n):
        pivot = next((i for i in range(column, n) if matrix[i][column]), None)
        require(pivot is not None, "singular matrix")
        matrix[column], matrix[pivot] = matrix[pivot], matrix[column]
        scale = matrix[column][column]
        matrix[column] = [v / scale for v in matrix[column]]
        for i in range(n):
            if i != column:
                scale = matrix[i][column]
                matrix[i] = [a - scale * b for a, b in zip(matrix[i], matrix[column])]
    require([row[:n] for row in matrix] == identity(n), "inverse residual")
    return [row[n:] for row in matrix]


def norm(matrix):
    return max(sum(abs(x) for x in row) for row in matrix)


def shear(operation, factors, ports):
    src, dst, factor, sign = operation
    matrix = identity(2 * ports)
    for i in range(2):
        for j in range(2):
            matrix[2 * dst + i][2 * src + j] += sign * factors[factor][i][j]
    return matrix


def dense_word(operations, factors, ports):
    matrix = identity(2 * ports)
    for operation in operations:
        matrix = multiply(shear(operation, factors, ports), matrix)
    return matrix


def evaluate(symbolic, factors):
    ports = len(symbolic)
    matrix = zero(2 * ports)
    for i, row in enumerate(symbolic):
        for j, poly in enumerate(row):
            block = zero(2)
            for word, coefficient in poly.items():
                value = identity(2)
                for k in word:
                    value = multiply(value, factors[k])
                for a in range(2):
                    for b in range(2):
                        block[a][b] += coefficient * value[a][b]
            for a in range(2):
                for b in range(2):
                    matrix[2 * i + a][2 * j + b] = block[a][b]
    return matrix


def family(n, m):
    require(n in (4, 7) and m >= 1, "declared witness family")
    factors = [identity(2) for _ in range(n)]
    factors[1] = [[F(0), F(m)], [-F(1, m), F(0)]]
    factors[2 if n == 4 else 4] = [[F(1, m), F(0)], [F(0), F(m)]]
    return factors


def ordered_subsets(factors):
    products = [identity(2)]
    for factor in factors:
        products += [multiply(factor, p) for p in products]
    return products


def as_strings(matrix):
    return [[str(v) for v in row] for row in matrix]


def example(n, m):
    operations = emit(n)
    ports = (n - 1).bit_length() + 2
    start, end, port = (5, 9, 2) if n == 4 else (13, 27, 4)
    factors = family(n, m)
    products = ordered_subsets(factors)
    require(max(map(norm, products)) == m, "ordered-subset budget")
    for factor in factors:
        require(factor[0][0] * factor[1][1] - factor[0][1] * factor[1][0] == 1,
                "all factors have determinant one")
    direct = dense_word(operations[start:end], factors, ports)
    symbolic = symbolic_interval(operations, start, end, ports)
    require(direct == evaluate(symbolic, factors), "free algebra vs dense product")
    p_start = dense_word(operations[:start], factors, ports)
    p_end = dense_word(operations[:end], factors, ports)
    require(direct == multiply(p_end, inverse(p_start)), "two-cut quotient identity")
    require(multiply(direct, inverse(direct)) == identity(2 * ports), "interval invertible")
    block = [row[2 * port:2 * port + 2] for row in direct[2 * port:2 * port + 2]]
    expected = [[F(1), -F(m * m)], [F(1, m * m), F(1)]]
    require(block == expected, "parametric I-JD block")
    require(norm(block) == 1 + m * m, "quadratic block norm")
    require((operations[start - 1][1] == port) == (n == 7), "actual leaf destination")
    full = dense_word(operations, factors, ports)
    expected_full = identity(2 * ports)
    total = products[-1]
    for i in range(2):
        for j in range(2):
            expected_full[2 + i][j] += total[i][j]
    require(full == expected_full and norm(full) == 2, "complete word and restored dirt")
    vector = [[F(0)] for _ in range(2 * ports)]
    vector[2 * port][0], vector[2 * port + 1][0] = F(1), F(-1)
    result = multiply(direct, vector)
    require(max(abs(row[0]) for row in result) == 1 + m * m, "attaining injection")
    return {"factors": n, "M": m, "ordered_subsets": len(products),
            "G": str(m), "start": start, "end": end, "port": port,
            "preceding_leaf": list(operations[start - 1]),
            "leaf_destination_supported": n == 7,
            "operations": [list(op) for op in operations[start:end]],
            "diagonal_block": as_strings(block), "block_norm": str(norm(block)),
            "injected_vector": ["1", "-1"],
            "result_by_port": [[str(row[0]) for row in result[2*i:2*i+2]]
                               for i in range(ports)],
            "complete_word_norm": str(norm(full)),
            "complete_factor_product": as_strings(total)}


def literal_injection(operations, factors, ports, start, end, port):
    """Independent vector interpreter, comparing two dirty trajectories."""
    initial = [[F((i * 7 + SEED) % 11 - 5), F((i * 3 + SEED) % 7 - 3)]
               for i in range(ports)]
    clean = [row[:] for row in initial]
    noisy = [row[:] for row in initial]

    def apply(state, operation):
        src, dst, k, sign = operation
        values = [sum(factors[k][i][j] * state[src][j] for j in range(2)) for i in range(2)]
        state[dst] = [a + sign * b for a, b in zip(state[dst], values)]

    for i, operation in enumerate(operations[:end]):
        if i == start:
            noisy[port][0] += 1
            noisy[port][1] -= 1
        apply(clean, operation)
        apply(noisy, operation)
    difference = [[a - b for a, b in zip(row1, row2)] for row1, row2 in zip(noisy, clean)]
    return as_strings(difference)


def controls():
    operations = emit(7)
    factors = family(7, SEED)
    d, j = factors[4], factors[1]
    jd, dj = multiply(j, d), multiply(d, j)
    require(jd != dj and norm(jd) == SEED ** 2 and norm(dj) == 1,
            "order and commutation controls")
    results = {"reversed_product_exceeds_ordered_budget": norm(jd) > SEED,
               "common_operator_commutation_hypothesis_fails": jd != dj,
               "all_permuted_subsets_hypothesis_fails": norm(jd) > SEED,
               "four_factor_input_is_not_a_leaf_destination": emit(4)[4][1] != 2}
    before = dense_word(operations[13:26], factors, 5)
    block = [row[8:10] for row in before[8:10]]
    results["omitting_final_cross_subtree_leaf_removes_quadratic_block"] = block == identity(2)
    corrupted = operations[:]
    src, dst, k, sign = corrupted[26]
    corrupted[26] = (src, dst, k, -sign)
    wrong = dense_word(corrupted[13:27], factors, 5)
    good = dense_word(operations[13:27], factors, 5)
    results["wrong_sign_changes_interval_identity"] = wrong != good
    require(all(results.values()), "a mathematical control failed")
    return results


def calculate():
    source_pins = bindings()
    actual = source_emitter((ROOT / DISPATCHER).read_text())
    count_domain = list(range(1, 9)) + [9, 12, 16, 31, SEED]
    words = []
    for n in count_domain:
        for sign in (1, -1):
            operations = emit(n, sign)
            require(operations == actual(n, sign), "pinned dispatcher word mismatch")
            require(emit(n, -sign) == [(a, b, c, -s) for a, b, c, s in reversed(operations)],
                    "literal signed inverse word")
            words.append({"factors": n, "sign": sign, "leaves": len(operations),
                          "word_sha256": digest(operations)})
    finite = census()
    sizes = [1, 2, 3, 4, 7, 16, SEED, 257]
    evidence = []
    for n in (4, 7):
        for m in sizes:
            witness = example(n, m)
            literal = literal_injection(emit(n), family(n, m),
                                        (n - 1).bit_length() + 2,
                                        witness["start"], witness["end"], witness["port"])
            require(literal == witness["result_by_port"], "two dirty vector trajectories")
            evidence.append({"factors": n, "M": m, "G": witness["G"],
                             "block_norm": witness["block_norm"],
                             "ordered_subsets": witness["ordered_subsets"]})
    witnesses = [example(n, SEED) for n in (4, 7)]
    return {"status": MARKER, "assignment_seed": SEED, "sources": source_pins,
            "source_word_checks": words, "census": finite,
            "parametric_examples": witnesses, "dense_checks": evidence,
            "controls": controls(),
            "scope": "Generic noncommuting invertible factors; exact local-error transport. "
                     "No actual rounded-leaf failure, common-operator counterexample, "
                     "supplier admission, new kappa or full formal proof."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="create a new receipt, refusing an overwrite")
    args = parser.parse_args()
    result = calculate()
    if args.write:
        with args.write.open("x") as stream:
            stream.write(json.dumps(result, indent=2) + "\n")
    else:
        expected = json.loads((PACKAGE / "CERTIFICATE.json").read_text())
        require(result == expected, "certificate mismatch")
    print(f"{MARKER} intervals={result['census']['intervals']} "
          f"leaf_supported={result['census']['leaf_supported_intervals']} "
          f"dense_cases={len(result['dense_checks'])} controls={len(result['controls'])} "
          f"receipt_sha256={digest(result)}")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError) as error:
        raise SystemExit("FAIL_DIRTY_INTERVAL_PROPAGATOR_AUDIT: " + str(error))
