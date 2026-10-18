"""Authenticate every consumed source before executing retained auditors."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
AUDITOR = 'research/gauge44-frames-x/independent/audit_local.py'
NATIVE = 'research/complex-sw4-frame8/local/hpe_audit_and_transport.py'
ROUTING = 'research/community-k492-audit/pr622/replay/baseline558/complex-global/base/split-centres/CANONICAL-WORD.json.gz'
CLIFFORD = 'research/complex-sw4-frame8/vendor/main/research/complex-k492-owner-repair/vendor/multicold/vendor/pr558/vendor/pr552/complex-global/vendor531/vendor/clifford/clifford_exact.py'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def authenticate():
    for name, base in [('SOURCES.json', ROOT), ('VENDOR.json', HERE)]:
        for row in json.loads((HERE/name).read_text())['files']:
            if row.get('usage', 'input') != 'input':
                continue
            raw = (base/row['path']).read_bytes()
            need(hashlib.sha256(raw).hexdigest() == row['sha256'], 'source hash: '+row['path'])
            blob = hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
            need(blob == row['git_blob'], 'source blob: '+row['path'])


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module
