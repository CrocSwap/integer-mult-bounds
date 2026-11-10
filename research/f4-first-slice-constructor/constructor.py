"""Fixed-F4 port of PR6543's first-success raw-pencil constructor.

Base arithmetic is supplied by Ali Romman's authenticated PR5664 Field.
Credit ToikY/6543, Nick Petalas/6451, and classical Bareiss/Frobenius/
Berlekamp methods. OpenAI Codex assistance; Apache-2.0.
"""


def need(condition, message):
    if not condition:
        raise ValueError(message)


def backend_check(f):
    need((f.p, f.e, f.q, tuple(f.modulus)) == (2, 2, 4, (1, 1, 1)), "fixed F4 backend")
    need(f.mul[2][2] == 3 and f.mul[2][3] == 1 and f.add[2][3] == 1,
         "nonprime arithmetic")


def trim(a):
    out = list(a)
    need(all(type(x) is int and 0 <= x < 4 for x in out), "polynomial coefficient")
    while len(out) > 1 and out[-1] == 0:
        out.pop()
    return tuple(out or [0])


def add(a, b, f):
    return trim([f.add[a[i] if i < len(a) else 0][b[i] if i < len(b) else 0]
                 for i in range(max(len(a), len(b)))])


def neg(a, f):
    return trim([f.neg[x] for x in a])


def sub(a, b, f):
    return add(a, neg(b, f), f)


def mul(a, b, f):
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i+j] = f.add[out[i+j]][f.mul[x][y]]
    return trim(out)


def divmod_poly(a, b, f):
    need(b != (0,), "zero polynomial divisor")
    rest = list(trim(a))
    quotient = [0] * max(1, len(rest)-len(b)+1)
    while tuple(rest) != (0,) and len(rest) >= len(b):
        k = len(rest)-len(b)
        c = f.mul[rest[-1]][f.inv[b[-1]]]
        quotient[k] = c
        for j, value in enumerate(b):
            rest[k+j] = f.add[rest[k+j]][f.neg[f.mul[c][value]]]
        rest = list(trim(rest))
    return trim(quotient), tuple(rest)


def exact_div(a, b, f):
    quotient, remainder = divmod_poly(a, b, f)
    need(remainder == (0,), "nonexact Bareiss division")
    return quotient


def monic(a, f):
    need(a != (0,), "zero monic polynomial")
    return trim([f.mul[x][f.inv[a[-1]]] for x in a])


def gcd(a, b, f):
    while b != (0,):
        a, b = b, divmod_poly(a, b, f)[1]
    return monic(a, f)


def modpow(a, exponent, h, f):
    need(type(exponent) is int and exponent >= 0, "polynomial power")
    out = (1,)
    a = divmod_poly(a, h, f)[1]
    while exponent:
        if exponent & 1:
            out = divmod_poly(mul(out, a, f), h, f)[1]
        a = divmod_poly(mul(a, a, f), h, f)[1]
        exponent >>= 1
    return out


def input_check(a, b):
    need(type(a) is list and type(b) is list, "matrix arrays")
    n = len(a)
    need(n <= 17 and len(b) == n, "matrix dimension")
    for matrix in (a, b):
        for row in matrix:
            need(type(row) is list and len(row) == n, "square matrix")
            need(all(type(x) is int and 0 <= x < 4 for x in row), "F4 entry")
    return n


def determinant(matrix, f):
    work, out = [row[:] for row in matrix], 1
    for k in range(len(work)):
        pivot = next((i for i in range(k, len(work)) if work[i][k]), None)
        if pivot is None:
            return 0
        if pivot != k:
            work[pivot], work[k] = work[k], work[pivot]
            out = f.neg[out]
        value = work[k][k]
        out = f.mul[out][value]
        for i in range(k+1, len(work)):
            scale = f.mul[work[i][k]][f.inv[value]]
            for j in range(k+1, len(work)):
                work[i][j] = f.add[work[i][j]][f.neg[f.mul[scale][work[k][j]]]]
    return out


def trace_new():
    return {"polynomial_row_swaps": 0, "exact_polynomial_divisions": 0,
            "base_element_trials": 0, "frobenius_degrees": [],
            "largest_dense_degree": 0, "berlekamp_kernel_dimensions": [],
            "berlekamp_scalar_trials": 0, "berlekamp_splits": 0}


