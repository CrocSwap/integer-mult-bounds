"""Certify the balanced 4+4 hinge and the equal-grade late rank-one rebind."""
from collections import defaultdict,Counter
from fractions import Fraction
import gzip,json,sys
from hashlib import sha256
from pathlib import Path

class Span:
 def __init__(self,rows=()):
  self.b={}
  for r in rows:
   while r:
    p=r.bit_length()-1
    if p not in self.b:self.b[p]=r;break
    r^=self.b[p]
 def residue(self,r):
  for p in sorted(self.b,reverse=True):
   if r>>p&1:r^=self.b[p]
  return r

def run(path):
 raw=Path(path).read_bytes();assert sha256(raw).hexdigest()=='74e93daf2b7acf794ffb51f92f03f51556f68126d41ee13a8969bddb4cbe6326';g=json.loads(gzip.decompress(raw));P=g['program'];D={int(k):r['dim'] for k,r in g['frames'].items()};G4=[(k,d,s,t) for k,(op,d,*a) in enumerate(P) if op=='MOVE' for s,t in [a] if D[t]-D[s]==4];pairs=[(a,b) for a in G4 for b in G4 if a[0]<b[0] and a[3]==b[2]];assert pairs==[((7112,2241,0,509),(7210,2252,509,1))];n=630;L=(1<<630)-1;ch=dict(enumerate(g['start']));v={i:1<<i for i in ch};hist=defaultdict(list)
 for i,c in ch.items():hist[c].append(v[i])
 patch={7110:['INIT',2241,509],7111:None,7112:None,7208:['INIT',2252,0],7209:['ADD',2252,626,0],7210:['MOVE',2252,0,1],21250:None}
 for k,row in enumerate(P):
  if k==7110:hinge=list(hist[509]);assert len(hinge)==12
  if k==7122:v[2242]^=1<<630
  if k==21256:pred={c:tuple(s) for c,s in hist.items()};assert all(not any(x>>630 for x in pred[c]) for c in D if D[c]<=1)
  row=patch.get(k,row)
  if row is None:continue
  op,d,*a=row
  if op=='INIT':ch[d],v[d]=a[0],0
  elif op=='ADD':s,c=a;assert ch[s]==ch[d]==c;v[d]^=v[s]
  elif op=='MOVE':
   assert ch[d]==a[0];ch[d]=a[1]
   if k==21260:v[d]=1<<631 # an arbitrary absolute new fourth receipt at chart544
   hist[a[1]].append(v[d])
  elif op=='SWAP':s,=a;ch[d],ch[s]=ch[s],ch[d];v[d],v[s]=v[s],v[d]
  elif op=='CLEAR':assert ch.pop(d)==a[0];del v[d]
 M=[(1<<i)^((1<<(i-111)) if 111<=i<222 else 0) for i in range(n)];W=Span(r for i,r in enumerate(M) if g['final'][i]==1);top=Span(r&L for r in hist[1]);assert len(W.b)==505 and len(top.b)==504
 tagged=Span(hist[1]);assert len(tagged.b)==505 and tagged.residue(1<<630)==0
 assert not any(x>>(n+1) for x in hist[1]);others=[x for x in hist[544] if x>>(n+1)==0];assert len(others)==3 and hist[544][-1]==1<<631
 combos=[0];
 for x in others:combos+=[v^x for v in combos]
 gs=[0];
 for x in hinge:gs+=[v^x for v in gs]
 assert len(set(gs))==4096;valid=[g for g in gs if not W.residue(g) and top.residue(g)];assert len(valid)==512
 zero=Span(pred[0]);lines=[c for c,d in D.items() if d==1];known={c:Span(zero.residue(r) for r in pred[c]) for c in lines};wins=Counter();noreceipt=0
 for ghat in valid:
  for x in combos:
   needed=M[130]^(x&L)^(ghat if x>>n&1 else 0)
   if needed==0:noreceipt+=1
   reduced=zero.residue(needed)
   for c,b in known.items():
    if b.residue(reduced)==0:wins[c]+=1
 assert noreceipt==0 and wins=={21:512} and g['start'][19]==21 and g['final'][111+19]==544
 # The rank-one image together with the rank-seven destination image has rank eight over Q.
 u=g['frames']['21'];b=g['frames']['544'];A=[[Fraction(v) for v in row] for row in b['B']+u['B']];assert len(A)==8
 for j in range(8):
  s=next(i for i in range(j,8) if A[i][j]);A[s],A[j]=A[j],A[s]
  for i in range(j+1,8):
   r=A[i][j]/A[j][j];A[i]=[x-r*y for x,y in zip(A[i],A[j])]
 return {'unique_causal_pair':pairs[0],'hinge_fields':len(hinge),'all_linear_hinge_codes':len(gs),'terminal_sink_complete_codes':len(valid),'candidate_late_rank1_senders':len(lines),'successful_linear_rank1_pairs_before_geometry':dict(wins),'nested_late_sender_solutions':0,'old_late_sender':91,'missed_output':130,'incomparable_only_source':21,'original_late_destination':544}
if __name__=='__main__':print(json.dumps(run(sys.argv[1]),sort_keys=True,indent=2))
