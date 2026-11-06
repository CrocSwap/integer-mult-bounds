#!/usr/bin/env python3
"""Exact finite corroboration, not a formal proof. Standard library only.
Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
"""
import hashlib
import json
from fractions import Fraction as F
from pathlib import Path
ROOT = Path(__file__).resolve().parent
BITS, STEPS = 112, 44

def require(ok, message):
    if not ok:
        raise ValueError(message)

def point(x):
    return F(x), F(x)

def add(x, y):
    return x[0] + y[0], x[1] + y[1]

def sub(x, y):
    return x[0] - y[1], x[1] - y[0]

def mul(x, y):
    products = [a * b for a in x for b in y]
    return min(products), max(products)

def div(x, y):
    require(y[0] > 0, 'nonpositive interval divisor')
    return mul(x, (1 / y[1], 1 / y[0]))

def iroot(n, degree):
    require(isinstance(n, int) and n >= 0, 'invalid root radicand')
    require(isinstance(degree, int) and 1 <= degree <= 32, 'invalid root degree')
    lo, hi = 0, 1 << ((n.bit_length() + degree - 1) // degree)
    for _ in range(hi.bit_length() + 1):
        if hi - lo <= 1:
            break
        mid = (lo + hi) // 2
        if mid ** degree <= n:
            lo = mid
        else:
            hi = mid
    require(lo ** degree <= n < (lo + 1) ** degree, 'integer-root enclosure')
    return lo

def power(x, exponent):
    """Outward dyadic bounds; preserve exact rational perfect roots."""
    x, exponent = F(x), F(exponent)
    require(x >= 0 and 0 < exponent <= 8, 'power domain')
    require(exponent.denominator <= 32, 'power denominator limit')
    p, q = exponent.numerator, exponent.denominator
    num, den = x.numerator ** p, x.denominator ** p
    rn, rd = iroot(num, q), iroot(den, q)
    if rn ** q == num and rd ** q == den:
        return point(F(rn, rd))
    scale = 1 << BITS
    low = iroot((num * scale ** q) // den, q)
    return F(low, scale), F(low + 1, scale)

def ipower(x, exponent):
    require(0 <= x[0] <= x[1], 'negative power interval')
    return power(x[0], exponent)[0], power(x[1], exponent)[1]

def parameters(t, sigma):
    require(isinstance(t, F) and isinstance(sigma, F), 'rational parameters required')
    require(0 < t < 1 and sigma > 1, 'finite interior parameter domain')
    require(t.denominator <= 16 and sigma.denominator <= 16, 'parameter denominator')
    require(sigma <= 4, 'census sigma bound')

def h_interval(q, s, t, sigma):
    require(q >= 1 and 0 < s <= 1, 'stationary equation domain')
    sp, xp = power(s, t), power(q + s, t)
    return add(sub(mul(point(t * q / s + t - sigma), sp), point(sigma * q)),
               mul(point(sigma - t), xp))

def remainder_root(q, t, sigma):
    lo, hi = F(0), F(1)
    for _ in range(STEPS):
        mid = (lo + hi) / 2
        value = h_interval(q, mid, t, sigma)
        if value[0] > 0:
            lo = mid
        elif value[1] < 0:
            hi = mid
        else:
            left, right = (lo + mid) / 2, (mid + hi) / 2
            require(h_interval(q, left, t, sigma)[0] > 0, 'root left refinement')
            require(h_interval(q, right, t, sigma)[1] < 0, 'root right refinement')
            lo, hi = left, right
    require(lo > 0 and h_interval(q, lo, t, sigma)[0] > 0, 'root lower sign')
    require(h_interval(q, hi, t, sigma)[1] < 0, 'root upper sign')
    return lo, hi

def ratio_interval(q, s, t, sigma):
    require(q >= 1 and 0 <= s[0] <= s[1] <= 1, 'split ratio domain')
    x = add(point(q), s)
    numerator = sub(add(point(q), ipower(s, t)), ipower(x, t))
    return div(numerator, ipower(x, sigma))

def turning_sign(q, t, sigma):
    a = power(t, 1 / (1 - t))
    value = sub(mul(point(sigma - t),
                    sub(ipower(add(point(q), a), t), div(a, point(t)))),
                point((sigma - 1) * q))
    require(value[0] > 0 or value[1] < 0, 'turning sign inconclusive')
    return 1 if value[0] > 0 else -1

def candidate_quotients(t, sigma):
    parameters(t, sigma)
    if t == F(1, 2):
        n = 1 / (2 * (sigma - 1))
        if n.denominator == 1:
            return [int(n * (n + 1))], 'exact-half-exponent-family'
    if turning_sign(1, t, sigma) < 0:
        return [1], 'turning-point-below-one'
    lo, hi = 1, 2
    for _ in range(12):
        if turning_sign(hi, t, sigma) < 0:
            break
        lo, hi = hi, hi * 2
    require(turning_sign(hi, t, sigma) < 0, 'turning bracket bound exhausted')
    for _ in range(12):
        if hi - lo == 1:
            break
        mid = (lo + hi) // 2
        if turning_sign(mid, t, sigma) > 0:
            lo = mid
        else:
            hi = mid
    require(hi - lo == 1, 'adjacent quotient bracket')
    return [lo, hi], 'strict-integer-turning-bracket'

def coefficient(t, sigma):
    candidates, kind = candidate_quotients(t, sigma)
    rows = []
    for q in candidates:
        root = remainder_root(q, t, sigma)
        value = ratio_interval(q, root, t, sigma)
        witness = ratio_interval(q, point((root[0] + root[1]) / 2), t, sigma)
        rows.append((q, root, value, witness))
    bounds = max(row[3][0] for row in rows), max(row[2][1] for row in rows)
    require(0 < bounds[0] <= bounds[1] < 1, 'coefficient interval')
    require(bounds[1] - bounds[0] < F(1, 10 ** 9), 'coefficient precision')
    return candidates, kind, rows, bounds

def power_controls():
    count = 0
    for base in [F(0), F(1, 17), F(2, 3), F(1), F(9, 4), F(17), F(257, 3)]:
        for exponent in [F(1, 3), F(1, 2), F(2, 3), F(3, 2), F(7, 4)]:
            lo, hi = power(base, exponent)
            exact = base ** exponent.numerator
            require(lo ** exponent.denominator <= exact <= hi ** exponent.denominator,
                    'rational-power enclosure')
            count += 1
    return count

def census():
    rows, cases, envelope_checks, witnesses = [], 0, 0, 0
    for t in [F(1, 3), F(1, 2), F(2, 3), F(3, 4)]:
        for sigma in [F(5, 4), F(3, 2), F(2), F(3)]:
            candidates, kind, optimized, bound = coefficient(t, sigma)
            for q in range(1, 9):
                root = remainder_root(q, t, sigma)
                value = ratio_interval(q, root, t, sigma)
                if q not in candidates:
                    require(value[1] < bound[0], 'noncandidate optimized quotient')
                    envelope_checks += 1
                for j in range(1, 9):
                    for r in range(j):
                        actual = ratio_interval(q, point(F(r, j)), t, sigma)
                        require(actual[1] <= bound[1], 'literal integer split exceeds bound')
                        cases += 1
            for q, root, _, _ in [max(optimized, key=lambda row: row[3][0])]:
                j = 10 ** 8
                r = (root[0].numerator * j) // root[0].denominator
                witness = ratio_interval(q, point(F(r, j)), t, sigma)
                require(bound[1] - witness[0] < F(1, 10 ** 6), 'integer sharpness witness')
                witnesses += 1
            rows.append(dict(t=str(t), sigma=str(sigma), candidates=candidates,
                             bracket=kind, coefficient=[str(x) for x in bound]))
    return rows, cases, envelope_checks, witnesses

def exact_family():
    for n in range(1, 17):
        t, sigma, q, s = F(1, 2), 1 + F(1, 2 * n), n * (n + 1), F(1, 4)
        zroot = F(2 * n + 1, 2)
        require((sigma - t) * (zroot - F(1, 2)) == (sigma - 1) * q,
                'exact turning point')
        require(h_interval(q, s, t, sigma) == point(0), 'exact remainder root')
        require(q + F(1, 2) - zroot == n * n, 'exact net numerator')
        for d in [1, 2, 7, 31]:
            j, rnk = 4 * d, (2 * n + 1) ** 2 * d
            quotient, rem = divmod(rnk, j)
            require(quotient == q and F(rem, j) == s, 'integer attainment')
        rational_power = F(n ** (4 * n), 1) / F(2 * n + 1, 2) ** (4 * n + 2)
        require(0 < rational_power < 1, 'exact family coefficient range')
    require(F(8, 27) ** 2 == 1 / F(3, 2) ** 6, '8/27 exact coefficient')
    require(F(8, 27) < F(1, 2), 'strict predecessor improvement')
    require(candidate_quotients(F(1, 2), F(3, 2))[0] == [2], 'net optimum quotient two')
    return 16, 64

def tensor(histogram):
    out = {}
    for r, nr in histogram.items():
        for s, ns in histogram.items():
            out[r * s] = out.get(r * s, 0) + nr * ns
    return out

def sqrt_exact(n):
    result = iroot(n, 2)
    require(result * result == n, 'fixture requires an integer square root')
    return result

def split_half(n, j):
    q, r = divmod(n, j)
    return q * sqrt_exact(j) + sqrt_exact(r)

def complete_gap():
    targets, paid = tensor({1: 1, 9: 2}), tensor({1: 1, 4: 1})
    j, ell = 4, 9
    raw_t = sum(n * sqrt_exact(r) for r, n in targets.items())
    raw_p = sum(n * sqrt_exact(r) for r, n in paid.items())
    new_t = sum(n * sqrt_exact(max(r, ell)) for r, n in targets.items())
    split_p = sum(n * split_half(r, j) for r, n in paid.items())
    completion_p = sum(n * split_half(ell - r, j) for r, n in targets.items() if r < ell)
    original_tax = split_p - raw_p
    completion_tax = sum(n * (sqrt_exact(r) + split_half(ell - r, j) - 3)
                         for r, n in targets.items() if r < ell)
    new_p = split_p + completion_p
    require((raw_t, raw_p, new_t, new_p, original_tax, completion_tax) ==
            (49, 9, 51, 17, 4, 2), 'literal complete inventory')
    require(new_t - new_p == raw_t - raw_p - original_tax - completion_tax,
            'full net gap identity')
    tax_bound = F(8, 27) * 9 ** 2 / j
    completion_bound = 3 ** 2 * (F(ell, 2) + 1 - 3)
    require(original_tax <= tax_bound and completion_tax <= completion_bound,
            'both retained tax bounds')
    sufficient = (raw_p + tax_bound + completion_bound) / raw_t
    require(sufficient == F(75, 98) < 1, 'full normalized sufficient certificate')
    return dict(targets=targets, paid=paid, final_gap=new_t-new_p,
                split_tax=original_tax, completion_tax=completion_tax,
                complete_sufficient_bound=str(sufficient))

def reject_controls():
    count = 0
    for t, sigma in [(F(0), F(2)), (F(1), F(2)), (F(1, 2), F(1)),
                     (F(1, 2), F(3, 4)), (F(1, 17), F(2)), (F(1, 2), F(5))]:
        try:
            parameters(t, sigma)
        except ValueError:
            count += 1
        else:
            raise ValueError('invalid parameter control accepted')
    require(F(8, 27) > F(1, 4), 'undercharged coefficient control')
    require(F(8, 27) > F(296, 1000), 'decimal down-rounding control')
    q1 = ratio_interval(1, remainder_root(1, F(1, 2), F(3, 2)), F(1, 2), F(3, 2))
    require(q1[1] < F(8, 27), 'q=1-only reduction control')
    require(ratio_interval(256, point(0), F(1, 2), F(3, 4)) == point(F(15, 4)),
            'sigma below one counterexample')
    require(split_half(9, 4) == 5 and split_half(9, 4) - 3 == 2,
            'full versus net charge control')
    require(1 + split_half(8, 4) - 3 > F(9, 2) - 3,
            'dropping positive completion term control')
    require(51 - 13 != 49 - 9 - 4 - 2, 'unpaid completion control')
    for q in [4, 16, 64, 256, 1024]:
        value = ratio_interval(q, point(0), F(1, 2), F(1))
        require(value == point(1 - F(1, sqrt_exact(q))), 'sigma one limit sequence')
    return count + 7

def authenticate():
    manifest = json.loads((ROOT / 'SOURCES.json').read_text(encoding='utf-8'))
    require(manifest['base_commit'] == '7c49fe32c55de02c2c873655c804b16e4c3fef0a', 'base commit pin')
    exports = manifest['exported_documents']
    require(len(exports) == 5, 'source export coverage')
    for row in exports:
        path = ROOT / row['path']
        require(path.is_file() and path.resolve().is_relative_to(ROOT), 'source path')
        data = path.read_bytes()
        require(len(data) <= 100000, 'source size bound')
        git_blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        require(hashlib.sha256(data).hexdigest() == row['sha256'] and
                git_blob == row['git_blob'], 'frozen source hash mismatch')
    return {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(ROOT.rglob('*')) if path.is_file()}

def main():
    sources = authenticate()
    power_cases = power_controls()
    rows, splits, optimized, witnesses = census()
    families, attainments = exact_family()
    gap, rejected = complete_gap(), reject_controls()
    result = dict(marker='PASS_SHARP_NET_SPLITTING_TAX', parameter_pairs=len(rows),
                  literal_splits=splits, optimized_noncandidate_checks=optimized,
                  sharpness_witnesses=witnesses, exact_families=families,
                  integer_attainments=attainments, rational_power_checks=power_cases,
                  rejection_controls=rejected, complete_gap_fixture=gap,
                  coefficient_intervals=rows, source_sha256=sources,
                  scope='Exact finite corroboration; universal theorem is PROOF.md.')
    print(json.dumps(result, sort_keys=True, indent=2))

if __name__ == '__main__':
    main()
