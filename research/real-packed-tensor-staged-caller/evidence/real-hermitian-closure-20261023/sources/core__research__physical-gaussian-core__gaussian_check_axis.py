"""Global producer checks against exact geometry and separate Gaussian intervals."""
from fractions import Fraction as Q
from hashlib import sha256
from gaussian_sources import require
from gaussian_check_exponentials import oracle


def run():
    from cardinal_counts import Count
    from check_support import no_decode
    from gaussian_axis import Axis
    from ring_check_words import decode
    from router_metadata import owned
    from scratch_pool import ScratchPool
    from session import OuterScope, borrowed_tape, erase_marker, sealed_constructors
    from words import BLANK
    pool = ScratchPool(512)
    scope = OuterScope(pool)
    s, t, u, w, bits = 8, 9, 1, 1, 16
    with owned(*(Count.literal(v) for v in (s, t, u, w, bits))) as parameters:
        saved = tuple((bytes(v.tape.cells), v.tape.head) for v in parameters)
        with sealed_constructors(), scope.installed():
            axis = None
            try:
                with no_decode():
                    axis = Axis(*parameters, pool)
                def number(value):
                    return Q((-1 if value.numerator.negative else 1)*decode(value.numerator.magnitude),
                             decode(value.denominator))
                def get(matrix, row, column):
                    with owned(Count.literal(row), Count.literal(column)) as (i, j):
                        with owned(matrix.get(i, j)) as (value,):
                            return number(value)
                rho, theta, eta = Q(t, s), Q(t-s, s), Q(1, 1 << bits)
                weights = [[get(axis.weights, i, j) for j in range(5)] for i in range(s)]
                kernel = [get(axis.kernel, i, 0) for i in range(w+1)]
                actual = [[get(axis.matrix, i, j) for j in range(s)] for i in range(s)]
                intervals = same_cell = cross_cell = 0
                for i in range(s):
                    a, beta, phase, diagonal, nearest = weights[i]
                    q = (rho*i+Q(1, 2)).__floor__()
                    require((beta, phase, nearest) == (rho*i-q, q-i, q),
                            "encoded global nearest phase including half-integer tie")
                    f = u*(Q(1, 4)-beta*beta)/theta
                    lo, hi = oracle(f)
                    require(0 < a <= lo <= hi and hi-a < 4*eta,
                            "global similarity weight has certified downward error")
                    lo, hi = oracle(u*beta*beta, True, 2*u)
                    require(0 <= diagonal <= lo <= hi and hi-diagonal < 4*eta,
                            "global normalized positive diagonal has certified error")
                    intervals += 2
                require(kernel[0] == 1, "exact global kernel diagonal")
                for distance in range(1, w+1):
                    lo, hi = oracle(u*rho*distance*distance)
                    require(0 <= kernel[distance] <= lo <= hi and hi-kernel[distance] < 4*eta,
                            "one global truncated Toeplitz kernel")
                    intervals += 1
                for i in range(s):
                    for j in range(s):
                        if i == j:
                            require(actual[i][j] == 1, "exact global H diagonal")
                            continue
                        delta = j-i
                        if abs(delta) > s//2:
                            delta += -s if delta > 0 else s
                        if abs(delta) > w:
                            require(actual[i][j] == 0, "exact global Gaussian band truncation")
                        elif abs(j-i) <= w and weights[i][2] == weights[j][2]:
                            require(actual[i][j] == weights[i][0]*kernel[abs(delta)]/weights[j][0],
                                    "exact rational within-cell similarity")
                            same_cell += 1
                        else:
                            exponent = u*((rho*delta+weights[i][1])**2-weights[j][1]**2)
                            lo, hi = oracle(exponent)
                            require(0 <= actual[i][j] <= lo <= hi and hi-actual[i][j] < 4*eta,
                                    "directed cross-cell coefficient including physical seam")
                            cross_cell += 1
                gap = min(1-sum(actual[i][j] for j in range(s) if i != j) for i in range(s))
                require(gap > 0 and same_cell and cross_cell, "nontrivial globally dominant Gaussian H")
                require(weights[4][1] == Q(-1, 2), "actual nearest-index tie control")
                tape = borrowed_tape(axis.matrix.current)
                digest = sha256(bytes(tape.cells)).hexdigest()
                calls = axis.exponentials.calls
                reflected = axis.reflected_weights
                require(reflected == (s-1)//2 and calls == 2*(s-reflected)+w+cross_cell,
                        "reflected global coefficients reuse the same encoded argument")
                require(saved == tuple((bytes(v.tape.cells), v.tape.head) for v in parameters),
                        "global producer preserves borrowed axis parameters")
            finally:
                if axis is not None:
                    axis.close()
                pool.empty()
    for tape in pool.tapes:
        erase_marker(tape)
        require(tape.head == 1 and all(v == BLANK for v in tape.cells), "global producer restoration")
    return {"s": s, "t": t, "u": u, "w": w, "precision": bits,
            "interval_checks": intervals, "same_cell_entries": same_cell,
            "cross_cell_entries": cross_cell, "row_gap": str(gap),
            "matrix_storage_sha256": digest, "exponential_calls": calls,
            "reflected_weight_pairs": reflected, "pool_peak": pool.peak,
            "scope": "complete encoded global H producer at finite precision; the production asymptotic parameters remain separate"}
