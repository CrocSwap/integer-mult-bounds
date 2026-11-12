"""Exact normalized row support for one saved-entry owned MOVE replacement."""
from fractions import Fraction as Q
from functools import cache
from gzip import decompress
from hashlib import sha256
from json import dumps,loads
from pathlib import Path
from signal import SIGALRM,alarm,signal

ROOT=Path(__file__).resolve().parent
ZIP="4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a"
RAW="9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
PRICE="ec9a60268731327b5628fea15510bb2a5b663c67d0a308ef6db5f077045c9ce3"


@cache
def scalar(a):
    return Q(a)


def stop(*_):
    raise TimeoutError("20-second entry row support gate")


def main():
    assert __debug__
    signal(SIGALRM,stop)
    alarm(20)
    raw=(ROOT/"inputs/7334-WORD.json.gz").read_bytes()
    p=(ROOT/"PRICE.json").read_bytes()
    assert sha256(raw).hexdigest()==ZIP and sha256(p).hexdigest()==PRICE
    raw=decompress(raw)
    assert sha256(raw).hexdigest()==RAW
    w=loads(raw)
    t=w["program"]
    n,m=w["public"],w["owned_fields"]
    assert (n,m,len(t))==(1501,68,76466)
    assert t[38967]==["MOVE",146,3,365,False]
    assert t[39811]==["MOVE",1503,520,595,True] and t[39828]==["INIT",1504,591]
    assert not any(e[1]==1504 or (e[0] in ("ADD","COPY") and e[2]==1504) for e in t[:39828])
    assert len(w["frames"][3])==0 and len(w["frames"][595])==1
    assert sum(x==3 for x in w["initial"])==1060
    rows=[{i:Q(1)} for i in range(n)]+[{} for _ in range(m)]
    charts=w["initial"]+[None]*m
    for i,(op,r,*a) in enumerate(t[:39811]):
        if i==38967:
            assert charts[146]==3
            ancestor=rows[146].copy()
        if op=="MOVE":
            assert charts[r]==a[0]
            charts[r]=a[1]
        elif op=="INIT":
            assert charts[r] is None and not rows[r]
            charts[r]=a[0]
        elif op=="CLEAR":
            assert charts[r]==a[0]
            charts[r]=None
            rows[r].clear()
        elif op=="SCALE":
            assert charts[r]==a[1]
            rows[r]={j:x*scalar(a[0]) for j,x in rows[r].items()}
        else:
            s,k,c=a
            assert op in ("ADD","COPY") and charts[r]==charts[s]==c and r!=s
            assert op!="COPY" or not rows[r]
            k=scalar(k)
            for j,x in rows[s].items():
                y=rows[r].get(j,Q(0))+k*x
                if y:
                    rows[r][j]=y
                else:
                    rows[r].pop(j,None)
    assert charts[1503]==520
    target=rows[1503]
    groups={}
    for i,x in sorted(target.items()):
        groups.setdefault(w["initial"][i],[]).append([i,str(x)])
    a={j:-x/2 for j,x in ancestor.items()}
    d=[(j,str(target.get(j,0)-a.get(j,0))) for j in sorted(set(target)|set(a)) if target.get(j,0)!=a.get(j,0)]
    alarm(0)
    print(dumps({"head":loads(p)["head"],"pins":{"word_gzip":ZIP,"word_payload":RAW,"price":PRICE},
                 "cut":39811,"source_coordinates":1501,"seconds_cap":20,"row":target,
                 "entry_chart_support":groups,"entry_chart3_only":set(groups)=={3},
                 "ancestor_difference":d,"shadow_first_init":39828},
                indent=2,sort_keys=True,default=str))


if __name__=="__main__":
    main()
