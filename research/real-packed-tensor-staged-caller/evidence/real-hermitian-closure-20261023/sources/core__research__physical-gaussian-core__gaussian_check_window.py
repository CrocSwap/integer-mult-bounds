"""Complete old-H principal/Schur page setup, including physical-period cuts."""
from fractions import Fraction as Q
from hashlib import sha256
import importlib.util
from gaussian_sources import active, require
from gaussian_check_interior import dense_solution


def inverse(matrix):
    n = len(matrix)
    columns = [dense_solution(matrix, [Q(int(i == j)) for i in range(n)]) for j in range(n)]
    return [[columns[j][i] for j in range(n)] for i in range(n)]


def lu(matrix):
    n = len(matrix)
    low, high = [[Q(0)]*n for _ in range(n)], [row[:] for row in matrix]
    for i in range(n):
        low[i][i] = 1
        for j in range(i+1, n):
            low[j][i] = high[j][i]/high[i][i]
            for k in range(i, n):
                high[j][k] -= low[j][i]*high[i][k]
    return low, high


def schur(matrix, boundary, interior, inverse_i):
    return [[matrix[i][j]-sum((matrix[i][a]*inverse_i[x][y]*matrix[b][j]
                               for x, a in enumerate(interior) for y, b in enumerate(interior)), Q(0))
             for j in boundary] for i in boundary]


