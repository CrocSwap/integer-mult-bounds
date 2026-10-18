from pathlib import Path
import subprocess,json,hashlib
P=Path('/tmp/pr-efficient1800');R=Path('/tmp/integer-mult-efficient1100-20261015');D=P/'sources/2219';base='05f7aad0f08992ee48ec2dd93e896d9a4567847d';pkg='research/p104-interleaved-search';new='research/p104-private-descent-reuse-seed915fa969'
def blob(ref):return subprocess.check_output(['git','show',ref],cwd=R)
def put(path,data):
 dst=D/path;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();dst.write_bytes(data)
files=subprocess.check_output(['git','ls-tree','-r','--name-only',base,'--',pkg],cwd=R,text=True).splitlines()
for path in files:put(path,blob(base+':'+path))
manifest=json.loads((D/pkg/'SOURCES.json').read_bytes())
for x in manifest['files']:
 data=blob(x['git_blob']);assert hashlib.sha256(data).hexdigest()==x['sha256'];assert blob(base+':'+x['path'])==data;put(x['path'],data)
task=json.loads((D/new/'TASK.json').read_bytes())
for name,digest in task['artifacts']['sha256'].items():assert hashlib.sha256((D/new/name).read_bytes()).hexdigest()==digest
subprocess.run(['git','apply','--check',str(D/new/'fanout-helper-reuse.patch')],cwd=D,check=True)
subprocess.run(['git','apply',str(D/new/'fanout-helper-reuse.patch')],cwd=D,check=True)
assert hashlib.sha256((D/pkg/'fanout.py').read_bytes()).hexdigest()==task['predecessor']['patched_source_sha256']
# All source code is pinned; no selected checkout changes or source downloading at runtime.
record={'number':2219,'head':json.load(open(P/'2219.json'))['headRefOid'],'predecessor':base,'predecessor_files':len(files),'hydrated_pinned_inputs':len(manifest['files']),'patched_source_sha256':task['predecessor']['patched_source_sha256'],'scope':'Exact predecessor minimal fixture plus original single-file patch and eight author contribution files. No altered checker predicates.'}
(P/'provenance-2219.json').write_text(json.dumps(record,indent=2)+'\n');print(record)
