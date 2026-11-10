#!/usr/bin/env python3
"""Upper bound for the odd-character window of the P120 odd graph.

Characteristic not 2 or 3: the matrix 3I-A has rank 36.
Characteristic 3: an explicit degree-at-most-2 factorisation has rank 45.
No kappa claim. Standard library only.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PORTS_SHA256 = "691c7b7d212112115b1bfc76db89f90d304ec448dc8c4a0c43d9a5954317146c"
P = 10007


def require(ok, message):
    if not ok:
        raise SystemExit("FAIL: " + message)


def weight(v):
    return bin(v).count("1")


def odd_dot(a, b):
    return bin(a & b).count("1") & 1


def hand_degree(u):
    """Degree in the odd graph, by the case split in PROOF.md."""
    coords = [i for i in range(9) if (u >> i) & 1]
    outside = [i for i in range(9) if not ((u >> i) & 1)]
    if weight(u) == 3:
        weight3 = 3 * (6 * 5 // 2)  # one point of u, two of the six outside
        weight7 = (6 * 5 // 2) + 3  # complement 2-set misses u, or sits inside u
        return weight3 + weight7
    complement = outside  # weight 2
    require(len(complement) == 2 and len(coords) == 7, "weight-7 shape")
    weight3 = (7 * 6 * 5 // 6) + 7  # 3-set outside the complement, or the complement plus one
    # other weight-7 vectors whose complement 2-set is disjoint from this one
    weight7 = 7 * 6 // 2
    return weight3 + weight7


def p120():
    return [v for v in range(1 << 9) if weight(v) % 4 == 3]


def load_p104():
    raw = (ROOT / "data" / "ports_p104.json").read_bytes()
    import hashlib
    require(hashlib.sha256(raw).hexdigest() == PORTS_SHA256, "P104 port-list bytes changed")
    ports = json.loads(raw)["ports"]
    require(len(ports) == len(set(ports)) == 104, "P104 is not 104 distinct ports")
    return ports


def rank_mod(rows, p):
    matrix = [row[:] for row in rows]
    n = len(matrix)
    m = len(matrix[0])
    rank = 0
    for col in range(m):
        pivot = None
        for i in range(rank, n):
            if matrix[i][col] % p:
                pivot = i
                break
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        inv = pow(matrix[rank][col], -1, p)
        for j in range(col, m):
            matrix[rank][j] = matrix[rank][j] * inv % p
        for i in range(n):
            if i == rank or matrix[i][col] % p == 0:
                continue
            factor = matrix[i][col] % p
            for j in range(col, m):
                matrix[i][j] = (matrix[i][j] - factor * matrix[rank][j]) % p
        rank += 1
    return rank


def pattern_matrix(vertices):
    """H = 3I - A over Z, as a dense integer matrix. Zeros sit on non-edges."""
    n = len(vertices)
    rows = [[0] * n for _ in range(n)]
    for i, u in enumerate(vertices):
        rows[i][i] = 3
        for j in range(i + 1, n):
            if odd_dot(u, vertices[j]):
                rows[i][j] = -1
                rows[j][i] = -1
    return rows


def valid_pattern(rows, vertices, p=None):
    """Unit-or-nonzero diagonal and zeros on unordered orthogonal pairs."""
    n = len(vertices)
    for i, u in enumerate(vertices):
        diag = rows[i][i] if p is None else rows[i][i] % p
        if diag == 0:
            return False
        for j in range(i + 1, n):
            entry = rows[i][j] if p is None else rows[i][j] % p
            orthogonal = not odd_dot(u, vertices[j])
            if orthogonal and entry != 0:
                return False
            other = rows[j][i] if p is None else rows[j][i] % p
            if orthogonal and other != 0:
                return False
    return True


def neighbor_data(vertices):
    n = len(vertices)
    lists = []
    bits = []
    for i, u in enumerate(vertices):
        nbrs = [j for j, v in enumerate(vertices) if i != j and odd_dot(u, v)]
        mask = 0
        for j in nbrs:
            mask |= 1 << j
        lists.append(nbrs)
        bits.append(mask)
    return lists, bits


def parameter_census(vertices):
    """Return (degree set, lambda set, mu set) by two independent pair counts."""
    lists, bits = neighbor_data(vertices)
    degrees = {len(nbrs) for nbrs in lists}
    lam_bits, mu_bits = set(), set()
    lam_sets, mu_sets = set(), set()
    n = len(vertices)
    as_sets = [set(nbrs) for nbrs in lists]
    for i in range(n):
        for j in range(i + 1, n):
            common_bits = (bits[i] & bits[j]).bit_count()
            common_sets = len(as_sets[i] & as_sets[j])
            require(common_bits == common_sets, "bitset and set censuses disagree")
            adjacent = ((bits[i] >> j) & 1) == 1
            if adjacent:
                lam_bits.add(common_bits)
                lam_sets.add(common_sets)
            else:
                mu_bits.add(common_bits)
                mu_sets.add(common_sets)
    require(lam_bits == lam_sets and mu_bits == mu_sets, "lambda/mu census mismatch")
    return degrees, lam_bits, mu_bits


def connected(bits):
    n = len(bits)
    seen = 0
    stack = [0]
    seen |= 1
    while stack:
        i = stack.pop()
        mask = bits[i]
        while mask:
            low = mask & -mask
            j = low.bit_length() - 1
            mask ^= low
            if (seen >> j) & 1:
                continue
            seen |= 1 << j
            stack.append(j)
    return seen == (1 << n) - 1


def multiplicities(n, k, theta, tau):
    """Solve 1+f+g = n and k + f*theta + g*tau = 0."""
    # f + g = n - 1
    # theta f + tau g = -k
    # f = ((n-1)*tau + k) / (tau - theta) wait, derive explicitly below.
    den = theta - tau
    require(den != 0, "repeated restricted eigenvalues")
    # theta f + tau ((n-1)-f) = -k, so (theta-tau) f = -k - tau(n-1).
    num = -k - tau * (n - 1)
    require(num % den == 0, "non-integral multiplicity")
    f = num // den
    g = (n - 1) - f
    return f, g


def principal(rows, index):
    return [[rows[i][j] for j in index] for i in index]


def odd_cliques(vertices, size):
    found = []

    def rec(start, chosen):
        if len(chosen) == size:
            found.append(list(chosen))
            return
        for i in range(start, len(vertices)):
            v = vertices[i]
            if all(odd_dot(v, vertices[j]) for j in chosen):
                chosen.append(i)
                rec(i + 1, chosen)
                chosen.pop()

    rec(0, [])
    return found


def features(v):
    bits = [(v >> i) & 1 for i in range(9)]
    coords = bits[:]
    for i in range(9):
        for j in range(i + 1, 9):
            coords.append(bits[i] * bits[j])
    return coords


def solve_column(phi, equations, p):
    """Solve phi[i] · y = rhs for each (i, rhs). Free variables are set to 0."""
    width = len(phi[0])
    matrix = []
    for i, rhs in equations:
        matrix.append(phi[i][:] + [rhs % p])
    where = [None] * width
    rank = 0
    for col in range(width):
        pivot = None
        for i in range(rank, len(matrix)):
            if matrix[i][col] % p:
                pivot = i
                break
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        inv = pow(matrix[rank][col], -1, p)
        for k in range(col, width + 1):
            matrix[rank][k] = matrix[rank][k] * inv % p
        for i in range(len(matrix)):
            if i == rank or matrix[i][col] % p == 0:
                continue
            factor = matrix[i][col] % p
            for k in range(col, width + 1):
                matrix[i][k] = (matrix[i][k] - factor * matrix[rank][k]) % p
        where[col] = rank
        rank += 1
    for i in range(rank, len(matrix)):
        if matrix[i][width] % p:
            return None
    solution = [0] * width
    for col in range(width):
        if where[col] is not None:
            solution[col] = matrix[where[col]][width] % p
    return solution


def char3_factorisation(vertices):
    p = 3
    phi = [[c % p for c in features(v)] for v in vertices]
    n = len(vertices)
    orthogonal = [[] for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if not odd_dot(vertices[i], vertices[j]):
                orthogonal[i].append(j)
                orthogonal[j].append(i)
    columns = []
    for j in range(n):
        equations = [(i, 0) for i in orthogonal[j]] + [(j, 1)]
        solution = solve_column(phi, equations, p)
        if solution is None:
            return None
        for i, rhs in equations:
            got = sum(phi[i][t] * solution[t] for t in range(len(solution))) % p
            require(got == rhs % p, "char-3 column solution does not meet its equations")
        columns.append(solution)
    rows = []
    for u in range(n):
        row = []
        for v in range(n):
            row.append(sum(phi[u][t] * columns[v][t] for t in range(len(phi[0]))) % p)
        rows.append(row)
    return rows


def linear_only_failures(vertices):
    """Degree-1 features are not enough for a char-3 column at every vertex."""
    p = 3
    phi = [[(v >> i) & 1 for i in range(9)] for v in vertices]
    n = len(vertices)
    failed = 0
    for j in range(0, n, 17):
        equations = [(i, 0) for i in range(n) if i != j and not odd_dot(vertices[i], vertices[j])]
        equations.append((j, 1))
        if solve_column(phi, equations, p) is None:
            failed += 1
    return failed


def main():
    vertices = p120()
    require(hand_degree(next(v for v in vertices if weight(v) == 3)) == 63, "hand count, weight 3")
    require(hand_degree(next(v for v in vertices if weight(v) == 7)) == 63, "hand count, weight 7")
    require(len(vertices) == 120, "P120 does not have 120 vectors")
    require(sorted(weight(v) for v in vertices)[0] == 3 and max(map(weight, vertices)) == 7,
            "P120 is not the weight-3 and weight-7 vectors")
    require(sum(weight(v) == 3 for v in vertices) == 84, "weight-3 count")
    require(sum(weight(v) == 7 for v in vertices) == 36, "weight-7 count")

    degrees, lambdas, mus = parameter_census(vertices)
    require(degrees == {63}, "degree is not constantly 63: %s" % sorted(degrees))
    require(lambdas == {30}, "lambda is not constantly 30: %s" % sorted(lambdas))
    require(mus == {36}, "mu is not constantly 36: %s" % sorted(mus))
    _, bits = neighbor_data(vertices)
    require(connected(bits), "P120 odd graph is disconnected")
    print("PASS_SRG_PARAMETERS n=120 k=63 lambda=30 mu=36")

    # Eigenvalues of an srg(120,63,30,36): discriminant (lambda-mu)^2 + 4(k-mu) = 36+108 = 144.
    delta = (30 - 36) ** 2 + 4 * (63 - 36)
    require(delta == 144, "discriminant")
    root = 12  # sqrt(144)
    theta = ((30 - 36) + root) // 2
    tau = ((30 - 36) - root) // 2
    require((theta, tau) == (3, -9), "restricted eigenvalues")
    f, g = multiplicities(120, 63, theta, tau)
    require((f, g) == (84, 35), "multiplicities f,g = %s,%s" % (f, g))
    require(63 + f * theta + g * tau == 0, "trace")
    require(1 + f + g == 120, "multiplicity sum")
    print("PASS_EIGENVALUE_ARITHMETIC theta=3 mult=84 tau=-9 mult=35")

    host = pattern_matrix(vertices)
    require(valid_pattern(host, vertices), "3I-A is not a 1-block pattern over Z")
    for prime in (5, 7, 11, P):
        reduced = [[entry % prime for entry in row] for row in host]
        require(valid_pattern(reduced, vertices, prime), "3I-A dies as a pattern mod %d" % prime)
        require(rank_mod(reduced, prime) == 36, "rank of 3I-A mod %d is not 36" % prime)
    print("PASS_RANK36_ODD_CHAR primes=5,7,11,10007")

    # Characteristic 3 kills this particular matrix: diagonal 3 ≡ 0.
    reduced3 = [[entry % 3 for entry in row] for row in host]
    require(all(row[i] % 3 == 0 for i, row in enumerate(reduced3)),
            "control: char 3 should kill the diagonal of 3I-A")
    require(not valid_pattern(reduced3, vertices, 3), "control: 3I-A must be illegal in char 3")

    # A nonzero orthogonal entry is rejected.
    planted = [row[:] for row in host]
    pair = next((i, j) for i in range(120) for j in range(i + 1, 120)
                if not odd_dot(vertices[i], vertices[j]))
    planted[pair[0]][pair[1]] = 5
    planted[pair[1]][pair[0]] = 5
    require(not valid_pattern(planted, vertices), "control: planted orthogonal entry was accepted")
    print("PASS_PATTERN_CONTROLS")

    ports = load_p104()
    require(set(ports) <= set(vertices), "P104 is not inside P120")
    require(sum(weight(v) == 3 for v in ports) == 70, "P104 weight-3 count")
    require(sum(weight(v) == 7 for v in ports) == 34, "P104 weight-7 count")
    index = {v: i for i, v in enumerate(vertices)}
    p104_index = [index[v] for v in ports]
    p104_rows = principal(host, p104_index)
    require(valid_pattern(p104_rows, ports), "induced 3I-A on P104 is not a pattern")
    require(rank_mod([[x % P for x in row] for row in p104_rows], P) <= 36, "P104 window matrix exceeds rank 36")
    p104_degrees = {sum(odd_dot(u, v) for v in ports if v != u) for u in ports}
    require(p104_degrees == {55}, "P104 is not 55-regular: %s" % sorted(p104_degrees))

    deleted = [v for v in vertices if v not in set(ports)]
    require(len(deleted) == 16, "deleted set")
    cliques = odd_cliques(deleted, 8)
    require(len(cliques) == 2, "expected two deleted 8-cliques, found %d" % len(cliques))
    for clique in cliques:
        extra = [deleted[i] for i in clique]
        block = ports + extra
        rows = principal(host, [index[v] for v in block])
        require(len(block) == 112 and valid_pattern(rows, block), "P112 pattern")
        require(rank_mod([[x % P for x in row] for row in rows], P) <= 36, "P112 rank")
    print("PASS_INDUCED_SUBSETS p104_regular=55 p112_cliques=2")

    char3 = char3_factorisation(vertices)
    require(char3 is not None, "char-3 degree-2 systems are inconsistent")
    require(valid_pattern(char3, vertices, 3), "char-3 factorisation is not a pattern")
    char3_rank = rank_mod(char3, 3)
    require(char3_rank == 38, "char-3 rank %d is not 38" % char3_rank)
    p104_char3 = principal(char3, p104_index)
    require(valid_pattern(p104_char3, ports, 3), "char-3 P104 principal submatrix")
    require(rank_mod(p104_char3, 3) <= char3_rank, "principal rank rose")
    failed_linear = linear_only_failures(vertices)
    require(failed_linear >= 1, "control: linear features unexpectedly solved every sampled column")
    print("PASS_CHAR3_FACTORISATION rank=%d linear_failures=%d" % (char3_rank, failed_linear))

    # The all-ones matrix is the wrong mask.
    ones = [[1] * 120 for _ in range(120)]
    require(not valid_pattern(ones, vertices), "control: all-ones was accepted")
    print("PASS_ODD_CHAR_WINDOW rank36=36 char3_rank=%d" % char3_rank)


if __name__ == "__main__":
    main()
