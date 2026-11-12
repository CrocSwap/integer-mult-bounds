"""Independently check exact historical-bank separator inputs on literal scalars."""
from argparse import ArgumentParser
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
    "inputs/STAGE1.json":"ae434c63bfc6e28ae3374d246ad086def96ed3dc8ddba3e759eb60af391bfadc",
    "inputs/R203.json":"502266e23fd2a12c56ae9c0e2f407882a7681be87be66242922ed573469df1f1",
}
PAYLOAD="9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
HEAD="aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CALLER="07a76c5e2738882c0cb322278e56f6cae3c9885d"
CASES,SECONDS=12,25


def unique(items):
    data=dict(items)
    assert len(data)==len(items),"duplicate key"
    return data


def read(path,pins):
    raw=(ROOT/path).read_bytes()
    assert sha256(raw).hexdigest()==pins[path],path
    return raw


def stop(*_):
    raise TimeoutError("25-second independent exact input cap")


@cache
def scalar(text):
    return Q(text)


def history(w,cases):
    n,m=w["public"],w["owned_fields"]
    state=w["final"]+[None]*m
    bank={}
    cuts={c["clocks"][2]:c for c in cases}
    tape=w["program"]
    for t in range(len(tape)-1,-1,-1):
        if t in cuts:
            c=cuts[t]
            assert state[c["role"]]==c["chart"]
            roles=[i for i,v in enumerate(state) if v==c["chart"] and i!=c["role"]]
            assert len(roles)==c["bank_count"]
            assert sha256(dumps(roles).encode()).hexdigest()==c["bank_role_sha256"]
            bank[tuple(c["clocks"])]=roles
        op,d,*a=tape[t]
        if op=="MOVE":
            assert state[d]==a[1] and a[2]==(d>=n)
            state[d]=a[0]
        elif op=="INIT":
            assert d>=n and state[d]==a[0]
            state[d]=None
        elif op=="CLEAR":
            assert d>=n and state[d] is None
            state[d]=a[0]
        else:
            assert op in ("ADD","COPY","SCALE") and state[d]==a[-1]
            if op!="SCALE":
                assert state[a[0]]==a[-1] and a[0]!=d
    assert state==w["initial"]+[None]*m
    return bank


def forward(w,cases,probes,banks):
    n,m=w["public"],w["owned_fields"]
    readings=defaultdict(list)
    values=[{} for _ in range(n+m)]
    for idx,(case,probe) in enumerate(zip(cases,probes,strict=True)):
        left,mid,right=case["clocks"]
        readings[mid].append((idx,"source",case["peer"]))
        readings[right+1].append((idx,"bank",banks[tuple(case["clocks"])]))
        for k,v in probe.items():
            assert 0<=k<n and v
            values[k][idx]=v
    results=[{} for _ in cases]
    state=w["initial"]+[None]*m
    fresh=set()
    for t,(op,d,*a) in enumerate(w["program"][:max(readings)+1]):
        for idx,kind,roles in readings[t]:
            if kind=="source":
                results[idx][kind]=values[roles].get(idx,0)
            else:
                nonzero=[[r,values[r][idx]] for r in roles if idx in values[r]]
                results[idx]["bank_nonzero"]=nonzero
                results[idx]["bank_count"]=len(roles)
        if op=="MOVE":
            assert state[d]==a[0] and a[2]==(d>=n)
            state[d]=a[1]
        elif op=="INIT":
            assert d>=n and state[d] is None and not values[d]
            state[d]=a[0]
            fresh.add(d)
            continue
        elif op=="CLEAR":
            assert d>=n and state[d]==a[0]
            state[d]=None
            values[d]={}
        elif op=="SCALE":
            assert state[d]==a[1] and scalar(a[0])
            values[d]={i:scalar(a[0])*x for i,x in values[d].items()}
        else:
            s,k,c=a
            assert op in ("ADD","COPY") and state[s]==state[d]==c and s!=d
            assert op!="COPY" or (d>=n and d in fresh and not values[d])
            for i,v in values[s].items():
                updated=values[d].get(i,0)+scalar(k)*v
                if updated:
                    values[d][i]=updated
                else:
                    values[d].pop(i,None)
        fresh.discard(d)
    return results,max(readings)+1


def main():
    assert __debug__
    cli=ArgumentParser(description=__doc__)
    cli.add_argument("--lead-sha",required=True)
    cli.add_argument("--remaining",action="store_true")
    args=cli.parse_args()
    signal(SIGALRM,stop)
    alarm(SECONDS)
    pins=PINS|{"inputs/R204-LEAD.json":args.lead_sha}
    a,old,new=[loads(read(p,pins),object_pairs_hook=unique) for p in
               ("inputs/STAGE1.json","inputs/R203.json","inputs/R204-LEAD.json")]
    assert (a["head"],a["caller"])==(old["head"],old["caller"])==(HEAD,CALLER)
    assert not old["unvisited"] and len(old["outside_small_bank_unresolved"])==175
    raw=decompress(read("inputs/7334-WORD.json.gz",pins))
    assert sha256(raw).hexdigest()==PAYLOAD
    w=loads(raw,object_pairs_hook=unique)
    assert (w["public"],w["owned_fields"],len(w["program"]))==(1501,68,76466)
    universe={tuple(c) for c in old["outside_small_bank_unresolved"]}
    all_records=[c for c in new["records"] if c["separator"] is not None]
    assert len(all_records)==50 and new["capped"] and new["unvisited"]==125
    got=all_records[CASES:] if args.remaining else all_records[:CASES]
    cap=38 if args.remaining else CASES
    assert len(got)==cap and len({tuple(c["clocks"]) for c in got})==cap
    selected={tuple(c["clocks"]):c for c in a["screen_survivors"] if tuple(c["clocks"]) in universe}
    cases=[selected[tuple(c["clocks"])] for c in got]
    probes=[{int(i):Q(v) for i,v in c["separator"]["input"].items()} for c in got]
    banks=history(w,cases)
    values,events=forward(w,cases,probes,banks)
    checks=[]
    for c,r,v,x in zip(cases,got,values,probes,strict=True):
        assert c["bank_count"]==v["bank_count"]==r["bank_count"]
        assert not v["bank_nonzero"] and v["source"]==Q(r["separator"]["source_value"])!=0
        assert sum(Q(c["target_row"].get(str(i),0))*a for i,a in x.items())==v["source"]
        checks.append({"clocks":c["clocks"],"peer":c["peer"],"role":c["role"],"chart":c["chart"],
                       "bank_count":v["bank_count"],"input":x,"source_value":v["source"]})
    alarm(0)
    print(dumps({"head":HEAD,"caller":CALLER,"pins":pins,"case_cap":cap,"seconds_cap":SECONDS,
                 "checked":checks,"historical_bank_rows_verified":sum(c["bank_count"] for c in checks),
                 "forward_prefix_events":events,"reverse_chart_events":len(w["program"]),
                 "unresolved_in_sample":0},sort_keys=True,indent=2,default=str))


if __name__=="__main__":
    main()
