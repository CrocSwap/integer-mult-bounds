"""Construct the whole source-specific interval using three existing QUERYs.

Only current ADD, SWAP, LAMBDA and QUERY events are newly emitted. Every
temporary linear combination uses an existing public role and is restored;
no new initialized role, helper credit, or service opcode appears.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from copy import deepcopy
from collections import Counter
from source_binding import need

START, STOP = 457, 576  # half-open, zero-based exact source event interval


def add(dst, src, coefficient):
    need(dst != src and coefficient in (-1,1), 'literal distinct unit ADD')
    return ['A','ADD',dst,src,str(coefficient)]


def lam(role, sign):
    return ['A','LAMBDA',role,sign]


def tscale(role):
    # Source lambda_+^2=q^2=t, and t^2=1. This is not a projection.
    return [lam(role,1),lam(role,1)]


def tadd(dst, src, sign):
    # Form +/-t*src, use it once, then restore the arbitrary source exactly.
    return tscale(src)+[add(dst,src,sign)]+[lam(src,-1),lam(src,-1)]


def three_queries(a=0,b=19,c=1,d=2):
    need(len({a,b,c,d}) == 4, 'four distinct arbitrary public fields')
    out = [['A','SWAP',a,c],['A','SWAP',b,c],add(b,d,1)]
    out += tscale(d)+tadd(c,a,1)
    out += [['A','QUERY',a,b,-1]]
    out += tadd(c,a,-1)+[['A','QUERY',b,c,-1]]+tadd(c,a,1)
    out += tadd(d,b,-1)+[['A','QUERY',c,d,-1]]+tadd(d,b,1)
    out += tscale(c)+[add(a,c,-1)]+tscale(d)
    need(len(out) == 38 and Counter(e[1] for e in out)['QUERY'] == 3,
         'fixed complete gadget inventory')
    return out


def to_basis():
    # c=old role1; d=lambda_+ * sum_{k=1}^{18}(-1)^k old rolek.
    out = [add(k,1,-1) for k in range(2,19)]
    out += [add(2,k,(-1)**k) for k in range(3,19)]
    return out+[lam(2,1)]


def from_basis():
    out = [lam(2,-1)]
    out += [add(2,k,-(-1)**k) for k in range(3,19)]
    out += [add(k,1,1) for k in range(2,19)]
    return out


def parts(caller):
    e = caller['events']
    need(len(e) == 2991 and e[START] == ['A','QSELF',0,-1]
         and e[495] == ['A','QUERY',0,1,-1]
         and e[STOP-1] == ['A','QSELF',19,-1], 'exact three paid source sites')
    first, second, other = deepcopy(e[458:495]),deepcopy(e[496:545]),deepcopy(e[545:575])
    need(len(first) == 37 and len(second) == 49 and len(other) == 30,
         'exact even subinterval boundaries')
    for block, lo, hi in ((first,0,19),(second,0,19),(other,19,38)):
        for event in block:
            need(event[0] == 'A' and event[1] in ('ADD','SCALE','SWAP','LAMBDA','IDLE_ONE'),
                 'even intervening operation alphabet')
            fields = event[2:4] if event[1] in ('ADD','SWAP') else event[2:3]
            need(all(lo <= x < hi for x in fields), 'disjoint actual chain support')
    need([x for x in first+second+other if x[1] == 'IDLE_ONE'] == [['A','IDLE_ONE',28,[9]]],
         'sole D operation is preserved in the second-chain block')
    return first,second,other


def transform(caller):
    first,second,other=parts(caller)
    replacement = other+to_basis()+[add(0,2,-1)]+three_queries()+from_basis()+first+second
    need(len(replacement) == 223, 'complete expanded interval')
    out=deepcopy(caller)
    out['events'][START:STOP]=replacement
    out['ops_note']=str(out.get('ops_note',''))+'; source interval457..575 replaced by a three-QUERY even-basis factorization; no QSELF'
    need(not any(e[0] != 'J' and e[1] == 'QSELF' for e in out['events']), 'all QSELF removed')
    return out


def counts(caller):
    out={}
    for ty,t in caller['types'].items():
        c=Counter(e[1] for e in caller['events'] if e[0] == ty)
        out[ty]={'source_events':dict(sorted(c.items())),
                 'physical_instances':{k:v*len(t['ports']) for k,v in sorted(c.items())}}
    return out
