"""Independent dense reference, exact regression evidence, and negative controls."""
import ast
from fractions import Fraction as F
import hashlib
import itertools
import json
from pathlib import Path
import random
import sys
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import lift


def check(condition, message):
    if not condition:
        raise ValueError(message)


def inverse(matrix):
    """Gauss-Jordan over Q; independent of the cyclic scan/pivot factorization."""
    n = len(matrix)
    rows = [[F(x) for x in row] + [F(i == j) for j in range(n)]
            for i, row in enumerate(matrix)]
    for j in range(n):
        pivot = next(i for i in range(j, n) if rows[i][j])
        rows[j], rows[pivot] = rows[pivot], rows[j]
        scale = rows[j][j]
        rows[j] = [x / scale for x in rows[j]]
        for i in range(n):
            if i != j:
                scale = rows[i][j]
                rows[i] = [x - scale * y for x, y in zip(rows[i], rows[j])]
    return [row[n:] for row in rows]


def factor_matrix(coefficients, direction):
    n = len(coefficients)
    matrix = [[F(i == j) for j in range(n)] for i in range(n)]
    for i, b in enumerate(coefficients):
        matrix[i][(i - direction) % n] -= b
    return inverse(matrix)


def matvec(matrix, vector):
    return [sum(a * b for a, b in zip(row, vector)) for row in matrix]


def rational_word(word, vector):
    vector = list(map(F, vector))
    for destination, source, coefficient in word:
        vector[destination] += coefficient * vector[source]
    return vector


def delta(coefficients):
    product = F(1)
    for b in coefficients:
        product *= b
    return 1 - product


def expected_column(coefficients, direction, column):
    n = len(coefficients)
    if column == n:
        return [F(0)] * n + [delta(coefficients)]
    return [row[column] for row in factor_matrix(coefficients, direction)] + [F(0)]


def ceil_fraction(x):
    return (x.numerator + x.denominator - 1) // x.denominator


