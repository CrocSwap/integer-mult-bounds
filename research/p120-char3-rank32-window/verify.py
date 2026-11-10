#!/usr/bin/env python3
"""Rank-32 characteristic-3 pattern on P120.

No kappa claim. Standard library only.

The pattern is one explicit 1-block pattern. Legality is checked on every
vertex and every orthogonal pair. Rank is the number of pivots in Gaussian
elimination over F_3. This is not a census of all patterns, and it is not a
proof that every pattern has rank at least 32.
"""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
PORTS = REPO / "research" / "p104-char3-rank36-window" / "data" / "ports_p104.json"
PORTS_SHA256 = "691c7b7d212112115b1bfc76db89f90d304ec448dc8c4a0c43d9a5954317146c"
MATRIX_SHA256 = "81e209bb5be3c3e9b9a5d593190fd9b19540656bb0162164f4df7a1f0bf4a8c4"
# Principal ranks of this same witness, in port-file order and clique order.
P104_RANK = 32
P112_RANKS = {
    (7, 25, 42, 52, 76, 82, 97, 127): 32,
    (67, 104, 137, 162, 266, 289, 448, 491): 32,
}


def require(ok, message):
    if not ok:
        raise SystemExit("FAIL: " + message)


def weight(v):
    return v.bit_count()


def odd_dot(a, b):
    return ((a & b).bit_count() & 1) == 1


def vertices():
    return [v for v in range(512) if weight(v) % 4 == 3]


def pairs():
    return [(i, j) for i in range(9) for j in range(i + 1, 9)]


def rref(matrix, width):
    """Reduced row echelon form. pivot_of[col] is the row of that pivot, or None.

    Elimination runs left to right. The pivot is scaled to 1 and cleared above
    and below. The result is the unique reduced row echelon form.
    """
    mat = [row[:] for row in matrix]
    extra = len(mat[0]) - width
    pivot_of = [None] * width
    rank = 0
    for col in range(width):
        pivot = None
        for row in range(rank, len(mat)):
            if mat[row][col] % 3:
                pivot = row
                break
        if pivot is None:
            continue
        mat[rank], mat[pivot] = mat[pivot], mat[rank]
        inverse = pow(mat[rank][col], -1, 3)
        for k in range(col, width + extra):
            mat[rank][k] = mat[rank][k] * inverse % 3
        for row in range(len(mat)):
            if row == rank or mat[row][col] % 3 == 0:
                continue
            factor = mat[row][col] % 3
            for k in range(col, width + extra):
                mat[row][k] = (mat[row][k] - factor * mat[rank][k]) % 3
        pivot_of[col] = rank
        rank += 1
    return mat, pivot_of


def rank_of(rows):
    if not rows:
        return 0
    _, pivots = rref(rows, len(rows[0]))
    return sum(pivot is not None for pivot in pivots)


def kernel_basis(rows, width):
    """Canonical kernel basis of a row space, one vector per free column.

    Free columns are taken in increasing order. The vector for a free column
    has a 1 there, 0 in every other free column, and pivot entries equal to
    the negation of the reduced-row-echelon coefficient. It does not depend
    on the order of the input rows, because the reduced form is unique.
    """
    if not rows:
        return [[1 if i == j else 0 for i in range(width)] for j in range(width)]
    reduced, pivots = rref(rows, width)
    basis = []
    for free in [col for col, pivot in enumerate(pivots) if pivot is None]:
        vector = [0] * width
        vector[free] = 1
        for col, pivot in enumerate(pivots):
            if pivot is not None:
                vector[col] = (-reduced[pivot][free]) % 3
        basis.append(vector)
    return basis


def solve_free_zero(rows, width):
    """Particular solution with free variables set to 0, or None if inconsistent."""
    reduced, pivots = rref(rows, width)
    rank = sum(pivot is not None for pivot in pivots)
    for row in range(rank, len(reduced)):
        if reduced[row][width] % 3:
            return None
    solution = [0] * width
    for col, pivot in enumerate(pivots):
        if pivot is not None:
            solution[col] = reduced[pivot][width]
    return solution


def dot(left, right):
    return sum(x * y for x, y in zip(left, right)) % 3


