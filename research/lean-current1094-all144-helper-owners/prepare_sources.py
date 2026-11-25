"""Materialize the exact 45 accepted source bodies. No fetch, Lean, or installation."""
import hashlib,json,os,pathlib,subprocess,sys
HERE=pathlib.Path(__file__).resolve().parent
if len(sys.argv)!=3:
 raise SystemExit('usage: python3 prepare_sources.py EXISTING_GIT_REPOSITORY ABSENT_OUTPUT_DIRECTORY')
repo=pathlib.Path(sys.argv[1]).resolve();out=pathlib.Path(sys.argv[2]).absolute()
if out.exists() or out.is_symlink():raise SystemExit('Output must be absent; preserve and diagnose prior output.')
manifest=json.loads((HERE/'SOURCE_MANIFEST.json').read_bytes())
def sha(b):return hashlib.sha256(b).hexdigest()
def blob(b):return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
prepared=[]
for row in manifest['modules']:
 if 'included_file' in row:
  raw=(HERE/row['included_file']).read_bytes();data=raw
 else:
  raw=subprocess.check_output(['git','--no-optional-locks','show',row['commit']+':'+row['path']],cwd=repo,env={**os.environ,'GIT_NO_LAZY_FETCH':'1','GIT_TERMINAL_PROMPT':'0'},timeout=15)
  assert len(raw)==row['raw_bytes'] and sha(raw)==row['raw_sha256'] and blob(raw)==row['git_blob'],row['module']
  change=row['replace'];data=raw
  if change:
   before=change['before'].encode();after=change['after'].encode()
   assert raw.count(before)==change['count']==1 and after not in raw
   data=raw.replace(before,after)
   assert data.count(after)==1 and data.replace(after,before)==raw
 assert len(data)==row['bytes'] and sha(data)==row['sha256'],row['module']
 prepared.append((row['module'],data))
# All input identities and inverses pass before creating any output.
out.mkdir(parents=False);(out/'sources').mkdir();(out/'objects').mkdir();(out/'logs').mkdir()
for module,data in prepared:
 p=out/'sources'/(module+'.lean')
 with p.open('xb') as f:f.write(data)
 assert p.read_bytes()==data
receipt={'status':'EXACT_SOURCES_PREPARED_NO_COMPILER','source_manifest_sha256':sha((HERE/'SOURCE_MANIFEST.json').read_bytes()),'modules':[{'module':n,'bytes':len(b),'sha256':sha(b)} for n,b in prepared],'no_fetch_or_runtime_execution':True}
with (out/'PREPARED.json').open('x') as f:json.dump(receipt,f,indent=2);f.write('\n')
print(json.dumps(receipt,indent=2))
