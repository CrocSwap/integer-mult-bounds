"""e8clean local program: #390's dirty-preconditioned bracket (target precancellation, helper prewhitening, main,
FULL repair of non-sink helpers only), recomputed for our word, with the bank padding C on coordinate 72 FUSED
into the final climb of each new zero-row sink helper.  Own code (reads #352/#390 only as data/spec).
Events: ('phase',p) ('adapter',kind,r,f) ('climb',phase,r,old,new,rank) ('climb_pad72',r,old,new,rank_local,rank_paid)
        ('center',k,old,new,rank) ('scalar',phase,op,frame).  Streams: ('L',i) live, ('C',k) centre, ('W',0) coefficient."""
import json,gzip
from fractions import Fraction as Fr
from collections import Counter
def frac(a,b): return Fr(a,b)
V,R=120,783; N=2*V+R
def role(r): return 'X' if r<V else 'Y' if r<2*V else 'S'
def gate_adds(g):
    if g[0]=='out': return [(t,g[2],Fr(a,b)) for t,a,b in g[3]]
    return [(g[2],s,Fr(a,b)) for s,a,b in g[3]]
def gate_regs(g):
    return [g[2]]+[x[0] for x in g[3]]+(list(g[4]) if g[0]=='out' else [])
def scat_table(c):
    return [{k:Fr(a,b) for k,a,b in row} for row in c['scat']['table']]
def replay_main(c,init):
    """exact replay of A, scatter (forward semantics), B on sparse column dicts"""
    reg=[dict(init.get(r,{})) for r in range(N)]; tab=scat_table(c)
    def axpy(t,src,q):
        d=reg[t]
        for k,x in src.items():
            z=d.get(k,0)+q*x
            if z: d[k]=z
            else: d.pop(k,None)
    for ph in 'AB':
        if ph=='B':
            tot=[dict(reg[s]) for _,s,_ in sorted(c['ret'])]
            for t in range(V):
                for k,q in tab[t].items(): axpy(V+t,tot[k],q)
        for g in c[ph]:
            if g[0]=='out':
                src=dict(reg[g[2]])
                for t,s,q in gate_adds(g): axpy(t,src,q)
            else:
                for t,s,q in gate_adds(g): axpy(t,reg[s],q)
    return reg
def prewhite(c,sinks):
    """returns (pre_target, pre_helper, post_repair) as lists of (t,s,Fraction)"""
    hh=[(t,s,q) for ph in 'AB' for g in c[ph] for t,s,q in gate_adds(g) if role(t)=='S' and role(s)=='S']
    pre_helper=[(t,s,-q) for t,s,q in reversed(hh)]
    # A^{-1} e_j by literal subword, then B (helper->Y block) applied: replay main from helper column u_j with x=y=0
    reg={}
    cols={j:{j:Fr(1)} for j in range(2*V,N)}
    st=[dict() for _ in range(N)]
    for j in range(2*V,N): st[j]={j:Fr(1)}
    for t,s,q in pre_helper:
        for k,x in st[s].items():
            z=st[t].get(k,0)+q*x
            if z: st[t][k]=z
            else: st[t].pop(k,None)
    # st[h] = row h of A^{-1} acting on original columns; now run main on these helper values (x=y=0)
    out=replay_main(c,{h:st[h] for h in range(2*V,N)})
    pre_target=[]
    for y in range(V,2*V):
        for k,x in sorted(out[y].items()): pre_target.append((y,k,-x))   # y -= (B A^-1 h)
        # helper part of main from preconditioned helpers must be identity:
    for h in range(2*V,N): assert out[h]=={h:Fr(1)}, ('A A^-1 != I',h)
    xo=replay_main(c,{t:{t:Fr(1)} for t in range(V)})
    post=[]
    for h in range(2*V,N):
        if h in sinks: assert not xo[h],('sink row nonzero',h); continue
        for s,x in sorted(xo[h].items()): post.append((h,s,-x))
    return pre_target,pre_helper,post
def lift(t,s,q,ori):
    return ('add',('L',t),('L',s),q) if ori=='forward' else ('add',('L',s),('L',t),-q)
