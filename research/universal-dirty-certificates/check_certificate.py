"""Small proof checker: no search, Gaussian elimination, or producer import.

The trusted surface includes this separately transcribed register compiler.
Prepared for zxv with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as F
import argparse
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from fields import scalars


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def combine(terms):
    result = {}
    for c, v in terms:
        for i, x in v.items():
            result[i] = result.get(i, F(0))+c*x
    return {i: x for i, x in result.items() if x}


def reconstruct(problem, shifted):
    """Reconstruct a dense dependency table using immutable register versions."""
    n = problem["roles"]
    require(type(n) is int and n > 0, "roles")
    require(set(problem) <= {"field", "roles", "program", "reference", "target"}, "problem keys")
    field = scalars(problem)
    require(("target" in problem) != ("reference" in problem), "reference/target")
    dependencies, labels, final = [], [], []

    def scalar(x):
        require(type(x) in (str, int), "coefficient type")
        return field(x)

    def role(i):
        require(type(i) is int and 0 <= i < n, "role index")
        return i

    def leaf(i):
        j = len(labels)
        labels.append(None)
        dependencies.append({})
        final.append(i)
        return {j: field(1)}

    def unary(s, v):
        require(type(s) is str and s, "symbol")
        j = len(labels)
        labels.append(s)
        dependencies.append(v.copy())
        final.append(None)
        return combine([(F(1), {j: field(1)}), (F(1), v)]) if shifted else {j: field(1)}

    def instructions(ops):
        require(type(ops) is list, "instruction list")
        registers = [leaf(i) for i in range(n)]
        for op in ops:
            require(type(op) is dict, "instruction")
            k = op.get("op")
            keys = {"add": {"op", "src", "dst", "coefficient"},
                    "query": {"op", "src", "dst", "symbol", "coefficient"},
                    "apply": {"op", "dst", "symbol"},
                    "scale": {"op", "dst", "coefficient"},
                    "swap": {"op", "src", "dst"}}
            require(k in keys and set(op) <= keys[k], "instruction keys")
            d = role(op["dst"])
            if k in ("add", "query", "swap"):
                s = role(op["src"])
            if k == "swap":
                registers[s], registers[d] = registers[d], registers[s]
            elif k == "scale":
                registers[d] = combine([(scalar(op["coefficient"]), registers[d])])
            elif k == "apply":
                registers[d] = unary(op["symbol"], registers[d])
            else:
                image = registers[s].copy()
                if k == "query":
                    image = unary(op["symbol"], image)
                registers[d] = combine([(F(1), registers[d]), (scalar(op.get("coefficient", 1)), image)])
        return registers

    left = instructions(problem["program"])
    if "reference" in problem:
        right = instructions(problem["reference"])
    else:
        t = problem["target"]
        require(type(t) is dict and set(t) <= {"identity", "terms"}, "target")
        require(type(t.get("identity", True)) is bool and type(t.get("terms", [])) is list, "target types")
        leaves = [leaf(i) for i in range(n)]
        right = [v.copy() if t.get("identity", True) else {} for v in leaves]
        for term in t.get("terms", []):
            require(type(term) is dict and set(term) <= {"out", "in", "word", "coefficient"}, "term keys")
            i, j = role(term["out"]), role(term["in"])
            require(type(term["word"]) is list, "word")
            image = leaves[j]
            for a in term["word"][::-1]:
                image = unary(a, image)
            right[i] = combine([(F(1), right[i]), (scalar(term.get("coefficient", 1)), image)])
    roots = [combine([(F(1), x), (F(-1), y)]) for x, y in zip(left, right)]

    def transition(v, a):
        return combine([(x, dependencies[i]) for i, x in v.items() if labels[i] == a])

    def terminal(v):
        return combine([(x, {final[i]: F(1)}) for i, x in v.items() if final[i] is not None])

    return roots, transition, terminal, len(labels), sorted(set(labels)-{None})


def check(problem, certificate):
    require(certificate.get("schema") == "dirty-linear-certificate/v1", "certificate schema")
    source_hash = hashlib.sha256(json.dumps(problem, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    require(certificate.get("problem_sha256") == source_hash, "problem digest")
    shifted = certificate.get("shifted")
    require(type(shifted) is bool and type(certificate.get("equivalent")) is bool, "certificate flags")
    roots, step, terminal, states, alphabet = reconstruct(problem, shifted)
    field = scalars(problem)
    require(certificate.get("states") == states, "state count")

    def path(output, word):
        require(type(output) is int and 0 <= output < len(roots), "output role")
        require(type(word) is list and all(a in alphabet for a in word), "path alphabet")
        v = roots[output]
        for a in word:
            v = step(v, a)
        return v

    if not certificate["equivalent"]:
        out = terminal(path(certificate["output"], certificate["word"]))
        j = certificate["input"]
        require(type(j) is int and 0 <= j < len(roots), "input role")
        require(type(certificate["coefficient"]) is str, "witness coefficient type")
        require(out.get(j, field(0)) == field(certificate["coefficient"]) != 0, "nonzero coefficient")
        require(certificate["matrix_dimension"] == len(certificate["word"])+1, "matrix dimension")
        return "counterexample"

    paths = certificate["paths"]
    require(type(paths) is list and len(paths) <= states, "basis size")
    basis = [path(p["output"], p["word"]) for p in paths]
    require(all(not terminal(v) for v in basis), "basis output is nonzero")

    def expand(c):
        require(type(c) is dict, "coordinates must be a sparse object")
        terms = []
        for j, x in c.items():
            require(type(j) is str and j.isascii() and j.isdecimal() and str(int(j)) == j, "coordinate key")
            require(0 <= int(j) < len(basis) and type(x) is str, "coordinate range/type")
            terms.append((field(x), basis[int(j)]))
        return combine(terms)

    init = certificate["initial"]
    require(type(init) is list and len(init) == len(roots), "initial coverage")
    require(all(expand(c) == v for c, v in zip(init, roots)), "initial span")
    closure = certificate["closure"]
    require(type(closure) is dict and set(closure) == set(alphabet), "complete operator closure")
    for a in alphabet:
        rows = closure[a]
        require(type(rows) is list and len(rows) == len(basis), "closure row coverage")
        require(all(expand(c) == step(v, a) for c, v in zip(rows, basis)), "invariant closure")
    return "universal-identity"


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("problem", type=Path)
    p.add_argument("certificate", type=Path)
    p.add_argument("--matrices", action="store_true", help="print sparse concrete counterexample matrices")
    args = p.parse_args()
    problem, certificate = json.loads(args.problem.read_text()), json.loads(args.certificate.read_text())
    verdict = check(problem, certificate)
    if args.matrices:
        require(verdict == "counterexample", "a positive certificate has no counterexample")
        word = certificate["word"]
        d = len(word)+1
        _, _, _, _, alphabet = reconstruct(problem, certificate["shifted"])
        matrices = {}
        for a in alphabet:
            triples = [[j, j, 1] for j in range(d)] if certificate["shifted"] else []
            triples += [[j, j+1, 1] for j, b in enumerate(word) if b == a]
            matrices[a] = triples
        print(json.dumps({"field": problem.get("field", "Q"), "dimension": d,
                          "operators_as_row_column_value": matrices,
                          "input_role": certificate["input"], "input_payload_basis": d-1,
                          "output_role": certificate["output"], "output_coordinate": 0,
                          "endpoint_discrepancy": certificate["coefficient"]}, indent=2, sort_keys=True))
    else:
        print("PASS_DIRTY_LINEAR_CERTIFICATE", verdict)


if __name__ == "__main__":
    main()
