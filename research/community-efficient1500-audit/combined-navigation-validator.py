from pathlib import Path
import subprocess,json,hashlib,re,posixpath,sys
P=Path('/tmp/pr-efficient1500');R=Path('/tmp/integer-mult-efficient1100-20261015');n=int(sys.argv[1]);meta=json.loads((P/f'{n}.json').read_text());files=json.loads((P/'packets'/f'{n}.json').read_text())['files'];inputs={};links=[]
for f in files:
 rel=f['path'];path=P/'resolutions'/rel
 if not path.exists():path=P/'sources'/str(n)/rel
 data=path.read_bytes();inputs[rel]=hashlib.sha256(data).hexdigest()
 for link in re.findall(r'\]\(([^\s)]+)\)',data.decode()):
  if link.startswith(('https://','http://','#','mailto:')):continue
  target=posixpath.normpath(posixpath.join(posixpath.dirname(rel),link.split('#',1)[0]))
  assert not target.startswith('../'),target
  if target not in [x['path'] for x in files]:subprocess.run(['git','cat-file','-e','HEAD:'+target],cwd=R,check=True,stdout=subprocess.DEVNULL)
  links.append([rel,target])
if n==2510:
 text=(P/'resolutions/docs/research/current-status.md').read_text()
 for i in range(100,1501,100):assert f'(community-efficient{i}-review.md)' in text
 assert 'fifteenth round is ongoing' in text and 'frozen review checkpoints, not live queue counts' in text
 for i,counts in [(1100,(79,21)),(1200,(78,22)),(1300,(76,24)),(1400,(78,22))]:
  original=subprocess.check_output(['git','show',f'HEAD:docs/research/community-efficient{i}-review.md'],cwd=R,text=True)
  assert f'{counts[0]} observed merged; {counts[1]} pending' in original
elif n==2585:
 text=(P/'sources/2585/docs/research/paired-plane-contract-map.md').read_text()
 frozen=re.findall(r'https://github.com/CrocSwap/integer-mult-bounds/blob/([0-9a-f]{40})/([^\s)]+)',text)
 for commit,path in frozen:
  data=subprocess.check_output(['git','show',commit+':'+path],cwd=R);inputs[commit+':'+path]=hashlib.sha256(data).hexdigest()
 assert len(frozen)==4
else:raise ValueError(n)
raw=(R/'certificates/selected-result.json').read_bytes();record=json.loads(raw)
assert hashlib.sha256(raw).hexdigest()=='10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32'
assert hashlib.sha256(subprocess.check_output(['git','show','HEAD:'+record['certificate']],cwd=R)).hexdigest()==record['certificate_sha256']
print(json.dumps(dict(status='PASS',number=n,head=meta['headRefOid'],input_sha256=inputs,local_links=links,selected_record_sha256=hashlib.sha256(raw).hexdigest(),scope='Navigation, frozen citations and unchanged selected record/certificate only; no mathematical replay. Full baseline binding check separately found an existing proof-supplement script digest mismatch; see combined-baseline-existing-mismatch.json.')))
