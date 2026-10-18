from pathlib import Path
import subprocess,json,ast,importlib.util
R=Path('/tmp/integer-mult-efficient1100-20261015');P=Path('/tmp/pr-efficient2600');tree={}
for rec in subprocess.check_output(['git','ls-tree','-r','-z','HEAD'],cwd=R).split(b'\0'):
 if rec:
  meta,name=rec.split(b'\t',1);mode,kind,oid=meta.decode().split()
  if kind=='blob':tree[name.decode()]=(mode,oid)
reader=subprocess.Popen(['git','cat-file','--batch'],cwd=R,stdin=subprocess.PIPE,stdout=subprocess.PIPE);seen=set();made=[];total=0
spec=importlib.util.spec_from_file_location('guard',R/'scripts/check_selected_ci_inputs.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
record=json.loads((R/'certificates/selected-result.json').read_text());_,driver=g.driver(record,R)
todo=[driver,'certificates/selected-result.json','scripts/verify_selected_result.py']
def strings(x):
 if isinstance(x,str):yield x
 elif isinstance(x,list):
  for v in x:yield from strings(v)
 elif isinstance(x,dict):
  for k,v in x.items():yield k;yield from strings(v)
while todo:
 name=todo.pop()
 if name in seen or name not in tree:continue
 seen.add(name);assert len(seen)<10000
 mode,oid=tree[name];reader.stdin.write((oid+'\n').encode());reader.stdin.flush();hdr=reader.stdout.readline().split();size=int(hdr[2]);raw=reader.stdout.read(size);assert reader.stdout.read(1)==b'\n';path=R/name
 if not path.exists():
  total+=size;assert total<128*1024*1024;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw);path.chmod(int(mode,8)&0o777);made.append(name)
 if name.endswith('.json'):
  obj=json.loads(raw,parse_int=str);todo.extend(v for v in strings(obj) if v in tree)
  if isinstance(obj,dict) and 'package_roots' in obj:
   for root in obj['package_roots']:
    todo.extend(root+'/'+n for n in g.PIN_FILES if root+'/'+n in tree)
 elif name.startswith('scripts/') and name.endswith('.py'):
  for node in ast.walk(ast.parse(raw)):
   if isinstance(node,ast.Constant) and isinstance(node.value,str) and node.value in tree:todo.append(node.value)
   modules=[a.name for a in node.names] if isinstance(node,ast.Import) else [node.module] if isinstance(node,ast.ImportFrom) and node.module else []
   todo.extend('scripts/'+m.split('.')[0]+'.py' for m in modules)
reader.stdin.close();assert reader.wait()==0
(P/'selected-hydration.json').write_text(json.dumps(dict(head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),missing_head_files_restored=made,bytes=total,scope='Materialize missing tracked HEAD inputs only; no existing file overwritten or scientific code executed.'),indent=2)+'\n');print('Restored',len(made),'missing HEAD inputs;',total,'bytes')
