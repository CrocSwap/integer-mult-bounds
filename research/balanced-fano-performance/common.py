"""Pinned reference loading for the balanced-Fano performance evidence."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def source_pins():
    pins = json.loads((HERE / 'SOURCE.json').read_text())
    files = {HERE / 'baseline.py': pins['baseline_sha256']}
    files.update({ROOT / name: digest for name, digest in pins['shared_source_sha256'].items()})
    for path, digest in files.items():
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError(f'Changed pinned source: {path.relative_to(ROOT)}')
    return pins


def load_baseline():
    source_pins()
    spec = importlib.util.spec_from_file_location('balanced_fano_baseline', HERE / 'baseline.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