def run():
    from cardinal_counts import Count
    from check_support import no_decode
    from gaussian_axis import Axis
    from gaussian_core import Core
    from gaussian_rationals import read_count
    from gaussian_window import Window
    from ring_check_words import body, decode
    from ring_words import Signed, read_signed, write_signed
    from router_metadata import owned
    from scratch_pool import ScratchPool
    from session import OuterScope, borrowed_tape, erase_marker, sealed_constructors
    from words import BLANK
    reference_path = active().branchfree_package / "code/branchfree.py"
    spec = importlib.util.spec_from_file_location("gaussian_window_branchfree_reference", reference_path)
    reference = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(reference)
    pool = ScratchPool(512)
    scope = OuterScope(pool)
    core = Core()
    s, t, u, w, bits, p = 13, 14, 1, 1, 24, 16
    records = []
    with owned(*(Count.literal(v) for v in (s, t, u, w, bits))) as parameters:
        with sealed_constructors(), scope.installed():
            axis = None
            try:
                with no_decode():
                    axis = Axis(*parameters, pool)
                def get(matrix, i, j):
                    with owned(Count.literal(i), Count.literal(j)) as (row, column):
                        with owned(matrix.get(row, column)) as (value,):
                            return Q((-1 if value.numerator.negative else 1)*decode(value.numerator.magnitude),
                                     decode(value.denominator))
                h = [[get(axis.matrix, i, j) for j in range(s)] for i in range(s)]
                weights = [[get(axis.weights, i, j) for j in range(5)] for i in range(s)]
                q = get(axis.kernel, 1, 0)
                for target_start, target_length, core_start, core_length in ((1, 5, 2, 3), (11, 8, 12, 4), (4, 7, 5, 4)):
                    window = None
                    with owned(Signed(Count.literal(target_start)), Count.literal(target_length),
                               Signed(Count.literal(core_start)), Count.literal(core_length), Count.literal(p)) as args:
                        try:
                            with no_decode():
                                window = Window(axis, *args, pool)
                            require(all(getattr(window, name) is None for name in
                                        ("principal", "kernel_inverse", "schur", "rounded_schur", "lower", "upper")),
                                    "dense rational window setup leaves only its compiled page")
                            start = Q(s*(2*target_start-1), 2*t).__ceil__()
                            end = Q(s*(2*(target_start+target_length)-1), 2*t).__ceil__()
                            selected = list(range(start, end))
                            cells = []
                            previous = None
                            for position, j in enumerate(selected):
                                residue, period = j % s, j//s
                                identity = period, weights[residue][2]
                                if identity != previous:
                                    cells.append([])
                                cells[-1].append(position)
                                previous = identity
                            boundary = [i for cell in cells for i in
                                        (cell if len(cell) <= 4*w else cell[:w]+cell[-w:])]
                            interior = [i for cell in cells if len(cell) > 4*w for i in cell[w:-w]]
                            source = [[h[i % s][j % s] for j in selected] for i in selected]
                            block = [[source[i][j] for j in interior] for i in interior]
                            inverse_i = inverse(block) if interior else []
                            exact_s = schur(source, boundary, interior, inverse_i)
                            rounding = lambda x: Q(int(x*(1 << bits)), 1 << bits)
                            rounded_s = [[rounding(x) for x in row] for row in exact_s]
                            low, high = lu(rounded_s)
                            page = window.page
                            page.rewind()
                            payload = bytearray()
                            while page.read() != BLANK:
                                payload.append(page.read())
                                page.step(1)
                            page.rewind()
                            header = []
                            for _ in range(11):
                                with owned(read_count(page)) as (value,):
                                    header.append(decode(value))
                            width = bits+8*p+8*(p+1).bit_length()+34
                            require(header == [1, p, bits, width, len(selected), target_length,
                                               core_start-start, core_length, len(boundary), 2*w, len(cells)],
                                    "complete principal-window page header")
                            for j in selected:
                                expected = (Q(t*j, s)+Q(1, 2)).__floor__()-target_start
                                with owned(read_count(page)) as (value,):
                                    require(decode(value) == expected, "exact lifted target selection")
                            def read_value():
                                with owned(Count.literal(width)) as (field,):
                                    with owned(read_signed(page, field)) as (value,):
                                        return Q((-1 if value.negative else 1)*decode(value.magnitude), 1 << bits)
                            for cell in cells:
                                expected_inside = cell[w:-w] if len(cell) > 4*w else []
                                expected_boundary = cell[:w]+cell[-w:] if expected_inside else cell
                                actual_descriptor = []
                                for _ in range(3):
                                    with owned(read_count(page)) as (value,):
                                        actual_descriptor.append(decode(value))
                                require(actual_descriptor == [len(cell), len(expected_inside), len(expected_boundary)],
                                        "original physical cell cuts and clipped boundary pieces")
                                if expected_inside:
                                    a = [weights[selected[i] % s][0] for i in expected_inside]
                                    factors = reference.prepare(q, a, bits)
                                    for name in ("weights", "inva", "f", "invf", "h"):
                                        actual = [read_value() for _ in expected_inside]
                                        require(actual == factors[name], "compiled branch-free factor page")
                                    edge = expected_inside[:w]+expected_inside[-w:]
                                    for rows, columns in ((expected_boundary, edge), (edge, expected_boundary)):
                                        for i in rows:
                                            for j in columns:
                                                require(read_value() == rounding(source[i][j]),
                                                        "original H coupling edge coefficients")
                                for i in cell:
                                    require(read_value() == weights[selected[i] % s][3],
                                            "compiled global D normalization")
                            for i in range(len(boundary)):
                                for j in range(i-2*w, i):
                                    expected = rounding(low[i][j]) if j >= 0 else Q(0)
                                    require(read_value() == expected, "old-H rounded Schur lower factors")
                            for i in reversed(range(len(boundary))):
                                for j in range(i+1, i+2*w+1):
                                    expected = rounding(high[i][j]) if j < len(boundary) else Q(0)
                                    require(read_value() == expected, "old-H rounded Schur upper factors")
                                require(read_value() == rounding(1/high[i][i]), "exact rounded-Schur pivot reciprocal")
                            require(page.read() == BLANK, "complete structured page extent")
                            page.rewind()
                            model_differs = False
                            if interior:
                                model = [[Q(0)]*len(interior) for _ in interior]
                                for cell in cells:
                                    ii = cell[w:-w] if len(cell) > 4*w else []
                                    for i in ii:
                                        for j in ii:
                                            model[interior.index(i)][interior.index(j)] = (
                                                weights[selected[i] % s][0]*q**((i-j)**2)/weights[selected[j] % s][0])
                                wrong_s = schur(source, boundary, interior, inverse(model))
                                model_differs = wrong_s != exact_s
                                require(model_differs, "local q-model must not replace old-H Schur setup")
                            target_data = [(Q((7*i+3) % 13-6, 16), Q((5*i+1) % 11-5, 16))
                                           for i in range(target_length)]
                            selected_data = [target_data[(Q(t*j, s)+Q(1, 2)).__floor__()-target_start]
                                             for j in selected]
                            expected_components = []
                            dense_error = Q(0)
                            j_scale = (32*p-1).bit_length()
                            for component in (0, 1):
                                b = [pair[component] for pair in selected_data]
                                first = [Q(0)]*len(selected)
                                for cell in cells:
                                    ii = cell[w:-w] if len(cell) > 4*w else []
                                    if ii:
                                        table = reference.prepare(q, [weights[selected[i] % s][0] for i in ii], bits)
                                        y = reference.apply(table, [b[i] for i in ii], reference.counter())
                                        for i, value in zip(ii, y):
                                            first[i] = value
                                rhs_b = [rounding(b[i]-sum((rounding(source[i][j])*first[j] for j in interior), Q(0)))
                                         for i in boundary]
                                y_b, x_b = [Q(0)]*len(boundary), [Q(0)]*len(boundary)
                                for i in range(len(boundary)):
                                    y_b[i] = rounding(rhs_b[i]-sum((rounding(low[i][j])*y_b[j] for j in range(i)), Q(0)))
                                for i in reversed(range(len(boundary))):
                                    x_b[i] = rounding(rounding(1/high[i][i])*(y_b[i]-sum(
                                        (rounding(high[i][j])*x_b[j] for j in range(i+1, len(boundary))), Q(0))))
                                merged = [Q(0)]*len(selected)
                                for i, value in zip(boundary, x_b):
                                    merged[i] = value
                                for cell in cells:
                                    ii = cell[w:-w] if len(cell) > 4*w else []
                                    if ii:
                                        table = reference.prepare(q, [weights[selected[i] % s][0] for i in ii], bits)
                                        rhs_i = [rounding(b[i]-sum((rounding(source[i][j])*value
                                                                  for j, value in zip(boundary, x_b)), Q(0))) for i in ii]
                                        final = reference.apply(table, rhs_i, reference.counter())
                                        for i, value in zip(ii, final):
                                            merged[i] = value
                                exact_solution = dense_solution(source, b)
                                expected = []
                                for i in range(core_start-start, core_start-start+core_length):
                                    diagonal = weights[selected[i] % s][3]
                                    integer = int(diagonal*merged[i]*(1 << p)/(1 << j_scale))
                                    expected.append(integer)
                                    dense_error = max(dense_error, abs(Q(integer, 1 << p)
                                                      -diagonal*exact_solution[i]/(1 << j_scale)))
                                expected_components.append(expected)
                            target_tape = pool.acquire()
                            returned = None
                            with owned(Count.literal(p+2)) as (input_width,):
                                try:
                                    for pair in target_data:
                                        for value in pair:
                                            integer = int(value*(1 << p))
                                            with owned(Signed(Count.literal(abs(integer)), integer < 0)) as (encoded,):
                                                write_signed(encoded, target_tape, input_width)
                                    target_tape.rewind()
                                    saved = [(bytes(borrowed_tape(value).cells), borrowed_tape(value).head)
                                             for value in (page, target_tape)]
                                    local_calls, boundary_calls = core.interior.calls, core.boundary.calls
                                    word_calls = dict(core.word.calls)
                                    with scope.suspended(), no_decode():
                                        returned = core.run(page, target_tape)
                                    raw_return = body(returned)
                                    actual = []
                                    for _ in range(core_length):
                                        pair = []
                                        for _ in range(2):
                                            with owned(read_signed(returned, input_width)) as (value,):
                                                pair.append((-1 if value.negative else 1)*decode(value.magnitude))
                                        actual.append(pair)
                                    require(actual == [list(pair) for pair in zip(*expected_components)]
                                            and returned.read() == BLANK, "complete true-Gaussian producer/consumer equals staged oracle")
                                    require(dense_error < Q(2, 1 << p), "complete core agrees with dense exact old-H inverse")
                                    require(any(value for pair in actual for value in pair), "nonzero true Gaussian core")
                                    require(saved == [(bytes(borrowed_tape(value).cells), borrowed_tape(value).head)
                                                      for value in (page, target_tape)], "complete Gaussian join preserves borrowed ports")
                                    require(core.interior.calls-local_calls == 4*sum(len(cell) > 4*w for cell in cells)
                                            and core.boundary.calls-boundary_calls == 2, "actual complete two-pass Gaussian join")
                                    long_cells = sum(len(cell) > 4*w for cell in cells)
                                    expected_words = (20*len(interior)+16*w*w*long_cells
                                                      +2*len(boundary)*(4*w+1)+2*len(selected)
                                                      +2*target_length+2*core_length+32*long_cells)
                                    actual_words = {key: core.word.calls[key]-word_calls[key] for key in word_calls}
                                    require(sum(actual_words.values()) == expected_words,
                                            "complete scalar, packed, validation and normalization word invoice")
                                    core.idle()
                                    require(core.closed and not core.pool.live
                                            and all(tape.head == 1 and all(bit == BLANK for bit in tape.cells)
                                                    for tape in core.pool.tapes), "complete joined Gaussian owner restoration")
                                finally:
                                    if returned is not None:
                                        returned.clear()
                                        erase_marker(returned)
                                    target_tape.clear()
                            records.append({"target_start": target_start, "target_length": target_length,
                                            "source_start": start, "source_length": len(selected),
                                            "cell_lengths": [len(cell) for cell in cells],
                                            "interior_rows": len(interior), "boundary_rows": len(boundary),
                                            "model_schur_differs": model_differs,
                                            "page_sha256": sha256(payload).hexdigest(),
                                            "core_sha256": sha256(raw_return).hexdigest(),
                                            "core_values": actual, "dense_core_error": str(dense_error),
                                            "interior_calls": core.interior.calls-local_calls,
                                            "boundary_calls": core.boundary.calls-boundary_calls,
                                            "word_calls": actual_words})
                        finally:
                            if window is not None:
                                window.close()
            finally:
                if axis is not None:
                    axis.close()
                pool.empty()
    for tape in pool.tapes:
        erase_marker(tape)
        require(tape.head == 1 and all(v == BLANK for v in tape.cells), "complete window setup restoration")
    return {"axis": [s, t, u, w], "work_precision": bits, "target_precision": p,
            "windows": records, "pool_peak": pool.peak,
            "scope": "complete encoded global-H/page producer and normalized complex core at finite precision; production asymptotic parameters remain separate"}
