from pathlib import Path
import subprocess,json,hashlib
P=Path('/tmp/pr-efficient1900');R=Path('/tmp/integer-mult-efficient1100-20261015');cache={};count=0
for n in [2874,2877,2882,2902,2905]:
 pkg=next(q for q in (P/'sources'/str(n)/'research').iterdir() if (q/'VERIFY.json').exists());source=json.loads((pkg/'SOURCES.json').read_text());rows=[]
 if (pkg/'SNAPSHOTS.json').exists():
  for row in json.loads((pkg/'SNAPSHOTS.json').read_text())['files']:rows.append((row['path'],row['commit']+':'+row['git_path'],row['blob'],row['sha256']))
 elif (pkg/'EXPORTS.json').exists():
  for row in json.loads((pkg/'EXPORTS.json').read_text())['files']:rows.append((row['path'],row['commit']+':'+row['source_path'],row['git_blob'],row['sha256']))
 else:
  for row in source['exports']:
   pin=row['pin'].removeprefix('head:') if 'pin' in row else row['source_head']+':'+row['source_path'];rows.append((row['export'],pin,row['git_blob'],row['sha256']))
 out=[]
 for rel,pin,blob,sha in rows:
  if pin not in cache:cache[pin]=subprocess.check_output(['git','show',pin],cwd=R)
  raw=cache[pin];assert raw==(pkg/rel).read_bytes(),(n,rel);assert hashlib.sha256(raw).hexdigest()==sha;assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==blob;out.append(dict(export=rel,git_pin=pin,git_blob=blob,sha256=sha));count+=1
 (P/f'provenance-{n}-exports.json').write_text(json.dumps(dict(status='PASS',number=n,scope='Every exported source independently matched to its original commit/path, Git blob and SHA256. Repeated original objects read once; all package-specific copies compared.',files=out),indent=2)+'\n');print(n,len(out),'Git-authenticated original exports')
print('Total',count,'exports;',len(cache),'distinct original objects')
