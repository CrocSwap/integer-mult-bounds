"""Exact support bound for the existing labels and real tensor encoders."""
from collections import Counter
import hashlib
import json
import numpy as np
from geometry import SOURCE, profile_labels, require


def independent_rows_mod3(rows):
    basis, selected = {}, []
    for index, raw in enumerate(rows):
        row = np.asarray(raw, dtype=np.int64).copy() % 3
        for pivot in sorted(basis):
            row = (row-row[pivot]*basis[pivot]) % 3
        nonzero = np.flatnonzero(row)
        if not len(nonzero):
            continue
        pivot = int(nonzero[0])
        basis[pivot] = (row*(1 if row[pivot] == 1 else 2)) % 3
        selected.append(index)
        if len(selected) == rows.shape[1]:
            break
    return selected


def certify_support(vectors, profiles):
    fitting = json.loads((SOURCE/'evidence/TURYN-FITS.json').read_text())
    labels, _ = profile_labels(vectors, profiles, fitting['profile_fit_independent_rows'])
    receipts = []
    for high in range(3):
        low = (high+1) % 3
        other = [block for block in range(3) if block != low]
        ids = np.flatnonzero(profiles == high)
        roots, first, assignment, counts = np.unique(
            vectors[ids, 8*low:8*(low+1)], axis=0, return_index=True,
            return_inverse=True, return_counts=True)
        representatives = ids[first]
        rootlabels = labels[representatives, 9*high:9*(high+1)]
        require(roots.shape == (120, 8) and np.all(counts == 64),
                'Exactly 120 low-root fibers, each with 64 ports')
        for group in range(120):
            indices = ids[assignment == group]
            require(np.all(labels[indices] == labels[indices[0]]),
                    'Existing labels are constant on every low-root fiber')
            blocks = vectors[indices].astype(np.int32).reshape(64, 3, 8)
            z = (blocks[:, other[0], :, None]*blocks[:, other[1], None, :]).reshape(64, 64)
            require(np.array_equal(z @ z.T, 128*np.eye(64, dtype=np.int32)),
                    'Every low-root fiber spans its full real tensor factor')
        histogram, witnesses = Counter(), []
        for functional in range(1, 512):
            bits = np.array([(functional >> j) & 1 for j in range(9)], dtype=np.uint8)
            selected = np.flatnonzero((rootlabels @ bits) & 1)
            basis = independent_rows_mod3(roots[selected])
            require(len(basis) == 8, 'Every nonzero binary functional selects a real root basis')
            witnesses.append(representatives[selected[basis]].tolist())
            histogram[str(len(selected))] += 1
        encoded = json.dumps(witnesses, separators=(',', ':')).encode()
        receipts.append(dict(profile=high, low_block=low, fibers_checked=120,
            ports_per_fiber=64, binary_functionals_checked=511,
            subset_size_histogram=dict(histogram),
            mod3_basis_witnesses_sha256=hashlib.sha256(encoded).hexdigest()))
    return dict(profiles=receipts, nonzero_tensor_encoder_support_rank=27,
        rank_minimal_512_encoder_bill_lower_bound=13824,
        scope='Existing direct-sum 27-bit labels and nonzero real linear tensor encoders. Applies to real basis changes and rank-minimal 512-feature factorizations; redundant encoders outside the tensor column space are excluded.')
