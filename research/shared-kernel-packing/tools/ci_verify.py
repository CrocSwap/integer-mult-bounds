# SPDX-License-Identifier: Apache-2.0
"""Generic CI entry: fresh external standard-library finite/LP replay."""
from pathlib import Path
import subprocess,sys,tempfile
if __name__=='__main__':
    root=Path(__file__).resolve().parents[1]
    parent=Path(tempfile.mkdtemp(prefix='t185-check-')).resolve()
    work=parent/'replay'
    print('Fresh external replay:',work,flush=True)
    raise SystemExit(subprocess.call([sys.executable,'-B',str(root/'tools/verify_package.py'),'--work',str(work)]))
