"""Independent original-offset periodic oracle and certified solve diagnostic.

No canonical matrix/coordinate function is used to produce the oracle.
Classical series/tail/residual arguments are credited in PROOF and NOTICE.
This indexed finite checker has no claimed production cost. Prepared for
@CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from fractions import Fraction as Q
from functools import lru_cache
from independent import pi_box


def need(ok, message):
    if not ok:
        raise ValueError(message)


def nearest(numerator, denominator):
    return (2*numerator+denominator)//(2*denominator)


def quantize_lower(x, bits):
    scale = 1 << bits
    return Q((x*scale).__floor__(), scale)


@lru_cache(None)
def direct_decay(factor, bits=240):
    """Positive full-argument Taylor, directed dyadic terms, then reciprocal.

    This does not use the producer's small-argument reduction/squaring.
    Every term encloses its exact positive term by induction. The remaining
    tail is bounded from the next term and the decreasing ratio. The finite
    checker verifies the final width and has an explicit iteration cap.
    """
    factor = Q(factor)
    need(factor >= 0 and bits >= 32, "independent dyadic exponential domain")
    if factor == 0:
        return Q(1), Q(1)
    if 3*factor >= bits+8:
        return Q(), Q(1, 1 << (3*factor).__floor__())
    work = 4*bits+128
    plo, phi = pi_box(work)
    xlo, xhi = factor*plo, factor*phi
    scale = 1 << work
    tlo = thi = slo = shi = scale
    for n in range(1, 8*(bits+1)+500):
        tlo = (tlo*xlo.numerator)//(n*xlo.denominator)
        numerator, denominator = thi*xhi.numerator, n*xhi.denominator
        thi = (numerator+denominator-1)//denominator
        slo, shi = slo+tlo, shi+thi
        if xhi < n+2:
            tail = Q(thi, scale)*xhi/(n+1)/(1-xhi/(n+2))
            if tail < Q(1, 1 << (bits+20)):
                lo, hi = 1/(Q(shi, scale)+tail), Q(scale, slo)
                need(0 < lo <= hi <= 1 and hi-lo < Q(1, 1 << bits),
                     "independent direct Taylor final enclosure")
                return lo, hi
    raise ValueError("bounded dyadic positive Taylor did not terminate")


def pair_norm(pair):
    return abs(pair[0])+abs(pair[1])


def norm(vector):
    return max(map(pair_norm, vector), default=Q())


def subtract(a, b):
    return [(x[0]-y[0], x[1]-y[1]) for x, y in zip(a, b)]


def apply(rows, vector):
    return [(sum((a*vector[k][0] for k, a in row.items()), Q()),
             sum((a*vector[k][1] for k, a in row.items()), Q())) for row in rows]


def identity_defect_norm(rows):
    return max(sum((abs(a-Q(int(k == i))) for k, a in row.items()), Q())
               + int(i not in row) for i, row in enumerate(rows))


def full_periodic(source_size, target_size, alpha, cutoff=4, bits=240):
    """Sparse lower matrix plus a proved row error for the entire infinite map."""
    need(0 < source_size < target_size < 2*source_size and
         alpha >= 1 and cutoff >= 1 and 2*cutoff < source_size,
         "finite independent periodic domain")
    selected = [nearest(target_size*j, source_size) for j in range(source_size)]
    need(len(set(selected)) == source_size and selected[-1] < target_size,
         "independent original q injection")
    beta = [Q(target_size*j, source_size)-selected[j] for j in range(source_size)]
    rho = Q(target_size, source_size)
    rows = [{k: Q(1)} for k in range(target_size)]
    boxes = [{k: (Q(1), Q(1))} for k in range(target_size)]
    row_widths = [Q() for _ in rows]
    # For |h|>cutoff: f>=alpha²(h²-|h|), pi>3 and exp(1)>2.
    tail = 2*Q(1, 1 << (3*alpha*alpha*cutoff*(cutoff+1))) / (
        1-Q(1, 1 << (6*alpha*alpha*(cutoff+1))))
    terms = 0
    for i, address in enumerate(selected):
        rows[address], boxes[address] = {}, {}
        for h in range(-cutoff, cutoff+1):
            j = (i+h) % source_size
            f = alpha*alpha*((rho*h+beta[i])**2-beta[j]**2)
            need(f >= 0, "independent positive narrow exponent")
            lo, hi = direct_decay(f, bits+20)
            lo = quantize_lower(lo, bits)
            hi = -quantize_lower(-hi, bits)
            column = selected[j]
            rows[address][column] = rows[address].get(column, Q())+lo
            old = boxes[address].get(column, (Q(), Q()))
            boxes[address][column] = old[0]+lo, old[1]+hi
            row_widths[address] += hi-lo
            terms += 1
    # Tail belongs only to selected rows; the hole identity is exact.
    selected_set = set(selected)
    widths = [w+(tail if i in selected_set else 0) for i, w in enumerate(row_widths)]
    rho_lower = identity_defect_norm(rows)
    ideal_rho_upper = rho_lower+max(widths)
    need(ideal_rho_upper < 1, "independent full ideal row contraction")
    return {"selected": selected, "holes": sorted(set(range(target_size))-selected_set),
            "betas": beta, "rows": rows, "boxes": boxes, "row_errors": widths,
            "tail": tail, "rho_upper": ideal_rho_upper, "terms": terms,
            "cutoff": cutoff, "bits": bits}


def rounded_neumann(rows, vector, bits=240, steps=128):
    """Fixed-grid recurrence; correctness certified by its final residual."""
    need(steps >= 1 and identity_defect_norm(rows) < 1,
         "bounded independent solve diagnostic")
    scale = 1 << bits
    def trunc(x):
        k = abs(x.numerator)*scale//x.denominator
        return Q(-k if x < 0 else k, scale)
    state = [tuple(x) for x in vector]
    total = [(Q(), Q()) for _ in vector]
    for _ in range(steps):
        total = [(x[0]+y[0], x[1]+y[1]) for x, y in zip(total, state)]
        product = apply(rows, state)
        state = [(trunc(x[0]-y[0]), trunc(x[1]-y[1])) for x, y in zip(state, product)]
    return total


def inverse_receipt(rows, vector, solution, row_error=Q()):
    """Rows approximate the ideal matrix in infinity norm by row_error."""
    rho = identity_defect_norm(rows)+row_error
    need(rho < 1, "independent residual inverse admission")
    residual = norm(subtract(vector, apply(rows, solution)))+row_error*norm(solution)
    return {"rho": rho, "residual": residual, "inverse_error": residual/(1-rho)}
