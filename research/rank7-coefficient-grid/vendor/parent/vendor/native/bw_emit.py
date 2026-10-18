# Warp-aware copy of hpe_emit_local.py (GK / PR #433 lineage: icekylinx with Codex assistance; DreamingOfClouds with Claude Opus 5.5).
# BW: every change for anticipatory dirty borrowing (PR2226, Cinna Davis @1337isnot1337, with OpenAI Codex assistance) is marked "BW:".
# On a word without warps / zero buffers / twisted additions the behaviour equals hpe_emit_local.py.
"""Emit both local programs of a BORROW canonical word: scalar macros, climbs, centres, wrappers, monomial warps, zero buffers.

A warp event ['warp', r, op, f0, f1] is the rank-zero logical reference change K_G^{+-1} of register r moving it from
frame f0 to frame f1 (G(f0) = f1 for op > 0, G^-1(f0) = f1 for op < 0).  The same event stream serves both orientations:
the inverse-transpose of a monomial K_G is the monomial conj(K_G) (same permutation, conjugated phases), a different
formal symbol of the free operator algebra, and the exact column check of the physical product is run for both.
"""
if not __debug__:
    raise RuntimeError('assertions must remain enabled')   # every check of this stage is an assert
import sys as _sys, os as _os; _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import gzip,hashlib,json
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

OUT=Path(_sys.argv[1]);cp=OUT/'CANONICAL-WORD.json.gz'
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
def reg(x):return list(x) if isinstance(x,list) else ['L',x]   # BW: ['Z', c] is a private zero buffer
def dual(e):
    e=list(e)
    if e[0]=='add':e[1],e[2]=e[2],e[1];e[3]*=-1
    else:e[2],e[3]=e[3],e[2]
    return e
def scalar(e,back):
    e=dual(e) if back else list(e)
    if e[0]=='add':return ['add',reg(e[1]),reg(e[2]),e[3],e[4]]
    return ['scale',reg(e[1]),e[2],e[3]]
def primitive_bound(e):
    if e[0] in ('clear','copy'):return 1
    q=Q(e[3],e[4]) if e[0]=='add' else Q(e[2],e[3])
    a,b=abs(q.numerator),q.denominator
    assert b&(b-1)==0
    if e[0]=='scale':
        assert a&(a-1)==0
        return abs(a.bit_length()-b.bit_length())+int(q<0)
    return 3+(a.bit_length()-1)+a.bit_count()+(b.bit_length()-1)
def lregs(e):return [r for r in ([e[1]]+([e[2]] if e[0]=='add' else [])) if not isinstance(r,list)]

def expand(e):
    """BW: a twisted addition t += c*W(s) at frame zero: warp s by W, add, unwarp (all rank zero at frame 0)."""
    if e[0]!='tadd':return [e]
    _,t,s,word,a,b,f=e
    return [['warp',s,op,0,0] for op in reversed(word)]+[['add',t,s,a,b,0]]+[['warp',s,-op,0,0] for op in word]

def emit(back):
    out=[];cur=c['start'].copy()
    def event(e):out.append(e)
    def scal(e,f):event(['scalar',e,f])
    def warp(e):
        _,r,op,f0,f1=e
        if isinstance(r,list):assert r[0]=='Z' and f0==f1==1
        else:
            assert cur[r]==f0,('warp frame mismatch',r,cur[r],f0);cur[r]=f1
        event(['warp',reg(r),op,f0,f1])
    event(['phase','zero_frame_precondition'])
    for e0 in c['precondition']+c['compensation']:
        for e in expand(e0):
            if e[0]=='warp':warp(e);continue
            regs=lregs(e)
            assert all(c['start'][r]==0 for r in regs)
            scal(scalar(e,back),0)
    event(['phase','entry_adapters'])
    entering=[r for r,f in enumerate(c['start']) if r>=2*v and f!=0]
    hpe={r for r in range(2*v,n) if c['final'][r]!=1}
    wrapped=sorted(set(entering)|hpe)
    for r,f in enumerate(c['start']):
        if r in wrapped:event(['residual_adapter','pre',r,f]+([c['final'][r]] if c['final'][r]!=1 else []))
        else:event(['adapter','old_to_new',r,f])
    def climb(r,f,part):
        old=cur[r]
        if old==f:return
        assert basis(frames[old]+frames[f])==tuple(frames[f])
        rank=len(frames[f])-len(frames[old]);assert rank>0
        event(['climb',part,r,old,f,rank]);cur[r]=f
    for part in ('A','centers','B')+(('cleanup_tail',) if c.get('tail') else ())+('final',):
        event(['phase',part])
        if part in ('A','B','cleanup_tail'):
            for e in (c['tail'] if part=='cleanup_tail' else c[part]):
                if e[0]=='warp':warp(e);continue    # BW: monomial reference change, no climb
                for r in lregs(e):climb(r,e[-1],part)
                scal(scalar(e,back),e[-1])
        elif part=='centers':
            lv=lambda r:c.get('target_levels',{}).get(str(r-v),0)
            assert all(cur[r]==lv(r) for r in range(v,2*v))
            for k,r in enumerate(c['centers']):
                cf=c['center_frames'][k];assert cur[r]==cf
                terms=[e for e in c['cut'] if e[2]==r]
                path=[cf]+sorted({lv(e[1]) for e in terms}-{cf},key=lambda x:-len(frames[x]))
                C=['C',k]
                if not back:
                    scal(['clear',C],cf);scal(['copy',C,['L',r]],cf)
                    for a in range(len(path)):
                        if a>0:event(['center',k,path[a-1],path[a],len(frames[path[a-1]])-len(frames[path[a]])])
                        for e in terms:
                            if lv(e[1])==path[a]:scal(['add',['L',e[1]],C,e[3],e[4]],path[a])
                    scal(['clear',C],path[-1])
                else:
                    scal(['clear',C],path[-1])
                    for a in range(len(path)-1,-1,-1):
                        for e in terms:
                            if lv(e[1])==path[a]:scal(['add',C,['L',e[1]],e[3],e[4]],path[a])
                        if a>0:event(['center',k,path[a],path[a-1],len(frames[path[a-1]])-len(frames[path[a]])])
                    scal(['add',['L',r],C,-1,1],cf);scal(['clear',C],cf)
        else:
            for r,f in enumerate(c['final']):climb(r,f,part)
    event(['phase','exit_adapters'])
    for r,f in enumerate(c['final']):
        if r not in hpe:event(['adapter','new_to_old',r,f])
    event(['phase','full_frame_cleanup'])
    zb=c.get('zero_buffers',[])
    for z in zb:event(['zero_buffer','alloc',z])             # BW: private FULL-frame zero buffers stand in for the restored (hyperplane-ended) helpers
    for e in c['cleanup']:
        if e[0]=='warp':warp(e);continue
        regs=lregs(e)
        assert all(c['final'][r]==1 for r in regs)
        assert all(r[0]=='Z' and r[1] in zb for r in [e[1]]+([e[2]] if e[0]=='add' else []) if isinstance(r,list))
        scal(scalar(e,back),1)
    for z in zb:event(['zero_buffer','free',z])
    for r in wrapped:event(['residual_adapter','post',r,c['start'][r]]+([c['final'][r]] if r in hpe else []))
    event(['phase','done'])
    return out

