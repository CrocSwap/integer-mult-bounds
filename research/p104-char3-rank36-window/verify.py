#!/usr/bin/env python3
"""Characteristic-3 rank-36 witness for the P104 port window.

No kappa claim. Standard library only.

The witness is one explicit 1-block pattern over F_3. It is not a census of
patterns. The class-constant ansatz is a separate, exhaustive algebraic check:
every matrix constant on the three relations has rank 120 in characteristic 3.
"""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PORTS_SHA256 = "691c7b7d212112115b1bfc76db89f90d304ec448dc8c4a0c43d9a5954317146c"
# sha256 of the 104x104 pattern in ports_p104.json order, entries in 0,1,2.
P104_MATRIX_SHA256 = "473541e0dcc7e2c22e879d37ebd3cd3e1f88c1de5c0306fd42fa38ff134c6e6a"
CLIQUE_RANK = {
    (7, 25, 42, 52, 76, 82, 97, 127): 36,
    (67, 104, 137, 162, 266, 289, 448, 491): 37,
}


def require(ok, message):
    if not ok:
        raise SystemExit("FAIL: " + message)


def weight(v):
    return bin(v).count("1")


def odd_dot(a, b):
    return (bin(a & b).count("1") & 1) == 1


def p120():
    return [v for v in range(1 << 9) if weight(v) % 4 == 3]


def features(v, constant):
    bits = [(v >> i) & 1 for i in range(9)]
    coords = [1] if constant else []
    coords.extend(bits)
    for i in range(9):
        for j in range(i + 1, 9):
            coords.append(bits[i] * bits[j])
    return coords


def rref_solve(phi, equations):
    """Unique solution supported on the pivot columns, or (None, None) if inconsistent.

    Free coordinates of the reduced row echelon form are set to 0. Pivot columns
    are exactly those of the unique RREF, so the particular solution does not
    depend on the order of the equations.
    """
    width = len(phi[0])
    matrix = [phi[i][:] + [rhs % 3] for i, rhs in equations]
    pivot_of = [None] * width
    rank = 0
    for col in range(width):
        pivot = None
        for row in range(rank, len(matrix)):
            if matrix[row][col] % 3:
                pivot = row
                break
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        inverse = pow(matrix[rank][col], -1, 3)
        for k in range(col, width + 1):
            matrix[rank][k] = matrix[rank][k] * inverse % 3
        for row in range(len(matrix)):
            if row == rank or matrix[row][col] % 3 == 0:
                continue
            factor = matrix[row][col] % 3
            for k in range(col, width + 1):
                matrix[row][k] = (matrix[row][k] - factor * matrix[rank][k]) % 3
        pivot_of[col] = rank
        rank += 1
    for row in range(rank, len(matrix)):
        if matrix[row][width] % 3:
            return None, None
    solution = [0] * width
    for col, row in enumerate(pivot_of):
        if row is not None:
            solution[col] = matrix[row][width] % 3
    free = [col for col, row in enumerate(pivot_of) if row is None]
    return solution, free


def null_basis(phi, equations):
    """Basis of the homogeneous solution space, one vector per free column."""
    width = len(phi[0])
    matrix = [phi[i][:] + [0] for i, _rhs in equations]
    # Reuse the inhomogeneous solver's elimination by calling rref on rhs 0
    # through the same pivot rule. Build it directly so the basis matches.
    pivot_of = [None] * width
    rank = 0
    for col in range(width):
        pivot = None
        for row in range(rank, len(matrix)):
            if matrix[row][col] % 3:
                pivot = row
                break
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        inverse = pow(matrix[rank][col], -1, 3)
        for k in range(col, width):
            matrix[rank][k] = matrix[rank][k] * inverse % 3
        for row in range(len(matrix)):
            if row == rank or matrix[row][col] % 3 == 0:
                continue
            factor = matrix[row][col] % 3
            for k in range(col, width):
                matrix[row][k] = (matrix[row][k] - factor * matrix[rank][k]) % 3
        pivot_of[col] = rank
        rank += 1
    basis = []
    for free in [col for col, row in enumerate(pivot_of) if row is None]:
        vector = [0] * width
        vector[free] = 1
        for col, row in enumerate(pivot_of):
            if row is not None:
                vector[col] = (-matrix[row][free]) % 3
        basis.append(vector)
    return basis


