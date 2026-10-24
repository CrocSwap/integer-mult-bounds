"""Source-bound replay of Mihir Srivastava's unchanged PR4504 frame audit.

Brian, with substantial OpenAI Codex assistance. Apache-2.0.
The canonical temporary-root workaround was identified by the maintainer review.
"""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
AUDIT = ROOT / 'research/pr4470-frame-audit/verify.py'


def load_audit():
    sources = json.loads((HERE / 'SOURCES.json').read_bytes())['files']
    script = None
    for row in sources:
        if row['usage'] != 'input':
            continue
        path = ROOT / row['path']
        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != row['sha256']:
            raise ValueError('source SHA256 mismatch: ' + row['path'])
        if path == AUDIT:
            script = raw
    if script is None:
        raise ValueError('missing pinned audit source')
    audit = types.ModuleType('pr4470_frame_audit')
    audit.__file__ = str(AUDIT)
    # Compile authenticated bytes directly, without consulting an import cache.
    exec(compile(script, str(AUDIT), 'exec'), audit.__dict__)
    return audit


def replay():
    if len(sys.argv) != 1:
        raise ValueError('verification only: no arguments or --write mode')
    audit = load_audit()
    previous = tempfile.tempdir
    try:
        tempfile.tempdir = str(Path(tempfile.gettempdir()).resolve())
        audit.main()
    finally:
        tempfile.tempdir = previous
    print('PASS_PR4470_TEMP_ROOT_REPLAY')


if __name__ == '__main__':
    replay()
