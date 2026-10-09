#!/usr/bin/env python3
"""Replay the merged-exterior selection, exact profiles and composition.

Checks the controlled permutations against the pinned PR34 module, recomputes
every candidate merged and removed edge profile in exact integer arithmetic,
replays the per-role selection, recomposes the complete recursive profile on
the PR79 witness and compares both certificates.
"""
import sys
if sys.flags.optimize:
    raise ValueError('Assertions must remain enabled')
sys.dont_write_bytecode = True

from hashlib import sha256
from pathlib import Path
import importlib.util, json

import binary_frame_math as arithmetic
from merged_exterior import OUT, PERMS, ROOT, selection
from merged_exterior_compose import compose

GEOMETRY = ROOT / 'research/copied-fixed/reversed'


def check_permutations():
    """Compare with the pinned PR34 module, loaded by the inherited loader (host resource caps omitted)."""
    pinned = json.loads((GEOMETRY / 'geometry-source.json').read_text())['sha256']['pr34/independent_controls.py']
    source = GEOMETRY / 'pr34/independent_controls.py'
    assert sha256(source.read_bytes()).hexdigest() == pinned, 'pinned PR34 source changed'
    spec = importlib.util.spec_from_file_location('merged_exterior_geometry', GEOMETRY / 'geometry.py')
    geometry = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(geometry)
    controls = geometry.load('pr34_independent_merged_exterior', source)
    assert controls.completion(23, *controls.corner_labels(23)) == PERMS, 'controlled permutations differ from pinned PR34'


def verify():
    check_permutations()
    replayed = selection()
    stored = json.loads((OUT / 'merged-exterior-selection.json').read_text())
    assert replayed == stored, 'selection or exact merged profiles differ'
    result = json.loads(json.dumps(arithmetic.js(compose(stored))))
    assert result == json.loads((OUT / 'merged-exterior-kappa.json').read_text()), 'composition differs'
    print(f'PASS merged exteriors: kappa={result["kappa"]}; bit saving={result["bit_saving"]}; '
          f'largest child {result["bit"]["maxchild"]}', flush=True)


if __name__ == '__main__':
    verify()
