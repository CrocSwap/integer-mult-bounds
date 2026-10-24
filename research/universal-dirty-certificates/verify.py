#!/usr/bin/env python3
"""Bounded semantic validation; default execution is read-only.

Prepared for zxv with substantial OpenAI Codex assistance. Apache-2.0.
"""
from copy import deepcopy
from fractions import Fraction as Q
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import random
import sys
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import linear_words as producer
import check_certificate as checker


def need(ok, message):
    if not ok:
        raise ValueError(message)


def ident(d):
    return [[Q(i == j) for j in range(d)] for i in range(d)]


def plus(a, b):
    return [[x+y for x, y in zip(ra, rb)] for ra, rb in zip(a, b)]


def times(a, b):
    return [[sum((a[i][k]*b[k][j] for k in range(len(b))), Q(0))
             for j in range(len(b[0]))] for i in range(len(a))]


def constant(c, a):
    return [[c*x for x in row] for row in a]


def dense(problem, matrices):
    """Literal full-column interpreter, unrelated to the atom representation."""
    n, d = problem["roles"], len(next(iter(matrices.values()), [[1]]))
    scalar = producer.scalars(problem) if problem.get("field") == "Qi" else Q
    zero = [[Q(0)]*d for _ in range(d)]

    def execute(ops):
        rows = [[ident(d) if i == j else deepcopy(zero) for j in range(n)] for i in range(n)]
        for op in ops:
            k, dst = op["op"], op["dst"]
            if k == "swap":
                s = op["src"]
                rows[s], rows[dst] = rows[dst], rows[s]
            elif k == "scale":
                rows[dst] = [constant(scalar(op["coefficient"]), b) for b in rows[dst]]
            elif k == "apply":
                rows[dst] = [times(matrices[op["symbol"]], b) for b in rows[dst]]
            else:
                source = deepcopy(rows[op["src"]])
                if k == "query":
                    source = [times(matrices[op["symbol"]], b) for b in source]
                c = scalar(op.get("coefficient", 1))
                rows[dst] = [plus(x, constant(c, y)) for x, y in zip(rows[dst], source)]
        return rows

    left = execute(problem["program"])
    if "reference" in problem:
        right = execute(problem["reference"])
    else:
        t = problem["target"]
        right = [[ident(d) if t.get("identity", True) and i == j else deepcopy(zero)
                  for j in range(n)] for i in range(n)]
        for term in t.get("terms", []):
            v = ident(d)
            for a in term["word"]:
                v = times(v, matrices[a])
            i, j = term["out"], term["in"]
            right[i][j] = plus(right[i][j], constant(scalar(term.get("coefficient", 1)), v))
    return [[plus(x, constant(-1, y)) for x, y in zip(a, b)] for a, b in zip(left, right)]


def witness_matrices(problem, certificate):
    m = producer.compile_problem(problem)
    word = certificate["word"]
    d = len(word)+1
    out = {}
    for a in m.edges:
        matrix = ident(d) if certificate["shifted"] else [[Q(0)]*d for _ in range(d)]
        for j, b in enumerate(word):
            if a == b:
                matrix[j][j+1] += 1
        out[a] = matrix
    return out


def check_negative(problem, certificate):
    need(checker.check(problem, certificate) == "counterexample", "coefficient checker")
    residual = dense(problem, witness_matrices(problem, certificate))
    value = residual[certificate["output"]][certificate["input"]][0][-1]
    field = producer.scalars(problem)
    need(field(value) == field(certificate["coefficient"]) != 0, "literal matrix counterexample")


def explicit_polynomials(problem):
    """Independent small-case word expansion: maps (word,input) to coefficients."""
    n = problem["roles"]
    rows = [{((), i): Q(1)} for i in range(n)]

    def add(a, b, c=Q(1)):
        r = a.copy()
        for key, x in b.items():
            r[key] = r.get(key, Q(0))+c*x
        return {k: x for k, x in r.items() if x}

    for op in problem["program"]:
        k, d = op["op"], op["dst"]
        if k == "swap":
            s = op["src"]
            rows[s], rows[d] = rows[d], rows[s]
        elif k == "scale":
            rows[d] = {key: Q(op["coefficient"])*x for key, x in rows[d].items() if Q(op["coefficient"])*x}
        else:
            source = rows[d if k == "apply" else op["src"]].copy()
            if k in ("query", "apply"):
                source = {((op["symbol"],)+word, i): x for (word, i), x in source.items()}
            rows[d] = source if k == "apply" else add(rows[d], source, Q(op.get("coefficient", 1)))
    return rows


