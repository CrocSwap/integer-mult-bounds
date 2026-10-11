"""Novel-stream experiment: exact helper inlining with paid frame repair.

This is a search, not a verified exponent. Starts from frozen Sussman/Chafik
E8, uses applecrusher's echelon frame repair, and screens short nonconstant
linear substitutions independently of the two published equal-value aliases.
"""
import argparse, copy, gzip, json, math, pathlib, sys, time
from collections import Counter, defaultdict
from fractions import Fraction as Q
from functools import lru_cache

HERE=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(HERE/'vendor/source376'))
from two_alias import canon, inside, join

@lru_cache(None)
def meet(a,b):
    vals=[0]
    for x in a:vals += [y^x for y in vals]
    return canon(x for x in vals if inside((x,),b))

def flatten(c):
    ops=[]
    for phase in ('A','B'):
        for g in c[phase]:
            assert g[0] in ('in','out') and (g[0]!='out' or not g[4])
            for r,a,b in g[3]:
                d,s=(g[2],r) if g[0]=='in' else (r,g[2])
                ops.append((g[1],d,s,Q(a,b)))
        if phase=='A':split=len(ops)
    return ops,split

def plus(dst,src,q):
    dst=dict(dst)
    for k,v in src.items():
        z=dst.get(k,Q(0))+q*v
        if z:dst[k]=z
        else:dst.pop(k,None)
    return dst

def proposals(c,max_terms):
    ops,split=flatten(c);v=c['v'];n=2*v+c['R']
    writes=defaultdict(list);reads=defaultdict(list)
    for i,(f,d,s,q) in enumerate(ops):writes[d].append(i);reads[s].append(i)
    protected={r for _,r,_ in c['ret']}
    plans={}
    for r in range(2*v,n):
        if r in protected or not writes[r] or not reads[r]:continue
        if max(writes[r])>=min(reads[r]):continue
        terms=Counter()
        for i in writes[r]:
            _,d,s,q=ops[i];terms[s]+=q
        terms={s:q for s,q in terms.items()if q}
        if not 1<=len(terms)<=max_terms or r in terms:continue
        if any(s<2*v for s in terms):continue
        plans[r]=terms
    vals=[{r:Q(1)}if r<v else{}for r in range(n)]
    count={r:0 for r in plans}
    for f,d,s,q in ops:
        if s in plans:
            expected={}
            for donor,coef in plans[s].items():expected=plus(expected,vals[donor],coef)
            if not vals[s] or expected!=vals[s]:plans.pop(s,None)
            else:count[s]+=1
        vals[d]=plus(vals[d],vals[s],q)
    return [(r,terms,count[r])for r,terms in plans.items()]

def repair(c,drop,terms):
    ops,split=flatten(c);v=c['v'];n=2*v+c['R'];frames=[tuple(f)for f in c['frames']]
    gs=[]
    for i,(f,d,s,q) in enumerate(ops):
        if d==drop:continue
        if s==drop:
            for donor,coef in sorted(terms.items()):
                assert d!=donor
                gs.append((i,f,d,donor,q*coef))
        else:gs.append((i,f,d,s,q))
    fixed={}
    for _,r,f in c['ret']:
        sites=[j for j,(i,ff,d,s,q)in enumerate(gs)if i<split and r in(d,s)]
        assert sites;fixed[sites[-1]]=frames[f]
    cur=[frames[f]for f in c['final']];upper=[]
    for j in range(len(gs)-1,-1,-1):
        _,f,d,s,q=gs[j];u=meet(cur[d],cur[s])
        if j in fixed:assert inside(fixed[j],u);u=fixed[j]
        upper.append(u);cur[d]=cur[s]=u
    upper.reverse();cur=[frames[f]for f in c['start']]
    for j,(i,f,d,s,q)in enumerate(gs):
        lo=join(cur[d],cur[s])
        if j in fixed:lo=join(lo,fixed[j])
        assert inside(lo,upper[j]);cur[d]=cur[s]=lo
    cur=[frames[f]for f in c['start']];new=[]
    for j,(i,f,d,s,q)in enumerate(gs):
        fr=join(join(cur[d],cur[s]),meet(frames[f],upper[j]))
        if j in fixed:fr=join(fr,fixed[j])
        assert inside(fr,upper[j]);cur[d]=cur[s]=fr;new.append((i,fr,d,s,q))
    out=copy.deepcopy(c);out['R']-=1;physical=[r for r in range(n)if r!=drop];ix={r:i for i,r in enumerate(physical)}
    out['start']=[c['start'][r]for r in physical];out['final']=[c['final'][r]for r in physical]
    out['ret']=[[k,ix[r],f]for k,r,f in c['ret']];ids={tuple(f):i for i,f in enumerate(out['frames'])}
    def fid(fr):
        if fr not in ids:ids[fr]=len(out['frames']);out['frames'].append(list(fr))
        return ids[fr]
    for phase in ('A','B'):
        out[phase]=[['in',fid(fr),ix[d],[[ix[s],q.numerator,q.denominator]]]for i,fr,d,s,q in new if(i<split)==(phase=='A')]
    cur=list(out['start']);H={k:Counter()for k in 'xysc'}
    def climb(r,f):
        old=cur[r];assert inside(tuple(out['frames'][old]),tuple(out['frames'][f]))
        if f!=old:H['x'if r<v else'y'if r<2*v else's'][len(out['frames'][f])-len(out['frames'][old])]+=1
        cur[r]=f
    for phase in ('A','B'):
        if phase=='B':
            for _,r,f in out['ret']:assert cur[r]==f;H['c'][len(out['frames'][f])]+=1
        for _,f,d,ss in out[phase]:
            climb(d,f)
            for s,_,_ in ss:climb(s,f)
    for r,f in enumerate(out['final']):climb(r,f)
    out['blocks']={k:{str(r):cnt for r,cnt in sorted(h.items())}for k,h in H.items()}
    out['N']=sum(r*cnt for h in H.values()for r,cnt in h.items());assert out['N']==c['N']-c['h']
    return out
