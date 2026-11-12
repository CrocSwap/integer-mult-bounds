"""Independent backward exact input support of one lower-rank owned descent."""
from collections import Counter,defaultdict
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
from json import dumps,loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM,alarm,signal
from time import monotonic

ROOT=Path(__file__).resolve().parent
PINS={
    "inputs/7334-WORD.json.gz":"4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
    "inputs/PRICE.json":"ec9a60268731327b5628fea15510bb2a5b663c67d0a308ef6db5f077045c9ce3",
    "inputs/reverse_span.py":"f8b48f2ed99d003e20f5b3fb2270603c4edbc3ce9a01484102816aa2710ce9ff",
}
HEAD="aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CALLER="07a76c5e2738882c0cb322278e56f6cae3c9885d"
PAYLOAD="9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
OWNER,CLOCK,SHADOW=1503,39811,1504
ANCESTOR,EARLY=146,38967
SECONDS=20


def unique(items):
    data=dict(items)
    assert len(data)==len(items)
    return data


def read(name):
    raw=(ROOT/name).read_bytes()
    assert sha256(raw).hexdigest()==PINS[name],name
    return raw


def stop(*_):
    raise TimeoutError("20-second exact row cap")


def main():
    assert __debug__
    signal(SIGALRM,stop)
    alarm(SECONDS)
    until=monotonic()+SECONDS-1
    price=loads(read("inputs/PRICE.json"),object_pairs_hook=unique)
    assert (price["head"],price["caller"],price["clock"],price["owner"],price["shadow"])==(HEAD,CALLER,CLOCK,OWNER,SHADOW)
    assert Q(price["gross"][0])>67
    raw=decompress(read("inputs/7334-WORD.json.gz"))
    assert sha256(raw).hexdigest()==PAYLOAD
    word=loads(raw,object_pairs_hook=unique)
    tape,frames,initial=map(word.__getitem__,("program","frames","initial"))
    assert len(tape)==76466 and len(initial)==word["public"]==1501
    assert len(frames[520])-len(frames[595])==5 and len(frames[595])-len(frames[3])==1
    assert tape[CLOCK]==["MOVE",OWNER,520,595,True]
    assert tape[EARLY]==["MOVE",ANCESTOR,3,365,False]
    assert not any(e[1]==SHADOW or (e[0] in ("COPY","ADD") and e[2]==SHADOW) for e in tape[:39828])
    assert tape[39828]==["INIT",SHADOW,591]
    read("inputs/reverse_span.py")
    solver=run_path(str(ROOT/"inputs/reverse_span.py"))["transpose_prefix"]
    req=defaultdict(list,{EARLY:[(ANCESTOR,0)],CLOCK:[(OWNER,1)]})
    early,row=[{j:Q(x,d) for j,x in values.items()} for values,d in solver(word,req,2,until)]
    assert all(0<=i<len(initial) for i in early.keys()|row.keys())
    bank=[i for i,c in enumerate(initial) if c==3]
    assert len(bank)==1060
    outside={i:x for i,x in row.items() if initial[i]!=3}
    partition=defaultdict(dict)
    for i,x in row.items():
        partition[initial[i]][i]=x
    piv=min(early)
    ratio=row.get(piv,0)/early[piv]
    disagreement={i:row.get(i,0)-ratio*early.get(i,0) for i in sorted(row.keys()|early.keys())
                  if row.get(i,0)!=ratio*early.get(i,0)}
    assert early
    first=min(outside) if outside else None
    if outside:
        assert first not in bank and row[first]
    alarm(0)
    print(dumps({"head":HEAD,"caller":CALLER,"pins":PINS,"clock":CLOCK,"owner":OWNER,
                 "shadow":SHADOW,"shadow_first_old_contact":39828,"entry_bank_count":len(bank),
                 "basis_columns":len(initial),"seconds_cap":SECONDS,"row":row,
                 "row_groups_by_initial_chart":partition,"group_sizes":Counter(initial[i] for i in row),
                 "outside_entry_chart":outside,"first_outside":[first,str(row[first]),initial[first]] if outside else None,
                 "ancestor":{"role":ANCESTOR,"clock":EARLY,"row":early,
                             "ratio_at_first_pivot":ratio,"disagreement":disagreement},
                 "status":"entry chart3 excludes" if outside else "entry chart3 support survives",
                 "price":price},sort_keys=True,indent=2,default=str))


if __name__=="__main__":
    main()
