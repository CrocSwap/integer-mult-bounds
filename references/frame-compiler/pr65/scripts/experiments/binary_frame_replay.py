"""Independent replay of serialized XOR word and original-envelope frames."""
import json,sys,gzip
from pathlib import Path
from itertools import combinations
from collections import Counter

def replay(path):
 d=json.loads(gzip.decompress(Path(path).read_bytes()) if str(path).endswith('.gz') else Path(path).read_bytes());h,v,R=d['h'],d['v'],d['R'];F=d['frames'];triples=list(combinations(range(h),3));assert len(triples)==v
 ranks=[1 if c==u else u.bit_count()-c.bit_count()for c,u in F]
 for c,u in F:assert c and not c&~u and(c.bit_count()in(1,2)or c==u and c.bit_count()==3)
 physical=[None]*R;symbols=[0]*R;hist=Counter();sources={int(i):s for i,s in d['sources'].items()};assert len(sources)==v and len(set(sources.values()))==v
 def incidence(s,g):
  old=physical[s]
  if old is not None:
   c,u=F[old];cc,uu=F[g];assert not cc&~c and not u&~uu
   hist[ranks[g]-ranks[old]]+=1
  else:hist[ranks[g]]+=1
  physical[s]=g
 for i,s in sources.items():
  mask=sum(1<<j for j in triples[i]);g=F.index([mask,mask]);incidence(s,g);symbols[s]=1<<i
 for a,b,g in d['ops']:
  assert a!=b;incidence(a,g);incidence(b,g);symbols[a]^=symbols[b]
 scatter=[0]*v;out=set()
 for s,g,common,triple in d['outputs']:
  assert s not in out;out.add(s);incidence(s,g);c,u=F[g]
  expected=sum(1<<i for i,t in enumerate(triples)if common in t and not(set(t)&(set(triple)-{common})))
  assert symbols[s]==expected
  if len(triple)==1:
   assert c==1<<common and u==(1<<h)-1;r=ranks[g];hist[r]+=1;hist[h-r]+=1
   tt=[i for i,t in enumerate(triples)if common in t]
  else:
   assert c==1<<common and u==((1<<h)-1)^sum(1<<j for j in triple if j!=common)
   hist[h-1-ranks[g]]+=1;hist[1]+=1;tt=[triples.index(tuple(triple))]
  for i in tt:scatter[i]^=symbols[s]
 for s,g in enumerate(physical):
  assert g is not None
  if s not in out:hist[h-ranks[g]]+=1
 assert scatter==[1<<i for i in range(v)]
 assert sum(t*n for t,n in hist.items())==h*R+h*(h-1)
 initial=[1<<i for i in range(2*v+R)];M=[(2*v+a,2*v+b)for a,b,g in d['ops']];V=[(2*v+s,i)for i,s in sources.items()];J=[tuple(x)for x in d['scatter']];word=M+J+M[::-1]+V+M+J+M[::-1]+V
 for dual in (False,True):
  x=initial.copy()
  for a,b in reversed(word)if dual else word:
   if dual:a,b=b,a
   x[a]^=x[b]
  assert x[2*v:]==initial[2*v:]
  if dual:assert x[:v]==[initial[i]^initial[v+i]for i in range(v)]and x[v:2*v]==initial[v:2*v]
  else:assert x[v:2*v]==[initial[i]^initial[v+i]for i in range(v)]and x[:v]==initial[:v]
 return dict(status='independent serialized word, exact frames, full input and dirty basis both orientations PASS',h=h,roles=R,output_roles=len(out),elementary_xors=len(M),word_length=len(word),full_basis_vectors=2*v+R,rank_mass=sum(t*n for t,n in hist.items()),histogram=dict(hist))
if __name__=='__main__':print(json.dumps(replay(sys.argv[1]),indent=2))
