"""Bind one real CLEAR output coordinate to a public pinned WORD and native map."""
import hashlib,importlib.util,json
from pathlib import Path
from fractions import Fraction as Q

def module(path,name):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def verify():
 root=Path(__file__).parent
 pins=json.loads((root/'VENDORED.json').read_text())
 for r in pins['files']:
  if hashlib.sha256((root/r['path']).read_bytes()).hexdigest()!=r['sha256']:raise ValueError('source integrity mismatch')
 src=root/'source7669';m=module(src/'replay.py','public_replay');v=module(src/'native_verify.py','public_native')
 word=m.reconstruct(m.read(src/'data/K372-2-WORD.json.gz'),m.read(src/'EDIT.json'))
 cert=m.read(src/'data/CERTS.json');assert m.digest(word)=='ee251f6005d2a92b887c5b804bd7aac05989d278b2c9ccb3c3091b50d533b08d'
 event=88937;assert word['program'][event]==['CLEAR',1502,353]
 charts=dict(enumerate(word['initial']))
 for e in word['program'][:event]:
  if e[0]=='INIT':assert e[1] not in charts;charts[e[1]]=e[2]
  elif e[0]=='MOVE':assert charts[e[1]]==e[2];charts[e[1]]=e[3]
  elif e[0]=='CLEAR':del charts[e[1]]
 assert cert['clear_event_index'][str(event)]=={'1072':'1','500':'-1'}
 assert charts[1072]==charts[500]==359 and charts[1502]==353
 route=v.adjoint(v.frame(tuple(word['frames'][359]),9))+v.frame(tuple(word['frames'][353]),9)
 row=[]
 # Each complex column determines both its real and imaginary input columns.
 for basis in range(512):
  col,power=v.state(route,basis);re,im=col.get(0,(0,0))
  for limb,n in [(0,re),(1,-im)]:
   if n:row.append((limb,basis,Q(n,1<<power)))
 assert sorted(row)==[(0,0,Q(1,2)),(0,102,Q(1,2)),(1,0,Q(1,2)),(1,102,Q(1,2))]
 # A deliberate global phase error must change the selected row.
 wrong=v.state(route+(('phase',1),),0);assert wrong!=v.state(route,0)
 return {'candidate_canonical_sha256':m.digest(word),'event_zero_based':event,'target':1502,'target_chart':353,'donors':{'1072':{'coefficient':1,'chart':359},'500':{'coefficient':-1,'chart':359}},'output_limb':['real',0],'source_columns_checked':512,'realified_source_columns':1024,'integer_coefficients':[1,1,1,1,-1,-1,-1,-1],'denominator':2,'phase_negative_control':True,'scope':'One real output row; exact published native interpreter reused. No rounded-input reachability, complete CLEAR or physical compiler claim.'}
if __name__=='__main__':print(json.dumps(verify()))
