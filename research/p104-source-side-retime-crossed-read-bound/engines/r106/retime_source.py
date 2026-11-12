"""Exact coframe and recipient-contact gate for source-side sole-ADD retiming."""
from bisect import bisect_left
from collections import Counter, defaultdict
from fractions import Fraction
from gzip import decompress
from hashlib import sha256
import json
from pathlib import Path
from signal import SIGALRM, alarm, signal
from time import monotonic

ROOT=Path(__file__).resolve().parents[1]
PINS={
    "lead/PRICE.json":"4ac52a9f1b56a86cb96d9eb6f3be9f635a58b7341ce10905c4a40e296c0f7f8a",
    "inputs/7334-WORD.json.gz":"4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
}


def checked(path):
    raw=(ROOT/path).read_bytes()
    if sha256(raw).hexdigest()!=PINS[path]:
        raise ValueError(f"changed dependency {path}")
    return raw


def contact_roles(event):
    op,r,*args=event
    return (r,args[0]) if op in ("ADD","COPY") else (r,)


def barrier(event,d):
    op,r,*_=event
    return op!="MOVE" and not (op=="ADD" and r==d)


def chart_at(clocks,labels,initial,cut):
    i=bisect_left(clocks,cut)
    return labels[i-1] if i else initial


def stable(clocks,at,size):
    i=bisect_left(clocks,at)
    assert i==len(clocks) or clocks[i]!=at
    return (clocks[i-1]+1 if i else 0,clocks[i] if i<len(clocks) else size)


def stop(*_):
    raise TimeoutError("hard runner cap")


def main():
    assert __debug__
    price=json.loads(checked("lead/PRICE.json"))
    limits=price["limits"]
    assert stable([2,5],3,8)==(3,5)
    assert barrier(["ADD",7,3,"1",1],3) and not barrier(["ADD",3,7,"1",1],3)
    assert barrier(["COPY",7,3,"1",1],3) and barrier(["SCALE",3,"-1",1],3)
    assert chart_at([2],[3],1,2)==1 and chart_at([2],[3],1,3)==3
    controls=["pre-event chart","incoming ADD commutes","source read and COPY barriers","SCALE barrier","nearest barriers"]
    signal(SIGALRM,stop)
    alarm(limits["seconds"])
    deadline=monotonic()+18
    counts,rows,candidates=Counter(),[],[]
    reason=unvisited_event=unvisited_cut=None
    try:
        raw=decompress(checked("inputs/7334-WORD.json.gz"))
        assert sha256(raw).hexdigest()==price["payload_sha256"]
        word=json.loads(raw)
        tape=word["program"]
        n=word["public"]
        assert len(tape)==limits["events"] and n==1501
        roles={x for r in price["candidate_rows"] for x in (r["key"][2],r["add"][1][1])}
        log=defaultdict(list)
        for t,e in enumerate(tape):
            unvisited_event=t
            if t%128==0 and monotonic()>=deadline:
                raise TimeoutError("contact index cap")
            for r in contact_roles(e):
                if r in roles:
                    log[r].append((t,e))
        unvisited_event=None
        for row in price["candidate_rows"]:
            f,g,s=row["key"]
            a,b,c=row["charts"]
            old,add=row["add"]
            _,d,src,k,chart=add
            assert src==s and chart==b and d!=s and d<n and s<n and Fraction(k)
            assert [(t,e) for t,e in log[s] if f<=t<=g]==[(f,["MOVE",s,a,b,False]),(old,add),(g,["MOVE",s,b,c,False])]
            moves=[(t,e[3]) for t,e in log[d] if e[0]=="MOVE"]
            clocks=[t for t,_ in moves]
            labels=[label for _,label in moves]
            initial=word["initial"][d]
            assert chart_at(clocks,labels,initial,old)==b
            assert chart_at(clocks,labels,initial,len(tape))==word["final"][d]
            blocks=[(t,e) for t,e in log[d] if barrier(e,d)]
            lo,hi=stable([t for t,_ in blocks],old,len(tape))
            record=dict(key=row["key"],old_add=row["add"],recipient=d,stable_interval=[lo,hi],
                nearest_barriers=[(t,e) for t,e in blocks if t in (lo-1,hi)],
                recipient_contacts=[(t,e) for t,e in log[d] if f<=t<=g],sides=[],counts=Counter())
            rows.append(record)
            for side,target in (("entrance",a),("exit",c)):
                groups=[]
                record["sides"].append(dict(side=side,target_chart=target,intervals=groups))
                for cut in range(f+1,g+1):
                    if cut==old:
                        continue
                    unvisited_cut=[*row["key"],side,cut]
                    if sum(counts.values())>=limits["typed_cuts"] or monotonic()>=deadline:
                        raise TimeoutError("typed cut cap")
                    actual=chart_at(clocks,labels,initial,cut)
                    if actual!=target:
                        status="wrong chart"
                    elif not lo<=cut<=hi:
                        status="recipient contact barrier"
                    else:
                        status="feasible"
                        candidates.append(dict(key=unvisited_cut,chart=target,old=old,recipient=d,
                                               source=s,full_probe=row["quote"]["full_probe"]))
                    counts[status]+=1
                    record["counts"][status]+=1
                    if groups and groups[-1][1]+1==cut and groups[-1][2:]==[status,actual]:
                        groups[-1][1]=cut
                    else:
                        groups.append([cut,cut,status,actual])
        assert len(rows)==limits["windows"] and sum(counts.values())==limits["typed_cuts"]
        unvisited_cut=None
    except TimeoutError as exc:
        reason=exc.args[0]
    finally:
        alarm(0)
    candidates.sort(key=lambda x:(-Fraction(x["full_probe"][0]),abs(x["key"][-1]-x["old"]),x["key"]))
    print(json.dumps(dict(head=price["head"],pins=PINS,limits=limits,controls=controls,counts=counts,rows=rows,
        candidates=candidates,unvisited_event=unvisited_event,unvisited_cut=unvisited_cut,timeout=reason),
        indent=2,sort_keys=True))
    if reason:
        raise SystemExit(2)


if __name__=="__main__":
    main()
