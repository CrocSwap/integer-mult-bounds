#!/usr/bin/env python3
"""Offline finite certificate replay. Python3.11+, numpy2.3.5, scipy1.17.0."""
from pathlib import Path
import argparse,hashlib,json,io,zipfile,tempfile,subprocess,shutil,sys
HERE=Path(__file__).resolve().parent
sys.dont_write_bytecode=True
if hasattr(sys,'set_int_max_str_digits'):sys.set_int_max_str_digits(0)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def pins():
 m=json.loads((HERE/'FILES.json').read_text())['files'];actual={p.relative_to(HERE).as_posix():sha(p) for p in HERE.rglob('*') if p.is_file() and p.name!='FILES.json'};assert actual==m,'Missing, changed, or unpinned upload file';return actual
assert not sys.flags.optimize
ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--temp-root',type=Path,help='Optional spacious scratch drive for extraction');args=ap.parse_args();before=pins();baseline=json.loads((HERE/'BASELINE.json').read_text());parts=[]
for entry in baseline['parts']:
 p=HERE/entry['file'];assert p.stat().st_size==entry['bytes'] and sha(p)==entry['sha256'];parts.append(p.read_bytes())
blob=b''.join(parts);assert hashlib.sha256(blob).hexdigest()==baseline['archive_sha256']
with tempfile.TemporaryDirectory(prefix='crossover-pr200-',dir=args.temp_root) as tmp:
 root=Path(tmp)/'source';root.mkdir()
 with zipfile.ZipFile(io.BytesIO(blob)) as z:
  for entry in z.infolist():assert (root/entry.filename).resolve().is_relative_to(root.resolve()),'Unsafe archive entry'
  z.extractall(root)
 package=root/'research/coordinated-crossover-pr200';package.mkdir()
 skip={x['file'] for x in baseline['parts']}
 for p in HERE.rglob('*'):
  if p.is_file() and p.name not in skip:
   target=package/p.relative_to(HERE);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
 result=subprocess.run([sys.executable,'-B',str(package/'verify_inner.py')],text=True)
 assert result.returncode==0,'Full finite replay failed'
assert pins()==before,'Upload files changed during replay'
print('PASS immutable offline package; no network or git required')