def features(v):
    """45 coordinates: 1, x0..x8, and x_i x_j for every pair except (7, 8)."""
    bits = [(v >> i) & 1 for i in range(9)]
    coords = [1]
    coords.extend(bits)
    for i, j in pairs():
        if (i, j) != (7, 8):
            coords.append(bits[i] * bits[j])
    return [c % 3 for c in coords]


def orthogonal(verts):
    lists = [[] for _ in verts]
    for i, u in enumerate(verts):
        for j in range(i + 1, len(verts)):
            if not odd_dot(u, verts[j]):
                lists[i].append(j)
                lists[j].append(i)
    return lists


def legal_rows(phi, orth, j, rhs_self):
    return [phi[i][:] + [0] for i in orth[j]] + [phi[j][:] + [rhs_self]]


def valid_pattern(matrix, verts):
    for i, u in enumerate(verts):
        if matrix[i][i] % 3 == 0:
            return False
        for j in range(i + 1, len(verts)):
            if odd_dot(u, verts[j]):
                continue
            if matrix[i][j] % 3 or matrix[j][i] % 3:
                return False
    return True


def principal(matrix, index):
    return [[matrix[i][j] for j in index] for i in index]


def relation_rows():
    """Nine coefficient relations that cut out the same 36-dimensional space.

    Layout: c, a0..a8, then b_ij for pairs other than (7, 8), in pair order.
    """
    width = 45
    pair_index = {}
    cursor = 10
    for i, j in pairs():
        if (i, j) == (7, 8):
            continue
        pair_index[(i, j)] = cursor
        cursor += 1
    rows = []
    constant = [0] * width
    constant[0] = 1
    constant[9] = 1
    rows.append(constant)
    trace = [0] * width
    for i in range(8):
        trace[1 + i] = 1
    trace[9] = 2
    for i, j in pairs():
        if j <= 7:
            trace[pair_index[(i, j)]] = 2
    rows.append(trace)
    for i in range(7):
        row = [0] * width
        row[pair_index[(i, 8)]] = 1
        rows.append(row)
    return rows


