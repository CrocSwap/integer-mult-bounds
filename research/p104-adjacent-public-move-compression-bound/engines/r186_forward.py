"""Reconstruct the two public rows just before the paired rank-five MOVEs."""
from fractions import Fraction as Q
from functools import cache
from gzip import decompress
from hashlib import sha256
from collections import Counter
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


def trace(word, pairs, checked):
    n, m = word["public"],word["owned_fields"]
    charts = word["initial"]+[None]*m
    rows = [{r:Q(1)} for r in range(n)]+[{} for _ in range(m)]
    for clock, (op, dst, *args) in enumerate(word["program"][:max(pairs)+1]):
        if clock in pairs:
            key = pairs[clock]
            _, left, right, a, _, _ = key
            assert charts[left] == charts[right] == a
            row_l,row_r = rows[left],rows[right]
            witness = minor(row_l,row_r)
            checked.append({"key":key,"left_support":len(row_l),"right_support":len(row_r),
                            "minor":witness,"left_row":row_l.copy(),"right_row":row_r.copy()})

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
    raise TimeoutError("25-second exact adjacent-pair sweep")


def main():
    assert __debug__
    signal(SIGALRM,stop)
    word=read("inputs/7334-WORD.json.gz")
    price=read("inputs/PRICE.json")
    prior_raw=(ROOT/"inputs"/"R185.json").read_bytes()
    assert sha256(prior_raw).hexdigest() == PRIOR
    prior=loads(prior_raw)
    assert len(word["program"])==76466 and word["public"]==1501 and word["owned_fields"]==68
    tape=word["program"]
    inventory=[]
    for k,(a,b) in enumerate(zip(tape,tape[1:])):
        if a[0]==b[0]=="MOVE" and a[2:]==b[2:] and a[4] is False and a[1]!=b[1]:
            source,destination=a[2:4]
            r=len(word["frames"][destination])-len(word["frames"][source])
            assert r>0
            inventory.append([k,a[1],b[1],source,destination,r])
    assert inventory==price["pairs"] and len(inventory)==29
    pairs={key[0]:key for key in inventory}
    assert len({i for k in pairs for i in (k,k+1)})==58
    checked=[]
    capped=False
    alarm(25)
    try:
        trace(word,pairs,checked)
    except TimeoutError:
        capped=True
    finally:
        alarm(0)
    if checked:
        assert checked[0]["key"]==prior["scope"]
        assert dumps(checked[0]["minor"],default=str,sort_keys=True)==dumps(prior["minor"],sort_keys=True)
    resolved={row["key"][0] for row in checked if row["minor"] is not None}
    tests={row["key"][0] for row in checked}
    print(dumps({"head":price["head"],"caller":price["caller"],
                 "pins":PINS|{"inputs/R185.json":PRIOR},
                 "pair_cap":29,"new_cases_cap":28,"seconds_cap":25,"capped":capped,
                 "distinct_pair_ranks":Counter(p[-1] for p in inventory),
                 "records":checked,"resolved":sorted(resolved),
                 "unresolved":sorted(set(pairs)-resolved),"unvisited":sorted(set(pairs)-tests)},
                indent=2,sort_keys=True,default=str))
    if capped:
        raise SystemExit(2)


PRIOR = "46dd9fa3c54d2f5547b43178ab86801429f0b53e3fa270d4b156c53007f9fe36"

if __name__=="__main__":
    main()
