# Adapted from PR425 by icekylinx with Codex assistance.
"""Emit both local programs, integrate the fixed nine-stage geometry, and bill.

The expanded scalar interface is justified in PROOF.txt. This script does not
claim a Lean proof or discharge the inherited all-size/analytic interfaces.
"""
import copy,gzip,hashlib,importlib.util,json,math
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

OUT=Path('split-centres');cp=OUT/'CANONICAL-WORD.json.gz'
c=json.load(gzip.open(cp))
frames=c['frames'];v,R,h=c['v'],c['R'],c['h'];n=2*v+R
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def basis(vs):
    b={}
    for x in vs:
        for p in sorted(b,reverse=True):
            if x>>p&1:x^=b[p]
        if x:
            p=x.bit_length()-1
            for q in b:
                if b[q]>>p&1:b[q]^=x
            b[p]=x
    return tuple(b[p] for p in sorted(b,reverse=True))
def dual(e):
    e=list(e)
    if e[0]=='add':e[1],e[2]=e[2],e[1];e[3]*=-1
    else:e[2],e[3]=e[3],e[2]
    return e
def scalar(e,back):
    e=dual(e) if back else list(e)
    if e[0]=='add':return ['add',['L',e[1]],['L',e[2]],e[3],e[4]]
    return ['scale',['L',e[1]],e[2],e[3]]
def primitive_bound(e):
    if e[0] in ('clear','copy'):return 1
    q=Q(e[3],e[4]) if e[0]=='add' else Q(e[2],e[3])
    a,b=abs(q.numerator),q.denominator
    assert b&(b-1)==0
    if e[0]=='scale':
        assert a&(a-1)==0
        return abs(a.bit_length()-b.bit_length())+int(q<0)
    # Exact binary Horner multiplication on a cleared private stream, repeated
    # halving, signed accumulation into the target, then clear the private stream.
    return 3+(a.bit_length()-1)+a.bit_count()+(b.bit_length()-1)

def emit(back):
    out=[];cur=c['start'].copy()
    def event(e):out.append(e)
    def scal(e,f):event(['scalar',e,f])
    event(['phase','zero_frame_precondition'])
    for e in c['precondition']+c['compensation']:
        regs=[e[1]]+([e[2]] if e[0]=='add' else [])
        assert all(c['start'][r]==0 for r in regs)
        scal(scalar(e,back),0)
    event(['phase','entry_adapters'])
    for r,f in enumerate(c['start']):event(['adapter','old_to_new',r,f])
    def climb(r,f,part):
        old=cur[r]
        if old==f:return
        assert basis(frames[old]+frames[f])==tuple(frames[f])
        rank=len(frames[f])-len(frames[old]);assert rank>0
        event(['climb',part,r,old,f,rank]);cur[r]=f
    for part in ('A','centers','B','final'):
        event(['phase',part])
        if part in ('A','B'):
            for e in c[part]:
                regs=[e[1]]+([e[2]] if e[0]=='add' else [])
                for r in regs:climb(r,e[-1],part)
                scal(scalar(e,back),e[-1])
        elif part=='centers':
            assert all(cur[r]==0 for r in range(v,2*v))
            for k,r in enumerate(c['centers']):
                cf=c['center_frames'][k];rank=len(frames[cf]);assert cur[r]==cf
                C=['C',k];scal(['clear',C],0 if back else cf)
                terms=[e for e in c['cut'] if e[2]==r]
                if back:
                    for e in terms:scal(['add',C,['L',e[1]],e[3],e[4]],0)
                else:scal(['copy',C,['L',r]],cf)
                event(['center',k,0 if back else cf,cf if back else 0,rank])
                if back:scal(['add',['L',r],C,-1,1],cf)
                else:
                    for e in terms:scal(['add',['L',e[1]],C,e[3],e[4]],0)
                scal(['clear',C],cf if back else 0)
        else:
            for r,f in enumerate(c['final']):climb(r,f,part)
    event(['phase','exit_adapters'])
    for r,f in enumerate(c['final']):event(['adapter','new_to_old',r,f])
    event(['phase','full_frame_cleanup'])
    for e in c['cleanup']:
        regs=[e[1]]+([e[2]] if e[0]=='add' else [])
        assert all(c['final'][r]==1 for r in regs)
        scal(scalar(e,back),1)
    event(['phase','done'])
    return out

def check_local(events,back):
    # Literal scalar replay of the emitted stream, including center lifetimes.
    state={('L',r):{r:Q(1)} for r in range(n)};live=[];paid=Counter();prims=0;macros=0
    for e in events:
        if e[0]=='climb':assert not live;paid[e[5]]+=1
        elif e[0]=='center':assert live==[e[1]];paid[e[4]]+=1
        elif e[0]=='scalar':
            op=e[1];tag=op[0];t=tuple(op[1]);macros+=1;prims+=2*primitive_bound(op)
            if tag=='clear':
                state[t]={}
                if t[0]=='C' and t[1] in live:live.remove(t[1])
            elif tag=='copy':state[t]=dict(state.get(tuple(op[2]),{}));live.append(t[1])
            elif tag=='scale':state[t]={j:Q(op[2],op[3])*x for j,x in state[t].items()}
            else:
                s=tuple(op[2]);q=Q(op[3],op[4]);row=state.setdefault(t,{})
                if t[0]=='C' and t[1] not in live:live.append(t[1])
                for j,x in list(state.get(s,{}).items()):
                    z=row.get(j,Q(0))+q*x
                    if z:row[j]=z
                    else:row.pop(j,None)
    assert not live and all(not row for r,row in state.items() if r[0]=='C')
    for r in range(n):
        expected={r:Q(1)}
        if back and r<v:expected[v+r]=Q(-1)
        elif not back and v<=r<2*v:expected[r-v]=Q(1)
        assert state['L',r]==expected,('emitted column mismatch',back,r)
    assert dict(paid)=={int(r):z for r,z in c['local_profile'].items()}
    return {'sha256':digest(events),'events':len(events),'scalar_macros':macros,
            'real_component_primitive_bound':prims,'paid_profile':dict(sorted(paid.items())),
            'all_columns':n,'private_centers_cleared':True,'private_coefficient_stream_cleared_after_each_macro':True}

programs={};checks={}
for name,back in [('forward',False),('backward',True)]:
    programs[name]=emit(back);checks[name]=check_local(programs[name],back)
    print('PASS emitted',name,checks[name]['events'],'events',flush=True)


(OUT/'LOCAL-PROGRAMS.json.gz').write_bytes(gzip.compress(json.dumps(programs,sort_keys=True,separators=(',',':')).encode(),mtime=0))
(OUT/'LOCAL-CHECKS.json').write_text(json.dumps(checks,indent=2)+'\n')
