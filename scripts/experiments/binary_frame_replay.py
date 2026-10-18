"""Independent replay of serialized XOR word and original-envelope frames.

Production form of research/joint-dual-replay-fast/: per-output triple scans
use containment masks over the same combinations(range(h), 3) enumeration.
Every assertion, check_word control, full-basis orientation and receipt field
is retained. See research/joint-dual-replay-production/ for equivalence evidence.
"""
import json,sys,gzip
from pathlib import Path
from itertools import combinations
from collections import Counter
from math import comb

if sys.flags.optimize:
 raise ValueError('Assertions must remain enabled')


def check_word(d):
 """Bind physical indices and every scatter incidence to the output plan.

 PR #64's separate audit (rfu08) identified the cancelling-scatter gap:
 https://github.com/CrocSwap/integer-mult-bounds/pull/64
 Scatter gates commute: each changes an output using an unchanged scratch
 source. Compare multisets so reordering remains valid, but extra gates do not.
 """
 h,v,R=d['h'],d['v'],d['R']
 assert type(h) is int and h>=3
 assert type(v) is int and v==comb(h,3)
 assert type(R) is int and R>=v
 frames=d['frames'];universe=(1<<h)-1
 for c,u in frames:
  assert type(c) is int and type(u) is int and 0<c<=u<=universe and not c&~u
  assert (c==u and c.bit_count()==3) or (c!=u and c.bit_count() in (1,2))
 assert set(d['sources'])=={str(i) for i in range(v)}
 assert all(type(s) is int and 0<=s<R for s in d['sources'].values())
 assert len(set(d['sources'].values()))==v
 for a,b,g in d['ops']:
  assert type(a) is int and type(b) is int and 0<=a<R and 0<=b<R and a!=b
  assert type(g) is int and 0<=g<len(frames)
 triples=list(combinations(range(h),3));lookup={t:i for i,t in enumerate(triples)}
 center_destinations=[[] for _ in range(h)]
 for i,triple in enumerate(triples):
  for common in triple:center_destinations[common].append(i)
 expected=Counter();outputs=set();centers=set()
 for s,g,common,triple in d['outputs']:
  assert type(s) is int and 0<=s<R and s not in outputs
  assert type(g) is int and 0<=g<len(frames)
  assert type(common) is int and 0<=common<h
  assert all(type(point) is int for point in triple)
  outputs.add(s)
  if len(triple)==1:
   assert triple==[common] and common not in centers
   centers.add(common)
   destinations=center_destinations[common]
  else:
   assert len(triple)==3 and triple==sorted(triple) and common in triple
   destinations=[lookup[tuple(triple)]]
  expected.update((v+i,2*v+s) for i in destinations)
 assert centers==set(range(h))
 for target,source in d['scatter']:
  assert type(target) is int and v<=target<2*v
  assert type(source) is int and 2*v<=source<2*v+R
 assert Counter(map(tuple,d['scatter']))==expected, 'Scatter differs from paid output incidences'


def _containment_tables(h):
 """Center/pair masks and destination lists over combinations(range(h), 3).

 Bit i of center[c] is set iff c is in triples[i]. Bit i of pair[c][x] is set
 iff {c, x} is contained in triples[i]. Then

   expected(common, triple) = center[common]
       & ~pair[common][x] for each x in set(triple) - {common}

 equals the historical full-triple scan
   sum(1<<i for i,t in enumerate(triples)
       if common in t and not (set(t) & (set(triple) - {common}))).
 """
 triples=list(combinations(range(h),3))
 center=[0]*h
 pair=[[0]*h for _ in range(h)]
 destinations=[[] for _ in range(h)]
 for i,t in enumerate(triples):
  bit=1<<i
  for c in t:
   center[c]|=bit
   destinations[c].append(i)
   for x in t:
    pair[c][x]|=bit
 return triples,center,pair,destinations,{t:i for i,t in enumerate(triples)}


def _expected_mask(center,pair,common,triple):
 mask=center[common]
 for x in set(triple)-{common}:
  mask&=~pair[common][x]
 return mask


def replay(path):
 d=json.loads(gzip.decompress(Path(path).read_bytes()) if str(path).endswith('.gz') else Path(path).read_bytes())
 check_word(d)
 h,v,R=d['h'],d['v'],d['R'];F=d['frames']
 triples,center,pair,destinations,lookup=_containment_tables(h)
 assert len(triples)==v
 ranks=[1 if c==u else u.bit_count()-c.bit_count()for c,u in F]
 for c,u in F:assert c and not c&~u and(c.bit_count()in(1,2)or c==u and c.bit_count()==3)
 # First-match semantics of the historical F.index([mask, mask]) scan.
 frame_index={}
 for index,frame in enumerate(F):
  frame_index.setdefault(tuple(frame),index)
 physical=[None]*R;symbols=[0]*R;hist=Counter();sources={int(i):s for i,s in d['sources'].items()};assert len(sources)==v and len(set(sources.values()))==v
 def incidence(s,g):
  old=physical[s]
  if old is not None:
   c,u=F[old];cc,uu=F[g];assert not cc&~c and not u&~uu
   hist[ranks[g]-ranks[old]]+=1
  else:hist[ranks[g]]+=1
  physical[s]=g
 for i,s in sources.items():
  mask=sum(1<<j for j in triples[i]);key=(mask,mask)
  if key not in frame_index:
   raise ValueError(str([mask,mask])+' is not in list')
  g=frame_index[key];incidence(s,g);symbols[s]=1<<i
 for a,b,g in d['ops']:
  assert a!=b;incidence(a,g);incidence(b,g);symbols[a]^=symbols[b]
 scatter=[0]*v;out=set()
 for s,g,common,triple in d['outputs']:
  assert s not in out;out.add(s);incidence(s,g);c,u=F[g]
  expected=_expected_mask(center,pair,common,triple)
  assert symbols[s]==expected
  if len(triple)==1:
   assert c==1<<common and u==(1<<h)-1;r=ranks[g];hist[r]+=1;hist[h-r]+=1
   tt=destinations[common]
  else:
   assert c==1<<common and u==((1<<h)-1)^sum(1<<j for j in triple if j!=common)
   hist[h-1-ranks[g]]+=1;hist[1]+=1
   key=tuple(triple)
   if key not in lookup:
    raise ValueError(str(list(key))+' is not in list')
   tt=[lookup[key]]
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
