"""Exact free-algebra certificates for complete dirty linear programs.

Prepared for zxv with substantial OpenAI Codex assistance. Apache-2.0.
Reachable-space equivalence is classical; see PROOF.md for attribution.
"""
from collections import deque
from fractions import Fraction as Q
import argparse
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from fields import scalars


def need(test, message):
    if not test:
        raise ValueError(message)


def number(value, scalar=Q):
    need(type(value) in (int, str), "coefficient must be an integer or exact scalar string")
    return scalar(value)


def index(value, n):
    need(type(value) is int and 0 <= value < n, "role index out of range")
    return value


def add(a, b, scale=Q(1)):
    out = a.copy()
    for j, x in b.items():
        out[j] = out.get(j, Q(0)) + scale*x
        if not out[j]:
            del out[j]
    return out


def scaled(a, c):
    return {j: c*x for j, x in a.items() if c*x}


def digest(problem):
    return hashlib.sha256(json.dumps(problem, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


class Machine:
    def __init__(self, roles, scalar=Q):
        self.roles = roles
        self.scalar = scalar
        self.states = roles
        self.edges = {}
        self.final = {i: i for i in range(roles)}
        self.initial = [{i: scalar(1)} for i in range(roles)]

    def atom(self, symbol, row):
        need(type(symbol) is str and bool(symbol), "nonempty operator symbol required")
        j = self.states
        self.states += 1
        self.edges.setdefault(symbol, {})[j] = row.copy()
        return {j: self.scalar(1)}

    def step(self, row, symbol):
        out = {}
        edges = self.edges.get(symbol, {})
        for i, c in row.items():
            out = add(out, edges.get(i, {}), c)
        return out

    def terminal(self, row):
        out = {}
        for i, c in row.items():
            if i in self.final:
                j = self.final[i]
                out[j] = out.get(j, Q(0)) + c
                if not out[j]:
                    del out[j]
        return out


def program_machine(roles, instructions, shifted=False, scalar=Q):
    need(type(instructions) is list, "program must be a list")
    m = Machine(roles, scalar)
    rows = m.initial
    for op in instructions:
        need(type(op) is dict and type(op.get("op")) is str, "instruction object required")
        kind = op["op"]
        allowed = {
            "add": {"op", "src", "dst", "coefficient"},
            "query": {"op", "src", "dst", "symbol", "coefficient"},
            "apply": {"op", "dst", "symbol"},
            "scale": {"op", "dst", "coefficient"},
            "swap": {"op", "src", "dst"},
        }
        need(kind in allowed and not (op.keys()-allowed[kind]), "unknown instruction or key")
        dst = index(op.get("dst"), roles)
        if kind in ("add", "query", "swap"):
            src = index(op.get("src"), roles)
        if kind == "swap":
            rows[src], rows[dst] = rows[dst], rows[src]
        elif kind == "scale":
            rows[dst] = scaled(rows[dst], number(op["coefficient"], scalar))
        elif kind == "add":
            rows[dst] = add(rows[dst], rows[src], number(op.get("coefficient", 1), scalar))
        else:
            old = rows[dst if kind == "apply" else src].copy()
            atom = m.atom(op.get("symbol"), old)
            image = add(old, atom) if shifted else atom
            if kind == "apply":
                rows[dst] = image
            else:
                rows[dst] = add(rows[dst], image, number(op.get("coefficient", 1), scalar))
    return m


def target_machine(roles, target, shifted=False, scalar=Q):
    need(type(target) is dict and not (target.keys()-{"identity", "terms"}), "invalid target")
    need(type(target.get("identity", True)) is bool, "identity must be Boolean")
    need(type(target.get("terms", [])) is list, "terms must be a list")
    m = Machine(roles, scalar)
    out = [{i: scalar(1)} if target.get("identity", True) else {} for i in range(roles)]
    for term in target.get("terms", []):
        need(type(term) is dict and not (term.keys()-{"out", "in", "word", "coefficient"}), "invalid target term")
        i, j = index(term.get("out"), roles), index(term.get("in"), roles)
        word = term.get("word")
        need(type(word) is list, "word must be an ordered symbol list")
        row = {j: scalar(1)}
        for a in reversed(word):
            atom = m.atom(a, row)
            row = add(row, atom) if shifted else atom
        out[i] = add(out[i], row, number(term.get("coefficient", 1), scalar))
    m.initial = out
    return m


def compile_problem(problem, shifted=False):
    need(type(problem) is dict and not (problem.keys()-{"field", "roles", "program", "reference", "target"}), "invalid problem keys")
    scalar = scalars(problem)
    n = problem.get("roles")
    need(type(n) is int and n > 0, "positive role count required")
    need(("reference" in problem) != ("target" in problem), "provide exactly one reference or target")
    a = program_machine(n, problem["program"], shifted, scalar)
    b = (program_machine(n, problem["reference"], shifted, scalar) if "reference" in problem
         else target_machine(n, problem["target"], shifted, scalar))
    m = Machine(n, scalar)
    m.states = a.states+b.states
    shift = lambda row: {j+a.states: x for j, x in row.items()}
    m.initial = [add(x, shift(y), Q(-1)) for x, y in zip(a.initial, b.initial)]
    m.final = dict(a.final)
    m.final.update({j+a.states: v for j, v in b.final.items()})
    m.edges = {s: dict(rows) for s, rows in a.edges.items()}
    for s, rows in b.edges.items():
        m.edges.setdefault(s, {}).update({j+a.states: shift(v) for j, v in rows.items()})
    return m


class Span:
    """Incremental elimination with coordinates in the original reachable rows."""
    def __init__(self):
        self.rows = []
        self.echelon = []

    def reduce(self, row):
        row = row.copy()
        coords = {}
        for pivot, basis, rep in self.echelon:
            c = row.get(pivot, Q(0))
            if c:
                row = add(row, basis, -c)
                coords = add(coords, rep, c)
        return row, coords

    def insert(self, row):
        rest, coords = self.reduce(row)
        if not rest:
            return False
        j = len(self.rows)
        self.rows.append(row)
        pivot = min(rest)
        c = 1/rest[pivot]
        rep = scaled(add({j: Q(1)}, coords, Q(-1)), c)
        self.echelon.append((pivot, scaled(rest, c), rep))
        self.echelon.sort(key=lambda item: item[0])
        return True

    def coordinates(self, row):
        rest, coords = self.reduce(row)
        need(not rest, "internal invariant space is not closed")
        return coords


def packed(row):
    return {str(j): str(x) for j, x in sorted(row.items())}


def decide(problem, shifted=False):
    m = compile_problem(problem, shifted)
    alphabet = sorted(m.edges)
    span, paths, queue = Span(), [], deque()

    def consider(row, output, word):
        terminal = m.terminal(row)
        if terminal:
            j = min(terminal)
            return {"schema": "dirty-linear-certificate/v1", "problem_sha256": digest(problem),
                    "equivalent": False, "shifted": shifted, "states": m.states,
                    "output": output, "input": j, "word": word,
                    "coefficient": str(terminal[j]), "matrix_dimension": len(word)+1}
        if span.insert(row):
            paths.append({"output": output, "word": word})
            queue.append(len(paths)-1)
        return None

    for i, row in enumerate(m.initial):
        bad = consider(row, i, [])
        if bad:
            return bad
    while queue:
        k = queue.popleft()
        for a in alphabet:
            p = paths[k]
            bad = consider(m.step(span.rows[k], a), p["output"], p["word"]+[a])
            if bad:
                return bad
    return {"schema": "dirty-linear-certificate/v1", "problem_sha256": digest(problem),
            "equivalent": True, "shifted": shifted, "states": m.states,
            "paths": paths, "initial": [packed(span.coordinates(row)) for row in m.initial],
            "closure": {a: [packed(span.coordinates(m.step(row, a))) for row in span.rows]
                        for a in alphabet}}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("problem", type=Path)
    ap.add_argument("--invertible", action="store_true", help="use X=I+Y to construct unipotent witnesses")
    ap.add_argument("--output", type=Path, help="new certificate path; never overwritten")
    args = ap.parse_args()
    cert = decide(json.loads(args.problem.read_text()), args.invertible)
    data = json.dumps(cert, indent=2, sort_keys=True)+"\n"
    if args.output:
        with args.output.open("x") as stream:
            stream.write(data)
    else:
        print(data, end="")


if __name__ == "__main__":
    main()
