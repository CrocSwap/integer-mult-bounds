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
run(p.parent/'code/build_wave.py','--input',out/'syndrome/FULL-WORD.json.gz','--recipe',p.parent/'inputs/WAVES.json','--gk',g,'--out',out/'wave')
run(p.parent/'response/build_weighted_coset.py','--input',out/'wave/FULL-WORD.json.gz','--selection',p.parent/'response/WEIGHTED-COSET-SELECTION.json','--gk-dir',g,'--out',out/'weighted')
run(p.parent/'epoch/build_epoch14.py','--input',out/'weighted/FULL-WORD.json.gz','--gk-dir',g,'--out',out/'epoch')
local=out/'local';base=p/'inputs/phase-baseline'
run(v/'code/audit_and_transport.py','--raw',out/'epoch/FULL-WORD.json.gz','--routing',base/'CANONICAL-WORD.json.gz','--out',local)
run(v/'code/phases_delta.py','--local',local,'--baseline',base,'--compiler',v/'vendor/clifford')
run(v/'code/adapters_local.py',local/'CANONICAL-WORD.json.gz',local/'RESIDUAL-ADAPTERS.json',local/'WRAPPER-CHECKS.json')
run(v/'code/emit_local.py',local)
run(v/'code/audit_local.py',local)
actual=hashlib.sha256(gzip.decompress((local/'CANONICAL-WORD.json.gz').read_bytes())).hexdigest()
assert actual=='970a0761d1a707ef2b2dc263b8fcc1800b401f35ae022094c6b98a007bfcf42d',actual
print('PASS complete local reconstruction, all columns and controls, final canonical hash',actual)