def emit(c,ori,hetero,fused,pw):
    """hetero: {helper: endpoint frame} (#390 rank-8 sinks, no final lift); fused: set of zero-row sinks whose
    final climb carries the bank padding C_72."""
    pre_target,pre_helper,post=pw; fr=c['frames']; dim=[len(f) for f in fr]
    final=list(c['final'])
    for r,f in hetero.items(): final[r]=f
    cur=list(c['start']); tab=scat_table(c)
    yield ('phase','old_response')
    for t,s,q in pre_target+pre_helper: yield ('scalar','old_response',lift(t,s,q,ori),'old0')
    yield ('phase','ad0')
    for r,f in enumerate(c['start']): yield ('adapter','old_to_new',r,f)
    for ph in ['A','centers','B']:
        yield ('phase',ph)
        if ph=='centers':
            for k,r,f in sorted(c['ret']):
                C=('C',k)
                yield ('scalar','main',('clear',C),f if ori=='forward' else 0)
                if ori=='forward': yield ('scalar','main',('add',C,('L',r),Fr(1)),f)
                else:
                    for t in range(V):
                        if k in tab[t]: yield ('scalar','main',('add',C,('L',V+t),tab[t][k]),0)
                yield ('center',k,f if ori=='forward' else 0,0 if ori=='forward' else f,dim[f])
                if ori=='forward':
                    for t in range(V):
                        if k in tab[t]: yield ('scalar','main',('add',('L',V+t),C,tab[t][k]),0)
                else: yield ('scalar','main',('add',('L',r),C,Fr(-1)),f)
                yield ('scalar','main',('clear',C),0 if ori=='forward' else f)
            continue
        for g in c[ph]:
            for r in gate_regs(g):
                if cur[r]!=g[1]:
                    yield ('climb',ph,r,cur[r],g[1],dim[g[1]]-dim[cur[r]]); cur[r]=g[1]
            for t,s,q in gate_adds(g): yield ('scalar','main',lift(t,s,q,ori),g[1])
    yield ('phase','final')
    for r,f in enumerate(final):
        if cur[r]!=f:
            if r in fused: yield ('climb_pad72',r,cur[r],f,dim[f]-dim[cur[r]],dim[f]-dim[cur[r]]+1)
            else: yield ('climb','final',r,cur[r],f,dim[f]-dim[cur[r]])
            cur[r]=f
    yield ('phase','adF')
    for r,f in enumerate(final):
        yield ('adapter','canonical_to_bank_residual' if r in hetero else 'new_to_old',r,f)
    yield ('phase','cleanup')
    for t,s,q in post: yield ('scalar','cleanup',lift(t,s,q,ori),'old1')
    yield ('phase','done')
PHASES=['old_response','ad0','A','centers','B','final','adF','cleanup','done']
def nested(fr,a,b):
    def red(u,B):
        for x in B:
            if u>>(x.bit_length()-1)&1: u^=x
        return u
    return all(red(u,fr[b])==0 for u in fr[a])
def validate(events,c,ori,hetero,fused):
    """independent exact replay on all 1023 live columns + label/lifetime/fusion rules"""
    fr=c['frames']; dim=[len(f) for f in fr]; final=list(c['final'])
    for r,f in hetero.items(): final[r]=f
    cur=list(c['start']); reg={('L',i):{i:Fr(1)} for i in range(N)}; seen=[]; phase=None
    hist=Counter(); paid=Counter(); fusedone=set(); centers=set(); counts=Counter(); edges=set()
    for ev in events:
        counts[ev[0]]+=1
        if ev[0]=='phase':
            phase=ev[1]; seen.append(phase); assert seen==PHASES[:len(seen)],'chronology'
            if phase=='adF': assert cur==final,'final climbs'
            continue
        if ev[0]=='adapter':
            assert (phase=='ad0' and ev[1]=='old_to_new') or (phase=='adF' and ev[1] in ('new_to_old','canonical_to_bank_residual')); continue
        if ev[0] in ('climb','climb_pad72'):
            if ev[0]=='climb': _,p,r,o,f,d=ev; assert p==phase
            else:
                _,r,o,f,d,dp=ev; assert phase=='final' and r in fused and dp==d+1 and f==1; fusedone.add(r)
            assert r not in fusedone or ev[0]=='climb_pad72'
            assert cur[r]==o and d==dim[f]-dim[o]>0 and nested(fr,o,f),'child'
            assert not centers,'centre live during child'
            cur[r]=f; hist[d]+=1; paid[d if ev[0]=='climb' else d+1]+=1; edges.add((o,f)); continue
        if ev[0]=='center':
            _,k,o,f,d=ev; assert phase=='centers' and centers=={('C',k)}; hist[d]+=1; paid[d]+=1; continue
        assert ev[0]=='scalar'; _,p,e,f=ev
        assert p==('main' if phase in ('A','centers','B') else phase)
        tgt=e[1]; src=e[2] if e[0]=='add' else None
        for x in [tgt]+([src] if src else []):
            if x[0]=='L':
                i=x[1]; assert i not in fusedone,'fused sink touched after its padded climb'
                if phase=='old_response': assert f=='old0' and role(i) in ('Y','S')
                elif phase=='cleanup': assert f=='old1' and cur[i]==1 and role(i) in ('X','S') and i not in hetero and i not in fused
                else: assert cur[i]==f,'scalar not at common exact label'
            else: assert x[0]=='C' and phase=='centers'
        if e[0]=='clear': reg[tgt]={}; centers.discard(tgt)
        else:
            q=e[3]; d=reg.setdefault(tgt,{})
            for k,x in dict(reg.get(src,{})).items():
                z=d.get(k,0)+q*x
                if z: d[k]=z
                else: d.pop(k,None)
            if tgt[0]=='C': centers.add(tgt)
    assert seen==PHASES and not centers
    exp={('L',i):{i:Fr(1)} for i in range(N)}
    for t in range(V):
        if ori=='forward': exp[('L',V+t)][t]=Fr(1)
        else: exp[('L',t)][V+t]=Fr(-1)
    bad=[r for r in exp if reg[r]!=exp[r]]
    assert not bad,(ori,'columns wrong',bad[:5])
    assert all(not z for r,z in reg.items() if r[0]!='L'),'private work not erased'
    assert fusedone==set(fused)
    return dict(events=sum(counts.values()),counts=dict(counts),local_hist=dict(sorted(hist.items())),paid_hist=dict(sorted(paid.items())),edges=sorted(edges))
