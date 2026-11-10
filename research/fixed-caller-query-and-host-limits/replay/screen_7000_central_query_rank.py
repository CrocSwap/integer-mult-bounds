"""Rank obstruction to compressing each caller's central four-query block."""
from pathlib import Path
from hashlib import sha256
import json,random
root=Path(__file__).resolve().parent
path=root/"PR7000-CALLER.json"
digest=sha256(path.read_bytes()).hexdigest()
assert digest=="3828d53e80ea97e8b866320f081af20b6b93bfebd58b95b56b85a7afe151af5e"
data=json.loads(path.read_bytes())
src=(root/"jclib_6936.py").read_text()
ns={"__file__":str(root/"jclib_6936.py")}
exec(src[:src.index("CONST =")]+src[src.index("PM ="):src.index("# ---------------------------------------------------------------- own resynthesis")],ns)
prime,IM,replay=ns["PM"],ns["IM"],ns["replay_matrix"]
rng=random.Random(281)
def rank(A):
    basis={}
    for row in A:
        v=dict((i,x) for i,x in enumerate(row) if x)
        while v:
            pivot=min(v)
            if pivot not in basis:
                inv=pow(v[pivot],-1,prime)
                basis[pivot]={j:x*inv%prime for j,x in v.items()}
                break
            scale=v[pivot]
            for j,x in basis[pivot].items():
                t=(v.get(j,0)-scale*x)%prime
                if t:v[j]=t
                else:v.pop(j,None)
    return len(basis),sorted(basis)
report={}
for tag in data["types"]:
    queries=[i for i,e in enumerate(data["events"]) if e[0]==tag and e[1]=="QUERY"]
    interval=[e for e in data["events"][queries[0]:queries[-1]+1] if e[0]==tag]
    assert len(queries)==4
    assert all(e[0]!="J" for e in data["events"][queries[0]:queries[-1]+1])
    trial={**data,"events":interval}
    records=[]
    for q in (1,IM):
        for case in range(2):
            D={j:(1 if case==0 else rng.randrange(2,prime)) for j in range(1,19)}
            P=replay(trial,q,D)
            M=replay(trial,-q%prime,D)
            r,pivots=rank([[(x-y)%prime for x,y in zip(a,b)] for a,b in zip(P,M)])
            records.append({"q":q,"stage_values":D,"rank":r,"pivot_columns":pivots})
    omitted=[]
    for pos,e in enumerate(interval):
        if e[1]!="QUERY":
            continue
        change={**trial,"events":interval[:pos]+interval[pos+1:]}
        D={j:1 for j in range(1,19)}
        before=replay(trial,1,D)
        after=replay(change,1,D)
        assert before!=after
        omitted.append(pos)
    report[tag]={"query_indices":queries,"tested_differences":records,
                 "fixed_interval_query_lower_bound":max(x["rank"] for x in records),
                 "literal_omission_negative_controls":omitted}
    print(tag,"difference ranks",[x["rank"] for x in records],flush=True)
with (root/"PR7000-CENTRAL-QUERY-SIGN-RANK.json").open("x") as out:
    json.dump({"source_sha256":digest,"prime":prime,"branches":report,
               "proof":"Each even ordinary map is equal at q and -q. Each odd query changes its sign, so its two maps differ by a rank-one matrix. A telescoping product difference has rank at most the sum of those ranks. A finite-field specialization where the required difference has rank r proves at least r queries for this fixed interval over the dyadic operator ring.",
               "scope":"Preserves the full input/output operator of the central interval. Moving a QUERY across a J call, changing the boundary operator or making new sign-sensitive native calls is outside the bound."},out,indent=2)
