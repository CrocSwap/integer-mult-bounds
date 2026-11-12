"""Modular signed reflection products for three/four Type B phase transfers."""
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
from runpy import run_path
import sys
from time import monotonic

HEAD="aaeec8c0acf01e99a5f331ef363a698d9c084ace"
PRICE="6bf60b702f2d8b879fe0fca3c6c93dc5a580ae264f19eb87d27d0268d29b63bf"
KEYS="2bb549fc7738efb4a159181094c771218903099be624a85474599683b73acde2"
PINS={"inputs/CALLER.json":"255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
      "inputs/two_phase.py":"ad3b5efd85a56c6c60c747cf45cbd1b7174ab9a714142ab069648261bcbf6631",
      "inputs/screen.py":"cdf54b266ac31fd0efe544badbb9840598d4c63c4d3cd363f60ae9a74cc4b256"}
P=65521


def checked(path,want):
    b=path.read_bytes()
    if sha256(b).hexdigest()!=want:
        raise ValueError(f"changed dependency {path.name}")
    return b


def sparse(v):
    return [(i,x) for i,x in enumerate(v) if x]


def witness(refl,clocks,vec):
    v=vec.copy()
    for k in clocks:
        col,row=refl[k]
        t=-2*sum(a*v[i] for i,a in row)%P
        if t:
            for i,a in col:
                v[i]=(v[i]+t*a)%P
    return next(([i,(x-y)%P] for i,(x,y) in enumerate(zip(v,vec)) if x!=y),None)


def controls():
    ref={0:([(0,1)],[(0,1)]),1:([(0,1)],[(0,1)]),2:([(1,1)],[(1,1)])}
    assert witness(ref,[0,1],[3,4]) is None
    assert witness(ref,[0,2],[3,4])==[0,P-6]
    assert witness(ref,[2],[3,0]) is None and witness(ref,[2],[0,1])==[1,P-2]
    return ["two cancel", "changed reflection", "probe pass needs all columns"]


def main():
    root=Path(sys.argv[1])
    price=json.loads(checked(root/"price/PRICE.json",PRICE))
    keys=json.loads(checked(root/"price/KEYS.json",KEYS))
    assert price["head"]==HEAD and price["keys_sha256"]==KEYS
    assert len(keys)==25350
    raw={k:checked(root/k,v) for k,v in PINS.items()}
    caller=json.loads(raw["inputs/CALLER.json"])
    prior=run_path(str(root/"inputs/two_phase.py"))
    decoder=run_path(str(root/"inputs/screen.py"))
    site=prior["check_stock"](caller,price)
    dense=list(range(1,37))
    checks=controls()
    deadline=monotonic()+32
    refl={k:tuple(map(sparse,v)) for k,v in prior["prefixes"](caller,site,decoder,[1]*17).items()}
    done,hits=[],[]
    for index,key in enumerate(keys):
        if monotonic()>=deadline:
            break
        clocks=sorted(key["odd"]+key["even"])
        assert len(clocks)==2*len(key["odd"]) and len(set(clocks))==len(clocks)
        bad=witness(refl,clocks,dense)
        if bad:
            done.append([index,"dense",*bad])
            continue
        for j in range(36):
            basis=[int(i==j) for i in range(36)]
            bad=witness(refl,clocks,basis)
            if bad:
                done.append([index,j,*bad])
                break
        else:
            done.append([index,"provisional"])
            hits.append(index)
    tested=Counter(len(keys[i]["odd"]) for i,*_ in done)
    print(json.dumps(dict(head=HEAD,price_sha256=PRICE,keys_sha256=KEYS,inputs=PINS,
        q=-1,prime=P,body="all one",dense_probe=dense,controls=checks,
        case_cap=25350,seconds_cap=32,status="EXHAUSTED" if len(done)==len(keys) else "CAPPED",
        tested_by_transfer_count=tested,records=done,provisional=hits,
        unvisited_index_interval=[len(done),len(keys)]),separators=(",",":"),sort_keys=True))


if __name__=="__main__":
    main()
