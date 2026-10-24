#!/usr/bin/env python3
"""Independent fixed-inventory arithmetic for source PR5405 equation (1).

Standard library only. Integer directed arithmetic; no imported interval engine.
Written for this independent check with substantial OpenAI Codex assistance.
Apache-2.0. See PROOF.md for derivation, scope, remainder proofs and credit.
"""
from __future__ import annotations
import argparse
import ast
from collections import Counter
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import platform
import resource
import re
import signal
import sys
import time

BITS = 256
Q = 1 << BITS
LOG_TERMS = 128
EXP_TERMS = 64
P = {1: 2193, 2: 412, 3: 510, 4: 127, 5: 40}
H = {4: 28, 7: 7, 8: 47, 9: 318}
KAPPA = Fraction(12109153, 4000000000)  # .00302728825, exact
ROOT = Path(__file__).resolve().parent

def ceildiv(a, b):
    return -((-a) // b)

def frac_up(x):
    return ceildiv(x.numerator * Q, x.denominator)

def frac_down(x):
    return x.numerator * Q // x.denominator

def plus(a, b):
    return a[0] + b[0], a[1] + b[1]

def neg(a):
    return -a[1], -a[0]

def minus(a, b):
    return plus(a, neg(b))

def scale(a, k):
    return (a[0] * k, a[1] * k) if k >= 0 else (a[1] * k, a[0] * k)

def positive_mul(a, b):
    assert a[0] >= 0 and b[0] >= 0
    return a[0] * b[0] // Q, ceildiv(a[1] * b[1], Q)

def constant(n):
    return n * Q, n * Q

def log_unit_interval(y):
    """ln(y) for exact 1<=y<=2 via 2 atanh((y-1)/(y+1))."""
    assert 1 <= y <= 2
    z = (y - 1) / (y + 1)
    zz = z * z
    z_iv = frac_down(z), frac_up(z)
    zz_iv = frac_down(zz), frac_up(zz)
    term = z_iv
    total = (0, 0)
    for j in range(LOG_TERMS):
        d = 2 * j + 1
        total = plus(total, (term[0] // d, ceildiv(term[1], d)))
        term = positive_mul(term, zz_iv)
    # All omitted terms positive, denominators >=2N+1:
    # R <=2*z^(2N+1)/((2N+1)*(1-z^2)).
    tail = 2 * z ** (2 * LOG_TERMS + 1) / ((2 * LOG_TERMS + 1) * (1 - zz))
    return 2 * total[0], 2 * total[1] + frac_up(tail)

LOG2 = log_unit_interval(Fraction(2))

def log_integer(r):
    assert isinstance(r, int) and r >= 1
    if r == 1:
        return 0, 0
    m = r.bit_length() - 1
    return plus(scale(LOG2, m), log_unit_interval(Fraction(r, 1 << m)))

def exp_positive(x):
    """exp(x) for 0<=x<=1; directed Taylor and exact geometric tail."""
    assert 0 <= x[0] <= x[1] <= Q
    term = (Q, Q)
    total = term
    for k in range(1, EXP_TERMS + 1):
        # Bounds for x^k/k!; all factors nonnegative.
        prod = positive_mul(term, x)
        term = prod[0] // k, ceildiv(prod[1], k)
        total = plus(total, term)
    upper_x = Fraction(x[1], Q)
    # First omitted term bounds remainder with subsequent ratios <=x/(N+2).
    first = upper_x ** (EXP_TERMS + 1)
    for k in range(1, EXP_TERMS + 2):
        first /= k
    tail = first / (1 - upper_x / (EXP_TERMS + 2))
    return total[0], total[1] + frac_up(tail)

class Powers:
    def __init__(self, kappa=KAPPA):
        assert 0 < kappa < 1
        self.kappa = kappa
        self.cache = {0: (0, 0), 1: (Q, Q)}

    def __call__(self, r):
        if r not in self.cache:
            log = log_integer(r)
            num, den = self.kappa.numerator, self.kappa.denominator
            x = log[0] * num // den, ceildiv(log[1] * num, den)
            ex = exp_positive(x)
            reciprocal = Q * Q // ex[1], ceildiv(Q * Q, ex[0])
            self.cache[r] = scale(reciprocal, r)
        return self.cache[r]

def moment(hist, f):
    total = (0, 0)
    for r, count in sorted(hist.items()):
        total = plus(total, scale(f(r), count))
    return total

def local(f):
    return minus(moment(P, f), moment(H, f))

def delta(r, f):
    return minus(f(r + 1), f(r))

def canonical_parts(n):
    assert n >= 0
    if n <= 2:
        return 1, 0, 0
    a = (n - 3) // 2
    b = n - 3 - a
    return n - 2, a, b

def canonical_mask(n):
    p, a, b = canonical_parts(n)
    x = [0] * (2 * p + 1)
    if n <= 2:
        for i in range(n):
            x[i] = 1
    else:
        x[0] = x[2 * p] = x[2 * a + 1] = 1
        for j in range(1, a + 1):
            x[2 * j - 1] = 1
        for j in range(1, b + 1):
            x[2 * p - 2 * j + 1] = 1
    assert sum(x) == n
    return p, a, x

def invoice_histograms(p, a, x):
    """Reconstruct paid/target lists from Eq1's individual invoice items."""
    assert p >= 1 and 0 <= a < p and len(x) == 2 * p + 1 and set(x) <= {0, 1}
    n = sum(x)
    paid = Counter({r: n * count for r, count in P.items()})
    target = Counter({r: n * count for r, count in H.items()})
    paid[1] += 112 * (2 * p + 1 - n)
    target[1 + 8 * n] += 224
    for j in range(1, p):
        h = sum(x[:2*j]) if j <= a else sum(x[2*j+1:])
        e = x[2*j]
        if h:
            paid[8 * h] += 224
        if e:
            paid[8] += 224
        target[1 + 8 * (h + e)] += 224
    return +paid, +target

def clean_signed(c):
    return {r: count for r, count in sorted(c.items()) if count}

def signed_histograms(paid, target):
    c = Counter(paid)
    c.subtract(target)
    return clean_signed(c)

def equation_one_coefficients(p, a, x):
    """Literal Eq1 expanded as integer coefficients of independent f(r)."""
    n = sum(x)
    c = Counter({1:112*(2*p+1)-112*n})
    for r, count in P.items(): c[r] += n*count
    for r, count in H.items(): c[r] -= n*count
    c[1+8*n] -= 224
    for j in range(1,p):
        h = sum(x[:2*j]) if j<=a else sum(x[2*j+1:])
        e = x[2*j]
        if h: c[8*h] +=224
        c[8] +=224*e
        c[1+8*(h+e)] -=224
    return clean_signed(c)

def canonical_coefficients(n):
    """Closed formula expanded symbolically; no interval overlap acceptance."""
    c = Counter()
    for r,count in P.items(): c[r] += n*count
    for r,count in H.items(): c[r] -= n*count
    c[1] +=336-112*n if n<=2 else 112*(n-3)
    c[1+8*n] -=224
    if n>=3:
        _,a,b=canonical_parts(n)
        for q in (a,b):
            for k in range(2,q+2):
                c[8*k+1]-=224
                c[8*k]+=224
    return clean_signed(c)

def equation_one(p, a, x, f):
    n = sum(x)
    val = plus(constant(112 * (2*p+1)), scale(minus(local(f), constant(112)), n))
    val = minus(val, scale(f(1+8*n), 224))
    for j in range(1, p):
        h = sum(x[:2*j]) if j <= a else sum(x[2*j+1:])
        e = x[2*j]
        g = minus(plus(f(8*h), scale(f(8), e)), f(1+8*(h+e)))
        val = plus(val, scale(g, 224))
    return val

def canonical(n, f):
    if n <= 2:
        return minus(plus(constant(336), scale(minus(local(f), constant(112)), n)), scale(f(1+8*n), 224))
    p, a, b = canonical_parts(n)
    val = minus(plus(scale(local(f), n), constant(112*(n-3))), scale(f(1+8*n), 224))
    for q in (a, b):
        for k in range(2, q+2):
            val = minus(val, scale(delta(8*k, f), 224))
    return val

def overlap(a, b):
    return a[0] <= b[1] and b[0] <= a[1]

def exact_grid_text(n, digits=40):
    sign = '-' if n < 0 else ''
    a = abs(n)
    whole, remain = divmod(a, Q)
    return sign + str(whole) + '.' + str(remain * (10**digits) // Q).zfill(digits)

def packed(iv):
    # Decimal strings are display only, exact integer/Q endpoints certify signs.
    return dict(lower_integer=str(iv[0]), upper_integer=str(iv[1]), denominator=str(Q),
                lower_decimal_truncated=exact_grid_text(iv[0]), upper_decimal_truncated=exact_grid_text(iv[1]),
                width_grid_units=str(iv[1]-iv[0]))

def authenticate(data, expected):
    if sha256(data).hexdigest() != expected:
        raise ValueError('source hash mismatch')

def validate_profile(p,h,source):
    source_p=ast.literal_eval(re.search(r'paid P = (\{[^\n]+\})',source).group(1))
    source_h=ast.literal_eval(re.search(r'helper targets H = (\{[^\n]+\})',source).group(1))
    if p!=source_p or h!=source_h:
        raise ValueError('profile differs from authenticated source')

def gate(c18,d17,d18):
    return c18[0]>0 and d17[1]<0 and d18[0]>0

def verify_sources():
    manifest = json.loads((ROOT/'SOURCE-MANIFEST.json').read_text())
    for row in manifest['inputs']:
        authenticate((ROOT/row['frozen']).read_bytes(), row['sha256'])
    source = (ROOT/'inputs/5405-PROOF.md').read_text()
    assert 'paid P = {1:2193, 2:412, 3:510, 4:127, 5:40}' in source
    assert 'helper targets H = {4:28, 7:7, 8:47, 9:318}' in source
    validate_profile(P,H,source)
    for row in json.loads((ROOT/'THEORY-MANIFEST.json').read_text()):
        authenticate((ROOT/row['frozen']).read_bytes(), row['sha256'])
    return manifest

def run():
    start = time.monotonic()
    manifest = verify_sources()
    f = Powers()
    values = {n: canonical(n, f) for n in range(16, 21)}
    # Recompute differences in both literal canonical expression and the short formula.
    differences = {n: minus(values[n+1], values[n]) for n in range(16, 20)}
    neighbor_short = {}
    for n in (17, 18):
        # Independently: newly added full stage contributes L+112; rank main
        # grows by 8, and one side sum gains delta at 8*floor((n+1)/2).
        cost = plus(minus(f(1+8*(n+1)), f(1+8*n)), delta(8*((n+1)//2), f))
        neighbor_short[n] = minus(plus(local(f), constant(112)), scale(cost, 224))
        assert overlap(differences[n], neighbor_short[n])
    assert gate(values[18],differences[17],differences[18])
    hist_checks = []
    for n in list(range(0, 6)) + list(range(16, 21)):
        p, a, mask = canonical_mask(n)
        paid, target = invoice_histograms(p, a, mask)
        assert signed_histograms(paid,target)==equation_one_coefficients(p,a,mask)==canonical_coefficients(n)
        direct = minus(moment(paid, f), moment(target, f))
        eq1 = equation_one(p, a, mask, f)
        assert overlap(direct, eq1) and overlap(direct, canonical(n, f))
        hist_checks.append(dict(n=n, p=p, a=a, mask=''.join(map(str,mask)),
                                paid=dict(sorted(paid.items())), target=dict(sorted(target.items())),
                                direct=packed(direct), equation_one=packed(eq1),symbolic_identity=True))
    # Small exhaustive identity control checks the prefix/suffix index branches,
    # with affine counts compared symbolically. It is not an all-mask proof.
    tiny_identity_count=0
    for p in range(1,4):
        for a in range(p):
            for bits in range(1<<(2*p+1)):
                x=[(bits>>i)&1 for i in range(2*p+1)]
                paid,target=invoice_histograms(p,a,x)
                assert signed_histograms(paid,target)==equation_one_coefficients(p,a,x)
                tiny_identity_count+=1
    controls=[]
    # Source mutation must be caught before accepting any arithmetic.
    src=(ROOT/'inputs/5405-PROOF.md').read_bytes()
    try:
        authenticate(src+b'\nMUTANT\n', manifest['inputs'][0]['sha256'])
    except ValueError:
        controls.append(dict(name='changed_source_bytes',expected='rejected',observed='rejected'))
    else:
        raise AssertionError('source mutant survived')
    reversed_sign=neg(values[18])
    assert reversed_sign[1] < 0 and not gate(neg(values[18]),neg(differences[17]),neg(differences[18]))
    controls.append(dict(name='reverse_paid_minus_target_sign',expected='positive_certificate_fails',
                         observed='fails',interval=packed(reversed_sign)))
    p,a,x=canonical_mask(18)
    paid,target=invoice_histograms(p,a,x)
    # Dropping one query invoice is a concrete 112-rank-one omission.
    mutant=paid.copy(); mutant[1]-=112
    mutant_val=minus(moment(mutant,f),moment(target,f))
    assert signed_histograms(mutant,target)!=equation_one_coefficients(p,a,x)
    assert not overlap(mutant_val,equation_one(p,a,x,f)) and mutant_val[1]<0
    controls.append(dict(name='omit_one_112_rank_one_query',expected='invoice_identity_fails_and_sign_negative',
                         observed='fails_as_expected',interval=packed(mutant_val)))
    mutant_target=target.copy(); mutant_target[145]-=224
    mutant_main=minus(moment(paid,f),moment(mutant_target,f))
    assert signed_histograms(paid,mutant_target)!=equation_one_coefficients(p,a,x)
    assert not overlap(mutant_main,equation_one(p,a,x,f))
    controls.append(dict(name='omit_224_full_path_targets',expected='invoice_identity_fails',
                         observed='fails_as_expected',interval=packed(mutant_main)))
    changed_profile = dict(P); changed_profile[4] -= 1
    try:
        validate_profile(changed_profile,H,src.decode())
    except ValueError:
        controls.append(dict(name='alter_paid_profile_count',expected='profile_pin_fails',observed='fails_as_expected'))
    else:
        raise AssertionError('profile mutant survived')
    return dict(status='PASS_SCOPED_ARITHMETIC', source_head=manifest['source_head'],
                canonical_main=manifest['canonical_main'],
                exponent=dict(kappa=str(KAPPA),t=str(1-KAPPA)),
                arithmetic=dict(bits=BITS,log_terms=LOG_TERMS,exp_terms=EXP_TERMS,
                                floating_point_used_for_acceptance=False),
                local_moment=packed(local(f)), values={str(n):packed(v) for n,v in values.items()},
                differences={str(n)+'_to_'+str(n+1):packed(v) for n,v in differences.items()},
                short_difference_crosschecks={str(n):packed(v) for n,v in neighbor_short.items()},
                canonical_histogram_checks=hist_checks,tiny_symbolic_identity_count=tiny_identity_count,
                negative_controls=controls,
                power_enclosures={str(r):packed(v) for r,v in sorted(f.cache.items())},
                environment=dict(python=sys.version,platform=platform.platform(),
                                 elapsed_seconds=time.monotonic()-start,
                                 maximum_resident_set_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss),
                excluded=['author interval engine','author 10290000-state DP','native replay','Lean',
                          'physical circuit admission','global circuit optimum','kappa gain','changed-profile PR5402'])

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--receipt',type=Path,required=True)
    args=parser.parse_args()
    # Local cap applies even when called without an external runner.
    resource.setrlimit(resource.RLIMIT_AS,(256*1024*1024,256*1024*1024))
    signal.alarm(60)
    try:
        result=run()
    except Exception as exc:
        result=dict(status='FAIL',error_type=type(exc).__name__,error=str(exc))
        with args.receipt.open('x') as out:
            json.dump(result,out,indent=2);out.write('\n')
        raise
    with args.receipt.open('x') as out:
        json.dump(result,out,indent=2);out.write('\n')
    print(json.dumps({k:result[k] for k in ('status','values','differences','environment')},indent=2))

if __name__=='__main__':
    main()
