"""Complex side: +1/2 * disjoint-triple sum (paired producer) and -1/2 * pair stars,
with pieces split while they cover every point outside the target."""
import sys
from itertools import combinations
from local import Producer
h=int(sys.argv[1]); full=(1<<h)-1
p=Producer(h); p.check(); d=p.d; trip=p.inputs; tmask=[sum(1<<x for x in t) for t in trip]
cov={}
def cover(sup):
    if sup in cov: return cov[sup]
    m=0; s=sup
    while s:
        lo=s&-s; m|=tmask[lo.bit_length()-1]; s^=lo
    cov[sup]=m; return m
# disjoint pieces, nodes in producer DAG d
dpieces=[]
def emit_d(S,node):
    if cover(d.sup[node])|S==full:
        a,b=d.args[node]; emit_d(S,a); emit_d(S,b)
    else: dpieces.append((S,node))
for t in trip:
    S=sum(1<<x for x in t); emit_d(S,p.outputs[t])
# pair stars in a separate DAG over the same leaves
from local import DAG
s2=DAG(len(trip)); tid={t:i+1 for i,t in enumerate(trip)}
spieces=[]
def emit_s(S,node):
    if not node: return
    if cover(s2.sup[node])|S==full:
        a,b=s2.args[node]; emit_s(S,a); emit_s(S,b)
    else: spieces.append((S,node))
for a,b in combinations(range(h),2):
    oth=[u for u in range(h) if u not in (a,b)]; xs=[tid[tuple(sorted((a,b,u)))] for u in oth]
    pre=[0]
    for x in xs: pre.append(s2.add(pre[-1],x))
    suf=[0]*(len(xs)+1)
    for i in range(len(xs)-1,-1,-1): suf[i]=s2.add(xs[i],suf[i+1])
    for i,c in enumerate(oth):
        S=(1<<a)|(1<<b)|(1<<c); emit_s(S,pre[i]); emit_s(S,suf[i+1])
ad=d.active([n for _,n in dpieces]); a_d=sum(1 for x in ad if d.args[x])
as_=s2.active([n for _,n in spieces]); a_s=sum(1 for x in as_ if s2.args[x])
# exact map check: per target, disjoint pieces partition {T: T∩S=∅}, star pieces partition {|T∩S|=2}
from collections import defaultdict
gd=defaultdict(list); gs=defaultdict(list)
for S,n in dpieces: gd[S].append(d.sup[n])
for S,n in spieces: gs[S].append(s2.sup[n])
cnt=defaultdict(int)
for t in trip:
    S=sum(1<<x for x in t)
    for grp,want in ((gd[S],0),(gs[S],2)):
        u=0
        for x in grp:
            assert u&x==0; u|=x; assert cover(x)|S!=full
        exp=sum(1<<i for i,m in enumerate(tmask) if bin(m&S).count('1')==want)
        assert u==exp
    cnt[len(gd[S])]+=1
print(dict(h=h,disjoint_additions=a_d,pair_star_additions=a_s,additions=a_d+a_s,injections=len(dpieces)+len(spieces),
  disjoint_pieces=len(dpieces),star_pieces=len(spieces),roles=a_d+a_s+len(dpieces)+len(spieces),
  disjoint_pieces_per_target=dict(cnt),map_exact=True))
