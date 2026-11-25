"""Pins and loaders for the optional Clifford state benchmark. Apache-2.0."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = json.loads((HERE / 'SOURCE.json').read_text())


def verify_sources(root=ROOT):
    if sys.flags.optimize:
        raise ValueError('Assertions must remain enabled')
    for relative, expected in SOURCE['files'].items():
        actual = hashlib.sha256((root / relative).read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError('Pinned source changed: ' + relative)


def load_clifford(which='baseline'):
    """Load the pairwise baseline (default) or the production multicold evaluator.

    Registers the module as ``clifford_exact`` so the helper-interface adapters
    reuse this object instead of re-importing the on-disk multicold file.
    """
    key = 'clifford' if which == 'baseline' else 'production_clifford'
    path = ROOT / SOURCE[key]
    spec = importlib.util.spec_from_file_location('clifford_exact', path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def fixture_runs():
    return [ROOT / path for path in SOURCE['runs']]
