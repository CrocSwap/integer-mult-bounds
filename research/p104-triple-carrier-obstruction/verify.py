"""Portable offline replay for the exact rational triple obstruction.
Jerry Chen / @CubeJerry, substantial OpenAI Codex assistance. Apache-2.0.
"""
from hashlib import sha1,sha256
from pathlib import Path
import json,runpy
HERE=Path(__file__).resolve().parent
def need(condition,message):
 if not condition:raise ValueError(message)
def chain_entry(rows,name,raw):
 matches=[item for item in rows if item['path']==name]
 need(len(matches)==1,'Unique first-party source-chain entry '+name)
 item=matches[0]
 need(item['sha256']==sha256(raw).hexdigest(),'First-party SHA256 chain '+name)
 need(item['git_blob']==sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest(),'First-party Git-blob chain '+name)
def main():
 origins=json.loads((HERE/'ORIGINS.json').read_text())
 for item in origins['files']:
  raw=(HERE/item['path']).read_bytes()
  need(len(raw)==item['bytes']and sha256(raw).hexdigest()==item['sha256'],'Exact retained input '+item['path'])
 outer=json.loads((HERE/'retained/PR6702-RETAINED.json').read_text())
 nested_raw=(HERE/'retained/PR6702-NATIVE-RETAINED.json').read_bytes()
 chain_entry(outer['files'],'research/gaussian-root-retirement/RETAINED.json',nested_raw)
 nested=json.loads(nested_raw)
 chain_entry(nested['native']['files'],'research/p104-scaled-transport-fusion/WORD.json.gz',(HERE/'inputs/PR6702-WORD.json.gz').read_bytes())
 primary=runpy.run_path(str(HERE/'generate.py'))['generate']()
 # JSON round-trip normalizes integer object keys and tuple/list encodings.
 need(json.loads(json.dumps(primary))==json.loads((HERE/'CERTIFICATE.json').read_text()),'Entire regenerated rational certificate')
 review=runpy.run_path(str(HERE/'review.py'))['check']()
 need(review==json.loads((HERE/'SSA-REVIEW.json').read_text()),'Separate full forward-SSA review receipt')
 scalar=runpy.run_path(str(HERE/'check_carrier_potentials.py'))['check'](HERE)
 need(scalar==json.loads((HERE/'SCALAR-ADJOINT-REVIEW.json').read_text()),'Independent literal-cut scalar-adjoint receipt')
 print('PASS_P104_TRIPLE_CARRIER_OBSTRUCTION: 14 exact triples; 42 rational duals; 1064 direct dot products; all 98 proper-frame topologies; 14 chronological positive controls; 126 mutation controls; 227055 independent literal-cut checks; no new kappa')
if __name__=='__main__':main()
