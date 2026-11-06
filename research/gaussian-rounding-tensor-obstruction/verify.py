#!/usr/bin/env python3
"""Exact finite checks supporting the all-n theorem in PROOF.md.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
The universal argument is algebraic; these bounded checks are not a search
or a finite substitute for its quantifier over n and all Gaussian inputs.
"""
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json
import platform

ZERO = (0, 0)
ONE = (1, 0)
UNITS = ((1, 0), (0, 1), (-1, 0), (0, -1))


def need(ok, label):
    if not ok:
        raise ValueError(label)


def add(a, b):
    return (a[0]+b[0], a[1]+b[1])


def sub(a, b):
    return (a[0]-b[0], a[1]-b[1])


def mul(a, b):
    return (a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0])


def conj(a):
    return (a[0], -a[1])


def power(a, n):
    out = ONE
    for _ in range(n):
        out = mul(out, a)
    return out


def norm2(a):
    return a[0]*a[0]+a[1]*a[1]


def scale(a, v):
    return tuple(mul(a, x) for x in v)


def inner_sum(values):
    out = ZERO
    for value in values:
        out = add(out, value)
    return out


def tensor_native(n):
    # Construct from the original two-by-two matrix, rather than the closed
    # Hamming-weight/denominator formula being checked.
    base = (((Q(1,2), Q(1,2)), (Q(1,2), Q(-1,2))),
            ((Q(1,2), Q(-1,2)), (Q(1,2), Q(1,2))))
    out = ((ONE,),)
    for _ in range(n):
        out = tuple(tuple(mul(x, y) for x in row for y in small)
                    for row in out for small in base)
    return out


def ideal(matrix, v):
    return tuple(inner_sum(mul(a, b) for a, b in zip(row, v)) for row in matrix)


def nearest_even(x):
    x = Q(x)
    q, rem = divmod(x.numerator, x.denominator)
    if 2*rem < x.denominator:
        return q
    if 2*rem > x.denominator:
        return q+1
    return q if q % 2 == 0 else q+1


