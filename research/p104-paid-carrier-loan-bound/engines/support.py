"""Check the exact carrier row at the frozen R142 nested move."""
from fractions import Fraction
from gzip import decompress
from hashlib import sha256
from json import dumps,loads
from pathlib import Path
from runpy import run_path
from time import monotonic

ROOT=Path(__file__).resolve().parents[1]
PINS={
    "inputs/7334-WORD.json.gz":"4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
    "inputs/donor_span.py":"4d5306e2c0b7e91c79d22c82e8e760aed2c311979298c558e631975d4d1ae5b1",
    "inputs/aggregate.py":"8bf1b91d7fc0937305466686522f5fb3920c66c71830acfc94adde84ba4f49e1",
    "next/PRICE.json":"7f99902aaa6b47029f51fa0e10a59c677a78eca0e91b43c213d4f7e34cfececa",
}


def checked(path):
    raw=(ROOT/path).read_bytes()
    if sha256(raw).hexdigest()!=PINS[path]:
        raise ValueError(f"changed dependency {path}")
    return raw


def main():
    assert __debug__
    checked("inputs/donor_span.py")
    checked("inputs/aggregate.py")
    price=loads(checked("next/PRICE.json"))
    assert Fraction(price["cells"][0]["complete_probe"][0])>0
    data=decompress(checked("inputs/7334-WORD.json.gz"))
    assert sha256(data).hexdigest()=="9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
    word=loads(data)
    u,m,f,h,B=40226,44235,1161,1550,543
    program=word["program"]
    assert program[u]==["MOVE",f,541,127,False] and program[m]==["MOVE",h,541,B,True]
    helper=run_path(str(ROOT/"inputs/donor_span.py"))
    algebra=run_path(str(ROOT/"inputs/aggregate.py"))
    tests=algebra["controls"](helper)
    limit=monotonic()+28
    req={(u,B,h)}
    banks,targets=helper["snapshot"](word,{u:{(B,h)}},{u:{f}},limit)
    assert set(banks)==req and (u,f) in targets
    bank=banks[u,B,h]
    assert sorted(bank)==[628,630]
    result=algebra["exact_span"](targets[u,f],bank,limit,helper)
    if result is None:
        raise TimeoutError("exact support cap reached")
    print(dumps(dict(key=[m,h,u,f,B],head=price["head"],caller=price["caller"],pins=PINS,controls=tests,
        source={i:str(v) for i,v in targets[u,f].items()},bank_roles=sorted(bank),result=result),indent=2,sort_keys=True))


if __name__=="__main__":
    main()
