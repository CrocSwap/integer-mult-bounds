"""Reconstruct the two public rows just before the paired rank-five MOVEs."""
from fractions import Fraction as Q
from functools import cache
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from signal import SIGALRM, alarm, signal

ROOT = Path(__file__).resolve().parent
PINS = {
    "inputs/7334-WORD.json.gz": "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
    "inputs/PRICE.json": "5bac77abf307955e7eabcd7121e9657820e3d44d05a783193179055939137daa",
}
PAYLOAD = "9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
CLOCK, FIRST, SECOND = 32944, 625, 624


def read(name):
    raw = (ROOT/name).read_bytes()
    assert sha256(raw).hexdigest()==PINS[name]
    if name.endswith(".gz"):
        raw = decompress(raw)
        assert sha256(raw).hexdigest()==PAYLOAD
    return loads(raw)


@cache
def scalar(a):
    return Q(a)


def trace(word):
    n, m = word["public"],word["owned_fields"]
    charts = word["initial"]+[None]*m
    rows = [{r:Q(1)} for r in range(n)]+[{} for _ in range(m)]
    for op, dst, *args in word["program"][:CLOCK]:
        if op=="MOVE":
            a,b,owned = args
            assert charts[dst]==a and owned==(dst>=n)
            charts[dst]=b
        elif op=="INIT":
            assert dst>=n and charts[dst] is None and not rows[dst]
            charts[dst]=args[0]
        elif op=="CLEAR":
            assert dst>=n and charts[dst]==args[0]
            charts[dst]=None
            rows[dst].clear()
        elif op=="SCALE":
            k,chart=args
            assert charts[dst]==chart and scalar(k)
            rows[dst]={i:scalar(k)*a for i,a in rows[dst].items()}
        else:
            assert op in ("ADD","COPY")
            src,k,chart=args
            assert src!=dst and charts[src]==charts[dst]==chart
            assert op!="COPY" or (dst>=n and not rows[dst])
            for i,a in rows[src].items():
                updated=rows[dst].get(i,Q(0))+scalar(k)*a
                if updated:
                    rows[dst][i]=updated
                else:
                    rows[dst].pop(i,None)
    assert charts[FIRST]==charts[SECOND]==3
    return rows[FIRST],rows[SECOND]


def minor(a,b):
    if not a or not b:
        return None
    coordinates=sorted(set(a)|set(b))
    i=coordinates[0]
    for j in coordinates[1:]:
        block=[[a.get(i,Q(0)),a.get(j,Q(0))],[b.get(i,Q(0)),b.get(j,Q(0))]]
        det=block[0][0]*block[1][1]-block[0][1]*block[1][0]
        if det:
            return {"source_coordinates":[i,j],"matrix":block,"determinant":det}
    return None


def stop(*_):
    raise TimeoutError("20-second paired public MOVE gate")


def main():
    assert __debug__
    signal(SIGALRM,stop)
    alarm(20)
    word=read("inputs/7334-WORD.json.gz")
    price=read("inputs/PRICE.json")
    assert price["candidate"]==[CLOCK,FIRST,SECOND,3,117,5]
    assert price["signed_histogram_delta"]=={"5":17}
    assert Q(price["one_pair_gross_interval"][0])>0
    assert len(word["program"])==76466 and word["public"]==1501 and word["owned_fields"]==68
    assert word["program"][CLOCK:CLOCK+2]==[["MOVE",FIRST,3,117,False],["MOVE",SECOND,3,117,False]]
    assert len(word["frames"][3])==0 and len(word["frames"][117])==5
    assert minor({0:Q(1)},{0:Q(2)}) is None
    assert minor({0:Q(1)},{1:Q(1)})["determinant"]==1
    left,right=trace(word)
    witness=minor(left,right)
    if witness is None:
        coefficient = right.get(min(left),Q(0))/left[min(left)] if left else None
    else:
        coefficient=None
    alarm(0)
    print(dumps({"head":price["head"],"caller":price["caller"],"pins":PINS,
                 "pre_event_cut":CLOCK,"roles":[FIRST,SECOND],"scope":price["candidate"],
                 "source_coordinates":1501,"seconds_cap":20,"first_row":left,
                 "second_row":right,"minor":witness,"proportion":coefficient,
                 "verdict":"EXCLUDED" if witness else "SURVIVES normalized rows only"},
                indent=2,sort_keys=True,default=str))


if __name__=="__main__":
    main()
