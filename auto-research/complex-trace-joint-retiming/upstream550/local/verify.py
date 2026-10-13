"""Offline dependency-closed local construction, arbitrary-dirt audit and pricing."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--work',type=Path,required=True);a=ap.parse_args()
if not __debug__:raise SystemExit('Assertions must remain enabled.')
for path,digest in json.loads((ROOT/'MANIFEST.json').read_text()).items():
 assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest,path
out=a.work.resolve();out.mkdir(exist_ok=False)
def run(script,*args):subprocess.run([sys.executable,'-B',str(ROOT/script),*map(str,args)],check=True)
run('construct.py','--input',ROOT/'inputs/PR548-FULL-WORD.json.gz','--gk',ROOT/'vendor/gk','--out',out/'candidate')
run('audit_scalar.py',out/'candidate/FULL-WORD.json.gz',ROOT/'inputs/STATIC44-SELECTION.json',out/'SCALAR-AUDIT.json')
run('price.py','--word',out/'candidate/FULL-WORD.json.gz','--out',out/'PRICE.json')
print('PASS_FROZEN_STEINBERG_LOCAL_REPLAY_AND_EXACT_PRICE')
