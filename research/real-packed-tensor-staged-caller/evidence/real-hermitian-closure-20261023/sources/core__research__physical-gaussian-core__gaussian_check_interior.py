"""Physical factor preparation and both triangular passes against PR489."""
from fractions import Fraction as Q
from hashlib import sha256
import importlib.util
from gaussian_sources import active, require


def dense_solution(matrix, vector):
    rows = [list(row)+[value] for row, value in zip(matrix, vector)]
    for k in range(len(rows)):
        pivot = rows[k][k]
        rows[k] = [v/pivot for v in rows[k]]
        for i in range(len(rows)):
            if i != k:
                factor = rows[i][k]
                rows[i] = [x-factor*y for x, y in zip(rows[i], rows[k])]
    return [row[-1] for row in rows]


def run():
    from cardinal_counts import Count
    from check_support import no_decode
    from gaussian_interior import Interior, InteriorFactors
    from ring_check_words import body, decode
    from ring_words import Signed, read_signed, write_signed
    from router_metadata import owned
    from scratch_pool import ScratchPool
    from session import OuterScope, borrowed_tape, erase_marker, sealed_constructors
    from words import BLANK
    path = active().branchfree_package / "code/branchfree.py"
    spec = importlib.util.spec_from_file_location("gaussian_branchfree_oracle", path)
    reference = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(reference)
    owner = Interior()
    pool = ScratchPool(256)
    scope = OuterScope(pool)
    result = []
    cases = ((Q(1, 8), [Q(1, 2), Q(1, 4), Q(3, 8)], [Q(3, 16), Q(-5, 16), Q(1, 8)], 12),
             (Q(1, 16), [Q(1, 4), Q(1, 2), Q(3, 4)], [Q(-1, 8), Q(7, 16), Q(-3, 16)], 12),
             (Q(1, 4), [Q(1, 2)], [Q(-3, 8)], 8))
    with sealed_constructors(), scope.installed():
        try:
            for q, weights, data, bits in cases:
                factors = None
                weight_tape = data_tape = None
                with owned(Count.literal(len(data)), Count.literal(32), Count.literal(bits),
                           Count.literal(int(q*(1 << bits)))) as (length, width, precision, q_numerator):
                    try:
                        weight_tape, data_tape = pool.acquire(), pool.acquire()
                        for values, tape in ((weights, weight_tape), (data, data_tape)):
                            for value in values:
                                integer = int(value*(1 << bits))
                                with owned(Signed(Count.literal(abs(integer)), integer < 0)) as (number,):
                                    write_signed(number, tape, width)
                            tape.rewind()
                        with no_decode():
                            factors = InteriorFactors(length, width, precision, pool)
                            factors.prepare(q_numerator, weight_tape)
                        before = {name: body(borrowed_tape(tape)) for name, tape in factors.streams.items()}
                        saved_input = body(borrowed_tape(data_tape))
                        products = owner.arithmetic.products
                        convolutions = owner.convolution.calls
                        with scope.suspended(), no_decode():
                            output = owner.run(factors, data_tape)
                        raw = body(output)
                        actual = []
                        for _ in data:
                            with owned(read_signed(output, width)) as (number,):
                                integer = (-1 if number.negative else 1)*decode(number.magnitude)
                                actual.append(Q(integer, 1 << bits))
                        require(output.read() == BLANK, "complete local Gaussian return")
                        table = reference.prepare(q, weights, bits)
                        count = reference.counter()
                        expected = reference.apply(table, data, count)
                        require(actual == expected, "physical interior equals independent PR489 packed evaluator")
                        matrix = [[weights[i]*q**((i-j)**2)/weights[j]
                                   for j in range(len(data))] for i in range(len(data))]
                        exact = dense_solution(matrix, data)
                        error = max(abs(a-b) for a, b in zip(actual, exact))
                        require(error < Q(64, 1 << bits), "finite interior accuracy against dense exact inverse")
                        require(before == {name: body(borrowed_tape(tape)) for name, tape in factors.streams.items()}
                                and saved_input == body(borrowed_tape(data_tape)),
                                "local inverse preserves all prepared factors and input")
                        require(owner.convolution.calls-convolutions == 2
                                and owner.arithmetic.products-products == 5*len(data),
                                "actual two convolutions and five diagonal passes")
                        owner.idle()
                        require(owner.closed and not owner.pool.live, "closed interior owner")
                        require(all(t.head == 1 and all(v == BLANK for v in t.cells)
                                    for t in owner.pool.tapes), "restored interior roles")
                        result.append({"length": len(data), "precision": bits, "q": str(q),
                                       "sha256": sha256(raw).hexdigest(), "error": str(error),
                                       "convolutions": 2, "diagonal_products": 5*len(data),
                                       "pool_peak": owner.pool.peak})
                        output.clear()
                        erase_marker(output)
                    finally:
                        if factors is not None:
                            factors.close()
                        for tape in (weight_tape, data_tape):
                            if tape is not None:
                                tape.clear()
        finally:
            pool.empty()
    for tape in pool.tapes:
        erase_marker(tape)
    return {"packets": result, "producer_pool_peak": pool.peak,
            "reference_head": "8922e3b3f0fd7772b0fb42028eb2532984c3ab42",
            "scope": "complete local factor producer/application; global H and Schur composition remain separate"}
