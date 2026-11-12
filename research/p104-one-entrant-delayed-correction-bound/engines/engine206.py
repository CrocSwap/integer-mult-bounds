"""Independently screen exact owner-free latest-cut banks and bounded spans."""
from bisect import bisect_right
from collections import defaultdict
from fractions import Fraction as Q
from functools import cache
from gzip import decompress
from hashlib import sha256
from json import dumps,loads
from pathlib import Path
from signal import SIGALRM,alarm,signal

ROOT=Path(__file__).resolve().parent
PINS={
 "inputs/7334-WORD.json.gz":"4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
 "inputs/R200.json":"33ba19c30803c39391a23dd8156f55fa06bcd6d3f0553c085ea5b5f0b314cb18",
 "inputs/STAGE1.json":"ae434c63bfc6e28ae3374d246ad086def96ed3dc8ddba3e759eb60af391bfadc",
 "inputs/STAGE2.json":"6de2686c00d1682065fec128f7cc1938a646ebb72f1895c38babb72e7bbb7d6d",
 "inputs/R203.json":"502266e23fd2a12c56ae9c0e2f407882a7681be87be66242922ed573469df1f1",
 "inputs/R204.json":"3e29bd164c607b33df2dac277cad2f9b9bf8fb0848dba269f09ddd483b8d6ce3",
}
HEAD="aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CALLER="07a76c5e2738882c0cb322278e56f6cae3c9885d"
PAYLOAD="9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"


def unique(items):
    d=dict(items)
    assert len(d)==len(items)
    return d


def read(name):
    path=f"inputs/{name}"
    raw=(ROOT/path).read_bytes()
    assert sha256(raw).hexdigest()==PINS[path],path
    return raw


def json(name):
    return loads(read(name),object_pairs_hook=unique)


@cache
def q(value):
    return Q(value)


def stop(*_):
    raise TimeoutError("bounded latest-cut gate")


def touch(e):
    return e[1:3] if e[0] in ("ADD","COPY") else e[1:2]


def freeze(w):
    r200,stage1,stage2,r203,r204=[json(x+".json") for x in ("R200","STAGE1","STAGE2","R203","R204")]
    assert (r200["head"],r200["caller"])==(stage1["head"],stage1["caller"])==(stage2["head"],stage2["caller"])==(r203["head"],r203["caller"])==(HEAD,CALLER)
    assert len(stage1["records"])==967 and len(stage1["screen_survivors"])==243
    first=[x["clocks"] for x in stage1["records"] if x["clocks"][-1]+1==r200["post_move_cut"]]
    groups={"R200":first,"R201":stage2["frozen_keys"],"R203":[c["clocks"] for c in r203["checked"]],
            "R204":[c["clocks"] for c in r204["records"] if c["separator"] is not None]}
    assert [len(x) for x in groups.values()]==[1,6,62,50]
    origins={tuple(key):origin for origin,keys in groups.items() for key in keys}
    assert len(origins)==119
    cases={tuple(row["clocks"]):row for row in stage1["records"] if tuple(row["clocks"]) in origins}
    assert set(cases)==set(origins) and cases[tuple(first[0])]["target_row"]==r200["source"]
    watched={c["role"] for c in cases.values()}
    tape=w["program"]
    contacts=defaultdict(list)
    for t,e in enumerate(tape):
        for r in watched.intersection(touch(e)):
            contacts[r].append(t)
    for key,c in cases.items():
        a,b,d=key
        owner,peer,chart=c["role"],c["peer"],c["chart"]
        assert tape[a][:2]==["MOVE",owner] and tape[b][:3]==["ADD",owner,peer]
        assert tape[d][0:2]==["MOVE",owner] and tape[d][3]==chart
        j=bisect_right(contacts[owner],d)
        assert tuple(contacts[owner][j-3:j])==key
        c["cut"]=contacts[owner][j] if j<len(contacts[owner]) else len(tape)
        assert c["cut"]>d
        c["old_origin"]=origins[key]
        assert q(c["gross"][0])>0
    return cases


def axpy(dst,src,c):
    for i,v in src.items():
        z=dst.get(i,0)+c*v
        if z:
            dst[i]=z
        else:
            dst.pop(i,None)


def proportional(target,row):
    if target.keys()!=row.keys():
        return None
    pivot=min(target)
    c=target[pivot]/row[pivot]
    return c if all(c*row[i]==x for i,x in target.items()) else None


def sort_key(record):
    return -q(record["gross"][0]),record["bank_count"],tuple(record["clocks"])


