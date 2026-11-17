"""Sharp denominator-capped error; exact arithmetic, fixed finite domains."""
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import json
from math import gcd


def need(condition, message):
    if not condition:
        raise ValueError(message)


def rounded(value):
    shifted = value + Fraction(1, 2)
    return shifted.numerator // shifted.denominator


def literal(a, b, x, y, z):
    """Four actual integer-register updates, including both inverse calls."""
    z += rounded(a * x)
    y += rounded(b * z)
    z -= rounded(a * x)
    y -= rounded(b * z)
    return x, y, z


def quotient_error(a, b, x, z):
    """Integer-only representation, independent of Fraction-round execution."""
    u, s = a.numerator, a.denominator
    v, t = b.numerator, b.denominator
    r = (2 * u * x + s) // (2 * s)
    high = (2 * v * (z + r) + t) // (2 * t)
    low = (2 * v * z + t) // (2 * t)
    return Fraction((high - low) * s * t - u * v * x, s * t)


def cap_bound(cap):
    need(type(cap) is int and 1 <= cap < 2**256, 'cap domain')
    return Fraction(0) if cap == 1 else Fraction(3 * (cap - 1), 2 * cap)


def witness(cap):
    need(type(cap) is int and 2 <= cap < 2**256, 'witness cap domain')
    return Fraction(1, 2), Fraction(cap - 1, cap), 2 * cap - 3, -((cap - 1) // 2)


def coefficients(cap):
    return tuple(sorted({Fraction(u, s) for s in range(1, cap + 1)
                         for u in range(-s, s + 1) if gcd(u, s) == 1}))


def exhaustive():
    """Each pair's complete error periods; record its smallest cap."""
    maximum = [Fraction(0)] * 9
    pairs = [0] * 9
    visits = 0
    values = coefficients(8)
    for a in values:
        for b in values:
            cap = max(a.denominator, b.denominator)
            pairs[cap] += 1
            for x in range(a.denominator * b.denominator):
                for z in range(b.denominator):
                    out = literal(a, b, x, 7, z)
                    need(out[0] == x and out[2] == z, 'arbitrary dirty return')
                    error = Fraction(out[1] - 7) - a * b * x
                    need(error == quotient_error(a, b, x, z), 'two arithmetic engines')
                    need(abs(error) <= cap_bound(cap), 'denominator-cap upper bound')
                    maximum[cap] = max(maximum[cap], abs(error))
                    visits += 1
    rows = []
    running = Fraction(0)
    for cap in range(1, 9):
        running = max(running, maximum[cap])
        need(running == cap_bound(cap), 'exact finite cap optimum')
        rows.append({'cap': cap, 'new_pairs': pairs[cap], 'maximum': str(running)})
    return {'rows': rows, 'pairs': sum(pairs), 'literal_visits': visits}


def families():
    caps = tuple(range(2, 257)) + tuple(2**p for p in range(9, 129))
    checks = 0
    for cap in caps:
        a, b, x, z = witness(cap)
        need(max(a.denominator, b.denominator) == cap, 'reduced denominator')
        for y in (-17, 0, 23):
            out = literal(a, b, x, y, z)
            need(out[0] == x and out[2] == z, 'witness restoration')
            error = Fraction(out[1] - y) - a * b * x
            need(error == cap_bound(cap), 'all-cap positive attainer')
            need(error == quotient_error(a, b, x, z), 'witness second engine')
            checks += 1
    periods = 0
    for a in coefficients(5):
        for b in coefficients(5):
            step = a.denominator * b.denominator
            for x, z in ((-11, -7), (0, 0), (13, 9)):
                base = quotient_error(a, b, x, z)
                need(base == quotient_error(a, b, x + step, z), 'source period')
                need(base == quotient_error(a, b, x, z + b.denominator), 'dirt period')
                periods += 1
    return {'attaining_caps': len(caps), 'attaining_executions': checks,
            'signed_period_checks': periods, 'largest_cap': str(caps[-1])}


def controls():
    a, b, x, z = witness(3)
    need(quotient_error(a, b, x, z) > cap_bound(2), 'larger denominator escapes')
    need(quotient_error(Fraction(1, 2), Fraction(2), 1, 0) > cap_bound(2),
         'expansive outer coefficient escapes')
    need(rounded(Fraction(-1, 2)) != -rounded(Fraction(1, 2)),
         'negated coefficient does not implement inverse')
    need(literal(Fraction(1, 2), Fraction(1, 2), 1, 0, 0)[1] == 1,
         'half-up tie fixture')
    need(literal(Fraction(1, 2), Fraction(1, 2), 1, 0, 1)[1] == 0,
         'dirty-dependent output despite exact return')
    rejected = 0
    for cap in (0, -1, True, Fraction(2), 2**256):
        try:
            cap_bound(cap)
        except ValueError:
            rejected += 1
    need(rejected == 5, 'invalid cap rejection')
    try:
        witness(1)
    except ValueError:
        rejected += 1
    need(rejected == 6, 'integer-only cap has no positive-error witness')
    for a in coefficients(1):
        for b in coefficients(1):
            for x in (-10, 0, 11):
                need(literal(a, b, x, 4, -3) == (x, 4 + a * b * x, -3),
                     'integer-only exact endpoint')
    return {'semantic_controls': 6, 'domain_rejections': rejected}


def main():
    result = {'marker': 'PASS_DENOMINATOR_CAPPED_COMMUTATOR',
              'exhaustive': exhaustive(), 'families': families(), 'controls': controls()}
    package = Path(__file__).resolve().parent
    names = ('README.md', 'TASK.json', 'SOURCES.json', 'VERIFY.json', 'verify.py')
    result['sha256'] = {name: sha256((package / name).read_bytes()).hexdigest()
                        for name in names}
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
