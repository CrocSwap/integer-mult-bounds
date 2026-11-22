#!/usr/bin/env python3
"""All chart-1 rank-two/rank-four ingresses vs every cheaper existing sender.

Requires only the Python standard library. The optional argument is a local
copy of the pinned gzip input; both compressed and expanded hashes are checked.
Clocks are zero-based in the source graph. See README.md for exact scope.
"""
import gzip, hashlib, json, sys, tempfile
from collections import Counter
from fractions import Fraction
from pathlib import Path

HERE=Path(__file__).resolve().parent
CSHA='74e93daf2b7acf794ffb51f92f03f51556f68126d41ee13a8969bddb4cbe6326'
ESHA='b096d6df2a0c4688296b13ab0cfd50fec1c7dec732819c624ddd7a745a144b69'
def sha(x):return hashlib.sha256(x).hexdigest()
def load(path):
 raw=Path(path).read_bytes()
 if sha(raw)!=CSHA:raise ValueError('compressed source hash mismatch')
 expanded=gzip.decompress(raw)
 if sha(expanded)!=ESHA:raise ValueError('expanded source hash mismatch')
 g=json.loads(expanded)
 assert g['public']==630 and len(g['frames'])==636 and len(g['program'])==39600
 return g

def support(x):return [i for i in range(x.bit_length()) if (x>>i)&1]
def dot(a,b):return (a&b).bit_count()&1
class Basis:
 def __init__(self):self.rows={}
 def add(self,x):
  while x:
   p=x.bit_length()-1
   if p not in self.rows:self.rows[p]=x;return
   x^=self.rows[p]
 def reduce(self,x):
  result=0
  while x:
   p=x.bit_length()-1
   if p in self.rows:x^=self.rows[p]
   else:result|=1<<p;x^=1<<p
  return result
 def contains(self,x):return self.reduce(x)==0
 def separator(self,x):
  reduced=self.reduce(x)
  if not reduced:raise ValueError('no separator: requested form belongs to span')
  k=(reduced&-reduced).bit_length()-1
  v=1<<k
  for p,row in sorted(self.rows.items()):
   if dot(row,v):v|=1<<p
  assert dot(x,v)==1 and all(dot(row,v)==0 for row in self.rows.values())
  return v

def union(*bases):
 b=Basis()
 for src in bases:
  for row in src.rows.values():b.add(row)
 return b

def matrix_mul(a,b):
 return [[sum((a[i][k]*b[k][j] for k in range(8)),Fraction(0)) for j in range(8)] for i in range(8)]
def inv(A):
 a=[[Fraction(x) for x in row]+[Fraction(int(i==j)) for j in range(8)] for i,row in enumerate(A)]
 for k in range(8):
  pivot=next((i for i in range(k,8) if a[i][k]),None)
  assert pivot is not None
  a[k],a[pivot]=a[pivot],a[k]
  z=a[k][k];a[k]=[x/z for x in a[k]]
  for i in range(8):
   if i!=k and a[i][k]:
    z=a[i][k];a[i]=[x-z*y for x,y in zip(a[i],a[k])]
 return [row[8:] for row in a]
def projector(spec):
 # Source's literal frame has B rows first, A rows second; their transpose
 # is the change-of-basis matrix. D selects exactly the B columns.
 src=spec['B']+spec['A']; assert len(src)==8 and all(len(x)==8 for x in src)
 Q=[[Fraction(src[j][i]) for j in range(8)] for i in range(8)]
 invQ=inv(Q)
 assert all(x.denominator%3 for row in invQ for x in row)
 d=spec['dim'];assert len(spec['B'])==d
 QD=[[Q[i][j] if j<d else Fraction(0) for j in range(8)] for i in range(8)]
 p=matrix_mul(QD,invQ)
 assert matrix_mul(p,p)==p
 return p

def reverse_original(g):
 n=g['public'];fr=dict(enumerate(g['final']));v={i:1<<i for i in range(n)}
 for op,d,*a in reversed(g['program']):
  if op=='CLEAR':assert d not in fr;fr[d]=a[0];v[d]=0
  elif op=='INIT':assert fr.pop(d)==a[0];del v[d]
  elif op=='MOVE':assert fr[d]==a[1];fr[d]=a[0]
  elif op=='ADD':s,c=a;assert fr[d]==fr[s]==c;v[s]^=v[d]
  elif op=='SWAP':s=a[0];fr[d],fr[s]=fr[s],fr[d];v[d],v[s]=v[s],v[d]
  else:raise ValueError(op)
 assert fr==dict(enumerate(g['start']))
 return [v[i] for i in range(n)]

