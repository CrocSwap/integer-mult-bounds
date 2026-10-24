"""Complete helper621 native and arithmetic replay. Apache-2.0; Codex assistance."""
from pathlib import Path
import subprocess,sys
P=Path(__file__).resolve().parent
for name in ("verify_native.py","arithmetic.py"):
    subprocess.run([sys.executable,"-I","-B",str(P/name)],check=True)
print("PASS_HELPER621_WHOLE_KAPPA_003021569")
