"""Finite just-in-time single-source cache/gauge census. Apache-2.0.
Prepared for @woklerx with substantial OpenAI Codex assistance.
"""
from collections import Counter
from fractions import Fraction as F
from itertools import product
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SRC='research/complex-factory-scale-frontier27/sources/PR924-COMPOSITION.json'

def exp(q):
    q=abs(q)
    if not(q and q.numerator&(q.numerator-1)==0 and q.denominator&(q.denominator-1)==0):raise ValueError('not power of two')
    return q.numerator.bit_length()-q.denominator.bit_length()

def normalize(raw):
    scale=[F(1)]*8;adds=[];uses=[0]*8;slots={}
    for op in raw:
        if op[0]=='scale':
            _,r,a,b,frame=op;scale[r]*=F(a,b);slots[r]=uses[r]
        else:
            _,d,s,a,b,frame=op
            c=F(a,b)*scale[s]/scale[d]
            adds.append((d,s,c));uses[d]+=1;uses[s]+=1
    return adds,scale,uses,slots

def materialize(adds,totals,slots):
    scales=[F(1)]*8;seen=[0]*8;done=set();out=[]
    for d,s,c in adds:
        for r in sorted((d,s)):
            if r in slots and r not in done and seen[r]==slots[r]:
                out.append(['scale',r,totals[r]]);scales[r]=totals[r];done.add(r)
        out.append(['add',d,s,c*scales[d]/scales[s]])
        seen[d]+=1;seen[s]+=1
    for r in sorted(slots):
        if r not in done:out.append(['scale',r,totals[r]])
    return out

def compile_word(macros,mode):
    if mode not in ('per_add','clean','defer','cache'):raise ValueError('mode')
    for op in macros:
        if op[0] not in ('add','scale') or type(op[1]) is not int or not 0<=op[1]<8:raise ValueError('work alias or gate')
        if op[0]=='add' and(type(op[2])is not int or not 0<=op[2]<8 or op[1]==op[2]):raise ValueError('source alias')
    out=[];cache=None;reuses=[];zero=False
    # Existing work register W=8 is arbitrary on entry. COPY overwrites it;
    # entry dirt is never read. Every emitted program ends in paid CLEAR.
    for k,op in enumerate(macros):
        if op[0]=='scale':
            _,r,c=op;e=exp(c)
            out += [[('double' if e>0 else 'half'),r]]*abs(e)
            if c<0:out.append(['neg',r])
            if cache is not None and cache[0]==r:
                cache=(r,cache[1]-e,cache[2]*(-1 if c<0 else 1))
            continue
        _,d,s,c=op;e=exp(c);sign=1 if c>0 else -1
        if e==0:
            out.append(['plus' if sign>0 else 'minus',d,s])
            if cache is not None and cache[0]==d:cache=None
        else:
            use_cache=(mode=='cache' and cache is not None and cache[0]==s
                       and abs(e-cache[1])<1+abs(e))
            if use_cache:
                delta=e-cache[1];work_sign=cache[2]
                reuses.append(k)
            else:
                out.append(['copy',8,s]);delta=e;work_sign=1
            out += [[('double' if delta>0 else 'half'),8]]*abs(delta)
            out.append(['plus' if sign*work_sign>0 else 'minus',d,8])
            cache=(s,e,work_sign);zero=False
        if mode=='per_add':out.append(['clear',8]);cache=None;zero=True
        elif mode=='clean':
            if e!=0 or not zero:out.append(['clear',8]);cache=None;zero=True
        elif mode not in ('cache','defer'):raise ValueError('mode')
    if not zero:out.append(['clear',8])
    return out,reuses

def census(raw):
    adds,totals,uses,old=normalize(raw)
    wires=[0,1,2,6,7];hist={m:Counter()for m in ('per_add','clean','defer','cache')};best={}
    for tup in product(*(range(uses[r]+1)for r in wires)):
        slots=dict(zip(wires,tup));slots[5]=23%8
        word=materialize(adds,totals,slots)
        for mode in hist:
            stream,reuses=compile_word(word,mode);cost=len(stream);hist[mode][cost]+=1
            if mode not in best or cost<best[mode]['cost']:
                best[mode]={'cost':cost,'slots':slots,'reuses':reuses,'stream':stream,'winners':[]}
            if cost==best[mode]['cost']:best[mode]['winners'].append(slots)
    original=[(['add',op[1],op[2],F(op[3],op[4])] if op[0]=='add' else ['scale',op[1],F(op[2],op[3])])for op in raw]
    return {'uses':uses,'original_slots':old,'count':sum(hist['cache'].values()),'histograms':{m:dict(sorted(h.items()))for m,h in hist.items()},'best':best,'original_costs':{m:len(compile_word(original,m)[0])for m in hist}}


def variants(raw):
    def inv(word):
        result=[]
        for op in reversed(word):
            p=op.copy()
            if p[0]=='add':p[3]=-p[3]
            else:p[2],p[3]=p[3],p[2]
            result.append(p)
        return result
    def dual(word):
        result=[]
        for op in word:
            p=op.copy()
            if p[0]=='add':p[1],p[2],p[3]=p[2],p[1],-p[3]
            else:p[2],p[3]=p[3],p[2]
            result.append(p)
        return result
    return {'forward':raw,'inverse':inv(raw),'inverse_transpose':dual(raw),'transpose':dual(inv(raw))}


def search(raw):
    return {name:census(word)for name,word in variants(raw).items()}
