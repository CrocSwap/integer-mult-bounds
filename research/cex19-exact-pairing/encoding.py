"""Exact bounded CNF for the fixed 19-line pairing problem. Apache-2.0."""
from itertools import combinations

PIVOTS = ((9, 11, 3, 17, 2, 8), (1, 10, 11, 2), (1, 4, 7, 10, 11, 3))


class Reject(ValueError):
    pass


def require(ok, message):
    if not ok:
        raise Reject(message)


def negative(literal):
    return not literal if type(literal) is bool else -literal


class Formula:
    """Boolean constants are bool; signed integer literals are never bool."""

    def __init__(self):
        self.variables = 0
        self.clauses = []
        self.inputs = {}
        self.gates = {}
        self.cache = {}

    def fresh(self, label=None):
        require(self.variables < 10000, "variable capacity")
        self.variables += 1
        if label is not None:
            self.inputs[self.variables] = label
        return self.variables

    def clause(self, literals):
        require(len(self.clauses) < 20000, "clause capacity")
        if any(x is True for x in literals):
            return
        self.clauses.append([x for x in literals if type(x) is not bool])

    def equal(self, left, right):
        self.clause([negative(left), right])
        self.clause([left, negative(right)])

    def gate(self, kind, left, right):
        require(kind in ("and", "xor"), "gate kind")
        if type(left) is bool:
            if kind == "and":
                return right if left else False
            return negative(right) if left else right
        if type(right) is bool:
            return self.gate_constant(kind, left, right)
        if left == right:
            return left if kind == "and" else False
        if left == -right:
            return False if kind == "and" else True
        key = (kind, *sorted((left, right)))
        if key not in self.cache:
            z = self.fresh()
            self.gates[z] = (kind, left, right)
            if kind == "and":
                clauses = [[-z, left], [-z, right], [z, -left, -right]]
            else:
                clauses = [[-z, left, right], [-z, -left, -right],
                           [z, -left, right], [z, left, -right]]
            for clause in clauses:
                self.clause(clause)
            self.cache[key] = z
        return self.cache[key]

    def gate_constant(self, kind, left, right):
        if kind == "and":
            return left if right else False
        return negative(left) if right else left

    def dimacs(self):
        header = f"p cnf {self.variables} {len(self.clauses)}\n"
        return header + "".join(" ".join(map(str, c)) + " 0\n" for c in self.clauses)


def validate_configuration(config):
    require(type(config) is list and len(config) == 19, "configuration size")
    for pair in config:
        require(type(pair) is list and len(pair) == 2, "point/line pair")
        for vector in pair:
            require(type(vector) is list and len(vector) == 3, "coordinate count")
            require(all(type(z) is int and -1 <= z <= 1 for z in vector), "coordinates")
        require(dot(*pair) != 0, "nonzero decoder diagonal")


def dot(left, right):
    return sum(x*y for x, y in zip(left, right))


def pairing(config, formula):
    matrix = []
    for t in range(19):
        row = []
        for s in range(19):
            if t == s:
                row.append(True)
            elif dot(config[t][0], config[s][1]) == 0:
                row.append(formula.fresh(("B", t, s)))
            else:
                row.append(False)
        matrix.append(row)
    return matrix


def schur(config, matrix, coordinate, formula):
    """Eliminate a forced unit upper-triangular principal minor over F2."""
    pivots = list(PIVOTS[coordinate])
    rows = [t for t in range(19) if config[t][0][coordinate]]
    cols = [s for s in range(19) if config[s][1][coordinate]]
    require(set(pivots) <= set(rows) & set(cols), "pivot support")
    rows = pivots + [t for t in rows if t not in pivots]
    cols = pivots + [s for s in cols if s not in pivots]
    a = [[matrix[t][s] for s in cols] for t in rows]
    count = len(pivots)
    require(all(a[t][s] is False for t in range(count) for s in range(t)),
            "forced triangular minor")
    for k in range(count):
        require(a[k][k] is True, "unit pivot")
        for t in range(k+1, len(rows)):
            multiplier = a[t][k]
            for s in range(k+1, len(cols)):
                term = formula.gate("and", multiplier, a[k][s])
                a[t][s] = formula.gate("xor", a[t][s], term)
            a[t][k] = False
    return [row[count:] for row in a[count:]]


def factor(formula, residual, coordinate, capacity):
    nr, nc = len(residual), len(residual[0])
    active = [formula.fresh(("e", coordinate, k)) for k in range(capacity)]
    for k in range(capacity-1):
        formula.clause([-active[k+1], active[k]])
    x = [[formula.fresh(("X", coordinate, t, k)) for k in range(capacity)]
         for t in range(nr)]
    y = [[formula.fresh(("Y", coordinate, k, s)) for s in range(nc)]
         for k in range(capacity)]
    for t in range(nr):
        for k in range(capacity):
            formula.clause([-x[t][k], active[k]])
    for t in range(nr):
        for s in range(nc):
            value = False
            for k in range(capacity):
                term = formula.gate("and", x[t][k], y[k][s])
                value = formula.gate("xor", value, term)
            formula.equal(value, residual[t][s])
    return active


def build(config, capacity=4):
    """Cost <= 16+capacity iff this formula is satisfiable; capacity is 4 or 5."""
    validate_configuration(config)
    require(type(capacity) is int and capacity in (4, 5), "rank budget")
    formula = Formula()
    matrix = pairing(config, formula)
    active = []
    residuals = []
    for j in range(3):
        residual = schur(config, matrix, j, formula)
        residuals.append(residual)
        active.extend(factor(formula, residual, j, capacity))
    cardinality_start = len(formula.clauses)
    # At most capacity of 3*capacity bits: forbid every (capacity+1)-subset.
    for subset in combinations(active, capacity+1):
        formula.clause([-x for x in subset])
    return formula, residuals, cardinality_start
