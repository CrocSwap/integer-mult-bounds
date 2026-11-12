"""Reuse each old exact separator on the sole entrant at the moved cut."""
from collections import defaultdict
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
from json import dumps,loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM,alarm,signal

ROOT=Path(__file__).resolve().parent
ENGINE="247fb32afea034e934441934d117fceb57edeeecb4ae11a1b9e6e88b0d6bf420"
R206="a5ad6b1d6a0aeb376ca9b945de03f44e40fb177225133b0fdd3a6466313b2fa3"


def checked(path,digest):
    raw=(ROOT/path).read_bytes()
    assert sha256(raw).hexdigest()==digest,path
    return raw


def old_duals(f):
    out={}
    for name in ("STAGE2.json","R203.json"):
        for row in f["json"](name)["checked"]:
            d=row["decision"]
            assert d["status"]=="exact_rank_exclusion"
            out[tuple(row["clocks"])]=(d["separating_covector"],d["separated_target"])
    for row in f["json"]("R204.json")["records"]:
        d=row["separator"]
        if d is not None:
            out[tuple(row["clocks"])]=(d["input"],d["source_value"])
    assert len(out)==118
    return out


def probe(w,scope):
    n,m=w["public"],w["owned_fields"]
    values=[{} for _ in range(n+m)]
    look=defaultdict(list)
    for j,r in enumerate(scope):
        for i,v in r["input"].items():
            assert 0<=i<n and v
            values[i][j]=v
        look[r["cut"]].append((j,r))
    tape=w["program"]
    for t in range(max(look)+1):
        for j,r in look.get(t,()):
            x=values[r["entrant_role"]].get(j,0)
            r["entrant_value"]=x
            r["inherited_exclusion"]=not x
        op,d,*a=tape[t]
        if op in ("INIT","CLEAR"):
            values[d]={}
        elif op=="SCALE":
            c=Q(a[0])
            values[d]={k:c*v for k,v in values[d].items()}
        elif op in ("COPY","ADD"):
            if op=="COPY":
                assert not values[d]
            s,c,_=a
            c=Q(c)
            for k,v in values[s].items():
                value=values[d].get(k,0)+c*v
                if value:
                    values[d][k]=value
                else:
                    values[d].pop(k,None)
        else:
            assert op=="MOVE"


def stop(*_):
    raise TimeoutError("bounded inherited-separator gate")


def main():
    assert __debug__
    signal(SIGALRM,stop)
    checked("engine206.py",ENGINE)
    f=run_path(str(ROOT/"engine206.py"))
    r206=loads(checked("inputs/R206.json",R206),object_pairs_hook=f["unique"])
    assert not r206["capped"] and not r206["span_capped"] and len(r206["results"])==119
    source=decompress(f["read"]("7334-WORD.json.gz"))
    assert sha256(source).hexdigest()==f["PAYLOAD"]
    w=loads(source,object_pairs_hook=f["unique"])
    prior=old_duals(f)
    already={tuple(x["clocks"]) for x in r206["span_complete"] if not x["proof"]["span"]}
    scope=[]
    for c in r206["results"]:
        key=tuple(c["clocks"])
        if c["cut"]==key[-1]+1 or key in already:
            continue
        assert c["cut"]==key[-1]+2 and c["coordinate_missing"]==0
        entrant=w["program"][key[-1]+1]
        assert entrant[0]=="MOVE" and entrant[3]==c["chart"] and entrant[1]!=c["role"]
        witness,value=prior[key]
        x={int(i):Q(v) for i,v in witness.items()}
        assert Q(value)
        scope.append({**c,"entrant_role":entrant[1],"entrant_event":entrant,"input":x,"old_source_value":Q(value)})
    assert len(scope)==12
    capped=False
    alarm(20)
    try:
        probe(w,scope)
    except TimeoutError:
        capped=True
    finally:
        alarm(0)
    completed=[x for x in scope if "entrant_value" in x]
    unresolved=[x for x in completed if x["entrant_value"]]
    span,span_capped=None,False
    if unresolved and not capped:
        rec=min(unresolved,key=f["sort_key"])
        key=tuple(rec["clocks"])
        alarm(30)
        try:
            found,pool=[],[]
            cases=f["freeze"](w)
            f["scan"](w,{key:cases[key]},found,pool)
            assert len(pool)==1
            _,row,donors=pool[0]
            span={"clocks":key,"result":f["exact_span"](row,donors)}
        except TimeoutError:
            span_capped=True
        finally:
            alarm(0)
    print(dumps({"head":f["HEAD"],"caller":f["CALLER"],"r206_sha256":R206,"engine_sha256":ENGINE,
                 "case_cap":12,"seconds_cap":20,"capped":capped,"records":scope,
                 "inherited_exclusions":sum(x["inherited_exclusion"] for x in completed),
                 "unvisited":[x["clocks"] for x in scope if "entrant_value" not in x],
                 "pre_span_unresolved":[x["clocks"] for x in unresolved],
                 "span_case_cap":1,"span_seconds_cap":30,"span_capped":span_capped,"span":span},
                 default=str,indent=2,sort_keys=True))
    if capped or span_capped:
        raise SystemExit(2)


if __name__=="__main__":
    main()
