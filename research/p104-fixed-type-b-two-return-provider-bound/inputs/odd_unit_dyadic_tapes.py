"""Build an exact asymmetric 8+9 B tape from five-turn closures."""
from pathlib import Path
from hashlib import sha256
from fractions import Fraction as Q
import json
import mirrored
from host34 import eye, z, inv, m, add, sc, msum, tr

root=Path(__file__).resolve().parent
p=root/"short_dyadic_seam.py"
ns={"__file__":str(p)}
exec(compile(p.read_text().split("control()\ntested=",1)[0],str(p),"exec"),ns)
a,b=8,9
n=2+2*(a-1+b-1)
stages=a+b
def masks():
    return [{0,1,*range(offset,offset+2*min(j+1,length-1))}
            for offset,length,order in ((2,a,range(a)),(2+2*(a-1),b,range(b-1,-1,-1))) for j in order]
src=ns["part"]
assert "range(half-1)" in src
src=src.replace("    for side, ids in enumerate((list(range(half)), list(range(stages-1, half-1, -1)))):",
                "    for side, ids in enumerate((list(range(half)), list(range(stages-1, half-1, -1)))):\n        arm=len(ids)-1")
src=src.replace("offset = 2 + 2*(half-1)*side","offset = 2 + 2*(half-1)*side")
src=src.replace("range(half-1)","range(arm)")
assert "range(arm)" in src
src=src.replace("def tape(blocks, ring_audit=None):","def tape(blocks, ring_audit=None, frames=None):")
src=src.replace("        P = m(x, dual)","        P = m(x, dual)\n        if frames is not None:frames.append((x,dual,add(I,local)))")
env=vars(mirrored)|ns|dict(half=a,stages=stages,N=n,masks=masks)
exec(compile(src,str(root/"mirrored.py"),"exec"),env)
tape=env["tape"]
J=ns["J"]
pair=[J,inv(J)]
srcpath=root/"ODD-UNIT-PREFIX-CLOSURES.json"
closures=json.loads(srcpath.read_text())["hits"]
attempted=rational=0
hits=[]
for ci,w in enumerate(closures):
    turns=[[[Q(t[0]),Q(t[1])],[Q(t[2]),Q(t[3])]] for t in w["turns"]]
    def inflate(v):
        return [[Q(v[0]),Q(v[1])],[Q(v[2]),Q(v[3])]]
    lp=inflate(w["left_padding"])
    rp=inflate(w["right_padding"])
    blocks=[lp,inv(lp)]*3+turns+[rp,inv(rp)]*3
    assert len(blocks)==stages and ns["matrix_word"](blocks)==sc(eye(2),-1)
    attempted+=1
    try:
        audit=[]
        tape(blocks,audit)
    except (AssertionError,ZeroDivisionError,StopIteration):
        continue
    hits.append({"closure":ci,"padding":[3,0],"sequence":[[[str(q) for q in row] for row in M] for M in blocks],
                 "stage_bounds":audit})
    print("exact asymmetric unit dyadic tape",ci,flush=True)
    if len(hits)>=8:break
with (root/"ODD-UNIT-DYADIC-TAPES.json").open("x") as f:
    json.dump({"closure_input_sha256":sha256(srcpath.read_bytes()).hexdigest(),"checked":attempted,"dyadic_tapes":hits,
               "shape":[a,b],"scope":"Exact rational construction and dyadic verification of each local B host and pulled-back passive projection. Grouped idle lowering, terminal signed correction and complete caller replay are separate."},f,indent=2)
print("asymmetric tapes",len(hits),"of",attempted,flush=True)
