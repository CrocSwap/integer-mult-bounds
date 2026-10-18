"""Bind the actual dirty reader, signed data permutation and binary covariance.

Jose Manuel (jmbarrancoml), with substantial OpenAI Codex assistance.
Apache-2.0. Reader pullback follows the credited PR2491/Richardson source.
"""
from fractions import Fraction as F
from hashlib import sha256
import gzip
import io
import json
from pathlib import Path
import tarfile

ROOT=Path(__file__).resolve().parents[2]
ARCHIVE="research/community-frontier1094-audit/selected-replay.tar.gz"
ARCHIVE_SHA="f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6"
PREFIX="candidate/strict/global/base/providers/gauge44/"
Q=(3,0,1,2,7,4,5,6)
PIVOTS=(224,225,226,227,240,241,256,257)
SIGMA=(433,309,174,143,313,398,64,158,307)


def need(ok,why):
    if not ok:raise ValueError(why)


def add(a,b,c=F(1)):
    out=a.copy()
    for j,v in b.items():
        x=out.get(j,F(0))+c*v
        if x:out[j]=x
        else:out.pop(j,None)
    return out


def binary(rows,x):
    return sum(((r&x).bit_count()%2)<<i for i,r in enumerate(rows))


def span(vectors):
    result={0}
    for v in vectors:result|={x^v for x in tuple(result)}
    return result


def inverse(matrix):
    n=len(matrix)
    rows=[[F(x) for x in row]+[F(i==j) for j in range(n)] for i,row in enumerate(matrix)]
    determinant=F(1)
    for j in range(n):
        k=next((k for k in range(j,n) if rows[k][j]),None)
        need(k is not None,"invertible helper section")
        if k!=j:rows[j],rows[k]=rows[k],rows[j];determinant=-determinant
        d=rows[j][j];determinant*=d;rows[j]=[v/d for v in rows[j]]
        for i in range(n):
            if i!=j:
                d=rows[i][j];rows[i]=[a-d*b for a,b in zip(rows[i],rows[j])]
    return [row[n:] for row in rows],determinant


def binary_lift(pairs):
    pivots={}
    for x,y in pairs:
        while x:
            p=x.bit_length()-1
            if p not in pivots:pivots[p]=(x,y);break
            a,b=pivots[p];x^=a;y^=b
        else:need(y==0,"consistent binary source symmetry")
    need(len(pivots)==9,"full binary source span")
    columns=[]
    for i in range(9):
        x,y=1<<i,0
        while x:
            a,b=pivots[x.bit_length()-1];x^=a;y^=b
        columns.append(y)
    return tuple(sum(((columns[j]>>i)&1)<<j for j in range(9)) for i in range(9))


def helper_entries(segment,support):
    support=set(support)
    need(not any(e[0]=="residual_adapter" and e[2] in support for e in segment),
         "supported helper has a residual input wrapper")
    entries=[tuple(e) for e in segment if e[0]=="adapter" and e[2] in support]
    need(len(entries)==len(support) and set(entries)==
         {("adapter","old_to_new",j,0) for j in support},"exact identity helper entries")


