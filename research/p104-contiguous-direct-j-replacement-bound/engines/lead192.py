from hashlib import sha256
from json import dumps,loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal

ROOT=Path(__file__).resolve().parents[1]


def stop(*_):
    raise TimeoutError("20-second exact gate")


def rank(rows):
    piv={}
    for row in rows:
        r=row.copy()
        for k,v in sorted(piv.items()):
            if r[k]:
                r=[x-r[k]*y for x,y in zip(r,v,strict=True)]
        k=next((i for i,x in enumerate(r) if x),None)
        if k is not None:
            piv[k]=[x/r[k] for x in r]
    return sorted(piv)


def main():
    assert __debug__
    signal(SIGALRM,stop)
    alarm(20)
    pins={}
    for line in (ROOT/"receipts/R192-LEAD-PINS.txt").read_text().splitlines():
        h,p=line.split()
        assert p not in pins and sha256((ROOT/(p if p.startswith("inputs/") else "engines/"+p)).read_bytes()).hexdigest()==h
        pins[p]=h
    assert pins["inputs/PRICE.json"]=="1ad9852ecff0b3780770cbf4e500731e65214a9c438f8b1ed2c0cbe484d9b36b"
    f=run_path(str(ROOT/"engines/forward.py"))
    assert pins["inputs/CALLER.json"]==f["PINS"]["inputs/CALLER.json"]
    c=loads((ROOT/"inputs/CALLER.json").read_bytes())
    tape=c["events"][43:269]
    assert [(43+i,e[1]) for i,e in enumerate(tape) if e[0]=="J"]==[(43,1),(137,2),(268,3)]
    unit,apply=f["unit"],f["apply"]
    cols={q:[apply(tape,unit(i),q) for i in range(36)] for q in (1,-1)}
    assert all(apply(tape,col,q,inverse=True)==unit(i) for q,xs in cols.items() for i,col in enumerate(xs))
    diff=[[x-y for x,y in zip(a,b,strict=True)] for a,b in zip(cols[1],cols[-1],strict=True)]
    piv=rank(diff)
    assert rank([unit(i) for i in range(4)])==list(range(4))
    alarm(0)
    print(dumps({"pins":pins,"rank":len(piv),"rank_cap":4,"pivot_rows":piv,
                 "clock_window_inclusive":[43,268],"unit_bodies":True,"signs":[1,-1],
                 "basis_columns":36,"seconds_cap":20,"delta_entries":[[i,j,str(x)] for j,v in enumerate(diff)
                 for i,x in enumerate(v) if x]},indent=2,sort_keys=True))


if __name__=="__main__":
    main()
