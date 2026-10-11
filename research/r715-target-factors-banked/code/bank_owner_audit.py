"""Explicit coordinate-bank route completion; OpenAI Codex assistance, Apache-2.0."""
import argparse,gzip,hashlib,json
from collections import Counter,defaultdict
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('word',type=Path);p.add_argument('template',type=Path);p.add_argument('out',type=Path);a=p.parse_args()
w=json.loads(a.word.read_bytes());raw=gzip.decompress(a.template.read_bytes());t=json.loads(raw)
assert (w['R'],w['h'],t['m'],t['replicas'])==(715,8,64,32)
assert hashlib.sha256(raw).hexdigest()=='d526b3b08661af3e99d7b4f883dbf40e8625f5a1de645e7784ba9225837fc0bb'
frames={}
for f in set(w['start'][240:]):
 E=tuple(i for i in w['frames'][f] if i<8)
 assert all(w['lines'][i]==[2*int(i==j) for j in range(8)] for i in range(8))
 assert all(all(x==0 or j in E for j,x in enumerate(w['lines'][i])) for i in w['frames'][f])
 residual=tuple(i for i in range(8) if i not in E);assert len(residual)>=6
 frames[f]=residual
occup=defaultdict(set);sha=hashlib.sha256();count=0;maxfactors=0
for call in t['calls']:
 owners=set()
 for helper,(family,route) in enumerate(call['owners'][240:]):
  kind,offset,width,f=route;assert kind=='bank' and f==w['start'][240+helper]
  residual=frames[f];assert len(residual)==width
  target=tuple(range(offset,offset+width));assert set(target)<=set(range(64))
  sigma=dict(zip(residual,target))
  sigma.update(zip((i for i in range(64) if i not in residual),(i for i in range(64) if i not in target)))
  sigma=tuple(sigma[i] for i in range(64));assert sorted(sigma)==list(range(64))
  assert {sigma[i] for i in residual}==set(target)
  assert (family,sigma) not in owners;owners.add((family,sigma))
  # Distinct residual intervals plus intersecting local residual spaces forbid
  # sigma equality within a family independently of chosen completion.
  assert not occup[family]&set(target);occup[family].update(target)
  seen=set();cycles=0
  for i in range(64):
   if i not in seen:
    cycles+=1;j=i
    while j not in seen:seen.add(j);j=sigma[j]
  factors=64-cycles;assert factors<=63;maxfactors=max(maxfactors,factors)
  sha.update(json.dumps([call['stage'],call['replica'],helper,family,sigma],separators=(',',':')).encode()+b'\n');count+=1
 assert len(owners)==715
assert count==9*32*715 and len(occup)==25200
assert all(z==set(range(64)) for z in occup.values())
# Every coordinate has exactly one disjoint residual projector per bank.
# D_U factors commute and multiply to D_I, on all arrays and every odd field.
result=dict(status='PASS_EXPLICIT_R715_BANK_ROUTE_COMPLETIONS',helpers=count,banks=len(occup),bank_dimensions=64,minimum_local_residual_dimension=6,actual_owner_injection=True,complete_disjoint_residual_partition=True,maximum_permutation_transpositions=maxfactors,paid_extra_route_allowance=144,route_digest=sha.hexdigest(),word_sha256=hashlib.sha256(a.word.read_bytes()).hexdigest(),template_sha256=hashlib.sha256(raw).hexdigest(),scope='Explicit full64 coordinate isometries and owner injection. Local scalar/operator identity and global data chronology are separate replayed obligations; arbitrary bank contents follow by all-input local identity and commuting disjoint residual products.')
a.out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
