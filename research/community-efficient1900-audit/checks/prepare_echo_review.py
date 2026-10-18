from pathlib import Path
import json,subprocess,hashlib
P=Path('/tmp/pr-efficient1900');R=Path('/tmp/integer-mult-efficient1100-20261015');D=P/'sources/2464';pkg=D/'research/z4-typed-echo-supplier-instance';s=json.loads((pkg/'SOURCES.json').read_text());rows=[]
for x in s['files']:
 name=x['path'];old=subprocess.check_output(['git','show',s['base_commit']+':'+name],cwd=R);assert hashlib.sha256(old).hexdigest()==x['sha256'];oid=subprocess.check_output(['git','rev-parse',s['base_commit']+':'+name],cwd=R,text=True).strip();assert oid==x['git_blob']
 data=subprocess.check_output(['git','show','HEAD:'+name],cwd=R);livehash=hashlib.sha256(data).hexdigest()
 if x['usage']=='input':assert data==old,('runtime drift',name)
 q=D/name;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(data);rows.append(dict(path=name,usage=x['usage'],historical_blob=oid,historical_sha256=x['sha256'],current_sha256=livehash))
name='scripts/research_package.py';q=D/name;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(subprocess.check_output(['git','show','HEAD:'+name],cwd=R))
subprocess.run(['git','init','-q',str(D)],check=True);common=subprocess.check_output(['git','rev-parse','--path-format=absolute','--git-common-dir'],cwd=R,text=True).strip();(D/'.git/objects/info/alternates').write_text(common+'/objects\n');subprocess.run(['git','add','.'],cwd=D,check=True)
head=json.loads((P/'2464.json').read_text())['headRefOid'];old=json.loads(subprocess.check_output(['git','show','HEAD:research/community-efficient1400-audit/packets/2464.json'],cwd=R))['head'];delta=subprocess.check_output(['git','diff','--stat',old,head,'--','research/z4-typed-echo-supplier-instance'],cwd=R,text=True)
(P/'provenance-2464-metadata.json').write_text(json.dumps(dict(status='PASS',head=head,base=s['base_commit'],inputs=rows,previous_head=old,delta=delta),indent=2)+'\n');print(delta)
