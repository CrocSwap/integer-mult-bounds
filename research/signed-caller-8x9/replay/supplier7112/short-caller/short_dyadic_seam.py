"""Build exact candidate central tapes for the 8+8 signed caller."""
from hashlib import sha256
from itertools import product
from pathlib import Path
import json

import host34
import mirrored
from host34 import Q,eye,z,m,tr,add,sc,msum,inv

root=Path(__file__).resolve().parent
orig=(root/"mirrored.py").read_text()
part=orig[orig.index("def tape("):orig.index("def varied_tape(")]
part=part.replace("def tape(signs, blocks=None, ring_audit=None):","def tape(blocks, ring_audit=None):")
part=part.replace("    blocks = blocks or [sc(J, sign) for sign in signs]\n","")
part=part.replace("[None] * 18","[None] * stages").replace("phi[:9]","phi[:half]")
part=part.replace("(list(range(9)), list(range(17, 8, -1)))",
                  "(list(range(half)), list(range(stages-1, half-1, -1)))")
part=part.replace("offset = 2 + 16 * side","offset = 2 + 2*(half-1)*side").replace("range(8)","range(half-1)")
part=part.replace("range(18)","range(stages)").replace("(18, block_tuple","(stages, block_tuple")
half=8
stages=2*half
N=2+4*(half-1)
def masks():
    return [{0,1,*range(2+2*(half-1)*side,2+2*(half-1)*side+2*min(j+1,half-1))}
            for side,order in enumerate((range(half),range(half-1,-1,-1))) for j in order]
def block_lu(H):
    n=len(H)
    U=[[b for b in row] for row in H]
    L=[[eye(2) if i==j else z(2,2) for j in range(n)] for i in range(n)]
    for k in range(n):
        P=inv(U[k][k])
        for i in range(k+1,n):
            f=m(U[i][k],P)
            L[i][k]=f
            for j in range(k,n):
                U[i][j]=add(U[i][j],m(f,U[k][j]),-1)
    assert all(H[i][j]==msum((m(L[i][k],U[k][j]) for k in range(n)),2,2)
               for i in range(n) for j in range(n))
    return U
ns=vars(mirrored)|dict(globals())
exec(compile(part,str(root/"mirrored.py"),"exec"),ns)
tape=ns["tape"]
I=eye(2)
J=[[Q(0),Q(-2)],[Q(1,2),Q(0)]]
def conj(t):
    S=[[Q(1),Q(t)],[Q(0),Q(1)]]
    return m(m(S,J),inv(S))
def matrix_word(items):
    value=I
    for u in items:value=m(value,u)
    return value
def dyadic(x):
    x=Q(x)
    return not (x.denominator & (x.denominator-1))
def control():
    audit=[]
    source=list(range(0,half))+list(range(half,stages))
    for _ in source: audit.append(J)
    assert matrix_word(audit)==I and matrix_word(audit[:-1]) not in (I,sc(I,-1))
    # In 8+8 the same-generator seam is ±I for all choices of signs.
    assert matrix_word(audit[:half])==I
control()
tested=0
rational=0
hits=[]
for t,a,b,position,sgn in product((-4,4),(-1,1),(-1,1),range(half//2),(0,stages-half-1)):
    terminal=[sc(J,a),sc(conj(t),b)]
    left=[J,inv(J)]*position+terminal+[J,inv(J)]*(half//2-1-position)
    right=[inv(u) for u in reversed(left)]
    right[sgn]=sc(right[sgn],-1)
    assert len(left)==len(right)==half and matrix_word(left+right)==sc(I,-1)
    seam=matrix_word(left)
    assert all(dyadic(x) for sign in (-1,1) for row in inv(add(I,seam,sign)) for x in row)
    tested+=1
    try:
        domains,physical=tape(left+right)
    except (AssertionError,ZeroDivisionError,StopIteration):
        continue
    rational+=1
    try:
        audit=[]
        domains,physical=tape(left+right,audit)
    except AssertionError:
        continue
    hits.append({"sequence":[[[str(x) for x in row] for row in v] for v in left+right],
                 "seam":[[str(x) for x in row] for row in seam],"stages":audit,
                 "parameter":[t,a,b,position,sgn]})
    print("exact dyadic candidate",hits[-1]["parameter"],flush=True)
    if len(hits)>=4:break
record={"archive_mirrored_sha256":sha256((root/"mirrored.py").read_bytes()).hexdigest(),
        "tested":tested,"rational_candidates":rational,"dyadic_candidates":hits,
        "scope":"Generalizes the pinned exact rational 9+9 mirrored B-host tape to 8+8. Same-generator odd stages fail total -I and an even half seam is ±I. Tests short noncommuting tapes with dyadic I±seam inverses and exact projection identities. The physical sign-query lowering and full bill remain separate."}
with (root/"SHORT-DYADIC-SEAM.json").open("x") as f:
    json.dump(record,f,indent=2)
print("tested",tested,"rational",rational,"dyadic",len(hits),flush=True)
