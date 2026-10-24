"""Uniform exact metadata compiler for the monomial gate subset.
All tests use explicit raises, including with python -O.
"""
import itertools
import json
import random


def compile_word(r, gates):
    A=[1<<j for j in range(r)]
    b,c=0,0
    a=[0]*r
    B=[0]*r
    def row(j): return [(v>>j)&1 for v in A]
    def toggle_edge(j,k):
        B[j]^=1<<k
        B[k]^=1<<j
    for gate in gates:
        op,j,*rest=gate
        if not (0<=j<r): raise ValueError('gate index')
        if op=='X': b^=1<<j
        elif op=='S':
            u=row(j)
            bj=(b>>j)&1
            c=(c+bj)&3
            for l in range(r): a[l]=(a[l]+(1-2*bj)*u[l])&3
            for l in range(r):
                for k in range(l+1,r):
                    if u[l]&u[k]: toggle_edge(l,k)
        elif op=='Z':
            u=row(j)
            c=(c+2*((b>>j)&1))&3
            for l in range(r): a[l]=(a[l]+2*u[l])&3
        elif op in ('CNOT','SWAP','CZ'):
            if len(rest)!=1 or not (0<=rest[0]<r) or j==rest[0]: raise ValueError('gate pair')
            k=rest[0]
            if op=='CNOT':
                A=[v^(((v>>j)&1)<<k) for v in A]
                b^=((b>>j)&1)<<k
            elif op=='SWAP':
                def sw(v):
                    d=((v>>j)^(v>>k))&1
                    return v^(d<<j)^(d<<k)
                A=[sw(v) for v in A]
                b=sw(b)
            else:
                u,v=row(j),row(k)
                bj,bk=(b>>j)&1,(b>>k)&1
                c=(c+2*(bj&bk))&3
                for l in range(r):
                    lin=(bj&v[l])^(bk&u[l])^(u[l]&v[l])
                    a[l]=(a[l]+2*lin)&3
                for l in range(r):
                    for t in range(l+1,r):
                        if (u[l]&v[t])^(u[t]&v[l]): toggle_edge(l,t)
        else: raise ValueError('nonmonomial or unknown gate: '+op)
    return dict(columns=A,bias=b,constant=c,linear=a,quadratic=B)


def evaluate(m,x):
    r=len(m['columns'])
    y=m['bias']
    q=m['constant']
    for j in range(r):
        if (x>>j)&1:
            y^=m['columns'][j]
            q+=m['linear'][j]
            for k in range(j+1,r): q+=2*((m['quadratic'][j]>>k)&1)*((x>>k)&1)
    return y,q&3


def literal(gates,x):
    q=0
    for gate in gates:
        op,j,*rest=gate
        if op=='X': x^=1<<j
        elif op=='S': q+=(x>>j)&1
        elif op=='Z': q+=2*((x>>j)&1)
        elif op=='CZ': q+=2*((x>>j)&1)*((x>>rest[0])&1)
        elif op=='CNOT': x^=((x>>j)&1)<<rest[0]
        elif op=='SWAP':
            k=rest[0]
            d=((x>>j)^(x>>k))&1
            x^=(d<<j)^(d<<k)
        else: raise ValueError(op)
    return x,q&3


def verify():
    words,states=0,0
    for r in range(1,4):
        gates=[(g,j) for g in ('X','S','Z') for j in range(r)]
        gates += [('CNOT',j,k) for j in range(r) for k in range(r) if j!=k]
        gates += [(g,j,k) for g in ('CZ','SWAP') for j in range(r) for k in range(j+1,r)]
        for length in range(4):
            for word in itertools.product(gates,repeat=length):
                m=compile_word(r,word)
                for x in range(1<<r):
                    if evaluate(m,x)!=literal(word,x): raise AssertionError('metadata differs from literal gate word')
                    states+=1
                words+=1
    rng=random.Random(20261022)
    for r in range(4,11):
        for _ in range(20):
            word=[]
            for _ in range(100):
                op=rng.choice(('X','S','Z','CZ','SWAP','CNOT'))
                j,k=rng.sample(range(r),2)
                word.append((op,j) if op in ('X','S','Z') else (op,j,k))
            m=compile_word(r,word)
            for x in range(1<<r):
                if evaluate(m,x)!=literal(word,x): raise AssertionError('metadata differs from long literal gate word')
                states+=1
            words+=1
    try: compile_word(1,[('H',0)])
    except ValueError: pass
    else: raise AssertionError('Hadamard wrongly accepted as monomial')
    # The nontrivial global phase from X;S must survive metadata construction.
    if compile_word(1,[('X',0),('S',0)])['constant']!=1: raise AssertionError('global phase lost')
    return dict(status='PASS',gate_words=words,basis_state_comparisons=states,
                rejected_nonmonomial_gate=True,retained_global_phase=True,
                scope='exact portable finite replay, not kernel proof or new kappa')


if __name__=='__main__':
    print(json.dumps(verify(),indent=2))
