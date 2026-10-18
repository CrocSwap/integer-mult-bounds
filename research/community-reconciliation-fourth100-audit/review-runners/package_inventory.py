import json,gzip,hashlib,collections
from pathlib import Path
P=Path('/tmp/reconciliation-fourth100-20261013');R=Path('/tmp/integer-mult-queue-20261013');rows=json.load(gzip.open(P/'SOURCES.json.gz','rt'))['pull_requests'];old={}
for audit in ['community-reconciliation-third100-audit','community-reconciliation-next100-audit','community-reconciliation92-audit']:
 for r in json.load(gzip.open(R/f'research/{audit}/SOURCES.json.gz','rt'))['pull_requests']:
  dec={x['number']:x for x in json.load(open(R/f'research/{audit}/DISPOSITIONS.json'))['pull_requests']}[r['number']];gr=collections.defaultdict(list)
  for f in r['files']:
   if f['path'].startswith('research/') and len(f['path'].split('/'))>2:gr['/'.join(f['path'].split('/')[:2])].append([f['path'],f['mode'],f['blob']])
  for root,fs in gr.items():
   sig=hashlib.sha256(json.dumps(fs,separators=(',',':')).encode()).hexdigest();old.setdefault(sig,[]).append(dict(number=r['number'],root=root,disposition=dec['disposition'],head=r['head']))
result=[]
for r in rows:
 gr=collections.defaultdict(list);changes={f['path']for f in r['changed_files']}
 for f in r['files']:
  if f['path'].startswith('research/') and len(f['path'].split('/'))>2:gr['/'.join(f['path'].split('/')[:2])].append([f['path'],f['mode'],f['blob']])
 packages=[]
 for root,fs in gr.items():
  if not any(f[0]in changes for f in fs):continue
  sig=hashlib.sha256(json.dumps(fs,separators=(',',':')).encode()).hexdigest();packages.append(dict(root=root,files=len(fs),fingerprint=sig,previous_exact_package=old.get(sig,[])))
 result.append(dict(number=r['number'],packages=packages))
(P/'package-inventory.json').write_text(json.dumps(result,indent=2)+'\n')
for r in result:
 if r['number'] in [309,321,355,360,390,398,401,404,392,400,403]:
  print(r['number'],[(x['root'].split('/')[-1],[(a['number'],a['disposition'])for a in x['previous_exact_package'] if a['disposition']=='incorporated'][-2:])for x in r['packages']])
