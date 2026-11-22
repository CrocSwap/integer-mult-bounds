"""Independently replay target-cut certificates with low-pivot elimination."""
from collections import defaultdict
from hashlib import sha256
from pathlib import Path
import gzip,json

HERE=Path(__file__).resolve().parent
SOURCE_SHA='74e93daf2b7acf794ffb51f92f03f51556f68126d41ee13a8969bddb4cbe6326'

def add(B,value):
 while value:
  pivot=(value&-value).bit_length()-1
  if pivot in B:value^=B[pivot]
  else:B[pivot]=value;return

def member(B,value):
 while value:
  pivot=(value&-value).bit_length()-1
  if pivot not in B:return False
  value^=B[pivot]
 return True

def bitcount(x):return x.bit_count()&1

def main():
 source=(HERE/'BINARY-CANDIDATE.json.gz').read_bytes();assert sha256(source).hexdigest()==SOURCE_SHA
 word=json.loads(gzip.decompress(source));n=word['public'];assert n==630
 values={i:1<<i for i in range(n)};frame=dict(enumerate(word['start']));stock=defaultdict(dict)
 for i,c in enumerate(word['start']):add(stock[c],1<<i)
 edges=[];inc=defaultdict(list);out=defaultdict(list)
 for clock,(op,r,*args) in enumerate(word['program']):
  if op=='INIT':assert r not in frame;frame[r]=args[0];values[r]=0
  elif op=='ADD':q,c=args;assert frame[r]==frame[q]==c;values[r]^=values[q]
  elif op=='MOVE':
   a,b=args;assert frame[r]==a and member(stock[a],values[r])
   j=len(edges);inc[b].append(j);out[a].append(j);edges.append((clock,r,a,b,values[r],stock[a].copy()))
   add(stock[b],values[r]);frame[r]=b
  elif op=='SWAP':q,=args;frame[r],frame[q]=frame[q],frame[r];values[r],values[q]=values[q],values[r]
  elif op=='CLEAR':assert frame.pop(r)==args[0];values.pop(r)
  else:raise ValueError(op)
 assert frame==dict(enumerate(word['final'])) and len(edges)==2803
 final=defaultdict(list)
 for i in range(n):
  target=(1<<i)^((1<<(i-111)) if 111<=i<222 else 0)
  assert values[i]==target;final[frame[i]].append((i,target))
 dims={int(i):r['dim'] for i,r in word['frames'].items()}
 expected=set()
 for h,arrivals in inc.items():
  if not final[h]:continue
  for first in arrivals:
   a=edges[first][2]
   if abs(dims[a]-dims[h])!=1:continue
   for last in out[h]:
    b=edges[last][3]
    if first<last and abs(dims[h]-dims[b])==1 and abs(dims[a]-dims[b])==2:expected.add((h,edges[first][0],edges[last][0]))
 raw=gzip.decompress((HERE/'TARGET-CUT-RESULTS.json.gz').read_bytes());receipt=json.loads(raw)
 assert len(expected)==854 and len(receipt['results'])==854
 byclock={e[0]:j for j,e in enumerate(edges)};seen=set();distinct=set();corrupt_controls=0
 for row in receipt['results']:
  h=row['hinge'];first=byclock[row['ingress_clock']];last=byclock[row['egress_clock']]
  key=(h,edges[first][0],edges[last][0]);assert key in expected and key not in seen;seen.add(key)
  assert edges[first][3]==h and edges[last][2]==h and row['replacement']==[edges[first][2],edges[last][3]]
  B={}
  for i,c in enumerate(word['start']):
   if c==h:add(B,1<<i)
  for j in inc[h]:
   if j!=first:
    for v in edges[j][5].values():add(B,v)
  assert len(row['target_certificates'])==1
  cert=row['target_certificates'][0];targets=dict(final[h]);target=targets[cert['output']]
  indices=cert['probe_inputs'];assert len(indices)==len(set(indices)) and all(0<=i<n for i in indices)
  probe=sum(1<<i for i in indices)
  assert not member(B,target) and all(bitcount(v&probe)==0 for v in B.values())
  assert bitcount(target&probe)==1 and bitcount(edges[first][4]&probe)==1
  positive=B.copy();add(positive,edges[first][4]);assert member(positive,target)
  corrupt=probe^(target&-target)
  assert bitcount(target&corrupt)==0
  corrupt_controls+=1;distinct.add((h,first))
 assert seen==expected and len(distinct)==304 and corrupt_controls==854
 print('PASS_INDEPENDENT_LOW_PIVOT_TARGET_AUDIT paths=854 cuts=304 positive_and_corrupt_controls=854')
if __name__=='__main__':main()
