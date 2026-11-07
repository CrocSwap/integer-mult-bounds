"""Exact mixed-mask root model and paid interval capacity.

CubeJerry, with substantial OpenAI GPT-6 Astra Pro assistance. Apache-2.0.
Root vectors/native counts are imported from byte-pinned #6833 sources.
"""
from collections import Counter
from decimal import Decimal, localcontext
from fractions import Fraction as Q
from functools import lru_cache
from pathlib import Path
import ast
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / 'retained'))
import chain_root as cr
from algebra import eye, inverse, multiply, need

C = Q('.0033718004755')
SHAPE = ([1] * 9, [1] * 9)


def rank(rows):
    a = [[Q(x) for x in row] for row in rows]
    if not a or not a[0]:
        return 0
    r = 0
    for col in range(len(a[0])):
        pivot = next((j for j in range(r, len(a)) if a[j][col]), None)
        if pivot is None:
            continue
        a[r], a[pivot] = a[pivot], a[r]
        d = a[r][col]
        a[r] = [x / d for x in a[r]]
        for j in range(r + 1, len(a)):
            d = a[j][col]
            if d:
                a[j] = [x - d*y for x, y in zip(a[j], a[r])]
        r += 1
        if r == len(a):
            break
    return r


def outer(x, y):
    return [[a*b for b in y] for a in x]


def dot(x, y):
    return sum(a*b for a, b in zip(x, y))


def source_profile():
    parsed = ast.parse((HERE/'retained/pricing.py').read_text())
    found = {}
    for node in parsed.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in ('HELPERS', 'LOCAL_PAID'):
                    found[target.id] = Counter(ast.literal_eval(node.value))
    need(set(found) == {'HELPERS', 'LOCAL_PAID'}, 'Pinned native invoice is complete')
    return found['HELPERS'], found['LOCAL_PAID']


def root_model(p, q):
    need(0 <= p <= 8 and 0 <= q <= 8, 'Declared crossing parameters')
    sites = cr.sites(*SHAPE)
    fields = cr.fields(*SHAPE)
    masks, indices = [], []
    for k, (_, _, mask, side, j) in enumerate(sites):
        if mask is None:
            continue
        mask = set(mask)
        if side == 'L' and j >= p:
            mask.update(fields['h'][9-q:])
        if side == 'R' and j < 9-q:
            mask.update(fields['f'][:p])
        masks.append(mask)
        indices.append(k)
    return sites, fields, masks, indices


def capacities(p, q):
    sites, fields, masks, indices = root_model(p, q)
    intervals = [(a, b) for a in range(18) for b in range(a, 18)]
    caps = []
    for a, b in intervals:
        support = sorted(set.intersection(*masks[a:b+1]))
        qs = range(indices[a], indices[b]+1)
        y = [[sites[k][1][f] for f in support] for k in qs]
        x = [[sites[k][0][f] for k in qs] for f in support]
        yx = multiply(y, x) if support else []
        cap = len(support)-rank(y)-rank(x)+rank(yx)
        need(cap >= 0, 'Nonnegative exact pairing rank')
        caps.append(cap)
    targets = Counter(1+8*sum(f in mask for mask in masks) for f in range(fields['n']))
    demands = [len(mask)-2 for mask in masks]
    return intervals, caps, demands, targets


def verify_stage_contract(p, q):
    sites, fields, masks, indices = root_model(p, q)
    n = fields['n']
    prefix = eye(n)
    lookup = dict(zip(indices, masks))
    for i, (x, y, _, _, _) in enumerate(sites):
        need(dot(y, x) == 0, 'Square-zero normalized query')
        need(all(dot(y, sj[0]) == (i > j)-(i < j) for j, sj in enumerate(sites)),
             'Exact source sign Gram')
        yp = [sum(y[k]*prefix[k][j] for k in range(n)) for j in range(n)]
        prefix = [[prefix[a][b]-2*x[a]*yp[b] for b in range(n)] for a in range(n)]
        if i in lookup:
            mask = lookup[i]
            need(all(not x[f] or f in mask for f in range(n)), 'Column in stage support')
            need(all(not y[f] or f in mask for f in range(n)), 'Row in stage support')
            need(all(not prefix[a][b] for a in range(n) for b in range(n)
                     if (a in mask) != (b in mask)), 'Stage projector commutes with prefix')
    need(prefix == [[-int(a == b) for b in range(n)] for a in range(n)], 'Full endpoint is -I')
    return {'fields': n, 'full_sites': 18, 'thin_queries': len(sites)-18,
            'arbitrary_input_identity': 'S I times the coordinate product of all 18 stage masks'}


