"""Check entry-chart rank-one replay for every favorably priced owned descent."""
from collections import Counter,defaultdict
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
from json import dumps,loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM,alarm,signal
from time import monotonic

ROOT=Path(__file__).resolve().parent
PINS={
    "inputs/7334-WORD.json.gz":"4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
    "inputs/PRICE.json":"ec9a60268731327b5628fea15510bb2a5b663c67d0a308ef6db5f077045c9ce3",
    "inputs/reverse_span.py":"f8b48f2ed99d003e20f5b3fb2270603c4edbc3ce9a01484102816aa2710ce9ff",
    "inputs/R197.json":"c80ea309c887721528bbd68c591b2358dc8613d9fb32b305abd4b39017645317",
    "inputs/R92-PRICE.json":"05d7a5ebdd2eeedd6c8f534e8e2eeac22484daf9f387f4a6b88cc9eed22a6b8f",
    "inputs/pricing.py":"f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
}
HEAD="aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CALLER="07a76c5e2738882c0cb322278e56f6cae3c9885d"
PAYLOAD="9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
CASES,SECONDS=8,25


def unique(items):
    data=dict(items)
    assert len(data)==len(items),"duplicate key"
    return data


def read(name):
    raw=(ROOT/name).read_bytes()
    assert sha256(raw).hexdigest()==PINS[name],name
    return raw


def stop(*_):
    raise TimeoutError("25-second exact entry bank cap")


def main():
    assert __debug__
    signal(SIGALRM,stop)
    alarm(SECONDS)
    until=monotonic()+SECONDS-1
    old,price,base=[loads(read(p),object_pairs_hook=unique) for p in
                    ("inputs/R197.json","inputs/PRICE.json","inputs/R92-PRICE.json")]
    assert (old["head"],old["caller"])==(price["head"],price["caller"])==(HEAD,CALLER)
    assert (base["head"],base["caller_head"])==(HEAD,CALLER)
    raw=decompress(read("inputs/7334-WORD.json.gz"))
    assert sha256(raw).hexdigest()==PAYLOAD
    w=loads(raw,object_pairs_hook=unique)
    n,m,tape,frames,initial=[w[k] for k in ("public","owned_fields","program","frames","initial")]
    assert (n,m,len(tape),len(initial))==(1501,68,76466,1501) and not frames[3]
    chart_stock=Counter(initial)
    assert chart_stock[3]==1060
    keys,descents,first_contact=[],[],{}
    for clock,(op,role,*args) in enumerate(tape):
        for r in (role,args[0]) if op in ("ADD","COPY") else (role,):
            if r>=n:
                first_contact.setdefault(r,clock)
        if op=="MOVE" and role>=n:
            source,target,owned=args
            rank=len(frames[source])-len(frames[target])
            if rank>0:
                descents.append(clock)
                if len(frames[target])==1 and rank>1:
                    assert owned
                    keys.append([clock,role,source,target,rank])
    assert len(keys)==CASES and len(descents)==24
    assert Counter(k[-1] for k in keys)=={2:4,4:3,5:1}
    assert any(k[0]==old["clock"] and k[1]==old["owner"] for k in keys)
    for p in ("inputs/reverse_span.py","inputs/pricing.py"):
        read(p)
    reducer=run_path(str(ROOT/"inputs/reverse_span.py"))["transpose_prefix"]
    cost=run_path(str(ROOT/"inputs/pricing.py"))["cost"]
    cross=Q(base["old_crossing_upper"])
    req=defaultdict(list,{key[0]:[(key[1],i)] for i,key in enumerate(keys)})
    rows=reducer(w,req,CASES,until)
    result=[]
    for key,(ints,d) in zip(keys,rows,strict=True):
        clock,role,source,target,rank=key
        row={i:Q(x,d) for i,x in ints.items()}
        assert all(0<=i<n for i in row)
        allowed={3,target}
        outside={i:x for i,x in row.items() if initial[i] not in allowed}
        if clock==old["clock"]:
            assert row=={int(i):Q(v) for i,v in old["row"].items()}
        j=min(outside) if outside else None
        quote=cost({rank:17,1:-17},cross)
        assert quote[0]>0
        result.append({"key":key,"row":row,"support_groups":Counter(initial[i] for i in row),
                       "entry_destination_count":chart_stock[target],"outside_count":len(outside),
                       "witness":[j,row[j],initial[j]] if outside else None,
                       "vacant_entry_shadows":[i for i in range(n,n+m) if first_contact.get(i,len(tape))>clock],
                       "gross":quote,"status":"outside entry support" if outside else "entry support survives"})
    whole=Counter({1:-17*len(keys)})
    whole.update({r:17*c for r,c in Counter(k[-1] for k in keys).items()})
    assert sum(r*c for r,c in whole.items())==price["eight_slot_raw_relaxation_below"]==289
    interval=cost(whole,cross)
    assert interval[1]<289
    alarm(0)
    print(dumps({"head":HEAD,"caller":CALLER,"pins":PINS,"case_cap":CASES,"new_case_cap":7,
                 "runner_cap_seconds":SECONDS,"source_coordinates":n,"owned_descents":24,
                 "entry_chart3_count":chart_stock[3],"whole_optimistic_gross":interval,
                 "results":result,"survivors":[r["key"] for r in result if not r["outside_count"]],
                 "unvisited":[],"control":"R197 full row equality"},sort_keys=True,indent=2,default=str))


if __name__=="__main__":
    main()
