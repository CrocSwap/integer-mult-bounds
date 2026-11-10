#!/usr/bin/env python3
"""Exact composition tests; no production Gaussian/core replay.
Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as F
from pathlib import Path
from itertools import product
import hashlib
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(ok, why):
    if not ok:
        raise ValueError(why)


def eye(n):
    return [[F(i == j) for j in range(n)] for i in range(n)]


def mm(a, b):
    bt = list(zip(*b))
    return [[sum((x*y for x, y in zip(row, col)), F(0))
             for col in bt] for row in a]


def inverse(a):
    n = len(a)
    rows = [r[:] + s for r, s in zip(a, eye(n))]
    for k in range(n):
        pivot = next((j for j in range(k, n) if rows[j][k]), None)
        require(pivot is not None, 'singular matrix')
        rows[k], rows[pivot] = rows[pivot], rows[k]
        v = rows[k][k]
        rows[k] = [x/v for x in rows[k]]
        for i in range(n):
            if i != k and rows[i][k]:
                v = rows[i][k]
                rows[i] = [x-v*y for x, y in zip(rows[i], rows[k])]
    return [r[n:] for r in rows]


def norm(a):
    return max(sum(map(abs, row)) for row in a)


def difference(a, b):
    return [[x-y for x, y in zip(r, s)] for r, s in zip(a, b)]


def polynomial(e, j):
    n = len(e)
    out, power = eye(n), eye(n)
    for _ in range(1, j):
        power = mm(power, e)
        out = [[x+y for x, y in zip(r, s)] for r, s in zip(out, power)]
    return out


def trunc(x, bits):
    q = abs(x.numerator)*(1 << bits)//x.denominator
    return F(q if x >= 0 else -q, 1 << bits)


def prepare(n, length, strip, j, holes, skip_holes):
    """Synthetic rational I+positive band entries, with exact identity holes."""
    h = eye(n)
    selected = [r for r in range(n) if r not in holes]
    for k, r in enumerate(selected):
        for shift in (-1, 1):
            c = selected[(k+shift) % len(selected)] if skip_holes else (r+shift) % n
            if c not in holes:
                h[r][c] += F(1+(r//3 + (shift == 1)) % 3, 65+r % 3)
    e = difference(eye(n), h)
    rho = norm(e)
    delta = 1-rho
    require(0 < rho < 1, 'row-gap admission')
    w = max(min((r-c) % n, (c-r) % n)
            for r in range(n) for c in range(n) if e[r][c])
    band = (j-1)*w
    require(strip > band and length > 4*strip, 'geometry admission')
    require(n % length == 0 and n >= 2*length, 'period/core admission')
    p, inv = polynomial(e, j), inverse(h)
    require(mm(h, inv) == eye(n) and mm(inv, h) == eye(n), 'two-sided inverse oracle')
    require(all(h[r] == eye(n)[r] and all(h[c][r] == F(c == r) for c in range(n))
                for r in holes), 'identity-hole completion')
    tau = rho**j/delta
    a = F(1)
    while a < 1/delta:
        a *= 2
    require(norm(difference(p, inv)) <= tau, 'global tail')
    cmat = [[F(0) for _ in range(n)] for _ in range(n)]
    kept = set()
    local_rows = 0
    wrong_reference_witness = False
    for start in range(0, n, length):
        indices = range(start, start+length)
        hs = [[h[r][c] for c in indices] for r in indices]
        es = difference(eye(length), hs)
        ps, ins = polynomial(es, j), inverse(hs)
        require(norm(difference(ps, ins)) <= tau, 'section tail')
        for r in range(length):
            cmat[start+r][start:start+length] = ins[r]
        for r in range(strip, length-strip):
            row = [F(0)]*n
            row[start:start+length] = ps[r]
            require(row == p[start+r], 'same-reference local path identity')
            require(sum(abs(x-y) for x, y in zip(cmat[start+r], inv[start+r])) <= 2*tau,
                    'kept inverse row comparison')
            kept.add(start+r)
            local_rows += 1
        changed = [row[:] for row in es]
        changed[strip][strip] += F(1, 32)
        wrong = polynomial(changed, j)
        wrong_reference_witness |= wrong[strip] != ps[strip]
    glued = [cmat[r] if r in kept else p[r] for r in range(n)]
    require(norm(difference(glued, inv)) <= 2*tau, 'complete row splice')
    require(wrong_reference_witness, 'wrong-reference control did not distinguish')
    nowrap = [row[:] for row in e]
    for r in range(n):
        for c in range(n):
            if abs(r-c) > w:
                nowrap[r][c] = F(0)
    require(polynomial(nowrap, j) != p, 'period-wrap control did not distinguish')
    first = [[e[r][c] for c in range(length)] for r in range(length)]
    firstp = polynomial(first, j)
    require(firstp[0]+[F(0)]*(n-length) != p[0], 'insufficient-strip control')
    return dict(n=n, length=length, strip=strip, j=j, holes=holes, h=h,
                e=e, p=p, inv=inv, core=cmat, rho=rho, delta=delta,
                tau=tau, a=a, band=band, kept=kept, local_rows=local_rows)


def apply_axis(data, axes, axis, matrix, cbits=None, dbits=None):
    """Full rectangular tensor evaluation, with optional inward rounding."""
    out = {}
    for key in product(*axes):
        value = [F(0), F(0)]
        for c in axes[axis]:
            coeff = matrix[key[axis]][c]
            if cbits is not None:
                coeff = trunc(coeff, cbits)
            old = list(key)
            old[axis] = c
            z = data[tuple(old)]
            value[0] += coeff*z[0]
            value[1] += coeff*z[1]
        out[key] = tuple(trunc(x, dbits) if dbits is not None else x for x in value)
    return out


def divide(a, scalar):
    return [[x/scalar for x in row] for row in a]


def distance(a, b):
    return max(sum(abs(x-y) for x, y in zip(a[k], b[k])) for k in a)


def radius(a):
    return max(sum(map(abs, z)) for z in a.values())


def rectangles(params):
    g = len(params)
    for cores in product(*[range(0, p['n'], p['length']) for p in params]):
        for face in range(g):
            for side in (0, 1):
                outs, ins = [], []
                for axis, (start, p) in enumerate(zip(cores, params)):
                    l, a, b, n = p['length'], p['strip'], p['band'], p['n']
                    if axis < face:
                        lo, hi = start+a, start+l-a
                    elif axis == face:
                        lo, hi = (start, start+a) if side == 0 else (start+l-a, start+l)
                    else:
                        lo, hi = start, start+l
                    outs.append(tuple(x % n for x in range(lo, hi)))
                    ins.append(tuple(x % n for x in range(lo-b, hi+b)))
                require(all(len(set(v)) == len(v) for v in ins), 'ambiguous periodic lift')
                yield tuple(outs), tuple(ins)


def fixture(params, corebits=12, coeffbits=14, databits=13):
    axes = [tuple(range(p['n'])) for p in params]
    original = {key: (F((sum((i+2)*v for i, v in enumerate(key)) % 17)-8, 16),
                      F((sum((i+1)*v for i, v in enumerate(key)) % 11)-5, 32))
                for key in product(*axes)}
    require(radius(original) <= 1, 'input radius')
    saved, output_keys = [], []
    for outs, ins in rectangles(params):
        saved.append((outs, ins, {k: original[k] for k in product(*ins)}))
        output_keys.extend(product(*outs))
    require(len(output_keys) == len(set(output_keys)), 'duplicate returned output')
    discarded = {k for k in original if any(k[i] not in p['kept'] for i, p in enumerate(params))}
    require(set(output_keys) == discarded, 'first-boundary partition')
    expected, core, exact_core = original, original, original
    core_errors = []
    for i, p in enumerate(params):
        require(radius(core) <= 2, 'actual admitted input radius')
        expected = apply_axis(expected, axes, i, divide(p['inv'], p['a']))
        exact_core = apply_axis(exact_core, axes, i, divide(p['core'], p['a']))
        # Admitted nonlinear oracle test-double, NOT #4205 execution.
        core = apply_axis(core, axes, i, p['core'], dbits=corebits)
        core = {k: tuple(z/p['a'] for z in v) for k, v in core.items()}
        core_errors.append(F(2, 2**corebits)/p['a'])
        require(radius(core) <= 1+sum(core_errors), 'actual core radius induction')
        require(distance(core, exact_core) <= sum(core_errors), 'actual nonlinear core accumulated error')
    out, stale = dict(core), dict(core)
    copies = 0
    eta = sum(F(min(p['n'], 2*p['band']+1), 2**coeffbits)+F(2, 2**databits) for p in params)
    rounded_coefficients = 0
    for p in params:
        normalized = divide(p['p'], p['a'])
        rounded = [[trunc(c, coeffbits) for c in row] for row in normalized]
        rounded_coefficients += sum(x != y for r, s in zip(normalized, rounded) for x, y in zip(r, s))
        require(norm(rounded) <= norm(normalized) <= 1, 'inward coefficient norm')
    require(rounded_coefficients > 0, 'coefficient-rounding fixture is vacuous')
    for outs, ins, data in saved:
        copies += len(data)
        bad = {k: core[k] for k in product(*ins)}
        for i, p in enumerate(params):
            mat = divide(p['p'], p['a'])
            data = apply_axis(data, ins, i, mat, coeffbits, databits)
            bad = apply_axis(bad, ins, i, mat, coeffbits, databits)
            require(radius(data) <= 1, 'halo inward radius')
        for k in product(*outs):
            out[k], stale[k] = data[k], bad[k]
    tail = sum(p['tau']/p['a'] for p in params)
    bound = max(sum(core_errors)+2*tail, eta+tail)
    require(distance(out, expected) <= bound, 'rounded complete splice theorem')
    require(distance(stale, expected) > bound, 'stale-input control did not exceed true-output error budget')
    direct = original
    for i, p in enumerate(params):
        direct = apply_axis(direct, axes, i, divide(p['p'], p['a']))
    crop_witness = False
    for outs, ins, data in saved:
        cropped = dict(data)
        for i, p in enumerate(params):
            data = apply_axis(data, ins, i, divide(p['p'], p['a']))
            if i == 0:
                cropped = apply_axis(cropped, ins, i, divide(p['p'], p['a']))
                cropped = {k: cropped[k] for k in product(*outs)}
            else:
                cropped = apply_axis(cropped, outs, i, divide(p['p'], p['a']))
        require(all(data[k] == direct[k] for k in product(*outs)), 'sparse rectangle tensor endpoint')
        crop_witness |= any(cropped[k] != direct[k] for k in product(*outs))
    require(len(params) == 1 or crop_witness, 'premature intermediate crop control')
    require(trunc(F(3, 2**(corebits+2)), corebits)*2 !=
            trunc(F(6, 2**(corebits+2)), corebits), 'nonlinear core control')
    return dict(axes=[p['n'] for p in params], outputs=len(out), copies=copies,
                discarded=len(discarded), core_rows=sum(p['local_rows'] for p in params),
                rounded_coefficients=rounded_coefficients,
                core_rounding_error=str(distance(core, exact_core)),
                bound=str(bound), observed_error=str(distance(out, expected)),
                stale_error=str(distance(stale, expected)))


def authenticate():
    sources = json.loads((HERE/'SOURCES.json').read_text())
    count = 0
    for row in sources['files']:
        if row['usage'] == 'input':
            raw = (ROOT/row['path']).read_bytes()
            require(hashlib.sha256(raw).hexdigest() == row['sha256'], 'source bytes: '+row['path'])
            count += 1
    return count


def domain_control():
    # H=I and a=1: a legal nonlinear error need not shrink the input radius.
    eps = F(1, 16)
    def core(x, admitted):
        require(abs(x) <= admitted, 'actual oracle input outside admitted radius')
        return x + (eps if x >= 0 else -eps)
    first = core(F(1), F(2))
    rejected = False
    try:
        core(first, F(1))
    except ValueError:
        rejected = True
    require(rejected, 'ideal-only radius was not rejected')
    second = core(first, F(2))
    require(first > 1 and second-1 == 2*eps and second <= 2, 'rounded radius induction control')
    return str(second)


def recovery_controls():
    s, b, e, v, r = 15, 4, F(1, 2**24), F(1, 2**28), F(1, 4)
    scale = s*s*2**(2*b+4)
    budget = scale*((2*r+1)*e+e*e+v)
    require(budget < F(1, 2), 'positive recovery guard')
    require(scale*(F(1, 2)/scale) == F(1, 2), 'strict boundary fixture')
    require(abs(F(7, 2)-3) == abs(F(7, 2)-4), 'half-unit ambiguity')
    omitted = scale/s*((2*r+1)*F(1, 2**20)+F(1, 2**40)+v)
    full = scale*((2*r+1)*F(1, 2**20)+F(1, 2**40)+v)
    require(omitted < F(1, 2) <= full, 'missing-S control')
    require((r+e)**2-r*r == 2*r*e+e*e, 'product cross-error identity')
    require(F(1, 16) < F(1, 2) <= 16*F(1, 16), 'unpaid normalizer control')
    # A unit-modulus rational phase expands component-l1, but not modulus.
    require(abs(F(3, 5))+abs(F(4, 5)) > 1 and F(3, 5)**2+F(4, 5)**2 == 1,
            'component-l1 Fourier norm-seam control')
    return str(budget)


def main():
    pins = authenticate()
    p = prepare(32, 16, 3, 2, {5, 19}, True)
    q = prepare(24, 12, 2, 2, {5, 14}, False)
    r = prepare(32, 16, 3, 3, {5, 19}, False)
    cases = [fixture([p]), fixture([r]), fixture([q, q]), fixture([q, p])]
    receipt = dict(schema_version=1, status='PASS_ROUNDED_CORE_HALO_SPLICE',
                   source_pins=pins, fixtures=cases, recovery_guard=recovery_controls(),
                   radius_control_final=domain_control(),
                   controls=['wrong_reference', 'missing_period_wrap', 'insufficient_strip',
                             'stale_post_core_inputs', 'nonlinear_core', 'half_unit_tie',
                             'missing_recovery_S', 'product_cross_term', 'premature_intermediate_crop',
                             'ideal_only_input_radius', 'unpaid_normalizer', 'complex_norm_seam'],
                   production_core_replayed=False, selected_frontier_changed=False)
    output = json.dumps(receipt, indent=2, sort_keys=True)+'\n'
    if sys.argv[1:] == ['--write-receipt']:
        (HERE/'RESULT.json').write_text(output)
    else:
        require(not sys.argv[1:], 'unknown arguments')
        require((HERE/'RESULT.json').read_text() == output, 'mandatory exact result receipt')
    print(output, end='')


if __name__ == '__main__':
    main()
