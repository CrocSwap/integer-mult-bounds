#!/usr/bin/env python3
"""Builder (NOT part of the independent audit): assembles the explicit chronological BORROW-WORD
(canonical coordinates, literal frames, explicit warps, explicit inverse-reverse cleanup) from
canonical word + borrow witness, following rp.py's replay order. audit_borrow.py re-derives
everything it trusts and never imports this file."""
import argparse,gzip,json,sys
from fractions import Fraction as Q
from pathlib import Path

def span(basis):
    s={0}
    for x in basis:s|={t^x for t in s.copy()}
    return frozenset(s)
def incident(e):return e[1:3] if e[0]=='add' else e[1:2]
def add(dst,src,c):
    for key,value in list(src.items()):
        z=dst.get(key,Q(0))+c*value
        if z:dst[key]=z
        elif key in dst:del dst[key]
def warp(row,op):
    out={}
    for (var,word),value in row.items():
        word=word[1:] if word and word[0]==-op else (op,)+word
        out[var,word]=value
    return out
def frame_basis(F):
    b={}
    for x in F:
        while x:
            j=x.bit_length()
            if j not in b:b[j]=x;break
            x^=b[j]
    return [b[j] for j in sorted(b,reverse=True)]
def frac(c):return c.numerator,c.denominator

def build(w,blocks,wit):
    pairs=wit['pairs'];gauss={r['operator']:r['G_columns'] for r in wit['gaussian']['records']}
    v=w['v'];n=2*v+w['R'];h=w['h'];full=span([1<<i for i in range(h)]);frames=list(map(span,w['frames']))
    lit=lambda idx:[int(x) for x in w['frames'][idx]]
    removed={x['register'] for x in pairs};active=[r for r in range(n) if r not in removed]
    val={r:{(r,()):Q(1)} for r in active};cur={r:frames[w['start'][r]] for r in active}
    out={k:[] for k in ('precondition','compensation','A','cut','B','restore')}
    sec=['precondition']
    corr=[]
    for term in wit['initial_corrections']:
        t=term['target'];s=term['source'];word=tuple(term['operator_word']);c=Q(term['coefficient'])
        add(val[t],{(s,word):Q(1)},c);corr.append(dict(term))
    warps=[];position={}
    def resolve(r):return mapping.get(r,r)
    mapping={}
    reverse=[]
    def climb(r,f):
        assert cur[r]<=f,('nonnest',r)
        cur[r]=f
    def scalar(e,framed=True,record=True,frame=None):
        rs=[resolve(r) for r in incident(e)]
        if any(r not in val for r in rs):return
        if framed:
            f=frames[e[-1]] if frame is None else frame
            for r in rs:climb(r,f)
        fl=None if not framed else (lit(e[-1]) if frame is None else frame_basis(frame))
        if e[0]=='add':
            c=Q(e[3],e[4]);add(val[rs[0]],val[rs[1]],c);g=['add',rs[0],rs[1],*frac(c),fl]
        else:
            c=Q(e[2],e[3]);val[rs[0]]={k:c*x for k,x in val[rs[0]].items()};g=['scale',rs[0],*frac(c),fl]
        out[sec[0]].append(g)
    original_target_levels={r:w['start'][r] for r in range(v,2*v)}
    for e in w['precondition']+w['compensation']:
        for r in incident(e):
            if v<=r<2*v:original_target_levels[r]=e[-1]
    sec[0]='precondition'
    for e in w['precondition']:scalar(e,record=False)
    sec[0]='compensation'
    for e in w['compensation']:
        if e[0]=='add' and e[2] in removed:continue
        scalar(e,record=False)
    sec[0]='A'
    for e in w['A']:scalar(e)
    for r,f in original_target_levels.items():climb(r,frames[f])
    target_levels={str(r-v):w['frames'][f] for r,f in original_target_levels.items() if w['frames'][f]}
    for r,f in zip(w['centers'],w['center_frames']):assert cur[r]==frames[f]
    sec[0]='cut'
    for e in w['cut']:scalar(e,framed=False,record=False)
    sec[0]='B'
    B=out['B']
    deferred={};skip=set()
    for b in blocks:
        ss=set(b['helpers']);part=[]
        for i in range(b['first_correction'],b['first_input']):
            e=w['B'][i]
            if set(incident(e))<=ss:part.append(e);skip.add(i)
        deferred[b['first_input']]=part
    starts={}
    for i,x in enumerate(pairs):starts.setdefault(x.get('handoff_B',x['deadline']),[]).append((i+1,x))
    removed_early_echoes={i for x in pairs if x['low'] for i in x.get('deleted_prefix_indices',x['deleted_echo_indices'])}
    early_rewrites={int(i):gates for x in pairs if x['low'] for i,gates in x.get('early_prefix_rewrites',{}).items()}
    early_tail={}
    for e in wit.get('early_tail_events',[]):early_tail.setdefault(e['before_B'],[]).append(e['gate'])
    for i,e in enumerate(w['B']):
        for t in early_tail.get(i,[]):scalar(t)
        if i in starts:
            for op,x in starts[i]:
                old=x['borrow_from'];new=x['register'];assert x['retirement_B_event']<i
                F1=None
                for j in range(i,len(w['B'])):
                    gl=list(deferred.get(j,[]))+list(early_rewrites.get(j,[]))
                    if j not in skip and j not in removed_early_echoes:gl.append(w['B'][j])
                    for g in gl:
                        if new in incident(g):F1=frames[g[-1]];break
                    if F1 is not None:break
                du=len(cur[old]).bit_length()-1
                fb=frame_basis(F1);E_basis=fb[:du] if len(fb)>=du else fb;E=span(E_basis)
                assert len(E_basis)==du,'paid handoff not supported'
                assert x['handoff_basis']==E_basis or span(x['handoff_basis'])==E,(op,)
                warps.append([len(B),old,gauss[op],frame_basis(cur[old]),E_basis,op])
                val[old]=warp(val[old],op);cur[old]=E;mapping[new]=old
                for target,c in x.get('handoff_echo_coefficients',{}).items():
                    target=int(target);climb(target,E);add(val[target],val[old],Q(c));raise NotImplementedError('echo')
        for d in deferred.get(i,[]):scalar(d)
        for d in early_rewrites.get(i,[]):scalar(d)
        if i not in skip and i not in removed_early_echoes:scalar(e)
    for t in early_tail.get(len(w['B']),[]):scalar(t)
    for r in range(v,2*v):climb(r,frames[w['final'][r]])
    return dict(w=w,out=out,corr=corr,warps=warps,val=val,cur=cur,removed=removed,active=active,frames=frames,
                full=full,target_levels=target_levels,n=n,v=v,h=h,mapping=mapping)