def add_row(dst,src,q):
    for j,x in src.items():
        z=dst.get(j,Q(0))+q*x
        if z:dst[j]=z
        else:dst.pop(j,None)
def warp_row(row,op):
    out={}
    for (var,word),x in row.items():
        word=word[1:] if word and word[0]==-op else (op,)+word
        out[var,word]=x
    return out

def check_local(events,back):
    # BW: literal scalar replay of the emitted stream in the free warp algebra (rows over (register, warp word)), centres and zero buffers.
    state={('L',r):{(r,()):Q(1)} for r in range(n)};live=[];paid=Counter();prims=0;macros=0;zlive=set();nwarp=0
    for e in events:
        if e[0]=='climb':assert not live;paid[e[5]]+=1
        elif e[0]=='center':assert live==[e[1]];paid[e[4]]+=1
        elif e[0]=='zero_buffer':
            z=e[2]
            if e[1]=='alloc':assert z not in zlive;zlive.add(z);state['Z',z]={}
            else:assert not state['Z',z] and z in zlive;zlive.remove(z)
        elif e[0]=='warp':
            t=tuple(e[1]);nwarp+=1;state[t]=warp_row(state[t],e[2])
        elif e[0]=='scalar':
            op=e[1];tag=op[0];t=tuple(op[1]);macros+=1;prims+=2*primitive_bound(op)
            if tag=='clear':
                state[t]={}
                if t[0]=='C' and t[1] in live:live.remove(t[1])
            elif tag=='copy':state[t]={(var,w):x for (var,w),x in state.get(tuple(op[2]),{}).items()};live.append(t[1])
            elif tag=='scale':state[t]={j:Q(op[2],op[3])*x for j,x in state[t].items()}
            else:
                s=tuple(op[2]);q=Q(op[3],op[4]);row=state.setdefault(t,{})
                if t[0]=='C' and t[1] not in live:live.append(t[1])
                add_row(row,state.get(s,{}),q)
    assert not live and not zlive and all(not row for r,row in state.items() if r[0] in 'CZ')
    for r in range(n):
        expected={(r,()):Q(1)}
        if back and r<v:expected[(v+r,())]=Q(-1)
        elif not back and v<=r<2*v:expected[(r-v,())]=Q(1)
        assert state['L',r]==expected,('emitted column mismatch',back,r)
    assert dict(paid)=={int(r):z for r,z in c['local_profile'].items()}
    return {'sha256':digest(events),'events':len(events),'scalar_macros':macros,'warp_events':nwarp,
            'real_component_primitive_bound':prims,'paid_profile':dict(sorted(paid.items())),
            'all_columns':n,'private_centers_cleared':True,'private_coefficient_stream_cleared_after_each_macro':True,
            'zero_buffers_returned_to_zero':len(c.get('zero_buffers',[]))}

programs={};checks={}
for name,back in [('forward',False),('backward',True)]:
    programs[name]=emit(back);checks[name]=check_local(programs[name],back)
    print('PASS emitted',name,checks[name]['events'],'events',flush=True)

(OUT/'LOCAL-PROGRAMS.json.gz').write_bytes(gzip.compress(json.dumps(programs,sort_keys=True,separators=(',',':')).encode(),mtime=0))
(OUT/'LOCAL-CHECKS.json').write_text(json.dumps(checks,indent=2)+'\n')
