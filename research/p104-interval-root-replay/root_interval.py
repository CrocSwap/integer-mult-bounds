"""Construct an exact root bracket and verify its two signed endpoints.

Interval Newton is standard. The source-bound implementation is by Ali
Romman with OpenAI Codex assistance. Arithmetic engines retain their credit.
Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
import json

GRID = 10**26
UPPER = 10**24
BIT_CAP_GRID = 34*10**22


def need(ok, message):
    if not ok:
        raise ValueError(message)


def margin(E, targets, paid, kappa):
    a,b = E.moment(targets,1-kappa), E.moment(paid,1-kappa)
    return a[0]-b[1], a[1]-b[0]


def derivative(E, signed, low, high, order):
    lower = upper = Q(0)
    for rank,count in signed.items():
        logarithm = E.log_bounds(rank)
        factor = logarithm if order == 1 else E.mul(logarithm,logarithm)
        a = E.mul(E.power(rank,1-high),factor)[0]
        b = E.mul(E.power(rank,1-low),factor)[1]
        coefficient = -count if order == 1 else count
        lower += coefficient*(a if coefficient >= 0 else b)
        upper += coefficient*(b if coefficient >= 0 else a)
    return lower,upper


def checked_bracket(E, targets, paid, record=None):
    if record is None:
        record = json.loads((Path(__file__).parent/'BRACKET.json').read_text())
    low,high = record['lower'],record['upper']
    need(type(low) is int and type(high) is int and record['grid'] == GRID
         and 0 <= low < high <= BIT_CAP_GRID and high-low == 1,'Adjacent source grid bracket')
    a,b = Q(low,GRID),Q(high,GRID)
    need(margin(E,targets,paid,a)[0] > 0,'Strict positive lower endpoint')
    need(margin(E,targets,paid,b)[1] < 0,'Strict negative upper endpoint')
    return a,b


def contract(low, high, value, slope):
    need(low < high and value[0] <= value[1] and slope[0] <= slope[1] < 0,
         'Ordered intervals and strictly negative derivative')
    middle = (low+high)/2
    quotients = [f/d for f in value for d in slope]
    a,b = max(low,middle-max(quotients)), min(high,middle-min(quotients))
    need(a <= b,'Nonempty interval Newton image')
    return (a*GRID).__floor__(), (b*GRID).__ceil__()


def construct(E, targets, paid):
    signed = Counter(targets)
    signed.subtract(paid)
    low,high = 0,UPPER
    global_slope = derivative(E,signed,Q(0),Q(UPPER,GRID),1)
    need(global_slope[1] < 0,'Strictly decreasing complete moment on the initial domain')
    second = derivative(E,signed,Q(0),Q(UPPER,GRID),2)
    curvature = max(map(abs,second))
    need(margin(E,targets,paid,Q(0))[0] > 0 and
         margin(E,targets,paid,Q(UPPER,GRID))[1] < 0,'Initial strict root bracket')
    steps = []
    for _ in range(16):
        a,b = Q(low,GRID),Q(high,GRID)
        middle = (a+b)/2
        value = margin(E,targets,paid,middle)
        point_slope = derivative(E,signed,middle,middle,1)
        radius = curvature*(b-a)/2
        slope = (max(global_slope[0],point_slope[0]-radius),
                 min(global_slope[1],point_slope[1]+radius))
        left,right = contract(a,b,value,slope)
        need(low <= left < right <= high and right-left < high-low,
             'Strict outward grid contraction')
        steps.append({'before':[low,high],'after':[left,right],
                      'moment':list(map(str,value)),'derivative':list(map(str,slope))})
        low,high = left,right
        if high-low == 1:
            break
    else:
        raise ValueError('Root search did not reach adjacent grid points')
    record = {'grid':GRID,'lower':low,'upper':high}
    checked_bracket(E,targets,paid,record)
    return record,{'steps':steps,'global_derivative':list(map(str,global_slope)),
                   'second_derivative':list(map(str,second)),
                   'curvature_majorant':str(curvature)}
