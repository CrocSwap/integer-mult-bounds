#!/usr/bin/env python3
"""Two real-file tamper controls for the archived-evidence checker; no science replay."""
import argparse,hashlib,json,shutil,subprocess,sys,tempfile
from pathlib import Path
ap=argparse.ArgumentParser()
for n in ('checker','package','source','out'):ap.add_argument('--'+n,type=Path,required=True)
a=ap.parse_args();checker=a.checker.resolve();package=a.package.resolve();source=a.source.resolve();E=package/'evidence/full'
if a.out.exists():raise ValueError('fresh output required')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();tests=[]
with tempfile.TemporaryDirectory(prefix='p53-evidence-controls-') as temp:
 d=Path(temp);bad_e=d/'bad-evidence';shutil.copytree(E,bad_e)
 p=bad_e/'candidate/RESULT.json';x=json.loads(p.read_bytes());x['status']='FAILED_MUTANT';p.write_text(json.dumps(x)+'\n')
 bad_p=d/'bad-package';bad_p.mkdir();shutil.copy2(package/'CLAIM.json',bad_p/'CLAIM.json');shutil.copytree(package/'data',bad_p/'data')
 p=bad_p/'data/CANDIDATE.json';x=json.loads(p.read_bytes());x['target']='0';p.write_text(json.dumps(x)+'\n')
 for name,P,A,reason in [('actual_release_status_changed',package,bad_e,'all167 archived evidence files'),('current_candidate_target_changed',bad_p,E,'current exact candidate/claim target')]:
  argv=[sys.executable,'-I','-O','-B',str(checker),'--package',str(P),'--source',str(source),'--evidence',str(A)]
  r=subprocess.run(argv,text=True,capture_output=True)
  if r.returncode==0 or reason not in r.stderr:raise ValueError('wrong outcome: '+name+' '+r.stderr)
  tests.append({'name':name,'rejected':True,'exit_code':r.returncode,'reason':r.stderr.strip().splitlines()[-1]})
record={'status':'PASS_ARCHIVED_EVIDENCE_TAMPER_CONTROLS','checker_sha256':sha(checker),'source_manifest_sha256':sha(source/'MANIFEST.json'),'evidence_manifest_sha256':sha(E/'MANIFEST.json'),'controls':tests,'scope':'Actual temporary-copy byte/status and current-candidate target mutations. Originals unchanged; no scientific replay.'}
a.out.write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2))
