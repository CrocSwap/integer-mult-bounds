"""Exact partial-flag representation obstruction, restricted encoding scope."""
from pathlib import Path
import json
O=Path(__file__).resolve().parent;q=3;m=2;N=q**(2*m)
def swap(x,axis):
 d=[]
 for _ in range(2*m):d.append(x%q);x//=q
 d[axis],d[m+axis]=d[m+axis],d[axis]
 return sum(v*q**i for i,v in enumerate(d))
D1=[swap(i,0) for i in range(N)];D2=[swap(i,1) for i in range(N)]
A1=[swap(i,0) for i in range(N)]+[N+i for i in range(N)]
A2=list(range(N))+[N+swap(i,0) for i in range(N)]
def mixed_col(a,b,i):
 r={}
 for j,c in [(i,1),(a[i],-1),(b[i],-1),(a[b[i]],1)]:r[j]=r.get(j,0)+c
 return {j:c for j,c in r.items() if c}
assert all(not mixed_col(A1,A2,i) for i in range(2*N))
w=next(i for i in range(N) if mixed_col(D1,D2,i));v=mixed_col(D1,D2,w)
assert v and all(sum(c for j,c in v.items() if D1[j]==k)==-v.get(k,0) for k in range(N))
assert all(sum(c for j,c in v.items() if D2[j]==k)==-v.get(k,0) for k in range(N))
r={'status':'PASS_EXACT_PARTIAL_FLAG_MODEL_OBSTRUCTION','q':q,'m':m,'logical_basis_columns':N,'physical_basis_columns':2*N,'logical_minus_minus_witness':v,'physical_mixed_character_operator_identically_zero':True,'logical_mixed_character_rank':((q*q-q)//2)**2,'conclusion':'No injective fixed value encoding E intertwines BOTH partial flag factors D1,D2 with physical family factors A1,A2. Since (I-A1)(I-A2)=0 but logical (I-D1)(I-D2) nonzero, intertwining would kill a nonzero logical subspace.','terminal_encoding_vs_flags':'Previous terminal-only embedding is valid. It cannot generally be extended to all partial operations by the same encoding. Intertwining D1 and D1D2 already forces intertwining D2.','scope':'Concrete aligned two-axis flag model, not a claim that every actual signed95 helper has this exact flag/piece alignment. Actual local-word frame matrices and lowering must be checked individually.','possible_escape':'Time-dependent encodings E_t or a richer multi-stream representation. Each change needs legal physical read/write/source maps, arbitrary spectator action/restoration, inverse and actual primitive profile. No cheap orthogonal ADDRESS sigma assumed.'}
if (O/'FLAGS.json').exists():
 r['compressed_domain_caveat']=json.loads((O/'FLAGS.json').read_text()).get('compressed_domain_caveat','See DIMENSION-AUDIT.json.')
(O/'FLAGS.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'])
