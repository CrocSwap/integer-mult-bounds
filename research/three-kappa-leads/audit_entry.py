"""Explicit isolated native-frame owner audit entry."""
from pathlib import Path
import os,subprocess,sys
P=Path(__file__).resolve().parent
if len(sys.argv)!=4:raise SystemExit('allocation native-cache output required')
env=dict(os.environ,OWNER_SOURCE_REPO=str(P.parents[1]),OWNER_LITERAL_DIR=sys.argv[1],OWNER_NATIVE_DIR=sys.argv[2],OWNER_AUDIT_OUTPUT=sys.argv[3],OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
subprocess.run([sys.executable,'-B',str(P/'independent_literal.py')],env=env,check=True)
