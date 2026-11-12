"""Exact modular transported projectors for odd/even idle fusion."""
from bisect import bisect_left,bisect_right
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
from runpy import run_path
import sys
from time import monotonic

HEAD="aaeec8c0acf01e99a5f331ef363a698d9c084ace"
PRICE="33aad506112912ddf0721a2b007d9194eaa02e5792aceda2f9774f8838511262"
CALLER="255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc"
ENGINE="cdf54b266ac31fd0efe544badbb9840598d4c63c4d3cd363f60ae9a74cc4b256"


def checked(path,digest):
    raw=path.read_bytes()
    if sha256(raw).hexdigest()!=digest:
        raise ValueError(f"changed dependency {path.name}")
    return raw


def main():
    root=Path(sys.argv[1])
    price=json.loads(checked(root/"price/PRICE.json",PRICE))
    caller=json.loads(checked(root/"price/inputs/7113-CALLER.json",CALLER))
    assert price["head"]==HEAD and price["caller_sha256"]==CALLER
    code=root/"inputs/screen.py"
    checked(code,ENGINE)
    s=run_path(str(code))
    p=s["MOD"]
    controls=s["controls"]()
    odd={int(k):v for k,v in price["odd_jobs"].items()}
    even={int(k):v for k,v in price["even_jobs"].items()}
    for clock,(role,mask) in odd.items():
        assert caller["events"][clock]==["B","IDLE_ODD",role+36,mask,-1]
    for clock,(role,mask) in even.items():
        kind,op,field,literal_mask=caller["events"][clock]
        assert (kind,op,field)==("B","IDLE_ONE",role+36)
        assert sorted(literal_mask)==mask and len(set(literal_mask))==len(mask)
    keys=price["keys"]
    assert len(keys)==180 and len(odd)==4 and len(even)==60
    assert {(r["odd"],r["even"]) for r in keys}=={
        (i,j) for i,a in odd.items() for j,b in even.items() if not set(a[1])&set(b[1])}
    sites=odd|even
    clocks,gates=s["compile_gates"](caller,1,[1]*17)
    deadline=monotonic()+18
    rows=[]
    survivors=[]
    for key in keys:
        if monotonic()>=deadline:
            break
        left,right=sorted((key["odd"],key["even"]))
        source,target=sites[left][0],sites[right][0]
        interval=gates[bisect_right(clocks,left):bisect_left(clocks,right)]
        col,_=s["transport"](interval,source,False,p)
        row,_=s["transport"](interval,target,True,p)
        bad_col,bad_row=s["outside"](col,target),s["outside"](row,source)
        decision="excluded" if bad_col or bad_row else "provisional"
        record=dict(key=key,chronological=[left,right],outside_column=bad_col,outside_row=bad_row,
                    decision=decision,source_role=source,target_role=target)
        rows.append(record)
        if decision=="provisional":
            survivors.append(key)
    print(json.dumps(dict(head=HEAD,price_sha256=PRICE,caller_sha256=CALLER,
        q=1,body="all one",modulus=p,controls=controls,case_cap=180,seconds_cap=18,
        decisions=rows,counts=Counter(x["decision"] for x in rows),provisional=survivors,
        unvisited=keys[len(rows):],status="EXHAUSTED" if len(rows)==len(keys) else "CAPPED"),
        indent=2,sort_keys=True))


if __name__=="__main__":
    main()
