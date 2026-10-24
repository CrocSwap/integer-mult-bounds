"""Corroborate the full central class with independent full-matrix invariants.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
Frozen fixture construction is credited in NOTICE.md.
"""
import argparse
import hashlib
from itertools import product
import json
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from central import classify, representative
from block_source import construct, matrices


def need(value,message):
    if not value: raise ValueError(message)


def ident(n): return tuple(tuple(int(i==j) for j in range(n)) for i in range(n))


def plus(a,b,q,sign=1):
    return tuple(tuple((x+sign*y)%q for x,y in zip(r,s)) for r,s in zip(a,b))


def mm(a,b,q=None):
    bt=tuple(zip(*b))
    result=tuple(tuple(sum(x*y for x,y in zip(r,c)) for c in bt) for r in a)
    return result if q is None else tuple(tuple(x%q for x in row) for row in result)


def rank_columns(a,q):
    basis={}
    for column in zip(*a):
        v=list(column)
        for pivot in sorted(basis):
            if v[pivot]:
                c=v[pivot];v=[(x-c*y)%q for x,y in zip(v,basis[pivot])]
        pivot=next((i for i,x in enumerate(v) if x),None)
        if pivot is not None:
            c=pow(v[pivot],-1,q);basis[pivot]=[(c*x)%q for x in v]
    return len(basis)


def charpoly(a,q):
    # Faddeev-LeVerrier over integer lifts; divide before reducing modulo q.
    n=len(a);b=ident(n);coeff=[1]
    for k in range(1,n+1):
        b=mm(a,b);trace=sum(b[i][i] for i in range(n))
        need(trace%k==0,'integer characteristic division')
        c=-trace//k;coeff.append(c)
        b=tuple(tuple(x+c*int(i==j) for j,x in enumerate(row)) for i,row in enumerate(b))
    return tuple(x%q for x in reversed(coeff))


def trim(p):
    p=list(p)
    while len(p)>1 and p[-1]==0:p.pop()
    return tuple(p)


def divide(a,b,q):
    work=list(a);out=[0]*max(1,len(a)-len(b)+1)
    while len(work)>=len(b) and any(work):
        k=len(work)-len(b);c=work[-1]*pow(b[-1],-1,q)%q;out[k]=c
        for j,x in enumerate(b):work[k+j]=(work[k+j]-c*x)%q
        work=list(trim(work))
    return trim(out),trim(work)


def factors(poly,q):
    remaining=poly;out=[];degree=1
    while len(remaining)>1 and 2*degree<=len(remaining)-1:
        need(q**degree<=100000,'factor oracle capacity')
        for coefficients in product(range(q),repeat=degree):
            f=tuple(coefficients)+(1,);used=False
            while True:
                quotient,remainder=divide(remaining,f,q)
                if remainder!=(0,):break
                remaining=quotient;used=True
            if used:out.append(f)
        degree+=1
    if len(remaining)>1:out.append(remaining)
    return out


def polynomial(a,p,q):
    n=len(a);out=tuple((0,)*n for _ in range(n))
    for c in reversed(p):out=plus(mm(out,a,q),ident(n),q,c)
    return out