def finish(S,cold_restore=True):
    """cold restoration (rp.py semantics, exact modular nomination replaced by direct exact solve)."""
    w=S['w'];v=S['v'];n=S['n'];h=S['h'];val=S['val'];cur=S['cur'];frames=S['frames'];full=S['full'];active=S['active']
    out=S['out']
    def dyadic(q):return q.denominator&(q.denominator-1)==0
    def unit(q):return q and dyadic(q) and abs(q.numerator)&(abs(q.numerator)-1)==0
    cold=[r for r in active if not(v<=r<2*v) and len(w['frames'][w['final'][r]])<h]
    prime=65521;cache={};clearable=[]
    for c in cold:
        V=frames[w['final'][c]]
        pool=tuple(r for r in active if not(v<=r<2*v) and cur[r]<=V<=frames[w['final'][r]])
        if pool not in cache:
            piv={}
            for r in pool:
                x={k:(q.numerator*pow(q.denominator,-1,prime))%prime for k,q in val[r].items()}
                while x:
                    j=min(x)
                    if j not in piv:
                        z=pow(x[j],-1,prime);piv[j]={k:t*z%prime for k,t in x.items()};break
                    z=x[j]
                    for k,t in piv[j].items():
                        y=(x.get(k,0)-z*t)%prime
                        if y:x[k]=y
                        elif k in x:del x[k]
            cache[pool]=piv
        x={(c,()):1};piv=cache[pool]
        while x:
            j=min(x)
            if j not in piv:break
            z=x[j]
            for k,t in piv[j].items():
                y=(x.get(k,0)-z*t)%prime
                if y:x[k]=y
                elif k in x:del x[k]
        if not x:
            dependents=[r for r in active if not(v<=r<2*v) and any(var==c for var,word in val[r])]
            if all(cur[r]<=V and all(not word for var,word in val[r] if var==c) for r in dependents):clearable.append(c)
    def exact_combination(pool,goal):
        piv={}
        for r in pool:
            x=dict(val[r]);code={r:Q(1)}
            while x:
                j=min(x)
                if j not in piv:
                    z=x[j];piv[j]=({k:t/z for k,t in x.items()},{k:t/z for k,t in code.items()});break
                row,coeff=piv[j];z=x[j];add(x,row,-z);add(code,coeff,-z)
        x=dict(goal);code={}
        while x:
            j=min(x)
            if j not in piv:return None
            row,coeff=piv[j];z=x[j];add(x,row,-z);add(code,coeff,z)
        return code
    def climb(r,f):
        assert cur[r]<=f;cur[r]=f
    R=out['restore'];restored=[]
    def emit(g):R.append(g)
    def gate_add(d,s,c,V):
        climb(d,V);climb(s,V);add(val[d],val[s],c);emit(['add',d,s,*frac(c),frame_basis(V)])
    for c in sorted(clearable,key=lambda r:(len(frames[w['final'][r]]),r)):
        V=frames[w['final'][c]]
        pool=[r for r in active if not(v<=r<2*v) and r not in restored and cur[r]<=V]
        sol=exact_combination(pool,{(c,()):Q(1)})
        if sol is None or not all(dyadic(z) for z in sol.values()):continue
        pivot=c if unit(sol.get(c,Q(0))) else next((r for r,z in sol.items() if unit(z)),None)
        if pivot is None:continue
        for r in set(sol)|{c}:climb(r,V)
        factor=sol[pivot]
        if factor!=1:
            val[pivot]={k:factor*z for k,z in val[pivot].items()};emit(['scale',pivot,*frac(factor),frame_basis(V)])
        for r,z in sol.items():
            if r!=pivot:gate_add(pivot,r,z,V)
        if pivot!=c:
            val[c],val[pivot]=val[pivot],val[c]
            fb=frame_basis(V)
            emit(['add',c,pivot,1,1,fb]);emit(['add',pivot,c,-1,1,fb]);emit(['add',c,pivot,1,1,fb]);emit(['scale',pivot,-1,1,fb])
        assert val[c]=={(c,()):Q(1)}
        for r in active:
            if v<=r<2*v or r==c:continue
            z=val[r].get((c,()),Q(0))
            if z:gate_add(r,c,-z,V)
        restored.append(c)
    S['restored']=restored
    return S

def assemble(S,base_name):
    w=S['w'];v=S['v'];n=S['n'];h=S['h'];frames=S['frames'];out=S['out'];full=S['full']
    FULLB=frame_basis(full)
    restored=S['restored'];fb=lambda r:frame_basis(frames[w['final'][r]])
    word=dict(kind='BORROW-WORD',base=base_name,
      ports=w['ports'],centers=w['centers'],center_frames=[w['frames'][f] for f in w['center_frames']],
      target_levels=S['target_levels'],
      start_extra={str(r):w['frames'][w['start'][r]] for r in range(2*v,n) if r not in S['removed'] and w['frames'][w['start'][r]]},
      helper_final={str(r):fb(r) for r in sorted(restored)},
      removed=sorted(S['removed']),
      initial_corrections=S['corr'],
      precondition=out['precondition'],compensation=out['compensation'],A=out['A'],cut=out['cut'],B=out['B'],
      restore=out['restore'],
      warps=[x[:5] for x in sorted(S['warps'],key=lambda x:x[5])],
      warp_order=[x[5] for x in sorted(S['warps'],key=lambda x:x[5])],
      report=dict(v=v,h=h,R=w['R']))
    return word
