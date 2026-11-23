"""Independent rational-series oracle for the literal dyadic mass routine.

No author checker imports, floating-point arithmetic, or source square-root
recurrence is used in the oracle. Integer-root bisection handles exact cases;
otherwise log and exp use exact rational series with explicit tail bounds.
"""

from __future__ import annotations

import argparse
from fractions import Fraction as F
from functools import cache
from hashlib import sha256
import json
from pathlib import Path
import sys
import types


HERE = Path(__file__).resolve().parent
SOURCE_SHA = '98bdb540233794338b426d1b0d0e72cff7fcbbd08be702af0d81e237dbecaae9'
Q = 1 << 384
GAUSSIAN_T = 1 - F(2092819, 1 << 29)
BINARY_T = 1 - F(4484997569314581, 1 << 60)


def floor(q: F) -> int:
    return q.numerator // q.denominator


def ceil(q: F) -> int:
    return -floor(-q)


def rounded(lo: F, hi: F) -> tuple[F, F]:
    return F(floor(lo * Q), Q), F(ceil(hi * Q), Q)


def root_floor(n: int, degree: int) -> int:
    """Monotone integer bisection, not isqrt or source arithmetic."""
    low, high = 0, 1 << ((n.bit_length() + degree - 1) // degree)
    while low + 1 < high:
        mid = (low + high) // 2
        if mid ** degree <= n:
            low = mid
        else:
            high = mid
    return high if high ** degree == n else low


def small_log(q: F) -> tuple[F, F]:
    assert 1 <= q <= 2
    z = (q - 1) / (q + 1)
    z2, power, total = z * z, z, F(0)
    terms = 110
    for j in range(terms):
        total += power / (2 * j + 1)
        power *= z2
    lo = 2 * total
    tail = 2 * power / ((2 * terms + 1) * (1 - z2))
    return rounded(lo, lo + tail)


@cache
def log_bounds(x: F) -> tuple[F, F]:
    assert x >= 1
    m = x.numerator.bit_length() - x.denominator.bit_length()
    if x < (1 << m):
        m -= 1
    q = x / (1 << m)
    assert 1 <= q < 2 and m >= 0
    qlo, qhi = small_log(q)
    l2, h2 = small_log(F(2))
    return rounded(m * l2 + qlo, m * h2 + qhi)


def small_exp(a: F) -> tuple[F, F]:
    assert 0 <= a <= F(1, 4)
    total = term = F(1)
    degree = 64
    for j in range(1, degree + 1):
        term = term * a / j
        total += term
    following = term * a / (degree + 1)
    tail = following / (1 - a / (degree + 2))
    return total, total + tail


@cache
def inverse_oracle(t: F, x: F) -> tuple[F, F]:
    if x == 1:
        return F(1), F(1)
    if t == 1:
        return 1 / x, 1 / x
    if t.denominator <= 64:
        degree = t.denominator
        a, b = root_floor(x.numerator, degree), root_floor(x.denominator, degree)
        if a ** degree == x.numerator and b ** degree == x.denominator:
            value = F(b, a) ** t.numerator
            return value, value
    lo, hi = log_bounds(x)
    lo, hi = t * lo, t * hi
    squarings = 0
    while hi > F(1, 4):
        lo, hi = lo / 2, hi / 2
        squarings += 1
    elo, _ = small_exp(lo)
    _, ehi = small_exp(hi)
    elo, ehi = rounded(elo, ehi)
    for _ in range(squarings):
        elo, ehi = rounded(elo * elo, ehi * ehi)
    return 1 / ehi, 1 / elo


def load_source(source: str, name: str):
    module = types.ModuleType(name)
    sys.modules[name] = module
    exec(compile(source, f'<{name}>', 'exec'), module.__dict__)
    return module.Measure


def verify_inverse(measure, x: F):
    low, high = measure.inverse_power(x)
    g = measure.grid
    lo, hi = F(low, g), F(high, g)
    actual_lo, actual_hi = inverse_oracle(measure.t, x)
    assert 0 <= lo <= actual_lo <= actual_hi <= hi <= 1
    d = measure.t.denominator.bit_length() - 1
    bound = (F((d + 1) * (d + 2), 2) * x + d + 1) / g
    assert actual_hi - lo <= bound
    assert hi - actual_lo <= bound
    return low == 0


def mass_oracle(t: F, volume: F, left: F, right: F):
    if right <= left:
        return F(0), F(0)
    ll, lh = inverse_oracle(t, left)
    rl, rh = inverse_oracle(t, right)
    return max(F(0), volume * (ll - rh) / t), volume * (lh - rl) / t


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path,
                        default=Path('/workspace/scratch/5b0914ccc34e/work-storage/runtime-exact/transport.py'))
    parser.add_argument('--proof', type=Path,
                        default=Path('/workspace/scratch/e64488edfaad/mass/PROOF.md'))
    args = parser.parse_args()
    source = args.source.read_text()
    assert sha256(args.source.read_bytes()).hexdigest() == SOURCE_SHA
    Measure = load_source(source, 'review_transport')
    exponents = tuple(map(F, (1,))) + (F(1, 2), F(3, 4), F(1, 8), F(7, 8),
                                      F(1, 64), F(63, 64), F(1, 1 << 60),
                                      GAUSSIAN_T, BINARY_T)
    xs = tuple(map(F, (1, 2, 3, 4, 7, 16, 257, 65537))) + (F(4, 3), F(9, 4))
    precisions = (0, 1, 4, 16, 64, 128)
    cases, zero_lower = 0, 0
    for t in exponents:
        for x in xs:
            for p in precisions:
                zero_lower += verify_inverse(Measure(t, F(1), p), x)
                cases += 1
    pairs = ((F(1), F(1)), (F(2), F(1)), (F(1), F(4, 3)),
             (F(4, 3), F(2)), (F(2), F(7)), (F(257), F(65537)))
    mass_cases = allocations = empty_cases = 0
    for t in exponents:
        for p in precisions:
            for volume in (F(0), F(1), F(7, 3)):
                obj = Measure(t, volume, p)
                for left, right in pairs:
                    lo, hi = obj.mass(left, right)
                    ml, mh = mass_oracle(t, volume, left, right)
                    assert 0 <= lo <= ml <= mh <= hi
                    mass_cases += 1
                    if right <= left:
                        assert (lo, hi) == (0, 0)
                        empty_cases += 1
                        continue
                    d = t.denominator.bit_length() - 1
                    e = F((d + 1) * (d + 2), 2) * right + d + 1
                    delta = 2 * volume * e / (t * obj.grid)
                    assert mh - lo <= delta and hi - ml <= delta
                    if delta < F(1, 4):
                        count = ceil(hi)
                        assert mh <= count and count - ml < F(5, 4)
                        for share in (F(0), F(1, 3), F(1)):
                            allocated = floor(share * lo)
                            assert 0 <= allocated <= share * ml
                            assert share * mh - allocated < F(5, 4)
                            allocations += 1

    replacements = {
        'upper_square_root_rounded_down': ('isqrt(b * g - 1) + 1', 'isqrt(b * g)'),
        'reversed_bit_order': ('t.denominator.bit_length() - 1 - j', 'j'),
        'upper_product_rounded_down': ('-(-hi * b // g)', '(hi * b // g)'),
        'lower_square_root_rounded_up': ('a = isqrt(a * g)', 'a = isqrt(a * g) + 1'),
    }
    rejected = {}
    for label, (old, new) in replacements.items():
        assert source.count(old) == 1
        Mutant = load_source(source.replace(old, new), 'mutant_' + label)
        witness = None
        for t in exponents:
            if witness is not None:
                break
            for x in xs:
                if witness is not None:
                    break
                for p in precisions:
                    try:
                        verify_inverse(Mutant(t, F(1), p), x)
                    except AssertionError:
                        witness = {'t': str(t), 'x': str(x), 'p': p}
                        break
        assert witness is not None, label
        rejected[label] = witness

    assert 1891 * 2064 == 3903024
    assert 3903024 * 2 + 61 < (1 << 22) * 2
    assert F(1 << 24, 2 ** 57) == F(1, 1 << 33) < F(1, 4)
    data = {
        'status': 'PASS', 'source_sha256': SOURCE_SHA,
        'proof_sha256': sha256(args.proof.read_bytes()).hexdigest(),
        'oracle': 'exact rational log/exp series plus integer-root bisection for rational cases',
        'inverse_power_cases': cases, 'lower_zero_cases': zero_lower,
        'mass_cases': mass_cases, 'empty_interval_cases': empty_cases,
        'directed_allocation_checks': allocations,
        'mutations_rejected': rejected,
        'finite_evidence_only': True,
    }
    (HERE / 'EVIDENCE.json').write_text(json.dumps(data, indent=2) + '\n')
    print(json.dumps(data, indent=2))


if __name__ == '__main__':
    main()