def rounder(matrix, floor=False):
    def apply(v):
        result = ideal(matrix, v)
        if floor:
            return tuple((Q(a).numerator//Q(a).denominator,
                          Q(b).numerator//Q(b).denominator) for a, b in result)
        return tuple((nearest_even(a), nearest_even(b)) for a, b in result)
    return apply


def integral(v):
    return all(Q(a).denominator == Q(b).denominator == 1 for a,b in v)


def integer_vector(v):
    need(integral(v), 'noninteger vector conversion')
    return tuple((int(a),int(b)) for a,b in v)


def conservative_bijection(matrix, chosen):
    size = len(matrix)
    e0 = (ONE,)+(ZERO,)*(size-1)
    ej = tuple(ONE if j == chosen else ZERO for j in range(size))
    def swap(v):
        for scalar in UNITS:
            if tuple(v) == scale(scalar,e0): return scale(scalar,ej)
            if tuple(v) == scale(scalar,ej): return scale(scalar,e0)
        return tuple(v)
    def forward(v):
        image = ideal(matrix,v)
        return integer_vector(image) if integral(image) else swap(v)
    def inverse(v):
        image = ideal(matrix,v)
        return tuple(reversed(integer_vector(image))) if integral(image) else swap(v)
    return forward, inverse


def rows(array, f):
    return tuple(f(row) for row in array)


def columns(array, f):
    return tuple(zip(*rows(tuple(zip(*array)), f)))


def rank_one(a, b):
    return tuple(tuple(mul(x, y) for y in b) for x in a)


def difference(a, b):
    return tuple(tuple(sub(x, y) for x, y in zip(row, other)) for row, other in zip(a, b))


def frobenius2(array):
    return sum(norm2(x) for row in array for x in row)


def reject(action, label):
    try:
        action()
    except ValueError:
        return label
    raise ValueError('negative control accepted: '+label)


def main():
    coefficient_cases = []
    tensor_cases = 0
    phase_cases = 0
    exact_grid_cases = 0
    sharp_cases = []
    conservative_cases = []
    sample = {}
    for n in range(7):
        matrix = tensor_native(n)
        size = 1 << n
        alpha = power((1, -1), n)
        lam = tuple(mul(power((0, -1), n), power((0, 1), j.bit_count()))
                    for j in range(size))
        unit = (ONE,) + (ZERO,)*(size-1)
        zero = (ZERO,)*size
        need(norm2(alpha) == size, 'Gaussian denominator norm')
        for r in range(size):
            for s in range(size):
                expected = power((0,-1), (r^s).bit_count())
                need(mul(alpha, matrix[r][s]) == expected, 'tensor coefficient formula')
        need(all(x in UNITS for x in lam), 'lambda must have Gaussian-unit entries')
        need(lam == tuple(mul(alpha, conj(matrix[0][r])) for r in range(size)),
             'lambda is alpha U inverse e0')
        need(ideal(matrix, lam) == scale(alpha, unit), 'U lambda equals alpha e0')
        coefficient_cases.append({'n': n, 'size': size, 'alpha': list(alpha)})
        f = rounder(matrix)
        z = tuple(((3*j+1) % 7-3, (5*j+2) % 9-4) for j in range(size))
        fixtures = (unit, z, tuple((1-j, j % 3) for j in range(size)))
        for v in fixtures:
            for scalar in UNITS:
                need(f(scale(scalar, v)) == scale(scalar, f(v)), 'global unit covariance')
                phase_cases += 1
            integral_input = scale(alpha, v)
            need(f(integral_input) == ideal(matrix, integral_input), 'exact integral-image action')
            exact_grid_cases += 1
        for scalar in ((0,0), (1,0), (0,1), (2,-3), ((1<<127)+1, -(1<<113))):
            v = scale(scalar, lam)
            need(f(v) == scale(mul(alpha, scalar), unit), 'exact lambda-line action')
            exact_grid_cases += 1
        if n == 0:
            need(f(unit) == unit and alpha == ONE, 'zero-axis identity control')
            continue
        need(f(unit) == zero, 'nearest-even sharp witness including half ties')
        ideal_unit = ideal(matrix, unit)
        need(sum(norm2(x) for x in ideal_unit) == 1, 'unit ideal-column norm')
        need(all(abs(a) <= Q(1,2) and abs(b) <= Q(1,2) for a,b in ideal_unit),
             'zero is a nearest Gaussian point')
        need(all(mul(alpha, x) in UNITS for x in ideal_unit), 'unit numerator column')
        sharp_cases.append({'n': n, 'defect_squared': size})
        if n <= 4:
            for v in fixtures:
                array = rank_one(lam, v)
                left = rows(columns(array, f), f)
                right = columns(rows(array, f), f)
                expected = rank_one(unit, scale(alpha, tuple(sub(x,y) for x,y in
                                                             zip(ideal(matrix,v), f(v)))))
                defect = difference(left, right)
                need(defect == expected, 'exact nonlinear tensor defect identity')
                need(frobenius2(defect) == size * sum(norm2(sub(x,y)) for x,y in
                                                     zip(ideal(matrix,v), f(v))),
                     'quantitative tensor defect identity')
                if v == unit:
                    need(frobenius2(defect) == size, 'sharp sqrt(N) floor')
                    need(all(x != ZERO for x in defect[0]) and
                         all(x == ZERO for row in defect[1:] for x in row),
                         'every first-row coordinate differs')
                tensor_cases += 1
        chosen = (1 << (n//2))-1
        maximum_component = Q(1, 1 << ((n+1)//2))
        need(ideal_unit[chosen][0] == maximum_component and
             all(abs(a) <= maximum_component and abs(b) <= maximum_component for a,b in ideal_unit),
             'exact largest column component')
        bijection, inverse = conservative_bijection(matrix,chosen)
        image = bijection(unit)
        ej = tuple(ONE if j==chosen else ZERO for j in range(size))
        need(image == ej, 'attaining coordinate orbit')
        stronger = 2*size-(1 << (n//2+1))
        need(size*sum(norm2(sub(x,y)) for x,y in zip(ideal_unit,image)) == stronger,
             'sharp conservative bijection witness')
        for v in fixtures + (ej,lam,scale(alpha,z),scale((0,1),unit)):
            out = bijection(v)
            need(inverse(out) == v and bijection(inverse(v)) == v, 'literal bijection inverse')
            need(inner_sum(out) == inner_sum(v), 'conservative bijection sum')
            for scalar in UNITS:
                need(bijection(scale(scalar,v)) == scale(scalar,out), 'whole unit-orbit swap')
            if integral(ideal(matrix,v)):
                need(out == ideal(matrix,v), 'bijection integral-image exactness')
        need(bijection(bijection(unit)) != tuple(reversed(unit)),
             'attainment example does not satisfy the native square')
        if n <= 4:
            array = rank_one(lam,unit)
            defect = difference(rows(columns(array,bijection),bijection),
                                columns(rows(array,bijection),bijection))
            need(frobenius2(defect) == stronger, 'complete conservative tensor witness')
        conservative_cases.append({'n':n,'chosen_coordinate':chosen,'defect_squared':stronger})
        if n == 1:
            sample = {'matrix': matrix, 'alpha': alpha, 'lambda': lam, 'unit': unit, 'f': f}

    # A signed fixture at scale 2**257 (at most 258 component bits) checks exact rounding and both composition
    # orders without floating point, on the two-axis native block.
    matrix = tensor_native(2)
    alpha = power((1,-1), 2)
    lam = tuple(mul(power((0,-1), 2), power((0,1), j.bit_count())) for j in range(4))
    unit = (ONE, ZERO, ZERO, ZERO)
    z = tuple((((-1)**j)*(1<<257)+j, (1<<193)-2*j) for j in range(4))
    f = rounder(matrix)
    defect = difference(rows(columns(rank_one(lam,z),f),f), columns(rows(rank_one(lam,z),f),f))
    need(defect == rank_one(unit, scale(alpha, tuple(sub(x,y) for x,y in zip(ideal(matrix,z),f(z))))),
         'large-word exact tensor identity')

    matrix, alpha, lam, unit, f = (sample[k] for k in ('matrix','alpha','lambda','unit','f'))
    controls = []
    identity = lambda v: tuple(v)
    array = rank_one(lam, unit)
    need(rows(columns(array, identity), identity) == columns(rows(array, identity), identity),
         'identity commutes when grid-exactness is dropped')
    need(all(identity(scale(u,unit)) == scale(u,identity(unit)) for u in UNITS),
         'identity retains phase covariance')
    controls.append(reject(lambda: need(identity(lam) == ideal(matrix,lam), 'identity is not exact on ideal grid'),
                           'dropping integral-image exactness admits identity'))

    fractional = lambda v: ideal(matrix,v)
    need(rows(columns(array,fractional),fractional) == columns(rows(array,fractional),fractional),
         'ideal rational transform commutes')
    controls.append(reject(lambda: need(all(Q(a).denominator == Q(b).denominator == 1
                                            for a,b in fractional(unit)), 'ideal image is nonintegral'),
                           'dropping integer codomain admits the ideal transform'))

    floor = rounder(matrix, floor=True)
    need(floor(lam) == ideal(matrix,lam), 'floor retains integral-image exactness')
    controls.append(reject(lambda: need(floor(scale((0,1),unit)) == scale((0,1),floor(unit)),
                                        'floor loses global phase covariance'),
                           'coordinate floors do not establish phase covariance'))
    wrong_lam = tuple(power((0,1),j.bit_count()) for j in range(2))
    controls.append(reject(lambda: need(ideal(matrix,wrong_lam) == scale(alpha,unit),
                                        'missing denominator conjugate phase'),
                           'omitting alpha over conjugate-alpha phase'))
    defect = difference(rows(columns(array,f),f),columns(rows(array,f),f))
    controls.append(reject(lambda: need(frobenius2(defect) == 0, 'nonzero exact tensor defect'),
                           'false tensor commutation'))
    controls.append(reject(lambda: need(frobenius2(defect) > 2, 'attained sharp floor'),
                           'false strictly larger universal defect floor'))
    need(f(unit) == f((ZERO, ZERO)), 'sharpness example is intentionally nonbijective')
    matrix4 = tensor_native(4)
    e0_4 = (ONE,)+(ZERO,)*15
    b4, _ = conservative_bijection(matrix4,3)
    broken = lambda v: tuple(v) if tuple(v)==scale((0,1),e0_4) else b4(v)
    controls.append(reject(lambda: need(broken(scale((0,1),e0_4)) == scale((0,1),broken(e0_4)),
                                        'one phase cannot be omitted from the swapped orbit'),
                           'swapping an incomplete Gaussian-unit orbit'))
    result = {
        'status': 'PASS_GAUSSIAN_ROUNDING_TENSOR_OBSTRUCTION',
        'python': platform.python_version(),
        'coefficient_cases': coefficient_cases,
        'full_nonlinear_tensor_cases': tensor_cases,
        'tensor_axis_range': [1,4],
        'large_word_cases': 1,
        'global_phase_cases': phase_cases,
        'integral_image_cases': exact_grid_cases,
        'sharp_defect_cases': sharp_cases,
        'sharp_conservative_bijection_cases': conservative_cases,
        'hypothesis_controls': controls,
        'zero_axis_identity_control': True,
        'broad_floor_example_bijective': False,
        'stronger_floor_example_bijective_and_sum_preserving': True,
        'stronger_floor_example_uniform_error_bound': False,
        'source_sha256': sha256(Path(__file__).read_bytes()).hexdigest(),
        'scope': 'Bounded exact checks plus the separate universal all-n proof; no new kappa, no selected-theorem counterexample.'
    }
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__ == '__main__':
    main()
