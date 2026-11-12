"""Independent reverse pullback and exact two-donor span decision for R142."""
from fractions import Fraction as Q
from functools import cache
from gzip import decompress
from hashlib import sha256
from json import dumps,loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM,alarm,signal
from time import monotonic

ROOT = Path(__file__).resolve().parent
PINS = {
    "GEOMETRY.json": "92f5533fb14a10f6594cca514e508478dc5e1e493701cb2ac63af7a0f5f0df02",
    "reverse_geometry.py": "8340cd379961ed1b36e1e1591aa174e0fb03b86d4bc3695ec9a54c072776f22a",
}
ZERO, ONE = Q(0), Q(1)


def check(name,digest):
    raw=(ROOT/name).read_bytes()
    if sha256(raw).hexdigest()!=digest:
        raise ValueError("changed dependency "+name)
    return raw


@cache
def rational(x):
    return Q(x)


def prefix_rows(tape,cut,roles,deadline):
    dual = {r:{r:ONE} for r in roles}
    for t in range(cut-1,-1,-1):
        if t%128==0 and monotonic()>=deadline:
            raise TimeoutError("reverse covector cap")
        op,dst,*args=tape[t]
        for row in dual.values():
            if dst not in row:
                continue
            value=row[dst]
            if op in ("INIT","CLEAR","COPY"):
                del row[dst]
            if op in ("ADD","COPY"):
                src, coeff, _ = args
                new=row.get(src,ZERO)+value*rational(coeff)
                if new:
                    row[src]=new
                else:
                    row.pop(src,None)
            elif op=="SCALE":
                row[dst]=value*rational(args[0])
            else:
                assert op in ("MOVE","INIT","CLEAR")
    return dual


def value(row,coord):
    return row.get(coord,ZERO)


def certify(target,first,second):
    columns=sorted(target.keys() | first.keys() | second.keys())
    for x in columns:
        if value(target,x) and not (value(first,x) or value(second,x)):
            return {"decision":"outside span","dual":{x:"1"},"value":str(target[x])}
    donors=[first,second]
    if not first:
        donors.reverse()
    a,b=donors
    if not a:
        assert not target
        return {"decision":"supported","coefficients":["0","0"]}
    x=min(a)
    other=next((y for y in columns if a[x]*value(b,y)-value(b,x)*value(a,y)),None)
    tx,bx=value(target,x),value(b,x)
    if other is None:
        alpha,beta=tx/a[x],ZERO
    else:
        y=other
        det=a[x]*value(b,y)-bx*value(a,y)
        alpha=(tx*value(b,y)-bx*value(target,y))/det
        beta=(a[x]*value(target,y)-tx*value(a,y))/det
    for z in columns:
        residual=value(target,z)-alpha*value(a,z)-beta*value(b,z)
        if not residual:
            continue
        if other is None:
            weights={x:-value(a,z)/a[x],z:ONE}
        else:
            y=other
            ax,ay,az=a[x],value(a,y),value(a,z)
            bx,by,bz=value(b,x),value(b,y),value(b,z)
            weights={x:(-az*by+ay*bz)/det,y:(-ax*bz+az*bx)/det,z:ONE}
        assert all(sum(w*value(v,k) for k,w in weights.items())==0 for v in (a,b))
        assert sum(w*value(target,k) for k,w in weights.items())==residual
        return {"decision":"outside span","dual":{k:str(w) for k,w in weights.items() if w},
                "value":str(residual)}
    coeff=[str(alpha),str(beta)]
    return {"decision":"supported","coefficients":coeff if a is first else coeff[::-1]}


def main():
    assert __debug__
    geom=loads(check("GEOMETRY.json",PINS["GEOMETRY.json"]))
    check("reverse_geometry.py",PINS["reverse_geometry.py"])
    g=run_path(str(ROOT/"reverse_geometry.py"))
    assert geom["complete"] and not geom["unresolved"] and len(geom["geometry"])==1
    key=geom["geometry"][0]
    assert (key["anchor"],key["carrier"],key["h"],key["f"],key["donor_public"],key["donor_owned"]) == (
        44235,40226,1550,1161,[628,630],[])
    assert certify({0:Q(2),1:Q(-3)},{0:ONE},{1:ONE})=={
        "decision":"supported","coefficients":["2","-3"]}
    assert certify({0:ONE,1:ONE,2:Q(3)},{0:ONE,2:ONE},{1:ONE,2:ONE})=={
        "decision":"outside span","dual":{0:"-1",1:"-1",2:"1"},"value":"1"}

    def timeout(*_):
        raise TimeoutError("30-second hard cap")

    signal(SIGALRM,timeout)
    alarm(30)
    deadline=monotonic()+29
    try:
        raw=decompress(g["authenticate"](ROOT)["inputs/7334-WORD.json.gz"])
        assert sha256(raw).hexdigest()==g["RAW"]
        word=loads(raw,object_pairs_hook=g["unique"])
        tape=word["program"]
        clock=key["carrier"]
        h=key["h"]
        anchor=key["anchor"]
        roles=[key["f"],*key["donor_public"]]
        cut=next(r for r in geom["anchors"] if r["anchor"]==anchor)
        assert cut["previous"][0] < clock < anchor < cut["first_use"][0] == anchor+1
        assert all(h not in g["incidences"](e) for e in tape[clock:anchor])
        assert tape[clock]==["MOVE",roles[0],541,127,False]
        assert tape[anchor]==["MOVE",h,541,543,True]
        rows=prefix_rows(tape,clock,roles,deadline)
        assert all(k<word["public"] for r in rows.values() for k in r)
        result=certify(*(rows[r] for r in roles))
        result |= dict(geometry=key,cut=cut,controls=["planted signed donor coefficients","three-coordinate separating dual"],
            caps={"keys":1,"seconds":30},pins=PINS|g["PINS"],
            rows={r:{k:str(v) for k,v in row.items()} for r,row in rows.items()},unresolved=[])
    finally:
        alarm(0)
    print(dumps(result,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
