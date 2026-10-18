from pathlib import Path
import json,subprocess,ast,importlib.util,hashlib
P=Path('/tmp/pr-efficient1800');R=Path('/tmp/integer-mult-efficient1100-20261015');D=P/'combined-2859'
paths=set(subprocess.check_output(['git','ls-tree','-r','--name-only','HEAD'],cwd=R,text=True).splitlines());proc=subprocess.Popen(['git','cat-file','--batch'],cwd=R,stdin=subprocess.PIPE,stdout=subprocess.PIPE);added={}
def put(rel):
 f=D/rel
 if f.exists():return f
 if rel not in paths:raise ValueError('Not on main: '+rel)
 proc.stdin.write(('HEAD:'+rel+'\n').encode());proc.stdin.flush();header=proc.stdout.readline().decode().split();assert len(header)==3 and header[1]=='blob',header;data=proc.stdout.read(int(header[2]));assert proc.stdout.read(1)==b'\n';f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(data);added[rel]=hashlib.sha256(data).hexdigest();return f
for path in paths:
 if path.startswith(('scripts/','.github/workflows/')):put(path)
seen=set();todo=['scripts/verify_frontier1094.py'];named=set()
while todo:
 name=todo.pop()
 if name in seen:continue
 seen.add(name)
 for node in ast.walk(ast.parse(put(name).read_bytes())):
  modules=[]
  if isinstance(node,ast.Import):modules=[a.name for a in node.names]
  elif isinstance(node,ast.ImportFrom) and node.module and not node.level:modules=[node.module]
  for mod in modules:
   rel='scripts/'+mod.split('.')[0]+'.py'
   if rel in paths:todo.append(rel)
  if isinstance(node,ast.Constant) and isinstance(node.value,str) and '/' in node.value:
   rel=node.value.rstrip('/')
   if rel in paths:
    put(rel);named.add(rel)
    if rel.startswith('scripts/') and rel.endswith('.py'):todo.append(rel)
records={'certificates/selected-result.json','certificates/checkpoints/frontier1042.json'}
for rel in named:
 if rel.startswith('certificates/') and rel.endswith('.json'):
  x=json.loads(put(rel).read_bytes())
  if isinstance(x,dict) and 'source_manifest' in x and 'proof_supplements' in x:records.add(rel)
for rel in records:
 record=json.loads(put(rel).read_bytes())
 for key in ['certificate','source_manifest','proof','review','validation']:put(record[key])
 for path in record['proof_supplements']:put(path)
 manifest=json.loads(put(record['source_manifest']).read_bytes());prefix='' if manifest.get('format')=='repository-packages-sha256-v1' else str(Path(record['source_manifest']).parent)+'/'
 for path in manifest['files']:put(prefix+path)
spec=importlib.util.spec_from_file_location('selected_ci',D/'scripts/check_selected_ci_inputs.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
for rel in g.live_pins(D)[2]:put(rel)
for rel in ['docs/research/pr-ledger.json','research/pr-reconciliation-20261012/starting-snapshot.json','research/single-intersection-spectrum-audit/RESULT.json','research/single-intersection-spectrum-audit/SOURCE.json','CONTRIBUTING.md','research/pair-assembly/frame/frame-certificate.json','certificates/joint-dual-kappa.json','certificates/skip-frame-kappa.json']:
 put(rel)
ledger=json.loads(put('docs/research/pr-ledger.json').read_bytes())
for rel in ledger['source_sha256']:put(rel)
proc.stdin.close();proc.wait()
(P/'provenance-2859-record-hydration.json').write_text(json.dumps(dict(baseline=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),added=added,scope='Exact current-main bytes for selected and historical record inventories, live pins, ledger sources and local source controls. Existing composed candidate files untouched.'),indent=2)+'\n');print('Hydrated',len(added),'files; records',len(records))