def load():
    raw=(ROOT/ARCHIVE).read_bytes()
    need(sha256(raw).hexdigest()==ARCHIVE_SHA,"selected archive pin")
    decoded={}
    with tarfile.open(fileobj=io.BytesIO(raw)) as tape:
        for name in ("CANONICAL-WORD.json.gz","LOCAL-PROGRAMS.json.gz","LOCAL-CHECKS.json","CLIFFORD-RECIPES.json"):
            members=[m for m in tape.getmembers() if m.name==PREFIX+name]
            need(len(members)==1 and members[0].isfile(),"unique selected source member")
            data=tape.extractfile(members[0]).read()
            decoded[name]=json.loads(gzip.decompress(data) if name.endswith(".gz") else data)
    word=decoded["CANONICAL-WORD.json.gz"];program=decoded["LOCAL-PROGRAMS.json.gz"]["forward"]
    need(word["frames"][0]==[],"zero frame is the identity")
    encoded=json.dumps(program,sort_keys=True,separators=(",",":"),default=str).encode()
    need(sha256(encoded).hexdigest()==decoded["LOCAL-CHECKS.json"]["forward"]["sha256"],"literal source program")
    first,last=program.index(["phase","entry_adapters"]),program.index(["phase","centers"])
    need((first,last)==(7401,12550) and (word["v"],word["R"],word["h"])==(112,480,9),"selected reader cut")
    centres=tuple(word["centers"])
    need(centres==(92,57,81,224,11,240,9,256),"actual centre fields")
    gates=[e[1] for e in program[first:last] if e[0]=="scalar"]
    need(len(gates)==3451,"complete reader scalar interval")
    rows=[{j:F(1)} for j in centres]
    for gate in reversed(gates):
        at=gate[1][1];need(gate[1][0]=="L" and 0<=at<704,"reader target")
        for row in rows:
            v=row.get(at,F(0))
            if gate[0]=="add":
                need(gate[2][0]=="L" and at!=gate[2][1],"reader source")
                j=gate[2][1];value=row.get(j,F(0))+v*F(gate[3],gate[4])
                if value:row[j]=value
                else:row.pop(j,None)
            else:
                need(gate[0]=="scale","reader scalar opcode")
                if v:row[at]=v*F(gate[2],gate[3])
    columns=[tuple(row.get(j,F(0)) for row in rows) for j in range(704)]
    need(all(not any(columns[j]) for j in range(112,224)),"reader ignores Y")
    helper_support=tuple(j for j in range(224,704) if any(columns[j]))
    need(len(helper_support)==115 and all(word["start"][j]==0 for j in helper_support),"zero-frame dirty helper support")
    helper_entries(program[first:last],helper_support)
    lookup={v:j for j,v in enumerate(columns[:112])}
    need(len(lookup)==112,"distinct data reader columns")
    permutation=[]
    for j in range(112):
        target=tuple(columns[j][i] for i in Q)
        if target in lookup:i,sign=lookup[target],1
        else:
            opposite=tuple(-x for x in target)
            need(opposite in lookup,"signed data column symmetry")
            i,sign=lookup[opposite],-1
        permutation.append((i,sign))
    need(len({i for i,_ in permutation})==112,"data permutation")
    sigma=binary_lift([(word["ports"][j],word["ports"][i]) for j,(i,_) in enumerate(permutation)])
    need(sigma==SIGMA,"derived binary lift")
    need(all((a&b).bit_count()%2==(i==j) for i,a in enumerate(sigma) for j,b in enumerate(sigma)),"orthogonal binary lift")
    need(all(binary(sigma,binary(sigma,binary(sigma,binary(sigma,1<<i))))==1<<i for i in range(9)),"binary fourth power")
    need(any(binary(sigma,binary(sigma,1<<i))!=1<<i for i in range(9)),"binary non-involution")
    for j,(i,_) in enumerate(permutation):
        need({binary(sigma,x) for x in span(word["frames"][word["start"][j]])}==
             span(word["frames"][word["start"][i]]),"data frame covariance")
    for i,j in enumerate(Q):
        need({binary(sigma,x) for x in span(word["frames"][word["center_frames"][j]])}==
             span(word["frames"][word["center_frames"][i]]),"centre frame orientation")
    basis=[[rows[i].get(j,F(0)) for j in PIVOTS] for i in range(8)]
    inv,det=inverse(basis)
    need(det==-32 and {x.denominator for row in inv for x in row}<={1,2},"dyadic dirty helper section")
    return dict(word=word,program=program,gates=gates,reader=rows,columns=columns,
                helper_support=helper_support,basis=basis,inverse=inv,determinant=det,
                permutation=tuple(permutation),sigma=sigma,recipes=decoded["CLIFFORD-RECIPES.json"])
