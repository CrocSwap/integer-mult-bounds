"""Price and check the final read-free role-532 temporal public span."""
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
import sys
from time import monotonic

ROOT = Path(__file__).resolve().parents[1]
ROLE, ENTRY, EXIT = 532, 44611, 46018
SOURCES = ((46019,363,Q(-1)), (58282,232,Q(2)))
PINS = {
    "inputs/7334-WORD.json.gz": "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
    "inputs/R132-PRICE.json": "66d7496dfebb3373aae7c702641877134f1caf48e0dca7bfc13f33a15999d489",
    "inputs/R134-PRICE.json": "76fe970dde53c19b1a068d705344a50afbd3c9a1a1dcd863d6fd605451119ac8",
    "inputs/R134-RESULT.json": "26d1dd900720a87cbc483bd79538066d45f1a52a0801e25e1bce1617e52032eb",
    "inputs/aggregate.py": "8bf1b91d7fc0937305466686522f5fb3920c66c71830acfc94adde84ba4f49e1",
    "inputs/donor_span.py": "4d5306e2c0b7e91c79d22c82e8e760aed2c311979298c558e631975d4d1ae5b1",
}


def unique(pairs):
    obj = dict(pairs)
    if len(obj) != len(pairs):
        raise ValueError("duplicate JSON key")
    return obj


def read(path):
    data = (ROOT/path).read_bytes()
    if sha256(data).hexdigest()!=PINS[path]:
        raise ValueError(f"changed dependency {path}")
    return data


def quote():
    old, later, census = (loads(read(path),object_pairs_hook=unique)
         for path in ("inputs/R132-PRICE.json","inputs/R134-PRICE.json","inputs/R134-RESULT.json"))
    assert old["head"]==later["head"]==census["head"]=="aaeec8c0acf01e99a5f331ef363a698d9c084ace"
    assert old["caller_head"]==later["caller_head"]=="07a76c5e2738882c0cb322278e56f6cae3c9885d"
    assert old["anchors"][str(ROLE)]==EXIT
    assert old["delta_paid_per_edit"]==later["delta_paid_per_edit"]=={"1":-17}
    assert old["delta_productive_per_edit"]==later["delta_productive_per_edit"]=={"8":17,"9":-17}
    scope = next(x for x in later["candidates"] if x["role"]==ROLE)
    assert (scope["entry_clock"],scope["terminal_clock"])==(ENTRY,EXIT)
    assert scope["contacts"]==[[t,"destination",["ADD",ROLE,s,str(q),127]] for t,s,q in SOURCES]
    at,probe,target=(old["quotes"][k] for k in ("old_crossing_upper","probe","moonshot"))
    assert Q(probe["one_edit_margin"][0])>0 and Q(probe["one_edit_one_additional_raw_paid_rank_one"][1])<0
    assert Q(target["one_edit_margin"][1])<0
    return dict(head=old["head"],caller=old["caller_head"],pins=PINS,scope=scope,compatible_cap=1,
        paid_delta=old["delta_paid_per_edit"],productive_delta=old["delta_productive_per_edit"],
        paid=110502,productive=22461,surplus=1424,gross=at["one_edit_gross"],
        probe=probe["one_edit_margin"],fixed_target=target["one_edit_margin"],
        cut_cap=1407,pair_cap=20000,seconds_cap=25)


def run(p):
    deadline = monotonic()+23
    read("inputs/aggregate.py")
    read("inputs/donor_span.py")
    support = run_path(str(ROOT/"inputs/aggregate.py"))
    rows = run_path(str(ROOT/"inputs/donor_span.py"))
    controls = support["controls"](rows)
    raw = decompress(read("inputs/7334-WORD.json.gz"))
    assert sha256(raw).hexdigest()=="9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
    word = loads(raw,object_pairs_hook=unique)
    tape = word["program"]
    assert len(tape)==76466
    assert tape[ENTRY]==["MOVE",ROLE,p["scope"]["entry_chart"],207,False]
    assert tape[EXIT]==["MOVE",ROLE,207,127,False]
    assert (word["initial"][ROLE],word["final"][ROLE])==(3,127)
    touched = [t for t,(op,r,*a) in enumerate(tape)
               if t>ENTRY and (r==ROLE or op in {"ADD","COPY"} and a[0]==ROLE)]
    assert [t for t in touched if t>EXIT]==[t for t,_,_ in SOURCES]
    assert all(tape[t]==["ADD",ROLE,s,str(q),127] for t,s,q in SOURCES)
    last = max([ENTRY]+[t for t in touched if t<EXIT])
    cuts = list(range(last+1,EXIT+1))
    assert 0<len(cuts)<=p["cut_cap"]
    banks,values = rows["snapshot"](word,{t:{(207,ROLE)} for t in cuts},
                                   {t:{s} for t,s,_ in SOURCES},deadline)
    pending = [t for t in cuts if (t,207,ROLE) not in banks]
    aggregate,vectors,slots,seen = {},{},{},set()
    pairs,result = 0,None
    if not pending and all((t,s) in values for t,s,_ in SOURCES):
        for t,s,q in SOURCES:
            rows["axpy"](aggregate,values[t,s],q)
        for t in cuts:
            for role,vector in sorted(banks[t,207,ROLE].items()):
                if role>=word["public"]:
                    continue
                pairs+=1
                key = role,tuple(sorted(vector.items()))
                if key not in seen:
                    seen.add(key)
                    i = len(slots)
                    vectors[i],slots[i] = vector,[t,207,role]
            if pairs>p["pair_cap"] or monotonic()>=deadline:
                pending = [u for u in cuts if u>=t]
                break
        if not pending:
            result = support["exact_span"](aggregate,vectors,deadline,rows)
    return dict(head=p["head"],caller=p["caller"],pins=PINS,controls=controls,
        last_contact=[last,tape[last]],cuts=[cuts[0],cuts[-1]],cut_count=len(cuts),cut_role_pairs=pairs,
        distinct_role_rows=len(vectors),slots=slots,aggregate={i:str(q) for i,q in aggregate.items()},
        unvisited_cuts=pending,disposition=result)


def main():
    assert __debug__
    p = quote()
    price_only = sys.argv[1:]==["--price-only"]
    assert price_only or not sys.argv[1:]
    out = p if price_only else run(p)
    print(dumps(out,indent=2,sort_keys=True))
    if not price_only and (out["unvisited_cuts"] or out["disposition"] is None):
        raise SystemExit(2)


if __name__=="__main__":
    main()
