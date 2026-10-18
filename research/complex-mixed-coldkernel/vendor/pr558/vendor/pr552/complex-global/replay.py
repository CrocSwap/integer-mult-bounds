"""Complete changed-complex controller replay; stdlib only. Local provider is rebuilt separately."""
from pathlib import Path
import argparse,subprocess,sys
p=argparse.ArgumentParser();p.add_argument('--local',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();b=Path(__file__).resolve().parent
subprocess.run([sys.executable,'-B',str(b/'run_complex44.py'),str(b/'vendor531'),str(b/'vendor535'),str(a.local.resolve()),str(b/'SAT-OWNERS.json.gz'),str(b/'SAT534-PLAN.json'),str(b/'run_portable.py'),str(a.out.resolve())],check=True)
