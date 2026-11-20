"""Check fine-prime pages generated with integer interval arithmetic."""

from decimal import Decimal, localcontext
from math import isqrt
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from gaussian_pages import ceil_sqrt, admitted_row, recovery_diagonal, selected_source, width_parameter


def demand(condition, message):
    if not condition:
        raise ValueError(message)


def independent_pi():
    # This comparison uses the arithmetic-geometric mean on Decimal.
    a, b, t, power = Decimal(1), (Decimal(1) / 2).sqrt(), Decimal(1) / 4, Decimal(1)
    for _ in range(8):
        mean = (a + b) / 2
        b = (a * b).sqrt()
        t -= power * (a - mean) ** 2
        a, power = mean, power * 2
    return (a + b) ** 2 / (4 * t)


def audit(p, bits, r, t, fine):
    unit = 1 << bits
    alpha = width_parameter(p)
    window = 8 * alpha * ceil_sqrt(p)
    B = 16 * p * p
    normalizer = 1 << (p**100 - 1).bit_length()
    if fine:
        demand(t <= 4*p*p*(t-r) and 2*p*p*(t-r) < t, 'source outside the fine interval')
        demand(all(r % k for k in range(2, isqrt(r)+1)), 'composite source')
    slots = [(2*t*j+r)//(2*r) for j in range(r)]
    demand(slots == sorted(set(slots)), 'source image collision')
    sources = {slot: j for j, slot in enumerate(slots)}
    broad_cols = [0] * t
    mass_max = left_wrap = right_wrap = aliased = samples = broadened_holes = 0
    with localcontext() as ctx:
        ctx.prec = 82
        pi = independent_pi()
        for v in range(t):
            selected = v in sources
            demand(selected_source(r,t,v) == sources.get(v), 'wrong original coordinate')
            diagonal = recovery_diagonal(p, bits, r, t, v)
            if selected:
                beta = Decimal(t*sources[v]-r*v)/r
                exact_d = (pi*(alpha*beta)**2).exp()*unit
                demand(diagonal <= exact_d <= diagonal+2, 'diagonal interval')
            else:
                demand(diagonal == unit, 'hole diagonal')
            mass = diag = broad_sum = 0
            seen = set()
            emitted = {}
            for col, period, broad, narrow in admitted_row(p,bits,r,t,v,window):
                emitted[col, period] = broad, narrow
                if broad:
                    aliased += col in seen
                    seen.add(col)
                    left_wrap += period < 0
                    right_wrap += period > 0
                    broadened_holes += not selected and col in sources
                broad_cols[col] += broad
                broad_sum += broad
                if col == v:
                    diag += narrow
                else:
                    mass += abs(narrow)
                if col not in sources:
                    demand((col, period, broad, narrow) == (v,0,unit,unit), 'invalid identity column')
                elif not selected:
                    demand(narrow == 0, 'invalid narrow coupling to a hole')
                if col in sources and (not fine or (7*v+col)%113==0):
                    beta = Decimal(t*sources[col]-r*col)/r
                    delta = Decimal(col+period*t-v)+beta
                    exact_b = (-pi*(delta*r/(t*alpha))**2).exp()*unit/alpha
                    demand(broad <= exact_b <= broad+2, 'broad entry interval')
                    if selected and col != v:
                        exact_n = (-pi*alpha**2*(delta**2-beta**2)).exp()*unit
                        demand(narrow <= exact_n <= narrow+2, 'narrow entry interval')
                    samples += 1
            if not fine or v % 31 == 0:
                # Choose the addresses independently of emitted support.
                for off in (-window, -9, -3, 0, 2, 7, window):
                    period, col = divmod(v + off, t)
                    if col not in sources:
                        continue
                    beta = Decimal(t*sources[col]-r*col)/r
                    delta = off + beta
                    broad, narrow = emitted.get((col, period), (0, 0))
                    exact_b = (-pi*(delta*r/(t*alpha))**2).exp()*unit/alpha
                    demand(broad <= exact_b <= broad+2, 'independent address broad interval')
                    if selected and col != v:
                        exact_n = (-pi*alpha**2*(delta**2-beta**2)).exp()*unit
                        demand(narrow <= exact_n <= narrow+2, 'independent address narrow interval')
                    samples += 1
            demand(diag == unit, 'missing principal narrow diagonal')
            demand(unit+B*mass <= B*unit, 'Neumann row gap')
            demand(unit+normalizer*mass <= normalizer*unit, 'normalized row radius')
            demand(broad_sum <= 8*unit, 'broad row bound')
            mass_max = max(mass_max,mass)
    demand(max(broad_cols) <= 8*unit, 'broad column bound')
    demand(min(left_wrap,right_wrap,broadened_holes,samples)>0, 'incomplete physical coverage')
    if not fine:
        demand(aliased>0,'a retained periodic occurrence was lost')
    return r,t,mass_max,left_wrap,right_wrap,aliased,samples


if __name__ == '__main__':
    for target in ((1013,1024,True),(2029,2048,True),(3,4,False)):
        print('r, t, max mass, left/right wrap, repeated slots, independent entries =', audit(6,36,*target))
    try:
        admitted_row(6, 36, 65535, 65536, 32767, 72)
    except ValueError as failure:
        demand(str(failure) == "narrow row fails the inverse bound", "unexpected rejection")
    else:
        raise ValueError("admitted a row with insufficient convergence margin")
    print("PASS_PHYSICAL_GAUSSIAN_ADMISSION")
