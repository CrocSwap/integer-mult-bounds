"""Pinned 111-port source parser and exact GF(2) primitive replay."""
from collections import Counter,defaultdict
from hashlib import sha256
from pathlib import Path
import gzip,json

SOURCE_SHA256='74e93daf2b7acf794ffb51f92f03f51556f68126d41ee13a8969bddb4cbe6326'

def load(path):
 data=Path(path).read_bytes()
 if sha256(data).hexdigest()!=SOURCE_SHA256: raise ValueError('Compressed source SHA-256 mismatch')
 word=json.loads(gzip.decompress(data))
 assert word['schema']=='BIT-functional-GL-kernel-native/1'
 assert (word['public'],len(word['frames']),len(word['program']),word['owned_fields'])==(630,636,39600,3433)
 return word

def insert(B,v):
 while v:
  p=v.bit_length()-1
  if p in B:v^=B[p]
  else:B[p]=v;return True
 return False

def residue(B,v):
 while v:
  p=v.bit_length()-1
  w=B.get(p)
  if w is None:return v
  v^=w
 return 0

def contains(B,v):return not residue(B,v)

def primitive(word):
 """Replay every instruction for all arbitrary public fields at once."""
 n=word['public']; frames=dict(enumerate(word['start']));values={i:1<<i for i in range(n)}
 # tokens express each normalized register as a linear form in public inputs
 # and preceding packet fields; used by the exploratory coding search.
 tokens={i:1<<i for i in range(n)}
 stock=defaultdict(dict)
 for i,c in enumerate(word['start']):insert(stock[c],1<<i)
 edges=[];incoming=defaultdict(list);outgoing=defaultdict(list);dirty=0
 for clock,(op,r,*args) in enumerate(word['program']):
  if op=='INIT':
   assert r>=n and r not in frames
   frames[r]=args[0];values[r]=0;tokens[r]=0
  elif op=='ADD':
   q,c=args;assert r!=q and frames[r]==frames[q]==c
   values[r]^=values[q];tokens[r]^=tokens[q]
  elif op=='MOVE':
   a,b=args;assert frames[r]==a and contains(stock[a],values[r])
   j=len(edges);incoming[b].append(j);outgoing[a].append(j)
   edges.append({'clock':clock,'reg':r,'a':a,'b':b,'F':values[r],'dependencies':tokens[r]})
   insert(stock[b],values[r]);frames[r]=b;tokens[r]=1<<(n+j)
  elif op=='SWAP':
   q,=args;frames[r],frames[q]=frames[q],frames[r];values[r],values[q]=values[q],values[r];tokens[r],tokens[q]=tokens[q],tokens[r]
  elif op=='CLEAR':
   assert r>=n and frames.pop(r)==args[0];dirty+=bool(values.pop(r));del tokens[r]
  else:raise ValueError(op)
 assert frames==dict(enumerate(word['final'])) and len(edges)==2803 and dirty==3433
 assert len(values)==n
 final=defaultdict(list)
 for r in range(n):
  want=(1<<r)^((1<<(r-111)) if 111<=r<222 else 0)
  assert values[r]==want and contains(stock[frames[r]],want),(r,frames[r])
  final[frames[r]].append((r,want))
 return edges,incoming,outgoing,final

def paths(word,edges,incoming,outgoing):
 dims={int(i):f['dim'] for i,f in word['frames'].items()}
 result=[]
 for h in sorted(set(incoming)&set(outgoing)):
  for i in incoming[h]:
   a=edges[i]['a']
   if abs(dims[a]-dims[h])!=1:continue
   for j in outgoing[h]:
    b=edges[j]['b']
    if i<j and abs(dims[h]-dims[b])==1 and abs(dims[a]-dims[b])==2:result.append((h,i,j))
 assert len(result)==1557
 return result

def record(edges,path):
 h,i,j=path;ie=edges[i];oe=edges[j]
 return {'hinge':h,'ingress_clock':ie['clock'],'ingress_register':ie['reg'],
  'egress_clock':oe['clock'],'egress_register':oe['reg'],
  'old_edges':[[ie['a'],h],[h,oe['b']]],'replacement':[ie['a'],oe['b']]}
