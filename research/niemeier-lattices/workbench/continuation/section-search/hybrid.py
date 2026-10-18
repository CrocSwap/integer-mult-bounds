"""Replace only the D16+ spinor decoder by a legal Hadamard-clique kernel.

Exact finite rank experiment, not a complete circuit or kappa certificate.
DominikScholz with OpenAI GPT-6 Astra assistance in T3 Code.
"""
from pathlib import Path
WORKBENCH = Path(__file__).resolve().parents[2]
PACKAGE = WORKBENCH.parent
import json
import time
import numpy as np


def require(ok, message):
    if not ok:
        raise ValueError(message)


def insert(basis, value):
    while value:
        pivot = value.bit_length()-1
        if pivot in basis:
            value ^= basis[pivot]
        else:
            basis[pivot] = value
            return True
    return False


def rank_with_bottom(top, bottom):
    basis = top.copy()
    for value in bottom:
        insert(basis, value)
    return len(basis)


rows = np.load((WORKBENCH / 'bit-routes/d16-ports.npz'))['ports']
sparse_count = 14576
spinors = rows[sparse_count:]
require(rows.shape == (30960, 16) and spinors.shape == (16384, 16), 'D16+ port census')
require(np.all(spinors[:, 0] == 1), 'Canonical spinor orientation')
ids = (spinors[:, 1:15] < 0).astype(np.uint32) @ (1 << np.arange(14, dtype=np.uint32))
require(len(set(ids.tolist())) == 16384, 'All canonical spinor sign patterns')
H = [sum((((a & j).bit_count() & 1) << (j-1)) for j in range(1, 15))
     for a in range(16)]
groups = {}
for index, value in enumerate(ids.tolist()):
    representative = min(value ^ h for h in H)
    groups.setdefault(representative, []).append(index)
require(len(groups) == 1024 and all(len(g) == 16 for g in groups.values()), 'Hadamard cosets')
clique_rows = [0]*16384
for group in groups.values():
    require(np.array_equal(spinors[group] @ spinors[group].T,
                           16*np.eye(16, dtype=np.int16)), 'Every clique orthogonal')
    packed = sum(1 << index for index in group) << sparse_count
    for index in group:
        clique_rows[index] = packed

start = time.monotonic()
top_basis = {}
sparse_basis = {}
sparse_mask = (1 << sparse_count)-1
for offset in range(0, sparse_count, 128):
    end = min(offset+128, sparse_count)
    decoder = ((rows[offset:end] @ rows.T) % 16 == 0)
    for packed in np.packbits(decoder, axis=1, bitorder='little'):
        value = int.from_bytes(packed.tobytes(), 'little')
        insert(top_basis, value)
        insert(sparse_basis, value & sparse_mask)
print('top ranks', len(top_basis), len(sparse_basis), 'seconds', time.monotonic()-start, flush=True)

original_basis, hybrid_basis = top_basis.copy(), top_basis.copy()
for offset in range(0, len(spinors), 128):
    end = min(offset+128, len(spinors))
    decoder = ((spinors[offset:end] @ rows.T) % 16 == 0)
    for local, packed in enumerate(np.packbits(decoder, axis=1, bitorder='little')):
        value = int.from_bytes(packed.tobytes(), 'little')
        insert(original_basis, value)
        insert(hybrid_basis, (value & sparse_mask) | clique_rows[offset+local])
require(len(sparse_basis) == 575 and len(original_basis) == 815, 'Replay known exact ranks')
result = dict(status='PASS_EXACT_HYBRID_RANK', ports=len(rows), dimension=16,
              sparse_rank=len(sparse_basis), top_block_rank=len(top_basis),
              original_full_rank=len(original_basis), hybrid_rank=len(hybrid_basis),
              hybrid_full_center_bill=16*len(hybrid_basis),
              asymptotic_rank_surplus=len(rows)-16*len(hybrid_basis),
              diagonal_and_support='Sparse and cross blocks retain exact orthogonality; spinor block is a disjoint union of orthogonal 16-port cliques including the diagonal.',
              scope='Exact rank and safe full-center charge only; no encoder, decoder or complete word certified.')
Path(__file__).with_name('HYBRID.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result, indent=2), 'seconds', time.monotonic()-start, flush=True)
