"""Independently price shared paid descendants and certify exact exterior spans."""
from collections import Counter
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
from itertools import combinations
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    "inputs/R198.json": "f7cbbca8b9b17405427dd7bb8a132e53b34f1c4646918d7a9bf174f1531add49",
    "inputs/R198-INDEPENDENT.json": "2a75693d5d48a7cb6a901ebf3c3cbe9436357ca5beaea6e9b43af1a2962de4b0",
    "inputs/7334-WORD.json.gz": "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
    "inputs/R92-PRICE.json": "05d7a5ebdd2eeedd6c8f534e8e2eeac22484daf9f387f4a6b88cc9eed22a6b8f",
    "inputs/pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
}
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CALLER = "07a76c5e2738882c0cb322278e56f6cae3c9885d"


def unique(items):
    d = dict(items)
    assert len(d) == len(items)
    return d


def read(name):
    raw = (ROOT/name).read_bytes()
    assert sha256(raw).hexdigest() == PINS[name], name
    return raw


def load(name):
    return loads(read(name), object_pairs_hook=unique)


def axpy(dst, src, c):
    for i,v in src.items():
        z = dst.get(i,0) + c*v
        if z:
            dst[i] = z
        else:
            dst.pop(i,None)


def dot(row, x):
    return sum(value*x.get(i,0) for i,value in row.items())


def certificate(rows, target):
    basis = {}
    for index,row in enumerate(rows):
        w,c = row.copy(),{index:Q(1)}
        for p,(v,a) in sorted(basis.items()):
            if p in w:
                scale = -w[p]
                axpy(w,v,scale)
                axpy(c,a,scale)
        if w:
            p = min(w)
            k = w[p]
            basis[p] = ({i:a/k for i,a in w.items()}, {i:a/k for i,a in c.items()})
    residual, coeff = target.copy(), {}
    for p,(v,c) in sorted(basis.items()):
        if p in residual:
            scale = residual[p]
            axpy(residual,v,-scale)
            axpy(coeff,c,scale)
    if not residual:
        rebuilt = {}
        for i,c in coeff.items():
            axpy(rebuilt,rows[i],c)
        assert rebuilt == target
        return {"rank":len(basis), "status":"span", "coefficients":coeff}
    j = min(residual)
    x = {j:Q(1)}
    for p,(v,_) in sorted(basis.items(),reverse=True):
        z = -dot(v,x)
        if z:
            x[p] = z
    assert all(not dot(row,x) for row in rows)
    separated = dot(target,x)
    assert separated == residual[j] and separated
    return {"rank":len(basis), "status":"outside span","input":x,"target_value":separated}


def stop(*_):
    raise TimeoutError("30-second subset cap")


def main():
    assert __debug__
    signal(SIGALRM,stop)
    alarm(30)
    lead = load("inputs/R198.json")
    old = load("inputs/R198-INDEPENDENT.json")
    price = load("inputs/R92-PRICE.json")
    assert lead["head"] == old["head"] == price["head"] == HEAD
    assert old["caller"] == price["caller_head"] == CALLER
    assert not old["unvisited"]
    raw = decompress(read("inputs/7334-WORD.json.gz"))
    assert sha256(raw).hexdigest() == "9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
    word = loads(raw, object_pairs_hook=unique)
    assert len(word["initial"]) == 1501 and len(word["program"]) == 76466
    assert not word["frames"][3] and word["initial"].count(3) == 1060
    data = []
    for a,b in zip(lead["records"],old["results"],strict=True):
        key = a["key"]
        assert key == b["key"] and a["row"] == b["row"]
        t,role,src,dst,r = key
        assert word["program"][t] == ["MOVE",role,src,dst,True]
        assert len(word["frames"][src])-len(word["frames"][dst]) == r > 1
        assert len(word["frames"][dst]) == 1
        row = {int(i):Q(v) for i,v in a["row"].items()}
        group = {}
        for label,parts in a["entry_chart_support"].items():
            for i,v in parts:
                assert word["initial"][i] == int(label) and i not in group
                group[i] = Q(v)
        assert group == row
        data.append((key,{i:v for i,v in row.items() if word["initial"][i]!=3}))
    assert len(data) == 8 and [k[0] for k,_ in data] == sorted(k[0] for k,_ in data)
    keys = [(t,s) for t in range(len(data)) for count in range(1,t+1)
            for s in combinations(range(t),count)]
    assert len(keys) == 247
    assert certificate([{0:Q(1)}],{0:Q(2)})["coefficients"] == {0:Q(2)}
    assert certificate([{0:Q(1)}],{1:Q(2)})["target_value"] == 2
    read("inputs/pricing.py")
    cost = run_path(str(ROOT/"inputs/pricing.py"))["cost"]
    crossing = Q(price["old_crossing_upper"])
    price_cache = {}
    cases, capped = [],False
    try:
        for target,donors in keys:
            key,row = data[target]
            charts = sorted({data[i][0][3] for i in donors} - {key[3]})
            paid = 1+len(charts)
            r = key[-1]
            cache = (r,paid)
            if cache not in price_cache:
                price_cache[cache] = cost(Counter({r:17,1:-17*paid}),crossing)
            interval = price_cache[cache]
            assert interval[0]>0 or interval[1]<=0
            proof = certificate([data[i][1] for i in donors],row) if interval[0]>0 else None
            cases.append({"target":key,"donors":[data[i][0][0] for i in donors],
                          "paid_rank_one_per_copy":paid,"lowered_charts":charts,
                          "directed_gross":interval,"certificate":proof})
    except TimeoutError:
        capped=True
    finally:
        alarm(0)
    survivors = [case for case in cases if case["certificate"] and case["certificate"]["status"]=="span"]
    print(dumps({"head":HEAD,"caller":CALLER,"pins":PINS,"cap_seconds":30,"subset_cap":247,
                 "capped":capped,"examined":len(cases),
                 "price_admitted":sum(c["certificate"] is not None for c in cases),
                 "survivors":survivors,"unvisited":[[data[t][0][0],[data[i][0][0] for i in s]]
                                                    for t,s in keys[len(cases):]],"cases":cases},
                default=str,sort_keys=True,indent=2))
    if capped:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
