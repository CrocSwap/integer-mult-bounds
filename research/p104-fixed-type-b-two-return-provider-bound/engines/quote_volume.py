"""Preprice two rank cells for a two-return canonical signed odd-idle child."""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import comb
from pathlib import Path
from runpy import run_path
from signal import SIGALRM,alarm,signal

ROOT=Path(__file__).resolve().parent
PINS={
 "R149-PRICE.json":"cca4b82a9b7b1670705373a245282043e32527f453cd24ba4500794857686872",
 "R85-PRICE.json":"33aad506112912ddf0721a2b007d9194eaa02e5792aceda2f9774f8838511262",
 "pricing.py":"f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
 "PR7344-CONTRACT.json":"e77f3e124605a059cbf803e8a64cfb99e528091c7b99cbe4ea9dc82b56c75967",
}
def load(name):
    raw=(ROOT/"inputs"/name).read_bytes()
    if sha256(raw).hexdigest()!=PINS[name]:
        raise ValueError("changed dependency "+name)
    return json.loads(raw) if name.endswith(".json") else raw

def bins(n):
    return [sum(comb(n,k) for k in range(j,n+1,4)) for j in range(4)]

def stop(*_):
    raise TimeoutError("10-second quote cap")

def main():
    assert __debug__
    signal(SIGALRM,stop)
    alarm(10)
    p=load("R149-PRICE.json")
    old=load("R85-PRICE.json")
    contract=load("PR7344-CONTRACT.json")
    load("pricing.py")
    assert (p["head"],p["caller"])==(old["head"],old["caller_head"])
    assert p["ports"]==8 and [1339,2970] in p["pairs"]
    assert "canonical_carrier_at_width_eight" in contract
    tariffs=run_path(str(ROOT/"inputs/pricing.py"))
    k=Q(p["points"]["incumbent"])
    hist=Counter({int(r):n for r,n in old["complete_targets"].items()})
    hist.subtract({int(r):n for r,n in old["complete_paid"].items()})
    phase=bins(8)
    assert phase==[72,64,56,64]
    need=2*Q(min(phase[0],phase[2])+min(phase[1],phase[3]),256)
    assert need==Q(15,16)
    h9=tariffs["power_bounds"](9,k)
    rows=[]
    for rank in (16,18):
        n=8*rank
        residues=bins(n)
        capacity=1-Q(min(residues),2**n)
        volume=need/capacity
        hr=tariffs["power_bounds"](rank,k)
        affordable=2*h9[1]/hr[0]
        assert volume>affordable
        gain=16*h9[1]-8*volume*hr[0]
        rows.append(dict(rank=rank,width=n,residues=residues,capacity=str(capacity),
                         necessary_volume=str(volume),affordable_upper=str(affordable),
                         gross_upper=str(gain),complete_upper=str(tariffs["cost"](hist,k)[1]+gain)))
    alarm(0)
    print(json.dumps(dict(pins=PINS,phase=phase,need=str(need),rows=rows),indent=2,sort_keys=True))

if __name__=="__main__":
    main()
