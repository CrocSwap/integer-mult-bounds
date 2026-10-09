"""Pinned PR117 scalar DAG adapter for the saturated deferred compiler.

The searched graph is upstream PR117 work credited to eumemic with Anthropic
Claude assistance. This adapter preserves that witness and producer unchanged;
saturation integration is separate OpenAI Codex-assisted work. Apache-2.0.
"""
from hashlib import sha256
from pathlib import Path
from replayed_producer import build as replayed_build

WITNESS_SHA256 = '3c034d0aae388ef567a454826f4f48b26fd8a94c71e8ffed4835271b349a783b'

def build(h, prefix, central_disjoint, base=2):
    assert (h, central_disjoint, base) == (24,24,2)
    witness=Path(__file__).resolve().parent/'inputs/complex-dag.json.gz'
    assert sha256(witness.read_bytes()).hexdigest() == WITNESS_SHA256, 'PR117 DAG pin mismatch'
    return replayed_build(witness,prefix)
