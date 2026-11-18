"""Exact periodic DDG samplers for paired denominator-13 decisions. Apache-2.0."""
from fractions import Fraction as Q
from itertools import product
from pathlib import Path
import hashlib
import json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
DEN=169
PERIOD=156


def need(ok,msg):
    if not ok:raise ValueError(msg)


def make(a,b):
    need(type(a) is int and type(b) is int and 1<=a<=12 and 1<=b<=12,'nonzero residue pair')
    weights=((13-a)*(13-b),(13-a)*b,a*(13-b),a*b)
    need(sum(weights)==DEN,'joint mass')
    need(weights[2]+weights[3]==13*a and weights[1]+weights[3]==13*b,'marginals')
    need(weights[0]*weights[3]==weights[1]*weights[2],'independence')
    residues=[tuple(w*pow(2,k,DEN)%DEN for w in weights) for k in range(PERIOD)]
    counts=[sum(row)//DEN for row in residues]
    need(all(sum(row)%DEN==0 and 1<=n<=3 for row,n in zip(residues,counts)),'unresolved nodes')
    states=[(k,j) for k,n in enumerate(counts) for j in range(n)]
    need(len(states)==312,'finite internal states')
    ids={s:i for i,s in enumerate(states)};table=[]
    for phase,node in states:
        digits=tuple(2*r//DEN for r in residues[phase]);row=[]
        for bit in (0,1):
            j=2*node+bit;target=None
            for out,digit in enumerate(digits):
                j-=digit
                if j<0:target=312+out;break
            if target is None:
                target=ids.get(((phase+1)%PERIOD,j))
                need(target is not None,'valid remaining node')
            row.append(target)
        table.append(tuple(row))
    mean=sum((Q(n,1<<k) for k,n in enumerate(counts)),Q(0))/(1-Q(1,1<<PERIOD))
    return weights,counts,table,mean


def census(table,weights,depth):
    need(len(table)==312 and all(len(row)==2 and all(type(t) is int and 0<=t<316 for t in row) for row in table),'table domain')
    active={0:1};done=[0]*4
    for k in range(1,depth+1):
        done=[2*n for n in done];nxt={}
        for state,n in active.items():
            for target in table[state]:
                if target>=312:done[target-312]+=n
                else:nxt[target]=nxt.get(target,0)+n
        active=nxt
        need(done==[w*(1<<k)//DEN for w in weights],'complete outcome-prefix counts')
        need(sum(active.values())+(sum(done))==1<<k,'complete fair-prefix mass')
        need(all(n==1 for n in active.values()) and 1<=len(active)<=3,'unresolved-prefix structure')
    return tuple(done),sum(active.values())


def run(table,bits):
    state=0
    for used,bit in enumerate(bits,1):
        target=table[state][bit]
        if target>=312:return target-312,used
        state=target
    return None,len(bits)


def rejected(fn):
    try:fn()
    except ValueError:return
    raise ValueError('negative control accepted')


def main():
    pins=json.loads((HERE/'SOURCES.json').read_text())
    for row in pins['files']:
        if row['usage']=='input':
            need(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'],'source bytes')
    need(pow(2,PERIOD,DEN)==1 and all(pow(2,k,DEN)!=1 for k in range(1,PERIOD)),'exact binary period')
    maximum=Q(0);minimum=Q(4);cases=literal=0
    for a,b in product(range(1,13),repeat=2):
        weights,counts,table,mean=make(a,b)
        census(table,weights,2*PERIOD)
        need(2<mean<Q(7,2),'certified paired expected cost')
        need(len(table)*2==624 and max(max(row) for row in table)<512,'nine-bit table targets')
        if (a,b)==(1,1):need(mean<Q(9,4),'strict two-small-residue gain')
        maximum=max(maximum,mean);minimum=min(minimum,mean)
        observed=[0]*4;left=0
        for bits in product((0,1),repeat=8):
            out,used=run(table,bits)
            if out is None:left+=1
            else:observed[out]+=1
            need(1<=used<=8,'bounded finite-tape test');literal+=1
        want=census(table,weights,8)
        need((tuple(observed),left)==want,'independent literal-tape oracle')
        cases+=1
    weights,counts,table,mean=make(1,1)
    need(mean==Q(9960277917013927549978,4649714690825496825793),'exact displayed pair mean')
    need(census(table,weights,PERIOD)[1]==1,'positive survival at one whole period')
    bad=list(table)
    for i,row in enumerate(bad):
        if 315 in row:
            bad[i]=tuple(312 if t==315 else t for t in row);break
    rejected(lambda:census(bad,weights,PERIOD))
    rejected(lambda:make(0,1))
    rejected(lambda:make(1,13))
    rejected(lambda:need(mean>=4,'false additivity of standalone lower bounds'))
    rejected(lambda:need(mean<=2,'understated joint mean'))
    rejected(lambda:need(census(table,weights,PERIOD)[1]==0,'false finite draw cap'))
    need(Q(1,13)!=Q(1,169),'reused single flag violates independent joint law')
    print(json.dumps(dict(status='PASS_PAIRED_RESIDUE_SAMPLER',residue_pairs=cases,
                         internal_states=312,transitions_per_pair=624,depths_checked_per_pair=312,
                         literal_tapes=literal,mean_one_one=str(mean),maximum_mean=str(maximum),
                         minimum_mean=str(minimum),
                         scope='optimal expected fair-bit count for a fixed nonadaptive pair; physical costs open; no new kappa'),sort_keys=True))


if __name__=='__main__':main()
