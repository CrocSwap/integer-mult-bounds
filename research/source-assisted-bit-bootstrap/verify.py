#!/usr/bin/env python3
"""Verify immutable source pins and arithmetic; --full regenerates and audits the literal BIT word."""
if not __debug__: raise RuntimeError('Do not run exact verification with -O')
import argparse,hashlib,json,os,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
ap=argparse.ArgumentParser();ap.add_argument('--full',action='store_true');ap.add_argument('--output-dir',type=Path,default=ROOT/'build/source-assisted-bit-bootstrap');a=ap.parse_args()
manifest=json.loads((HERE/'SOURCE.json').read_text());count=0
for section,base in [('package_files',HERE),('repository_files',ROOT)]:
 for name,expected in manifest[section].items():
  assert hashlib.sha256((base/name).read_bytes()).hexdigest()==expected,('Source hash mismatch',section,name);count+=1
print(f'PASS {count} immutable source pins',flush=True)
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
def run(script,*args):subprocess.run([sys.executable,'-B',str(HERE/script),*map(str,args)],cwd=ROOT,env=env,check=True)
run('certificate.py')
if a.full:
 a.output_dir.mkdir(parents=True,exist_ok=True)
 run('emit_word.py','--output-dir',a.output_dir)
 run('prime_coverage.py','--word',a.output_dir/'emitted-word.json','--output',a.output_dir/'prime-coverage.json')
 run('verify_emitted.py','--output-dir',a.output_dir)
 run('scalar_cost.py','--output-dir',a.output_dir)
 run('audit.py','--word',a.output_dir/'emitted-word.json','--output',a.output_dir/'independent-all-columns.json')
 for name in ['emitted-physical.json','scalar-cost.json','independent-all-columns.json']:
  regenerated=json.loads((a.output_dir/name).read_text());frozen=json.loads((HERE/name).read_text())
  if name=='independent-all-columns.json':
   # Keep both raw timing receipts; elapsed wall time is not semantic evidence.
   regenerated.pop('elapsed_seconds',None);frozen.pop('elapsed_seconds',None)
  assert regenerated==frozen,('Regenerated artifact differs',name)
 print('PASS literal emitted BIT word, conservative geometry, paid histogram, scalar count, all-column forward/reflection and mutation controls',flush=True)
