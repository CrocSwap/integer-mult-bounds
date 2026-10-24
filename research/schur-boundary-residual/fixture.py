"""Finite, observer-only replay of the retained Window/BandedSolve source.

The caller authenticates and opens gaussian_sources before calling run_fixture.
Raw tape snapshots are decoded only after the protected source call returns.
No Fraction value is supplied to setup or used to replace runtime arithmetic.
The small p=16, P=24 fixture does not satisfy the production precision premise.
"""
from fractions import Fraction as Q
from hashlib import sha256


def require(condition, message):
    if not condition:
        raise ValueError(message)


def tape_bytes(tape):
    """Observer-only copy, including the physical tape behind a setup lease."""
    from session import borrowed_tape
    return bytes(borrowed_tape(tape).cells)


def count(raw):
    require(raw[0] == 2, "observed Count left marker")
    value, end = field(raw, 1)
    require(all(x == 4 for x in raw[end:]), "observed Count complete extent")
    return value


def field(raw, pos):
    start, value = pos, 0
    while pos < len(raw) and raw[pos] in (0, 1):
        value += raw[pos] << (pos-start)
        pos += 1
    require(pos > start and pos < len(raw) and raw[pos] == 3, "canonical count record")
    require(pos == start+1 or raw[pos-1] == 1, "canonical count high bit")
    return value, pos+1


def body(raw):
    require(raw[0] == 2, "observed tape left marker")
    end = raw.find(bytes([4]), 1)
    end = len(raw) if end < 0 else end
    require(all(x == 4 for x in raw[end:]), "observed erased suffix")
    return raw[1:end]


def matrix_snapshot(matrix):
    return (tape_bytes(matrix.rows.tape), tape_bytes(matrix.columns.tape), tape_bytes(matrix.current))


def matrix(snapshot):
    rows, columns = count(snapshot[0]), count(snapshot[1])
    raw, pos, result = snapshot[2], 1, []
    require(raw[0] == 2, "matrix left marker")
    for _ in range(rows):
        row = []
        for _ in range(columns):
            sign = raw[pos]
            require(sign in (0, 1), "matrix rational sign")
            numerator, pos = field(raw, pos+1)
            denominator, pos = field(raw, pos)
            require(denominator > 0 and (numerator or not sign), "matrix rational form")
            row.append(Q((-1 if sign else 1)*numerator, denominator))
        result.append(row)
    require(all(x == 4 for x in raw[pos:]), "matrix exact extent")
    return result


def fixed(raw, width):
    payload = body(raw)
    require(len(payload) % width == 0 and all(x in (0, 1) for x in payload),
            "fixed signed record extent")
    result = []
    for start in range(0, len(payload), width):
        bits = payload[start:start+width]
        result.append(sum(v << i for i, v in enumerate(bits))-(bits[-1] << width))
    return result


def inverse(a):
    n = len(a)
    work = [list(row)+[Q(int(i == j)) for j in range(n)] for i, row in enumerate(a)]
    for col in range(n):
        pivot = next((i for i in range(col, n) if work[i][col]), None)
        require(pivot is not None, "independent inverse nonsingularity")
        work[col], work[pivot] = work[pivot], work[col]
        scale = work[col][col]
        work[col] = [x/scale for x in work[col]]
        for i in range(n):
            if i != col:
                scale = work[i][col]
                work[i] = [x-scale*y for x, y in zip(work[i], work[col])]
    return [row[n:] for row in work]


def mul(a, b):
    return [[sum((x*y for x, y in zip(row, col)), Q(0))
             for col in zip(*b)] for row in a]


def mv(a, v):
    return [sum((x*y for x, y in zip(row, v)), Q(0)) for row in a]


def sub(a, b):
    return [[x-y for x, y in zip(row, other)] for row, other in zip(a, b)]


def vector_sub(a, b):
    return [x-y for x, y in zip(a, b)]


def norm(a):
    return max((sum(map(abs, row), Q(0)) for row in a), default=Q(0))


def encode(value):
    if isinstance(value, Q):
        return [value.numerator, value.denominator]
    if isinstance(value, (tuple, list)):
        return [encode(x) for x in value]
    if isinstance(value, dict):
        return {key: encode(item) for key, item in value.items()}
    return value


