"""Independent integer witnesses. @CubeJerry with substantial OpenAI Codex assistance.
Apache-2.0. No import from the phase package or any solver."""
import hashlib
import json
from pathlib import Path

def need(ok, why):
    if not ok: raise ValueError(why)
def unit(j): return tuple(int(i==j) for i in range(16))
def add(a,b,c=1): return tuple(x+c*y for x,y in zip(a,b))
def scale(a,c): return tuple(c*x for x in a)
def walsh(z):
    return tuple(sum((-1)**((r&s).bit_count())*x for s,x in enumerate(z)) for r in range(16))
def in_l(z):
    return sum(z)%4==0 and all(sum(z[s] for s in range(16) if s>>j&1)%2==0 for j in range(4))
def in_2l(z): return all(x%2==0 for x in z) and in_l(tuple(x//2 for x in z))
def a(z):
    raw=walsh(z);need(all(x%4==0 for x in raw),'A integrality')
    return tuple(x//4 for x in raw)
def k(z): return tuple((-1)**j.bit_count()*z[j^15] for j in range(16))
def sign(z): return tuple((-1)**j.bit_count()*x for j,x in enumerate(z))
def complement(z): return tuple(z[j^15] for j in range(16))
def d(z): return add(k(z),z)

for index in range(16):
    z=unit(index)
    need(walsh(walsh(z))==scale(z,16),'W square on a complete basis')
    need(walsh(sign(walsh(z)))==scale(complement(z),16),'W S W=16J')
    need(walsh(k(z))==k(walsh(z)),'W K=K W on a complete basis')
    need(sign(complement(z))==complement(sign(z)),'S J=J S')
    residues=tuple((sum(z)-2*sum(((r>>j)&1)*sum(z[t] for t in range(16) if t>>j&1)
                                for j in range(4)))%4 for r in range(16))
    need(tuple(x%4 for x in walsh(z))==residues,'Coarse quotient linear identity')

u=[scale(unit(0),4)]+[scale(add(unit(1<<j),unit(0),-1),2) for j in range(4)]
v=tuple(sum(x) for x in zip(*u[1:]))
w=(1,-2,-1,0,-1,0,0,-1,-1,0,0,-1,0,-1,0,-1)
for z in u+[v,w]:
    need(in_l(z) and all(x%4==0 for x in walsh(z)),'Two integrality predicates')
    need(k(k(z))==z and in_l(k(z)),'K preserves L')
    need(a(k(z))==k(a(z)),'A K commutation')
for mask in range(1,32):
    z=tuple(sum(u[j][r] for j in range(5) if mask>>j&1) for r in range(16))
    need(not in_2l(z),'Five independent E classes')
need(in_2l(d(u[0])),'D u0=0 mod2L')
for z in u[1:]: need(in_2l(add(d(z),u[0],-1)),'D uj=u0 mod2L')
need(in_2l(add(d(w),v,-1)),'D w=v mod2L')
need(not in_2l(v) and not in_2l(add(v,u[0])),'Independent image classes')
need(not in_l(add(w,unit(0))),'Malformed preimage control')
need(not in_2l(add(d(w),u[0],-1)),'False image control')
need(not in_2l(add(add(complement(u[1]),u[1]),u[0],-1)),'Missing S phase control')
print(json.dumps({'status':'PASS_INDEX4096_OBSTRUCTION_WITNESSES','E_basis':u,'v':v,'w':w,
    'half_residual_u1':tuple(x//2 for x in add(d(u[1]),u[0],-1)),
    'half_residual_w':tuple(x//2 for x in add(d(w),v,-1)),
    'independent_parity_classes':5,'rank_Kplus_on_E':1,'independent_E_image_classes':2,
    'controls':['malformed preimage','false image','missing S phase'],'affine_period_index_divisor':4096,
    'sha256':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(Path(__file__).parent.iterdir()) if f.is_file()}},sort_keys=True))