def signature(a,q):
    cp=charpoly(a,q);result=[]
    for f in factors(cp,q):
        b=polynomial(a,f,q);current=ident(len(a));ranks=[len(a)]
        for _ in range(len(a)+1):
            current=mm(current,b,q);ranks.append(rank_columns(current,q))
            if ranks[-1]==ranks[-2]:break
        need(ranks[-1]==ranks[-2],'rank sequence did not stabilize')
        blocks=[];degree=len(f)-1
        for size in range(1,len(ranks)-1):
            numerator=ranks[size-1]-2*ranks[size]+ranks[size+1]
            need(numerator>=0 and numerator%degree==0,'invalid primary multiplicity')
            blocks += [size]*(numerator//degree)
        result.append({'polynomial':list(f),'exponents':sorted(blocks,reverse=True)})
    need(sum((len(r['polynomial'])-1)*sum(r['exponents']) for r in result)==len(a),'primary dimension')
    return {'characteristic_polynomial':list(cp),'primary_blocks':result}


def pad(a,values):
    n=len(a);m=len(values)
    return tuple(tuple(row)+(0,)*m for row in a)+tuple((0,)*n+tuple(values[i]*int(i==j) for j in range(m)) for i in range(m))


def inspect(h,q,extra=()):
    p,t=construct(h,q);d=len(h)
    if extra:p=pad(p,[a for a,b in extra]);t=pad(t,[b for a,b in extra])
    need(mm(p,p,q)==p and mm(t,t,q)==t and mm(p,t,q)==mm(t,p,q),'source premises')
    need(tuple(row[:d] for row in p[:d])==ident(d) and tuple(row[:d] for row in t[:d])==ident(d),'identity pivot')
    pq=mm(p,t,q);need(tuple(row[:d] for row in pq[:d])==h,'compressed H')
    def schur(a):return plus(tuple(row[d:] for row in a[d:]),mm(tuple(row[:d] for row in a[d:]),tuple(row[d:] for row in a[:d]),q),q,-1)
    s,u=schur(p),schur(t);m=len(s)
    k=plus(mm(s,u,q),mm(u,s,q),q,-1);z=mm(plus(s,u,q,-1),plus(s,u,q,-1),q)
    need(rank_columns(k,q)==2*d,'sharp premise')
    a1=2*m-rank_columns(s+plus(u,ident(m),q,-1),q)-rank_columns(plus(s,ident(m),q,-1)+u,q)
    predicted=classify(h,m,a1,q);model=representative(predicted,q)
    actual=signature(z,q);expected=signature(model,q)
    need(actual==expected,'full central similarity invariants differ')
    return {'field':q,'h':[list(row) for row in h],'padding':[list(x) for x in extra],
            'prediction':predicted,'invariants':actual}


def jordan(size,lam=0,q=2):return tuple(tuple((lam*int(i==j)+int(j==i+1))%q for j in range(size)) for i in range(size))


def reject(call):
    try:call()
    except ValueError:return
    raise ValueError('control accepted')


def controls():
    h=jordan(3);base=inspect(h,2);zero=inspect(h,2,((0,0),));one=inspect(h,2,((0,1),))
    need(zero['prediction']['dimension']==one['prediction']['dimension'] and zero['h']==one['h'],'same input class control')
    need(zero['invariants']!=one['invariants'],'opposite-sector count is necessary')
    need(base['prediction']['endpoint_blocks']['0']==[2,2,2,2,1,1],'characteristic-two J3 law')
    odd=inspect(h,3);need(odd['prediction']['endpoint_blocks']['0']==[4,3,1,1,1],'credited odd law')
    repeated=inspect(jordan(4,1,2),2)
    need(max(repeated['prediction']['endpoint_blocks']['1'])>1,'endpoint-one repeated blocks')
    reject(lambda: classify(h,5,0,2))
    reject(lambda: classify(h,10,5,2))
    reject(lambda: classify(h,10,0,4))
    reject(lambda: classify(((0,1),),10,0,2))
    odd_nonsplit=inspect(((0,0,0,2),(1,0,0,0),(0,1,0,1),(0,0,1,0)),3)
    need(any(len(r['polynomial'])==3 and max(r['exponents'])>1 for r in odd_nonsplit['invariants']['primary_blocks']), 'non-split repeated central factor')
    return {'groups':9,'odd_nonsplit':odd_nonsplit,'same_h_dimension_different_classes':[zero,one],'binary_j3':base,'ternary_j3':odd,'endpoint_one':repeated}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');ap.add_argument('--small',action='store_true');args=ap.parse_args()
    record=controls()
    if args.small:
        print('PASS_SMALL_WHOLE_CENTRAL');return
    digest=hashlib.sha256();domains=[]
    for q,d in ((2,1),(2,2),(2,3),(3,1),(3,2),(5,1),(5,2)):
        count=0
        for h in matrices(q,d):
            result=inspect(h,q);digest.update(json.dumps(result,sort_keys=True).encode());count+=1
        domains.append({'field':q,'dimension_h':d,'count':count})
    examples=[]
    for q in (2,3,5,7):
        for size in (2,3,5):
            for lam in (0,1):examples.append(inspect(jordan(size,lam,q),q,((0,0),(1,1),(0,1),(1,0))))
    # Companion of (t^2+t+1)^2 over F2: non-split and repeated.
    h=((0,0,0,1),(1,0,0,0),(0,1,0,1),(0,0,1,0))
    examples.append(inspect(h,2))
    # A mixed primary example has endpoints and a non-split component.
    h=((0,1,0,0),(0,0,0,0),(0,0,0,1),(0,0,1,1))
    examples.append(inspect(h,2,((0,1),)))
    record.update({'domains':domains,'exhaustive_cases':sum(r['count'] for r in domains),
                   'exhaustive_result_sha256':digest.hexdigest(),'additional_examples':examples})
    sources=json.loads((HERE/'SOURCES.json').read_text())
    for r in sources['files']:
        if '/vendor/' in r['path']:
            local=HERE/'vendor'/Path(r['path']).name
            need(hashlib.sha256(local.read_bytes()).hexdigest()==r['sha256'],'source byte drift')
    record['files']={p.relative_to(HERE).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(HERE.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.name!='RESULT.json'}
    if args.write:(HERE/'RESULT.json').write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
    else:need(record==json.loads((HERE/'RESULT.json').read_text()),'receipt drift')
    print('PASS_SCHUR_WHOLE_CENTRAL',json.dumps({'exhaustive_cases':record['exhaustive_cases'],'additional_examples':len(examples),'controls':record['groups'],'result_sha256':digest.hexdigest()}))


if __name__=='__main__':main()
