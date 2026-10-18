"""NewBArch's unchanged run_controls.py on the X54 joint-entrance recipe: C0, recipe, and four mutants globally and for X=54 (10 outcomes)."""
import argparse,json,subprocess,sys
from pathlib import Path
P=Path(__file__).resolve().parent
def main():
 assert __debug__
 ap=argparse.ArgumentParser();ap.add_argument('--base',type=Path,required=True);ap.add_argument('--audit',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();assert not a.out.exists()
 subprocess.run([sys.executable,'-B',str(P/'vendor/barch/run_controls.py'),str(a.base),str(P/'RECIPE-X54-joint.json'),str(a.audit),str(a.out)],check=True)
 res=json.loads((a.out/'controls.json').read_text());assert len(res)==10 and all(x['ok'] for x in res.values());print('PASS_X54_CONTROLS',len(res))
if __name__=='__main__':main()