def payload_digest(items):
    data = json.dumps(items, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(data).hexdigest()


def pinned_sources():
    source = json.loads((HERE / "SOURCES.json").read_text())
    for item in source["consumed"]:
        data = (HERE / item["local_path"]).read_bytes()
        check(hashlib.sha256(data).hexdigest() == item["sha256"], "pinned source drift")
    check(source["base_commit"] == "66849e1475c930fd7732b1a0067ffee7e1e95f60", "base pin")
    return source


def original_dispatcher_counts():
    """Execute only the pinned compose definition, with a counting leaf stub.

    This checks original dispatcher counts, not the predecessor's numerical leaf.
    """
    tree = ast.parse((HERE / "vendor/pr628-dirty.py").read_text())
    definition = next(node for node in tree.body if isinstance(node, ast.FunctionDef)
                      and node.name == "compose")
    calls = []

    def leaf(*arguments):
        calls.append(1)

    namespace = {"c": SimpleNamespace(need=check, norm2=lambda _: 1), "leaf": leaf}
    exec(compile(ast.Module(body=[definition], type_ignores=[]), "pinned-compose", "exec"), namespace)
    rows = []
    for n in range(1, 129):
        calls.clear()
        scratch = [[0] for _ in range((n - 1).bit_length())]
        namespace["compose"]([0], [0], [None] * n, scratch, [1], F(1, 2), 128, 1)
        h = n.bit_length() - 1
        closed = (1 << h) * (3 * n - (1 << (h + 1)))
        check(len(calls) == closed, "predecessor dispatcher count")
        rows.append([n, closed])
    return rows


def factor_checks():
    alphabet = (F(-1, 2), F(-1, 4), F(0), F(1, 4), F(1, 2))
    count, columns, rounded, maximum = 0, 0, 0, F(0)
    digest_rows = []
    for length in range(1, 5):
        for coefficients in itertools.product(alphabet, repeat=length):
            for direction in (-1, 1):
                word = lift.factor_word(coefficients, direction)
                matrix = factor_matrix(coefficients, direction)
                for column in range(length + 1):
                    vector = [F(i == column) for i in range(length + 1)]
                    expected = [row[column] for row in matrix] + [F(0)] if column < length else [F(0)] * length + [delta(coefficients)]
                    check(rational_word(word, vector) == expected, "stabilized full-column identity")
                    columns += 1
                for magnitude in (0, 7, -(1 << 220)):
                    data = [magnitude + (i * 3 % 11) - 5 for i in range(length)]
                    helper = [magnitude - 19]
                    original, initial_helper = data[:], helper[:]
                    exact = matvec(matrix, data) + [delta(coefficients) * helper[0]]
                    lift.run_word(data, helper, word)
                    error = max(abs(x - y) for x, y in zip(data + helper, exact))
                    maximum = max(maximum, error)
                    check(error <= 5, "uniform factor rounding error")
                    digest_rows.append(data + helper)
                    lift.run_word(data, helper, word, True)
                    check(data == original and helper == initial_helper, "exact factor inverse")
                    rounded += 1
                count += 1
    return {"factors": count, "full_columns": columns, "rounded_cases": rounded,
            "max_error": str(maximum), "output_sha256": payload_digest(digest_rows)}


def fixture(n, length, rng):
    alphabet = (F(-1, 2), F(-3, 8), F(-1, 4), F(1, 4), F(3, 8), F(1, 2))
    return [(tuple(rng.choice(alphabet) for _ in range(length)), rng.choice((-1, 1)))
            for _ in range(n)]


def product_checks():
    rng = random.Random(55)
    count, rows, largest = 0, [], None
    for n in (1, 2, 3, 5, 8, 16, 55):
        maximum = F(0)
        for length in (1, 2, 3, 5, 8):
            factors = fixture(n, length, rng)
            matrices = [factor_matrix(b, d) for b, d in factors]
            for bits in (0, 16, 80):
                source = [((i * 7 % 13) - 6) * (1 << bits) for i in range(length)]
                expected = source[:]
                for matrix in matrices:
                    expected = matvec(matrix, expected)
                for dirt in (0, 7, -(1 << 220)):
                    target = [19 - 3 * i for i in range(length)]
                    data = [dirt + i * i - 5 for i in range(length)]
                    helper = [dirt - 17]
                    original = [source[:], target[:], data[:], helper[:]]
                    stats = lift.add_product(source, target, data, helper, factors)
                    error = max(abs(y - y0 - wanted) for y, y0, wanted in zip(target, original[1], expected))
                    maximum = max(maximum, error)
                    check(error <= lift.error_bound(n), "complete product error")
                    check([source, data, helper] == [original[0], original[2], original[3]], "product dirty restoration")
                    check(stats["coordinate_updates"] == 8 * n * (length + 1) + 4 * length, "complete operation bill")
                    net = [a - b for a, b in zip(target, original[1])]
                    lift.add_product(source, target, data, helper, factors, -1)
                    check([source, target, data, helper] == original, "negative product cancellation")
                    rows.append([n, length, bits, str(dirt), net])
                    count += 1
                    if (n, length, bits, dirt) == (55, 5, 80, 7):
                        largest = {"factors": [[list(map(str, b)), d] for b, d in factors],
                                   "grid_bits": bits, "increment": net, "stats": stats,
                                   "error_ceiling_grid_units": ceil_fraction(error),
                                   "uniform_error_bound_grid_units": lift.error_bound(n)}
        rows.append([n, "max_error_ceiling", ceil_fraction(maximum)])
    return {"cases": count, "output_sha256": payload_digest(rows), "seed55_fixture": largest}


def controls():
    coefficients = (F(1, 2), F(-1, 4), F(3, 8), F(-1, 2), F(1, 4))
    word = lift.factor_word(coefficients)
    rejected = []
    for omitted in range(len(word)):
        altered = word[:omitted] + word[omitted + 1:]
        check(any(rational_word(altered, [F(i == c) for i in range(6)]) != expected_column(coefficients, 1, c)
                  for c in range(6)), "ineffective omission control")
        rejected.append("omit_shear_" + str(omitted))
    source, target, data, helper = [1, -2], [7, 9], [-5, 11], [19]
    factors = [((F(1, 2), F(-1, 4)), 1)]
    initial = [source[:], target[:], data[:], helper[:]]

    def reject(name, call):
        try:
            call()
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError("admission control accepted: " + name)
        check([source, target, data, helper] == initial, "rejection mutated inputs")

    reject("source_target_alias", lambda: lift.add_product(source, source, data, helper, factors))
    reject("source_scratch_alias", lambda: lift.add_product(source, target, source, helper, factors))
    reject("target_scratch_alias", lambda: lift.add_product(source, target, target, helper, factors))
    reject("helper_alias", lambda: lift.add_product(source, target, data, source, factors))
    reject("unstable_coefficient", lambda: lift.add_product(source, target, data, helper, [((F(3, 4), F(0)), 1)]))
    reject("float_coefficient", lambda: lift.add_product(source, target, data, helper, [((0.5, F(0)), 1)]))
    reject("empty_factors", lambda: lift.add_product(source, target, data, helper, []))
    reject("unequal_factors", lambda: lift.add_product(source, target, data, helper, factors + [((F(0),), 1)]))
    reject("boolean_sign", lambda: lift.add_product(source, target, data, helper, factors, True))
    reject("invalid_direction", lambda: lift.add_product(source, target, data, helper, [(factors[0][0], 0)]))
    # Noncommuting varying-coefficient factors prevent a silent order substitution.
    a = factor_matrix((F(1, 2), F(1, 4)), 1)
    b = factor_matrix((F(-1, 4), F(1, 2)), 1)
    ab, ba = matvec(a, matvec(b, [1, 0])), matvec(b, matvec(a, [1, 0]))
    check(ab != ba, "factor-order control")
    rejected.append("reversed_factor_order")
    # Direct rounded pivot division is not a permutation; the stabilized pair is.
    collision = [lift.nearest(F(2, 3) * z) for z in (1, 2)]
    check(collision == [1, 1], "pivot collision witness")
    rejected.append("unpaired_pivot_scaling")
    # Omit an inverse pipeline: exact restoration must fail on an explicit state.
    dirty, aux = [5, -7, 3, 2, 11], [-19]
    lift.run_word(dirty, aux, word)
    check([dirty, aux] != [[5, -7, 3, 2, 11], [-19]], "missing inverse witness")
    rejected.append("omitted_pipeline_restoration")
    # All 25 small dirt states are examined; rounding need not be dirt independent.
    increments = []
    for dirt, scalar in itertools.product(range(-2, 3), repeat=2):
        out = [0]
        lift.add_product([1], out, [dirt], [scalar], [((F(-1, 2),), 1)])
        increments.append([dirt, scalar, out[0]])
    check(len({row[2] for row in increments}) > 1, "dirt-dependence control")
    return {"rejected": rejected, "noncommuting_ab": list(map(str, ab)),
            "noncommuting_ba": list(map(str, ba)), "pivot_collision": collision,
            "dirt_dependence_all_25_states": increments}


def evidence():
    source = pinned_sources()
    predecessor = original_dispatcher_counts()
    return {"status": "PASS_BALANCED_CYCLIC_LIFT", "assignment_seed": 55,
            "base_commit": source["base_commit"], "predecessor_count_cases": len(predecessor),
            "predecessor_count_sha256": payload_digest(predecessor),
            "comparison_n55": {"original_additive_leaf_calls": dict(predecessor)[55],
                               "original_dirty_arrays": 6, "stabilized_factor_executions": 220,
                               "stabilized_dirty_arrays": 1, "stabilized_dirty_scalars": 1,
                               "units": "different leaf interfaces; not a runtime comparison"},
            "factor_checks": factor_checks(), "product_checks": product_checks(),
            "controls": controls()}


def main():
    check(sys.argv[1:] in ([], ["--write-certificate"]), "usage: verify.py [--write-certificate]")
    actual = evidence()
    output = HERE / "CERTIFICATE.json"
    if sys.argv[1:]:
        output.write_text(json.dumps(actual, indent=2) + "\n")
    else:
        # Canonical JSON distinguishes true from 1 and 1.0 from 1 under -O.
        check(json.dumps(actual, sort_keys=True) == json.dumps(json.loads(output.read_text()), sort_keys=True), "certificate mismatch")
    print("PASS_BALANCED_CYCLIC_LIFT: {} factors; {} full columns; {} rounded factors; {} products; {} controls; n55: 3232 additive leaves vs 220 stabilized factor executions".format(
        actual["factor_checks"]["factors"], actual["factor_checks"]["full_columns"],
        actual["factor_checks"]["rounded_cases"], actual["product_checks"]["cases"],
        len(actual["controls"]["rejected"])))


if __name__ == "__main__":
    main()
