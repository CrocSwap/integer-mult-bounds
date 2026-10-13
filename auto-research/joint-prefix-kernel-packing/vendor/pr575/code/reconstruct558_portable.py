"""Content-portable dispatcher derived from PR558 code/reconstruct.py.
See proof/PORTABLE-BASELINE.json; every reconstruction and scalar stage retained.
Prepared with OpenAI Codex assistance. Apache-2.0. No optimizer or network.
"""
import argparse,subprocess,sys
from pathlib import Path
if not __debug__:raise SystemExit('Assertions required')
a=argparse.ArgumentParser();a.add_argument('--out',type=Path,required=True);a=a.parse_args();ROOT=Path(__file__).resolve().parents[1];P=ROOT/'vendor/pr558';v=P/'vendor/pr552';s=v/'complex-local/static44';g=s/'gk';a.out.mkdir(parents=True,exist_ok=False);O=a.out

def run(script,*args):subprocess.run([sys.executable,'-B',str(P/'code/run_portable.py'),str(script),*map(str,args)],check=True)
run(s/'build.py','--raw',s/'inputs/RAW504.json.gz','--base',s/'inputs/BASE535.json.gz','--old-recipe',s/'inputs/OLD-RECIPE.json','--recipe',s/'RECIPE.json','--gk-dir',g,'--out',O/'static44')
run(s/'audit_scalar.py',O/'static44/FULL-WORD.json.gz',O/'static44/SELECTION.json',O/'static44/SCALAR-AUDIT.json')
run(v/'complex-local/code/port_frames.py','--input',O/'static44/FULL-WORD.json.gz','--source',v/'complex-local/inputs/PR534-WORD.json.gz','--gk',g,'--out',O/'lifted')
run(v/'complex-local/code/apply_syndrome.py','--input',O/'lifted/FULL-WORD.json.gz','--gk',g,'--out',O/'syndrome')
run(v/'code/build_wave.py','--input',O/'syndrome/FULL-WORD.json.gz','--recipe',v/'inputs/WAVES.json','--gk',g,'--out',O/'wave')
run(v/'response/build_weighted_coset.py','--input',O/'wave/FULL-WORD.json.gz','--selection',v/'response/WEIGHTED-COSET-SELECTION.json','--gk-dir',g,'--out',O/'weighted')
run(ROOT/'code/promote_eight_portable.py','--input',O/'weighted/FULL-WORD.json.gz','--gk',g,'--recipe',P/'data/PROMOTION.json','--out',O/'promoted')
run(s/'audit_scalar.py',O/'promoted/FULL-WORD.json.gz',O/'static44/SELECTION.json',O/'promoted/STATIC44-SCALAR-AUDIT.json')
run(P/'code/audit_promoted_scalar.py',O/'promoted/FULL-WORD.json.gz',O/'static44/SELECTION.json',O/'promoted/PROMOTED8-SCALAR-AUDIT.json')
