"""Compact feedback realization and exact reachable-space search.

This is the producer implementation; check_certificate.py does not import it.
Prepared for Krzysztof Wójt with OpenAI Codex assistance. Apache-2.0.
"""

from collections import deque

from syntax import fingerprint, validate


def add_scaled(dst, src, scalar, field):
    if scalar:
        for j, value in enumerate(src):
            if value:
                dst[j] = field.add(dst[j], field.mul(scalar, value))


def row_times(row, matrix, field):
    result = [field.zero] * len(matrix[0])
    for scalar, source in zip(row, matrix):
        add_scaled(result, source, scalar, field)
    return result


def compile_program(program):
    """Return U,T,V with coefficients U T_word V after G=I+Y.

    Both sides share the original leaf atoms. Each unary occurrence creates
    exactly one further atom, including inverse and zero-coefficient queries.
    """
    f = validate(program)
    roles = program["roles"]
    r = len(roles)
    q = sum(ins["op"] != "linear" for side in ("left", "right") for ins in program[side])
    d = r + q
    atoms = []
    finals = []
    for side in ("left", "right"):
        regs = {name: [f.one if j == i else f.zero for j in range(d)]
                for i, name in enumerate(roles)}
        for ins in program[side]:
            dst = ins["dst"]
            if ins["op"] == "linear":
                result = [f.zero] * d
                for name, coefficient in ins["terms"]:
                    add_scaled(result, regs[name], f.parse(coefficient), f)
                regs[dst] = result
                continue
            source = dst if ins["op"] == "apply" else ins["src"]
            dependency = regs[source][:]
            j = r + len(atoms)
            atoms.append((ins["operator"], ins["direction"], dependency))
            if ins["op"] == "apply":
                regs[dst] = [f.one if k == j else f.zero for k in range(d)]
            else:
                result = regs[dst][:]
                result[j] = f.add(result[j], f.parse(ins["coefficient"]))
                regs[dst] = result
        finals.append([regs[name] for name in roles])
    u = [[f.sub(x, y) for x, y in zip(a, b)] for a, b in zip(*finals)]
    v = [[f.one if i == j else f.zero for j in range(r)] for i in range(d)]
    transitions = {a: [[f.zero] * d for _ in range(d)] for a in program["operators"]}
    for j, (symbol, direction, dependency) in enumerate(atoms, r):
        v[j] = row_times(dependency[:j], v[:j], f)
        for a, matrix in transitions.items():
            matrix[j] = row_times(dependency[:j], matrix[:j], f)
            if a == symbol:
                if direction == 1:
                    add_scaled(matrix[j], dependency, f.one, f)
                else:
                    matrix[j][j] = f.sub(matrix[j][j], f.one)
    return {"field": f, "dimension": d, "U": u, "T": transitions, "V": v}


class ReachableBasis:
    """Echelon rows with exact coordinates in the original path rows."""

    def __init__(self, field):
        self.field = field
        self.rows = []
        self.echelon = []

    def reduce(self, row):
        f = self.field
        residual = row[:]
        coefficients = [f.zero] * len(self.rows)
        for pivot, normalized, coordinates in self.echelon:
            scalar = residual[pivot]
            if scalar:
                add_scaled(residual, normalized, f.neg(scalar), f)
                add_scaled(coefficients, coordinates, scalar, f)
        return residual, coefficients

    def append(self, row):
        f = self.field
        residual, removed = self.reduce(row)
        pivot = next((j for j, x in enumerate(residual) if x), None)
        if pivot is None:
            return False
        scale = residual[pivot]
        normalized = [f.div(x, scale) for x in residual]
        coordinates = [f.div(f.neg(x), scale) for x in removed] + [f.div(f.one, scale)]
        self.rows.append(row[:])
        self.echelon.append((pivot, normalized, coordinates))
        return True

    def coordinates(self, row):
        remainder, coefficients = self.reduce(row)
        if any(remainder):
            raise ValueError("row is outside the claimed span")
        return coefficients


def produce(program):
    model = compile_program(program)
    f, u, t, v = (model[k] for k in ("field", "U", "T", "V"))
    basis = ReachableBasis(f)
    paths = []
    queue = deque()
    for output, row in enumerate(u):
        if basis.append(row):
            path = {"output": output, "word": []}
            paths.append(path)
            queue.append((row, path))
    while queue:
        row, path = queue.popleft()
        projected = row_times(row, v, f)
        if any(projected):
            i = next(i for i, value in enumerate(projected) if value)
            return {
                "schema": "inverse-dirty-certificate/v1",
                "program_sha256": fingerprint(program),
                "verdict": "different",
                "output": path["output"], "input": i, "word": path["word"],
                "coefficient": f.dump(projected[i]),
            }
        for symbol, matrix in t.items():
            successor = row_times(row, matrix, f)
            if basis.append(successor):
                successor_path = {"output": path["output"], "word": path["word"] + [symbol]}
                paths.append(successor_path)
                queue.append((successor, successor_path))
    encode = lambda rows: [[f.dump(x) for x in row] for row in rows]
    return {
        "schema": "inverse-dirty-certificate/v1",
        "program_sha256": fingerprint(program),
        "verdict": "equal",
        "paths": paths,
        "initial": encode([basis.coordinates(row) for row in u]),
        "closure": {a: encode([basis.coordinates(row_times(b, matrix, f))
                                for b in basis.rows]) for a, matrix in t.items()},
    }