def source_echo():
    path = HERE.parents[1]/"research/cyclic-dirty-commutator-audit/echo.py"
    manifest = json.loads((HERE/"SOURCES.json").read_text())
    pin = next(f for f in manifest["files"] if f["path"].endswith("/echo.py"))
    need(hashlib.sha256(path.read_bytes()).hexdigest() == pin["sha256"], "echo source pin")
    spec = importlib.util.spec_from_file_location("pinned_echo", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def echo_problem(source, count, fanout, sign=1):
    scratch, calls = source.resources(count, fanout)
    instructions = list(source.instructions(0, count, 0, 1, 2, fanout, sign))
    need(len(instructions) == calls, "source count")
    return {"roles": 2+scratch,
            "program": [{"op": "query", "src": s, "dst": t, "symbol": f"A{i}", "coefficient": q}
                        for s, t, i, q in instructions],
            "target": {"identity": True, "terms": [{"out": 1, "in": 0,
                        "word": [f"A{i}" for i in reversed(range(count))], "coefficient": sign}]}}


def rejected(fn):
    try:
        fn()
    except (ValueError, KeyError, TypeError, ZeroDivisionError):
        return
    raise ValueError("malformed control accepted")


def main():
    source = source_echo()
    report = {"echo_identities": 0, "literal_counterexamples": 0, "differential_cases": 0,
              "certificate_rejections": 0, "input_rejections": 0}
    start = time.monotonic()
    max_states = max_basis = 0
    for field in ("Q", "Qi", 2, 3, 5):
        for n in (1, 2, 3, 5, 8, 12, 16):
            for fanout in (2, 3, 8):
                for sign in (-1, 1):
                    p = echo_problem(source, n, fanout, sign)
                    p["field"] = field
                    c = producer.decide(p)
                    need(c["equivalent"] and checker.check(p, c) == "universal-identity", "source echo identity")
                    max_states = max(max_states, c["states"])
                    max_basis = max(max_basis, len(c["paths"]))
                    report["echo_identities"] += 1
    p = echo_problem(source, 3, 3)
    mutations = []
    a = deepcopy(p); a["program"].pop(); mutations.append(a)
    a = deepcopy(p); a["program"][1]["coefficient"] *= -1; mutations.append(a)
    a = deepcopy(p); a["target"]["terms"][0]["word"].reverse(); mutations.append(a)
    a = deepcopy(p); a["program"][0]["src"] = 1; mutations.append(a)
    a = deepcopy(p); a["program"].append({"op": "scale", "dst": 2, "coefficient": 0}); mutations.append(a)
    for field in ("Q", "Qi", 2, 3, 5):
        for a in mutations:
            a["field"] = field
            for shift in (False, True):
                c = producer.decide(a, shift)
                # Negating a call changes nothing in characteristic two.
                if field == 2 and a is mutations[1]:
                    need(c["equivalent"], "characteristic-two sign")
                    checker.check(a, c)
                    continue
                need(not c["equivalent"], "bad echo accepted")
                check_negative(a, c)
                report["literal_counterexamples"] += 1

    # Dense scalar evaluations cannot see a commutator. The formal checker can.
    trap = {"roles": 1, "program": [], "target": {"terms": [
        {"out": 0, "in": 0, "word": ["X", "Y"]},
        {"out": 0, "in": 0, "word": ["Y", "X"], "coefficient": -1}]}}
    for x, y in itertools.product(range(-2, 3), repeat=2):
        need(dense(trap, {"X": [[Q(x)]], "Y": [[Q(y)]]}) == [[[[0]]]], "scalar blindness")
    for shift in (False, True):
        c = producer.decide(trap, shift)
        need(len(c["word"]) == 2, "shortest commutator word")
        check_negative(trap, c)
        report["literal_counterexamples"] += 1
    bad = producer.decide(trap)
    for key, value in (("coefficient", "0"), ("input", 1), ("matrix_dimension", 99), ("word", ["X"])):
        wrong = deepcopy(bad); wrong[key] = value
        rejected(lambda: checker.check(trap, wrong))
        report["certificate_rejections"] += 1

    # Tensoring the named unary map H=G-I differs from substituting in G-I.
    def kron(a, b):
        return [[a[i][j]*b[k][l] for j in range(len(a)) for l in range(len(b))]
                for i in range(len(a)) for k in range(len(b))]
    g = [[Q(2), Q(0)], [Q(0), Q(3)]]
    h = plus(g, constant(-1, ident(2)))
    need(h == [[1, 0], [0, 2]], "one-column tensor trap premise")
    need(kron(h, h) != plus(kron(g, g), constant(-1, ident(4))), "tensor-of-sum trap")
    report["tensor_of_sum_rejections"] = 1

    # Exact differential tests include self reads, rational signs, swaps, scales,
    # zero maps, dead symbols, and correlated reuse. Expand only these small cases.
    rng = random.Random(20261023)
    for _ in range(120):
        n = rng.randrange(1, 5)
        ops = []
        for _ in range(9):
            k, s, d = rng.choice(("add", "query", "apply", "scale", "swap")), rng.randrange(n), rng.randrange(n)
            op = {"op": k, "dst": d}
            if k in ("add", "query", "swap"):
                op["src"] = s
            if k in ("query", "apply"):
                op["symbol"] = rng.choice(("X", "Y"))
            if k in ("add", "query", "scale"):
                op["coefficient"] = rng.choice(("0", "1/2", "-2", "3/2"))
            ops.append(op)
        a = {"roles": n, "program": ops}
        rows = explicit_polynomials(a)
        terms = [{"out": o, "in": i, "word": list(w), "coefficient": str(c)}
                 for o, row in enumerate(rows) for (w, i), c in row.items()]
        a["target"] = {"identity": False, "terms": terms}
        for shift in (False, True):
            c = producer.decide(a, shift)
            need(c["equivalent"], "word expansion mismatch")
            checker.check(a, c)
        # Force a known discrepancy, then compare shortest degree to expansion.
        a["target"]["terms"].append({"out": 0, "in": 0, "word": ["X", "Y", "X"], "coefficient": 1})
        c = producer.decide(a)
        need(not c["equivalent"] and len(c["word"]) == 3, "shortest witness mismatch")
        check_negative(a, c)
        report["literal_counterexamples"] += 1
        report["differential_cases"] += 1

    c = producer.decide(p)
    corruptions = []
    a = deepcopy(c); a["paths"].pop(); corruptions.append(a)
    a = deepcopy(c); a["initial"].pop(); corruptions.append(a)
    a = deepcopy(c); a["initial"][0] = {}; corruptions.append(a)
    a = deepcopy(c); a["closure"].pop(next(iter(a["closure"]))); corruptions.append(a)
    a = deepcopy(c); a["closure"][next(iter(a["closure"]))].pop(); corruptions.append(a)
    a = deepcopy(c); a["problem_sha256"] = "0"*64; corruptions.append(a)
    a = deepcopy(c); a["states"] += 1; corruptions.append(a)
    a = deepcopy(c); a["shifted"] = 0; corruptions.append(a)
    a = deepcopy(c); a["paths"][0]["word"] = ["unknown"]; corruptions.append(a)
    # Replace one genuinely nonzero closure row by zero.
    a = deepcopy(c)
    symbol, row = next((s, i) for s, rows in a["closure"].items() for i, v in enumerate(rows) if v)
    a["closure"][symbol][row] = {}; corruptions.append(a)
    a = deepcopy(c); a["initial"][0] = {"99999": "1"}; corruptions.append(a)
    for a in corruptions:
        rejected(lambda: checker.check(p, a))
        report["certificate_rejections"] += 1
    # Omit every dirty-return requirement except the apparent target success.
    # The earlier scale(0) mutation proves that such a weakening would miss dirt.
    for modify in (
        lambda a: a.update(roles=True),
        lambda a: a["program"][0].update(src=99),
        lambda a: a["program"][0].update(coefficient=0.5),
        lambda a: a["program"][0].update(op="inverse"),
        lambda a: a["program"][0].update(symbol=""),
        lambda a: a.update(reference=[]),
        lambda a: a.update(field=4),
        lambda a: a.update(field=True),
        lambda a: (a.update(field=2), a["program"][0].update(coefficient="1/2")),
    ):
        a = deepcopy(p); modify(a)
        rejected(lambda: producer.decide(a))
        report["input_rejections"] += 1

    # A characteristic-dependent identity must not be silently certified over Q.
    binary = {"roles": 2, "program": [{"op": "query", "src": 0, "dst": 1, "symbol": "X"}]*2,
              "reference": []}
    need(not producer.decide(binary)["equivalent"], "rational double query")
    binary["field"] = 2
    checker.check(binary, producer.decide(binary))
    report["finite_field_operations"] = 0
    for prime in (2, 3, 5, 7, 11):
        field = producer.scalars({"field": prime})
        for x, y in itertools.product(range(prime), repeat=2):
            need(str(field(x)+field(y)) == str((x+y) % prime), "field addition")
            need(str(field(x)*field(y)) == str(x*y % prime), "field product")
            if y:
                need(str(field(x)/field(y)) == str(x*pow(y, -1, prime) % prime), "field quotient")
            report["finite_field_operations"] += 2+bool(y)

    gaussian = producer.scalars({"field": "Qi"})
    complex_problem = {"field": "Qi", "roles": 2, "program": [
        {"op": "scale", "dst": 0, "coefficient": "i"},
        {"op": "query", "src": 0, "dst": 1, "symbol": "X", "coefficient": "1/2+3/4i"},
        {"op": "scale", "dst": 0, "coefficient": "-i"}],
        "target": {"terms": [{"out": 1, "in": 0, "word": ["X"], "coefficient": "-3/4+1/2i"}]}}
    checker.check(complex_problem, producer.decide(complex_problem))
    need(gaussian("i")*gaussian("i") == -1, "Gaussian phase square")
    for r, s in itertools.product(range(-2, 3), repeat=2):
        z = gaussian.pair(Q(r, 2), Q(s, 3))
        need(gaussian(str(z)) == z, "Gaussian exact serialization")
        if z:
            need(z/z == 1, "Gaussian quotient")
    complex_problem["target"]["terms"][0]["coefficient"] = "-3/4-1/2i"
    for shift in (False, True):
        check_negative(complex_problem, producer.decide(complex_problem, shift))
        report["literal_counterexamples"] += 1
    report["gaussian_field_controls"] = 51

    # 2^64 distinct words per endpoint; never enumerate them.
    k = 64
    ops = [{"op": "query", "src": 0, "dst": 0, "symbol": f"X{i}"} for i in range(k)]
    stress = {"roles": 1, "program": ops, "reference":
              [{"op": "scale", "dst": 0, "coefficient": 2}]+ops+
              [{"op": "scale", "dst": 0, "coefficient": "1/2"}]}
    t = time.monotonic(); c = producer.decide(stress); checker.check(stress, c)
    report["exponential_support"] = {"distinct_words": 2**k, "states": c["states"],
                                      "basis_rows": len(c["paths"]), "seconds": round(time.monotonic()-t, 6)}
    # Sharpness of the unipotent witness bound within the unipotent test class.
    for degree in range(1, 9):
        a = {"roles": 1, "program": [{"op": "query", "src": 0, "dst": 0,
              "symbol": "X", "coefficient": -1} for _ in range(degree)],
              "reference": [{"op": "scale", "dst": 0, "coefficient": 0}]}
        c = producer.decide(a, True)
        need(len(c["word"]) == degree, "sharp unipotent bound")
        check_negative(a, c)
        for dim in range(1, degree+1):
            x = ident(dim)
            for j in range(dim-1):
                x[j][j+1] = 1
            need(all(not z for row in dense(a, {"X": x})[0][0] for z in row), "below degree vanishing")
        report["literal_counterexamples"] += 1
    report["max_echo_states"] = max_states
    report["max_echo_basis_rows"] = max_basis
    report["seconds"] = round(time.monotonic()-start, 6)
    names = ("dirty-echo3", "binary-echo3", "wrong-order")
    expected = {name+suffix for name in names for suffix in (".json", ".certificate.json")}
    need({p.name for p in (HERE/"examples").glob("*.json")} == expected, "committed example inventory")
    for name in names:
        path = HERE/"examples"/(name+".json")
        example = json.loads(path.read_text())
        certificate = json.loads(path.with_suffix(".certificate.json").read_text())
        checker.check(example, certificate)
        need(producer.decide(example, certificate["shifted"]) == certificate, "committed certificate drift")
        if not certificate["equivalent"]:
            check_negative(example, certificate)
    report["committed_examples"] = len(names)
    print(json.dumps(report, indent=2, sort_keys=True))
    print("PASS_UNIVERSAL_DIRTY_CERTIFICATES")


if __name__ == "__main__":
    main()
