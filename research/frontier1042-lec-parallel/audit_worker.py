# SPDX-License-Identifier: Apache-2.0
"""Worker side of lec_parallel.py: PR635's pinned audit applied to exact trial bytes.

Kept in its own module so that the worker functions stay importable (and picklable) while
the pinned launcher and script temporarily occupy __main__ during the record and replay passes.
"""
import contextlib
import hashlib
import importlib.util
import io
import shutil
import tempfile
from pathlib import Path

AUDIT_SHA256 = 'c9a05ff291016b870b4fc925b317abd9c3a604c73ffc8920dfdbbeb475e20aa3'
AUDIT = None


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load_audit(code_dir):
    path = Path(code_dir) / 'hpe_audit_and_transport.py'
    if sha(path.read_bytes()) != AUDIT_SHA256:
        raise RuntimeError('pinned hpe_audit_and_transport.py digest mismatch')
    spec = importlib.util.spec_from_file_location('pinned_hpe_audit_and_transport', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def init_worker(code_dir):
    global AUDIT
    AUDIT = load_audit(code_dir)


def evaluate(task):
    """The outcome, and the printed output, that trial() of the pinned script would observe.

    Returns (kind, args, stdout): kind 'pass' (run returned), 'assert' (AssertionError with
    these args) or 'error' (any other exception, which the pinned trial() does not catch).
    """
    data, routing = task
    tmp = Path(tempfile.mkdtemp())
    out = io.StringIO()
    try:
        p = tmp / 'w.json.gz'
        p.write_bytes(data)
        with contextlib.redirect_stdout(out):
            try:
                AUDIT.run(p, Path(routing), tmp / 'out')
                kind, args = 'pass', ()
            except AssertionError as e:
                kind, args = 'assert', e.args
            except Exception as e:
                kind, args = 'error', (repr(e),)
        return kind, args, out.getvalue()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
