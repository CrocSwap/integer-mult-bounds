from pathlib import Path
import json,subprocess,hashlib
P=Path('/tmp/pr-efficient1900'); R=Path('/tmp/integer-mult-efficient1100-20261015'); D=P/'sources/1830'; pkg=D/'research/h6-compensation-network';head=json.loads((P/'1830.json').read_text())['headRefOid'];baseline=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()
def blob(rev,path):return subprocess.check_output(['git','show',rev+':'+path],cwd=R)
pins=json.loads((pkg/'gate/PINS.json').read_text())['files'];rows=[]
for name,pin in pins.items():
 historical=blob(pin['commit'],name);assert hashlib.sha256(historical).hexdigest()==pin['sha256']
 existing=D/name
 if existing.exists():data=existing.read_bytes();source=head
 else:data=blob(baseline,name);source=baseline
 if name=='certificates/selected-result.json':data=blob(baseline,name);source=baseline
 else:assert data==historical,('current ordinary source differs',name)
 existing.parent.mkdir(parents=True,exist_ok=True);existing.write_bytes(data);rows.append(dict(path=name,source=source,sha256=hashlib.sha256(data).hexdigest(),historical_sha256=pin['sha256']))
subprocess.run(['git','init','-q',str(D)],check=True)
common=subprocess.check_output(['git','rev-parse','--path-format=absolute','--git-common-dir'],cwd=R,text=True).strip()
(D/'.git/objects/info/alternates').write_text(common+'/objects\n')
subprocess.run(['git','add','.'],cwd=D,check=True)
changed=subprocess.check_output(['git','diff','--name-only','a6578b3dfad3d0b3279b1b6db23940b0660f9e5f',head,'--','research/h6-compensation-network','research/h6-banked-breakeven','research/h6-independent-audit','.github/workflows/h6-compensation-network.yml'],cwd=R,text=True).splitlines()
old=json.loads(Path('/tmp/pr-efficient800/check-1830.json').read_text());receipt=dict(status='PASS',head=head,baseline=baseline,inputs=rows,changed_since_previous_review=changed,prior_replay={k:old[k] for k in ('head','commands','seconds','status','log_sha256','scope')},scope='Exact upstream pin authentication; current ordinary inputs; historical benchmark substitution only as declared by ci.py.')
(P/'provenance-1830-hydration.json').write_text(json.dumps(receipt,indent=2)+'\n');print('PASS hydrated',len(rows),'pins; changed',changed)