def bareiss(a, b, f, trace):
    n = len(a)
    if n == 0:
        return (1,)
    work = [[trim([b[i][j], a[i][j]]) for j in range(n)] for i in range(n)]
    previous, sign = (1,), 1
    for k in range(n-1):
        pivot = next((i for i in range(k, n) if work[i][k] != (0,)), None)
        if pivot is None:
            return (0,)
        if pivot != k:
            work[pivot], work[k] = work[k], work[pivot]
            sign = f.neg[sign]
            trace["polynomial_row_swaps"] += 1
        value = work[k][k]
        for i in range(k+1, n):
            for j in range(k+1, n):
                numerator = sub(mul(value, work[i][j], f),
                                mul(work[i][k], work[k][j], f), f)
                work[i][j] = exact_div(numerator, previous, f)
                trace["exact_polynomial_divisions"] += 1
            work[i][k] = (0,)
        previous = value
    return trim([f.mul[sign][x] for x in work[-1][-1]])


def kernel(matrix, f):
    work, pivots, row = [r[:] for r in matrix], [], 0
    cols = len(work[0]) if work else 0
    for col in range(cols):
        pivot = next((i for i in range(row, len(work)) if work[i][col]), None)
        if pivot is None:
            continue
        work[row], work[pivot] = work[pivot], work[row]
        inverse = f.inv[work[row][col]]
        work[row] = [f.mul[x][inverse] for x in work[row]]
        for i in range(len(work)):
            if i != row and work[i][col]:
                scale = work[i][col]
                work[i] = [f.add[x][f.neg[f.mul[scale][y]]] for x, y in zip(work[i], work[row])]
        pivots.append(col)
        row += 1
        if row == len(work):
            break
    basis = []
    for col in range(cols):
        if col not in pivots:
            vector = [0] * cols
            vector[col] = 1
            for i, pivot in enumerate(pivots):
                vector[pivot] = f.neg[work[i][col]]
            basis.append(vector)
    return basis


def one_factor(polynomial, degree, f, trace):
    current = monic(polynomial, f)
    while len(current)-1 > degree:
        m = len(current)-1
        columns = [modpow((0,)*j+(1,), f.q, current, f) for j in range(m)]
        matrix = [[f.add[columns[j][i] if i < len(columns[j]) else 0][f.neg[int(i == j)]]
                   for j in range(m)] for i in range(m)]
        basis = kernel(matrix, f)
        vector = next((trim(v) for v in basis if any(v[1:])), None)
        need(vector is not None, "Berlekamp nonconstant fixed vector")
        trace["berlekamp_kernel_dimensions"].append(len(basis))
        factor = None
        for c in range(f.q):
            candidate = gcd(current, sub(vector, (c,), f), f)
            trace["berlekamp_scalar_trials"] += 1
            if 1 < len(candidate) < len(current):
                factor = candidate
                break
        need(factor is not None, "Berlekamp proper split")
        current = factor
        trace["berlekamp_splits"] += 1
    need(len(current) == degree+1, "factor degree")
    return current


def evaluate(poly, x, h, f):
    out = (0,)
    for value in reversed(poly):
        out = add(divmod_poly(mul(out, x, f), h, f)[1], (value,), f)
    return out


def choose_slice(a, b, f, trace):
    if determinant(a, f):
        return 1, True, (0, 1), None
    polynomial = bareiss(a, b, f, trace)
    need(polynomial != (0,), "nonregular pencil")
    for c in range(min(f.q, len(a)+1)):
        trace["base_element_trials"] += 1
        if evaluate(polynomial, (c,), (0, 1), f) != (0,):
            return 1, False, (0, 1), (c,)
    n = len(a)
    need(f.q < n, "base failure dimension")
    for e in range(2, n+1):
        power = f.q ** e
        need(power < n*n, "dense Frobenius size")
        frobenius = [0] * (power+1)
        frobenius[1], frobenius[-1] = f.neg[1], 1
        divisor = gcd(polynomial, tuple(frobenius), f)
        trace["frobenius_degrees"].append([e, len(divisor)-1])
        trace["largest_dense_degree"] = power
        if len(divisor)-1 < power:
            missing = exact_div(tuple(frobenius), divisor, f)
            return e, False, one_factor(missing, e, f, trace), (0, 1)
    raise ValueError("UNKNOWN degree cap")


