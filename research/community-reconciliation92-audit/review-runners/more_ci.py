import json,subprocess,gzip,hashlib,time
from pathlib import Path
P=Path('/tmp/reconciliation92-20261013');D=json.loads((P/'ci-evidence.json').read_text())
base={'community','ternary','research','clones','positive','joint','producers','pair','certificates','tests','strips','matrix','gaussian'}
for r in D:
 for run in r.get('runs',[]):
  for j in run['jobs']:
   name=j['name'];group=name.split(', ')[-1].rstrip(')')
   relevant=('3.13' in name and group not in base) or (r['number'] in [91,141] and name=='formal (historical)')
   if not relevant or j['conclusion']!='success' or any(l['job']==j['id'] for l in r['inspected_logs']):continue
   try:
    b=subprocess.check_output(['gh','api',f'repos/{run["repo"]}/actions/jobs/{j["id"]}/logs'],stderr=subprocess.DEVNULL)
   except subprocess.CalledProcessError:continue
   f=f'pr{r["number"]}-ci-{j["id"]}.txt.gz';(P/f).write_bytes(gzip.compress(b,mtime=0))
   r['inspected_logs'].append(dict(job=j['id'],name=name,file=f,log_sha256=hashlib.sha256(b).hexdigest(),lines=len(b.splitlines())))
   print(r['number'],name,flush=True)
 (P/'ci-evidence.json').write_text(json.dumps(D,indent=2)+'\n')
