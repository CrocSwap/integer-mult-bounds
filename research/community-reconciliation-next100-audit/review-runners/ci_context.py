import json,gzip,subprocess,concurrent.futures
from pathlib import Path
P=Path('/tmp/reconciliation-next100-20261013');R=Path('/tmp/integer-mult-queue-20261013');rows={r['number']:r for r in json.load(gzip.open(P/'SOURCES.json.gz','rt'))['pull_requests']};ci=json.load(open(P/'ci-checkout-context.json'));jobs={}
for r in ci:
 if r['checkout_heads'] and not r['exact_checkout']:jobs[(r['number'],r['checkout_heads'][0])]=r
# API tree is an authenticated GitHub listing; store exact Git tree IDs and compare all submitted files.
def api(path):return json.loads(subprocess.check_output(['gh','api','repos/CrocSwap/integer-mult-bounds/'+path],text=True))
def work(key):
 n,h=key;row=rows[n]
 try:
  c=api('git/commits/'+h);t=api('git/trees/'+c['tree']['sha']+'?recursive=1');assert not t['truncated']
  fs={x['path']:x for x in t['tree'] if x['type']=='blob'};mismatches=[]
  for f in row['files']:
   q=fs.get(f['path']);
   if q is None or q['sha']!=f['blob'] or q['mode']!=f['mode']:mismatches.append(dict(path=f['path'],submitted_blob=f['blob'],executed=q))
  changed={f['path'] for f in row['changed_files']};return dict(number=n,submitted_head=row['head'],checkout_head=h,checkout_commit=c,checkout_tree=t,all_submitted_files_match=not mismatches,mismatches=mismatches,changed_file_mismatches=[x for x in mismatches if x['path'] in changed])
 except Exception as e:return dict(number=n,checkout_head=h,error=str(e))
out=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
 for r in ex.map(work,jobs):out.append(r);print(r['number'],'mismatches',len(r.get('mismatches',[])),'changed',len(r.get('changed_file_mismatches',[])),r.get('error',''),flush=True)
(P/'ci-source-context.json.gz').write_bytes(gzip.compress(json.dumps(out,indent=2).encode(),mtime=0))
