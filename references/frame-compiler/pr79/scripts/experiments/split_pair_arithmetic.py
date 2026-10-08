"""Private adapters for the unchanged PR65 directed arithmetic and audit."""
import sys
if sys.flags.optimize:
    raise ValueError('Assertions must remain enabled')
sys.dont_write_bytecode = True

import importlib.util
from pathlib import Path

BASELINE = Path(__file__).resolve().parents[2] / 'references/frame-compiler/pr65'


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def private_arithmetic():
    here = BASELINE / 'research/reordered-rank-pair/arithmetic'
    previous_path = sys.path[:]
    absent = object()
    previous_refine = sys.modules.get('refine', absent)
    try:
        refine = _load('split_pair_private_refine', here / 'refine.py')
        sys.modules['refine'] = refine
        audit = _load('split_pair_private_arithmetic_audit', here / 'audit.py')
        assert audit.refine is refine
        return refine, audit
    finally:
        sys.path[:] = previous_path
        if previous_refine is absent:
            sys.modules.pop('refine', None)
        else:
            sys.modules['refine'] = previous_refine


refine, audit = private_arithmetic()
