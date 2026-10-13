"""Rebuild the chosen complex word from primitive inputs and independently audit it."""
from pathlib import Path
import argparse,subprocess,sys,json,gzip,hashlib
if not __debug__:raise SystemExit('Assertions must remain enabled.')
p=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--vendor',type=Path,required=True);a=ap.parse_args()
out=a.out.resolve();assert not out.exists();out.mkdir(parents=True)
v=a.vendor.resolve();launcher=p/'code/run_portable.py'
def run(script,*args):
 subprocess.run([sys.executable,'-B',str(launcher),str(script),*map(str,args)],check=True)
s=p/'static44';g=s/'gk'
run(s/'build.py','--raw',s/'inputs/RAW504.json.gz','--base',s/'inputs/BASE535.json.gz','--old-recipe',s/'inputs/OLD-RECIPE.json','--recipe',s/'RECIPE.json','--gk-dir',g,'--out',out/'static44')
run(s/'audit_scalar.py',out/'static44/FULL-WORD.json.gz',out/'static44/SELECTION.json',out/'static44/SCALAR-AUDIT.json')
run(p/'code/port_frames.py','--input',out/'static44/FULL-WORD.json.gz','--source',p/'inputs/PR534-WORD.json.gz','--gk',g,'--out',out/'lifted')
run(p/'code/apply_syndrome.py','--input',out/'lifted/FULL-WORD.json.gz','--gk',g,'--out',out/'syndrome')
local=out/'local';base=p/'inputs/phase-baseline'
run(v/'code/audit_and_transport.py','--raw',out/'syndrome/FULL-WORD.json.gz','--routing',base/'CANONICAL-WORD.json.gz','--out',local)
run(v/'code/phases_delta.py','--local',local,'--baseline',base,'--compiler',v/'vendor/clifford')
run(v/'code/adapters_local.py',local/'CANONICAL-WORD.json.gz',local/'RESIDUAL-ADAPTERS.json',local/'WRAPPER-CHECKS.json')
run(v/'code/emit_local.py',local)
run(v/'code/audit_local.py',local)
actual=hashlib.sha256(gzip.decompress((local/'CANONICAL-WORD.json.gz').read_bytes())).hexdigest()
assert actual=='5d96dbd7eb01548edbeac7f3b8a9401ac14268f3ecea1de4a61e13953448cc7c',actual
print('PASS complete local reconstruction, all columns and controls, final canonical hash',actual)
