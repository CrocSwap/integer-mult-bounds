"""Load exact retained sources. Ali Romman, with Codex. Apache-2.0."""

from hashlib import sha256
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PINS = json.loads((ROOT / 'SOURCE-PINS.json').read_text())
for pin in PINS:
    if sha256((ROOT / pin['retained_path']).read_bytes()).hexdigest() != pin['sha256']:
        raise ValueError('retained source digest')


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


arithmetic = load('source7746_arithmetic', 'retained/paired-ddg-arithmetic-step/circuit.py')
graph = load('source6072_graph', 'retained/paired-residue-sampler/verify.py')
