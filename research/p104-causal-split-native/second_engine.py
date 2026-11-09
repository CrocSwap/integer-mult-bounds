#!/usr/bin/env python3
"""Second value engine: the word replayed on a random vector mod 2^61-1 (standard library), independently of the Fraction replay of check.py. The clean word has 0 bad rows; mutants (x2, deleted, negated) on sampled events touching second mains and cross-plane helpers must all be rejected. usage: second_engine.py WORD.json.gz"""
import gzip,json,sys,random
from fractions import Fraction as Q
W=json.load(gzip.open(sys.argv[1],'rt'));P=2**61-1;n=len(W['initial']);NR=n+W['owned_fields'];H=W['hosted'];X2=H['X2'];Y2=H['Y2'];live=set(W['live'])
fm=lambda s:(lambda q:q.numerator%P*pow(q.denominator,P-2,P)%P)(Q(s))
prog=[[e[0],e[1],e[2] if e[0] in('ADD','COPY') else None,fm(e[3] if e[0] in('ADD','COPY') else e[2]) if e[0] in('ADD','COPY','SCALE') else 0] for e in W['program']]
rnd=random.Random(99);inp=[rnd.randrange(P) for _ in range(n)]
ex=list(inp)+[0]*W['owned_fields']
DP=set(H['Dports']);hf=fm('1/2')
for i,r in enumerate(W['live']):
    if i in DP:ex[r+112]=(inp[r+112]+inp[r])%P
    else:ex[r+112]=hf*(inp[r+112]+inp[r])%P;ex[r]=(inp[r]-inp[r+112])%P
for a,b in zip(X2,Y2):ex[a]=(inp[a]-inp[b])%P
def run(pr):
    S=list(inp)+[0]*W['owned_fields']
    for o,r,s,c in pr:
        if o=='ADD':S[r]=(S[r]+c*S[s])%P
        elif o=='SCALE':S[r]=S[r]*c%P
        elif o in('INIT','CLEAR'):S[r]=0
        elif o=='COPY':S[r]=c*S[s]%P
    return sum(a!=b for a,b in zip(S,ex))
print('clean bad',run(prog));assert run(prog)==0
xs=set(X2);ys=set(Y2);cl={}
for i,e in enumerate(prog):
    if e[0]=='ADD':
        k=('X2' if e[1] in xs else 'Y2' if e[1] in ys else 'o','X2' if e[2] in xs else 'Y2' if e[2] in ys else 'o')
        if k!=('o','o'):cl.setdefault(k,[]).append(i)
acc=0;tot=0
for k,ix in cl.items():
    for i in rnd.sample(ix,min(6,len(ix))):
        for mode in('x2','del','neg'):
            pr=list(prog);e=list(prog[i])
            if mode=='del':del pr[i]
            else:
                e[3]=e[3]*2%P if mode=='x2' else (P-e[3])%P;pr[i]=e
            b=run(pr);tot+=1;acc+=b==0
print('classes',{k:len(v) for k,v in cl.items()},'mutants',tot,'accepted',acc);assert acc==0;print('PASS_SECOND_ENGINE')