def main():
 path=Path(sys.argv[1]) if len(sys.argv)>1 else HERE/'strong-bit.json.gz'
 g=load(path);P=g['program'];F=g['frames'];dims={int(i):v['dim'] for i,v in F.items()}
 dcount=Counter(dims.values());assert dict(sorted(dcount.items()))=={0:1,1:111,2:153,4:70,6:180,7:120,8:1}
 ident=[[Fraction(int(i==j)) for j in range(8)] for i in range(8)]
 assert projector(F['1'])==ident
 candidates=sorted(i for i,d in dims.items() if d in (6,7))
 for c in candidates:
  p=projector(F[str(c)])
  assert matrix_mul(p,ident)==matrix_mul(ident,p)==p
 # Also verify the two original rank-four sources' rational projectors.
 for c in (506,509):projector(F[str(c)])
 n=g['public'];fr=dict(enumerate(g['start']));v={i:1<<i for i in range(n)}
 hist={i:Basis() for i in dims}
 for i in fr:hist[fr[i]].add(v[i])
 checks=[];counts=Counter();positive=[];clear_count=0;dirty_clears=0
 for clock,(op,d,*args) in enumerate(P):
  if op=='MOVE' and args[1]==1 and 8-dims[args[0]] in (2,4):
   grade=8-dims[args[0]]; f=v[d]; assert f
   eligible=[c for c in candidates if 1<=8-dims[c]<grade]
   assert len(eligible)==(120 if grade==2 else 300)
   counts[f'rank_{grade}_arrivals']+=1
   counts[f'rank_{grade}_sender_checks']+=len(eligible)
   top=hist[1]; assert not top.contains(f)
   pooled=union(top,*(hist[c] for c in eligible))
   assert not pooled.contains(f)
   separator=pooled.separator(f)
   assert dot(f,separator)==1
   assert all(dot(row,separator)==0 for c in [1]+eligible for row in hist[c].rows.values())
   # This checks each of the 22,200 pairs directly, not merely by the pooled proof.
   for c in eligible:
    assert not union(top,hist[c]).contains(f)
   # Positive control: the expensive original sender really holds the form
   # both historically and in the live owner at this clock.
   assert hist[args[0]].contains(f) and fr[d]==args[0] and v[d]==f
   positive.append(clock)
   # Corrupted dual vector fails its required target pairing.
   corrupt=separator^(f&-f)
   assert dot(f,corrupt)==0
   if clock==6908:
    short=sum(1<<i for i in (47,48,52,58))
    assert grade==4 and args[0]==506 and support(f)==[47,328]
    assert dot(f,short)==1 and all(dot(row,short)==0 for row in pooled.rows.values())
   if clock==8075:
    short=(1<<1)|(1<<71)
    assert grade==2 and args[0]==326
    assert dot(f,short)==1 and all(dot(row,short)==0 for row in pooled.rows.values())
   checks.append({'clock':clock,'owner':d,'source_chart':args[0],'grade':grade,
                  'required_form':support(f),'eligible_senders':len(eligible),
                  'top_history_rank':len(top.rows),'all_cheaper_histories_pooled_rank':len(pooled.rows),
                  'separator':support(separator),'individual_donor_hits':0,'local_history_hit':False})
  if op=='INIT':assert d not in fr;fr[d]=args[0];v[d]=0
  elif op=='MOVE':assert fr[d]==args[0];fr[d]=args[1]
  elif op=='ADD':s,c=args;assert fr[d]==fr[s]==c;v[d]^=v[s]
  elif op=='SWAP':
   s=args[0];fr[d],fr[s]=fr[s],fr[d];v[d],v[s]=v[s],v[d]
   hist[fr[s]].add(v[s])
  elif op=='CLEAR':
   assert d>=n and fr.pop(d)==args[0];clear_count+=1;dirty_clears+=int(bool(v.pop(d)))
  else:raise ValueError(op)
  if d in fr:hist[fr[d]].add(v[d])
 assert fr==dict(enumerate(g['final']))
 assert [v[i] for i in range(n)]==[(1<<i)^((1<<(i-111)) if 111<=i<222 else 0) for i in range(n)]
 dual=reverse_original(g)
 assert all(((v[o]>>i)&1)==((dual[i]>>o)&1) for o in range(n) for i in range(n))
 assert dict(counts)=={'rank_4_arrivals':2,'rank_4_sender_checks':600,'rank_2_arrivals':180,'rank_2_sender_checks':21600}
 assert len(checks)==len(positive)==182 and checks[0]['clock']==6908
 assert clear_count==dirty_clears==3433
 with tempfile.TemporaryDirectory(prefix='p104-bad-') as tmp:
  b=Path(tmp)/'bad.gz';raw=path.read_bytes();b.write_bytes(raw[:-1]+bytes([raw[-1]^1]))
  try:load(b)
  except ValueError as e:assert str(e)=='compressed source hash mismatch'
  else:raise AssertionError('corrupted source accepted')
 output={'source_compressed_sha256':CSHA,'source_expanded_sha256':ESHA,
         'source':'#8036 commit 99878b566bfcce80ef7ae2650a1231a203361445 graph blob',
         'counts':dict(sorted(counts.items())), 'individual_cheaper_donor_hits':0,
         'cheaper_histories_pooled_hits':0,'chart1_free_history_hits':0,
         'rational_candidate_projectors_verified':len(candidates),'output_rows':630,
         'original_private_clears':clear_count,'symbolically_dirty_private_clears':dirty_clears,
         'positive_original_sender_controls':len(positive),'corrupted_input_rejected':True,
         'explicit_short_separators':{'6908':[47,48,52,58],'8075':[1,71]},
         'checks':checks}
 print(json.dumps(output,sort_keys=True,indent=2))
if __name__=='__main__':main()
