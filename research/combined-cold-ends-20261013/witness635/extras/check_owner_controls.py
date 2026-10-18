"""Targeted rejection controls for the independent owner/moment checker.
Chi Zhao, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse,copy,gzip,json,subprocess,sys,tempfile
from pathlib import Path
from fractions import Fraction as Q
ap=argparse.ArgumentParser();ap.add_argument('--package',type=Path,required=True);ap.add_argument('--replay',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
checker=Path(__file__).resolve().with_name('check_native_owners.py')
original={name:json.loads(gzip.decompress((a.package/'data'/name).read_bytes()) if name.endswith('.gz') else (a.package/'data'/name).read_bytes()) for name in ('SPEC.json','PLAN.json','OWNERS.json.gz')}
cases=[('positive',None),('wrong_width','actual width'),('duplicate_helper','helper uniqueness'),('wrong_family','physical family'),('wrong_profile','native plus idle profile'),('false_moment','strict exact moment')];results=[]
for name,expected in cases:
 data=copy.deepcopy(original);roles=data['OWNERS.json.gz'];spec=data['SPEC.json']
 if name=='wrong_width':roles[0]['width']+=1
 if name=='duplicate_helper':roles[1]['helper']=roles[0]['helper']
 if name=='wrong_family':roles[0]['family']+=100000
 if name=='wrong_profile':spec['expected']['global_profile']['1']+=1
 if name=='false_moment':spec['expected']['complex_lower']=str(Q(spec['expected']['complex_lower'])+Q(1,10**8))
 with tempfile.TemporaryDirectory(prefix='combined-owner-control-')as tmp:
  root=Path(tmp);(root/'data').mkdir()
  for filename,value in data.items():
   raw=json.dumps(value).encode();(root/'data'/filename).write_bytes(gzip.compress(raw,mtime=0) if filename.endswith('.gz') else raw)
  p=subprocess.run([sys.executable,'-I','-O','-B',str(checker),'--package',str(root),'--replay',str(a.replay),'--out',str(root/'result.json')],capture_output=True,text=True)
  if expected is None:
   if p.returncode:raise RuntimeError(p.stderr)
  elif not p.returncode or 'ValueError: '+expected not in p.stderr:raise RuntimeError(name+' unexpected result '+p.stdout+p.stderr)
  results.append(dict(name=name,status='PASS'if expected is None else'REJECTED',expected_reason=expected))
a.out.write_text(json.dumps(dict(status='PASS_INDEPENDENT_OWNER_CONTROLS',isolated_optimized=True,cases=results),indent=2)+'\n');print('PASS independent positive and five rejection controls')
