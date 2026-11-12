"""Check exact row certificates independently using forward support masks."""
from collections import defaultdict
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
from json import dumps,loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM,alarm,signal

R=Path(__file__).resolve().parent


def stop(*_):
    raise TimeoutError("25-second forward readback cap")


def main():
    assert __debug__
    signal(SIGALRM,stop)
    alarm(25)
    pins={}
    for line in (R/"PINS").read_text().splitlines():
        h,p=line.split()
        assert p not in pins and sha256((R/p).read_bytes()).hexdigest()==h
        pins[p]=h
    one=loads((R/"inputs/STAGE1.json").read_bytes())
    two=loads((R/"inputs/STAGE2.json").read_bytes())
    assert two["stage1_sha256"]==pins["inputs/STAGE1.json"]
    raw=decompress((R/"inputs/7334-WORD.json.gz").read_bytes())
    assert sha256(raw).hexdigest()=="9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
    w=loads(raw)
    f=run_path(str(R/"bank_gate.py"))
    add,scalar=f["add"],f["scalar"]
    n,m=w["public"],w["owned_fields"]
    rows=[{i:Q(1)} for i in range(n)]+[{} for _ in range(m)]
    masks=[1<<i for i in range(n)]+[0]*m
    charts=w["initial"]+[None]*m
    reads,tails={},{}
    for row in one["records"]:
        a,b,c=row["clocks"]
        assert b not in reads and c not in tails
        reads[b]=tails[c]=row
    check2={tuple(r["clocks"]):r for r in two["checked"]}
    src={}
    checked=[]
    for i,(op,r,*a) in enumerate(w["program"][:max(tails)+1]):
        if i in reads:
            peer=reads[i]["peer"]
            src[i]=rows[peer].copy(),masks[peer]
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
            masks[r]=0
        elif op=="SCALE":
            assert charts[r]==a[1] and scalar(a[0])
            rows[r]={j:x*scalar(a[0]) for j,x in rows[r].items()}
        else:
            s,k,c=a
            assert op in ("ADD","COPY") and charts[r]==charts[s]==c and r!=s
            assert op!="COPY" or not rows[r]
            add(rows[r],rows[s],scalar(k))
            masks[r]=sum(1<<j for j in rows[r])
        if i not in tails:
            continue
        t=tails[i]
        key=tuple(t["clocks"])
        bank=[j for j,c in enumerate(charts) if c==t["chart"] and j!=t["role"]]
        row,mask=src.pop(key[1])
        assert {str(j):str(v) for j,v in row.items()}==t["target_row"]
        assert len(bank)==t["bank_count"]
        union=0
        for j in bank:
            union|=masks[j]
        missing=mask&~union
        assert missing.bit_count()==t["missing_count"]
        j=(missing&-missing).bit_length()-1 if missing else None
        witness=[j,str(row[j])] if missing else None
        assert witness==t["missing_witness"]
        if key in check2:
            data=check2[key]
            x={int(j):Q(v) for j,v in data["decision"]["separating_covector"].items()}
            def dot(r):
                return sum(r.get(j,0)*v for j,v in x.items())
            assert bank==data["bank_roles"] and all(not dot(rows[j]) for j in bank)
            assert dot(row)==Q(data["decision"]["separated_target"])!=0
        checked.append([key,witness])
    assert len(checked)==967 and not src and len(check2)==6
    alarm(0)
    print(dumps({"pins":pins,"case_cap":967,"seconds_cap":25,
                 "checked":len(checked),"coordinate_excluded":sum(x[1] is not None for x in checked),
                 "dual_checks":len(check2)},indent=2,sort_keys=True))


if __name__=="__main__":
    main()
