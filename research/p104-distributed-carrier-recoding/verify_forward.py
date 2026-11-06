"""Replay the separately authored forward-SSA/dual checker against its receipt.

Jerry Chen / @CubeJerry with OpenAI Codex assistance. Apache-2.0.
The wrapper authenticates and runs independent review code without modifying it.
"""
from pathlib import Path
import contextlib
import hashlib
import io
import json
import runpy
import sys
import tempfile

HERE=Path(__file__).resolve().parent

def need(condition,reason):
    if not condition:raise ValueError(reason)

origins=json.loads((HERE/'ORIGINS.json').read_text())
for row in origins['independent_review_files']:
    need(hashlib.sha256((HERE/row['path']).read_bytes()).hexdigest()==row['sha256'],'Exact independent-review input '+row['path'])
with tempfile.TemporaryDirectory(prefix='p104-forward-review-') as temp:
    output=Path(temp)/'receipt.json';old=sys.argv
    sys.argv=[str(HERE/'review_forward.py'),str(HERE),'PR6702',str(output)]
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            runpy.run_path(str(HERE/'review_forward.py'),run_name='__main__')
    finally:sys.argv=old
    actual=json.loads(output.read_text())
    expected=json.loads((HERE/'FORWARD-REVIEW.json').read_text())
    need(actual==expected,'Complete independent forward/dual receipt including every certificate')
print('PASS_INDEPENDENT_FORWARD_REVIEW: complete residence, interval and response census; 2387 dual witnesses checked by direct dot products')
