import json,pathlib,subprocess,concurrent.futures,re,io,tarfile,ctypes,hashlib,threading,os,bisect,sys
cache={};lock=threading.Lock();lib=ctypes.CDLL(None,use_errno=True)
clone=lib.clonefile;clone.argtypes=[ctypes.c_char_p,ctypes.c_char_p,ctypes.c_int];clone.restype=ctypes.c_int
P=pathlib.Path('/tmp/pr-efficient1400');R=pathlib.Path('/tmp/integer-mult-efficient1100-20261015')
objects=str((R/subprocess.check_output(['git','rev-parse','--git-path','objects'],cwd=R,text=True).strip()).resolve())
def setup(row):
 if 'command' not in row:return
 n=row['number']
 if (P/f'setup-{n}.json').exists():return
 root=P/'sources'/str(n);head=json.load(open(P/f'{n}.json'))['headRefOid']
 tree={};oids={};modes={}
 for line in subprocess.check_output(['git','ls-tree','-rl',head],cwd=R,text=True).splitlines():
  info,path=line.split('\t',1);parts=info.split()
  if parts[1]=='blob':tree[path]=int(parts[3]);oids[path]=parts[2];modes[path]=int(parts[0],8)
 # Restart-safe validation of partially hydrated fixtures before using them.
 for f in root.rglob('*'):
  if not f.is_file() or '.git' in f.parts:continue
  path=str(f.relative_to(root))
  if path not in oids:continue
  b=f.read_bytes()
  if hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()!=oids[path]:
   f.write_bytes(subprocess.check_output(['git','show',head+':'+path],cwd=R))
 keys=sorted(tree);prefix_cache={}
 def descendants(prefix):
  if prefix not in prefix_cache:
   lo=bisect.bisect_left(keys,prefix);hi=bisect.bisect_left(keys,prefix+'\U0010ffff')
   prefix_cache[prefix]=keys[lo:hi]
  return prefix_cache[prefix]
 changed_paths={x['path'] for x in json.load(open(P/'packets'/f'{n}.json'))['files']}
 provided=[];seen=set()
 def restore(paths):
  paths=[p for p in paths if p in tree and not(root/p).exists()]
  pending=[]
  for path in paths:
   target=root/path;source=cache.get(oids[path]);copied=False
   if source and source.exists():
    data=source.read_bytes();digest=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
    if digest==oids[path]:
     target.parent.mkdir(parents=True,exist_ok=True)
     copied=clone(os.fsencode(source),os.fsencode(target),0)==0
     if copied:target.chmod(0o755 if modes[path]&0o111 else 0o644);provided.append(path)
   if not copied:pending.append(path)
  for i in range(0,len(pending),200):
   chunk=pending[i:i+200]
   if not chunk:continue
   data=subprocess.check_output(['git','archive',head,*chunk],cwd=R)
   with tarfile.open(fileobj=io.BytesIO(data)) as tar:tar.extractall(root,filter='data')
   provided.extend(chunk)
   with lock:
    for path in chunk:cache.setdefault(oids[path],root/path)
 restore([p for p in tree if p.startswith('scripts/') or p in ['CONTRIBUTING.md','AGENTS.md','README.md','LICENSE','NOTICE','Makefile','certificates/selected-result.json'] or (any(f['path'].startswith(('tests/','scripts/','.github/')) for f in json.load(open(P/'packets'/f'{n}.json'))['files']) and (p.startswith('tests/') or p.startswith('.github/workflows/')))])
 # Command packages are dependencies even for documentation-only submissions.
 command_files={arg for cmd in row.get('commands',[]) for arg in cmd if isinstance(arg,str) and arg.endswith('.py') and arg in tree} | {rel for rel in changed_paths if rel.endswith('.py') and rel in tree}
 command_paths=set(command_files)
 for rel in command_files:
  if rel.startswith('research/'):
   sub=descendants(str(pathlib.PurePosixPath(rel).parent)+'/')
   if len(sub)<800 and sum(tree[x] for x in sub)<30000000:command_paths.update(sub)
 restore(sorted(command_paths))
 # Manifest paths and literal package references, iterated through dependencies.
 for round in range(5):
  refs=set()
  for f in list(root.rglob('*')):
   if not f.is_file() or '.git' in f.parts or f in seen or f.suffix not in ('.py','.json','.toml','.sh') or f.stat().st_size>1500000:continue
   seen.add(f)
   if str(f.relative_to(root)).startswith(('scripts/','docs/','certificates/')) and str(f.relative_to(root)) not in changed_paths:continue
   try:s=f.read_text()
   except UnicodeError:continue
   refs.update(re.findall(r'(?:research|scripts|upstream|tests|notes|docs|certificates)/[A-Za-z0-9_./+\-]+',s))
  want=set()
  for ref in refs:
   ref=ref.rstrip('./')
   if ref in tree:
    want.add(ref)
    if ref.startswith('research/') and ref.endswith('.py'):
     sub=descendants(str(pathlib.PurePosixPath(ref).parent)+'/')
     if len(sub)<150 and sum(tree[p]for p in sub)<10000000:want.update(sub)
   elif ref.count('/')>=1:
    sub=descendants(ref+'/')
    if len(sub)<800 and sum(tree[p] for p in sub)<30000000:want.update(sub)
  before=len(provided);restore(sorted(want))
  if len(provided)==before:break
 subprocess.run(['git','init','-q',str(root)],check=True)
 (root/'.git/objects/info/alternates').write_text(objects+'\n');(root/'.git/HEAD').write_text(head+'\n')
 (P/f'setup-{n}.json').write_text(json.dumps(dict(provided=provided,head=head),indent=2))
 print('hydrated',n,len(provided),flush=True)
# Existing fixture files are only clone sources when their Git blob hash matches.
old=pathlib.Path('/tmp/pr-efficient300/sources/1193');head=json.load(open('/tmp/pr-efficient300/1193.json'))['headRefOid']
for line in subprocess.check_output(['git','ls-tree','-r',head],cwd=R,text=True).splitlines():
 info,path=line.split('\t',1);parts=info.split();f=old/path
 if parts[1]=='blob' and f.is_file():cache.setdefault(parts[2],f)
wanted=set(map(int,sys.argv[1:]))
rows=[r for r in json.load(open(P/'plan.json')) if not wanted or r['number'] in wanted]
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(setup,rows))
