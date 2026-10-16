# SPDX-License-Identifier: Apache-2.0
"""Four rejecting controls for the standalone shared-kernel owner auditor.
Prepared by Yiyang with OpenAI Codex assistance. Inputs remain read-only.
"""
import argparse,copy,gzip,hashlib,json,tempfile,types
from pathlib import Path
ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--source-dir',type=Path,required=True);ap.add_argument('--candidate-dir',type=Path,required=True);ap.add_argument('--words-dir',type=Path,required=True);ap.add_argument('--work-dir',type=Path,required=True);a=ap.parse_args()
p=Path(__file__).with_name('audit_owners.py');raw=p.read_bytes();m=types.ModuleType('independent_owner_auditor');m.__file__=str(p);exec(compile(raw,str(p),'exec'),m.__dict__)
a.work_dir.mkdir(parents=True,exist_ok=True);results=[]
def shadow(src,dst):
 dst.mkdir()
 for f in src.iterdir():
  if f.is_file():(dst/f.name).symlink_to(f.resolve())
def write(dst,name,data):
 p=dst/name
 if p.is_symlink():p.unlink()
 p.write_bytes(data)
with tempfile.TemporaryDirectory(dir=a.work_dir)as temp:
 root=Path(temp)
 for case,reason in [('same_mass_wrong_profile','provider bound to fixed word'),('invalid_source_window','strict source-event window'),('overlapping_offsets','bin capacity or overlapping offsets'),('source_byte_mutation','source SHA256')]:
  D=root/case;D.mkdir();src=D/'sources';cand=D/'candidate';shadow(a.source_dir,src);shadow(a.candidate_dir,cand)
  if case=='same_mass_wrong_profile':
   v=json.loads((cand/'PROVIDERS.json').read_bytes());prof=v['gauge44']['actual_paid_profile'];prof['1']-=2;prof['2']+=1;write(cand,'PROVIDERS.json',json.dumps(v).encode())
  elif case=='invalid_source_window':
   v=json.loads(gzip.decompress((cand/'FILL.json.gz').read_bytes()));row=next(r for r in v['rows']if r[0]==0);row[2:]=[0,12,0,0];write(cand,'FILL.json.gz',gzip.compress(json.dumps(v).encode(),mtime=0))
  elif case=='overlapping_offsets':
   v=json.loads(gzip.decompress((cand/'FILL.json.gz').read_bytes()));seen={}
   for row in v['rows']:
    key=tuple(row[2:5])
    if key in seen:row[5]=seen[key];break
    seen[key]=row[5]
   else:raise ValueError('no multi-role bin for overlap control')
   write(cand,'FILL.json.gz',gzip.compress(json.dumps(v).encode(),mtime=0))
  else:
   n='PR2833-T37-DISPATCH.json';write(src,n,(src/n).read_bytes()+b'\n')
  try:m.audit(src,cand,a.words_dir)
  except ValueError as e:
   if reason not in str(e):raise ValueError((case,'unexpected rejection',str(e)))
   results.append({'case':case,'status':'REJECTED','reason':str(e)})
  else:raise ValueError((case,'mutant accepted'))
print(json.dumps({'status':'PASS_TARGETED_INDEPENDENT_OWNER_CONTROLS','auditor_sha256':hashlib.sha256(raw).hexdigest(),'controls':results},sort_keys=True,indent=2))
