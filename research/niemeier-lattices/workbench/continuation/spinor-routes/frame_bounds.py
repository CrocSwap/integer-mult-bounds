"""Finite premises for the accompanying exact, scoped frame bounds."""
from pathlib import Path
from math import comb
import json
import numpy as np
OUT=Path(__file__).resolve().parent
D=14;N=1<<D

def require(condition,message):
    if not condition: raise ValueError(message)

def binary_rank(rows):
    basis={}
    for value in rows:
        v=int(value)
        while v:
            p=v.bit_length()-1
            if p in basis:v^=basis[p]
            else:basis[p]=v;break
    return len(basis)

# The degree-six representation is an equality of all 2^14 truth values,
# compressed to the fifteen possible Hamming weights.
truth=[int(w==0 or w in (7,8)) for w in range(15)]
polynomial=[sum(comb(w,k) for k in range(min(w,6)+1))%2 for w in range(15)]
require(truth==polynomial,'C != e0+...+e6')
H=[sum((((a&j).bit_count()&1)<<(j-1)) for j in range(1,15)) for a in range(16)]
require(len(set(H))==16,'H size')
require(all(h==0 or h.bit_count()in(7,8) for h in H),'H orthogonality')
V=np.array([[1]+[1-2*((x>>i)&1) for i in range(14)]+[1-2*(x.bit_count()&1)] for x in H],dtype=np.int64)
require(np.array_equal(V@V.T,16*np.eye(16,dtype=np.int64)),'H clique full rational rank')
# This is the exact 32-dimensional quotient of the fused packet-pair
# block after collapsing the constant eight-entry halves.
I=np.eye(16,dtype=np.uint8);J=np.ones((16,16),dtype=np.uint8);A=I^J
require(np.array_equal((A@A)%2,I),'I+J16 must be an involution')
T=np.block([[I,A],[A,I]])
rank_T=binary_rank(int.from_bytes(np.packbits(r,bitorder='little').tobytes(),'little') for r in T)
require(rank_T==16,'fused quotient rank')
require(np.array_equal(T[16:],(A@T[:16])%2),'fused image must be (z,Az)')
receipt={
 'ports':N,'address_dimension':16,
 'C_truth_by_weight':truth,'C_ANF':'e0+e1+e2+e3+e4+e5+e6',
 'C_ANF_degree':6,'nonzero_H_derivative_minimum_weight':512,
 'rational_dimension_at_most_8_spinor_line_bound':128,
 'residual_D_rank_previously_certified':1268,
 'every_nonzero_residual_image_column_rational_span_at_least':9,
 'rank_minimal_full_aggregate_private_copy_descent_lower_bound':11412,
 'spinor_full_center_bill':9216,'spinor_nominal_surplus':7168,
 'fused_packet_quotient_rank':rank_T,
 'fused_rank_minimal_column_width':16,
 'fused_rank':1024,'fused_rank_minimal_center_bill':16384,
 'scope':'The residual bound applies to rank-minimal factorizations implemented by full-frame aggregates followed by private copies into common target caps. The fused bill applies to rank-minimal scalar factorizations of the specified fused packet kernel. Neither is a universal circuit lower bound.'}
(OUT/'FRAME-BOUNDS.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
