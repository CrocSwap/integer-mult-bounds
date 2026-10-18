# SPDX-License-Identifier: Apache-2.0
"""Run the frozen source-derivation review with disposable output.

Prepared for Yiyang (@Lyy-iiis) with substantial OpenAI Codex assistance.
"""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
sys.dont_write_bytecode = True
p = Path(__file__).resolve().parent
r = p / 'integration-review'
with tempfile.TemporaryDirectory(prefix='shared-kernel-integration-review-') as work:
    subprocess.run([sys.executable, '-I', '-O', '-B',
                    str(r / 'check_integration_derivation.py'),
                    '--old', str(r / 'fixtures/old'), '--new', str(r / 'fixtures/new'),
                    '--derivation', str(r / 'fixtures/derivation'), '--controls',
                    '--out', str(Path(work) / 'RESULT.json')],
                   check=True, env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
