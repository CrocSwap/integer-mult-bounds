# SPDX-License-Identifier: Apache-2.0
"""Exact independent controls for simultaneous gate/trajectory perturbation."""
import argparse
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent


def need(ok,message):
    if not ok:raise ValueError(message)


def eye(n):return [[Q(i==j) for j in range(n)] for i in range(n)]
def mul(a,b):return [[sum(x*y for x,y in zip(row,col)) for col in zip(*b)] for row in a]
def add(a,b):return [[x+y for x,y in zip(r,s)] for r,s in zip(a,b)]
def sub(a,b):return [[x-y for x,y in zip(r,s)] for r,s in zip(a,b)]
def norm(a):return max(sum(abs(x) for x in row) for row in a)
def inv(a):
    n=len(a);v=[list(row)+ident for row,ident in zip(a,eye(n))]
    for j in range(n):
        pivot=next((i for i in range(j,n) if v[i][j]),None)
        need(pivot is not None,'singular matrix')
        v[j],v[pivot]=v[pivot],v[j];scale=v[j][j];v[j]=[x/scale for x in v[j]]
        for i in range(n):
            if i!=j:
                scale=v[i][j];v[i]=[x-scale*y for x,y in zip(v[i],v[j])]
    return [r[n:] for r in v]


def prefixes(gates):
    values=[eye(len(gates[0]))]
    for a in gates:values.append(mul(a,values[-1]))
    return values


def ceil_log2(q):
    need(q>0,'positive logarithm argument')
    k=0
    while Q(2)**k<q:k+=1
    return k


def rounded(q,p):
    q=q*(1<<p)
    return Q((q+Q(1,2)).numerator//(q+Q(1,2)).denominator,1<<p)


def admit(gates,changed):
    need(len(gates)==len(changed)>0,'same nonempty gate inventory')
    f=prefixes(gates);n=len(gates[0]);b=max(norm(v) for p in f for v in (p,inv(p)))
    eps=[norm(sub(a,c)) for a,c in zip(gates,changed)]
    ds=[mul(mul(inv(f[i+1]),sub(changed[i],gates[i])),f[i]) for i in range(len(gates))]
    rho=sum(map(norm,ds));need(rho<1,'interaction budget must be below one')
    need(rho<=b*b*sum(eps),'absolute-to-relative error budget')
    direct=prefixes(changed);relative=prefixes([add(eye(n),d) for d in ds])
    for j in range(len(f)):
        need(direct[j]==mul(f[j],relative[j]),'ordered interaction identity')
        need(norm(direct[j])<=b/(1-rho),'rounded prefix bound')
        need(norm(inv(direct[j]))<=b/(1-rho),'rounded inverse prefix bound')
        need(norm(sub(direct[j],f[j]))<=b*rho/(1-rho),'simultaneous operator bound')
    return f,b,rho,direct


def source_check():
    pins=json.loads((HERE/'REFERENCES.json').read_bytes())
    for row in pins['files']:
        need(hashlib.sha256((HERE/row['local']).read_bytes()).hexdigest()==row['sha256'],
             'reference source pin: '+row['local'])
    return pins['commit']


def run():
    source=source_check();rows=[];prefix_count=trajectory_count=0
    for scale in (Q(1,3),Q(2),Q(16)):
        u=[[Q(1),scale],[Q(0),Q(1)]];v=[[Q(1),Q(0)],[1/scale,Q(1)]]
        for repeats in (1,2,4):
            gates=[u,v,inv(v),inv(u)]*repeats
            f=prefixes(gates);b=max(norm(w) for p in f for w in (p,inv(p)))
            for target in (0,4,9):
                p=target+ceil_log2(8*len(gates)*b**3);eta=Q(1,1<<p)
                # All entries perturbed together, including exact zeros and ones.
                changed=[[[x+(-1 if (i+j+k)%2 else 1)*eta for j,x in enumerate(row)]
                          for i,row in enumerate(a)] for k,a in enumerate(gates)]
                exact,b,rho,direct=admit(gates,changed);prefix_count+=len(exact)
                need(rho<=Q(1,4),'explicit guard admits the relative budget')
                need(norm(sub(direct[-1],exact[-1]))<=Q(1,1<<target),'explicit coefficient guard')
                for x in ([[Q(1)],[Q(0)]],[[Q(3,5)],[Q(4,5)]],[[Q(-1)],[Q(1)]]):
                    y=x;noise=Q(0)
                    for j,a in enumerate(changed,1):
                        raw=mul(a,y)
                        y=[[rounded(row[0],p)] for row in raw]
                        noise+=norm(sub(y,raw))
                        error=norm(sub(y,mul(exact[j],x)))
                        need(error<=b*(rho*norm(x)+b*noise)/(1-rho),'arithmetic trajectory bound')
                        need(error<=Q(1,1<<target),'explicit arithmetic guard')
                        trajectory_count+=1
                rows.append(dict(scale=str(scale),gates=len(gates),prefix_bound=str(b),
                                 target_bits=target,fractional_bits=p,rho=str(rho),
                                 operator_error=str(norm(sub(direct[-1],exact[-1])))))
    # Each foil invalidates a material premise or tempting shortened conclusion.
    e=Q(1,8);need((1+e)**2-1>2*e,'first-order-only foil')
    gates=[[[Q(16),Q(0)],[Q(0),Q(1)]],[[Q(1,16),Q(0)],[Q(0),Q(1)]]]
    changed=[gates[0],add(gates[1],[[e,Q(0)],[Q(0),Q(0)]])]
    need(norm(sub(prefixes(changed)[-1],eye(2)))>e/(1-e),'endpoint-only foil')
    try:admit([eye(2)],[[[Q(0),Q(0)],[Q(0),Q(1)]]])
    except ValueError as error:need('budget' in str(error),'small-budget rejection reason')
    else:raise ValueError('singular rounded gate admitted')
    need(norm([[e],[Q(0)]])>0,'omitted arithmetic noise foil')
    u=[[Q(1),Q(2)],[Q(0),Q(1)]];v=[[Q(1),Q(0)],[Q(3),Q(1)]]
    need(mul(u,v)!=mul(v,u),'changed order foil')
    return dict(status='PASS_SIMULTANEOUS_GATE_ROUNDING',source_commit=source,
                circuits=len(rows),prefixes=prefix_count,trajectory_steps=trajectory_count,
                controls=['higher_order_terms','endpoint_only_norm','rho_one_singular',
                          'omitted_arithmetic_noise','noncommuting_order'],cases=rows,
                limits='Exact rational two-wire controls; source compiler prefix envelope, spectral proof, actual arithmetic kernel and all-size admission remain external.')


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path);args=ap.parse_args()
    if args.out:need(not args.out.exists(),'output already exists')
    result=run();data=json.dumps(result,sort_keys=True,indent=2)+'\n'
    if args.out:
        with args.out.open('x',encoding='utf-8',newline='\n') as f:f.write(data)
    else:
        canonical=lambda obj:json.dumps(obj,sort_keys=True,separators=(',',':'),allow_nan=False)
        need(canonical(result)==canonical(json.loads((HERE/'RESULT.json').read_bytes())),'result receipt')
    print(data,end='')
