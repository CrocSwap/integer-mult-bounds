"""Classify original-source retimings on five pinned public MOVE pairs."""
from bisect import bisect_left
from collections import Counter, defaultdict
from gzip import decompress
from hashlib import sha256
import json
from pathlib import Path
from signal import SIGALRM, alarm, signal
from time import monotonic

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    "lead/PRICE.json":"8fbd560cf7708b99609614a0b96d02b55efc55304225ddffa5dd223ed49d4073",
    "inputs/7334-WORD.json.gz":"4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
}


def read(path):
    raw=(ROOT/path).read_bytes()
    if sha256(raw).hexdigest()!=PINS[path]:
        raise ValueError(f"changed dependency {path}")
    return raw


def chart_at(clocks,frames,initial,cut):
    i=bisect_left(clocks,cut)
    return frames[i-1] if i else initial


def stable_window(writes,old,size):
    i=bisect_left(writes,old)
    assert i==len(writes) or writes[i]!=old
    return (writes[i-1]+1 if i else 0,writes[i] if i<len(writes) else size)


def stop(*_):
    raise TimeoutError("hard retiming cap")


def main():
    assert __debug__
    price=json.loads(read("lead/PRICE.json"))
    lim=price["limits"]
    assert chart_at([3],[4],2,3)==2 and chart_at([3],[4],2,4)==4
    assert stable_window([2,5],3,8)==(3,5)
    signal(SIGALRM,stop)
    alarm(lim["runner_seconds"])
    deadline=monotonic()+18
    counts,rows=Counter(),[]
    next_event,next_cut,reason=None,None,None
    try:
        raw=decompress(read("inputs/7334-WORD.json.gz"))
        assert sha256(raw).hexdigest()==price["payload_sha256"]
        word=json.loads(raw)
        tape=word["program"]
        n=word["public"]
        assert len(tape)==lim["events"] and n==1501
        sources={r["add"][1][2] for r in price["candidates"]}
        movers={r["key"][2] for r in price["candidates"]}
        moves,writes,contacts=defaultdict(list),defaultdict(list),defaultdict(list)
        for t,event in enumerate(tape):
            next_event=t
            if t%128==0 and monotonic()>=deadline:
                raise TimeoutError("incident index cap")
            op,d,*args=event
            if d in sources:
                (moves if op=="MOVE" else writes)[d].append((t,event))
            used=(d,args[0]) if op in ("ADD","COPY") else (d,)
            for r in used:
                if r in movers:
                    contacts[r].append((t,event))
        next_event=None
        for row in price["candidates"]:
            f,g,d=row["key"]
            a,b,c=row["charts"]
            old,add=row["add"]
            s=add[2]
            assert 0<=s<n and s!=d and f<old<g
            assert [(t,e) for t,e in contacts[d] if f<=t<=g]==[(f,["MOVE",d,a,b,False]),(old,add),(g,["MOVE",d,b,c,False])]
            initial=word["initial"][s]
            clocks=[t for t,_ in moves[s]]
            frames=[e[3] for _,e in moves[s]]
            assert chart_at(clocks,frames,initial,old)==b
            assert chart_at(clocks,frames,initial,len(tape))==word["final"][s]
            lo,hi=stable_window([t for t,_ in writes[s]],old,len(tape))
            item={"move_pair":row["key"],"original_add":row["add"],"source":s,
                  "unchanged_row_window":[lo,hi],"cuts":[],"counts":Counter(),
                  "source_moves":[[t,e] for t,e in moves[s] if f<=t<=g],
                  "source_writes":[[t,e] for t,e in writes[s] if f<=t<=g]}
            rows.append(item)
            for side,chart in (("entrance",a),("exit",c)):
                intervals=[]
                item["cuts"].append({"side":side,"chart":chart,"intervals":intervals})
                for cut in range(f+1,g+1):
                    if cut==old:
                        continue
                    next_cut=[*row["key"],side,cut]
                    if sum(counts.values())>=lim["typed_cuts"] or monotonic()>=deadline:
                        raise TimeoutError("typed cut cap")
                    actual=chart_at(clocks,frames,initial,cut)
                    status=("different chart" if actual!=chart else "source write" if not lo<=cut<=hi else "exact unchanged source")
                    item["counts"][status]+=1
                    counts[status]+=1
                    if intervals and intervals[-1][1]+1==cut and intervals[-1][2:]==[status,actual]:
                        intervals[-1][1]=cut
                    else:
                        intervals.append([cut,cut,status,actual])
        assert len(rows)==lim["pair_windows"] and sum(counts.values())==lim["typed_cuts"]
        next_cut=None
    except TimeoutError as exc:
        reason=str(exc)
    finally:
        alarm(0)
    result={"head":price["head"],"pins":PINS,"limits":lim,"rows":rows,"counts":counts,
            "controls":["pre-event source chart","post-MOVE source chart","source-write boundaries"],
            "first_unvisited_event":next_event,"first_unvisited_cut":next_cut,"timeout":reason}
    print(json.dumps(result,indent=2,sort_keys=True))
    if reason:
        raise SystemExit(2)


if __name__=="__main__":
    main()
