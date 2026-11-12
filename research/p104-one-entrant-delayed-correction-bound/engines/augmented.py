from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
from json import dumps,loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM,alarm,signal
R=Path(__file__).resolve().parent
b=run_path(str(R/"bank_gate.py"))
add,scalar,solve=b["add"],b["scalar"],b["solve"]
test=run_path(str(R/"peel.py"))["test"]
def trace(w):
    n,m=w["public"],w["owned_fields"]
    rows=[{i:Q(1)} for i in range(n)]+[{} for _ in range(m)]
    charts=w["initial"]+[None]*m
    for i,(op,r,*a) in enumerate(w["program"][:46025]):
        if i==40398:
            source=rows[980].copy()
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
    return source,{i:rows[i] for i,c in enumerate(charts) if c==127 and i!=822}


def stop(*_):
    raise TimeoutError("30-second single augmented bank cap")
signal(SIGALRM,stop)
alarm(30)
raw=(R/"inputs/7334-WORD.json.gz").read_bytes()
assert sha256(raw).hexdigest()==b["PINS"]["inputs/7334-WORD.json.gz"]
w=loads(decompress(raw))
target,bank=trace(w)
assert len(bank)==203 and 417 in bank
rank,single,sep=test(target,bank)
coeff=None
if sep is None:
    _,coeff,_=solve(target,bank)
alarm(0)
print(dumps({"clocks":[40396,40398,46023],"rank":rank,"singletons":single,
             "seconds_cap":30,"separator":sep,"coefficients":coeff},sort_keys=True,indent=2,default=str))