def rank_mod(rows):
    matrix = [row[:] for row in rows]
    if not matrix:
        return 0
    n = len(matrix)
    m = len(matrix[0])
    rank = 0
    for col in range(m):
        pivot = None
        for row in range(rank, n):
            if matrix[row][col] % 3:
                pivot = row
                break
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        inverse = pow(matrix[rank][col], -1, 3)
        for k in range(col, m):
            matrix[rank][k] = matrix[rank][k] * inverse % 3
        for row in range(n):
            if row == rank or matrix[row][col] % 3 == 0:
                continue
            factor = matrix[row][col] % 3
            for k in range(col, m):
                matrix[row][k] = (matrix[row][k] - factor * matrix[rank][k]) % 3
        rank += 1
    return rank


def rank_prime(rows, prime):
    matrix = [row[:] for row in rows]
    n = len(matrix)
    m = len(matrix[0])
    rank = 0
    for col in range(m):
        pivot = None
        for row in range(rank, n):
            if matrix[row][col] % prime:
                pivot = row
                break
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        inverse = pow(matrix[rank][col], -1, prime)
        for k in range(col, m):
            matrix[rank][k] = matrix[rank][k] * inverse % prime
        for row in range(n):
            if row == rank or matrix[row][col] % prime == 0:
                continue
            factor = matrix[row][col] % prime
            for k in range(col, m):
                matrix[row][k] = (matrix[row][k] - factor * matrix[rank][k]) % prime
        rank += 1
    return rank


def load_ports():
    raw = (ROOT / "data" / "ports_p104.json").read_bytes()
    require(hashlib.sha256(raw).hexdigest() == PORTS_SHA256, "P104 port bytes changed")
    ports = json.loads(raw)["ports"]
    require(len(ports) == len(set(ports)) == 104, "P104 is not 104 distinct ports")
    return ports


def orthogonal_lists(vertices):
    lists = [[] for _ in vertices]
    for i, u in enumerate(vertices):
        for j in range(i + 1, len(vertices)):
            if not odd_dot(u, vertices[j]):
                lists[i].append(j)
                lists[j].append(i)
    return lists


def factorisation(vertices, constant):
    phi = [[c % 3 for c in features(v, constant)] for v in vertices]
    orth = orthogonal_lists(vertices)
    columns = []
    nullities = []
    for j in range(len(vertices)):
        equations = [(i, 0) for i in orth[j]] + [(j, 1)]
        solution, free = rref_solve(phi, equations)
        require(solution is not None, "degree-2 system inconsistent at vertex %d" % j)
        for i, rhs in equations:
            got = sum(phi[i][t] * solution[t] for t in range(len(solution))) % 3
            require(got == rhs % 3, "solution misses an equation")
        columns.append(solution)
        nullities.append(len(free))
    width = len(phi[0])
    matrix = []
    for u in range(len(vertices)):
        matrix.append(
            [sum(phi[u][t] * columns[v][t] for t in range(width)) % 3 for v in range(len(vertices))]
        )
    return phi, orth, columns, nullities, matrix


def valid_pattern(matrix, vertices):
    n = len(vertices)
    for i, u in enumerate(vertices):
        if matrix[i][i] % 3 == 0:
            return False
        for j in range(i + 1, n):
            if odd_dot(u, vertices[j]):
                continue
            if matrix[i][j] % 3 or matrix[j][i] % 3:
                return False
    return True


def principal(matrix, index):
    return [[matrix[i][j] for j in index] for i in index]


def odd_cliques(vertices, size):
    found = []

    def rec(start, chosen):
        if len(chosen) == size:
            found.append(tuple(sorted(vertices[i] for i in chosen)))
            return
        for i in range(start, len(vertices)):
            v = vertices[i]
            if all(odd_dot(v, vertices[j]) for j in chosen):
                chosen.append(i)
                rec(i + 1, chosen)
                chosen.pop()

    rec(0, [])
    return found


def adjacency_square_vanishes(vertices):
    """(A^2)_ij is the number of length-2 walks. Every such count is 0 mod 3."""
    neighbor = []
    for i, u in enumerate(vertices):
        mask = 0
        for j, v in enumerate(vertices):
            if i != j and odd_dot(u, v):
                mask |= 1 << j
        neighbor.append(mask)
    n = len(vertices)
    for i in range(n):
        for j in range(i, n):
            if (neighbor[i] & neighbor[j]).bit_count() % 3:
                return False
    return True


