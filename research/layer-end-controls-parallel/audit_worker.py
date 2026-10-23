# SPDX-License-Identifier: Apache-2.0
"""Worker side of controls_parallel.py: the real, pinned PR635 audit applied to exact trial bytes.

Kept in its own module so that worker functions stay importable (and picklable) while
the pinned script temporarily occupies __main__ during the record and replay passes.
"""
import hashlib
import shutil
import sys
import tempfile
from pathlib import Path

AUDIT_SHA256 = '0dacf4cedb020d561e0188052319f1a6e6abaf6c79f9e94d8c9c91492e5c1747'
AUDIT = None


def sha(data):
    return hashlib.sha256(data).hexdigest()


def init_worker(code_dir):
    global AUDIT
    path = Path(code_dir) / 'hpe_audit_and_transport.py'
    if sha(path.read_bytes()) != AUDIT_SHA256:
        raise RuntimeError('pinned hpe_audit_and_transport.py digest mismatch')
    if str(code_dir) not in sys.path:
        sys.path.insert(0, str(code_dir))
    import importlib.util
    spec = importlib.util.spec_from_file_location('pinned_hpe_audit_and_transport', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    AUDIT = mod


def evaluate(task):
    """The outcome trial() of the pinned script would observe for these exact bytes."""
    data, routing = task
    tmp = Path(tempfile.mkdtemp())
    try:
        p = tmp / 'w.json.gz'
        p.write_bytes(data)
        try:
            AUDIT.run(p, Path(routing), tmp / 'out')
            return ('pass', ())
        except AssertionError as e:
            return ('assert', e.args)
        except Exception as e:      # the pinned trial() does not catch these; the replay re-raises
            return ('error', (repr(e),))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