def main():
    verts = vertices()
    require(len(verts) == 120, "P120 count")
    require(sum(weight(v) == 3 for v in verts) == 84, "weight-3 count")
    require(sum(weight(v) == 7 for v in verts) == 36, "weight-7 count")
    orth = orthogonal(verts)
    phi = [features(v) for v in verts]
    require(len(phi[0]) == 45, "chart width")

    # The dropped monomial is redundant on P120: every pair product sums to 0.
    syzygy_values = []
    for v in verts:
        bits = [(v >> i) & 1 for i in range(9)]
        total = 0
        for i, j in pairs():
            total += bits[i] * bits[j]
        syzygy_values.append(total % 3)
    require(syzygy_values == [0] * 120, "pair-sum syzygy")
    require(rank_of(phi) == 45, "degree-2 evaluation rank")
    print("PASS_CHART rank45 syzygy=0")

    witness = []
    for j in range(len(verts)):
        solution = solve_free_zero(legal_rows(phi, orth, j, 1), 45)
        require(solution is not None, "degree-2 system inconsistent at %d" % j)
        witness.append(solution)
    witness_matrix = [
        [dot(phi[u], witness[v]) for v in range(len(verts))] for u in range(len(verts))
    ]
    require(valid_pattern(witness_matrix, verts), "degree-2 witness is not a pattern")
    require(rank_of(witness_matrix) == 37, "degree-2 free-zero rank is not 37")
    print("PASS_PREDECESSOR_POINT rank37")

    reduced, pivots = rref(witness, 45)
    span_dim = sum(pivot is not None for pivot in pivots)
    require(span_dim == 37, "witness column span %d" % span_dim)
    basis = [reduced[row][:45] for row in range(span_dim)]
    evaluation = [[dot(phi[u], basis[t]) for t in range(span_dim)] for u in range(len(verts))]

    def coordinates(vector):
        rows = [[basis[t][i] for t in range(span_dim)] + [vector[i]] for i in range(45)]
        solution = solve_free_zero(rows, span_dim)
        require(solution is not None, "vector outside the witness span")
        return solution

    witness_coords = [coordinates(column) for column in witness]
    direction_dim = []
    for j in range(len(verts)):
        rows = [evaluation[i][:] for i in orth[j] + [j]]
        direction_dim.append(len(kernel_basis(rows, span_dim)))
    rigid_index = [j for j, dim in enumerate(direction_dim) if dim == 0]
    rigid_vertices = [verts[j] for j in rigid_index]
    expected_rigid = [v for v in verts if weight(v) == 7 and ((v >> 8) & 1) == 0]
    require(rigid_vertices == expected_rigid, "rigid set %s" % rigid_vertices)
    require(len(rigid_vertices) == 8, "rigid count")
    require(rank_of([witness_coords[j] for j in rigid_index]) == 8, "rigid columns")
    print("PASS_RIGID_COLUMNS count=8 bit8_clear_weight7")

    dual = kernel_basis([witness_coords[j] for j in rigid_index], span_dim)
    require(len(dual) == 29, "annihilator of the rigid columns")

    def meets_every_flat(form):
        if all(entry == 0 for entry in form):
            return False
        for j in range(len(verts)):
            rows = [evaluation[i][:] + [0] for i in orth[j]] + [evaluation[j][:] + [1]]
            # Restrict the unknown to ker(form) by one extra equation form·c = 0,
            # and test consistency of the legal system inside the witness span.
            rows.append(form[:] + [0])
            if solve_free_zero(rows, span_dim) is None:
                return False
        return True

    good_lines = [i for i, form in enumerate(dual) if meets_every_flat(form)]
    require(good_lines == [1], "hyperplane lines %s" % good_lines)
    print("PASS_HYPERPLANE_LINE index=1 of 29")

    form = dual[1]
    space = []
    for coord in kernel_basis([form], span_dim):
        ambient = [0] * 45
        for t, scale in enumerate(coord):
            if scale:
                for i in range(45):
                    ambient[i] = (ambient[i] + scale * basis[t][i]) % 3
        space.append(ambient)
    require(len(space) == 36 and rank_of(space) == 36, "hyperplane dimension")
    relation_rank = rank_of(relation_rows() + kernel_basis(space, 45))
    # The nine declared relations and the annihilator of the space are the same.
    require(rank_of(relation_rows()) == 9, "relation rank")
    require(rank_of(kernel_basis(space, 45)) == 9, "annihilator rank")
    require(relation_rank == 9, "relations do not cut out the hyperplane")
    print("PASS_COEFFICIENT_RELATIONS n=9")

    factor = [[dot(phi[u], column) for column in space] for u in range(len(verts))]
    require(rank_of(factor) == 36, "evaluation of the hyperplane")
    coefficients = []
    affine = {}
    for j in range(len(verts)):
        rows = legal_rows(factor, orth, j, 1)
        solution = solve_free_zero(rows, 36)
        require(solution is not None, "hyperplane system inconsistent at %d" % j)
        _, pivots = rref(rows, 36)
        freedom = 36 - sum(pivot is not None for pivot in pivots)
        affine[freedom] = affine.get(freedom, 0) + 1
        coefficients.append(solution)
    require(affine == {0: 36, 2: 56, 5: 28}, "affine dimensions %s" % affine)
    print("PASS_AFFINE_DIMENSIONS 0=36 2=56 5=28")
    matrix = [
        [dot(factor[u], coefficients[v]) for v in range(len(verts))]
        for u in range(len(verts))
    ]
    require(valid_pattern(matrix, verts), "rank-32 candidate is not a pattern")
    pattern_rank = rank_of(matrix)
    reversed_rank = rank_of([row[::-1] for row in matrix])
    transpose_rank = rank_of([list(column) for column in zip(*matrix)])
    require(pattern_rank == reversed_rank == transpose_rank == 32, "ranks %s" % pattern_rank)
    digest = hashlib.sha256(bytes(entry for row in matrix for entry in row)).hexdigest()
    require(digest == MATRIX_SHA256, "matrix sha256 %s" % digest)

    # Literal 120 by 32 factorisation: pivot columns of the pattern, then coordinates.
    _, row_pivots = rref(matrix, len(verts))
    independent = [c for c, pivot in enumerate(row_pivots) if pivot is not None]
    require(len(independent) == 32, "pivot column count")
    narrow = [[matrix[r][c] for c in independent] for r in range(len(verts))]
    require(rank_of(narrow) == 32, "narrow factor rank")
    for c in range(len(verts)):
        target = [matrix[r][c] for r in range(len(verts))]
        rows = [narrow[r][:] + [target[r]] for r in range(len(verts))]
        require(solve_free_zero(rows, 32) is not None, "column %d outside the 32-factor" % c)
    print("PASS_FACTORISATION shape=120x32 rank=32 sha256=%s" % digest)

    edge_values = {
        matrix[i][j]
        for i in range(len(verts))
        for j in range(len(verts))
        if i != j and odd_dot(verts[i], verts[j])
    }
    asymmetric = any(
        matrix[i][j] != matrix[j][i]
        for i in range(len(verts))
        for j in range(i + 1, len(verts))
    )
    require(asymmetric and len(edge_values) > 1, "pattern collapsed to a class-constant matrix")

    raw = PORTS.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == PORTS_SHA256, "P104 port bytes")
    ports = json.loads(raw)["ports"]
    deleted = set(verts) - set(ports)
    require(len(ports) == 104 and len(deleted) == 16, "port counts")
    require(set().union(*P112_RANKS) == deleted, "deleted cliques")
    index = {v: i for i, v in enumerate(verts)}
    port_index = [index[v] for v in ports]
    p104 = principal(matrix, port_index)
    require(valid_pattern(p104, ports), "P104 principal submatrix")
    p104_rank = rank_of(p104)
    require(p104_rank == P104_RANK, "P104 rank %d" % p104_rank)
    seen = {}
    for clique, expected in P112_RANKS.items():
        block = list(ports) + list(clique)
        rows = principal(matrix, [index[v] for v in block])
        require(valid_pattern(rows, block), "P112 pattern")
        require(all(odd_dot(a, b) for a in clique for b in clique if a < b), "clique")
        seen[clique] = rank_of(rows)
        require(seen[clique] == expected, "P112 rank %s for %s" % (seen[clique], clique))
    print("PASS_PRINCIPAL p104=%d p112=%s" % (P104_RANK, sorted(seen.values())))

    # The same space in the relation-kernel basis has another legal point.
    # Its rank is 36, so rank 32 is a property of this basis, not of every
    # pattern whose columns lie in the space.
    relation_basis = kernel_basis(relation_rows(), 45)
    require(len(relation_basis) == 36, "relation kernel")
    relation_factor = [
        [dot(phi[u], column) for column in relation_basis] for u in range(len(verts))
    ]
    relation_columns = []
    for j in range(len(verts)):
        solution = solve_free_zero(legal_rows(relation_factor, orth, j, 1), 36)
        require(solution is not None, "relation basis inconsistent at %d" % j)
        relation_columns.append(solution)
    relation_matrix = [
        [dot(relation_factor[u], relation_columns[v]) for v in range(len(verts))]
        for u in range(len(verts))
    ]
    require(valid_pattern(relation_matrix, verts), "relation-basis point is not a pattern")
    require(rank_of(relation_matrix) == 36, "relation-basis rank")
    print("PASS_SAME_SPACE_OTHER_POINT rank36")

    planted = [row[:] for row in matrix]
    pair = next(i for i in range(1, len(verts)) if not odd_dot(verts[0], verts[i]))
    planted[0][pair] = (planted[0][pair] + 1) % 3
    require(not valid_pattern(planted, verts), "control accepted a planted orthogonal entry")
    killed = [row[:] for row in matrix]
    killed[0][0] = 0
    require(not valid_pattern(killed, verts), "control accepted a zero diagonal")
    pure = []
    for v in verts:
        bits = [(v >> i) & 1 for i in range(9)]
        pure.append([bits[i] * bits[j] % 3 for i, j in pairs()])
    pure_fail = solve_free_zero(legal_rows(pure, orth, 0, 1), 36)
    require(pure_fail is None, "control: pure quadrics solved vertex 0")
    full = []
    for beta in (0, 1, 2):
        rows = [[0] * 120 for _ in range(120)]
        for i, u in enumerate(verts):
            rows[i][i] = 1
            for j in range(i + 1, 120):
                if odd_dot(u, verts[j]):
                    rows[i][j] = rows[j][i] = beta
        full.append(rank_of(rows))
    require(full == [120, 120, 120], "class-constant ranks %s" % full)
    print("PASS_CONTROLS planted=1 zero_diagonal=1 pure_quadrics=inconsistent class_constant=120")
    print("PASS_P120_CHAR3_RANK32 rank=32 p104=%d p112=%s" % (P104_RANK, sorted(seen.values())))


if __name__ == "__main__":
    main()
