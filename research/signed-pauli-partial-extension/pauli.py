"""Complete partial Hermitian Pauli conjugations; exact binary arithmetic.

Prepared for JoyboyBrian with substantial OpenAI Codex assistance. Apache-2.0.
"""
from math import prod


def need(condition, message):
    if not condition:
        raise ValueError(message)


def parity(value):
    return value.bit_count() & 1


def omega(a, b, n):
    mask = (1 << n) - 1
    return parity(((a & mask) & (b >> n)) ^ ((a >> n) & (b & mask)))


def label(p, n):
    return p[0] | (p[1] << n)


def multiply(a, b):
    return a[0] ^ b[0], a[1] ^ b[1], (a[2] + b[2] + 2 * parity(a[1] & b[0])) % 4


def span_coordinates(rows, value):
    pivots = {}
    for j, row in enumerate(rows):
        tag = 1 << j
        while row and row.bit_length() - 1 in pivots:
            old, coefficient = pivots[row.bit_length() - 1]
            row ^= old
            tag ^= coefficient
        if row:
            pivots[row.bit_length() - 1] = row, tag
    coefficient = 0
    while value and value.bit_length() - 1 in pivots:
        old, tag = pivots[value.bit_length() - 1]
        value ^= old
        coefficient ^= tag
    return None if value else coefficient


def rank(rows):
    independent = []
    for row in rows:
        if span_coordinates(independent, row) is None:
            independent.append(row)
    return len(independent)


def solve(rows, rhs, width):
    """Solve binary equations, taking all free variables zero."""
    pivots = {}
    for row, bit in zip(rows, rhs):
        while row and row.bit_length() - 1 in pivots:
            old, value = pivots[row.bit_length() - 1]
            row ^= old
            bit ^= value
        if not row:
            need(not bit, "inconsistent internal linear system")
        else:
            pivots[row.bit_length() - 1] = row, bit
    value = 0
    for pivot, (row, bit) in sorted(pivots.items()):
        if bit ^ parity(row & value):
            value |= 1 << pivot
    need(value < (1 << width), "linear-system width")
    return value


def dual(vector, n):
    mask = (1 << n) - 1
    return (vector >> n) | ((vector & mask) << n)


def apply_gate(pauli, gate):
    x, z, phase = pauli
    if gate[0] == "turn":
        a, b, sign = gate[1:]
        if parity((a & z) ^ (b & x)):
            phase += (a & b).bit_count() + 2 * parity(b & x) - sign
            x ^= a
            z ^= b
    elif gate[0] == "x":
        phase += 2 * parity(z & gate[1])
    elif gate[0] == "s":
        phase += gate[2] * (x & gate[1]).bit_count()
        if gate[2] % 2:
            z ^= x & gate[1]
    else:
        need(gate[0] == "phase", "unknown literal gate")
    return x, z, phase % 4


def apply_word(pauli, gates):
    for gate in gates:
        pauli = apply_gate(pauli, gate)
    return pauli


def validate(n, constraints):
    need(type(n) is int and 0 <= n <= 9, "reference n must be 0..9")
    for pair in constraints:
        need(len(pair) == 2, "constraint pair length")
        for p in pair:
            need(len(p) == 3 and all(type(v) is int for v in p), "typed Pauli triple")
            x, z, phase = p
            need(0 <= x < (1 << n) and 0 <= z < (1 << n) and 0 <= phase < 4,
                 "Pauli range")
            need(phase % 2 == parity(x & z), "Hermitian Pauli required")


def analyze(n, constraints):
    validate(n, constraints)
    selected, source, target = [], [], []
    for j, (p, q) in enumerate(constraints):
        if span_coordinates(source, label(p, n)) is None:
            selected.append(j)
            source.append(label(p, n))
            target.append(label(q, n))
    if rank(target) != len(target):
        return None, "label-relations"
    for i, v in enumerate(source):
        for j, w in enumerate(source):
            if omega(v, w, n) != omega(target[i], target[j], n):
                return None, "commutators"
    for p, q in constraints:
        coordinate = span_coordinates(source, label(p, n))
        pp = qq = (0, 0, 0)
        for j, index in enumerate(selected):
            if coordinate & (1 << j):
                pp = multiply(pp, constraints[index][0])
                qq = multiply(qq, constraints[index][1])
        if label(qq, n) != label(q, n):
            return None, "label-relations"
        if (pp[2] - p[2]) % 4 != (qq[2] - q[2]) % 4:
            return None, "central-relations"
    restricted = [sum(omega(a, b, n) << j for j, b in enumerate(source)) for a in source]
    k, twice_r = len(source), rank(restricted)
    need(twice_r % 2 == 0, "alternating rank must be even")
    return {"indices": selected, "source": source, "target": target,
            "k": k, "r": twice_r // 2, "t": k - twice_r}, "compatible"


def sp_order(n):
    return (1 << (n * n)) * prod((1 << (2 * j)) - 1 for j in range(1, n + 1))


def completion_count(n, data):
    ambient = n - data["r"]
    orbit = prod((1 << (2 * ambient - j)) - (1 << j) for j in range(data["t"]))
    symplectic = sp_order(ambient)
    need(symplectic % orbit == 0, "pointwise stabilizer quotient")
    return (1 << (2 * n - data["k"])) * (symplectic // orbit)


def complete(n, constraints):
    """Return projective count and an actual chosen dyadic Clifford word."""
    data, reason = analyze(n, constraints)
    if data is None:
        return {"count": 0, "reason": reason, "gates": None}
    columns = [1 << i for i in range(2 * n)]
    fixed, gates = [], []
    mask = (1 << n) - 1
    for source, target in zip(data["source"], data["target"]):
        current = 0
        for j, column in enumerate(columns):
            if source & (1 << j):
                current ^= column
        axes = []
        if current != target:
            if omega(current, target, n):
                axes = [current ^ target]
            else:
                rows = [dual(p, n) for p in (*fixed, current, target)]
                rhs = [omega(current, p, n) for p in fixed] + [1, 1]
                middle = solve(rows, rhs, 2 * n)
                axes = [current ^ middle, middle ^ target]
        for axis in axes:
            need(axis != 0 and all(not omega(axis, p, n) for p in fixed), "fixed-prefix axis")
            columns = [v ^ (axis if omega(v, axis, n) else 0) for v in columns]
            gates.append(["turn", axis & mask, axis >> n, 1])
        fixed.append(target)
    rhs = []
    for index in data["indices"]:
        p, q = constraints[index]
        actual = apply_word(tuple(p), gates)
        need(label(actual, n) == label(q, n) and (q[2] - actual[2]) % 2 == 0,
             "unsigned symplectic completion")
        rhs.append(((q[2] - actual[2]) % 4) // 2)
    correction = solve([dual(p, n) for p in data["target"]], rhs, 2 * n)
    if correction & mask:
        gates.append(["x", correction & mask])
    if correction >> n:
        gates.append(["s", correction >> n, 2])
    need(all(apply_word(tuple(p), gates) == tuple(q) for p, q in constraints), "signed completion")
    tableau = [apply_word((1 << j, 0, 0), gates) for j in range(n)]
    tableau += [apply_word((0, 1 << j, 0), gates) for j in range(n)]
    return {"count": completion_count(n, data), "reason": reason,
            "gates": gates, "tableau": tableau,
            "dimensions": {k: data[k] for k in ("k", "r", "t")},
            "global_phase_contract": "literal word chooses its own phase; no supplied target equality"}
