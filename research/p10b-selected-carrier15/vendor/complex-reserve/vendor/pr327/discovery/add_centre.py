"""Append a centre root (sum of all inputs) to a pair module by a greedy disjoint cover of existing nodes.
usage: add_centre.py SRC.json DST.json   (made pmod46_p1 from pmod_p1, the seed of the centre-sharing anneal)
Prepared by DreamingOfClouds with Anthropic Claude assistance (Apache-2.0)."""
import json,sys
src,dst=sys.argv[1],sys.argv[2]
d=json.load(open(src)); n=d['input_count']; args=d['args']
sup=[]
for x,a in enumerate(args):
    sup.append(1<<x if a is None else sup[a[0]]|sup[a[1]])
full=(1<<n)-1
assert len(d['roots'])==n
order=sorted(range(len(args)),key=lambda x:-bin(sup[x]).count('1'))
cov=0;parts=[]
for x in order:
    if sup[x]&cov==0:
        parts.append(x);cov|=sup[x]
        if cov==full:break
assert cov==full
# balanced pairwise sum
cur=parts[:]
while len(cur)>1:
    nxt=[]
    for i in range(0,len(cur)-1,2):
        args.append([cur[i],cur[i+1]]);nxt.append(len(args)-1)
    if len(cur)%2:nxt.append(cur[-1])
    cur=nxt
d['roots']=d['roots']+[cur[0]]
d['provenance']=dict(source=src,extra_root='greedy disjoint cover centre, %d parts'%len(parts))
json.dump(d,open(dst,'w'))
print('parts',len(parts),'additions',len(args)-n,'roots',len(d['roots']))
