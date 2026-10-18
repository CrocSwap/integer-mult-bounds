from pathlib import Path
import json,subprocess,hashlib
P=Path('/tmp/pr-efficient1800');R=Path('/tmp/integer-mult-efficient1100-20261015');D=P/'sources/2227';H=D/'research/complex-compensation-network';sha=lambda b:hashlib.sha256(b).hexdigest()
s=json.loads((H/'SOURCES.json').read_bytes());c=json.loads((H/'COMPARISON-SOURCES.json').read_bytes());checked=[]
for commit,items in [(s['base_commit'],s['files']),(c['upstream_commit'],[dict(path=v['upstream_path'],usage='input',git_blob=v['git_blob'],sha256=v['sha256']) for v in c['files'].values()])]:
 for row in items:
  obj=subprocess.check_output(['git','rev-parse',commit+':'+row['path']],cwd=R,text=True).strip();raw=subprocess.check_output(['git','cat-file','blob',obj],cwd=R);assert obj==row['git_blob'] and sha(raw)==row['sha256'],row
  result=dict(commit=commit,**row)
  if row['usage']=='input':
   current=subprocess.check_output(['git','show','HEAD:'+row['path']],cwd=R);assert current==raw,('Current input drift',row['path'])
   target=D/row['path'];target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(current);result['current_matches']=True
  checked.append(result)
assert set(json.loads((H/'VERIFY.json').read_bytes())['inputs'])=={x['path'] for x in checked if x['usage']=='input'}
(P/'provenance-2227-current-inputs.json').write_text(json.dumps(dict(status='passed',baseline=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),sources=checked,scope='Every declared current input equals the pinned historical commit/blob/SHA256; provenance-only entries independently authenticated too.'),indent=2)+'\n');print('Authenticated',len(checked),'source records')
