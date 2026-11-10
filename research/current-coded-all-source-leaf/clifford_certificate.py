"""Independent Pauli-generator and absolute-column certificate arithmetic.

No retained Clifford tableau/matrix helper computes these expected values.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from all_leaf_sources import need

N = 9


def parity(value):
    return value.bit_count() % 2


def mv(rows, value):
    return sum(parity(row & value) << i for i, row in enumerate(rows))


def inverse(rows):
    size = len(rows)
    work = [row | (1 << (size+i)) for i, row in enumerate(rows)]
    for col in range(size):
        pivot = next((j for j in range(col, size) if work[j] >> col & 1), None)
        need(pivot is not None, "invertible literal binary matrix")
        work[col], work[pivot] = work[pivot], work[col]
        for j in range(size):
            if j != col and work[j] >> col & 1:
                work[j] ^= work[col]
    need([row & ((1 << size)-1) for row in work] == [1 << j for j in range(size)],
         "complete independent matrix inverse")
    return tuple(row >> size for row in work)


def rank(columns):
    pivots = {}
    for value in columns:
        while value:
            first = value.bit_length()-1
            if first not in pivots:
                pivots[first] = value
                break
            value ^= pivots[first]
    return len(pivots)


def qvalue(rows, linear, value):
    return (sum(linear[j] for j in range(N) if value >> j & 1)
            +2*sum(1 for j in range(N) for k in range(j+1, N)
                   if value >> j & 1 and value >> k & 1 and rows[j] >> k & 1)) % 4


def rotate(value, phase):
    a, b = value
    return ((a, b), (-b, a), (-a, -b), (b, -a))[phase % 4]


def multiply(a, b):
    return a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]


def pauli_gate(value, gate):
    x, z, p = value
    kind = gate[0]
    if kind == "P":
        inv = inverse(gate[1])
        z_new = 0
        for j in range(N):
            if z >> j & 1:
                z_new ^= inv[j]
        return mv(gate[1], x), z_new, p
    if kind == "X":
        return x, z, (p+2*parity(z & gate[1])) % 4
    if kind == "phase":
        return value
    if kind == "C":
        mask, sign = gate[1:]
        need(0 < mask < 1 << N and sign in (-1, 1), "source normalized signed C")
        return (x ^ mask, z, (p+3*sign) % 4) if parity(z & mask) else value
    need(kind == "D", "independent source primitive alphabet")
    rows, linear = gate[1:]
    difference = sum(((linear[j] % 2) & (x >> j & 1)) << j for j in range(N))
    for j in range(N):
        for k in range(j+1, N):
            if rows[j] >> k & 1:
                if x >> j & 1:
                    difference ^= 1 << k
                if x >> k & 1:
                    difference ^= 1 << j
    return x, z ^ difference, (p+qvalue(rows, linear, x)) % 4


def generators(circuit):
    answer = []
    for start in ([(1 << j, 0, 0) for j in range(N)]
                  +[(0, 1 << j, 0) for j in range(N)]):
        value = start
        for gate in circuit:
            value = pauli_gate(value, gate)
        answer.append(value)
    return tuple(answer)


def monomial_circuit(literal):
    return [("D", tuple(literal["quadratic_rows"]), tuple(literal["linear_Z4"])),
            ("P", tuple(literal["matrix_rows"])), ("X", literal["offset"]),
            ("phase", literal["phase"])]


def lowered_circuit(record):
    return (monomial_circuit(record["right"])
            +[("C", 1 << j, 1) for j in range(record["rank"])]
            +monomial_circuit(record["left"]))


def normalized(vector, denominator):
    while denominator and all(a % 2 == b % 2 == 0 for a, b in vector):
        vector = [(a//2, b//2) for a, b in vector]
        denominator -= 1
    return tuple(vector), denominator


def zero_column(circuit):
    values = [(0, 0)]*(1 << N)
    values[0] = (1, 0)
    denominator = 0
    for gate in circuit:
        kind = gate[0]
        if kind == "P":
            output = [(0, 0)]*len(values)
            for j, value in enumerate(values):
                output[mv(gate[1], j)] = value
            values = output
        elif kind == "X":
            values = [values[j ^ gate[1]] for j in range(len(values))]
        elif kind == "D":
            values = [rotate(value, qvalue(gate[1], gate[2], j)) for j, value in enumerate(values)]
        elif kind == "phase":
            values = [rotate(value, gate[1]) for value in values]
        elif kind == "C":
            mask, sign = gate[1:]
            need(0 < mask < 1 << N and sign in (-1, 1), "source normalized signed C")
            output = []
            for j, value in enumerate(values):
                a = multiply((1, sign), value)
                b = multiply((1, -sign), values[j ^ mask])
                output.append((a[0]+b[0], a[1]+b[1]))
            values = output; denominator += 1
        else:
            raise ValueError("independent source primitive alphabet")
    need(any(value != (0, 0) for value in values), "nonzero separating column")
    need(sum(a*a+b*b for a, b in values) == 1 << (2*denominator),
         "exact unit normalization of separating column")
    return normalized(values, denominator)


def certify(original, record):
    lowered = lowered_circuit(record)
    first, second = generators(original.circuit), generators(lowered)
    need(first == second, "all eighteen exact Pauli images")
    need(rank([x for x, _z, _p in first[N:]]) == record["rank"], "actual source Fourier rank")
    a, b = zero_column(original.circuit), zero_column(lowered)
    need(a == b, "exact separating column including absolute phase")
    return first, a
