"""Check source pins and load the retained algebra and PR662 gate tables."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = json.loads((HERE / 'SOURCES.json').read_text())


def verify_sources():
    if sys.flags.optimize:
        raise ValueError('Assertions must remain enabled')
    for relative, digest in SOURCE['files'].items():
        if hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() != digest:
            raise ValueError('Pinned source changed: ' + relative)


def load(relative, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def engines():
    verify_sources()
    return (load(SOURCE['algebra'], 'selected_exact_algebra'),
            load(SOURCE['dense'], 'selected_dense_state'))
