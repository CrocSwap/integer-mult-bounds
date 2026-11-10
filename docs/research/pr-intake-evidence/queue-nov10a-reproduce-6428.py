import hashlib,json,pathlib,subprocess,tempfile,sys
D=pathlib.Path(tempfile.mkdtemp(prefix='pr6428-review-'));src=D/'6428-source';src.mkdir(exist_ok=True)
head='40591325403a9897ca95f642345742d17b1bd2a0'
for name,ref in [('check_pinned_edits.py',head),('research_package.py','7c49fe32c55de02c2c873655c804b16e4c3fef0a')]:
 (src/name).write_bytes(subprocess.check_output(['git','show',(ref+':research/pinned-edit-read-reuse/optimized.py') if name=='check_pinned_edits.py' else ref+':scripts/'+name]))
rows=[]
for case in ('directory','deletion'):
 with tempfile.TemporaryDirectory(prefix='pr6357-') as tmp:
  root=pathlib.Path(tmp)
  def git(*a):return subprocess.check_output(['git','-C',tmp,*a],stderr=subprocess.DEVNULL).decode().strip()
  git('init');git('config','user.email','review@example.invalid');git('config','user.name','Intake fixture')
  (root/'research').mkdir();(root/'research/target').write_bytes(b'old');digest=hashlib.sha256(b'old').hexdigest()
  for n in ('a-pin','z-pin'):(root/n).write_text(digest+'\n')
  git('add','.');git('commit','-m','base');base=git('rev-parse','HEAD')
  (root/'research/target').write_bytes(b'new');(root/'a-pin').unlink()
  if case=='directory':(root/'a-pin').mkdir();(root/'a-pin/child').write_text('child')
  git('add','.');git('commit','-m','changed')
  for flags in ([],['-O']):
   proc=subprocess.run([sys.executable,*flags,'-B',str(src/'check_pinned_edits.py'),'--root',tmp,'--base',base,'--json'],capture_output=True,text=True,timeout=30)
   row=dict(case=case,optimized=bool(flags),returncode=proc.returncode,stdout=proc.stdout,stderr=proc.stderr);rows.append(row)
   d=json.loads(proc.stdout);assert (proc.returncode,d['frozen_stale'])==(1,1),row
out=dict(source_head=head,python=sys.version,timeout_seconds_per_command=30,scope='Four tiny isolated Git CLI fixtures only; no scientific replay.',rows=rows)
(D/'6428-reproduction.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
