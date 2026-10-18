from pathlib import Path
import json,subprocess,hashlib
P=Path('/tmp/pr-efficient1900');R=Path('/tmp/integer-mult-efficient1100-20261015')
def verify(n,items):
 out=[]
 for snap,commit,rel,pin in items:
  raw=subprocess.check_output(['git','show',commit+':'+rel],cwd=R)
  assert snap.read_bytes()==raw,(n,rel)
  sha=hashlib.sha256(raw).hexdigest();blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
  assert sha==pin['sha256'] and ('git_blob' not in pin or blob==pin['git_blob'])
  out.append(dict(snapshot=str(snap.relative_to(P/'sources'/str(n))),commit=commit,path=rel,sha256=sha,git_blob=blob))
 (P/f'provenance-{n}-exports.json').write_text(json.dumps(dict(status='PASS',scope='Vendored bytes authenticated to original Git commit/path/blob, not just self-declared hashes.',files=out),indent=2)+'\n');print(n,len(out),'exports PASS')
d=P/'sources/2876/research/qq16-block-scale-scan';m=json.loads((d/'PREDECESSOR.json').read_text());verify(2876,[(d/x['snapshot'],x['snapshot_commit'],x['source'],x) for x in m['files']])
d=P/'sources/2893/research/t185-integral-optimal-face';m=json.loads((d/'SOURCE-EXPORT.json').read_text());verify(2893,[(d/x['export'],x['commit'],x['original_path'],x) for x in m['files']])
d=P/'sources/2904/research/t185-dirty-entry-frame-screens';m=json.loads((d/'vendor/INPUTS.json').read_text());verify(2904,[(d/x['path'],x['source_head'],x['source_path'],x) for x in m['files']])
d=P/'sources/2918/research/helper408-rank7-pairing';m=json.loads((d/'SOURCE-PINS.json').read_text());tree=subprocess.check_output(['git','ls-tree','-r',m['source_commit']],cwd=R,text=True);entries={line.split()[2]:line.split('\t',1)[1] for line in tree.splitlines()};verify(2918,[(d/'sources'/rel,m['source_commit'],entries[x['git_blob']],x) for rel,x in m['files'].items()])
d=P/'sources/2903/research/qq16-numerical-contract-navigation';m=json.loads((d/'PENDING.json').read_text());verify(2903,[(d/x['path'],m['head'],'research/qq16-block-scale-scan/'+x['path'].split('PR2876-',1)[1],x) for x in m['files']])
