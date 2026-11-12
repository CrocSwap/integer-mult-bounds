"""Price and disprove a fixed-fibre (8,10) concentration of two odd returns."""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal

ROOT=Path(__file__).resolve().parents[1]
PINS={
 "inputs/CALLER.json":"255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
 "inputs/R92-PRICE.json":"05d7a5ebdd2eeedd6c8f534e8e2eeac22484daf9f387f4a6b88cc9eed22a6b8f",
 "inputs/pricing.py":"f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
 "inputs/7113-signed-child.py":"ef03444360f02225138be9b38e2f9a85f313eeaa910d63a365de0f16d228cb8b",
}
RAILS=(68,70)
CLOCKS=(1339,2970)
PORTS=(15,17,27,34,35,42,47,55)


def inspect(tape):
    contacts={role:[] for role in RAILS}
    for i,e in enumerate(tape):
        if e[0]=="A":
            continue
        if e[0]=="J":
            touched=e[3][:2]
        else:
            assert e[0]=="B"
            _,op,a,*rest=e
            touched=[a]+(rest[:1] if op in ("ADD","QUERY","SWAP") else [])
        for role in touched:
            if role in contacts:
                contacts[role].append((i,e))
    return contacts


def det(m):
    return m[0][0]*m[1][1]-m[0][1]*m[1][0]


def stop(*_):
    raise TimeoutError("20-second rank concentration gate")


def main():
    assert __debug__
    signal(SIGALRM,stop)
    alarm(20)
    for name,h in PINS.items():
        assert sha256((ROOT/name).read_bytes()).hexdigest()==h
    c=loads((ROOT/"inputs/CALLER.json").read_bytes())
    price=loads((ROOT/"inputs/R92-PRICE.json").read_bytes())
    assert len(c["events"])==4783 and tuple(c["types"]["B"]["ports"])==PORTS
    contacts=inspect(c["events"])
    assert contacts=={68:[(1339,["B","IDLE_ODD",68,[8],-1])],
                      70:[(2970,["B","IDLE_ODD",70,[9],-1])]}
    signed=run_path(str(ROOT/"inputs/7113-signed-child.py"))
    C,mul=signed["C"],signed["multiply"]
    for sign,eigen in ((1,(1,0)),(-1,(0,1))):
        for i in range(2):
            assert tuple(C[i][0][k]+sign*C[i][1][k] for k in range(2))==tuple(2*sign**i*v for v in eigen)
    assert mul((1,0),(1,0))==(1,0) and mul((0,1),(0,1))==(-1,0)
    unit_body={(q,i):(q if i==0 else 0,q if i==1 else 0)
               for q in (1,-1) for i in range(2)}
    defect=[[a-b for a,b in zip(unit_body[1,i],unit_body[-1,i],strict=True)] for i in range(2)]
    assert det(defect)==4
    assert det([[2,4],[3,6]])==0 and det([[2,0],[0,0]])==0
    cost=run_path(str(ROOT/"inputs/pricing.py"))["cost"]
    delta=Counter({9:16,8:-8,10:-8})
    assert sum(r*n for r,n in delta.items())==0
    k=Q(price["old_crossing_upper"])
    result=cost(delta,k)
    assert 0<result[0]<=result[1]<k<Q("0.00376669")
    alarm(0)
    print(dumps({"pins":PINS,"native":price["head"],"caller":price["caller_head"],
                 "ports":PORTS,"clocks":CLOCKS,"contacts":contacts,"signs":[1,-1],
                 "columns":4,"difference":defect,"determinant":det(defect),
                 "allowed_replacement_difference_rank_upper":1,
                 "rank_histogram_delta":delta,"price_at_old_crossing_upper":result,
                 "runner_cap_seconds":20},default=str,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
