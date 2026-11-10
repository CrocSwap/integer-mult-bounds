"""Independent finite full-coordinate product replay, without an odometer cache.
Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
This exact-integer observer is not the physical program or its complexity proof.
"""
from math import prod


def need(ok,message):
    if not ok:raise ValueError(message)


def truncate(value,precision):
    return (-1 if value<0 else 1)*(abs(value)>>precision)


def multiply(left,right,precision):
    a,b=left;c,d=right
    return (truncate(a*c-b*d,precision),truncate(a*d+b*c,precision))


def action(values,radices,tables,precision,conjugate=False):
    need(len(values)==prod(radices),'oracle complete coordinate domain')
    out=[]
    for index,value in enumerate(values):
        coordinates=[];quotient=index
        for radix in radices:
            coordinates.append(quotient%radix);quotient//=radix
        need(quotient==0,'oracle coordinate extent')
        phase=(1<<precision,0)
        for axis in reversed(range(len(radices))):
            phase=multiply(tables[axis][coordinates[axis]],phase,precision)
        if conjugate:phase=(phase[0],-phase[1])
        out.append(multiply(value,phase,precision))
    return tuple(out)


def cache_updates(radices):
    total=prod(radices);prefix=1;result=0
    for radix in radices:
        result+=total//prefix-1;prefix*=radix
    return result
