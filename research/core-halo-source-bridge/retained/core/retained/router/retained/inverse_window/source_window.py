"""Exact same-Reference setup for the first narrow union window.

All routines here are input-independent preparation or finite observers.
The online consumer receives only encoded masks and physically prepared pages.
Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
"""
from dataclasses import dataclass
from fractions import Fraction as Q
from math import isqrt


def need(condition, message):
    if not condition:
        raise ValueError(message)


def frozen(matrix):
    return tuple(tuple(Q(x) for x in row) for row in matrix)


def identity(n):
    return tuple(tuple(Q(i == j) for j in range(n)) for i in range(n))


def sub(matrix, rows, columns):
    return tuple(tuple(matrix[i][j] for j in columns) for i in rows)


def multiply(first, second):
    if not first:
        return ()
    need(second and len(first[0]) == len(second), 'matching exact matrix dimensions')
    return tuple(tuple(sum((x*y for x, y in zip(row, col)), Q())
                       for col in zip(*second)) for row in first)


def inverse(matrix):
    n = len(matrix)
    need(all(len(row) == n for row in matrix), 'square exact inverse')
    data = [list(row) + list(unit) for row, unit in zip(matrix, identity(n))]
    for k in range(n):
        pivot = data[k][k]
        need(pivot != 0, 'nonzero exact setup pivot')
        data[k] = [x/pivot for x in data[k]]
        for i in range(n):
            if i != k:
                coefficient = data[i][k]
                data[i] = [x-coefficient*y for x, y in zip(data[i], data[k])]
    result = frozen(row[n:] for row in data)
    need(not n or multiply(matrix, result) == identity(n), 'exact inverse residual')
    return result


def row_norm(matrix):
    return max((sum(map(abs, row), Q()) for row in matrix), default=Q())


def row_gap(matrix):
    need(bool(matrix), 'nonempty row-gap matrix')
    return min(row[i]-sum((abs(x) for j, x in enumerate(row) if i != j), Q())
               for i, row in enumerate(matrix))


def bandwidth(matrix):
    return max((abs(i-j) for i, row in enumerate(matrix)
                for j, x in enumerate(row) if x), default=0)


def lu(matrix):
    """Exact Doolittle setup, used only for the row-DD Schur matrix."""
    n = len(matrix)
    lower, upper = [list(row) for row in identity(n)], [[Q()]*n for _ in range(n)]
    for i in range(n):
        for j in range(i, n):
            upper[i][j] = matrix[i][j]-sum((lower[i][k]*upper[k][j]
                                          for k in range(i)), Q())
        need(upper[i][i] > 0, 'positive exact Schur pivot')
        for j in range(i+1, n):
            lower[j][i] = (matrix[j][i]-sum((lower[j][k]*upper[k][i]
                                           for k in range(i)), Q()))/upper[i][i]
    lower, upper = frozen(lower), frozen(upper)
    need(multiply(lower, upper) == matrix, 'exact Schur LU residual')
    return lower, upper


