"""Certified sparse LU. Ali Romman with Codex assistance. Apache-2.0.

Classical elimination follows the credited native band solver. The exact
residual certificate covers cyclic fill and the larger source row norm.
"""
from dataclasses import dataclass
from fractions import Fraction as Q


def need(ok, message):
    if not ok:
        raise ValueError(message)


def trunc(a, b):
    need(b != 0, 'zero divisor')
    if b < 0:
        a, b = -a, -b
    return (1 if a >= 0 else -1)*(abs(a)//b)


def bounded(value, width):
    need(abs(value) < 1 << width, 'arithmetic word overflow')
    return value


@dataclass(frozen=True)
class Prepared:
    lower: tuple
    upper: tuple
    bits: int
    source_bits: int
    width: int
    radius: int
    target: int
    certificate: tuple
    setup: tuple


def factors(rows, source_bits, bits, width):
    n = len(rows)
    need(n > 0 and type(source_bits) is int and 1 <= source_bits <= bits < width, 'factor dimensions')
    scale = 1 << bits
    a = []
    for i,row in enumerate(rows):
        need(len({j for j,v in row}) == len(row), 'duplicate coefficient')
        need(all(type(j) is int and 0 <= j < n and j != i and type(v) is int and v >= 0
                 for j,v in row), 'coefficient contract')
        a.append({i:scale, **{j:bounded(v << (bits-source_bits),width) for j,v in row if v}})
    columns = [set() for _ in range(n)]
    for i,row in enumerate(a):
        for j in row:
            if i > j:
                columns[j].add(i)
    lower = [{} for _ in range(n)]
    products = divisions = 0
    active = peak = sum(map(len,a))
    for k in range(n):
        pivot = a[k][k]
        need(pivot > 0, 'nonpositive pivot')
        right = sorted((j,v) for j,v in a[k].items() if j > k)
        for i in sorted(columns[k]):
            value = a[i].pop(k)
            active -= 1
            quotient = trunc(bounded(value*scale,width),pivot)
            divisions += 1
            if quotient:
                lower[i][k] = bounded(quotient,width)
                active += 1
            for j,value in right:
                prior = j in a[i]
                new = bounded(a[i].get(j,0)-trunc(bounded(quotient*value,width),scale),width)
                products += 1
                if new:
                    a[i][j] = new
                    active += int(not prior)
                    if i > j:
                        columns[j].add(i)
                else:
                    a[i].pop(j,None)
                    active -= int(prior)
                    if i > j:
                        columns[j].discard(i)
            peak = max(peak,active)
        columns[k].clear()
    l = tuple(tuple(sorted(row.items())) for row in lower)
    u = tuple(tuple(sorted(row.items())) for row in a)
    bill = dict(products=products,divisions=divisions,coefficient_updates=products,
                lower_records=sum(map(len,l)),upper_records=sum(map(len,u)),
                active_factor_coefficient_records_peak=peak)
    return l,u,bill


def certify(rows, source_bits, lower, upper, bits, gap, radius, target):
    """Check every input coefficient in L U using exact integers."""
    n = len(rows)
    need(len(lower) == len(upper) == n and n > 0, 'certificate dimensions')
    need(type(radius) is int and radius >= 1 and type(target) is int and target >= 1,
         'radius/target contract')
    need(0 < gap <= 1 and bits >= source_bits, 'certificate scale/gap')
    scale = 1 << bits
    l = [dict(row) for row in lower]
    u = [dict(row) for row in upper]
    for i in range(n):
        need(len({j for j,v in rows[i]}) == len(rows[i]) and
             all(type(j) is int and 0 <= j < n and j != i and type(v) is int and v >= 0
                 for j,v in rows[i]), 'certificate input contract')
        need(len(l[i]) == len(lower[i]) and len(u[i]) == len(upper[i]), 'duplicate factor entry')
        need(all(type(j) is int and 0 <= j < i and type(v) is int for j,v in lower[i]), 'lower triangular contract')
        need(all(type(j) is int and i <= j < n and type(v) is int for j,v in upper[i]), 'upper triangular contract')
        need(u[i].get(i,0) > 0, 'positive factor diagonal')
        need(sum(v for j,v in rows[i]) <= (1-gap)*(1<<source_bits), 'source row gap')
    defect = products = scratch = 0
    for i in range(n):
        row = {j:v*scale for j,v in u[i].items()}
        for k,a in l[i].items():
            for j,b in u[k].items():
                row[j] = row.get(j,0)+a*b
                products += 1
        row[i] = row.get(i,0)-scale*scale
        for j,v in rows[i]:
            row[j] = row.get(j,0)-(v << (bits-source_bits))*scale
        defect = max(defect,sum(map(abs,row.values())))
        scratch = max(scratch,len(row))
    eta = Q(defect,scale*scale)
    need(eta < gap, 'factor residual consumes inverse margin')
    ln = Q(max(scale+sum(abs(v) for j,v in row) for row in lower),scale)
    un = Q(max(sum(abs(v) for j,v in row) for row in upper),scale)
    ud = Q(max(u[i][i] for i in range(n)),scale)
    h = Q(1,scale)
    rounding = 2*h*(1+ln*ud)
    output_bound = (radius+rounding)/(gap-eta)
    forward_bound = un*(radius+2*h)/(gap-eta)
    coefficient_error = max(map(len,rows),default=0)*Q(1,1<<source_bits)
    error = ((coefficient_error+eta)*output_bound+rounding)/gap+2*Q(1,1<<source_bits)
    need(error <= Q(1,1<<(target+1)), 'complete numerical error budget')
    return dict(factor_residual=eta,lower_norm=ln,upper_norm=un,upper_diagonal=ud,
                output_bound=output_bound,forward_bound=forward_bound,
                coefficient_error=coefficient_error,error_bound=error,
                certificate_products=products,residual_scratch_records=scratch)


def prepare(rows, source_bits, gap, radius=1, target=20, bits=48, width=128):
    lower,upper,bill = factors(rows,source_bits,bits,width)
    certificate = certify(rows,source_bits,lower,upper,bits,gap,radius,target)
    z = certificate['forward_bound']
    y = certificate['output_bound']
    ln = certificate['lower_norm']
    un = certificate['upper_norm']
    word_bound = (1<<(2*bits))*max(radius+(ln-1)*z,z+un*y,radius,z,y,1)
    need(word_bound < 1<<width, 'uniform solve word bound')
    certificate['solve_word_magnitude_bound'] = word_bound
    return Prepared(lower,upper,bits,source_bits,width,radius,target,tuple(certificate.items()),tuple(bill.items()))


def execute(plan, data):
    """Borrow grid input. Use an unchanged Prepared returned by prepare."""
    n = len(plan.lower)
    scale = 1 << plan.bits
    need(type(data) is tuple and len(data) == n and
         all(type(z) is tuple and len(z) == 2 and all(type(v) is int for v in z)
             and abs(z[0])+abs(z[1]) <= plan.radius*(1<<plan.source_bits) for z in data), 'immutable input/radius')
    cert = dict(plan.certificate)
    forward = cert['forward_bound']*scale
    output = cert['output_bound']*scale
    forward_limit = forward.numerator//forward.denominator
    output_limit = output.numerator//output.denominator
    y = []
    x = [(0,0)]*n
    products = divisions = peak = 0
    def word(v):
        nonlocal peak
        peak = max(peak,abs(v).bit_length())
        return bounded(v,plan.width)
    try:
        for i,row in enumerate(plan.lower):
            value = []
            for c in range(2):
                total = word(data[i][c]*(1<<(2*plan.bits-plan.source_bits)))
                for j,a in row:
                    total = word(total-word(a*y[j][c]))
                    products += 1
                value.append(word(trunc(total,scale)))
                divisions += 1
            y.append(tuple(value))
            need(sum(map(abs,value)) <= forward_limit, 'forward range')
        for i in range(n-1,-1,-1):
            row = plan.upper[i]
            diagonal = next(v for j,v in row if j == i)
            value = []
            for c in range(2):
                total = word(y[i][c]*scale)
                for j,a in row:
                    if i != j:
                        total = word(total-word(a*x[j][c]))
                        products += 1
                value.append(word(trunc(total,diagonal)))
                divisions += 1
            x[i] = tuple(value)
            need(sum(map(abs,value)) <= output_limit, 'output range')
        answer = tuple(tuple(trunc(v,1<<(plan.bits-plan.source_bits)) for v in z) for z in x)
        return answer,dict(products=products,component_divisions=divisions+2*n,
                            component_output_truncations=2*n,source_grid_input_scalings=2*n,
                            component_subtractions=products,component_accumulator_loads=4*n,
                            range_bound_divisions=2,range_checks=2*n,
                            component_solution_writes=4*n,output_copy_components=2*n,
                            scratch_clear_components=4*n,scratch_components=4*n,
                            input_components=2*n,output_components=2*n,
                            peak_integer_magnitude_bits=peak)
    finally:
        for i in range(len(y)):
            y[i] = (0,0)
        for i in range(len(x)):
            x[i] = (0,0)
        y.clear()
        x.clear()
