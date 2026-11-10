"""Independent original Reference oracle; classical identities are inherited.

Review code, not an online implementation. Prepared for @CubeJerry with
substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as Q


def require(ok, message):
    if not ok:
        raise ValueError(message)


def inverse(matrix):
    n = len(matrix)
    work = [[Q(v) for v in row] + [Q(i == j) for j in range(n)]
            for i, row in enumerate(matrix)]
    for column in range(n):
        pivot = next((i for i in range(column, n) if work[i][column]), None)
        require(pivot is not None, 'original matrix nonsingular')
        work[pivot], work[column] = work[column], work[pivot]
        value = work[column][column]
        work[column] = [x / value for x in work[column]]
        for i in range(n):
            if i != column and work[i][column]:
                multiple = work[i][column]
                work[i] = [x - multiple*y
                           for x, y in zip(work[i], work[column])]
    return [row[n:] for row in work]


def action(matrix, vector):
    return [sum((a*x for a, x in zip(row, vector)), Q(0)) for row in matrix]


def norm(matrix):
    return max(sum(map(abs, row), Q(0)) for row in matrix)


def gap(matrix):
    return min(row[i] - sum((abs(x) for j, x in enumerate(row) if j != i), Q(0))
               for i, row in enumerate(matrix))


def original_geometry(reference):
    s, k, w = (reference.spec.source_size, reference.spec.excess,
               reference.spec.source_halfwidth)
    selected = [(2 * (s + k) * i + s) // (2 * s) for i in range(s)]
    phases = [q - i for i, q in enumerate(selected)]
    runs = []
    for i, phase in enumerate(phases):
        if i == 0 or phase != phases[i-1]:
            runs.append([])
        runs[-1].append(i)
    require(all(2 * (len(run)-1) < s for run in runs), 'ordinary unique lifts')
    boundary = sorted({i for run in runs for i in run[:w] + run[-w:]})
    matrix = [[Q(reference.entry('narrow', row, column).value)
               for column in selected] for row in selected]
    block = [[v if phases[i] == phases[j] else Q(0)
              for j, v in enumerate(row)] for i, row in enumerate(matrix)]
    difference = [[a-b for a,b in zip(row, brow)]
                  for row,brow in zip(matrix,block)]
    boundary_set = set(boundary)
    require(all(not difference[i][j] or i in boundary_set and j in boundary_set
                for i in range(s) for j in range(s)), 'boundary support')
    require(gap(matrix) >= reference.narrow_gap > 0, 'original positive row gap')
    require(gap(block) >= gap(matrix), 'principal deletion gap')
    return selected, runs, boundary, matrix, block, difference


def check_geometry(reference):
    selected, runs, boundary, matrix, block, difference = original_geometry(reference)
    s, m = len(matrix), len(boundary)
    bi = inverse(block)
    trace_inverse = [[bi[i][j] for j in boundary] for i in boundary]
    sb = inverse(trace_inverse)
    k = [[difference[i][j] for j in boundary] for i in boundary]
    sa = [[a+b for a,b in zip(row,krow)] for row,krow in zip(sb,k)]
    require(gap(sb) >= reference.narrow_gap, 'block Schur gap')
    require(gap(sa) >= reference.narrow_gap, 'periodic Schur gap')
    require(norm(sb) <= norm(block), 'block Schur mass')
    require(norm(sa) <= norm(matrix), 'periodic Schur mass')
    folded = [i//2 if i%2 == 0 else m-1-i//2 for i in range(m)]
    band = max((abs(i-j) for i in range(m) for j in range(m)
                if sa[folded[i]][folded[j]]), default=0)
    w = reference.spec.source_halfwidth
    require(band <= min(m-1,4*w-2), 'inherited folded multi-run band')
    ai, sai = inverse(matrix), inverse(sa)
    controls = 0
    for component in range(2):
        rhs = [Q(((7 + component*4)*i + 3 + component)%19 - 9,16)
               for i in range(s)]
        y = action(bi,rhs)
        z = action(sai,action(sb,[y[i] for i in boundary]))
        correction = action(k,z)
        new_rhs = list(rhs)
        for i,value in zip(boundary,correction):
            new_rhs[i] -= value
        composed = action(bi,new_rhs)
        expected = action(ai,rhs)
        require(composed == expected, 'direct original periodic inverse')
        require(action(matrix,expected) == rhs, 'original exact residual')
        require(y != expected, 'omitted boundary correction rejected')
        require(expected[::-1] != expected, 'reversed source order rejected')
        controls += 2
    wraps = [(i,j) for i in range(s) for j in range(s)
             if difference[i][j] and abs(i-j) > s//2]
    require(bool(wraps), 'fixture exercises period-cut couplings')
    return dict(source_size=s, excess=reference.spec.excess, selected=selected,
                runs=[len(r) for r in runs], boundary_size=m,
                folded_band=band, wrap_entries=len(wraps), controls=controls,
                matrix_entries=s*s, source_identity=reference.description_hash)
