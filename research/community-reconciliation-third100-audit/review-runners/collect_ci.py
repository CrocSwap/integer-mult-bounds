import json,gzip,subprocess,concurrent.futures,hashlib,re,time
from pathlib import Path
P=Path('/tmp/reconciliation-third100-20261013'); rows=json.load(gzip.open(P/'SOURCES.json.gz','rt'))['pull_requests'];snap={r['number']:r for r in json.load(open(P/'checks.json'))}
def api(path):
 for attempt in range(3):
  proc=subprocess.run(['gh','api',path],capture_output=True)
  if proc.returncode==0:return json.loads(proc.stdout)
  if attempt==2:raise RuntimeError(proc.stderr.decode()[:300])
  time.sleep(2)
def work(row):
 n=row['number'];head=row['head'];changed={x['path']for x in row['changed_files']}; repos=['CrocSwap/integer-mult-bounds'];fork=snap[n]['headRepository']['nameWithOwner']
 if fork not in repos:repos.append(fork)
 rr=[];logs=[]
 for repo in repos:
  data=api(f'repos/{repo}/actions/runs?head_sha={head}&per_page=100')
  for run in data['workflow_runs']:
   path=run['path'].split('@')[0]
   if run['head_sha']!=head or not (path in changed or n==318 and 'research' in run['name'].lower()):continue
   jobs=api(f'repos/{repo}/actions/runs/{run["id"]}/jobs?per_page=100')['jobs']; rr.append(dict(repo=repo,id=run['id'],url=run['html_url'],head=head,path=path,name=run['name'],conclusion=run['conclusion'],jobs=jobs))
   # Keep one interpreter per identical matrix lane, plus distinct regeneration/checker jobs.
   groups={}
   for j in jobs:
    key=re.sub(r'3\.(?:11|12|13|14|15)', 'PY',j['name']);old=groups.get(key)
    if old is None or ('3.14' in j['name'] and j['conclusion']=='success'):groups[key]=j
   for j in groups.values():
    if j['status']!='completed':continue
    raw=subprocess.check_output(['gh','api',f'repos/{repo}/actions/jobs/{j["id"]}/logs']);name=f'pr{n}-ci-{j["id"]}.txt.gz';(P/name).write_bytes(gzip.compress(raw,mtime=0));lines=raw.decode(errors='replace').splitlines();checkout=[]
    for i,line in enumerate(lines):
     if "git log -1 --format=%H" in line and i+1<len(lines):
      found=re.findall(r'\b[0-9a-f]{40}\b',lines[i+1]);checkout+=found
    evidence=[l for l in lines if re.search(r'(Run |PASS|FAIL|SUCCESS|ERROR|python.*verify|bash.*verify|E4|E5|E6)',l)]
    logs.append(dict(job=j['id'],name=j['name'],conclusion=j['conclusion'],run=run['id'],workflow=path,file=name,log_sha256=hashlib.sha256(raw).hexdigest(),checkout_heads=list(dict.fromkeys(checkout)),evidence=evidence[-100:]))
 return dict(number=n,head=head,runs=rr,inspected_logs=logs)
out=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
 fut={ex.submit(work,r):r for r in rows}
 for f in concurrent.futures.as_completed(fut):
  r=fut[f]
  try:x=f.result()
  except Exception as e:x=dict(number=r['number'],head=r['head'],runs=[],inspected_logs=[],error=str(e))
  out.append(x);(P/'ci-evidence.json').write_text(json.dumps(sorted(out,key=lambda x:x['number']),indent=2)+'\n');print(x['number'],'runs',len(x['runs']),'logs',len(x['inspected_logs']),x.get('error',''),flush=True)
