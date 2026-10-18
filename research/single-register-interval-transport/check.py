"""Independent single-register impulse checks. Charles Bethin / OpenAI Codex.

Apache-2.0. No production verifier or predecessor checking code is imported.
The actual pinned compose AST supplies one traversal. An independently written
recursive prefix model skips completed subtrees using their ideal shear map.
"""
import ast
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import random
import sys
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent

def need(ok, message):
    if not ok:
        raise ValueError(message)

def trace(n, sign):
    raw = (HERE / 'vendor/dirty.py').read_text()
    funcs = [x for x in ast.parse(raw).body if isinstance(x, ast.FunctionDef) and x.name == 'compose']
    need(len(funcs) == 1, 'dispatcher source')
    ports = [[0] for _ in range((n-1).bit_length()+2)]
    ids = {id(p): i for i,p in enumerate(ports)}
    events = []
    def leaf(x,y,factor,phases,beta,bits,direction,s,stats):
        events.append((ids[id(x)],ids[id(y)],factor,s))
    scope = dict(c=SimpleNamespace(need=need,norm2=lambda x:x*x), leaf=leaf)
    exec(compile(ast.Module(body=funcs,type_ignores=[]),'pinned compose','exec'),scope)
    scope['compose'](ports[0],ports[1],list(range(n)),ports[2:],[1],Q(1,2),64,1,sign)
    return events

def eye(d):
    return [[Q(i==j) for j in range(d)] for i in range(d)]

def mm(a,b):
    return [[sum(x*y for x,y in zip(row,col)) for col in zip(*b)] for row in a]

def inverse(a):
    d=len(a); rows=[r[:]+e for r,e in zip(a,eye(d))]
    for j in range(d):
        k=next(k for k in range(j,d) if rows[k][j])
        rows[k],rows[j]=rows[j],rows[k]
        scale=rows[j][j]; rows[j]=[x/scale for x in rows[j]]
        for i in range(d):
            if i != j:
                scale=rows[i][j]
                rows[i]=[x-scale*y for x,y in zip(rows[i],rows[j])]
    return [r[d:] for r in rows]

def leaf_count(n):
    if n==1:return 1
    return 2*(leaf_count(n//2)+leaf_count(n-n//2))

def prefix(factors,cut,sign=1):
    """Compute a cut without emitting a word: completed nodes become one shear."""
    d=(len(factors)-1).bit_length()+2
    def rec(fs,t,s,x,y,z):
        count=leaf_count(len(fs))
        if t==0:return eye(d)
        if t==count:
            p=Q(s)
            for a in fs:p*=a
            result=eye(d); result[y][x]=p
            return result
        need(len(fs)>1,'invalid leaf cut')
        mid=len(fs)//2; left,right=fs[:mid],fs[mid:]
        # These are endpoint transitions; no literal source instruction is used.
        children=[(left,x,z,1),(right,z,y,1),(left,x,z,-1),(right,z,y,-1)]
        if s<0:children=[(fs,a,b,-v) for fs,a,b,v in children[::-1]]
        result=eye(d)
        for fs,a,b,v in children:
            take=min(t,leaf_count(len(fs)))
            result=mm(rec(fs,take,v,a,b,z+1),result)
            t-=take
            if t==0:return result
        raise ValueError('invalid cut')
    return rec(list(factors),cut,sign,0,1,2)

def impulse(events, factors, a,b,j,d):
    v=[0]*d;v[j]=1
    seq=events[a:b] if a<=b else [(x,y,k,-s) for x,y,k,s in events[b:a][::-1]]
    for x,y,k,s in seq:v[y]+=s*factors[k]*v[x]
    return v

def run():
    pins=json.loads((HERE/'SOURCES.json').read_text())
    for name, row in pins['files'].items():
        raw=(HERE/name).read_bytes()
        need(hashlib.sha256(raw).hexdigest()==row['sha256'],'source hash '+name)
        need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==row['git_blob'],'source blob '+name)
    rng=random.Random(83); census=[]; count=0
    # All destination-supported chronological transports for these concrete factors.
    # The domain is deliberately finite; the proof is separate.
    for n in range(1,17):
        d=(n-1).bit_length()+2; maximum=0; witness=None
        for sign in (-1,1):
            events=trace(n,sign)
            for factors in ([1]*n, [(-1)**i for i in range(n)], [rng.choice((-1,1)) for _ in range(n)]):
                for a,event in enumerate(events,1):
                    j=event[1];v=[0]*d;v[j]=1
                    for b in range(a,len(events)+1):
                        size=max(map(abs,v)); count+=1
                        need(size<=d,'linear column bound')
                        if size>maximum:maximum=size;witness=[sign,a,b,j,factors]
                        if b<len(events):
                            x,y,k,s=events[b];v[y]+=s*factors[k]*v[x]
        census.append(dict(n=n,dimension=d,maximum=maximum,witness=witness))
    independent=[]
    for n in list(range(1,18))+[23,31,32,47,64,83]:
        d=(n-1).bit_length()+2
        factors=[rng.choice((-1,1)) for _ in range(n)]
        for sign in (-1,1):
            events=trace(n,sign);need(len(events)==leaf_count(n),'length model')
            for case in range(6):
                a=rng.randrange(len(events)+1);b=rng.randrange(len(events)+1)
                j=(events[a-1][1] if a else rng.randrange(d))
                direct=impulse(events,factors,a,b,j,d)
                model=mm(prefix(factors,b,sign),inverse(prefix(factors,a,sign)))
                need(direct==[r[j] for r in model],'independent recursive cut model')
                need(max(map(abs,direct))<=d,'independent column envelope')
                independent.append([n,sign,a,b,j,max(map(abs,direct))])
    lower=[]
    for h in range(1,9):
        n=2**h;f=[1]*n
        for k in range(h-1):f[n-2**k-1]=-1
        a=(3*4**(h-1))//5;b=(4**h+2)//3;events=trace(n,1)
        j=h+1;value=impulse(events,f,a,b,j,h+2)[1]
        need(abs(value)==h,'PR1374 last connector coefficient')
        destination=events[a-1][1] if a else None
        actual=impulse(events,f,a,b,destination,h+2)[1] if a else None
        if h>=2:
            need(destination==h and abs(actual)==h-1,'actual destination lower bound')
        lower.append(dict(h=h,a=a,b=b,column=j,value=value,preceding_destination=destination,destination_value=actual))
    # A joint perturbation is outside the single-register contract.
    events=trace(4,1);f=[1,1,-1,1]
    cols=[impulse(events,f,2,6,j,4)[1] for j in range(4)]
    need(sum(map(abs,cols))==6 and max(map(abs,cols))==2,'joint versus one-register control')
    # The complete ordered-subset hypothesis cannot be replaced by singleton norms <=G.
    big=impulse(trace(4,1),[2]*4,0,16,0,4)
    need(max(map(abs,big))==16 and 16>4*2,'factor subset boundary')
    return dict(status='PASS_SINGLE_REGISTER_TRANSPORT',seed=83,sys_version=sys.version,sys_executable=sys.executable,
                destination_intervals=count,census=census,independent_cases=independent,lower_family=lower,
                controls=dict(joint_row=cols,joint_norm=6,single_column_norm=2,four_large_factors=big),
                proof_scope='Finite supporting evidence only; all-size argument in PROOF.md')

if __name__=='__main__':
    print(json.dumps(run(),indent=2))
