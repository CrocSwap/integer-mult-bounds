"""Disposable source/package-boundary controls; not a mathematical replay."""
import argparse,hashlib,json,shutil,subprocess,sys,tempfile
from pathlib import Path
P=Path(__file__).resolve().parent

def duplicate(destination):
 shutil.copytree(P,destination)
 destination.chmod(0o755)
 for path in destination.rglob('*'):
  path.chmod(0o755 if path.is_dir() else 0o644)

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',type=Path);args=ap.parse_args()
 if args.out and args.out.exists():raise ValueError('output exists')
 rows=[]
 with tempfile.TemporaryDirectory(prefix='dirty cubic bindings ') as tmp:
  root=Path(tmp)
  mutations=['core','fixture','expected','source_pins','missing_source','extra_file','manifest_path','resigned_fixture']
  for name in mutations:
   case=root/name;duplicate(case)
   if name in ['core','fixture','expected','source_pins','resigned_fixture']:
    target={'core':'core.py','fixture':'vendor/628/FACTORS.json','expected':'EXPECTED.json',
            'source_pins':'SOURCES.json','resigned_fixture':'vendor/628/FACTORS.json'}[name]
    file=case/target;file.write_bytes(file.read_bytes()+b'\n')
    if name=='resigned_fixture':
     manifest=json.loads((case/'MANIFEST.json').read_text())
     manifest['files'][target]=hashlib.sha256(file.read_bytes()).hexdigest()
     (case/'MANIFEST.json').write_text(json.dumps(manifest))
   elif name=='missing_source':(case/'vendor/628/dirty.py').unlink()
   elif name=='extra_file':(case/'unbound-proof-input.txt').write_text('unexpected')
   else:
    manifest=json.loads((case/'MANIFEST.json').read_text());manifest['files']['../escape']='0'*64
    (case/'MANIFEST.json').write_text(json.dumps(manifest))
   p=subprocess.run([sys.executable,'-I','-O','-B',str(case/'verify.py'),'--bindings-only'],capture_output=True,text=True,timeout=30)
   if not p.returncode:raise ValueError('corruption accepted: '+name)
   rows.append(dict(control=name,rejected=p.stderr.strip().splitlines()[-1]))
  case=root/'read only relocated package';duplicate(case)
  files=list(case.rglob('*'))
  try:
   for path in files:
    path.chmod(0o555 if path.is_dir() else 0o444)
   case.chmod(0o555)
   p=subprocess.run([sys.executable,'-I','-O','-B',str(case/'verify.py'),'--bindings-only'],cwd=root,capture_output=True,text=True,timeout=30)
   if p.returncode or 'PASS_PACKAGE_BINDINGS' not in p.stdout:raise ValueError('relocated binding replay failed: '+p.stderr)
  finally:
   case.chmod(0o755)
   for path in files:
    path.chmod(0o755 if path.is_dir() else 0o644)
 report=dict(status='PASS_PACKAGE_BINDINGS',rejected=rows,read_only_relocation=True,
             scope='Integrity and source pin checks only; mathematical replay is verify.py without --bindings-only.')
 if args.out:
  with args.out.open('x') as f:f.write(json.dumps(report,indent=2)+'\n')
 print('PASS_PACKAGE_BINDINGS controls='+str(len(rows))+' readonly_relocation=1')

if __name__=='__main__':main()
