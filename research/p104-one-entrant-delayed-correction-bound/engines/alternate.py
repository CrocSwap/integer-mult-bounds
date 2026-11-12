from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
from json import dumps,loads
from pathlib import Path
from runpy import run_path
R=Path(__file__).resolve().parent
b=run_path(str(R/"bank_gate.py"))
add,scalar=b["add"],b["scalar"]
def trace(w):
    n,m=w["public"],w["owned_fields"]
    rows=[{i:Q(1)} for i in range(n)]+[{} for _ in range(m)]
    charts=w["initial"]+[None]*m
    for i,(op,r,*a) in enumerate(w["program"][:43486]):
        if i==42063:
            source=rows[67].copy()
        if op=="MOVE":
            assert charts[r]==a[0]
            charts[r]=a[1]
        elif op=="INIT":
            assert charts[r] is None and not rows[r]
            charts[r]=a[0]
        elif op=="CLEAR":
            assert charts[r]==a[0]
            charts[r]=None
            rows[r].clear()
        elif op=="SCALE":
            assert charts[r]==a[1]
            rows[r]={j:x*scalar(a[0]) for j,x in rows[r].items()}
        else:
            s,k,c=a
            assert op in ("ADD","COPY") and charts[r]==charts[s]==c and r!=s
            assert op!="COPY" or not rows[r]
            add(rows[r],rows[s],scalar(k))
    return source,{i:rows[i] for i,c in enumerate(charts) if c==930 and i!=117}


raw=(R/"inputs/7334-WORD.json.gz").read_bytes()
assert sha256(raw).hexdigest()==b["PINS"]["inputs/7334-WORD.json.gz"]
target,bank=trace(loads(decompress(raw)))
probe={1287:Q(1),1340:Q(1,8)}
def dot(row):
    return sum(row.get(j,0)*a for j,a in probe.items())
assert len(bank)==5 and 238 in bank and all(not dot(row) for row in bank.values()) and dot(target)
print(dumps({"clocks":[42061,42063,43484],"probe":probe,"entrant":238,
             "bank_count":len(bank),"target_value":dot(target)},default=str,sort_keys=True))
