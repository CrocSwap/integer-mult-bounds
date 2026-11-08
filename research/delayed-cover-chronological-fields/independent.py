"""Separate dense runtime and inverse ordinal oracle; no author verifier."""
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys

PACKAGE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('lead_fields',PACKAGE/'producer.py')
p=importlib.util.module_from_spec(spec);sys.modules[spec.name]=p;spec.loader.exec_module(p)


def binary(n):
    return [3+((n>>i)&1) for i in range(n.bit_length())]


def encoded(symbols, origin):
    values=[3+((s>>bit)&1) for s in [1,*symbols,2] for bit in (2,1,0)]
    return {origin:1,**{origin+1+i:v for i,v in enumerate(values)}},origin+4


def decode(raw,q,n,codes,width,Q):
    pos=0;cap=q**(width-1);H=cap**(n*n);ordinal=0;place=1
    def word():
        nonlocal pos
        value=0;shift=0
        while raw[pos]!=5:
            if raw[pos] not in (3,4): raise ValueError('nonbinary word')
            value+=(raw[pos]-3)<<shift;shift+=1;pos+=1
        pos+=1
        return value,shift
    for code in codes:
        if word()!=(code,Q): raise ValueError('wrong chronological source code')
        high=0
        for _ in range(n*n):
            value,length=word()
            if value>=cap or length!=(q**width).bit_length()+1: raise ValueError('matrix digit')
            high=high*cap+value
        if raw[pos]!=6: raise ValueError('field separator')
        pos+=1;ordinal+=place*high;place*=H
    if pos!=len(raw): raise ValueError('excess prefix')
    return ordinal


def fixture(q,n,codes,width,fibre,repeats,newest=False):
    Q=max(2,max(codes).bit_length());program,meta=p.build(q,n,Q,oldest_first=not newest)
    origins=[11+3*i for i in range(program.tapes)]
    original=[{o-3:4,o-2:3} for o in origins];heads=list(origins)
    for role,value in ((0,width),(2,fibre)):
        cells,heads[role]=encoded(binary(value),origins[role]);original[role].update(cells)
    codewords=[s for code in codes for s in [*[3+((code>>i)&1) for i in range(Q)],5]]
    original[1].update({origins[1]:1,**{origins[1]+1+i:s for i,s in enumerate(codewords)},origins[1]+len(codewords)+1:2})
    heads[1]+=1
    H=q**((width-1)*n*n);total=H**len(codes)*repeats
    cells,heads[3]=encoded([3+((i*19+i//5)%2) for i in range(total*fibre)],origins[3]);original[3].update(cells)
    entry_heads=list(heads);tapes=[]
    for cells in original:
        tape=bytearray(max(cells)+1)
        for i,v in cells.items(): tape[i]=v
        tapes.append(tape)
    counts={key:0 for key in ('branch','write','move','goto','halt')}
    visits=[set() for _ in tapes];pc=program.entry;steps=prefixes=mismatches=0;digest=sha256()
    while True:
        if pc==meta['events']['ready']:
            h=heads[12];raw=[]
            if h!=origins[12]+1: raise ValueError('port origin')
            while h<len(tapes[12]) and tapes[12][h]: raw.append(tapes[12][h]);h+=1
            mismatches+=decode(raw,q,n,codes,width,Q)!=prefixes%(H**len(codes))
            digest.update(bytes(raw));prefixes+=1
        row=program.instructions[pc];op=row[0];steps+=1
        if op=='reject' or steps>50_000_000: raise ValueError(('reject/cap',row))
        counts[op]+=1
        if op=='halt': break
        if op=='goto': pc=row[1];continue
        t=row[1];i=heads[t];visits[t].add(i)
        if i<origins[t]: raise ValueError('buried caller visited')
        if op=='move': heads[t]+=row[2];visits[t].add(heads[t]);pc+=1
        elif op=='write':
            while len(tapes[t])<=i: tapes[t].append(0)
            tapes[t][i]=row[2];pc+=1
        elif op=='branch':
            symbol=tapes[t][i] if i<len(tapes[t]) else 0;pc=row[3]
            for value,target in row[2]:
                if value==symbol: pc=target;break
    if prefixes!=total: raise ValueError('incomplete cube')
    for t,tape in enumerate(tapes):
        nonblank={i:v for i,v in enumerate(tape) if v}
        expected=original[t] if t<4 else {origins[t]-3:4,origins[t]-2:3}
        if nonblank!=expected or heads[t]!=entry_heads[t]: raise ValueError(('endpoint',t))
    if (not newest and mismatches) or (newest and not mismatches): raise ValueError('order control')
    return dict(q=q,N=n,codes=codes,w=width,fibre=fibre,repeats=repeats,prefixes=prefixes,
                mismatches=mismatches,steps=steps,counts=counts,visited=sum(map(len,visits)),digest=digest.hexdigest())


if __name__=='__main__':
    cases=[fixture(*args) for args in ((3,1,(0,1),2,3,2),(5,1,(2,0,1),2,1,1),
                                     (3,2,(0,1),2,1,1),(3,2,(0,3,1),1,5,2))]
    control=fixture(3,1,(0,1),2,2,1,True)
    print('PASS_LEAD_DENSE_FIELD_MACHINE')
    print(json.dumps({'producer_sha256':sha256((PACKAGE/'producer.py').read_bytes()).hexdigest(),
                      'cases':cases,'newest_first_control':control},sort_keys=True))
