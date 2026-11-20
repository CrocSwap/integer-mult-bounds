"""Run the four independent coordinate, Gaussian, ring and sparse-operator checks."""

from pathlib import Path
import subprocess
import sys

if __name__=="__main__":
    here=Path(__file__).resolve().parent
    for component in ("routes","blocks","middle","solve"):
        subprocess.run([sys.executable,"-I","-O","-B",str(here/("verify_"+component+".py"))],
                       check=True)
