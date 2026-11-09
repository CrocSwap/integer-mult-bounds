"""Independent original-Reference and rounded union-window finite oracle.

Prepared for @CubeJerry with separate source-aware OpenAI AI verification.
This module is an external exact observer, never an online tape primitive.
No producer elimination, rounded-action function, or physical implementation
is imported.  Apache-2.0.
"""
from fractions import Fraction as Q
from itertools import product


def need(condition, message):
    if not condition:
        raise ValueError(message)


def identity(n):
    return tuple(tuple(Q(i == j) for j in range(n)) for i in range(n))


def product_matrix(a, b):
    need(bool(b) and all(len(row) == len(b) for row in a), "observer matrix dimensions")
    return tuple(tuple(sum((a[i][k]*b[k][j] for k in range(len(b))), Q())
                       for j in range(len(b[0]))) for i in range(len(a)))


def inverse(a):
    """Pivoted triangular elimination plus back-substitution, not producer GJ."""
    n = len(a)
    need(n > 0 and all(len(row) == n for row in a), "observer square inverse")
    upper = [list(map(Q, row)) for row in a]
    right = [list(row) for row in identity(n)]
    for k in range(n):
        pivot = next((i for i in range(k, n) if upper[i][k]), None)
        need(pivot is not None, "observer nonsingular original matrix")
        upper[k], upper[pivot] = upper[pivot], upper[k]
        right[k], right[pivot] = right[pivot], right[k]
        for i in range(k+1, n):
            ratio = upper[i][k]/upper[k][k]
            upper[i][k] = Q()
            for j in range(k+1, n):
                upper[i][j] -= ratio*upper[k][j]
            for j in range(n):
                right[i][j] -= ratio*right[k][j]
    answer = [[Q()]*n for _ in range(n)]
    for i in reversed(range(n)):
        for j in range(n):
            answer[i][j] = (right[i][j]-sum((upper[i][k]*answer[k][j]
                                            for k in range(i+1, n)), Q()))/upper[i][i]
    answer = tuple(map(tuple, answer))
    need(product_matrix(a, answer) == identity(n)
         and product_matrix(answer, a) == identity(n), "both original inverse identities")
    return answer


def sub(a, rows, columns):
    return tuple(tuple(a[i][j] for j in columns) for i in rows)