def class_constant_patterns(vertices):
    """I + beta A for beta in F_3. Each is a legal pattern. Return their ranks."""
    n = len(vertices)
    ranks = []
    for beta in (0, 1, 2):
        rows = [[0] * n for _ in range(n)]
        for i, u in enumerate(vertices):
            rows[i][i] = 1
            for j in range(i + 1, n):
                if odd_dot(u, vertices[j]):
                    rows[i][j] = rows[j][i] = beta
        require(valid_pattern(rows, vertices), "I+%dA is not a pattern" % beta)
        product = [[0] * n for _ in range(n)]
        # (I+beta A)(I-beta A) = I when A^2 = 0. -beta == 3-beta == -beta mod 3.
        minus = (-beta) % 3
        other = [[0] * n for _ in range(n)]
        for i, u in enumerate(vertices):
            other[i][i] = 1
            for j in range(i + 1, n):
                if odd_dot(u, vertices[j]):
                    other[i][j] = other[j][i] = minus
        for i in range(n):
            for j in range(n):
                product[i][j] = sum(rows[i][k] * other[k][j] for k in range(n)) % 3
        require(all(product[i][i] == 1 and all(product[i][j] == 0 for j in range(n) if j != i) for i in range(n)),
                "(I+%dA)(I-%dA) is not I" % (beta, beta))
        ranks.append(rank_mod(rows))
    return ranks


def three_i_minus_a_mod5(vertices):
    n = len(vertices)
    rows = [[0] * n for _ in range(n)]
    for i, u in enumerate(vertices):
        rows[i][i] = 3 % 5
        for j in range(i + 1, n):
            if odd_dot(u, vertices[j]):
                rows[i][j] = rows[j][i] = (-1) % 5
    return rank_prime(rows, 5)


def matrix_sha256(rows):
    raw = bytes(entry % 3 for row in rows for entry in row)
    return hashlib.sha256(raw).hexdigest()


