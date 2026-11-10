"""Independent whole-grid rounded oracle, outside the production algorithm."""
from fractions import Fraction
from math import prod


def need(ok,why):
    if not ok: raise ValueError(why)


def trunc(n,d):
    need(type(n) is int and type(d) is int and d>0,'signed quotient')
    q=abs(n)//d
    return -q if n<0 else q


def coefficient(x,bits):
    x=Fraction(x)
    return trunc(x.numerator*(2**bits),x.denominator)


def full_grid(matrices,plans,original):
    periods=tuple(p.period for p in plans)
    need(len(original)==prod(periods),'full-grid cardinality')
    current=tuple(original)
    for axis,p in enumerate(plans):
        n=periods[axis];stride=prod(periods[axis+1:]);block=n*stride
        a=tuple(tuple(coefficient(x,p.bits) for x in row) for row in matrices[axis])
        need(len(a)==n and all(len(row)==n for row in a),'dense matrix')
        result=[None]*len(current)
        for prefix in range(len(current)//block):
            base=prefix*block
            for remainder in range(stride):
                source=tuple(current[base+r*stride+remainder] for r in range(n))
                iterate=((0,0),)*n
                for _ in range(p.terms):
                    following=[]
                    for row in range(n):
                        pair=[]
                        for component in (0,1):
                            total=source[row][component]*(2**(p.bits-p.normalizer_shift))
                            total+=sum(a[row][column]*iterate[column][component] for column in range(n))
                            pair.append(trunc(total,2**p.bits))
                        following.append(tuple(pair))
                    iterate=tuple(following)
                for row,value in enumerate(iterate):
                    result[base+row*stride+remainder]=value
        need(all(value is not None for value in result),'all global rows filled')
        current=tuple(result)
    return current


def decode_global(address,periods):
    result=[]
    for period in reversed(periods):
        result.append(address%period);address//=period
    need(address==0,'address range')
    return tuple(reversed(result))


def sigmag(value,width):
    need(type(value) is int and abs(value)<2**(width-1),'word carrier')
    return str(int(value<0))+format(abs(value),'0'+str(width-1)+'b')


def encoded(pair,width):
    return ''.join(sigmag(value,width) for value in pair)


def expected_after_core(matrices,plans,original,ell,boundary,spectators=1):
    periods=tuple(p.period for p in plans);size=prod(periods)
    need(len(original)==spectators*size,'spectator source cardinality')
    width=plans[0].data_width;side=2**ell;result=[];targets=0
    for spectator in range(spectators):
        source=original[spectator*size:(spectator+1)*size]
        rounded=full_grid(matrices,plans,source)
        for address,pair in enumerate(source):
            point=decode_global(address,periods)
            boundary_point=any(x%side<boundary or x%side>=side-boundary for x in point)
            if boundary_point:
                result.append(encoded(rounded[address],width));targets+=1
            else:
                result.append(''.join('1' if bit=='0' else '0' for bit in encoded(pair,width)))
    return ''.join(value+'#' for value in result),targets
