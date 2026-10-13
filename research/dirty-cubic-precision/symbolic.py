"""Research-only free noncommuting algebra trace of frozen balanced word."""
import importlib.util, json, hashlib, time
from pathlib import Path
P=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('upstream_core',P/'vendor/877/core.py')
core=importlib.util.module_from_spec(spec);spec.loader.exec_module(core)

def identity(n):
    return [[{():1} if i==j else {} for j in range(n)] for i in range(n)]

def add_factor(dst,src,factor,sign,left):
    out=dst.copy()
    for word,c in src.items():
        key=(factor,)+word if left else word+(factor,)
        out[key]=out.get(key,0)+sign*c
        if not out[key]:del out[key]
    return out

def audit(matrix,n):
    mass=0;terms=0
    for row in matrix:
        mass=max(mass,sum(abs(c) for entry in row for c in entry.values()))
        for entry in row:
            for word in entry:
                if any(a<=b for a,b in zip(word,word[1:])):
                    raise ValueError(('repeated or unordered factor',n,word))
                terms+=1
    return mass,terms

def run(n,sign):
    dim=2+(n-1).bit_length();forward=identity(dim);inverse=identity(dim)
    bound=2*3**((n-1).bit_length());peak=[1,1];count=0
    stream=hashlib.sha256()
    for src,dst,f,q in core.word(n,sign):
        forward[dst]=[add_factor(a,b,f,q,True) for a,b in zip(forward[dst],forward[src])]
        for row in inverse:row[src]=add_factor(row[src],row[dst],f,-q,False)
        m1,t1=audit(forward,n);m2,t2=audit(inverse,n)
        if max(m1,m2)>bound:raise ValueError(('coefficient mass bound',n,count,m1,m2,bound))
        peak=[max(peak[0],m1),max(peak[1],m2)];count+=1
        stream.update(json.dumps([m1,m2,t1,t2]).encode())
    expected=identity(dim);expected[1][0]={tuple(reversed(range(n))):sign}
    if forward!=expected:raise ValueError('endpoint')
    expected[1][0]={tuple(reversed(range(n))):-sign}
    if inverse!=expected:raise ValueError('inverse endpoint')
    return dict(n=n,sign=sign,leaves=count,bound=bound,prefix_coefficient_mass=peak[0],inverse_prefix_coefficient_mass=peak[1],sha256=stream.hexdigest())
