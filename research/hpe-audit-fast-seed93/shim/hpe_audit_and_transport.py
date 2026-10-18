"""Stand-in for PR635's hpe_audit_and_transport module (opt-in tooling, seed 93).

HPE_AUDIT_MODE=fast        run() is hpe_audit_fast.run.
HPE_AUDIT_MODE=crosscheck  run() executes the pinned reference and the fast
                           variant on the same input and raises RuntimeError
                           (never AssertionError, so no caller can absorb it)
                           unless both give the same outcome and byte-identical
                           outputs; the reference result is then returned.
HPE_AUDIT_REFERENCE names the pinned reference file; its sha256 is checked.
Prepared by Wronskode (@Wronskode) with substantial AI assistance from Claude
(Anthropic) via Claude Code. Apache-2.0.
"""
import contextlib
import hashlib
import importlib.util
import io
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

PACKAGE = Path(__file__).resolve().parents[1]
REFERENCE_SHA256 = 'c9a05ff291016b870b4fc925b317abd9c3a604c73ffc8920dfdbbeb475e20aa3'
MODE = os.environ.get('HPE_AUDIT_MODE', 'fast')
if MODE not in ('fast', 'crosscheck'):
    raise RuntimeError('HPE_AUDIT_MODE must be fast or crosscheck')


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_fast = _load('hpe_audit_fast', PACKAGE / 'hpe_audit_fast.py')
_reference = None
if MODE == 'crosscheck':
    ref_path = Path(os.environ['HPE_AUDIT_REFERENCE'])
    if hashlib.sha256(ref_path.read_bytes()).hexdigest() != REFERENCE_SHA256:
        raise RuntimeError('reference audit is not the pinned PR635 file')
    _reference = _load('hpe_audit_reference', ref_path)
CROSSCHECKS = []


def _outcome(module, raw_path, routing_path, out):
    stdout = io.StringIO()
    try:
        with contextlib.redirect_stdout(stdout):
            module.run(raw_path, routing_path, out)
    except Exception as exc:          # compared, then re-raised by the caller
        return exc, (type(exc).__name__, repr(exc.args)), None, None
    files = {p.name: p.read_bytes() for p in sorted(out.iterdir())}
    receipt = json.loads(files.pop('SCALAR-FRAME-AUDIT.json'))
    receipt.pop('seconds')
    printed = json.loads(stdout.getvalue())
    printed.pop('seconds')
    return None, None, (files, receipt, printed), stdout.getvalue()


def run(raw_path, routing_path, out):
    if MODE == 'fast':
        return _fast.run(raw_path, routing_path, out)
    scratch = Path(tempfile.mkdtemp())
    try:
        f_exc, f_key, f_out, _ = _outcome(_fast, raw_path, routing_path, scratch / 'fast')
        r_exc, r_key, r_out, r_text = _outcome(_reference, raw_path, routing_path, out)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    if f_key != r_key or f_out != r_out:
        raise RuntimeError(('hpe audit crosscheck mismatch', str(raw_path), r_key, f_key))
    CROSSCHECKS.append(r_key)
    with open(os.environ.get('HPE_AUDIT_CROSSCHECK_LOG', os.devnull), 'a') as log:
        log.write(json.dumps(dict(outcome=r_key or 'PASS', input_sha256=hashlib.sha256(
            Path(raw_path).read_bytes()).hexdigest())) + '\n')
    if r_exc is not None:
        raise r_exc
    sys.stdout.write(r_text)
