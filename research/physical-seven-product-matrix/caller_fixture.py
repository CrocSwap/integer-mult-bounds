"""Reduced-grid supplied-factor fixture adapted from Jose Manuel gaussian_check_consumer.
Adapted from physical-two-column-boundary-kernel/source_fixture.py at canonical
7c49fe32c55de02c2c873655c804b16e4c3fef0a. Only the explicit signed payload
family varies; exact LU(round_P(S)) is unchanged.
Checker-only Fraction setup; actual Core.gather/first_cell execute unchanged.
Prepared for @CubeJerry with OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as Q
import importlib.util
from gaussian_sources import active
from gaussian_check_window import inverse, lu, schur

def fixture(length=8, payload_case=0):
    from cardinal_counts import Count
    from gaussian_rationals import write_count
    from records import Tape
    from ring_words import Signed, write_signed
    from router_metadata import owned
    spec = importlib.util.spec_from_file_location("rhs_branchfree_reference", active().branchfree_package / "code/branchfree.py")
    reference = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(reference)
    if length not in (1,5,8):
        raise ValueError("fixed supplied-source cases")
    bits = 16
    p, band = 4, 2
    target_length = 1 if length == 1 else length+1
    selection = [0] if length == 1 else [0,1]+list(range(3,length+1))
    inside = [] if length == 1 else [1, 2, 3]
    boundary = [i for i in range(length) if i not in inside]
    cells = [(1,0,1)] if length == 1 else [(5,3,2)]+([(3,0,3)] if length == 8 else [])
    width = 32
    q = Q(1, 16)
    matrix = [[Q(int(i == j)) for j in range(length)] for i in range(length)]
    if inside:
        for i in inside:
            for j in inside:
                matrix[i][j] = q**((i-j)**2)
        for a, b in ((0, 1), (1, 0), (3, 4), (4, 3)):
            matrix[a][b] = Q(1, 64)
    if length == 8:
        for i in range(4,7):
            matrix[i][i+1] = matrix[i+1][i] = Q(1,32)
    block = [[matrix[i][j] for j in inside] for i in inside]
    exact_s = schur(matrix, boundary, inside, inverse(block) if inside else [])
    rounding = lambda x: Q(int(x*(1 << bits)), 1 << bits)
    rounded_s = [[rounding(v) for v in row] for row in exact_s]
    exact_low, exact_high = lu(rounded_s)
    low = [[rounding(v) for v in row] for row in exact_low]
    high = [[rounding(v) for v in row] for row in exact_high]
    reciprocal = [rounding(1/exact_high[i][i]) for i in range(len(boundary))]
    factors = reference.prepare(q, [Q(1)]*len(inside), bits) if inside else None
    target = [(Q((3*i+2+payload_case) % 7-3, 8), Q((5*i+1+2*payload_case) % 7-3, 8)) for i in range(target_length)]
    page, source = Tape(), Tape()
    with owned(Count.literal(width), Count.literal(p+2)) as (work_width, input_width):
        def put_count(value):
            with owned(Count.literal(value)) as (count,):
                write_count(count, page)
        def put(value, destination=page, field=work_width, precision=bits):
            integer = int(value*(1 << precision))
            with owned(Signed(Count.literal(abs(integer)), integer < 0)) as (encoded,):
                write_signed(encoded, destination, field)
        for value in (1, p, bits, width, length, target_length, 0, length, len(boundary), band, len(cells)):
            put_count(value)
        for value in selection:
            put_count(value)
        for cell_index,(cell_length,cell_inside,cell_boundary) in enumerate(cells):
            for value in (cell_length,cell_inside,cell_boundary):
                put_count(value)
            if cell_inside:
                for name in ("weights", "inva", "f", "invf", "h"):
                    for value in factors[name]:
                        put(value)
                edges = inside[:1]+inside[-1:]
                for rows, columns in (([0,4],edges),(edges,[0,4])):
                    for i in rows:
                        for j in columns:
                            put(rounding(matrix[i][j]))
            for _ in range(cell_length):
                put(Q(1,2))
        for i in range(len(boundary)):
            for j in range(i-band, i):
                put(low[i][j] if j >= 0 else Q(0))
        for i in reversed(range(len(boundary))):
            for j in range(i+1, i+band+1):
                put(high[i][j] if j < len(boundary) else Q(0))
            put(reciprocal[i])
        for real, imaginary in target:
            put(real, source, input_width, p)
            put(imaginary, source, input_width, p)
        page.rewind()
        source.rewind()
    expected = []
    for component in (0, 1):
        b = [target[i][component] for i in selection]
        y = reference.apply(factors, [b[i] for i in inside], reference.counter()) if inside else []
        expected.append([rounding(b[i]-sum((rounding(matrix[i][j])*y[k] for k,j in enumerate(inside)), Q())) for i in boundary])
    return page, source, exact_low, exact_high, expected, width, bits
