#!/usr/bin/env python3
"""Optional genuinely independent width oracle using SciPy sparse matching.

No import of generate.py or verify.py. This is *not* required for verification
of the exact 21 antichain / chain-cover certificates, which are stdlib-only.
Requires scipy>=1.8 and numpy.
"""
import json
from collections import Counter
from pathlib import Path
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import maximum_bipartite_matching

source=json.loads(Path(__file__).with_name('CERTIFICATE.json').read_text())['support_masks']
expected={0:{32:1},1:{26:8},2:{18:24,20:4},3:{10:56},4:{6:70},5:{3:56},6:{2:28},7:{1:8}}
hist={q:Counter() for q in range(8)}
for survivors in range(1,256):
    members=sorted({mask & survivors for mask in source if mask & survivors})
    n=len(members)
    rows=[];cols=[]
    for i,a in enumerate(members):
        for j,b in enumerate(members):
            if a != b and a & b == a:
                rows.append(i);cols.append(j)
    mat=csr_matrix(([1]*len(rows),(rows,cols)),shape=(n,n))
    matched=maximum_bipartite_matching(mat, perm_type='row')
    width=n-sum(j>=0 for j in matched)
    erased=8-survivors.bit_count()
    hist[erased][width]+=1
    if erased==2:
        deleted=survivors^255
        a=(deleted&-deleted).bit_length()-1
        b=(deleted^(deleted&-deleted)).bit_length()-1
        assert width == (20 if a^b == 7 else 18), (deleted,width)
assert {q:dict(v) for q,v in hist.items()}==expected,hist
print('PASS_SCIPY_INDEPENDENT_MATCHING subsets=255 antipodal_pairs=4 no_new_kappa')
