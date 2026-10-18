"""Retain all sparse/cross entries but prune spinor cubic-class interactions."""
from pathlib import Path
import importlib.util
import json
import numpy as np

spec = importlib.util.spec_from_file_location('hybrid', Path(__file__).with_name('hybrid.py'))
h = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h)

truth = (h.spinors < 0).astype(np.uint8)
anf = truth.copy()
for bit in range(4):
    for index in range(16):
        if index >> bit & 1:
            anf[:, index] ^= anf[:, index ^ (1 << bit)]
h.require(not anf[:, 0].any() and not anf[:, 15].any(), 'Even sign parity and canonical representatives')
cubic = anf[:, [7, 11, 13, 14]] @ np.array([1, 2, 4, 8], dtype=np.uint8)
bases = [h.top_basis.copy() for k in range(4)]
for offset in range(0, len(h.spinors), 128):
    end = min(offset+128, len(h.spinors))
    decoder = (h.spinors[offset:end] @ h.rows.T) % 16 == 0
    spinor_decoder = decoder[:, h.sparse_count:].copy()
    for k, basis in enumerate(bases):
        decoder[:, h.sparse_count:] = spinor_decoder & (
            (cubic[offset:end, None] >> k) == (cubic[None, :] >> k))
        for packed in np.packbits(decoder, axis=1, bitorder='little'):
            h.insert(basis, int.from_bytes(packed.tobytes(), 'little'))

results = [dict(cubic_dimensions=k, spinor_block_count=1 << (4-k),
                ports=len(h.rows), rank=len(basis), full_center_bill=16*len(basis),
                asymptotic_surplus=len(h.rows)-16*len(basis))
           for k, basis in enumerate(bases)]
Path(__file__).with_name('HYBRID-SECTIONS.json').write_text(json.dumps(results, indent=2)+'\n')
print(json.dumps(results, indent=2), flush=True)
