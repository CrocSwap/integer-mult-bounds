"""Compute exact stabilizer matrix elements by elimination of binary path variables."""


def indices(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def subset_xor(rows, mask):
    value = 0
    for i in indices(mask):
        value ^= rows[i]
    return value


class Quadratic:
    """Store c + sum a[j] x[j] + 2 sum b[i,j] x[i] x[j] modulo four."""

    def __init__(self, size):
        self.constant = 0
        self.linear = [0] * size
        self.edges = [0] * size
        self.active = (1 << size) - 1

    def add_linear(self, affine, weight):
        """The low bit of affine is the constant. Each other bit names a variable."""
        if affine & 1:
            self.constant += weight
            weight = -weight
        variables = affine >> 1
        for i in indices(variables):
            self.linear[i] += weight
            if weight & 1:
                self.edges[i] ^= variables ^ (1 << i)

    def add_cross(self, a, b):
        """Add twice the product of two affine bits."""
        self.constant += 2 * ((a & b) & 1)
        x, y = a >> 1, b >> 1
        diagonal = (x & y) ^ (y if a & 1 else 0) ^ (x if b & 1 else 0)
        for i in indices(diagonal):
            self.linear[i] += 2
        for i in indices(x | y):
            bit = 1 << i
            edges = (y if x & bit else 0) ^ (x if y & bit else 0)
            self.edges[i] ^= edges & ~bit

    def remove(self, i):
        bit = 1 << i
        self.active ^= bit
        for j in indices(self.edges[i]):
            self.edges[j] ^= bit
        self.edges[i] = 0

    def sum(self):
        """Return (sqrt-two exponent, eighth-root phase). None denotes zero."""
        shift = eighth = 0
        while self.active:
            x = next(indices(self.active))
            neighbours = self.edges[x]
            a = self.linear[x] % 4
            self.remove(x)
            if a & 1:
                shift += 1
                eighth += 1 if a == 1 else -1
                self.add_linear(neighbours << 1, -a)
            elif neighbours:
                y = next(indices(neighbours))
                replacement = ((neighbours ^ (1 << y)) << 1) | (a >> 1)
                rest = self.edges[y]
                self.remove(y)
                self.add_linear(replacement, self.linear[y])
                self.add_cross(replacement, rest << 1)
                shift += 2
            elif a:
                return None
            else:
                shift += 2
        return shift, (eighth + 2 * self.constant) % 8


def restrictions(rows, address, paths):
    """Solve output-address equations and return one affine form per path bit."""
    equations = [v ^ ((address >> i) & 1) for i, v in enumerate(rows)]
    pivots = []
    for j in range(paths):
        bit = 2 << j
        p = next(
            (t for t in range(len(pivots), len(equations)) if equations[t] & bit), None
        )
        if p is None:
            continue
        k = len(pivots)
        equations[k], equations[p] = equations[p], equations[k]
        pivot = equations[k]
        for i in range(len(equations)):
            if i != k and equations[i] & bit:
                equations[i] ^= pivot
        pivots.append(j)
    if any(equations[len(pivots) :]):
        return None
    mask = sum(1 << j for j in pivots)
    forms = [0] * paths
    d = 0
    for i in range(paths):
        if not (mask >> i & 1):
            forms[i] = 2 << d
            d += 1
    for j, e in zip(pivots, equations):
        forms[j] = (e & 1) ^ subset_xor(forms, (e >> 1) & ~mask)
    return d, forms


def traverse(circuit, n, source, choices, phase=None):
    location = [(source >> i) & 1 for i in range(n)]
    for gate in circuit:
        tag = gate[0]
        if tag == "P":
            location = [subset_xor(location, row) for row in gate[1]]
        elif tag == "X":
            for j in indices(gate[1]):
                location[j] ^= 1
        elif tag == "C":
            choice = next(choices)
            if phase is not None:
                phase.add_linear(choice, -gate[2])
            for j in indices(gate[1]):
                location[j] ^= choice
        elif tag == "D":
            if phase is not None:
                for i, (q, a) in enumerate(zip(gate[1], gate[2], strict=True)):
                    if a:
                        phase.add_linear(location[i], a)
                    for j in indices(q & -(2 << i)):
                        phase.add_cross(location[i], location[j])
        elif tag == "phase":
            if phase is not None:
                phase.constant += gate[1]
        else:
            raise ValueError(f"Unknown Clifford gate {tag}")
    return location


def matrix_element(circuit, n, source, target):
    """Return sqrt(2)^s exp(i*pi*p/4) for one exact circuit entry."""
    signs = [g[2] for g in circuit if g[0] == "C"]
    paths = len(signs)
    if not paths:
        value = Quadratic(0)
        address = traverse(circuit, n, source, iter(()), value)
        if sum(v << i for i, v in enumerate(address)) != target:
            return None
        return 0, (2 * value.constant) % 8
    location = traverse(circuit, n, source, (2 << j for j in range(paths)))
    solution = restrictions(location, target, paths)
    if solution is None:
        return None
    dimension, forms = solution
    value = Quadratic(dimension)
    traverse(circuit, n, source, iter(forms), value)
    entry = value.sum()
    if entry is None:
        return None
    shift, phase = entry
    return shift - paths, (phase + sum(signs)) % 8
