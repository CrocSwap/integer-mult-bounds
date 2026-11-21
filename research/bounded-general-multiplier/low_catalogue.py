"""Generate the low-type directory and its complete right-action tables."""

from itertools import product


def nonsingular(entries, n):
    rows = [list(entries[n*i:n*(i+1)]) for i in range(n)]
    for i in range(n):
        pivot = next((j for j in range(i,n) if rows[j][i] % 3), None)
        if pivot is None:
            return False
        rows[i], rows[pivot] = rows[pivot], rows[i]
        inv = pow(rows[i][i], -1, 3)
        for j in range(i+1,n):
            step = rows[j][i] * inv
            for k in range(i+1,n):
                rows[j][k] = (rows[j][k] - step*rows[i][k]) % 3
    return True


def low_directory(n):
    """Enumerate the exact invertible rows in ternary lexicographic order."""
    if n < 1:
        raise ValueError("Use at least one coordinate")
    return [row for row in product(range(3), repeat=n*n) if nonsingular(row,n)]


def right_image(row, n, step):
    """Apply one elementary factor on the right of the current low matrix."""
    kind, i, j, value = step
    out = list(row)
    for k in range(0,n*n,n):
        if kind == "swap":
            out[k+i], out[k+j] = row[k+j], row[k+i]
        elif kind == "scale":
            if value % 3 == 0:
                raise ValueError("The right-action scale must be a unit")
            out[k+i] = value * row[k+i] % 3
        elif kind == "add":
            if i == j:
                raise ValueError("A row addition needs two different columns")
            out[k+j] = (row[k+j] + value*row[k+i]) % 3
        else:
            raise ValueError("Unknown right-action factor")
    return tuple(out)


def right_table(directory, n, step):
    """Sort and merge the full returned rows with their actual low ordinals."""
    placed = sorted((right_image(g,n,step), i) for i,g in enumerate(directory))
    arcs = []
    for dest, (image, origin) in enumerate(placed):
        if image != directory[dest]:
            raise ArithmeticError("The low action did not permute the entire group")
        arcs.append((origin,dest))
    return [dest for _,dest in sorted(arcs)]


def pivot_table(directory, n, native):
    """Emit the old-low decision for every genuine low matrix and this site."""
    from ternary_frames import covered_factors
    from ternary_leaf import select_pivot
    for g in directory:
        matrix = [g[n*i:n*(i+1)] for i in range(n)]
        u,v = covered_factors(native, matrix, 1)
        yield select_pivot(u,v)
