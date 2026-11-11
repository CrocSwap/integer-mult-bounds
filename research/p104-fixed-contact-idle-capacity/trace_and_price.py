"""Independent backward contact trace and rigorous rational rank tariff."""
from bisect import bisect_left, bisect_right
from collections import defaultdict
from fractions import Fraction as F
from functools import cache

K = F(10018846261809, 2500000000000000)


def log_bounds(x):
    z = (x-1)/(x+1)
    partial = 2*sum(z**i/i for i in range(1, 113, 2))
    return partial, partial + 2*z**113/(113*(1-z*z))


def exponential(x):
    term = value = F(1)
    for i in range(1, 37):
        term *= x/i
        value += term
    return value, value+(term*x/37)/(1-x/38)


@cache
def power(rank):
    e = rank.bit_length()-1
    a = log_bounds(F(rank, 2**e))
    b = log_bounds(F(2))
    lo,hi = (K*(x+e*y) for x,y in zip(a,b,strict=True))
    assert 0 <= lo <= hi < 1
    p,q = rank/exponential(hi)[1],rank/exponential(lo)[0]
    grid = 10**50
    return F((p*grid).__floor__(),grid), F((q*grid).__ceil__(),grid)


def backward(caller):
    events = caller["events"]
    # Name each lineage by its final slot, then translate names to initial slots.
    lineage = list(range(caller["roles"]))
    contacts = defaultdict(list)
    idle = []
    for clock in range(len(events)-1,-1,-1):
        e = events[clock]
        if e[0] == "J":
            roles = (*e[2],*e[3][:2])
        else:
            ty,op,a,*args = e
            match op:
                case "SWAP":
                    b = args[0]
                    lineage[a],lineage[b] = lineage[b],lineage[a]
                    continue
                case "IDLE_ONE" | "IDLE_ODD":
                    idle.append((clock,ty,op,a,lineage[a],args[0]))
                    continue
                case "ADD" | "QUERY":
                    roles = (a,args[0])
                case "LAMBDA" | "SCALE":
                    roles = (a,)
                case _:
                    raise ValueError(f"unknown caller contact {op}")
        for slot in roles:
            contacts[lineage[slot]].append(clock)

    initial_name = {token:slot for slot,token in enumerate(lineage)}
    result = []
    for clock,ty,op,slot,token,stages in reversed(idle):
        hits = [-1,*reversed(contacts[token]),len(events)]
        p,q = bisect_left(hits,clock),bisect_right(hits,clock)
        assert p==q
        result.append({"clock":clock,"kind":ty,"slot":slot,
                       "role":initial_name[token],"op":op,
                       "rank":8*len(stages)+int(op=="IDLE_ODD"),
                       "ports":len(caller["types"][ty]["ports"]),
                       "selected_stages":stages,"window":[hits[p-1]+1,hits[q]]})
    return result
