import pathlib,json,subprocess,os,time,hashlib,platform,signal
P=pathlib.Path('/tmp/pr-efficient800');R=pathlib.Path('/tmp/integer-mult-efficient600-20261014');D=P/'combined-tooling';PY='/tmp/pr-efficient200-venv/bin/python'
base=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()
if not D.exists():subprocess.run(['cp','-cR',str(P/'sources/1793'),str(D)],check=True)
for n in [1834,1852]:
 root=P/'sources'/str(n)
 for f in root.rglob('*'):
  if f.is_file() and '.git' not in f.relative_to(root).parts and '__pycache__'not in f.parts:
   dst=D/f.relative_to(root)
   if not dst.exists():dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(f.read_bytes())
# Bind existing tracked dependencies to current integration tree, then overlay only reviewed PR deltas.
tree={}
for line in subprocess.check_output(['git','ls-tree','-r',base],cwd=R,text=True).splitlines():
 info,path=line.split('\t',1);tree[path]=info.split()[2]
bound=[]
for f in D.rglob('*'):
 if f.is_file() and '.git'not in f.relative_to(D).parts and '__pycache__'not in f.parts:
  rel=str(f.relative_to(D))
  if rel in tree:bound.append((f,tree[rel]))
for start in range(0,len(bound),64):
 batch=bound[start:start+64]
 data=subprocess.check_output(['git','cat-file','--batch'],input=('\n'.join(oid for _,oid in batch)+'\n').encode(),cwd=R)
 pos=0
 for f,oid in batch:
  end=data.index(b'\n',pos);header=data[pos:end].split();assert header[0].decode()==oid and header[1]==b'blob';size=int(header[2]);pos=end+1;f.write_bytes(data[pos:pos+size]);pos+=size+1
 assert pos==len(data)
for n in [1793,1834,1852]:
 pk=json.load(open(P/'packets'/f'{n}.json'))
 for row in pk['files']:
  assert row['source'];dst=D/row['path'];dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(subprocess.check_output(['git','cat-file','blob',row['source']['oid']],cwd=R))
cmds=[[PY,'-B','-m','unittest','discover','-s','tests','-p',f]for f in ['test_inplace_side.py','test_inplace_side_performance.py','test_research_current_status.py','test_isolated_test_runner.py']]
inputs={str(f.relative_to(D)):hashlib.sha256(f.read_bytes()).hexdigest()for f in D.rglob('*')if f.is_file()and '.git'not in f.relative_to(D).parts and '__pycache__'not in f.parts};codes=[];start=time.time();status='passed';log=P/'combined-tooling.log';env=os.environ.copy();env.pop('PYTHONOPTIMIZE',None);env['PYTHONDONTWRITEBYTECODE']='1'
with log.open('w')as out:
 for cmd in cmds:
  out.write(repr(cmd)+'\n');out.flush();q=subprocess.Popen(cmd,cwd=D,env=env,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
  try:code=q.wait(timeout=600)
  except subprocess.TimeoutExpired:os.killpg(q.pid,signal.SIGTERM);q.wait();code=None
  codes.append(code)
  if code!=0:status='failed';break
receipt=dict(status=status,base=base,heads={str(n):json.load(open(P/f'{n}.json'))['headRefOid']for n in[1793,1834,1852]},commands=cmds,seconds=round(time.time()-start,3),exit_codes=codes,input_sha256=inputs,log_sha256=hashlib.sha256(log.read_bytes()).hexdigest(),platform=platform.platform(),scope='Combined current-main dependencies plus reviewed1793/1834/1852 changes; targeted runtime-equivalence, source-certificate, locale and process-isolation tests.')
(P/'combined-tooling.json').write_text(json.dumps(receipt,indent=2)+'\n');print(status,codes,flush=True)
