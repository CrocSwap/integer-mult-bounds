#!/usr/bin/env python3
"""Raw budget of the mix word: package ordinary.py formulas; native per-call once; caller, thin, output, adapter terms are per port so weighted nD/104 and (104-nD)/104. second-main boundary terms per D port."""
import gzip,json,sys
from fractions import Fraction as Q
from collections import Counter
W=json.load(gzip.open(sys.argv[1],'rt'));H=W['hosted'];nD=len(H['Dports'])
def swaps(sel,dim):
    wanted=set(range(len(sel)));return len(list(zip(sorted(set(sel)-wanted),sorted(wanted-set(sel)))))
n=len(W['initial']);live=set(W['live']);main=live|{r+112 for r in live}|set(H['X2'])|set(H['Y2'])
fr=W['frames'];dim=[len(b) for b in fr];paid=Counter(abs(dim[e[3]]-dim[e[2]]) for e in W['program'] if e[0]=='MOVE');hel=Counter(dim[W['final'][r]]-dim[W['initial'][r]] for r in range(n) if r not in main);life=sum(e[0]=='INIT' for e in W['program'])
allow=upper=0
for e in W['program']:
    if e[0] in('INIT','CLEAR'):allow+=2
    elif e[0]=='SCALE':
        q=Q(e[2]);a,d=abs(q.numerator),q.denominator;allow+=2*(abs(a.bit_length()-d.bit_length())+int(q<0));upper+=4*(a.bit_length()+d.bit_length()+1)
    elif e[0] in('ADD','COPY'):
        q=Q(e[3]);a,d=abs(q.numerator),q.denominator;allow+=2*(3+a.bit_length()-1+a.bit_count()+d.bit_length()-1);upper+=4*(a.bit_length()+a.bit_count()+d.bit_length()+1)
routes=(sum(paid.values())+2*sum(hel.values())+208+2*nD+4*104+4*nD+4*life)*1000
def rest(C,ports):
    ev=C['events'];roles=C['roles'];amb=C['ambient_rank'];mx=mn=mp=0
    for role,(qp,zero,*sel) in enumerate(C['diagonal']):
        axes=([0] if qp else [])+[a for st,y in enumerate(sel,1) if y for a in range(9+8*(st-1),9+8*st)];k=swaps(axes,amb);mx+=2*k*ports;mn+=2*bool(qp)*ports;mp+=int(qp==-1)*ports
    ie=0;qn=qph=0
    for e in ev:
        if e[0]=='IDLE_ONE':ie+=2*swaps([a for st in e[2] for a in range(9+8*(st-1),9+8*st)],amb)*ports
        elif e[0]=='QUERY':qn+=2*ports;qph+=int(e[3]==-1)*ports
    return 32*roles*ports*len(ev)+sum(e[0]=='QUERY' for e in ev)*16*ports+roles*ports*26+(mx+mn+mp)*1000+ie*1000+(qn+qph)*1000
J=json.load(open(sys.argv[2]))
def shim(ty):
    t=J['types'][ty];off=t['offset'];ev=[]
    for e in J['events']:
        if e[0]=='J':ev.append(['HOST',e[1]])
        elif e[0]==ty:
            e=list(e[1:])
            if e[0] in('ADD','SWAP','QUERY'):e[1]-=off;e[2]-=off
            else:e[1]-=off
            ev.append(e)
    return dict(events=ev,roles=t['roles'],ambient_rank=J['ambient_rank'],diagonal=t['diagonal'])
assert len(J['types']['A']['ports'])==nD
r=rest(shim('A'),nD)+rest(shim('B'),104-nD)
print('per call allowance+routes',allow+routes,'upper+routes',upper+routes,'rest',r);print('RAW literal',18*10**7+r,18*10**7+r<10**9);print('RAW actual',18*(allow+routes)+r,18*(allow+routes)+r<10**9);print('RAW upper',18*(upper+routes)+r,18*(upper+routes)+r<10**9)
