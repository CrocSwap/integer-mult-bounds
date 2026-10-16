# SPDX-License-Identifier: Apache-2.0
"""Run independent owner failure controls in an automatically cleaned workspace."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import os,subprocess,tempfile
p=Path(__file__).resolve().parent
with tempfile.TemporaryDirectory(prefix='shared-kernel-owner-controls-') as work:
    subprocess.run([sys.executable,'-I','-B',str(p/'owner_controls.py'),
                    '--source-dir',str(p/'sources'),'--candidate-dir',str(p),
                    '--words-dir',str(p/'words'),'--work-dir',str(Path(work)/'controls')],
                   check=True,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'))