def toward_zero_integer(numerator, denominator):
    need(denominator > 0, "positive rounding denominator")
    return (1 if numerator >= 0 else -1)*(abs(numerator)//denominator)


def grid_integer(value, p):
    value = Q(value)
    return toward_zero_integer(value.numerator << p, value.denominator)


def padded(a, block):
    n = len(a)
    size = ((n+block-1)//block)*block
    return tuple(tuple(a[i][j] if i < n and j < n else Q(i == j)
                       for j in range(size)) for i in range(size))


def page_words(lower, upper, block, precision):
    """Derive all four page banks independently, including padded reversal."""
    banks = []
    for direction, raw in enumerate((lower, upper)):
        a = padded(raw, block)
        if direction:
            a = tuple(tuple(a[-i-1][-j-1] for j in range(len(a))) for i in range(len(a)))
        diagonals, couplings = [], []
        for start in range(0, len(a), block):
            rows = tuple(range(start, start+block))
            diagonal = inverse(sub(a, rows, rows))
            diagonals.extend(grid_integer(x, precision) for row in diagonal for x in row)
            if start:
                couplings.extend(grid_integer(a[i][j], precision)
                                 for i in rows for j in range(start-block, start))
        banks.extend((tuple(diagonals), tuple(couplings)))
    return tuple(banks)


def check_source(reference, window):
    """Use inverse(full original Q)_JJ = inverse(F), avoiding C A^-1 B."""
    n, jset, iset, exposed = window.length, tuple(window.J), tuple(window.I), tuple(window.E)
    original = tuple(tuple(Q(reference.entry("narrow", window.origin+i, window.origin+j).value)
                           for j in range(n)) for i in range(n))
    need(original == window.H, "original Reference principal window")
    need(tuple(sorted(iset+jset)) == tuple(range(n)) and not set(iset)&set(jset),
         "independent complete interior/boundary partition")
    need(jset == tuple(i for i in range(n) if i not in set(iset)), "increasing boundary order")
    complete_inverse = inverse(original)
    boundary_inverse = sub(complete_inverse, jset, jset)
    f_from_original = inverse(boundary_inverse)
    need(f_from_original == window.F, "full original inverse gives exact Schur F")
    expected_e = tuple(i for i in range(n) if i in jset or any(
        original[i][j] or original[j][i] for j in jset))
    need(exposed == expected_e, "complete incident exposed set")
    for name, rows, columns in (("A", iset, iset), ("B", iset, jset),
                               ("C", jset, iset), ("D", jset, jset)):
        need(getattr(window, name) == sub(original, rows, columns), "original block "+name)
    mask = tuple(int(i in jset) for i in exposed)
    coupling = tuple(tuple(original[i][j] if i in jset and j in iset else Q()
                           for j in exposed) for i in exposed)
    need(mask == window.j_mask and coupling == window.N, "original C0 lifted in complete E")
    m, b = len(exposed), window.block
    pieces = tuple(tuple(tuple(coupling[i][j] if relation(i//b, j//b) else Q()
                               for j in range(m)) for i in range(m))
                   for relation in (lambda i,j:i>j, lambda i,j:i==j, lambda i,j:i<j))
    zero = tuple(tuple(Q() for _ in range(m)) for _ in range(m))
    for first in pieces:
        for second in pieces:
            need(product_matrix(first, second) == zero, "all nine masked products vanish")
    expected_lower = tuple(tuple(Q(i == j)+pieces[0][i][j] for j in range(m)) for i in range(m))
    expected_upper = tuple(tuple(Q(i == j)+pieces[1][i][j]+pieces[2][i][j]
                                 for j in range(m)) for i in range(m))
    need(expected_lower == window.shear_lower and expected_upper == window.shear_upper,
         "source block-split shear factors")
    need(product_matrix(window.f_lower, window.f_upper) == f_from_original,
         "source Schur factor product")
    shear = page_words(expected_lower, expected_upper, b, window.P)
    schur = page_words(window.f_lower, window.f_upper, b, window.P)
    return dict(original_identity_entries=2*n*n, boundary_identity_entries=2*len(jset)**2,
                annihilation_products=9, exposed=exposed, selected=jset,
                shear_pages=shear, schur_pages=schur)


def source_operator(reference, window):
    """Exact first-window map directly from original inverse and original C0."""
    original = tuple(tuple(Q(reference.entry("narrow", window.origin+i, window.origin+j).value)
                           for j in range(window.length)) for i in range(window.length))
    f_inverse = sub(inverse(original), window.J, window.J)
    exposed = tuple(window.E)
    boundary_rows = tuple(tuple(Q(i == j)-(original[i][j] if j in window.I else 0)
                                for j in exposed) for i in window.J)
    corrected = iter(product_matrix(f_inverse, boundary_rows))
    return tuple(next(corrected) if i in window.J
                 else tuple(Q(i == j) for j in exposed) for i in exposed)


def source_controls(reference, window):
    """These are bad source bindings, not attacks the online parser promises."""
    from dataclasses import replace
    controls = []
    wrong_n = [list(row) for row in window.N]
    nonzero = next((i,j) for i,row in enumerate(wrong_n) for j,x in enumerate(row) if x)
    wrong_n[nonzero[0]][nonzero[1]] = Q()
    alternatives = ((replace(window, origin=window.origin+1), 'original Reference principal window'),
        (replace(window, F=tuple(zip(*window.F))), 'full original inverse gives exact Schur F'),
        (replace(window, N=tuple(map(tuple,wrong_n))), 'original C0 lifted in complete E'),
        (replace(window, E=tuple(reversed(window.E))), 'complete incident exposed set'))
    for bad, wanted in alternatives:
        try:
            check_source(reference, bad)
        except ValueError as error:
            need(wanted in str(error), 'specific independent source control: '+str(error))
        else:
            raise ValueError('source mutation was not distinguished: '+wanted)
        controls.append(wanted)
    return tuple(controls)


def solve_pages(banks, rhs, block, p):
    """Pure integer completed-dot recurrence, returning original row order."""
    rows = len(rhs)
    need(rows > 0 and bool(rhs[0]), "nonempty oracle RHS")
    columns, scale = len(rhs[0]), 1 << p
    size = ((rows+block-1)//block)*block
    current = [list(row) for row in rhs]+[[0]*columns for _ in range(size-rows)]
    need(all(len(row) == columns for row in current), "rectangular oracle RHS")
    for direction in range(2):
        if direction:
            current = current[::-1]
        diagonal_bank, coupling_bank = banks[2*direction:2*direction+2]
        need(len(diagonal_bank) == size*block and len(coupling_bank) == (size-block)*block,
             "oracle complete page extents")
        output = []
        for start in range(0, size, block):
            residual = [list(row) for row in current[start:start+block]]
            if start:
                at = (start-block)*block
                for i in range(block):
                    for c in range(columns):
                        dot = sum(coupling_bank[at+i*block+j]*output[start-block+j][c]
                                  for j in range(block))
                        residual[i][c] = toward_zero_integer(scale*residual[i][c]-dot, scale)
            at = start*block
            for i in range(block):
                output.append([toward_zero_integer(sum(diagonal_bank[at+i*block+j]*residual[j][c]
                                                       for j in range(block)), scale)
                               for c in range(columns)])
        current = output
    return tuple(tuple(row) for row in current[::-1][:rows])


def window_action(window, rhs, *, pages=None):
    if pages is None:
        pages = (page_words(window.shear_lower, window.shear_upper, window.block, window.P),
                 page_words(window.f_lower, window.f_upper, window.block, window.P))
    sheared = solve_pages(pages[0], rhs, window.block, window.P)
    boundary = solve_pages(pages[1], tuple(row for row, flag in zip(sheared, window.j_mask) if flag),
                           window.block, window.P)
    it = iter(boundary)
    result = tuple(next(it) if flag else row for row, flag in zip(sheared, window.j_mask))
    need(all(row == old for row, old, flag in zip(result, rhs, window.j_mask) if not flag),
         "E minus J is bit-exact")
    return result


def full_grid(side, windows, inputs, *, axis_order=None):
    """Independent ascending-axis schedule; nonlinear flag-class causality.

    inputs maps every coordinate tuple to the real/imag integer numerator pair.
    No union round order, parser, batching, or host regrouping from the physical
    verifier is imported. Each axis reads the data changed by earlier axes.
    """
    d = len(windows)
    coordinates = tuple(product(range(side), repeat=d))
    need(set(inputs) == set(coordinates), "complete independent full-grid input")
    grid = {x: tuple(inputs[x]) for x in coordinates}
    visited, changed_later, largest_l1 = 0, 0, 0
    order = tuple(range(d)) if axis_order is None else tuple(axis_order)
    need(sorted(order) == list(range(d)), "complete oracle axis order")
    for step, axis in enumerate(order):
        window = windows[axis]
        need(window.length == side, "one original window per full-grid axis")
        pages = (page_words(window.shear_lower, window.shear_upper, window.block, window.P),
                 page_words(window.f_lower, window.f_upper, window.block, window.P))
        for other in product(range(side), repeat=d-1):
            points = tuple(other[:axis]+(v,)+other[axis:] for v in window.E)
            rhs = tuple(grid[x] for x in points)
            if step and any(grid[x] != tuple(inputs[x]) for x in points):
                changed_later += 1
            largest_l1 = max(largest_l1, *(abs(a)+abs(b) for a,b in rhs))
            answer = window_action(window, rhs, pages=pages)
            for x, pair in zip(points, answer):
                grid[x] = pair
            visited += len(points)
    return grid, dict(visited_records=visited, later_lines_with_changed_inputs=changed_later,
                      maximum_incoming_l1_numerator=largest_l1)


def decode_records(bits, axes, coordinate_bits, tag_bits, width):
    """Independent fixed-schema external observer, retaining exact headers."""
    header_size = 2+2*axes*coordinate_bits+axes+2*tag_bits
    stride = header_size+2*width
    need(len(bits) % stride == 0 and all(x in (0,1) for x in bits),
         "complete external union records")
    result = []
    for start in range(0, len(bits), stride):
        header = tuple(bits[start:start+header_size])
        need(header[:2] == (0,1), "external union marker")
        coordinate = []
        for i in range(axes):
            value = 0
            for bit in header[2+i*coordinate_bits:2+(i+1)*coordinate_bits]:
                value = 2*value+bit
            coordinate.append(value)
        pair = []
        for component in range(2):
            at = start+header_size+component*width
            field = bits[at:at+width]
            value = sum(bit << i for i,bit in enumerate(field))
            pair.append(value-(field[-1] << width))
        result.append((tuple(coordinate),header,tuple(pair)))
    return tuple(result)


def check_record_return(before, after, expected, axes, coordinate_bits, tag_bits, width):
    incoming = decode_records(before, axes, coordinate_bits, tag_bits, width)
    outgoing = decode_records(after, axes, coordinate_bits, tag_bits, width)
    need(len(incoming) == len(outgoing), "unchanged record count")
    for (point,header,_), (returned,retained,pair) in zip(incoming,outgoing):
        need((point,header) == (returned,retained), "bit-exact immutable union header return")
        need(pair == tuple(expected[point]), "independent staged union payload return")
    return len(outgoing)


def causality_control():
    """A scoped dyadic example demonstrates rounded axis noncommutation."""
    from types import SimpleNamespace
    window = SimpleNamespace(length=2, E=(0,1), j_mask=(1,0), block=2, P=2,
        shear_lower=identity(2), shear_upper=((Q(1),Q(1,4)),(Q(0),Q(1))),
        f_lower=((Q(1),),), f_upper=((Q(1),),))
    inputs = {(0,0):(-3,0), (0,1):(-3,0), (1,0):(-1,0), (1,1):(-3,0)}
    forward, first_receipt = full_grid(2, (window,window), inputs)
    backward, _ = full_grid(2, (window,window), inputs, axis_order=(1,0))
    need(forward[(0,0)] == (-1,0) and backward[(0,0)] == (-2,0),
         "opposite rounded axis orders give distinct exact words")
    need(first_receipt['later_lines_with_changed_inputs'] > 0,
         "noncommutation control uses updated inputs")
    return dict(forward_numerator=-1, reversed_numerator=-2, precision=2,
                scope='independent dyadic support control, not an actual Reference fixture')