def explicit_jobs():
    _, F, _, _ = root_model(1, 2)
    n, A, f, h = F['n'], F['A'], F['f'], F['h']
    v = lambda *pairs: cr.vector(n, *pairs)
    jobs = [
        ('cross_1', v((f[0], 1), (h[8], 1)),
         v((A, 2), (f[0], -1), (h[7], -1), (h[8], 2)), 1, 15),
        ('cross_2', v((f[0], -1), (h[7], 1)),
         v((A, 2), (f[0], -1), (h[8], 1)), 1, 15),
        ('left_remainder', v((f[0], 1), (h[7], 1), (h[8], 1)),
         v((A, -2), (f[0], 1), (h[7], 1), (h[8], -1)), 1, 8),
        ('right_remainder', v((f[0], 1), (h[7], 1), (h[8], 1)),
         v((f[0], 1), (h[7], 1), (h[8], -1)), 9, 15),
        ('right_boundary', v((h[8], 1)), v((A, 2), (h[8], 1)), 16, 16),
    ]
    for j in range(1, 8):
        jobs.append((f'left_{j}', v((f[j], 1)), v((f[j], 1), (A, -2)), j+1, 8))
    for j in range(1, 7):
        jobs.append((f'right_{j}', v((h[j], 1)), v((h[j], 1), (A, 2)), 9, 9+j-1))
    return jobs


def verify_jobs(jobs):
    sites, fields, masks, indices = root_model(1, 2)
    n = fields['n']
    for name, phi, gamma, a, b in jobs:
        need(dot(gamma, phi) == 1, f'{name}: unit dual pair')
        for i in range(a, b+1):
            need(all(not phi[f] or f in masks[i] for f in range(n)), f'{name}: column support')
            need(all(not gamma[f] or f in masks[i] for f in range(n)), f'{name}: row support')
        for k in range(indices[a], indices[b]+1):
            x, y = sites[k][:2]
            need(dot(y, phi) == dot(gamma, x) == 0, f'{name}: actual query conjugation')
    height = 0
    for i, mask in enumerate(masks):
        x, y = sites[indices[i]][:2]
        active_jobs = [job for job in jobs if job[3] <= i <= job[4]]
        need(len(active_jobs) == len(mask)-2, 'Every idle dimension is paid')
        for j, (_, phi, gamma, _, _) in enumerate(active_jobs):
            for k, (_, phi2, _, _, _) in enumerate(active_jobs):
                need(dot(gamma, phi2) == int(j == k), 'Simultaneous dual orthogonality')
        projector = [[Q(int(a == b and a in mask)) for b in range(n)] for a in range(n)]
        active = [[projector[a][b]-sum(job[1][a]*job[2][b] for job in active_jobs)
                   for b in range(n)] for a in range(n)]
        need(multiply(active, active) == active, 'Native active projector is idempotent')
        need(rank(active) == 2, 'Native active plane has rank two')
        need([dot(row, x) for row in active] == x, 'Active plane fixes native column')
        need([sum(y[a]*active[a][b] for a in range(n)) for b in range(n)] == y,
             'Active plane fixes native row')
        w = [row[fields['A']] for row in active]
        columns = [x, w]+[job[1] for job in active_jobs]
        columns += [[Q(int(j == f)) for j in range(n)] for f in range(n) if f not in mask]
        basis = [list(row) for row in zip(*columns)]
        ib = inverse(basis)
        need(all(z.denominator == 1 for row in ib for z in row), 'Integral ordinary interface inverse')
        need(dot(y, w) == 1, 'Standard native nilpotent interface')
        height = max(height, max(abs(z.numerator).bit_length() for row in basis+ib for z in row))
    paid = Counter(8*(job[4]-job[3]+1) for job in jobs)
    paid[1] += 3
    return paid, {'whole_idle_jobs': len(jobs), 'crossing_jobs': 2,
                  'native_basis_integer_bit_length': height, 'checked_native_planes': 18}


def ln_bounds(r, terms=20):
    if r == 1:
        return Q(0), Q(0)
    k = r.bit_length()-1
    def atanh_log(a):
        z = (a-1)/(a+1)
        total = 2*sum(z**(2*j+1)/Q(2*j+1) for j in range(terms))
        tail = 2*z**(2*terms+1)/((2*terms+1)*(1-z*z))
        return total, total+tail
    l2, u2 = atanh_log(Q(2))
    lr, ur = atanh_log(Q(r, 2**k))
    return k*l2+lr, k*u2+ur


@lru_cache(None)
def power_bounds(r):
    """Exact rational enclosure of r**(1-C), using alternating exp(-a)."""
    if r == 0:
        return Q(0), Q(0)
    lo, hi = ln_bounds(r)
    alo, ahi = C*lo, C*hi
    need(0 <= alo <= ahi < 1, 'Alternating exponential domain')
    def partial(a, last):
        term = Q(1)
        total = term
        for j in range(1, last+1):
            term *= -a/j
            total += term
        return total
    return r*partial(ahi, 9), r*partial(alo, 10)


def moment_bounds(hist):
    lo = hi = Q(0)
    for r, count in hist.items():
        a, b = power_bounds(r)
        if count >= 0:
            lo += count*a
            hi += count*b
        else:
            lo += count*b
            hi += count*a
    return lo, hi


def complete_bounds(targets, paid):
    helpers, local = source_profile()
    hist = Counter({r: 18*n for r, n in helpers.items()})
    for r, count in local.items():
        hist[r] -= 18*count
    for r, count in targets.items():
        hist[r] += 104*count
    for r, count in paid.items():
        hist[r] -= 104*count
    return moment_bounds(hist)


def decimal(q, places=16):
    with localcontext() as ctx:
        ctx.prec = places+12
        return str(Decimal(q.numerator)/Decimal(q.denominator))
