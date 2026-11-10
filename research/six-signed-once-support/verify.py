#!/usr/bin/env python3
"""Checks for six once-each signed frames and the equation F1+...+F6 = 4I.

PROOF.md is the argument. This program checks the determinant identities,
the support witness, the character reduction on the trace-2 splitting of
2I, the two exceptional orbit eliminations, and the degree-1 certificate
census of every other subset system. Python -O is safe: nothing here
depends on assert.
"""

from fractions import Fraction
from itertools import combinations, permutations


TARGETS = ((Fraction(1), Fraction(0), Fraction(1)),
           (Fraction(2), Fraction(1), Fraction(-1)),
           (Fraction(0), Fraction(1), Fraction(1)),
           (Fraction(1), Fraction(2), Fraction(-1)))
TOTAL = (Fraction(4), Fraction(4), Fraction(0))
TWO_I = (Fraction(2), Fraction(2), Fraction(0))
OLD = (
    (Fraction(1), Fraction(0), Fraction(0)),
    (Fraction(0), Fraction(1), Fraction(0)),
    (Fraction(0), Fraction(0), Fraction(1)),
    (Fraction(1), Fraction(1), Fraction(-1)),
)
CYCLE = (3, 5, 10, 12)
TRIPLE = (7, 11, 21, 25)
ZERO3 = (0, 0, 0)


def require(condition, message):
    if not condition:
        raise SystemExit("FAIL: " + message)


def add(left, right, scale=1):
    return tuple(left[i] + scale * right[i] for i in range(3))


def quad(frame):
    a, b, c = frame
    return 2 * a * b + c * (a + b)


def trace(frame):
    return frame[0] + frame[1] + frame[2]


def det(frame):
    a, b, c = frame
    return a * b + c * (a + b) / 2


def mask_list():
    masks = []
    for weight in (2, 3, 4):
        for columns in combinations(range(6), weight):
            mask = 0
            for column in columns:
                mask |= 1 << column
            masks.append(mask)
    return masks


def poly_add(left, right, scale=1):
    out = dict(left)
    for key, value in right.items():
        total = out.get(key, 0) + scale * value
        if total:
            out[key] = total
        elif key in out:
            del out[key]
    return out


def poly_mul(left, right):
    out = {}
    for exp_l, coef_l in left.items():
        for exp_r, coef_r in right.items():
            key = tuple(i + j for i, j in zip(exp_l, exp_r))
            out[key] = out.get(key, 0) + coef_l * coef_r
    return {key: value for key, value in out.items() if value}


def poly_scale(poly, factor):
    return {key: value * factor for key, value in poly.items() if value * factor}


def mono(coef, *exp):
    if coef == 0:
        return {}
    return {tuple(exp): Fraction(coef)}


def univariate(poly, index):
    """View a bivariate polynomial as a polynomial in one variable.

    The coefficient of each power is a univariate polynomial in the other
    variable, with integer exponents.
    """
    out = {}
    for exp, coef in poly.items():
        power = exp[index]
        rest = exp[1 - index]
        bucket = out.setdefault(power, {})
        bucket[rest] = bucket.get(rest, 0) + coef
    return {power: {key: value for key, value in coefs.items() if value}
            for power, coefs in out.items()}


# --- inherited determinant facts and the size cut -------------------------------


def check_determinants():
    for target in TARGETS:
        require(trace(target) == 2, "target trace")
        require(det(target) == Fraction(1, 2), "target determinant")
        require(quad(target) == 1, "target quad")
        complement = add(TOTAL, target, -1)
        require(det(complement) == Fraction(17, 2), "five-frame complement determinant")
    require(trace(TOTAL) == 8, "total trace")
    require(det(TOTAL) == 16, "total determinant")
    require(quad(TOTAL) == 32, "total quad")
    require(det((0, 0, 0)) == 0 and quad((0, 0, 0)) == 0, "zero frame")
    require(quad((1, 1, 0)) != 0, "I is not rank one")
    # Q(2-a,2-b,-c) = 8 - 4(a+b+c) + Q(a,b,c) as polynomials.
    a, b, c = mono(1, 1, 0, 0), mono(1, 0, 1, 0), mono(1, 0, 0, 1)
    one = mono(1, 0, 0, 0)
    q_g = poly_add(poly_scale(poly_mul(a, b), 2), poly_mul(c, poly_add(a, b)))
    left = poly_add(
        poly_scale(poly_mul(poly_add(poly_scale(one, 2), a, -1), poly_add(poly_scale(one, 2), b, -1)), 2),
        poly_mul(poly_scale(c, -1), poly_add(poly_add(poly_scale(one, 2), a, -1), poly_add(poly_scale(one, 2), b, -1))),
    )
    right = poly_add(poly_add(mono(8, 0, 0, 0), poly_scale(poly_add(poly_add(a, b), c), -4)), q_g)
    require(left == right, "padding quad identity")
    # Q(a+2,b+2,c) = Q(a,b,c) + 4(a+b+c) + 8.
    lifted = poly_add(
        poly_scale(poly_mul(poly_add(a, poly_scale(one, 2)), poly_add(b, poly_scale(one, 2))), 2),
        poly_mul(c, poly_add(poly_add(a, b), poly_scale(one, 4))),
    )
    expected = poly_add(poly_add(q_g, poly_scale(poly_add(poly_add(a, b), c), 4)), mono(8, 0, 0, 0))
    require(lifted == expected, "common-frame quad identity")


