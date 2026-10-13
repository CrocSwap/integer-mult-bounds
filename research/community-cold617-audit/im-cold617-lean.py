import pathlib,subprocess,json,hashlib,os,time,re,sys
root=pathlib.Path('/tmp/integer-mult-family588'); lean=pathlib.Path.home()/'.elan/toolchains/leanprover--lean4---v4.21.0/bin/lean'
libpath=subprocess.check_output(['lake','env','printenv','LEAN_PATH'],cwd=root/'research/hyperplane-end-lean',text=True).strip()
for n,name,dep,depdir in [(605,'lean-current588-native-moment',585,'lean-selected-rational-certificates'),(612,'lean-current-r420-boundary-interfaces',590,'lean-selected-bit-scalar-boundaries')]:
 pkg=pathlib.Path(f'/tmp/im-cold617-sources/pr{n}/research')/name;man=json.load(open(pkg/'MANIFEST.json'));out=pathlib.Path(f'/tmp/im-cold617-replay/lean{n}-macos');out.mkdir();records=[]
 for row in man['compile_order']:
  mod=row['module'];fn=row['file']; src=pkg/fn
  if not src.exists():
   head={585:'809915a264d4fbe1f7597cc13da3610dc4d52f15',590:'58690bdbb587f482569ba1bdf7bf61a5396b4768'}[dep]
   body=subprocess.check_output(['git','show',head+':research/'+depdir+'/'+fn],cwd=root)
  else:body=src.read_bytes()
  assert hashlib.sha256(body).hexdigest()==row['sha256'];(out/fn).write_bytes(body)
  assert not re.search(r'\b(sorry|admit|native_decide)\b',re.sub(r'/\-.*?\-/|--[^\n]*','',body.decode(),flags=re.S)),mod
  env=dict(os.environ,LEAN_PATH=str(out)+':'+libpath)
  cmd=[str(lean),'-o',str(out/(mod+'.olean')),str(out/fn)];start=time.time()
  print('RUN',n,mod,flush=True)
  with (out/(mod+'.log')).open('w') as f:
   try:p=subprocess.run(cmd,cwd=out,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=90);rc=p.returncode
   except subprocess.TimeoutExpired:rc=124
  log=(out/(mod+'.log')).read_text(); probes=[]
  for declaration,axs in re.findall(r"'([^']+)' depends on axioms: \[([^\]]*)\]",log,re.S):probes.append({'declaration':declaration,'axioms':re.findall(r'[\w.]+',axs)})
  for declaration in re.findall(r"'([^']+)' does not depend on any axioms",log):probes.append({'declaration':declaration,'axioms':[]})
  good=rc==0 and sorted(probes,key=lambda x:x['declaration'])==sorted(row['expected_probes'],key=lambda x:x['declaration'])
  records.append({'module':mod,'source_sha256':row['sha256'],'exit_code':rc,'seconds':time.time()-start,'probes_match':good,'probes':probes,'log_sha256':hashlib.sha256(log.encode()).hexdigest()})
  (out/'REVIEW.json').write_text(json.dumps({'pr':n,'mode':'Fresh macOS Lean 4.21 source build, not the submitted Linux retained-object checker','records':records},indent=2)+'\n')
  if not good:print('STOP',n,mod,log[-1000:],flush=True);break
  print('PASS',n,mod,flush=True)
