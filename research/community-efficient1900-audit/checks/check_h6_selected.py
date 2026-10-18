from pathlib import Path
import json,subprocess,hashlib,tarfile,io,time
P=Path('/tmp/pr-efficient1900');R=Path('/tmp/integer-mult-efficient1100-20261015');s=json.loads((R/'certificates/selected-result.json').read_text());m=json.loads(subprocess.check_output(['git','show','HEAD:'+s['source_manifest']],cwd=R));names=set(m['files'])|set(s['proof_supplements'])|{s[k] for k in ('source_manifest','certificate','proof','review','validation')};missing=sorted(n for n in names if not (R/n).exists());raw=subprocess.check_output(['git','archive','HEAD','--',*missing],cwd=R)
with tarfile.open(fileobj=io.BytesIO(raw)) as ar:
 for f in ar:
  if f.isdir():continue
  assert f.isfile() and f.name in names and not (R/f.name).exists()
  q=R/f.name;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(ar.extractfile(f).read());q.chmod(f.mode)
start=time.monotonic();cmd=['python3','-I','-B','scripts/verify_selected_result.py'];a=subprocess.run(cmd,cwd=R,capture_output=True,text=True);(P/'check-1830-selected.log').write_text(a.stdout+a.stderr);d=dict(status='passed' if a.returncode==0 else 'failed',exit_code=a.returncode,argv=cmd,seconds=time.monotonic()-start,head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),hydrated_missing_tracked_files=missing,log_sha256=hashlib.sha256((P/'check-1830-selected.log').read_bytes()).hexdigest(),setup_note='Initial check stopped because sparse worktree omitted ASSEMBLY.json. Hydrated only absent tracked HEAD bytes for declared selected inputs; no source edits or Lean execution.',scope='Selected record/source integrity, not construction replay.');(P/'check-1830-selected.json').write_text(json.dumps(d,indent=2)+'\n');print(a.stdout+a.stderr);a.check_returncode()