def run_fixture():
    from cardinal_counts import Count
    from check_support import no_decode
    from gaussian_axis import Axis
    import gaussian_boundary as boundary_module
    import gaussian_window as window_module
    from ring_words import Signed, write_signed
    from router_metadata import owned
    from scratch_pool import ScratchPool
    from session import OuterScope, borrowed_tape, erase_marker, sealed_constructors

    bits, p, scale, bandwidth = 24, 16, 1 << 24, 2
    rounding = lambda x: Q(int(x*scale), scale)
    observed = {}
    saved_prepare, saved_close = window_module.prepare_bands, window_module.Window.close_dense

    def observe_banks(*args):
        result = saved_prepare(*args)
        observed["banks"] = tuple(tape_bytes(tape) for tape in result)
        return result

    def observe_dense(self):
        if self.schur is not None:
            observed["dense"] = {name: matrix_snapshot(getattr(self, name))
                                 for name in ("principal", "schur", "rounded_schur", "lower", "upper")}
            observed["width"] = tape_bytes(self.width.tape)
        return saved_close(self)

    pool = ScratchPool(512)
    scope = OuterScope(pool)
    axis = window = None
    window_module.prepare_bands, window_module.Window.close_dense = observe_banks, observe_dense
    try:
        with owned(*(Count.literal(v) for v in (13, 14, 1, 1, bits))) as parameters:
            with sealed_constructors(), scope.installed():
                try:
                    with no_decode():
                        axis = Axis(*parameters, pool)
                    observed["old_h"] = matrix_snapshot(axis.matrix)
                    observed["weights"] = matrix_snapshot(axis.weights)
                    with owned(Signed(Count.literal(11)), Count.literal(8),
                               Signed(Count.literal(12)), Count.literal(4), Count.literal(p)) as args:
                        with no_decode():
                            window = window_module.Window(axis, *args, pool)
                        require(all(getattr(window, name) is None for name in
                                    ("principal", "schur", "rounded_schur", "lower", "upper")),
                                "source Window releases dense setup")
                        page_body = body(tape_bytes(window.page))
                        require(page_body.endswith(b"".join(body(bank) for bank in observed["banks"])),
                                "reused banks are the actual compiled Window page suffix")
                        observed["page_sha256"] = sha256(page_body).hexdigest()
                finally:
                    if window is not None:
                        window.close()
                    if axis is not None:
                        axis.close()
                    pool.empty()
    finally:
        window_module.prepare_bands, window_module.Window.close_dense = saved_prepare, saved_close
    for tape in pool.tapes:
        erase_marker(tape)
    require(not pool.live and all(t.head == 1 and all(x == 4 for x in t.cells) for t in pool.tapes),
            "complete setup scratch cleanup")

    h, weights = matrix(observed["old_h"]), matrix(observed["weights"])
    selected = list(range(Q(13*21, 28).__ceil__(), Q(13*37, 28).__ceil__()))
    cells, previous = [], None
    for position, j in enumerate(selected):
        key = (j//13, weights[j % 13][2])
        if key != previous:
            cells.append([])
        cells[-1].append(position)
        previous = key
    interior = [i for cell in cells if len(cell) > 4 for i in cell[1:-1]]
    boundary = [i for cell in cells for i in (cell[:1]+cell[-1:] if len(cell) > 4 else cell)]
    require(interior and boundary, "actual old-H fixture includes eliminated interior")
    principal = [[h[i % 13][j % 13] for j in selected] for i in selected]
    hii = [[principal[i][j] for j in interior] for i in interior]
    hbi = [[principal[i][j] for j in interior] for i in boundary]
    hib = [[principal[i][j] for j in boundary] for i in interior]
    schur = sub([[principal[i][j] for j in boundary] for i in boundary], mul(mul(hbi, inverse(hii)), hib))
    dense = {name: matrix(value) for name, value in observed["dense"].items()}
    require(principal == dense["principal"] and schur == dense["schur"],
            "independent old-H elimination matches actual setup")
    rounded = [[rounding(x) for x in row] for row in schur]
    require(rounded == dense["rounded_schur"], "observed first Schur rounding")
    low, high = dense["lower"], dense["upper"]
    require(mul(low, high) == rounded, "actual exact LU factors the rounded Schur matrix")
    n, width = len(boundary), count(observed["width"])
    low_bank, high_bank = [fixed(raw, width) for raw in observed["banks"]]
    require(len(low_bank) == n*bandwidth and len(high_bank) == n*(bandwidth+1), "actual prepared bank extents")
    lower = [[Q(int(i == j)) for j in range(n)] for i in range(n)]
    upper = [[Q(0) for _ in range(n)] for _ in range(n)]
    reciprocal = [Q(0)]*n
    pos = 0
    for i in range(n):
        for j in range(i-bandwidth, i):
            value = Q(low_bank[pos], scale)
            pos += 1
            require(value == (rounding(low[i][j]) if j >= 0 else 0), "actual lower coefficient")
            if j >= 0:
                lower[i][j] = value
    pos = 0
    for i in reversed(range(n)):
        for j in range(i+1, i+bandwidth+1):
            value = Q(high_bank[pos], scale)
            pos += 1
            require(value == (rounding(high[i][j]) if j < n else 0), "actual upper coefficient")
            if j < n:
                upper[i][j] = value
        reciprocal[i] = Q(high_bank[pos], scale)
        pos += 1
        require(reciprocal[i] == rounding(1/high[i][i]) and reciprocal[i] > 0, "actual pivot reciprocal")
        upper[i][i] = 1/reciprocal[i]
    effective = mul(lower, upper)
    e0, e1 = sub(rounded, schur), sub(effective, rounded)
    require(norm(e0) > 0 and norm(e1) > 0, "two distinct nonzero setup perturbations")

    def solve_model(rhs, early=False):
        forward, result = [Q(0)]*n, [Q(0)]*n
        for i in range(n):
            forward[i] = rounding(rhs[i]-sum((lower[i][j]*forward[j] for j in range(i)), Q(0)))
        for i in reversed(range(n)):
            residual = forward[i]-sum((upper[i][j]*result[j] for j in range(i+1, n)), Q(0))
            result[i] = rounding(reciprocal[i]*(rounding(residual) if early else residual))
        return forward, result

    # Bounded fixture selection only: all candidates use the actual saved banks.
    candidates = [[Q(((7*i+3+5*k) % 19)-9, 16) for i in range(n)] for k in range(64)]
    chosen = next((rhs for rhs in candidates if solve_model(rhs)[1] != solve_model(rhs, True)[1]), None)
    require(chosen is not None, "actual bank witness distinguishes premature upper rounding")
    right_hands = [chosen, [Q(((5*i+1) % 11)-5, 16) for i in range(n)]]
    owner = boundary_module.BandedSolve()
    input_pool, components = ScratchPool(256), []
    input_scope = OuterScope(input_pool)
    raw_trace = []
    saved_truncate = boundary_module.truncate

    def observe_truncate(value, amount):
        before = (value.negative, tape_bytes(value.magnitude.tape), tape_bytes(amount.tape))
        result = saved_truncate(value, amount)
        raw_trace.append((before, result.negative, tape_bytes(result.magnitude.tape)))
        return result

    try:
        with owned(*(Count.literal(v) for v in (n, bandwidth, width, bits))) as args:
            with sealed_constructors(), input_scope.installed():
                tapes = [input_pool.acquire() for _ in range(3)]
                try:
                    for target, raw in zip(tapes[:2], observed["banks"]):
                        for bit in body(raw):
                            target.append(bit)
                        target.rewind()
                    for rhs in right_hands:
                        for item in rhs:
                            integer = int(item*scale)
                            with owned(Signed(Count.literal(abs(integer)), integer < 0)) as (value,):
                                write_signed(value, tapes[2], args[2])
                        tapes[2].rewind()
                        ports = [borrowed_tape(x) for x in tapes]+[borrowed_tape(x.tape) for x in args]
                        borrowed = [(bytes(x.cells), x.head) for x in ports]
                        raw_trace.clear()
                        boundary_module.truncate = observe_truncate
                        products_before = owner.arithmetic.products
                        try:
                            with input_scope.suspended(), no_decode():
                                output = owner.run(*tapes, *args)
                        finally:
                            boundary_module.truncate = saved_truncate
                        require(borrowed == [(bytes(x.cells), x.head) for x in ports], "all source borrowed ports restored")
                        result = [Q(x, scale) for x in fixed(bytes(output.cells), width)]
                        trace = [(((-1 if before[0] else 1)*count(before[1]), count(before[2])),
                                  (-1 if sign else 1)*count(after)) for before, sign, after in raw_trace]
                        require(len(trace) == 2*n and [a[0][1] for a in trace] == [bits]*n+[2*bits]*n,
                                "actual forward/backward truncation schedule")
                        forward = [Q(item[1], scale) for item in trace[:n]]
                        require(result == [Q(item[1], scale) for item in reversed(trace[n:])], "observed backward outputs")
                        expected_y, expected_x = solve_model(rhs)
                        require((forward, result) == (expected_y, expected_x), "independent rational model agrees with actual source")
                        for i in range(n):
                            raw = rhs[i]-sum((lower[i][j]*forward[j] for j in range(i)), Q(0))
                            require(trace[i][0][0] == raw*scale*scale, "actual exact forward dot product")
                            raw = reciprocal[i]*(forward[i]-sum((upper[i][j]*result[j] for j in range(i+1, n)), Q(0)))
                            require(trace[2*n-1-i][0][0] == raw*scale**3, "actual unrounded upper residual times reciprocal")
                        ef, eb = vector_sub(mv(lower, forward), rhs), vector_sub(mv(upper, result), forward)
                        rho = vector_sub(mv(effective, result), rhs)
                        split = [a+b for a, b in zip(ef, mv(lower, eb))]
                        require(rho == split and any(ef) and any(eb), "nonzero computed-state residual identity")
                        require(max(map(abs, ef)) < Q(1, scale)
                                and all(abs(error*qhat) < Q(1, scale) for error, qhat in zip(eb, reciprocal)),
                                "forward and reciprocal-scaled backward truncation bounds")
                        original_residual = vector_sub(mv(schur, result), rhs)
                        complete = [a-b-c for a, b, c in zip(rho, mv(e1, result), mv(e0, result))]
                        require(original_residual == complete, "complete original-Schur residual decomposition")
                        omitted = vector_sub(rho, mv(e1, result))
                        require(original_residual != omitted, "omitting first Schur rounding fails")
                        wrong_upper = [row[:] for row in upper]
                        for i in range(n):
                            wrong_upper[i][i] = rounding(high[i][i])
                        wrong_diagonal = vector_sub(mv(mul(lower, wrong_upper), result), rhs)
                        require(wrong_diagonal != rho, "rounded U diagonal is not the source effective diagonal")
                        ideal = mv(inverse(schur), rhs)
                        error = vector_sub(result, ideal)
                        recovered_error = mv(inverse(effective), vector_sub(rho, mv(sub(effective, schur), ideal)))
                        require(error == recovered_error, "exact original-Schur solution error identity")
                        require(owner.arithmetic.products-products_before == 5*n, "source multiply calls")
                        components.append({"rhs": rhs, "forward": forward, "output": result,
                                           "forward_residual": ef, "backward_residual": eb,
                                           "effective_residual": rho, "original_residual": original_residual,
                                           "first_rounding_contribution": mv(e0, result),
                                           "factor_rounding_contribution": mv(e1, result),
                                           "solution_error": error,
                                           "max_solution_error": max(map(abs, error)),
                                           "early_rounding_output": solve_model(rhs, True)[1],
                                           "early_rounding_rejected": solve_model(rhs, True)[1] != result,
                                           "wrong_diagonal_residual": wrong_diagonal,
                                           "truncate_calls": len(trace), "multiply_calls": 5*n,
                                           "borrowed_restored": True})
                        output.clear()
                        erase_marker(output)
                        owner.idle()
                        require(owner.closed and not owner.pool.live and all(
                            t.head == 1 and all(x == 4 for x in t.cells) for t in owner.pool.tapes),
                            "source solver scratch blank after completed call")
                        borrowed_tape(tapes[2]).clear()
                finally:
                    for tape in tapes:
                        tape.clear()
                    input_pool.empty()
    finally:
        boundary_module.truncate = saved_truncate
    for tape in input_pool.tapes:
        erase_marker(tape)
    require(not input_pool.live and all(t.head == 1 and all(x == 4 for x in t.cells) for t in input_pool.tapes),
            "input carrier cleanup")
    return encode({"fixture": {"s": 13, "t": 14, "u": 1, "w": 1, "P": bits, "p": p,
                               "window": [11, 8, 12, 4], "selected": selected, "cells": cells,
                               "boundary": boundary, "interior": interior, "width": width},
                   "original_schur": schur, "rounded_schur": rounded,
                   "stored_lower": lower, "effective_upper": upper, "stored_reciprocals": reciprocal,
                   "schur_rounding_norm": norm(e0), "factor_rounding_norm": norm(e1),
                   "bank_sha256": [sha256(body(raw)).hexdigest() for raw in observed["banks"]],
                   "compiled_page_sha256": observed["page_sha256"], "components": components,
                   "banks_bound_to_page_suffix": True, "solution_error_identity": True,
                   "observer_only": True, "source_calls": owner.calls, "all_cleanup_checks": True,
                   "production_precision_claim": False})
