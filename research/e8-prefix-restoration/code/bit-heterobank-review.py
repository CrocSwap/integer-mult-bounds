"""Review only the changed heterogeneous bank witness and sink frames.
Usage: python -B bit-heterobank-review.py --banks HETEROBANKS.json --certificate PREFIX18.json --sink-audit SINK-AUDIT.json --output BANK-REVIEW.json
Global emitters must use each recorded inverse matrix, emit the pinned exact
rank-zero endpoint adapters, and charge all scalar/route/adaptor primitives.
This receipt is binary geometry admission, not a Clifford or invoice proof.
"""
from pathlib import Path
import argparse,json,hashlib,gzip
assert __debug__, 'Assertions must remain enabled'
a=argparse.ArgumentParser(description=__doc__)
a.add_argument('--banks',required=True,type=Path);a.add_argument('--certificate',required=True,type=Path);a.add_argument('--sink-audit',required=True,type=Path);a.add_argument('--output',required=True,type=Path)
x=a.parse_args();paths=[x.banks,x.certificate,x.sink_audit];pins={str(p.resolve()):hashlib.sha256(p.read_bytes()).hexdigest()for p in paths}
b=json.loads(x.banks.read_text());raw=x.certificate.read_bytes();c=json.loads(gzip.decompress(raw)if x.certificate.suffix=='.gz'else raw);s=json.loads(x.sink_audit.read_text())
assert(c['h'],c['v'],c['R'])==(9,120,783)
routers=[[int(z,2)for z in rr]for rr in b['route_recipes']]
def mv(A,z):return sum(((row&z).bit_count()%2)<<i for i,row in enumerate(A))
def tr(A):return [sum(((row>>i)&1)<<j for j,row in enumerate(A))for i in range(73)]
assert len(set(tuple(A)for A in routers))==len(routers)
for A in routers:
 assert len(A)==73 and all(0<=row<1<<73 for row in A)
 for i in range(73):assert mv(tr(A),mv(A,1<<i))==1<<i
assign=b['assignments'];assert len(assign)==32*783
assert {(a['replica'],a['helper'])for a in assign}=={(rep,h)for rep in range(32)for h in range(240,1023)}
assert len({(a['bank'],a['orthogonal_route_id'])for a in assign})==len(assign),'duplicated complete owner route'
sink={z['sink_helper']:z for z in s['accepted']};assert set(sink)=={355,403};used={};normal_images=[]
for z in assign:
 A=routers[z['orthogonal_route_id']];h=z['helper'];rank=z['rank'];off=z['offset'];bank=z['bank'];mask=((1<<rank)-1)<<off
 assert rank==(8 if h in sink else 9) and off>=0 and off+rank<=73 and 0<=bank<3131
 assert not(used.get(bank,0)&mask);used[bank]=used.get(bank,0)|mask
 E=c['frames'][sink[h]['frame']]if h in sink else[1<<i for i in range(9)]
 assert len(E)==rank and all(not(mv(A,v)&~mask)for v in E)
 if h in sink:
  q=508 if h==355 else 499;normal_images.append((bank,off,mv(A,q).bit_length()-1))
assert set(used)==set(range(3131))
for bank,mask in used.items():assert mask==((1<<73)-1)if bank<8 else mask==((1<<72)-1)
for h,z in sink.items():
 owner=next(a for a in assign if a['helper']==h);A=routers[owner['orthogonal_route_id']];mask=((1<<8)-1)<<owner['offset']
 for gi,g in enumerate(c['A']+c['B']):
  regs=[g[2]]+[e[0]for e in g[3]]+(g[4]if g[0]=='out'else[])
  if h in regs:
   assert gi<=z['cut_group'],'retired helper read later'
   assert all(not(mv(A,v)&~mask)for v in c['frames'][g[1]]),'sink internal frame outside assigned rank8 block'
 for donor,_,_ in z['uncompute']:
  assert donor!=h
 assert all(not(mv(A,v)&~mask)for v in c['frames'][z['frame']])
# Each possible stage/replica/pair has injective complete owners. Data owners
# occupy families0..30719; heterogeneous bank families occupy30720..58898.
per_rep={rep:[z for z in assign if z['replica']==rep]for rep in range(32)}
for rep,aa in per_rep.items():
 assert len({(z['bank'],z['orthogonal_route_id'])for z in aa})==783
 for stage in range(9):
  for pair in range(4):
   data={rep*960+(2*pair+r//120)*120+r%120 for r in range(240)}
   assert len(data)==240 and all(0<=f<30720 for f in data)
   owners={(30720+stage*3131+z['bank'],z['orthogonal_route_id'])for z in aa}
   assert len(owners)==783 and all(30720<=f<58899 for f,r in owners)
assert b['live']==58899 and b['banks_per_stage']==3131 and b['padding_rank1_per_stage']==3123
assert pins=={str(p.resolve()):hashlib.sha256(p.read_bytes()).hexdigest()for p in paths}
r={'status':'PASS_PROPOSED_BANK_SUBSPACES_INVERSES_AND_ALL_SINK_MAIN_FRAMES','source_hashes':pins,'routes':len(routers),'assignments':len(assign),'banks':len(used),'rank1_padding':3123,'nonsymmetric_routes':sum(A!=tr(A)for A in routers),'inverse_route_recipes':[[format(z,'073b')for z in tr(A)]for A in routers],'sink_normal_axes':normal_images[:8],'stage_replica_pair_owner_checks':9*32*4,'global_emission_requirements':['Bind this exact bank witness and endpoint phase receipts in global template','Use matrix transpose for inverse owner routes;14 recipes are not symmetric','Emit both exact rank8 canonical-to-coordinate phase adapters; the inverse-adjoint dual preserves unitary address operators','Use the actual scalar coefficient primitive counts, not structural61161 metadata','Count every288 invocation,3131banks perstage,3123rank1padding perstage,all-live cover correction and private stock'],'scope':'Binary proposed-bank review only; requires emitted local scalar/charts/phase and global finite invoice.'}
x.output.write_text(json.dumps(r,indent=2));print({k:v for k,v in r.items()if k not in ['inverse_route_recipes','source_hashes']})


