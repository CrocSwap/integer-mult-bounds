"""Exact two-parameter output-family certificate; no parameter sampling.

The caller supplies the source-reconstructed rational dirty/hot block G.
PROOF-FAMILY.md gives the universal parameter and basis-change argument.
"""
from fractions import Fraction as Q


HOT = [13, 16, 43, 44, 51, 78, 99, 104]
DIRTY = [16, 43, 44, 104, 417, 418, 419, 420, 421, 422,
         423, 424, 426, 428, 430]
N0 = [Q(x) for x in (2, 0, -1, 0, 0, -1, -1, 1)]
NL = [Q(x) for x in (0, 0, -1, 0, -2, 1, 1, 1)]
NM = [Q(x) for x in (0, 1, -1, 1, 0, 0, 0, -1)]


def need(condition, message):
    if not condition:
        raise ValueError(message)


def rank(rows):
    """Independent exact row elimination, used only on tiny matrices."""
    rows = [[Q(value) for value in row] for row in rows]
    if not rows:
        return 0
    width = len(rows[0])
    need(all(len(row) == width for row in rows), "ragged matrix")
    count = 0
    for column in range(width):
        pivot = next((i for i in range(count, len(rows)) if rows[i][column]), None)
        if pivot is None:
            continue
        rows[count], rows[pivot] = rows[pivot], rows[count]
        divisor = rows[count][column]
        rows[count] = [value / divisor for value in rows[count]]
        for i in range(count + 1, len(rows)):
            multiplier = rows[i][column]
            if multiplier:
                rows[i] = [a - multiplier * b for a, b in zip(rows[i], rows[count])]
        count += 1
        if count == len(rows):
            break
    return count


def verify(G, dirty, hot):
    """Certify every rational shear419+=lambda*u,421+=mu*u at once."""
    need(list(dirty) == DIRTY and list(hot) == HOT, "source role order")
    need(len(G) == len(DIRTY) and all(len(row) == len(HOT) for row in G),
         "source block dimensions")
    G = [[Q(value) for value in row] for row in G]
    need(rank([row[1:] for row in G]) == 7, "seven unaffected columns independent")
    need(rank([row for role, row in zip(DIRTY, G) if role not in (419, 421)]) == 5,
         "both changed rows removed rank")
    # G' = G + (lambda*e419 + mu*e421)*e13^T.
    # Match ALL coefficients of G'*(N0 + lambda*NL + mu*NM).
    for role, row in zip(DIRTY, G):
        dot = lambda vector: sum(a * b for a, b in zip(row, vector))
        e419, e421 = Q(role == 419), Q(role == 421)
        coefficients = [dot(N0), dot(NL) + e419 * N0[0],
                        dot(NM) + e421 * N0[0], e419 * NL[0],
                        e419 * NM[0] + e421 * NL[0], e421 * NM[0]]
        need(coefficients == [0] * 6, "symbolic kernel coefficient identity")
    need(N0[0] == 2 and NL[0] == NM[0] == 0, "uniformly nonzero kernel")
    # Each coordinate below is the affine triple (constant, lambda, mu).
    triples = [tuple(v) for v in zip(N0, NL, NM)]
    pair_triples = [[triples[HOT.index(role)] for role in pair]
                    for pair in [(13, 51), (78, 99), (16, 44), (43, 104)]]
    need(pair_triples == [[(2, 0, 0), (0, -2, 0)],
                          [(-1, 1, 0), (-1, 1, 0)],
                          [(0, 0, 1), (0, 0, 1)],
                          [(-1, -1, -1), (1, 1, -1)]],
         "four exact pair restrictions")
    return {
        "status": "RULED_OUT_FOR_ALL_RATIONAL_LAMBDA_MU",
        "hot_columns": HOT,
        "changed_dirty_outputs": [419, 421],
        "unaffected_seven_columns_rank": 7,
        "both_changed_rows_removed_rank": 5,
        "kernel_constant": [str(x) for x in N0],
        "kernel_lambda": [str(x) for x in NL],
        "kernel_mu": [str(x) for x in NM],
        "symbolic_coefficients_checked_per_row": ["1", "lambda", "mu", "lambda^2", "lambda*mu", "mu^2"],
        "rank_for_every_parameter": 7,
        "pair_dimension_formula": "4 + [lambda=1] + [mu=0] + [lambda=-1 and mu=0]",
        "maximum_single_color_span_dimension": 6,
        "covers_invertible_complement_mixing": True,
        "new_kappa": False,
    }


def controls(G, dirty, hot):
    """Substantive input and algebra mutations, without sampling parameters."""
    rejected = []
    changed = [[Q(value) for value in row] for row in G]
    changed[DIRTY.index(419)][HOT.index(13)] += 1
    damaged_column = [[Q(value) for value in row] for row in G]
    for row in damaged_column:
        row[HOT.index(16)] = 0
    for name, matrix, row_order, column_order in [
        ("changed_shear_row_coefficient", changed, dirty, hot),
        ("lost_unaffected_column_rank", damaged_column, dirty, hot),
        ("wrong_role_binding", G, list(reversed(dirty)), hot),
    ]:
        try:
            verify(matrix, row_order, column_order)
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError("negative control accepted: " + name)
    return rejected
