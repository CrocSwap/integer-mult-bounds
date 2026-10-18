import json,gzip,subprocess
from pathlib import Path
P=Path('/tmp/reconciliation-next100-20261013');row=next(r for r in json.load(gzip.open(P/'SOURCES.json.gz','rt'))['pull_requests']if r['number']==266);h='a60acd7d628d9ff40b5f934c6f8695ce720aa40a'
def api(path):return json.loads(subprocess.check_output(['gh','api','repos/CrocSwap/integer-mult-bounds/'+path],text=True))
c=api('git/commits/'+h);t=api('git/trees/'+c['tree']['sha']+'?recursive=1');assert not t['truncated'];fs={x['path']:x for x in t['tree']if x['type']=='blob'};m=[]
for f in row['files']:
 q=fs.get(f['path'])
 if q is None or q['sha']!=f['blob']or q['mode']!=f['mode']:m.append(dict(path=f['path'],submitted_blob=f['blob'],executed=q))
assert not m,m
changed={f['path']for f in row['changed_files']};r=dict(number=266,submitted_head=row['head'],checkout_head=h,checkout_commit=c,checkout_tree=t,all_submitted_files_match=True,mismatches=[],changed_file_mismatches=[]);allr=json.load(gzip.open(P/'ci-source-context.json.gz','rt'));allr=[v for v in allr if v['number']!=266]+[r];(P/'ci-source-context.json.gz').write_bytes(gzip.compress(json.dumps(allr,indent=2).encode(),mtime=0));r=dict(number=266,log='pr266-ci-114133084222.txt.gz',submitted_head=row['head'],checkout_heads=[h],exact_checkout=False,commands=['##[group]Run python3 -I research/multicut-kernel-composition/verify.py --output /tmp/mkc-replay']);allr=json.load(open(P/'ci-checkout-context.json'));allr=[v for v in allr if v['number']!=266]+[r];(P/'ci-checkout-context.json').write_text(json.dumps(allr,indent=2)+'\n');print('PASS PR266 complete submitted source matches actual Linux checkout',len(row['files']))
