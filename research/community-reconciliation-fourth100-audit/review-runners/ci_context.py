import json,gzip,subprocess,concurrent.futures,time
from pathlib import Path
P=Path('/tmp/reconciliation-fourth100-20261013');rows={r['number']:r for r in json.load(gzip.open(P/'SOURCES.json.gz','rt'))['pull_requests']};ci=json.load(open(P/'ci-evidence.json'));jobs={}
for r in ci:
 runs={x['id']:x for x in r['runs']}
 for log in r['inspected_logs']:
  for head in log['checkout_heads']:
   jobs[(r['number'],head,runs[log['run']]['repo'])]=log

def api(repo,path):
 for attempt in range(3):
  p=subprocess.run(['gh','api','repos/'+repo+'/'+path],capture_output=True)
  if p.returncode==0:return json.loads(p.stdout)
  if attempt==2:raise RuntimeError(p.stderr.decode()[:200])
  time.sleep(2)
def work(key):
 n,h,repo=key;row=rows[n]
 try:
  c=api(repo,'git/commits/'+h);t=api(repo,'git/trees/'+c['tree']['sha']+'?recursive=1');assert not t['truncated']
  fs={x['path']:x for x in t['tree']if x['type']=='blob'};bad=[]
  for f in row['files']:
   q=fs.get(f['path'])
   if q is None or q['sha']!=f['blob']or q['mode']!=f['mode']:bad.append(dict(path=f['path'],submitted_blob=f['blob'],executed=q))
  changed={f['path']for f in row['changed_files']};return dict(number=n,repo=repo,submitted_head=row['head'],checkout_head=h,checkout_commit=c,checkout_tree=t,all_submitted_files_match=not bad,mismatches=bad,changed_file_mismatches=[x for x in bad if x['path']in changed])
 except Exception as e:return dict(number=n,checkout_head=h,error=str(e))
out=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
 for r in ex.map(work,jobs):
  out.append(r);(P/'ci-source-context.json.gz').write_bytes(gzip.compress(json.dumps(out,separators=(',',':')).encode(),mtime=0));print(r['number'],r['checkout_head'][:8],'mismatches',len(r.get('mismatches',[])),'changed',len(r.get('changed_file_mismatches',[])),r.get('error',''),flush=True)