def main():
    vertices = p120()
    require(len(vertices) == 120, "P120 count")
    require(sum(weight(v) == 3 for v in vertices) == 84, "weight-3 count")
    require(sum(weight(v) == 7 for v in vertices) == 36, "weight-7 count")
    require(adjacency_square_vanishes(vertices), "A^2 does not vanish over F_3")
    print("PASS_A_SQUARE_ZERO")

    ranks = class_constant_patterns(vertices)
    require(ranks == [120, 120, 120], "class-constant patterns are not full rank: %s" % ranks)
    print("PASS_CLASS_CONSTANT_RANK120")

    require(three_i_minus_a_mod5(vertices) == 36, "3I-A mod 5 is not rank 36")
    reduced = []
    n = len(vertices)
    for i, u in enumerate(vertices):
        row = [0] * n
        row[i] = 0  # 3 ≡ 0, so the characteristic-3 reduction of 3I-A is -A
        for j, v in enumerate(vertices):
            if i != j and odd_dot(u, v):
                row[j] = (-1) % 3
        reduced.append(row)
    require(all(reduced[i][i] == 0 for i in range(n)), "3I-A should have zero diagonal in char 3")
    require(not valid_pattern(reduced, vertices), "3I-A must be illegal in char 3")
    print("PASS_OFFCHAR_CONTROL rank36_mod5=36 char3_diagonal=0")

    ports = load_ports()
    require(set(ports) <= set(vertices), "P104 not inside P120")
    require(sum(weight(v) == 3 for v in ports) == 70, "P104 weight 3")
    require(sum(weight(v) == 7 for v in ports) == 34, "P104 weight 7")
    degrees = {sum(odd_dot(u, v) for v in ports if v != u) for u in ports}
    require(degrees == {55}, "P104 is not 55-regular: %s" % sorted(degrees))

    phi, orth, columns, nullities, matrix = factorisation(vertices, constant=True)
    require(len(phi[0]) == 46, "feature width")
    require(rank_mod(phi) == 45, "quadratic evaluation rank")
    require(valid_pattern(matrix, vertices), "constant quadratic factorisation is not a pattern")
    full_rank = rank_mod(matrix)
    require(full_rank == 37, "P120 witness rank %d is not 37" % full_rank)
    asymmetric = sum(
        matrix[i][j] != matrix[j][i] for i in range(len(vertices)) for j in range(i + 1, len(vertices))
    )
    edge_values = {
        matrix[i][j]
        for i in range(len(vertices))
        for j in range(len(vertices))
        if i != j and odd_dot(vertices[i], vertices[j])
    }
    require(asymmetric > 0 and len(edge_values) > 1,
            "witness collapsed into a class-constant matrix")
    by_weight = {}
    for v, nullity in zip(vertices, nullities):
        by_weight.setdefault(weight(v), set()).add(nullity)
    require(by_weight == {3: {4}, 7: {9}}, "nullities %s" % by_weight)

    # The one-dimensional syzygy of Φ lies in every homogeneous column space,
    # so coefficient nullity is one larger than the dimension of legal columns.
    kernel = null_basis(phi, [(i, 0) for i in range(len(vertices))])
    require(len(kernel) == 1, "evaluation corank")
    syzygy = kernel[0]
    image_dims = {3: set(), 7: set()}
    for j, v in enumerate(vertices):
        equations = [(i, 0) for i in orth[j]] + [(j, 0)]
        basis = null_basis(phi, equations)
        require(_in_span(syzygy, basis), "syzygy missed at vertex %d" % j)
        images = []
        width = len(phi[0])
        for vector in basis:
            images.append([sum(phi[u][t] * vector[t] for t in range(width)) % 3 for u in range(len(vertices))])
        image_dims[weight(v)].add(rank_mod(images))
    require(image_dims == {3: {3}, 7: {8}}, "legal-column dimensions %s" % image_dims)
    print("PASS_FAMILY_DIMENSIONS coeff_nullity=4,9 column_dim=3,8")

    index = {v: i for i, v in enumerate(vertices)}
    p104 = principal(matrix, [index[v] for v in ports])
    require(valid_pattern(p104, ports), "P104 principal submatrix is not a pattern")
    p104_rank = rank_mod(p104)
    require(p104_rank == 36, "P104 witness rank %d is not 36" % p104_rank)
    digest = matrix_sha256(p104)
    require(digest == P104_MATRIX_SHA256, "P104 matrix sha256 %s" % digest)

    deleted = [v for v in vertices if v not in set(ports)]
    require(len(deleted) == 16, "deleted set")
    cliques = odd_cliques(deleted, 8)
    require(len(cliques) == 2, "expected two deleted 8-cliques")
    require(set(cliques) == set(CLIQUE_RANK), "deleted cliques changed: %s" % (cliques,))
    seen = {}
    for clique in cliques:
        block = list(ports) + list(clique)
        rows = principal(matrix, [index[v] for v in block])
        require(len(block) == 112 and valid_pattern(rows, block), "P112 pattern")
        seen[clique] = rank_mod(rows)
    require(seen == CLIQUE_RANK, "P112 ranks %s" % seen)
    print("PASS_CHAR3_WITNESS p120=37 p104=36 p112=%s" % sorted(seen.values()))

    # Predecessor feature map: no constant term. Same solver, free variables 0.
    _phi0, _orth0, _cols0, _null0, matrix0 = factorisation(vertices, constant=False)
    require(valid_pattern(matrix0, vertices), "no-constant factorisation is not a pattern")
    require(rank_mod(matrix0) == 38, "no-constant P120 rank is not 38")
    require(rank_mod(principal(matrix0, [index[v] for v in ports])) == 37, "no-constant P104 rank is not 37")
    print("PASS_NO_CONSTANT_COMPARISON p120=38 p104=37")

    # Controls that reject illegal masks and an inconsistent smaller feature map.
    planted = [row[:] for row in matrix]
    pair = next((i, j) for i in range(120) for j in range(i + 1, 120) if not odd_dot(vertices[i], vertices[j]))
    planted[pair[0]][pair[1]] = (planted[pair[0]][pair[1]] + 1) % 3
    require(not valid_pattern(planted, vertices), "control: planted orthogonal entry was accepted")
    killed = [row[:] for row in matrix]
    killed[0][0] = 0
    require(not valid_pattern(killed, vertices), "control: zero diagonal was accepted")
    ones = [[1] * 120 for _ in range(120)]
    require(not valid_pattern(ones, vertices), "control: all-ones was accepted")
    linear = [[(v >> i) & 1 for i in range(9)] for v in vertices]
    linear_fail = 0
    for j in range(0, 120, 17):
        equations = [(i, 0) for i in orth[j]] + [(j, 1)]
        solution, _free = rref_solve(linear, equations)
        if solution is None:
            linear_fail += 1
    require(linear_fail >= 1, "control: linear features solved every sampled column")
    print("PASS_CONTROLS linear_failures=%d" % linear_fail)
    print("PASS_CHAR3_RANK36 p104=36 p120=37 class_constant=120")


def _in_span(vector, basis):
    if not basis:
        return all(entry == 0 for entry in vector)
    width = len(vector)
    matrix = [[basis[c][r] for c in range(len(basis))] + [vector[r] % 3] for r in range(width)]
    cols = len(basis)
    rank = 0
    for col in range(cols):
        pivot = None
        for row in range(rank, width):
            if matrix[row][col] % 3:
                pivot = row
                break
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        inverse = pow(matrix[rank][col], -1, 3)
        for k in range(col, cols + 1):
            matrix[rank][k] = matrix[rank][k] * inverse % 3
        for row in range(width):
            if row == rank or matrix[row][col] % 3 == 0:
                continue
            factor = matrix[row][col] % 3
            for k in range(col, cols + 1):
                matrix[row][k] = (matrix[row][k] - factor * matrix[rank][k]) % 3
        rank += 1
    return all(matrix[row][cols] % 3 == 0 for row in range(rank, width))


if __name__ == "__main__":
    main()
