"""Independent forward mixed ADD contact chronology."""
from collections import defaultdict
from hashlib import sha256
import gzip
import json
from pathlib import Path
import sys
from time import monotonic

HEAD = "9d0119eb12fbd9fa534b48cd37b68e7099757b91"
PRICE = "c83fd7c8cc34b1fdef6ca889da91f18315d8d7ba244c284909023ac6f296bbb6"
WORD = "c404b9b61220e6cf740d85276df2828bbb4a9d68a4d44b5e283f8d96f78c0fd9"


def read(path, digest):
    data = Path(path).read_bytes()
    if sha256(data).hexdigest() != digest:
        raise ValueError("changed input")
    return data


def check(word, cap_seconds):
    deadline = monotonic()+cap_seconds
    tape, n = word["program"], word["public"]
    main = set(word["live"]) | {i+112 for i in word["live"]}
    main.update(word["hosted"]["X2"])
    main.update(word["hosted"]["Y2"])
    excluded = main | {863,1355,1568}
    last, wait, candidates = {}, defaultdict(list), []
    t = -1
    for t,(op,dst,*args) in enumerate(tape):
        if t%256 == 0 and monotonic() >= deadline:
            return dict(exhausted=False, first_unvisited_event=t, pending=len(candidates))
        roles = [dst,args[0]] if op in ("ADD","COPY") else [dst]
        for r in roles:
            for row,j in wait.pop(r, ()):
                row["after"][j]=t
        if op == "ADD" and (dst<n) != (args[0]<n):
            row=dict(clock=t, roles=roles, old_chart=args[-1],
                     before=[last.get(r) for r in roles],after=[None,None])
            candidates.append(row)
            for j,r in enumerate(roles):
                wait[r].append((row,j))
        for r in roles:
            last[r]=t
    for row in candidates:
        row["has_four_moves"] = all(k is not None and tape[k][0]=="MOVE"
                                    for k in row["before"]+row["after"])
        row["excluded_operand"] = bool(excluded.intersection(row["roles"]))
    keys = [r["clock"] for r in candidates if r["has_four_moves"] and not r["excluded_operand"]]
    return dict(exhausted=True, literal_events=t+1, cases=candidates,
                all_four_moves=[r["clock"] for r in candidates if r["has_four_moves"]],
                eligible_four_move_sites=keys)


def controls():
    w=dict(public=1,live=[],hosted={"X2":[],"Y2":[]},program=[
      ["MOVE",0,0,1,False],["MOVE",1,0,1,True],["ADD",0,1,"-2",1],
      ["MOVE",0,1,2,False],["MOVE",1,1,2,True]])
    assert check(w,10)["eligible_four_move_sites"] == [2]
    w["program"].insert(2,["SCALE",0,"2",1])
    assert not check(w,10)["eligible_four_move_sites"]
    return ["four literal MOVE neighbors", "intervening scalar contact"]


if __name__=="__main__":
    assert json.loads(read(sys.argv[1],PRICE))["head"]==HEAD
    word=json.loads(gzip.decompress(read(sys.argv[2],WORD)))
    answer=check(word,23)
    answer.update(head=HEAD,price_sha256=PRICE,word_sha256=WORD,controls=controls())
    print(json.dumps(answer,indent=2,sort_keys=True))