def emul(x, y, h, f):
    return divmod_poly(mul(x, y, f), h, f)[1]


def inverse_matrix(matrix, h, f):
    n = len(matrix)
    work = [row[:] + [(int(i == j),) for j in range(n)] for i, row in enumerate(matrix)]
    for k in range(n):
        pivot = next((i for i in range(k, n) if work[i][k] != (0,)), None)
        need(pivot is not None, "singular returned slice")
        work[k], work[pivot] = work[pivot], work[k]
        inverse = modpow(work[k][k], f.q ** (len(h)-1)-2, h, f)
        work[k] = [emul(x, inverse, h, f) for x in work[k]]
        for i in range(n):
            if i != k:
                scale = work[i][k]
                work[i] = [sub(x, emul(scale, y, h, f), f) for x, y in zip(work[i], work[k])]
    return [row[n:] for row in work]


def product(a, b, h, f):
    n = len(a)
    out = [[(0,) for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for j in range(n):
            for k in range(n):
                out[i][j] = add(out[i][j], emul(a[i][k], b[k][j], h, f), f)
    return out


def irreducible(h, f):
    e = len(h)-1
    if e == 1:
        return True
    x = divmod_poly((0, 1), h, f)[1]
    power = x
    for j in range(1, e+1):
        power = modpow(power, f.q, h, f)
        if j <= e//2 and gcd(h, sub(power, x, f), f) != (1,):
            return False
    return power == x


def canonical_element(x, e):
    need(type(x) in (list, tuple) and 1 <= len(x) <= e, "field element length")
    need(tuple(x) == trim(x), "noncanonical field element")
    return tuple(x)


def validate_answer(a, b, answer, f):
    n = input_check(a, b)
    e, infinity = answer["e"], answer["infinity"]
    need(type(e) is int and 1 <= e <= max(1, n), "answer degree")
    need(type(infinity) is bool, "infinity boolean")
    h = answer["field_modulus"]
    need(type(h) in (list, tuple) and len(h) == e+1 and h[-1] == 1, "field modulus degree")
    h = trim(h)
    need(irreducible(h, f), "reducible field modulus")
    alpha = None if infinity else canonical_element(answer["alpha"], e)
    need(not infinity or (e == 1 and answer["alpha"] is None), "infinity degree")
    expected = [[(a[i][j],) if infinity else
                 add(emul(alpha, (a[i][j],), h, f), (b[i][j],), f)
                 for j in range(n)] for i in range(n)]
    actual, inverse = [], []
    for key, out in (("slice", actual), ("inverse", inverse)):
        matrix = answer[key]
        need(type(matrix) is list and len(matrix) == n, "witness matrix dimension")
        for row in matrix:
            need(type(row) is list and len(row) == n, "witness square matrix")
            out.append([canonical_element(x, e) for x in row])
    need(actual == expected, "literal slice binding")
    identity = [[(int(i == j),) for j in range(n)] for i in range(n)]
    need(product(actual, inverse, h, f) == identity, "right inverse")
    need(product(inverse, actual, h, f) == identity, "left inverse")
    if e > 1:
        need(f.q < n and f.q ** e < n*n, "answer dense bound")
        need(determinant(a, f) == 0, "earlier infinity success")
        polynomial = bareiss(a, b, f, trace_new())
        for j in range(1, e):
            power = [0] * (f.q ** j+1)
            power[1], power[-1] = f.neg[1], 1
            need(len(gcd(polynomial, tuple(power), f))-1 == f.q ** j, "earlier affine success")
    return True


def assemble(a, b, e, infinity, h, alpha, f, trace):
    n = len(a)
    matrix = [[(a[i][j],) if infinity else
               add(emul(alpha, (a[i][j],), h, f), (b[i][j],), f)
               for j in range(n)] for i in range(n)]
    return {"e": e, "infinity": infinity, "field_modulus": list(h),
            "alpha": None if alpha is None else list(alpha),
            "slice": [[list(x) for x in row] for row in matrix],
            "inverse": [[list(x) for x in row] for row in inverse_matrix(matrix, h, f)],
            "trace": trace}


def construct(a, b, f):
    backend_check(f)
    input_check(a, b)
    trace = trace_new()
    e, infinity, h, alpha = choose_slice(a, b, f, trace)
    answer = assemble(a, b, e, infinity, h, alpha, f, trace)
    validate_answer(a, b, answer, f)
    return answer
