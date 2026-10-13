#!/usr/bin/env python3
"""Reproduce the complete conditional witness offline from immutable source parts."""
from pathlib import Path
from hashlib import sha256
import argparse,io,json,shutil,subprocess,sys,tempfile,zipfile
HERE=Path(__file__).resolve().parent
sys.dont_write_bytecode=True
if hasattr(sys,'set_int_max_str_digits'):sys.set_int_max_str_digits(0)
def digest(p):return sha256(p.read_bytes()).hexdigest()
def pins():
 manifest=json.loads((HERE/'FILES.json').read_text())
 inventory={p.relative_to(HERE).as_posix() for p in HERE.rglob('*') if p.is_file() and p.name!='FILES.json'}
 assert inventory==set(manifest['files']),'Unpinned or missing upload file'
 actual={n:digest(HERE/n) for n in manifest['files']}
 assert actual==manifest['files'],'Upload source bytes changed'
 return actual
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--write',action='store_true',help='Authoring only: generate the derived certificate');args=parser.parse_args()
 assert not sys.flags.optimize,'Assertions must remain enabled'
 before=None if args.write else pins()
 baseline=json.loads((HERE/'BASELINE.json').read_text());chunks=[]
 for p in baseline['parts']:
  block=(HERE/p['file']).read_bytes();assert len(block)==p['bytes'] and sha256(block).hexdigest()==p['sha256'];chunks.append(block)
 blob=b''.join(chunks);assert sha256(blob).hexdigest()==baseline['archive_sha256']
 with tempfile.TemporaryDirectory(prefix='coordinated-frames-offline-') as tmp:
  root=Path(tmp)/'source';root.mkdir()
  with zipfile.ZipFile(io.BytesIO(blob)) as z:
   for entry in z.infolist():
    target=(root/entry.filename).resolve();assert target.is_relative_to(root.resolve()),'Unsafe archive path'
   z.extractall(root)
  package=root/'research'/'coordinated-frames-and-entrance-banks';package.mkdir(parents=True)
  for p in HERE.rglob('*'):
   if p.is_file() and p.name!='baseline-pr179.zip' and p.name not in {entry['file'] for entry in baseline['parts']} and not p.name.startswith('baseline-pr179.part'):
    rel=p.relative_to(HERE);dest=package/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
  command=[sys.executable,'-B',str(package/'verify_inner.py')]
  if args.write:command.append('--write')
  result=subprocess.run(command,text=True,capture_output=True)
  print(result.stderr,file=sys.stderr,end='');print(result.stdout,end='')
  if result.returncode:raise RuntimeError('Complete offline verification failed')
  if args.write:shutil.copyfile(package/'certificate.json',HERE/'certificate.json')
 if not args.write:assert pins()==before,'Upload source changed during verification'
 print('PASS offline immutable archive, source closure and complete derived certificate')
if __name__=='__main__':main()
