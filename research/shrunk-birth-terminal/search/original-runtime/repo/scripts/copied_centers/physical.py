"""Exact copied-retained-total physical histogram replacement.

Copyright 2026 icekylinx, Apache-2.0; developed with OpenAI GPT-6 Astra and
Codex assistance. The copied-stream interface is credited to Aurel Prosz
(Paureel); this application to retained-total reads is icekylinx's work.
"""
from .corners import require


def copied_histogram(record):
    """Return H' from the unchanged selected scalar/matching record."""
    h, roles = record['h'], record['R']
    old = record['histogram']
    loss = h*(h-1)
    require(record['loss'] == loss, 'Every selected retained center must have rank h-1')
    require(len(old) == h+1 and all(isinstance(n,int) and n>=0 for n in old),
            'Invalid original physical histogram')
    require(sum(r*n for r,n in enumerate(old)) == h*roles+2*loss,
            'Original producer rank identity failed')
    require(old[h] >= h, 'Missing retained-total rank-h cleanup children')
    changed = list(old)
    changed[1] += h
    changed[h] -= h
    require(sum(changed) == sum(old), 'Copied reads changed the charged call count')
    require(changed[h-1] == old[h-1], 'Copied rank-(h-1) transforms were removed')
    require(all(changed[r] == old[r] for r in range(h+1) if r not in (1,h)),
            'Copied read modified an unrelated residual')
    mass = sum(r*n for r,n in enumerate(changed))
    require(mass == h*roles+loss, 'Copied-total rank mass failed')
    return dict(histogram=changed, rank_sum=mass, saved_rank=loss,
                retained_total_uses=h, roles_unchanged=roles)