def check_witness():
    frames = (
        (Fraction(1), Fraction(0), Fraction(0)),
        (Fraction(0), Fraction(0), Fraction(1)),
        (Fraction(0), Fraction(1), Fraction(0)),
        (Fraction(1), Fraction(1), Fraction(-1)),
        (Fraction(2), Fraction(0), Fraction(0)),
        (Fraction(0), Fraction(2), Fraction(0)),
    )
    require(all(quad(frame) == 0 and frame != (0, 0, 0) for frame in frames), "witness rank one")
    require(add(add(add(frames[0], frames[1]), add(frames[2], frames[3])),
                add(frames[4], frames[5])) == TOTAL, "witness sum")
    pairs = {
        add(frames[0], frames[1]): TARGETS[0],
        add(frames[0], frames[3]): TARGETS[1],
        add(frames[2], frames[1]): TARGETS[2],
        add(frames[2], frames[3]): TARGETS[3],
    }
    require(set(pairs.values()) == set(TARGETS), "witness support")
    odd_ab = sum((frame[0] + frame[1]) % 2 for frame in frames)
    odd_c = sum(frame[2] % 2 for frame in frames)
    require(odd_ab == 2 and odd_c == 2, "witness character counts")
    tampered = list(frames)
    tampered[4] = (Fraction(3), Fraction(0), Fraction(0))
    require(add(add(add(tampered[0], tampered[1]), add(tampered[2], tampered[3])),
                add(tampered[4], tampered[5])) != TOTAL, "tampered witness")
    twin = (
        frames[0], frames[2], frames[1], frames[3],
        (Fraction(0), Fraction(0), Fraction(2)),
        (Fraction(2), Fraction(2), Fraction(-2)),
    )
    require(all(quad(frame) == 0 for frame in twin), "twin rank one")
    acc = (0, 0, 0)
    for frame in twin:
        acc = add(acc, frame)
    require(acc == TOTAL, "twin sum")


# --- character reduction for every rational trace-2 splitting ------------------


