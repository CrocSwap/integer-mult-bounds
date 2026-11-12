"""Check exactly the 13 frozen R109 prefix banks at prime 65537."""
from argparse import ArgumentParser
from collections import Counter
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal
from time import monotonic
import sys

ROOT=Path(__file__).resolve().parent
HEAD="aaeec8c0acf01e99a5f331ef363a698d9c084ace"
WORD="4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a"
PAYLOAD="9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
PINS={
    "inputs/SELECTION.json":"d2b40a0130616e378bf2d35e12805c647a1132230b632fe3adc3449bc2778dad",
    "inputs/MODULAR.json":"792eeb7e32a9e4c980bbf4597cd166bc92cf6c25aac0ba12faeb45b26bb49199",
    "inputs/R105-SELECTION.json":"3bd7bdc9859436ef1d75d011e09d9dfc43a731c5b0a8e9c42fc96d9a6481a30c",
    "inputs/R105-MODULAR.json":"1d99a9842dc8c42395878eb0c14b0027656041f150672491d65d3f023d9df23d",
    "inputs/GEOMETRY.json":"2d0dee60998d168d2eff4c16794176c5ec3b4d18ffa8bde247602035f1b68129",
    "inputs/PRICE.json":"4e0d6436eb4fc6a9dfa34c05ba98aacc63e3a8bf7214145dd9f9254763c5a13e",
    "inputs/sweep.py":"089192d85154c1f8ff1d1cf6329397fe9d40b3e4b09c18dd9c90eda169f09fd9",
    "inputs/second_prime.py":"21dbd96192e1f60c00ceddba01a7e8d0ddd7d6ad7da4ad3ed22ef2e47cc589c4",
    "inputs/7334-WORD.json.gz":WORD,
}
CAP, SECONDS, EVENTS, PRIME=13,25,76466,65537


def unique(items):
    d=dict(items)
    if len(d)!=len(items):
        raise ValueError("duplicate JSON key")
    return d


def freeze(raw):
    def read(name):
        return loads(raw[f"inputs/{name}.json"],object_pairs_hook=unique)
    price,geom,selection,primary,prior_s,prior_m=(read(k) for k in
        ("PRICE","GEOMETRY","SELECTION","MODULAR","R105-SELECTION","R105-MODULAR"))
    assert all(d["head"]==HEAD for d in (price,geom,selection,primary,prior_s,prior_m))
    assert geom["price_sha256"]==PINS["inputs/PRICE.json"] and geom["word_sha256"]==price["word_sha256"]==WORD
    assert geom["eligible_bank_count"]==65 and geom["visited_events"]==primary["prefix_events"]==EVENTS
    assert primary["prime"]==65521 and primary["counts"]=={"prefix exclusion":CAP}
    assert primary["caps"]==selection["caps"] and selection["caps"]["modular_cases"]==CAP
    assert selection["caps"]["modular_seconds"]==SECONDS and not selection["unselected"] and not primary["unselected"]
    assert all(selection["pins"][k]==PINS[k] for k in ("inputs/R105-SELECTION.json","inputs/R105-MODULAR.json"))
    assert primary["pins"]["SELECTION.json"]==PINS["inputs/SELECTION.json"]
    assert selection["selected"]==prior_s["unselected"]==prior_m["unselected"]
    assert len(selection["selected"])==CAP and all(not row["aliases"] for row in selection["selected"])
    assert prior_m["counts"]=={"prefix exclusion":16}
    chosen={tuple(r["key"]):r for r in selection["selected"]}
    earlier={tuple(r["key"]):r["prefix"] for r in primary["results"]}
    geometry={tuple(r["key"]):r for r in geom["all_representatives"]}
    assert list(chosen)==list(earlier) and len(chosen)==CAP
    for k,r in chosen.items():
        assert earlier[k]["determinant"] and earlier[k]["exterior_rank"]==len(r["public"])
        assert all(r[f]==earlier[k][f]==geometry[k][f] for f in ("public","owned","pivots"))
    cohort=set(price["cohort"])
    assert cohort=={1457,1458,1474,1475,1476}
    return cohort,chosen,earlier


def main():
    p=ArgumentParser(description=__doc__)
    p.add_argument("--root",type=Path,default=ROOT)
    args=p.parse_args()
    assert __debug__ and sys.version_info[:2]==(3,12)
    def stop(*_):
        raise TimeoutError("hard 25-second cap")
    signal(SIGALRM,stop)
    alarm(SECONDS)
    deadline=monotonic()+23
    chosen,out,progress,checks={},{},{},[]
    timeout=None
    try:
        raw={}
        for rel,digest in PINS.items():
            data=(args.root/rel).read_bytes()
            if sha256(data).hexdigest()!=digest:
                raise ValueError(f"changed dependency: {rel}")
            raw[rel]=data
        cohort,chosen,earlier=freeze(raw)
        engine=run_path(str(args.root/"inputs/second_prime.py"))
        sweep=run_path(str(args.root/"inputs/sweep.py"))
        assert engine["PRIME"]==PRIME
        checks=engine["controls"]()
        payload=decompress(raw["inputs/7334-WORD.json.gz"])
        assert sha256(payload).hexdigest()==PAYLOAD
        word=loads(payload,object_pairs_hook=unique)
        sweep["sweep"](word,cohort,chosen,earlier,engine,deadline,progress,out)
    except TimeoutError as exc:
        timeout=str(exc)
    finally:
        alarm(0)
    rows=[out[k] for k in chosen if k in out]
    complete=timeout is None and progress.get("first_unvisited_cut",0) is None and len(rows)==CAP
    agreement=complete and all(r["disposition"]=="excluded" for r in rows)
    print(dumps(dict(head=HEAD,pins=PINS,prime=PRIME,controls=checks,cap_cases=CAP,cap_seconds=SECONDS,
        counts=Counter(r["disposition"] for r in rows),rows=rows,complete=complete,agreement=agreement,
        progress=progress,timeout=timeout,original_minor_axes_nonzero=sum(bool(r["primary_minor_det_mod_65537"]) for r in rows),
        remaining=[k for k in chosen if k not in out or out[k]["disposition"]!="excluded"]),indent=2,sort_keys=True))
    if not agreement:
        raise SystemExit(2)


if __name__=="__main__":
    main()
