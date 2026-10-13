"""Plane-section covers and target frame chains of a verified split-centre complex word (PR433 lineage).
Usage: plane_cover.py CANONICAL-WORD.json.gz [OUT.json]
Prepared by higherbeing with Claude Code assistance; Apache-2.0.

Facts checked exactly on the word:
  * ports u_t in F_2^9; every target's final frame (cap) is u_t^perp (dim 8);
  * the readers of source s (targets whose decoder row contains s) are exactly the 56 targets with u_t . u_s = 0;
  * a register holding source s that has climbed above its own line sits on a plane span(u_s, v); it can be read by
    target t only if that plane lies in cap(t), i.e. u_t . v = 0.  So a 'branch' of s serves the readers in one
    hyperplane section {t in N(s): u_t . v = 0} of its reader set.
  * exhaustive over all 255 planes through u_s, for all 120 sources: the largest section has 32 readers, and TWO
    planes always cover all 56: every port has odd weight, so the all-ones functional is 1 on every port and the
    planes spanned with v and v+1 are complementary on the readers.  Plane-level delivery is therefore NOT what limits
    the carrier count.  What limits it is that each target reads along a nested chain of frames (dims 0 -> 5 -> 6 -> 8
    in the #433 word), so a source register can be read by t only when it sits exactly at one of t's chain frames;
    the script therefore also reports the chain frames per target and how many targets share each pre-cap frame.
"""
import gzip,json,sys,itertools
from fractions import Fraction as Fr
from collections import Counter,defaultdict
w=json.loads(gzip.decompress(open(sys.argv[1],'rb').read()));V=120;ports=w['ports'];frames=w['frames']
dot=lambda a,b:bin(a&b).count('1')&1
def span(vs):
    b=[]
    for v in vs:
        for x in b:v=min(v,v^x)
        if v:b.append(v)
    return b
def inspan(v,b):
    for x in b:v=min(v,v^x)
    return v==0
# decoder rows: replay the word over Q to get each target's source support
val={i:{i:Fr(1)}for i in range(V)};val.update({i:{}for i in range(V,2*V+w['report']['R']if'report'in w else 800)})
for ph in('precondition','A','cut','B'):
    for g in w[ph]:
        if g[0]=='add':
            dst,src,q,den=g[1],g[2],Fr(g[3]),g[4];c=Fr(q,den)if den else q
            for s,v in val[src].items():
                val[dst][s]=val[dst].get(s,0)+c*v
                if val[dst][s]==0:del val[dst][s]
        elif g[0]=='scale':
            dst,q,den=g[1],Fr(g[2]),g[3];c=Fr(q,den)if den else q
            for s in list(val[dst]):val[dst][s]*=c
rows={t:{s:c for s,c in val[V+t].items()if s<V}for t in range(V)}
caps={t:span(frames[w['final'][V+t]])for t in range(V)}
assert all(len(caps[t])==8 and all(dot(ports[t],x)==0 for x in caps[t])for t in range(V)),'caps are u_t^perp'
# a source s can be delivered to t only if u_s lies in cap(t) = u_t^perp, i.e. u_s . u_t = 0; these are the readers
readers={s:{t for t in range(V)if t!=s and inspan(ports[s],caps[t])}for s in range(V)}
assert all(readers[s]=={t for t in range(V)if t!=s and dot(ports[s],ports[t])==0}for s in range(V))
assert all(len(readers[s])==56 for s in range(V))
# the decoder rows: the 56 readers carry s with coefficient -+1/2 (neighbour term); other sources enter only through the centres
res=[]
for s in range(V):
    us=ports[s];N=readers[s];planes={}
    for v in range(1,512):
        if v==us:continue
        key=min(v,v^us)
        if key in planes:continue
        planes[key]=frozenset(t for t in N if dot(ports[t],v)==0)
    secs=list(planes.values());mx=max(len(x)for x in secs)
    two=any(a|b==N for a,b in itertools.combinations([x for x in secs if len(x)>=56-mx],2))
    big=[x for x in secs if len(x)>=19]
    three=any(a|b|c==N for a,b,c in itertools.combinations(big,3))
    res.append((mx,two,three))
summary=dict(sources=V,readers_per_source=56,planes_per_source=255,max_section=Counter(r[0]for r in res),two_cover_exists_for_all_sources=all(r[1]for r in res),all_ports_odd_weight=all(bin(p).count('1')&1 for p in ports))
# target chains: frames at which each target reads before its cap, and how many targets share each such frame
chains=defaultdict(list)
for ph in('B',):
    for g in w[ph]:
        if g[0]=='add'and V<=g[1]<2*V and g[5]is not None:
            F=tuple(span(frames[g[5]]))
            if len(F)<8 and F not in chains[g[1]-V]:chains[g[1]-V].append(F)
share=Counter()
for t,fs in chains.items():
    for F in fs:share[F]+=1
summary['chain_dims_per_target']={str(k):v for k,v in Counter(tuple(len(F)for F in fs)for fs in chains.values()).items()}
summary['targets_sharing_a_pre_cap_frame']={d:dict(Counter(n for F,n in share.items()if len(F)==d))for d in sorted({len(F)for F in share})}
# how many carriers does the word use (helpers whose first gate copies a source register)
first={}
for ph in('precondition','A'):
    for g in w[ph]:
        if g[0]=='add'and g[1]>=2*V and g[1]not in first:first[g[1]]=g[2]
summary['carriers_used']=sum(1 for h,src in first.items()if src<V);summary['helpers']=len(first)
print(json.dumps(summary,indent=1,default=str))
if len(sys.argv)>2:json.dump(summary,open(sys.argv[2],'w'),indent=1,default=str)
