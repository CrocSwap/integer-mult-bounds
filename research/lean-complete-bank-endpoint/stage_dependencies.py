#!/usr/bin/env python3
"""Offline source staging only; never downloads or invokes a compiler."""
from pathlib import Path
import argparse,hashlib,json,re
P=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--pr509',required=True);ap.add_argument('--pr516',required=True);ap.add_argument('--pr513',required=True);ap.add_argument('--output',required=True);a=ap.parse_args()
 lock=json.loads((P/'DEPENDENCIES.json').read_text());roots={k:Path(getattr(a,k)).resolve()for k in ['pr509','pr516','pr513']};roots['this_package']=P
 prepared=[];seen=set()
 for row in lock['compile_order']:
  src=roots[row['dependency']]/row['input_file'];data=src.read_bytes();assert sha(data)==row['input_sha256'],str(src)
  rule=row['transformation']
  if rule:
   before=rule['from'].encode();after=rule['to'].encode();assert data.count(before)==rule['count']==1
   transformed=data.replace(before,after);assert transformed.replace(after,before)==data;data=transformed
  assert sha(data)==row['staged_sha256'],row['module']
  imports=re.findall(r'^import (\S+)\s*$',data.decode(),re.M);assert imports==row['imports']
  assert set(imports)-{'Lean'}-set(lock.get('allowed_external_direct_imports',[]))<=seen,imports
  seen.add(row['module']);prepared.append((row,data))
 assert len(prepared)==9 and len({r['module']for r,_ in prepared})==9
 out=Path(a.output).resolve();out.mkdir(parents=True,exist_ok=False)
 result=[]
 for row,data in prepared:
  dest=out/row['staged_file'];assert dest.parent==out
  with dest.open('xb')as f:f.write(data)
  result.append(dict(module=row['module'],file=dest.name,sha256=sha(dest.read_bytes()),bytes=len(data),imports=row['imports'],dependency=row['dependency']))
 report=dict(status='SOURCE_STAGING_ONLY_NO_COMPILER',dependency_lock_sha256=sha((P/'DEPENDENCIES.json').read_bytes()),compile_order=result,local_modules=9)
 (out/'STAGED_SOURCES.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
