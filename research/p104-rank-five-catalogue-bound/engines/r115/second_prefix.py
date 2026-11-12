"""Independently check the eleven frozen R115 banks at prime 65537."""
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
CALLER="07a76c5e2738882c0cb322278e56f6cae3c9885d"
WORD="4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a"
PAYLOAD="9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
PINS={
    "inputs/SELECTION.json":"a9d4cb3acf6ad489c631ae984665391fbacfc069a2ba8d4521970ed5dd46bb88",
    "inputs/MODULAR.json":"118fda832ce46e8e52e88a321bf0fcfd182b24e358756c956bc29a1944ec62ff",
    "inputs/GEOMETRY.json":"c2a4406cf7130a819189e8ceefb4bb6e09edd392eb56820f9fcadb0e9415ef4e",
    "inputs/PRICE.json":"c04adfb199f6dbc25806d6062562c7d707b8fda8ad73f3ed818901248d25ffbf",
    "inputs/sweep.py":"7d66a3f00eee69cfb7ebacc72a6330b72f9a538205119949d5bd60da5767d74c",
    "inputs/second_prime.py":"21dbd96192e1f60c00ceddba01a7e8d0ddd7d6ad7da4ad3ed22ef2e47cc589c4",
    "inputs/7334-WORD.json.gz":WORD,
}
CASES,CAP,SECONDS,EVENTS,PRIME=11,16,25,76466,65537
GROUP=[3,241]


def unique(items):
    d=dict(items)
    if len(d)!=len(items):
        raise ValueError("duplicate JSON key")
    return d


def load_freeze(raw):
    def read(name):
        return loads(raw[f"inputs/{name}.json"],object_pairs_hook=unique)
    price,geom,sel,primary=[read(k) for k in ("PRICE","GEOMETRY","SELECTION","MODULAR")]
    assert all(d["head"]==HEAD for d in (price,geom,sel,primary)) and price["caller"]==CALLER
    assert price["word_sha256"]==geom["pins"]["inputs/7334-WORD.json.gz"]==WORD
    assert sel["geometry_sha256"]==PINS["inputs/GEOMETRY.json"]
    assert geom["pins"]["lead/PRICE.json"]==PINS["inputs/PRICE.json"]
    assert primary["pins"]["SELECTION.json"]==PINS["inputs/SELECTION.json"]
    assert geom["status"]=="EXHAUSTED" and geom["visited_events"]==primary["prefix_events"]==EVENTS
    assert primary["prime"]==65521 and primary["counts"]=={"prefix exclusion":CASES}
    assert primary["caps"]==sel["caps"] and sel["caps"]["modular_cases"]==CAP
    assert sel["caps"]["modular_seconds"]==SECONDS and primary["unselected"]==sel["unselected"]
    assert sel["selected_group"]==geom["selected_group"]==GROUP
    chosen={tuple(r["key"]):r for r in sel["selected"]}
    earlier={tuple(r["key"]):r["prefix"] for r in primary["results"]}
    geometry={tuple(r["key"][:2]):r for r in geom["selected"] if r["key"][2:]==GROUP}
    assert len(chosen)==len(geometry)==CASES and list(chosen)==list(earlier)==list(geometry)
    for k,r in chosen.items():
        assert earlier[k]["determinant"] and earlier[k]["exterior_rank"]==len(r["public"])
        assert all(r[f]==earlier[k][f]==geometry[k][f] for f in ("public","owned","pivots"))
    groups=[g for g in price["groups"] if g["endpoints"]==GROUP]
    assert len(groups)==1 and len(price["groups"])==28 and len(price["cohort"])==80
    cohort=set(groups[0]["roles"])
    assert cohort=={339,1101}
    remaining=[r for r in sel["unselected"] if r[2:]==GROUP]
    return cohort,chosen,earlier,remaining,len(sel["unselected"])


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
    same_group_pending=[]
    total_pending=None
    timeout=None
    try:
        raw={}
        for rel,digest in PINS.items():
            data=(args.root/rel).read_bytes()
            if sha256(data).hexdigest()!=digest:
                raise ValueError(f"changed dependency: {rel}")
            raw[rel]=data
        cohort,chosen,earlier,same_group_pending,total_pending=load_freeze(raw)
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
    complete=timeout is None and progress.get("first_unvisited_cut",0) is None and len(rows)==CASES
    agreement=complete and all(r["disposition"]=="excluded" for r in rows)
    print(dumps(dict(head=HEAD,caller=CALLER,pins=PINS,prime=PRIME,controls=checks,case_count=CASES,
        cap_cases=CAP,cap_seconds=SECONDS,group=GROUP,cohort=[339,1101],counts=Counter(r["disposition"] for r in rows),
        rows=rows,complete=complete,agreement=agreement,progress=progress,timeout=timeout,
        original_minor_axes_nonzero=sum(bool(r["primary_minor_det_mod_65537"]) for r in rows),
        unresolved_selected=[k for k in chosen if k not in out or out[k]["disposition"]!="excluded"],
        same_group_unselected=same_group_pending,total_unselected=total_pending),indent=2,sort_keys=True))
    if not agreement:
        raise SystemExit(2)


if __name__=="__main__":
    main()