def pad(matrix, block):
    n = len(matrix)
    extent = ((n+block-1)//block)*block
    return tuple(tuple(matrix[i][j] if i < n and j < n else Q(i == j)
                       for j in range(extent)) for i in range(extent))


def reverse(matrix):
    return tuple(tuple(reversed(row)) for row in reversed(matrix))


def toward_zero(value, precision):
    numerator = value.numerator << precision
    integer = abs(numerator)//value.denominator
    return Q(-integer if numerator < 0 else integer, 1 << precision)


def ceil_log2(value):
    value = Q(value)
    need(value > 0, 'positive logarithm argument')
    result = max(0, value.numerator.bit_length()-value.denominator.bit_length())
    while Q(1 << result) < value:
        result += 1
    return result


def sufficient_allocation(reference, *, band, radius, target, incoming=0,
                          largest_descriptor=1):
    """Conservative all-size allocation, before any payload is supplied."""
    reference.require_narrow_gap()
    need(all(type(x) is int for x in (band, target, incoming, largest_descriptor))
         and band >= 1 and target >= 1 and incoming >= 0 and largest_descriptor >= 1,
         'all-size allocation domain')
    radius = Q(radius)
    need(radius >= 1, 'all-size admitted radius')
    square = 1/(16*reference.narrow_gap)
    gap_parameter = isqrt(square.numerator//square.denominator)
    if gap_parameter*gap_parameter*square.denominator < square.numerator:
        gap_parameter += 1
    pbar = max(band+1, gap_parameter, 1)
    block = 1 << ceil_log2(max(2, 2*band-1))
    precision = max(incoming, target+45+16*ceil_log2(pbar)+ceil_log2(radius))
    width = max(precision+52+16*ceil_log2(pbar)+ceil_log2(radius),
                largest_descriptor.bit_length()+2)
    need(block <= 4*pbar, 'envelope block guard')
    return dict(pbar=pbar, block=block, precision=precision, width=width)


@dataclass(frozen=True)
class PassBudget:
    diagonal: Q
    preceding: Q
    inverse: Q
    c0: Q
    c1: Q
    error_coefficient: Q


def pass_budget(matrix, block, eta):
    matrix = pad(matrix, block)
    n = len(matrix)
    need(all(not matrix[i][j] or (i//block-1 <= j//block <= i//block)
             for i in range(n) for j in range(n)), 'exact adjacent-block factor support')
    diagonal = max(row_norm(sub(matrix, range(k, k+block), range(k, k+block)))
                   for k in range(0, n, block))
    preceding = max([Q()] + [row_norm(sub(matrix, range(k, k+block), range(k-block, k)))
                             for k in range(block, n, block)])
    inv = row_norm(inverse(matrix))
    c0 = diagonal*block+2*diagonal+1
    c1 = block*(diagonal*(preceding+1)+1)
    need(block*eta <= 1 and eta*c0 <= 1 and inv*eta*c1 <= Q(1, 2),
         'funded completed-residual absorption')
    return PassBudget(diagonal, preceding, inv, c0, c1,
                      inv*(c0+4*inv*c1))


def rounded_pages(lower, upper, block, precision):
    """Observer only: exact expected bytes' values for unchanged prepare_pages.

    Four flat Fraction tuples: lower inverse diagonals, lower preceding blocks,
    upper inverse diagonals in reversed padded order, upper preceding blocks.
    This routine must not replace actual physical prepare_pages in the fixture.
    """
    result = []
    for matrix in (pad(lower, block), reverse(pad(upper, block))):
        diagonals, couplings = [], []
        for start in range(0, len(matrix), block):
            rows = range(start, start+block)
            diagonal = inverse(sub(matrix, rows, rows))
            diagonals.extend(toward_zero(x, precision) for row in diagonal for x in row)
            if start:
                coupling = sub(matrix, rows, range(start-block, start))
                couplings.extend(toward_zero(x, precision) for row in coupling for x in row)
        result.extend((tuple(diagonals), tuple(couplings)))
    return tuple(result)


def rounded_solve(lower, upper, rhs, block, precision):
    """Finite value observer; each RHS is one real column, unpadded on entry."""
    n = len(lower)
    need(len(rhs) == n and all(len(row) == len(rhs[0]) for row in rhs),
         'rectangular finite observer RHS')
    need(all((Q(x)*(1 << precision)).denominator == 1 for row in rhs for x in row),
         'observer inputs already on the admitted grid')
    columns = len(rhs[0])
    extent = len(pad(lower, block))
    current = [list(row) for row in rhs] + [[Q()]*columns for _ in range(extent-n)]
    pages = rounded_pages(lower, upper, block, precision)
    for stage in range(2):
        if stage:
            current.reverse()
        output = []
        diagonals, couplings = pages[2*stage:2*stage+2]
        for k, start in enumerate(range(0, extent, block)):
            residual = current[start:start+block]
            if k:
                coupling = [couplings[(k-1)*block*block+i*block:(k-1)*block*block+(i+1)*block]
                            for i in range(block)]
                product = multiply(coupling, output[-block:])
                residual = [[toward_zero(x-y, precision) for x, y in zip(row, term)]
                            for row, term in zip(residual, product)]
            diagonal = [diagonals[k*block*block+i*block:k*block*block+(i+1)*block]
                        for i in range(block)]
            output.extend([toward_zero(x, precision) for x in row]
                          for row in multiply(diagonal, residual))
        current = output
    current.reverse()
    return frozen(current[:n])


@dataclass(frozen=True)
class Window:
    source_parameters: tuple
    reference_sha256: str
    origin: int
    length: int
    band: int
    cap: int
    block: int
    precision: int
    width: int
    radius: Q
    target: int
    interior_blocks: tuple
    I: tuple
    J: tuple
    E: tuple
    j_mask: tuple
    H: tuple
    A: tuple
    B: tuple
    C: tuple
    D: tuple
    F: tuple
    N: tuple
    shear_lower: tuple
    shear_upper: tuple
    f_lower: tuple
    f_upper: tuple
    source_gap: Q
    pass_budgets: tuple
    shear_error: Q
    solve_input_radius: Q
    total_error: Q
    root_record_radius: Q

    @property
    def P(self):
        return self.precision

    @property
    def w(self):
        return self.width

    def exact_action(self, rhs):
        """Finite oracle against the current post-dense E-line, not original x."""
        need(len(rhs) == len(self.E), 'complete exact E-line')
        sheared = multiply(inverse(multiply(self.shear_lower, self.shear_upper)), rhs)
        boundary = multiply(inverse(self.F), [sheared[i] for i, bit in enumerate(self.j_mask) if bit])
        at = iter(boundary)
        return tuple(next(at) if bit else tuple(row) for bit, row in zip(self.j_mask, sheared))

    def rounded_action(self, rhs):
        sheared = rounded_solve(self.shear_lower, self.shear_upper, rhs,
                               self.block, self.precision)
        boundary = rounded_solve(self.f_lower, self.f_upper,
                                 [sheared[i] for i, bit in enumerate(self.j_mask) if bit],
                                 self.block, self.precision)
        at = iter(boundary)
        return tuple(next(at) if bit else tuple(row) for bit, row in zip(self.j_mask, sheared))

    def receipt(self):
        return dict(source=list(self.source_parameters), reference_sha256=self.reference_sha256,
                    window=[self.origin, self.origin+self.length], band=self.band, cap=self.cap,
                    block=self.block, precision=self.precision, width=self.width,
                    radius=str(self.radius), target=self.target, I=list(self.I), J=list(self.J),
                    E=list(self.E), j_mask=list(self.j_mask), source_gap=str(self.source_gap),
                    F_band=bandwidth(self.F), shear_band=bandwidth(self.N),
                    shear_error=str(self.shear_error), solve_input_radius=str(self.solve_input_radius),
                    total_error=str(self.total_error), root_record_radius=str(self.root_record_radius),
                    error_decimal=float(self.total_error), radius_decimal=float(self.root_record_radius),
                    original_reference=True, source_scope='ordinary exact local-band window; no global outer claim')


def make_window(reference, *, origin=16, length=8, interior_blocks=((1, 2, 3, 4),),
                band=1, cap=4, block=4, precision=24, width=32, radius=Q(1), target=10):
    """Prepare and exactly validate a source-bound ordinary-window contract.

    `reference` must come from the authenticated unchanged canonical Reference
    loader. The explicit interior partition is admitted only after geometry and
    zero-support validation. No online input or RHS count is accepted here.
    """
    reference.require_narrow_gap()
    integers = (origin, length, band, cap, block, precision, width, target)
    need(all(type(x) is int for x in integers), 'integer window preparation descriptors')
    need(length > 0 and band >= 1 and cap > 0 and cap & (cap-1) == 0
         and block > 0 and block & (block-1) == 0 and precision >= 0
         and width > precision and target >= 1, 'positive dyadic window geometry and grid')
    need(0 <= origin < origin+length <= reference.target_size
         and reference.target_size-length >= 2*reference.spec.source_halfwidth+2,
         'ordinary window retains a sufficient original-period complement')
    need(2*cap <= reference.spec.source_size, 'dyadic cap fits original source period')
    radius = Q(radius)
    need(radius >= 1, 'admitted complex-l1 input radius')
    entries = tuple(tuple(reference.entry('narrow', origin+i, origin+j)
                          for j in range(length)) for i in range(length))
    need(all(not entry.value or entry.lift == 0 for row in entries for entry in row),
         'no retained periodic corner inside ordinary window')
    H = frozen(tuple(entry.value for entry in row) for row in entries)
    need(bandwidth(H) <= band, 'exact certified local ordinary bandwidth')
    need(row_norm(H) <= 2 and row_gap(H) >= reference.narrow_gap > 0,
         'same-reference positive row gap and norm')
    blocks = tuple(tuple(part) for part in interior_blocks)
    for part in blocks:
        need(bool(part) and all(type(i) is int for i in part)
             and part == tuple(range(part[0], part[0]+len(part)))
             and 0 <= part[0] and part[-1] < length
             and len(part) <= cap and len(part) & (len(part)-1) == 0,
             'ordinary contiguous dyadic interior')
        source = reference.source_at.get(origin+part[0])
        need(source is not None, 'interior excludes original holes')
        coordinates, _, _ = reference.interior(source, len(part))
        need(tuple(coordinates) == tuple(origin+i for i in part),
             'interior retains original phase and selected coordinates')
    I = tuple(i for part in blocks for i in part)
    need(I == tuple(sorted(set(I))), 'disjoint increasing interiors')
    need(all(not H[i][j] for a, first in enumerate(blocks) for b, second in enumerate(blocks)
             if a != b for i in first for j in second), 'exact zero coupling between interiors')
    J = tuple(i for i in range(length) if i not in set(I))
    need(bool(J), 'nonempty boundary bank')
    A, B, C, D = (sub(H, I, I), sub(H, I, J), sub(H, J, I), sub(H, J, J))
    correction = multiply(multiply(C, inverse(A)), B) if I else tuple(tuple(Q() for _ in J) for _ in J)
    F = frozen(tuple(x-y for x, y in zip(row, term)) for row, term in zip(D, correction))
    need(row_gap(F) >= reference.narrow_gap and row_norm(F) <= 2,
         'exact Schur row gap and row norm')
    E = tuple(sorted(set(J) | {i for i in I if any(H[j][i] or H[i][j] for j in J)}))
    j_mask = tuple(int(i in J) for i in E)
    N = tuple(tuple(H[i][j] if i in J and j in I else Q() for j in E) for i in E)
    need(bandwidth(F) <= 2*band-1 and max(bandwidth(F), bandwidth(N)) <= block,
         'funded compressed Schur and shear bandwidths')
    shear_lower = tuple(tuple(Q(i == j)+(N[i][j] if i//block > j//block else 0)
                              for j in range(len(E))) for i in range(len(E)))
    shear_upper = tuple(tuple(Q(i == j)+(N[i][j] if i//block <= j//block else 0)
                              for j in range(len(E))) for i in range(len(E)))
    need(multiply(N, N) == tuple(tuple(Q() for _ in E) for _ in E), 'source-mask square zero')
    need(multiply(shear_lower, shear_upper) == tuple(tuple(Q(i == j)+N[i][j]
         for j in range(len(E))) for i in range(len(E))), 'exact block-split shear factors')
    f_lower, f_upper = lu(F)
    eta = Q(1, 1 << max(precision-1, 0)) if precision else Q(2)
    budgets = (pass_budget(shear_lower, block, eta),
               pass_budget(reverse(pad(shear_upper, block)), block, eta),
               pass_budget(f_lower, block, eta),
               pass_budget(reverse(pad(f_upper, block)), block, eta))
    s1, s2, f1, f2 = budgets
    shear_error = eta*(s2.inverse*s1.error_coefficient
                      +s2.error_coefficient*4*s1.inverse)*radius
    solve_input_radius = (1+row_norm(N))*radius+shear_error
    f_error = eta*(f2.inverse*f1.error_coefficient
                  +f2.error_coefficient*4*f1.inverse)*solve_input_radius
    total_error = row_norm(inverse(F))*shear_error+f_error
    need(total_error <= Q(1, 1 << target), 'funded full first-window error')
    root = Q()
    for first, second, incoming in ((s1, s2, radius), (f1, f2, solve_input_radius)):
        for budget, value in ((first, incoming), (second, 4*first.inverse*incoming)):
            root = max(root, value, 4*budget.inverse*value,
                       6*budget.inverse*(budget.preceding+1)*value,
                       value+(budget.preceding+block*eta)*4*budget.inverse*value+eta,
                       budget.inverse+1, budget.preceding+1)
    need(root < Q(1 << (width-precision-1)), 'funded signed scalar record carrier')
    need(width >= max(origin+length, reference.target_size, cap, block).bit_length()+2,
         'funded encoded source and runtime descriptor carrier')
    parameters = tuple(getattr(reference.spec, name) for name in reference.spec.__dataclass_fields__)
    return Window(parameters, reference.description_hash, origin, length, band, cap, block,
                  precision, width, radius, target, blocks, I, J, E, j_mask, H, A, B, C, D, F, N,
                  shear_lower, shear_upper, f_lower, f_upper, reference.narrow_gap,
                  budgets, shear_error, solve_input_radius, total_error, root)


def physical_factors(window, pool):
    """Paid setup serializer for exact factors; calls no online numerical work.

    Caller installs its retained setup scope. Returned Matrix owners must all
    be closed after unchanged prepare_pages has emitted the two four-page banks.
    `decode` here indexes immutable setup data and is excluded from the online
    theorem; NUMERICS charges a sequential simulation of this preparation.
    """
    from cardinal_counts import Count
    from gaussian_matrix import Matrix
    from gaussian_rationals import Rational
    from ring_check_words import decode
    from ring_words import Signed
    from router_metadata import owned
    result = []
    def make(value):
        return Rational(Signed(Count.literal(abs(value.numerator)), value < 0),
                        Count.literal(value.denominator))
    try:
        for data in (window.shear_lower, window.shear_upper, window.f_lower, window.f_upper):
            with owned(Count.literal(len(data))) as (size,):
                result.append(Matrix(size, size, pool,
                    lambda i, j, data=data: make(data[decode(i)][decode(j)])))
        return tuple(result)
    except BaseException:
        for matrix in result:
            matrix.close()
        raise
