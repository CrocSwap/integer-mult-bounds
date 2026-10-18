import json,subprocess,concurrent.futures,re,gzip,hashlib
from pathlib import Path
P=Path('/tmp/reconciliation92-20261013');rows=json.loads((P/'checks.json').read_text())
def api(url):return json.loads(subprocess.check_output(['gh','api',url],text=True))
def inspect(r):
 n=r['number'];repo=r['headRepository']['nameWithOwner'];head=r['headRefOid']
 checks=r['statusCheckRollup'];runs={}
 if not checks:
  data=api(f'repos/{repo}/actions/runs?head_sha={head}&per_page=100')
  for run in data['workflow_runs']:
   if run['head_sha']==head and run['conclusion']=='success':runs[(repo,run['id'])]=run
 else:
  for c in checks:
   m=re.search(r'https://github.com/([^/]+/[^/]+)/actions/runs/(\d+)/job/(\d+)',c.get('detailsUrl',''))
   if m and c.get('conclusion')=='SUCCESS':
    key=(m[1],int(m[2]));runs.setdefault(key,None)
 for key,v in list(runs.items()):
  if v is None:runs[key]=api(f'repos/{key[0]}/actions/runs/{key[1]}')
 selected=[];runrows=[]
 for (owner,rid),run in runs.items():
  if run['head_sha']!=head:continue
  jobs=api(f'repos/{owner}/actions/runs/{rid}/jobs?per_page=100')['jobs']
  runrows.append(dict(repo=owner,id=rid,url=run['html_url'],head=run['head_sha'],conclusion=run['conclusion'],jobs=[dict(id=j['id'],name=j['name'],conclusion=j['conclusion'],steps=[dict(name=s['name'],conclusion=s.get('conclusion')) for s in j.get('steps',[])]) for j in jobs]))
  for j in jobs:
   name=j['name']
   if j['conclusion']!='success':continue
   relevant=('3.13' in name and any(x in name for x in ('research','joint','frame','cyclic','paired','selected','coordinate','complex','bit','sharing','terminal','depth','word','final','aligned','climbed','copied')))
   relevant|=(len(jobs)<=4 and ('3.13' in name or not re.search(r'3\.(11|12|14)',name)))
   relevant|=(n in (91,141) and name=='formal (matrix)')
   if not relevant:continue
   log=subprocess.check_output(['gh','api',f'repos/{owner}/actions/jobs/{j["id"]}/logs'])
   namefile=f'pr{n}-ci-{j["id"]}.txt.gz';(P/namefile).write_bytes(gzip.compress(log,mtime=0))
   lines=log.decode(errors='replace').splitlines()
   evidence=[line for line in lines if any(x in line for x in ('Run ','PASS','SUCCESS','FAIL','Ran ','tests','git diff','python','HEAD is now'))]
   selected.append(dict(job=j['id'],name=name,file=namefile,log_sha256=hashlib.sha256(log).hexdigest(),lines=len(lines),evidence=evidence[-120:]))
 return dict(number=n,head=head,runs=runrows,inspected_logs=selected)
results=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
 future={ex.submit(inspect,r):r['number'] for r in rows}
 for f in concurrent.futures.as_completed(future):
  n=future[f]
  try:r=f.result()
  except Exception as e:r={'number':n,'error':str(e)}
  results.append(r);(P/'ci-evidence.json').write_text(json.dumps(sorted(results,key=lambda r:r['number']),indent=2)+'\n')
  print(n,'runs',len(r.get('runs',[])),'logs',len(r.get('inspected_logs',[])),r.get('error',''),flush=True)
