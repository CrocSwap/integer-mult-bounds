"""Source-only research intake. Does not import or execute submitted code."""
from pathlib import Path
import ast,collections,hashlib,json,subprocess,time
P=Path('/tmp/pr-efficient1900');R=Path('/tmp/integer-mult-efficient1100-20261015')
NS=[2873,2875,2883,2908,2917,654,669,899,933,1175,1337,1487,1529,2309,2322,2363,2836,2839,2848,2849,2855,2857]
def git(*a):return subprocess.check_output(['git',*a],cwd=R)
base=git('rev-parse','HEAD').decode().strip()
current={x.split('\t',1)[1] for x in git('ls-tree','-r','--name-only',base).decode().splitlines() if '\t' in x} # populated below
current=set(git('ls-tree','-r','--name-only',base).decode().splitlines())
live_query='query {repository(owner:"CrocSwap",name:"integer-mult-bounds") {'+' '.join(f'p{n}:pullRequest(number:{n})'+'{number headRefOid state isDraft}' for n in NS)+'}}'
live=json.loads(subprocess.check_output(['gh','api','graphql','-f','query='+live_query]))['data']['repository']
seen=set();results=[]
for n in NS:
 pk=json.loads((P/'packets'/f'{n}.json').read_text());v=live['p'+str(n)]
 assert v['state']=='OPEN' and not v['isDraft'] and v['headRefOid']==pk['head'],v
 files={};errors=[];syntax=collections.Counter();rootpaths=set()
 for entry in pk['files']:
  name=entry['path'];f=entry['source'];path=Path(name)
  assert name.startswith('research/') and '..' not in path.parts and f and f['mode'] in ('100644','100755') and entry['baseline'] is None,(n,name)
  assert name not in current and name not in seen,(n,name,'overlap')
  seen.add(name);rootpaths.add('/'.join(path.parts[:2]))
  raw=git('cat-file','blob',f['oid']);files[name]=raw
  assert git('rev-parse',pk['head']+':'+name).decode().strip()==f['oid']
  try:
   if name.endswith('.py'):ast.parse(raw,filename=name);syntax['python']+=1
   if name.endswith('.json'):json.loads(raw);syntax['json']+=1
  except (SyntaxError,ValueError,UnicodeDecodeError) as e:errors.append(dict(path=name,check='syntax',error=str(e)))
 manifests=[]
 for root in sorted(rootpaths):
  name=root+'/MANIFEST.json'
  if name not in files:continue
  obj=json.loads(files[name]);checked=0;external=0
  if isinstance(obj,dict):
   for rel,digest in obj.items():
    if not isinstance(digest,str) or len(digest)!=64 or not all(c in '0123456789abcdef' for c in digest):continue
    assert not Path(rel).is_absolute() and '..' not in Path(rel).parts,(n,rel)
    key=root+'/'+rel
    if key not in files:external+=1;continue
    checked+=1
    if hashlib.sha256(files[key]).hexdigest()!=digest:errors.append(dict(path=key,check='package_manifest_sha256'))
  manifests.append(dict(path=name,local_pins_checked=checked,outside_changed_files=external))
 results.append(dict(number=n,head=pk['head'],status='archive_intake_pass' if not errors else 'intake_needs_resolution',paths=sorted(rootpaths),file_count=len(files),bytes=sum(map(len,files.values())),syntax=dict(syntax),manifests=manifests,errors=errors,files={k:dict(sha256=hashlib.sha256(v).hexdigest(),bytes=len(v)) for k,v in files.items()},scope='Exact original Git blobs and modes, new research-only paths, Python/JSON syntax, and available flat package-manifest pins. NO author code executed, dependency replay, mathematical review, full reproducibility or frontier validation.'))
 print(n,results[-1]['status'],len(files),'files',len(errors),'errors',flush=True)
receipt=dict(schema_version=1,baseline=base,observed_unix=time.time(),live=live,pull_requests=results,selected_result_sha256=hashlib.sha256(git('show',base+':certificates/selected-result.json')).hexdigest(),scope='Archive admission only. Stored PASS receipts and claims remain author-supplied, not independent replay evidence.')
(P/'check-archive-intake.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('TOTAL',len(results),'eligible',sum(x['status']=='archive_intake_pass' for x in results),'files',len(seen))