def scan(w,cases,results,span_pool):
    n,m=w["public"],w["owned_fields"]
    rows=[{i:Q(1)} for i in range(n)]+[{} for _ in range(m)]
    charts=w["initial"]+[None]*m
    bank=defaultdict(set)
    for i,c in enumerate(charts[:n]):
        bank[c].add(i)
    source=defaultdict(list)
    cuts=defaultdict(list)
    for c in cases.values():
        source[c["clocks"][1]].append(c)
        cuts[c["cut"]].append(c)
    fresh=set()
    old_rows={}
    tape=w["program"]
    for t in range(max(cuts)+1):
        for c in source.get(t,()):
            row=rows[c["peer"]]
            assert row and row=={int(i):q(x) for i,x in c["target_row"].items()}
            old_rows[tuple(c["clocks"])]=row
        for c in cuts.get(t,()):
            key=tuple(c["clocks"])
            target=old_rows.pop(key)
            dst=c["role"]
            chart=c["chart"]
            assert charts[dst]==chart
            donors=[(r,rows[r]) for r in sorted(bank[chart]-{dst})]
            hit=None
            missing=set(target)
            for r,row in donors:
                ratio=proportional(target,row)
                if hit is None and ratio is not None:
                    hit=[r,ratio,ratio*q(tape[key[1]][3])]
                missing.difference_update(row)
            result={"clocks":key,"old_origin":c["old_origin"],"role":dst,"chart":chart,
                    "source_role":c["peer"],"cut":t,"observer":tape[t] if t<len(tape) else None,
                    "gross":c["gross"],"bank_count":len(donors),"literal_donor_ratio_coefficient":hit,
                    "coordinate_missing":len(missing),
                    "first_missing":[min(missing),target[min(missing)]] if missing else None}
            results.append(result)
            if hit is None and not missing:
                span_pool.append((result,target,donors))
                span_pool.sort(key=lambda x:sort_key(x[0]))
                del span_pool[3:]
        if t==len(tape):
            break
        op,d,*args=tape[t]
        if op=="MOVE":
            a,b,owned=args
            assert charts[d]==a and owned==(d>=n)
            bank[a].remove(d); bank[b].add(d)
            charts[d]=b
        elif op=="INIT":
            assert d>=n and charts[d] is None and not rows[d]
            charts[d]=args[0]
            bank[args[0]].add(d)
            fresh.add(d)
            continue
        elif op=="CLEAR":
            assert d>=n and charts[d]==args[0]
            bank[args[0]].remove(d)
            charts[d],rows[d]=None,{}
        elif op=="SCALE":
            a,f=args
            assert charts[d]==f
            rows[d]={i:q(a)*v for i,v in rows[d].items()}
        else:
            s,a,f=args
            assert op in ("ADD","COPY") and d!=s and charts[d]==charts[s]==f
            assert op!="COPY" or (d>=n and d in fresh and not rows[d])
            row=rows[d].copy()
            axpy(row,rows[s],q(a))
            rows[d]=row
        fresh.discard(d)
    assert not old_rows


def dot(row,x):
    return sum(v*x.get(i,0) for i,v in row.items())


def exact_span(target,donors):
    basis={}
    for role,row in donors:
        w,c=row.copy(),{role:Q(1)}
        for p,(b,a) in sorted(basis.items()):
            if p in w:
                v=-w[p]
                axpy(w,b,v); axpy(c,a,v)
        if w:
            p=min(w)
            k=w[p]
            basis[p]=({i:v/k for i,v in w.items()},{i:v/k for i,v in c.items()})
    rest,c=target.copy(),{}
    for p,(b,a) in sorted(basis.items()):
        if p in rest:
            v=rest[p]
            axpy(rest,b,-v); axpy(c,a,v)
    if not rest:
        rows=dict(donors)
        combined={}
        for r,v in c.items():
            axpy(combined,rows[r],v)
        assert combined==target
        return {"rank":len(basis),"span":True,"coefficients":c}
    j=min(rest)
    x={j:Q(1)}
    for p,(b,_) in sorted(basis.items(),reverse=True):
        v=-dot(b,x)
        if v:
            x[p]=v
    assert all(dot(row,x)==0 for _,row in donors)
    assert dot(target,x)==rest[j]!=0
    return {"rank":len(basis),"span":False,"separator":x,"source_value":rest[j]}


def main():
    assert __debug__
    signal(SIGALRM,stop)
    raw=decompress(read("7334-WORD.json.gz"))
    assert sha256(raw).hexdigest()==PAYLOAD
    w=loads(raw,object_pairs_hook=unique)
    assert (w["public"],w["owned_fields"],len(w["program"]))==(1501,68,76466)
    cases=freeze(w)
    assert proportional({1:Q(2)},{1:Q(1)})==2 and proportional({1:Q(1)},{2:Q(1)}) is None
    results,pool=[],[]
    capped=False
    alarm(25)
    try:
        scan(w,cases,results,pool)
    except TimeoutError:
        capped=True
    finally:
        alarm(0)
    visited={tuple(c["clocks"]) for c in results}
    assert capped or visited==set(cases)
    literal=sorted((c for c in results if c["literal_donor_ratio_coefficient"]),key=sort_key)
    complete_spans=[]
    span_capped=False
    attempted_keys=[]
    if not capped and not literal:
        alarm(30)
        try:
            for rec,target,donors in pool:
                attempted_keys.append(rec["clocks"])
                proof=exact_span(target,donors)
                complete_spans.append({"clocks":rec["clocks"],"proof":proof})
                if proof["span"]:
                    break
        except TimeoutError:
            span_capped=True
        finally:
            alarm(0)
    print(dumps({"head":HEAD,"caller":CALLER,"pins":PINS,"case_cap":119,"seconds_cap":25,
                 "capped":capped,"results":results,"unvisited":sorted(set(cases)-visited),
                 "literal_survivor_count":len(literal),"literal_first_to_advance":literal[0] if literal else None,
                 "coordinate_survivor_count":sum(r["coordinate_missing"]==0 for r in results),
                 "span_case_cap":3,"span_seconds_cap":30,"span_capped":span_capped,
                 "span_attempted":attempted_keys,"span_complete":complete_spans},
                default=str,sort_keys=True,indent=2))
    if capped or span_capped:
        raise SystemExit(2)


if __name__=="__main__":
    main()
