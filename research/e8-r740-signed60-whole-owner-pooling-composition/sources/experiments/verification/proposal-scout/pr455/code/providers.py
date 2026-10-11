"""Instantiate one of four complete exact local providers.
The invocation controller must charge actual residual owners; no split is permitted.
"""
from pathlib import Path
import argparse,json,hashlib,copy
ap=argparse.ArgumentParser();ap.add_argument('source',type=Path);ap.add_argument('selection',type=Path);ap.add_argument('count',type=int,choices=range(4));ap.add_argument('output',type=Path);a=ap.parse_args()
c=json.loads(a.source.read_text());w=json.loads(a.selection.read_text());assert hashlib.sha256(a.source.read_bytes()).hexdigest()==w['source_sha256'];drop=set([963,970,948][:a.count])
for p in drop:
 assert c['start'][p]!=0;c['start'][p]=0
 for i in w['restore'][str(p)]:
  assert p not in c['D'][i][2];c['D'][i][2]=sorted(c['D'][i][2]+[p])
for ph in ['A','C']:
 gs=[]
 for i,(f,t,ss)in enumerate(c[ph]):
  selected=i<w['A_head'] if ph=='A' else i>=len(c['C'])-w['C_tail'];ns=[p for p in ss if p not in drop] if selected else ss
  if selected and not ns:continue
  gs.append([f,t,ns])
 c[ph]=gs
blob=json.dumps(c,sort_keys=True,separators=(',',':')).encode();expected=['c80eadc14fc3365e61c90e7c717fb0c35c9a9a4a90da6f4bb13d6c27f3789c97','55907246f00b577f20451f72cd099b62b8094f37197fb616f46c63b9ea92ee14','43be68ade7b1e9a75d653c6f8015d08f906d5f00789b84c5fe04c4477b2d1102','7be496ae3431b25d9dbc1c1e16beea883892054c6da10dcc784cfb5979e991da']
assert hashlib.sha256(blob).hexdigest()==expected[a.count];assert not a.output.exists();a.output.write_bytes(blob);print(expected[a.count])