def check_character_family():
    """Every rational rank-one splitting of 2I is killed by chi_AB."""
    # Parametrization of s^2 + u^2 = 4, s = p - 2, from the point s = -2.
    # v = r/t gives the cleared coefficient vector below. The point s = -2
    # is 2P and is checked directly; s = 2 is v = 0.
    samples = ((1, 1), (1, 2), (2, 1), (3, 2), (1, 4), (5, 2))
    for r, t in samples:
        d = r * r + t * t
        coef = (2 * t * (t + r), 2 * t * (t - r), 2 * (r * r - t * t))
        frame = tuple(Fraction(value, d) for value in coef)
        require(trace(frame) == 2 and quad(frame) == 0, "chart point")
        other = add(TWO_I, frame, -1)
        require(quad(other) == 0 and trace(other) == 2, "chart complement")
        if d % 2 == 1:
            require(all(value % 2 == 0 for value in coef), "odd denominator clearing")
        else:
            half = d // 2
            require(half % 2 == 1, "half denominator stays odd")
            scaled = tuple(value // 2 for value in coef)  # coef is divisible by 4? check half*frame
            # (d/2) * frame = coef / 2
            require(all(value % 2 == 0 for value in scaled), "even-denominator clearing")
    two_p = (Fraction(0), Fraction(0), Fraction(2))
    two_q = (Fraction(2), Fraction(2), Fraction(-2))
    require(quad(two_p) == 0 and quad(two_q) == 0, "poles")
    require(all(value % 2 == 0 for value in two_p + two_q), "poles are even")
    # On {A,B,P,Q}, chi_AB detects A and B only. All four targets have odd a+b.
    chi_ab = lambda frame: (frame[0] + frame[1]) % 2
    old_hits = sum(chi_ab(frame) for frame in OLD)
    target_hits = sum(chi_ab(frame) for frame in TARGETS)
    require(old_hits == 2 and target_hits == 4, "chi_AB counts")
    # A character with chi(A) = chi(B) != chi(P) detects exactly one of the
    # two pairs {A,B} and {P,Q}, because Q = A+B-P.
    for chi_a, chi_p in ((1, 0), (0, 1)):
        chi_b = chi_a
        chi_q = (chi_a + chi_b + chi_p) % 2
        require(chi_q == chi_p, "Q follows A+B-P")
        detected = chi_a + chi_b + chi_p + chi_q
        require(detected == 2, "exactly two old frames")
        for target, expected_parts in (
            (TARGETS[0], (chi_a, chi_p)),
            (TARGETS[1], (chi_a, chi_q)),
            (TARGETS[2], (chi_b, chi_p)),
            (TARGETS[3], (chi_b, chi_q)),
        ):
            require((expected_parts[0] + expected_parts[1]) % 2 == 1, "target detected")
            require(chi_ab(target) == 1, "chi_AB detects every target")


def sigma(frame):
    a, b, c = frame
    return (b, a, c)


def tau(frame):
    a, b, c = frame
    return (a + c, b + c, -c)


def check_automorphisms():
    for frame in list(OLD) + list(TARGETS) + [TOTAL, TWO_I, (Fraction(3), Fraction(-2), Fraction(5))]:
        require(quad(sigma(frame)) == quad(frame), "sigma preserves quad")
        require(quad(tau(frame)) == quad(frame), "tau preserves quad")
        require(sigma(sigma(frame)) == frame and tau(tau(frame)) == frame, "involutions")
    require(sigma(TOTAL) == TOTAL and tau(TOTAL) == TOTAL, "total fixed")
    require(tuple(sorted(sigma(t) for t in TARGETS)) == tuple(sorted(TARGETS)), "sigma permutes targets")
    require(tuple(sorted(tau(t) for t in TARGETS)) == tuple(sorted(TARGETS)), "tau permutes targets")


# --- incidence linear algebra ---------------------------------------------------


def rref_incidence(masks, rhs_rows):
    width = 9
    matrix = []
    for row, mask in enumerate(masks):
        matrix.append([Fraction((mask >> col) & 1) for col in range(6)]
                      + [Fraction(value) for value in rhs_rows[row]])
    matrix.append([Fraction(1)] * 6 + [Fraction(value) for value in rhs_rows[4]])
    rank = 0
    pivot_of = {}
    for col in range(6):
        pivot = None
        for row in range(rank, 5):
            if matrix[row][col]:
                pivot = row
                break
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        pivot_value = matrix[rank][col]
        for entry in range(col, width):
            matrix[rank][entry] /= pivot_value
        for row in range(5):
            if row == rank or not matrix[row][col]:
                continue
            factor = matrix[row][col]
            for entry in range(col, width):
                matrix[row][entry] -= factor * matrix[rank][entry]
        pivot_of[col] = rank
        rank += 1
    for row in range(rank, 5):
        if any(matrix[row][6:]):
            return False, None, None
    particular = [[Fraction(0), Fraction(0), Fraction(0)] for _ in range(6)]
    for col, row in pivot_of.items():
        for coord in range(3):
            particular[col][coord] = matrix[row][6 + coord]
    kernel = []
    for col in range(6):
        if col in pivot_of:
            continue
        vector = [Fraction(0)] * 6
        vector[col] = Fraction(1)
        for pivot, row in pivot_of.items():
            vector[pivot] = -matrix[row][col]
        kernel.append(vector)
    return True, particular, kernel


def monomials(nvars, degree):
    found = []

    def walk(remaining, start, acc):
        if start == nvars:
            if remaining == 0:
                found.append(tuple(acc))
            return
        for exponent in range(remaining + 1):
            acc.append(exponent)
            walk(remaining - exponent, start + 1, acc)
            acc.pop()

    for total in range(degree + 1):
        walk(total, 0, [])
    return found


def frame_polynomials(particular, kernel, column, nvars):
    coords = []
    for coord in range(3):
        poly = {tuple(0 for _ in range(nvars)): particular[column][coord]}
        for k, vector in enumerate(kernel):
            coef = vector[column]
            if coef:
                exponent = [0] * nvars
                exponent[3 * k + coord] = 1
                poly[tuple(exponent)] = poly.get(tuple(exponent), 0) + coef
        coords.append({key: value for key, value in poly.items() if value})
    return coords


def quad_polynomial(coords):
    a, b, c = coords
    return poly_add(poly_scale(poly_mul(a, b), 2), poly_mul(c, poly_add(a, b)))


def solve_linear(columns, rhs):
    """Exact solve of columns * x = rhs. Returns a solution or None."""
    rows = len(rhs)
    cols = len(columns)
    matrix = [[columns[col][row] for col in range(cols)] + [rhs[row]] for row in range(rows)]
    rank = 0
    pivot_at = [-1] * cols
    for col in range(cols):
        pivot = None
        for row in range(rank, rows):
            if matrix[row][col]:
                pivot = row
                break
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        pivot_value = matrix[rank][col]
        for entry in range(col, cols + 1):
            matrix[rank][entry] /= pivot_value
        for row in range(rows):
            if row == rank or not matrix[row][col]:
                continue
            factor = matrix[row][col]
            for entry in range(col, cols + 1):
                matrix[row][entry] -= factor * matrix[rank][entry]
        pivot_at[col] = rank
        rank += 1
    for row in range(rank, rows):
        if matrix[row][cols]:
            return None
    solution = [Fraction(0)] * cols
    for col, row in enumerate(pivot_at):
        if row >= 0:
            solution[col] = matrix[row][cols]
    return solution


def certificate_of_one(polys, nvars):
    monoms = monomials(nvars, 3)
    require(monoms[0] == tuple(0 for _ in range(nvars)), "constant monomial first")
    index = {exp: position for position, exp in enumerate(monoms)}
    multipliers = monomials(nvars, 1)
    columns = []
    for poly in polys:
        for multiplier in multipliers:
            acc = [Fraction(0)] * len(monoms)
            for exp, coef in poly.items():
                key = tuple(i + j for i, j in zip(exp, multiplier))
                acc[index[key]] += coef
            columns.append(acc)
    rhs = [Fraction(0)] * len(monoms)
    rhs[0] = Fraction(1)
    solution = solve_linear(columns, rhs)
    if solution is None:
        return None
    return solution, multipliers


def expansion_is_one(polys, multipliers, solution, nvars):
    total = {}
    width = len(multipliers)
    for index, poly in enumerate(polys):
        multiplier = {}
        for offset, exp in enumerate(multipliers):
            coef = solution[index * width + offset]
            if coef:
                multiplier[exp] = coef
        total = poly_add(total, poly_mul(multiplier, poly))
    one = {tuple(0 for _ in range(nvars)): Fraction(1)}
    return total == one


def certify_linear(polys, nvars, target):
    monoms = monomials(nvars, 3)
    index = {exp: position for position, exp in enumerate(monoms)}
    multipliers = monomials(nvars, 1)
    columns = []
    for poly in polys:
        for multiplier in multipliers:
            acc = [Fraction(0)] * len(monoms)
            for exp, coef in poly.items():
                key = tuple(i + j for i, j in zip(exp, multiplier))
                acc[index[key]] += coef
            columns.append(acc)
    rhs = [Fraction(0)] * len(monoms)
    for exp, coef in target.items():
        rhs[index[exp]] += coef
    solution = solve_linear(columns, rhs)
    if solution is None:
        return False
    total = {}
    width = len(multipliers)
    for index_poly, poly in enumerate(polys):
        multiplier = {}
        for offset, exp in enumerate(multipliers):
            coef = solution[index_poly * width + offset]
            if coef:
                multiplier[exp] = coef
        total = poly_add(total, poly_mul(multiplier, poly))
    return total == target


# --- exceptional orbit: the 4-cycle --------------------------------------------


def check_cycle():
    consistent = []
    for perm in permutations(range(4)):
        rhs = [TARGETS[perm[i]] for i in range(4)] + [TOTAL]
        ok, particular, kernel = rref_incidence(CYCLE, rhs)
        if not ok:
            continue
        consistent.append(perm)
        require(len(kernel) == 2, "cycle nullity")
        used = [vec for vec in kernel if any(vec[j] for j in range(4))]
        padding = [vec for vec in kernel if any(vec[j] for j in (4, 5))]
        require(len(used) == 1 and len(padding) == 1, "cycle kernel split")
        vec = used[0]
        hits = []
        for candidate in OLD:
            frames = [tuple(particular[j][coord] + vec[j] * candidate[coord] for coord in range(3))
                      for j in range(4)]
            if set(frames) == set(OLD) and all(quad(frame) == 0 for frame in frames):
                hits.append(candidate)
        require(len(hits) == 1, "one old quadruple")
        polys = [quad_polynomial(frame_polynomials(particular, used, j, 3)) for j in range(4)]
        for coord, value in enumerate(hits[0]):
            exponent = [0, 0, 0]
            exponent[coord] = 1
            target = {tuple(exponent): Fraction(1)}
            if value:
                target[ZERO3] = Fraction(-value)
            require(certify_linear(polys, 3, target), "used-frame uniqueness")
        pad = padding[0]
        total_pad = [particular[4][coord] + particular[5][coord] for coord in range(3)]
        require(tuple(total_pad) == TWO_I, "padding sums to 2I")
        require(pad[4] + pad[5] == 0, "padding kernel cancels")
        require(all(pad[j] == 0 for j in range(4)), "padding kernel misses the cycle")
    require(len(consistent) == 8, "eight cycle assignments")


# --- exceptional orbit: four triples through one frame -------------------------


def eliminant_ab():
    """Cleared trace equations for masks (7,11,21,25) and targets AP,AQ,BP,BQ.

    Returns the determinant of the two linear-in-p coefficient pairs.
    """
    # Variables (p, y). z = -2y(y+1)/(2y+1), c = -2-p, x = y+1.
    p = mono(1, 1, 0)
    y = mono(1, 0, 1)
    one = mono(1, 0, 0)
    den = poly_add(poly_scale(y, 2), one)
    znum = poly_scale(poly_mul(y, poly_add(y, one)), -2)
    left = poly_add(poly_mul(p, poly_add(p, mono(2, 0, 0))), poly_scale(poly_mul(y, p), 2))
    left = poly_add(left, poly_scale(poly_mul(y, y), 2))
    factor = poly_add(poly_mul(poly_add(mono(3, 0, 0), p), den), znum, -1)
    eq2 = poly_add(poly_mul(den, left), poly_mul(factor, poly_add(p, poly_scale(y, 2))), -1)
    one_y = poly_add(one, y, -1)
    two_ab = poly_add(poly_add(poly_scale(poly_mul(one_y, one_y), 2),
                               poly_scale(poly_mul(one_y, p), -2)),
                      poly_mul(p, poly_add(p, mono(2, 0, 0))))
    ab_sum = poly_add(poly_add(mono(2, 0, 0), poly_scale(y, -2)), p, -1)
    cf = poly_add(poly_mul(poly_add(one, p), den), znum, -1)
    eq3 = poly_add(poly_mul(den, two_ab), poly_mul(cf, ab_sum))

    def split(poly):
        high, low = {}, {}
        for (ep, ey), coef in poly.items():
            bucket = high if ep else low
            bucket[ey] = bucket.get(ey, 0) + coef
            if ep not in (0, 1):
                raise SystemExit("FAIL: eliminant was not linear in p")
        return high, low

    a2, b2 = split(eq2)
    a3, b3 = split(eq3)

    def mul1(left, right):
        out = {}
        for i, u in left.items():
            for j, v in right.items():
                out[i + j] = out.get(i + j, 0) + u * v
        return out

    det_poly = poly_add(mul1(a2, b3), mul1(b2, a3), -1)
    # a = b = 0, y = 1 is on the trace -2 circle. den*Q(F2) = -20.
    value = 0
    for (ep, ey), coef in eq2.items():
        if ep == 0:
            value += coef
    require(value == -20, "AB equation matches the frame at (a,b,y)=(0,0,1)")
    return {exp: coef for exp, coef in det_poly.items() if coef}


def check_positive_f(det_poly):
    # det = -4 f, f(y) = 2(y^2-y)^2 + 4y + 1.
    f = {4: Fraction(2), 3: Fraction(-4), 2: Fraction(2), 1: Fraction(4), 0: Fraction(1)}
    require(det_poly == {exp: -4 * coef for exp, coef in f.items()}, "eliminant equals -4f")
    # f(-t) = k(t) = 2t^4 + 4t^3 + 2t^2 - 4t + 1.
    k = {4: Fraction(2), 3: Fraction(4), 2: Fraction(2), 1: Fraction(-4), 0: Fraction(1)}
    flipped = {}
    for exp, coef in f.items():
        flipped[exp] = flipped.get(exp, 0) + coef * ((-1) ** exp)
    require(flipped == k, "f(-t) = k(t)")
    m = {3: Fraction(2), 2: Fraction(3), 1: Fraction(1), 0: Fraction(-1)}
    remainder = {2: Fraction(-1, 2), 1: Fraction(-7, 2), 0: Fraction(3, 2)}
    quotient = {1: Fraction(1), 0: Fraction(1, 2)}
    product = {}
    for e, coef in quotient.items():
        for fexp, fcoef in m.items():
            product[e + fexp] = product.get(e + fexp, 0) + coef * fcoef
    for exp, coef in remainder.items():
        product[exp] = product.get(exp, 0) + coef
    require(product == k, "k = (t+1/2) m + remainder")
    # m' = 6t^2+6t+1 has negative roots: sum -1, product 1/6, discriminant 12.
    require(36 - 24 == 12, "discriminant")
    # On [0, infinity) m' >= 1, so m has one nonnegative root.
    require(m[0] + m[1] * Fraction(1, 3) + m[2] * Fraction(1, 9) + m[3] * Fraction(1, 27) < 0,
            "m(1/3) < 0")
    require(sum(coef * Fraction(2, 5) ** exp for exp, coef in m.items()) > 0, "m(2/5) > 0")
    # remainder (1/2)(3-7t-t^2) is decreasing for t >= 0 and positive at 2/5.
    at_two_fifths = sum(coef * Fraction(2, 5) ** exp for exp, coef in remainder.items())
    require(at_two_fifths == Fraction(1, 50), "remainder at the bracket end")
    for value in (0, 1, 2, Fraction(1, 2)):
        require(sum(coef * value ** exp for exp, coef in f.items()) > 0, "f positive on samples")


def check_ab_obstruction():
    # Q(F4) - Q(W) = 2(x-y-1) when Delta = (-1, 1, 0).
    # W = (x,y,z), F4 = (x-1, y+1, z).
    samples = []
    for xv in (-2, -1, 0, 1, 2):
        for yv in (-2, -1, 0, 1, 2):
            for zv in (-1, 0, 1):
                q_w = quad((xv, yv, zv))
                q_4 = quad((xv - 1, yv + 1, zv))
                require(q_4 - q_w == 2 * (xv - yv - 1), "AB difference")
                samples.append(q_4 - q_w)
    require(len(samples) == 75, "AB grid")
    # y = -1/2 makes the cone equation -1/2.
    require(quad((Fraction(1, 2), Fraction(-1, 2), 0)) == Fraction(-1, 2), "forbidden cone point")
    det_poly = eliminant_ab()
    check_positive_f(det_poly)
    # The cleared equations are den times the real quadrics, and den = 2y+1
    # vanishes only at the forbidden point. A never-zero eliminant leaves
    # no common p.


def qp_polynomials():
    """Cleared quadrics of the two frames that remain after z = 1 and the chart.

    Coordinates are numerators over Delta = D*(2x+1). The returned polynomials
    equal Delta^2 times the quadrics, so they vanish exactly where the quadrics
    do whenever Delta is nonzero.
    """
    x = mono(1, 1, 0)
    v = mono(1, 0, 1)
    one = mono(1, 0, 0)
    d = poly_add(one, poly_mul(v, v))
    den = poly_add(poly_scale(x, 2), one)
    delta = poly_mul(d, den)
    ynum = poly_scale(x, -1)
    anum = poly_scale(poly_add(one, v), -2)
    bnum = poly_mul(poly_scale(v, -2), poly_add(one, v))
    cnum = poly_add(poly_add(poly_scale(d, -2), anum, -1), bnum, -1)
    f0 = (
        poly_mul(anum, den),
        poly_mul(bnum, den),
        poly_mul(cnum, den),
    )
    w = (
        poly_mul(x, delta),
        poly_mul(ynum, d),
        delta,
    )

    def sub_frame(target):
        coords = []
        for coord in range(3):
            piece = poly_scale(delta, target[coord])
            piece = poly_add(piece, f0[coord], -1)
            piece = poly_add(piece, w[coord], -1)
            coords.append(piece)
        return coords

    def cleared_quad(coords):
        a, b, c = coords
        return poly_add(poly_scale(poly_mul(a, b), 2), poly_mul(c, poly_add(a, b)))

    ap = (1, 0, 1)
    bp = (0, 1, 1)
    return cleared_quad(sub_frame(ap)), cleared_quad(sub_frame(bp)), den


def divide_by_linear(parts):
    """Divide a polynomial in x, coefficients in the other variable, by 2x+1."""
    quotient = {}
    remainder = {power: dict(coef) for power, coef in parts.items()}
    while remainder and max(remainder) >= 1:
        degree = max(remainder)
        lead = remainder.pop(degree)
        qcoef = {key: value / 2 for key, value in lead.items()}
        quotient[degree - 1] = qcoef
        dest = remainder.setdefault(degree - 1, {})
        for key, value in qcoef.items():
            dest[key] = dest.get(key, 0) - value
            if dest[key] == 0:
                del dest[key]
        if not dest:
            del remainder[degree - 1]
    return quotient, remainder


def euclid_positive(left, right):
    def degree(poly):
        return max(poly) if poly else -1

    def lead(poly):
        return poly[degree(poly)]

    def scale(poly, factor):
        out = {}
        for power, coef in poly.items():
            scaled = {}
            for exp, value in coef.items():
                total = value * factor if not isinstance(factor, dict) else None
                if total is None:
                    # factor is a univariate polynomial
                    pass
            out[power] = scaled
        return out

    def mul_coef(coef, other):
        if not isinstance(other, dict):
            return {exp: value * other for exp, value in coef.items()}
        out = {}
        for e1, v1 in coef.items():
            for e2, v2 in other.items():
                out[e1 + e2] = out.get(e1 + e2, 0) + v1 * v2
        return {exp: value for exp, value in out.items() if value}

    def combine(first, second, first_lead, second_lead, shift):
        out = {}
        for power, coef in first.items():
            out[power] = mul_coef(coef, second_lead)
        for power, coef in second.items():
            dest = out.setdefault(power + shift, {})
            sub = mul_coef(coef, first_lead)
            for exp, value in sub.items():
                dest[exp] = dest.get(exp, 0) - value
                if dest[exp] == 0:
                    del dest[exp]
            if not dest:
                del out[power + shift]
        return out

    a, b = left, right
    while b:
        if degree(b) > degree(a):
            a, b = b, a
        shift = degree(a) - degree(b)
        a = combine(a, b, lead(a), lead(b), shift)
        a, b = b, a
    require(degree(a) == 0, "Euclid remainder is a polynomial in v")
    remainder = a[0]
    require(all(coef > 0 for coef in remainder.values()), "positive remainder")
    require(0 in remainder and all(exp % 2 == 0 for exp in remainder), "even powers")
    return remainder


def multiply_uni(left, right):
    out = {}
    for i, u in left.items():
        for j, v in right.items():
            out[i + j] = out.get(i + j, 0) + u * v
    return {exp: coef for exp, coef in out.items() if coef}


def reduce_circle(poly):
    """Reduce a polynomial in (s, t) by t^2 = 2 - s^2."""
    changed = True
    while changed:
        changed = False
        reduced = {}
        for (s_exp, t_exp), coef in poly.items():
            if t_exp >= 2:
                reduced[(s_exp, t_exp - 2)] = reduced.get((s_exp, t_exp - 2), 0) + 2 * coef
                reduced[(s_exp + 2, t_exp - 2)] = reduced.get((s_exp + 2, t_exp - 2), 0) - coef
                changed = True
            else:
                reduced[(s_exp, t_exp)] = reduced.get((s_exp, t_exp), 0) + coef
        poly = {key: value for key, value in reduced.items() if value}
    return poly


def check_chart_completeness():
    """The slope from (s,t)=(1,-1) recovers every other circle point."""
    def mul(left, right):
        out = {}
        for (s1, t1), u in left.items():
            for (s2, t2), v in right.items():
                key = (s1 + s2, t1 + t2)
                out[key] = out.get(key, 0) + u * v
        return {key: value for key, value in out.items() if value}

    def add(left, right, scale=1):
        out = dict(left)
        for key, value in right.items():
            total = out.get(key, 0) + scale * value
            if total:
                out[key] = total
            elif key in out:
                del out[key]
        return out

    s, t, one = {(1, 0): Fraction(1)}, {(0, 1): Fraction(1)}, {(0, 0): Fraction(1)}
    one_s = add(one, s, -1)
    one_t = add(one, t, -1)
    norm = add(mul(one_s, one_s), mul(one_t, one_t))
    # s*(den^2) - (v_num^2 - 2 v_num den - den^2) clears to 0 on the circle,
    # and the same for t against den^2 - 2 v_num den - v_num^2.
    right_s = add(add(mul(one_t, one_t), mul(mul({(0, 0): Fraction(2)}, one_t), one_s), -1),
                  mul(one_s, one_s), -1)
    right_t = add(add(mul(one_s, one_s), mul(mul({(0, 0): Fraction(2)}, one_t), one_s), -1),
                  mul(one_t, one_t), -1)
    require(reduce_circle(add(mul(s, norm), right_s, -1)) == {}, "chart recovers s")
    require(reduce_circle(add(mul(t, norm), right_t, -1)) == {}, "chart recovers t")


def check_qp_obstruction():
    # Q(F4)-Q(W) = 2(z-1) for Delta = (1,1,-2).
    for xv, yv, zv in ((0, 0, 0), (1, -2, 3), (Fraction(1, 2), 4, -1), (-3, 1, 1)):
        difference = quad((xv + 1, yv + 1, zv - 2)) - quad((xv, yv, zv))
        require(difference == 2 * (zv - 1), "QP difference")
    require(quad((Fraction(-1, 2), 0, 1)) == Fraction(-1, 2), "x = -1/2 is off the cone")
    check_chart_completeness()
    # Missing chart point F0 = (0,-2,0), z = 1, y = -x/(2x+1).
    # F2 = (1-x, 2-y, 0) and F3 = (-x, 3-y, 0); both third coordinates vanish.
    den = {0: Fraction(1), 1: Fraction(2)}
    ynum = {1: Fraction(-1)}
    # (2-y)*den = 2*den - ynum, and Q(F2)*den = 2(1-x)*that.
    two_minus_y = {exp: 2 * coef for exp, coef in den.items()}
    two_minus_y[1] = two_minus_y.get(1, 0) - ynum[1]
    q2 = multiply_uni({0: Fraction(2), 1: Fraction(-2)}, two_minus_y)
    three_minus_y = {exp: 3 * coef for exp, coef in den.items()}
    three_minus_y[1] = three_minus_y.get(1, 0) - ynum[1]
    q3 = multiply_uni({1: Fraction(-2)}, three_minus_y)

    def eval_uni(poly, value):
        return sum(coef * value ** exp for exp, coef in poly.items())

    # q3 = -2x(3*den - ynum)/something already includes the factor. Roots:
    roots = []
    # -2x * (3(2x+1) - (-x)) = -2x(6x+3+x) = -2x(7x+3) = -14x^2 - 6x
    require(q3 == {1: Fraction(-6), 2: Fraction(-14)}, "missing-point F3 quad")
    for root in (0, Fraction(-3, 7)):
        require(eval_uni(q3, root) == 0, "q3 root")
        require(eval_uni(q2, root) != 0, "missing point has no cone partner")
    q_y, q_z, _den = qp_polynomials()
    # Delta^2 Q at x=1, v=1. D=2, den=3, Delta=6.
    frame = (Fraction(-2), Fraction(-2), Fraction(2))
    w = (Fraction(1), Fraction(-1, 3), Fraction(1))
    f2 = tuple(TARGETS[0][i] - frame[i] - w[i] for i in range(3))
    f3 = tuple(TARGETS[2][i] - frame[i] - w[i] for i in range(3))
    scale = 36

    def eval_bivar(poly, xv, vv):
        total = 0
        for (ex, ev), coef in poly.items():
            total += coef * xv ** ex * vv ** ev
        return total

    require(eval_bivar(q_y, 1, 1) == scale * quad(f2), "QP polynomial matches F2")
    require(eval_bivar(q_z, 1, 1) == scale * quad(f3), "QP polynomial matches F3")
    # Both are divisible by 2x+1. Euclid on the quotients has a positive remainder.
    left, rem_l = divide_by_linear(univariate(q_y, 0))
    right, rem_r = divide_by_linear(univariate(q_z, 0))
    require(rem_l == {} and rem_r == {}, "extraneous factor divides both")
    remainder = euclid_positive(left, right)
    expected = {
        0: 122880, 2: 1613824, 4: 12115968, 6: 64200704, 8: 253976576,
        10: 773136384, 12: 1818779648, 14: 3259113472, 16: 4364804096,
        18: 4292730880, 20: 3048382464, 22: 1536876544, 24: 543760384,
        26: 136077312, 28: 24387584, 30: 2580480,
    }
    require(remainder == {exp: Fraction(coef) for exp, coef in expected.items()},
            "QP remainder")


def check_triple():
    names = list(permutations(range(4)))
    consistent = []
    for perm in names:
        rhs = [TARGETS[perm[i]] for i in range(4)] + [TOTAL]
        ok, _particular, kernel = rref_incidence(TRIPLE, rhs)
        if ok:
            consistent.append(perm)
            require(len(kernel) == 2, "triple nullity")
            difference = tuple(_particular[5][coord] - _particular[0][coord] for coord in range(3))
            require(difference == TWO_I, "padding is 2I plus the common frame")
            require(all(vector[5] == vector[0] for vector in kernel), "kernel preserves the relation")
    require(len(consistent) == 8, "eight triple assignments")
    # Equation swap (0 1)(2 3) preserves the solution set.
    def swapped(perm):
        return (perm[1], perm[0], perm[3], perm[2])

    def apply_map(perm, mapping):
        images = [mapping(TARGETS[perm[i]]) for i in range(4)]
        return tuple(TARGETS.index(image) for image in images)

    ab = (0, 1, 2, 3)
    qp = (0, 2, 1, 3)
    expected = {
        ab, swapped(ab),
        apply_map(ab, sigma), swapped(apply_map(ab, sigma)),
        qp, swapped(qp),
        apply_map(qp, tau), swapped(apply_map(qp, tau)),
    }
    require(set(consistent) == expected, "triple assignments are the automorphism orbit")
    check_ab_obstruction()
    check_qp_obstruction()


# --- orbit census ---------------------------------------------------------------


def canonical_key(masks):
    degrees = [0] * 6
    for mask in masks:
        for column in range(6):
            degrees[column] += (mask >> column) & 1
    order = sorted(range(6), key=lambda column: (-degrees[column], column))
    groups = []
    start = 0
    for index in range(1, 7):
        if index == 6 or degrees[order[index]] != degrees[order[index - 1]]:
            groups.append(order[start:index])
            start = index
    best = None
    blocks = [list(permutations(group)) for group in groups]

    def walk(position, columns):
        nonlocal best
        if position == len(blocks):
            mapped = []
            for mask in masks:
                dest = 0
                for new, old in enumerate(columns):
                    if (mask >> old) & 1:
                        dest |= 1 << new
                mapped.append(dest)
            mapped.sort()
            key = (mapped[0], mapped[1], mapped[2], mapped[3])
            if best is None or key < best:
                best = key
            return
        for block in blocks[position]:
            walk(position + 1, columns + list(block))

    walk(0, [])
    return best


def orbit_representatives(masks):
    keys = {}
    for choice in combinations(range(len(masks)), 4):
        system = tuple(masks[i] for i in choice)
        key = canonical_key(system)
        keys.setdefault(key, key)
    return list(keys)


def check_census():
    masks = mask_list()
    require(len(masks) == 50, "fifty subsets")
    representatives = orbit_representatives(masks)
    require(len(representatives) == 658, "658 orbits")
    require(canonical_key(CYCLE) == canonical_key((3, 6, 9, 12)), "witness is the cycle orbit")
    require(canonical_key(CYCLE) != canonical_key(TRIPLE), "the exceptional orbits differ")
    cycle_key = canonical_key(CYCLE)
    triple_key = canonical_key(TRIPLE)
    counts = {"inconsistent": 0, "special": 0, "cert-1": 0, "cert-2": 0}
    for system in representatives:
        for perm in permutations(range(4)):
            rhs = [TARGETS[perm[i]] for i in range(4)] + [TOTAL]
            ok, particular, kernel = rref_incidence(system, rhs)
            if not ok:
                counts["inconsistent"] += 1
                continue
            if system in (cycle_key, triple_key):
                counts["special"] += 1
                continue
            nvars = 3 * len(kernel)
            polys = [quad_polynomial(frame_polynomials(particular, kernel, column, nvars))
                     for column in range(6)]
            found = certificate_of_one(polys, nvars)
            require(found is not None, "missing certificate for " + str(system))
            solution, multipliers = found
            require(expansion_is_one(polys, multipliers, solution, nvars), "certificate expansion")
            counts["cert-" + str(len(kernel))] += 1
    require(counts == {"inconsistent": 4224, "special": 16, "cert-1": 11472, "cert-2": 80},
            "census counts " + str(counts))
    require(sum(counts.values()) == 658 * 24, "every assignment was classified")


def main():
    check_determinants()
    check_witness()
    check_character_family()
    check_automorphisms()
    check_cycle()
    check_triple()
    check_census()
    print("PASS")


if __name__ == "__main__":
    main()
