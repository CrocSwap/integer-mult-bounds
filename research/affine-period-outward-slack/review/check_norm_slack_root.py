"""Independent exact-rational checks; finite evidence, not the universal proof."""
from fractions import Fraction as Q
from pathlib import Path
import hashlib
import json
import sys


def need(ok, why):
    if not ok:
        raise ValueError(why)


def dot(x, y):
    return sum(a * b for a, b in zip(x, y))


def matvec(a, x):
    return tuple(dot(r, x) for r in a)


def norm2(x):
    return dot(x, x)


def plus(x, y):
    return tuple(a + b for a, b in zip(x, y))


def minus(x, y):
    return tuple(a - b for a, b in zip(x, y))


def times(t, x):
    return tuple(t * a for a in x)


def nearest_up(x):
    z = x + Q(1, 2)
    return z.numerator // z.denominator


def gap_gt(a, b, c, s):
    """Exactly certify sqrt(a)-sqrt(b) > c sqrt(s), for c,s positive."""
    h = a - b - c * c * s
    return h > 0 and h * h > 4 * c * c * s * b


def gap_le(a, b, c, s):
    h = a - b - c * c * s
    return h <= 0 or h * h <= 4 * c * c * s * b


def main():
    u = ((Q(3, 5), Q(-4, 5)), (Q(4, 5), Q(3, 5)))
    ut = tuple(zip(*u))
    need(all(dot(ut[i], ut[j]) == int(i == j) for i in range(2) for j in range(2)),
         'rational rotation is orthogonal')

    def f(x):
        return tuple(nearest_up(z) for z in matvec(u, x))

    errors = []
    rays = 0
    for a in range(5):
        for b in range(5):
            x = (Q(a), Q(b))
            e = minus(f(x), matvec(u, x))
            s = norm2(e)
            errors.append(s)
            for lam in ((5, 0), (0, 5), (-5, -10)):
                need(f(plus(x, lam)) == plus(f(x), matvec(u, lam)), 'period law')
            if not s:
                continue
            lam = times(125, matvec(ut, e))
            need(all(v.denominator == 1 and v % 5 == 0 for v in lam), 'ray in period')
            need(matvec(u, lam) == times(125, e), 'exact positive error ray')
            for t in (1, 2, 16, 256):
                xt = plus(x, times(t, lam))
                ft = f(xt)
                need(minus(ft, matvec(u, xt)) == e, 'error constant on ray')
                aa, bb = norm2(ft), norm2(xt)
                need(gap_le(aa, bb, Q(1), s), 'triangle upper bound')
                c = 1 - Q(1, (t + 2) ** 2)
                need(gap_gt(aa, bb, c, s), 'rational lower approach certificate')
                rays += 1
    need(set(errors) == {Q(0), Q(1, 5)}, 'complete quotient error census')

    source = Path(sys.argv[1]).resolve()
    raw = source.read_bytes()
    blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
    need(blob == 'b00bbbc7655121232a46101962c48e71cee98a39', 'unchanged #6509 kernel')
    namespace = {'__name__': 'pinned_source_kernel'}
    exec(compile(raw, str(source), 'exec'), namespace)
    pair = namespace['pair']
    source_cases = 0
    for t in (0, 1, 2, 3, 8, 64, 1024, 1 << 32, 1 << 64, 1 << 256):
        for sign in (-1, 1):
            x, y = (1 - t, -sign * t), (t, sign * t)
            expected = ((1 + t, -sign * t), (-t, sign * t))
            width = t.bit_length() + 5
            out = pair(x, y, width, sign)
            need(out == expected, 'actual pinned source on exact ray')
            need(pair(*out, width, -sign) == (x, y), 'actual opposite-sign inverse')
            aa, bb = sum(norm2(z) for z in out), norm2(x) + norm2(y)
            need((aa, bb) == (4*t*t + 2*t + 1, 4*t*t - 2*t + 1), 'ray norm polynomials')
            if t:
                c = Q(32*t*t - 2, 32*t*t + 1)
                need(gap_gt(aa, bb, c, Q(1)), 'strict quantitative pair lower bound')
                need(gap_le(aa, bb, Q(1), Q(1)), 'source pair upper bound')
                need(not gap_gt(aa, bb, Q(1), Q(1)), 'source does not exceed its error')
            source_cases += 1
    balls = []
    for p in (1, 2, 3, 7, 31, 128, 257):
        h, t = Q(1, 1 << p), 1 << (p - 1)
        before = h*h*(4*t*t - 2*t + 1)
        after = h*h*(4*t*t + 2*t + 1)
        need(before == 1-h+h*h and after == 1+h+h*h, 'dyadic polynomial identity')
        need(before < 1 < after, 'closed pair Euclidean ball counterexample')
        balls.append(p)

    # Premise controls are explicit counterexamples, not a heuristic search.
    need(f((1, 0)) != plus(f((0, 0)), matvec(u, (1, 0))), 'wrong period rejected')
    need(norm2((2, 0)) - norm2((1, 0)) > 0, '2I cannot replace orthogonality')
    inward = lambda x: (x[0], x[1] - ((x[1] > 0) - (x[1] < 0)))
    need(inward((7, 2)) == plus(inward((2, 2)), (5, 0)), 'rank-one period control')
    need(norm2(minus(inward((0, 1)), (0, 1))) == 1, 'rank-one error is nonzero')
    need(all(norm2(inward((a, b))) <= a*a+b*b for a in range(-3,4) for b in range(-3,4)),
         'rank-one example is inward on finite corroborating box')
    # For U:x->(x,0), F(x)=(x, x mod 2), the exact supremum is sqrt(2)-1 < 1.
    need(gap_le(Q(2), Q(1), Q(1), Q(1)), 'rectangular isometry counterexample')
    need(norm2(minus((1,1),(1,0))) == 1, 'rectangular error magnitude')
    print(json.dumps({
        'status': 'PASS_ROOT_AFFINE_PERIOD_SLACK_REVIEW',
        'rotation': '[[3,-4],[4,3]]/5', 'quotient_representatives': 25,
        'rotation_max_error_squared': str(max(errors)), 'exact_ray_checks': rays,
        'source_blob': blob, 'source_sha256': hashlib.sha256(raw).hexdigest(),
        'unchanged_source_ray_and_inverse_cases': source_cases,
        'source_t_exponents_through': 256, 'dyadic_unit_ball_p': balls,
        'premise_controls': ['wrong period', 'nonorthogonal map', 'rank-deficient period', 'rectangular isometry'],
        'scope': 'Exact finite independent corroboration; universal equality and source-family optimum require written proofs. No full #6758 table replay.',
    }, indent=2))


if __name__ == '__main__':
    main()
