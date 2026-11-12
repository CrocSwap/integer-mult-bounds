"""Fixed-paid exact 3+6 split support on chart 1089."""
from collections import Counter
from gzip import decompress
from hashlib import sha256
import json
from pathlib import Path
from runpy import run_path
import sys
from time import monotonic

HEAD="aaeec8c0acf01e99a5f331ef363a698d9c084ace"
WORD="4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a"
PRICE="3659931ae9d38e58629ad111c21a97e1e41175bf2e181c7084ed5645892cb146"
PINS={"paired_rank.py":"d1b7c34e6f8c8a7b810414762015e6e300a8292422af66ff671ae09741141f09",
      "paired_support.py":"38c796cbe1a73f386177faf88cd53294d4b911f6cde7fd47cd9fcef3b558373f"}
KEYS=[[t,1089,1081] for t in range(44588,44600)]


def checked(path,digest):
    b=path.read_bytes()
    if sha256(b).hexdigest()!=digest:
        raise ValueError(f"changed dependency: {path.name}")
    return b


def banks_at(word,deadline):
    n=word["public"]
    active=word["initial"]+[None]*word["owned_fields"]
    banks,owned={},{}
    for t,e in enumerate(word["program"]):
        if (t%128==0 or t>=44588) and monotonic()>=deadline:
            break
        if 44588<=t<=44599:
            banks[t]=[i for i in range(n) if active[i]==1089]
            owned[t]=[i for i in range(n,len(active)) if active[i]==1089]
            assert 1081 in banks[t]
        if t==44599:
            break
        op,d,*p=e
        if op=="MOVE":
            assert active[d]==p[0] and p[2]==(d>=n)
            active[d]=p[1]
        elif op=="INIT":
            assert active[d] is None
            active[d]=p[0]
        elif op=="CLEAR":
            assert active[d]==p[0]
            active[d]=None
        else:
            assert active[d]==p[-1]
            if op in ("ADD","COPY"):
                assert active[p[0]]==p[-1]
            else:
                assert op=="SCALE"
    return banks,owned


def main():
    root=Path(sys.argv[1])
    price=json.loads(checked(root/"price/PRICE.json",PRICE))
    assert price["head"]==HEAD and price["stock"]==KEYS
    assert price["productive_delta"]=={"3":17,"6":17,"9":-17} and not price["paid_delta"]
    engines=[]
    for name,digest in PINS.items():
        path=root/"inputs"/name
        checked(path,digest)
        engines.append(run_path(str(path)))
    rank,solve=engines
    controls=solve["controls"]()
    word=json.loads(decompress(checked(root/"inputs/7334-WORD.json.gz",WORD)),object_pairs_hook=solve["unique"])
    cohort,_=solve["initial_groups"](word)
    assert len(cohort)==615 and 1081 in cohort and 319 not in cohort
    assert word["program"][44599][:4]==["MOVE",1081,1089,207]
    assert [len(word["frames"][i]) for i in (3,1089,127)]==[0,3,9]
    deadline=monotonic()+18
    banks,owned=banks_at(word,deadline)
    f=rank["side"](word,banks,cohort,deadline,False) if banks else {}
    decisions,live={},{}
    for t,rows in f.items():
        row=dict(public_bank=banks[t],owned_bank_excluded=owned[t],
                 prefix_kernel_dim=len(rows),prefix_exterior_rank=len(banks[t])-len(rows),
                 nonzero_pure_prefix=sum(bool(c) for _,c in rows))
        if any(c for _,c in rows):
            live[t]=row
        else:
            decisions[t]=row|dict(decision="no nonzero pure prefix")
    if live:
        deadline=monotonic()+32
        suffix=rank["side"](word,{t:banks[t] for t in live},cohort,deadline,True)
        for t,rows in sorted(suffix.items()):
            if monotonic()>=deadline:
                break
            row=live[t]|dict(suffix_kernel_dim=len(rows),suffix_exterior_rank=len(banks[t])-len(rows))
            if not any(d for _,d in rows):
                decisions[t]=row|dict(decision="no nonzero pure suffix")
                continue
            try:
                w=solve["paired"](f[t],rows,deadline)
            except solve["Capped"]:
                break
            if w is None:
                decisions[t]=row|dict(decision="no unit pairing")
                continue
            decisions[t]=row|dict(decision="exact rational support only",
                witness={k:{j:str(c) for j,c in v.items()} for k,v in w.items()})
    rows=[dict(key=k,**decisions[k[0]]) for k in KEYS if k[0] in decisions]
    unvisited=[k for k in KEYS if k[0] not in decisions]
    print(json.dumps(dict(head=HEAD,word_sha256=WORD,price_sha256=PRICE,engines_sha256=PINS,
        controls=controls,case_cap=12,prefix_seconds_cap=18,exact_followup_seconds_cap=32,
        prefix_survivors=[k for k in KEYS if k[0] in live],
        counts=Counter(r["decision"] for r in rows),decisions=rows,unvisited=unvisited,
        status="CAPPED" if unvisited else "EXHAUSTED"),indent=2,sort_keys=True))


if __name__=="__main__":
    main()
