"""Standalone exact local-only static44 reconstruction and scalar audit."""
from pathlib import Path
import argparse,subprocess,sys
if not __debug__:raise SystemExit('Assertions must remain enabled.')
p=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();assert not a.out.exists()
subprocess.run([sys.executable,'-B',str(p/'build.py'),'--raw',str(p/'inputs/RAW504.json.gz'),'--base',str(p/'inputs/BASE535.json.gz'),'--old-recipe',str(p/'inputs/OLD-RECIPE.json'),'--recipe',str(p/'RECIPE.json'),'--gk-dir',str(p/'gk'),'--out',str(a.out)],check=True)
subprocess.run([sys.executable,'-B',str(p/'audit_scalar.py'),str(a.out/'FULL-WORD.json.gz'),str(a.out/'SELECTION.json'),str(a.out/'SCALAR-AUDIT.json')],check=True)
print('PASS standalone local-only appendix')
