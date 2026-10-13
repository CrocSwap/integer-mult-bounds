"""Where the excess carriers of a split-centre complex word sit, and whether identical packet copies can be merged.
Usage: delivery_layer.py CANONICAL-WORD.json.gz [OUT.json]
Prepared by higherbeing with Claude Code assistance; Apache-2.0.

Symbolic replay over Q of phases precondition+A: each helper's content as a signed rational combination of sources.
Reports helper roles (support sizes), duplicate supports (identical copies vs sign variants), what each class feeds,
and the legality of merging each identical pair at the two readers' shared 7-dim frame given the readers' other reads.
"""
import gzip,json,sys
from fractions import Fraction as Fr
from collections import Counter,defaultdict
w=json.loads(gzip.decompress(open(sys.argv[1],'rb').read()));V=120;ports=w['ports'];frames=w['frames'];centres=set(w['centers'])
NR=2*V+w['report']['R']if'report'in w else 800
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
le=lambda A,B:all(inspan(a,B)for a in A)
def meet(A,B):
    out=[]
    for mask in range(1,1<<len(A)):
        v=0
        for i,a in enumerate(A):
            if mask>>i&1:v^=a
        if inspan(v,B):out.append(v)
    return span(out)
val={i:{i:Fr(1)}for i in range(V)};val.update({i:{}for i in range(V,NR)})
uses=defaultdict(list);treads=defaultdict(list);first={}
def apply(g,ph):
    if g[0]=='add':
        dst,src,q,den,fr=g[1],g[2],Fr(g[3]),g[4],g[5];c=Fr(q,den)if den else q
        kind='target'if V<=dst<2*V else('source'if dst<V else('centre'if dst in centres else'helper'))
        uses[src].append((ph,kind));first.setdefault(dst,src)
        if V<=dst<2*V and fr is not None:treads[dst-V].append((src,span(frames[fr])))
        for s,v in val[src].items():
            val[dst][s]=val[dst].get(s,0)+c*v
            if val[dst][s]==0:del val[dst][s]
    elif g[0]=='scale':
        dst,q,den=g[1],Fr(g[2]),g[3];c=Fr(q,den)if den else q
        for s in list(val[dst]):val[dst][s]*=c
for ph in('precondition','A'):
    for g in w[ph]:apply(g,ph)
snap={h:dict(val[h])for h in range(2*V,NR)if val[h]}
for ph in('cut','B'):
    for g in w[ph]:apply(g,ph)
out={}
out['helpers_with_content_after_A']=len(snap)
out['support_sizes']=dict(sorted(Counter(len(v)for v in snap.values()).items()))
out['coefficients']=dict(sorted(Counter(str(c)for v in snap.values()for c in v.values()).items()))
out['carriers_first_gate_from_source']=sum(1 for h in snap if first.get(h,-1)<V)
groups=defaultdict(list)
for h,v in snap.items():groups[tuple(sorted(v))].append(h)
kinds=Counter();ident=[]
for S,hs in groups.items():
    if len(hs)<2:continue
    vecs=[tuple(snap[h][s]for s in S)for h in hs]
    for vv in vecs[1:]:
        if vv==vecs[0]:kinds['identical copy']+=1
        elif all(a==-b for a,b in zip(vv,vecs[0])):kinds['global sign flip']+=1
        elif all(abs(a)==abs(b)for a,b in zip(vv,vecs[0])):kinds['partial sign change']+=1
        else:kinds['different magnitudes']+=1
    if all(v==vecs[0]for v in vecs):ident.append((S,hs))
out['duplicate_supports']=dict(kinds);out['identical_groups']=len(ident)
single=[h for h,v in snap.items()if len(v)==1]
out['single_source_copies']=dict(count=len(single),consumers=dict(Counter(k for h in single for ph,k in uses[h])))
sums=[h for h in snap if h not in single and all(g[2]>=2*V for g in w['A']if g[1]==h and g[0]=='add')]
out['helpers_built_only_from_helpers']=dict(count=len(sums),support_sizes=dict(sorted(Counter(len(snap[h])for h in sums).items())),consumers=dict(Counter(k for h in sums for ph,k in uses[h])))
caps={t:span(frames[w['final'][V+t]])for t in range(V)}
pairs=[]
for S,hs in ident:
    if len(hs)!=2:continue
    r=[[t for t in range(V)if any(src==h for src,_ in treads[t])]for h in hs]
    if len(r[0])==1 and len(r[1])==1 and r[0]!=r[1]:pairs.append((hs,r[0][0],r[1][0],S))
ok=0;reasons=Counter()
for hs,t1,t2,S in pairs:
    F=meet(caps[t1],caps[t2]);psp=span([ports[s]for s in S])
    if len(F)!=7:reasons['meet dim '+str(len(F))]+=1;continue
    if not le(psp,F):reasons['packet span not inside the meet']+=1;continue
    good=True
    for t,h in((t1,hs[0]),(t2,hs[1])):
        others=[fb for src,fb in treads[t]if src!=h and len(fb)<8]
        if not all(le(fb,F)for fb in others):good=False;reasons['another pre-cap read of a reader is outside the meet']+=1;break
    ok+=good
out['identical_pairs_each_read_by_one_distinct_target']=len(pairs)
out['mergeable_at_shared_7frame_without_other_changes']=ok;out['merge_blockers']=dict(reasons)
out['target_pre_cap_read_dims']=dict(sorted(Counter(len(fb)for t in range(V)for src,fb in treads[t]if len(fb)<8).items()))
print(json.dumps(out,indent=1))
if len(sys.argv)>2:json.dump(out,open(sys.argv[2],'w'),indent=1)
