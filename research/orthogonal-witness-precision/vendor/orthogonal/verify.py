"""Check exact witnesses against separate dense and reduced-word oracles.

Prepared by Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""

import argparse
from copy import deepcopy
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import random
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from witness import construct
from check_witness import check
from literal import action, parameters, replay


def require(value, message):
    if not value:
        raise ValueError(message)


def rejected(call):
    try:
        call()
    except (ValueError, TypeError, ZeroDivisionError):
        return
    raise ValueError("invalid case was accepted")


def program(roles=None):
    return {"schema": "inverse-dirty-program/v1", "field": 0,
            "roles": roles or ["x"], "operators": ["A", "B"], "left": [], "right": []}


def apply(dst, a, direction):
    return {"op": "apply", "dst": dst, "operator": a, "direction": direction}


def linear(dst, terms):
    return {"op": "linear", "dst": dst, "terms": terms}


def query(dst, src, a, direction, coefficient):
    return {"op": "query", "dst": dst, "src": src, "operator": a,
            "direction": direction, "coefficient": coefficient}


def dense_inverse(matrix):
    n = len(matrix)
    rows = [row[:] + [Q(i == j) for j in range(n)] for i, row in enumerate(matrix)]
    for col in range(n):
        pivot = next(i for i in range(col, n) if rows[i][col])
        rows[col], rows[pivot] = rows[pivot], rows[col]
        v = rows[col][col]
        rows[col] = [x / v for x in rows[col]]
        for i in range(n):
            if i != col:
                v = rows[i][col]
                rows[i] = [x - v * y for x, y in zip(rows[i], rows[col])]
    return [row[n:] for row in rows]


def matvec(matrix, vector):
    return [sum((a * b for a, b in zip(row, vector)), Q(0)) for row in matrix]


def mm(a, b):
    return [[sum((x * y for x, y in zip(row, col)), Q(0))
             for col in zip(*b)] for row in a]


def determinant(matrix):
    a = [row[:] for row in matrix]
    value = Q(1)
    for j in range(len(a)):
        pivot = next((i for i in range(j, len(a)) if a[i][j]), None)
        if pivot is None:
            return Q(0)
        if pivot != j:
            a[j], a[pivot] = a[pivot], a[j]
            value = -value
        value *= a[j][j]
        for i in range(j + 1, len(a)):
            ratio = a[i][j] / a[j][j]
            a[i] = [x - ratio * y for x, y in zip(a[i], a[j])]
    return value


def dense_replay(p, w):
    n, t = w["dimension"], Q(w["parameter"])
    matrices = {}
    identity = [[Q(i == j) for j in range(n)] for i in range(n)]
    for a in p["operators"]:
        plus, minus = deepcopy(identity), deepcopy(identity)
        for j, label in enumerate(w["word"]):
            if label == a:
                plus[j][j + 1], plus[j + 1][j] = t / 2, -t / 2
                minus[j][j + 1], minus[j + 1][j] = -t / 2, t / 2
        matrix = mm(dense_inverse(minus), plus)
        inverse = dense_inverse(matrix)
        transpose = list(map(list, zip(*matrix)))
        require(inverse == transpose, "inverse must be transpose")
        require(mm(transpose, matrix) == identity, "exact orthogonality")
        require(determinant(matrix) == 1, "special orthogonal determinant")
        matrices[a, 1], matrices[a, -1] = matrix, inverse
    results = []
    for side in ("left", "right"):
        values = [[Q(i == w["input"] and j == n - 1) for j in range(n)]
                  for i in range(len(p["roles"]))]
        for ins in p[side]:
            target = p["roles"].index(ins["dst"])
            old = [v[:] for v in values]
            if ins["op"] == "linear":
                values[target] = [sum((Q(c) * old[p["roles"].index(src)][j]
                                      for src, c in ins["terms"]), Q(0)) for j in range(n)]
            else:
                source = target if ins["op"] == "apply" else p["roles"].index(ins["src"])
                product = matvec(matrices[ins["operator"], ins["direction"]], old[source])
                values[target] = product if ins["op"] == "apply" else [
                    x + Q(ins["coefficient"]) * y for x, y in zip(old[target], product)]
        results.append(values)
    return [[x - y for x, y in zip(a, b)] for a, b in zip(*results)]


def group_difference(p):
    """Expand only the small tests in the free-group basis."""
    finals = []
    for side in ("left", "right"):
        regs = {role: {(i, ()): Q(1)} for i, role in enumerate(p["roles"])}
        for ins in p[side]:
            result = {}
            def add(source, c, letter=None):
                for (i, word), value in source.items():
                    if letter is None:
                        out = word
                    elif word and word[0] == (letter[0], -letter[1]):
                        out = word[1:]
                    else:
                        out = (letter,) + word
                    key = i, out
                    result[key] = result.get(key, Q(0)) + c * value
            dst = ins["dst"]
            if ins["op"] == "linear":
                for src, c in ins["terms"]:
                    add(regs[src], Q(c))
            else:
                src = dst if ins["op"] == "apply" else ins["src"]
                if ins["op"] == "query":
                    add(regs[dst], Q(1))
                c = Q(1) if ins["op"] == "apply" else Q(ins["coefficient"])
                add(regs[src], c, (ins["operator"], ins["direction"]))
            regs[dst] = {key: value for key, value in result.items() if value}
        finals.append(regs)
    return finals[0] != finals[1]


def grid_roots(count):
    p = program(["x", "h"])
    p["left"] = [linear("h", [["x", 1]]), apply("x", "A", 1),
                 linear("x", [["x", 1], ["h", -1]])]
    grid = 4 * count + 3
    for j in range(1, count + 1):
        root = Q(grid + 1 - j, 4 * grid)
        alpha = 2 * (1 - root**2 / 4) / (1 + root**2 / 4)
        p["left"] += [linear("h", [["x", 1]]), linear("x", [["h", str(-alpha)]]),
                      query("x", "h", "A", 1, 1), query("x", "h", "A", -1, 1)]
    p["left"].append(linear("h", []))
    p["right"] = [linear("x", []), linear("h", [])]
    return p


def stress(count):
    p = program(["x", "h"])
    for _ in range(count):
        p["left"] += [linear("h", [["x", 1]]), linear("x", [["x", 2]]),
                      query("x", "h", "A", -1, -1), query("x", "h", "B", -1, -1)]
    p["left"].append(linear("h", []))
    p["right"] = [linear("x", []), linear("h", [])]
    return p


def run(small):
    digest = hashlib.sha256()
    dense_count = 0
    def inspect(p, cap=Q(1, 4), dense=True):
        nonlocal dense_count
        w = construct(p, cap)
        literal = check(p, w)
        if dense:
            require(literal == dense_replay(p, w), "independent dense endpoint")
            dense_count += 1
        digest.update(json.dumps(w, sort_keys=True).encode())
        return w

    wrong = json.loads((ROOT / "vendor/wrong-order.json").read_text())
    wrong_witness = inspect(wrong)
    require(wrong_witness["dimension"] == 3, "commutator must have degree two")
    tiny = inspect(wrong, Q(1, 2**40))
    require(Q(tiny["parameter"]) <= Q(1, 2**40), "arbitrary small cap")
    sandwich = json.loads((ROOT / "vendor/dirty-sandwich.json").read_text())
    rejected(lambda: construct(sandwich))
    deletion_count = 0
    for index in range(len(sandwich["left"])):
        p = deepcopy(sandwich)
        del p["left"][index]
        require(group_difference(p), "deleted sandwich instruction is detectable")
        inspect(p)
        deletion_count += 1

    roots = []
    for count in (1, 2, 4, 7):
        p = grid_roots(count)
        w = inspect(p)
        require(w["word"] == ["A"] and w["grid_index"] == count + 1, "must skip all grid roots")
        for j in range(1, count + 1):
            require(replay(p, ["A"], Q(4 * count + 4 - j, 4 * (4 * count + 3)), 0)[0][0] == 0, "grid root")
        roots.append({"roots": count, "grid_size": w["grid_size"],
                      "accepted_index": w["grid_index"], "difference": w["endpoint_difference"][0][0]})

    difference = program()
    difference["left"] = [apply("x", "A", 1)]
    difference["right"] = [apply("x", "A", -1)]
    short = inspect(difference)
    require(short["word"] == ["A"], "shortest coefficient is required")
    for t in (Q(1, 4), Q(1, 7), Q(1, 100)):
        require(replay(difference, ["A", "A"], t, 0)[0][0] == 0,
                "a longer nonzero coefficient need not survive Cayley substitution")
    nested = [("A", 1), ("B", 1), ("A", -1), ("B", -1)]
    for degree in range(2, 6):
        p = program()
        p["left"] = [apply("x", a, sign) for a, sign in nested]
        w = inspect(p)
        require(w["dimension"] == degree + 1, "nested commutator leading degree")
        nested = nested + [("A", 1)] + [(a, -sign) for a, sign in reversed(nested)] + [("A", -1)]

    # This case returns a changed dirty role even though x is unchanged.
    dirty = program(["x", "h"])
    dirty["left"] = [apply("h", "A", -1)]
    dw = inspect(dirty)
    require(dw["input"] == dw["output"] == 1, "retain every dirty input and return")
    # The source and destination alias in this inverse query.
    self_query = program()
    self_query["left"] = [query("x", "x", "A", -1, -1)]
    self_query["right"] = [linear("x", [])]
    inspect(self_query)
    constant = program()
    constant["left"] = [linear("x", [["x", 2]])]
    cw = inspect(constant)
    require(cw["grid_size"] == cw["dimension"] == 1, "constant boundary")

    controls = 0
    changes = {"program_sha256": "0" * 64, "dimension": 4, "input": True,
               "output": 7, "word": ["C"], "parameter": "0", "parameter_cap": "1/2",
               "numerator_degree_bound": -1, "grid_index": 0, "grid_size": 0,
               "endpoint_difference": [["0"] * 3]}
    for key, value in changes.items():
        bad = deepcopy(wrong_witness)
        bad[key] = value
        rejected(lambda: check(wrong, bad))
        controls += 1
    bad_program = deepcopy(wrong)
    bad_program["field"] = 2
    rejected(lambda: construct(bad_program))
    rejected(lambda: construct(wrong, Q(0)))
    rejected(lambda: construct(wrong, Q(1, 3)))
    controls += 3

    random_count, equal_count, negative_count = 0, 0, 0
    rng = random.Random(52625268)
    for index in range(12 if small else 160):
        p = program(["x", "h", "y"])
        for side in ("left", "right"):
            for _ in range(rng.randrange(3, 9)):
                dst, src = rng.choice(p["roles"]), rng.choice(p["roles"])
                a, sign = rng.choice(p["operators"]), rng.choice((-1, 1))
                kind = rng.randrange(3)
                if kind == 0:
                    ins = apply(dst, a, sign)
                elif kind == 1:
                    ins = query(dst, src, a, sign, str(Q(rng.randrange(-2, 3), 2)))
                else:
                    ins = linear(dst, [[src, rng.randrange(-2, 3)], [dst, 1]])
                p[side].append(ins)
        if index % 4 == 0:
            p["right"] = deepcopy(p["left"]) + [apply("h", "B", 1), apply("h", "B", -1)]
        if group_difference(p):
            inspect(p)
            negative_count += 1
        else:
            rejected(lambda: construct(p))
            equal_count += 1
        random_count += 1

    depth = 5 if small else 32
    sw = inspect(stress(depth), dense=False)
    require(sw["dimension"] == depth + 1 and sw["word"] == ["A"] * depth, "delayed inverse series")
    # Check exact inverse action on all basis vectors on independent path labels.
    vector_checks = 0
    for length in range(1, 5 if small else 12):
        word = [rng.choice(("A", "B")) for _ in range(length)]
        for band in parameters(wrong, word, Q(1, 4)).values():
            for j in range(length + 1):
                vector = [Q(i == j) for i in range(length + 1)]
                require(action(band, action(band, vector, -1), 1) == vector, "solve residual")
                require(sum(x*x for x in action(band, vector, 1)) == 1, "exact Euclidean norm")
                vector_checks += 1
    result = {"schema": "orthogonal-inverse-verification/v1", "status": "PASS",
              "random_programs": random_count, "random_equal": equal_count,
              "random_different": negative_count, "dense_full_replays": dense_count,
              "sandwich_deletions": deletion_count, "rejecting_controls": controls,
              "true_inverse_basis_checks": vector_checks, "nested_commutators": 4, "nonshortest_zero_controls": 3, "forced_grid_examples": roots,
              "commutator": wrong_witness, "near_identity_parameter": tiny["parameter"],
              "stress": {"lowest_degree_words": 2**depth, "states": 2 + 2 * depth,
                         "dimension": sw["dimension"], "degree_bound": sw["numerator_degree_bound"],
                         "grid_size": sw["grid_size"], "accepted_index": sw["grid_index"]},
              "witness_digest": digest.hexdigest()}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--small", action="store_true")
    parser.add_argument("--write-result", action="store_true")
    args = parser.parse_args()
    result = run(args.small)
    if not args.small:
        source = json.loads((ROOT / "SOURCES.json").read_text())
        for row in source["files"]:
            if "/vendor/" in row["path"]:
                path = ROOT / "vendor" / Path(row["path"]).name
                require(hashlib.sha256(path.read_bytes()).hexdigest() == row["sha256"], "source bytes")
        if args.write_result:
            (ROOT / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        else:
            require(result == json.loads((ROOT / "RESULT.json").read_text()), "committed receipt")
    print(json.dumps(result, sort_keys=True))
    print("PASS_ORTHOGONAL_INVERSE_CIRCUIT_WITNESS")


if __name__ == "__main__":
    main()
