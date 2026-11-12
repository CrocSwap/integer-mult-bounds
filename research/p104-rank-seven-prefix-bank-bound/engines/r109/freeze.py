"""Freeze exactly the 13 still-unvisited #7367 bank keys."""
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PINS={
    "inputs/R105-SELECTION.json":"3bd7bdc9859436ef1d75d011e09d9dfc43a731c5b0a8e9c42fc96d9a6481a30c",
    "inputs/R105-MODULAR.json":"1d99a9842dc8c42395878eb0c14b0027656041f150672491d65d3f023d9df23d",
}


def main():
    assert __debug__
    docs=[]
    for path,pin in PINS.items():
        raw=(ROOT/path).read_bytes()
        if sha256(raw).hexdigest()!=pin:
            raise ValueError(f"changed dependency {path}")
        docs.append(json.loads(raw))
    select,mod=docs
    assert select["head"]==mod["head"] and mod["counts"]=={"prefix exclusion":16}
    assert [r["key"] for r in mod["results"]]==[r["key"] for r in select["selected"]]
    keys=select["unselected"]
    assert keys==mod["unselected"] and len(keys)==13
    assert all(not r["aliases"] and not r["owned"] for r in keys)
    assert Counter(len(r["public"]) for r in keys)=={1:9,2:4}
    print(json.dumps(dict(head=select["head"],pins=PINS,selected=keys,unselected=[],
        caps={"modular_cases":13,"modular_seconds":25,"exact_cases":4,"exact_seconds":35}),
        indent=2,sort_keys=True))


if __name__=="__main__":
    main()
