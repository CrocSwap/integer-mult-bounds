"""Price and check fixed-clock terminal coframe closure."""
from collections import defaultdict
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
from json import dumps,loads
from pathlib import Path
import sys
from time import monotonic

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    "inputs/7334-WORD.json.gz": "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
    "inputs/R92-PRICE.json": "05d7a5ebdd2eeedd6c8f534e8e2eeac22484daf9f387f4a6b88cc9eed22a6b8f",
    "inputs/R132-PRICE.json": "66d7496dfebb3373aae7c702641877134f1caf48e0dca7bfc13f33a15999d489",
}


def unique(pairs):
    obj = dict(pairs)
    if len(obj)!=len(pairs):
        raise ValueError("duplicate JSON key")
    return obj


def read(path):
    raw=(ROOT/path).read_bytes()
    if sha256(raw).hexdigest()!=PINS[path]:
        raise ValueError(f"changed dependency {path}")
    return raw


def price():
    cohort,old=(loads(read(path),object_pairs_hook=unique)
                for path in ("inputs/R92-PRICE.json","inputs/R132-PRICE.json"))
    assert cohort["head"]==old["head"]=="aaeec8c0acf01e99a5f331ef363a698d9c084ace"
    assert cohort["caller_head"]==old["caller_head"]=="07a76c5e2738882c0cb322278e56f6cae3c9885d"
    roles=cohort["endpoint_cohort"]
    assert roles==sorted(set(roles)) and len(roles)==615
    assert old["delta_paid_per_edit"]=={"1":-17}
    assert old["delta_productive_per_edit"]=={"8":17,"9":-17}
    a,b,t=(old["quotes"][key] for key in ("old_crossing_upper","probe","moonshot"))
    whole=len(roles)*Q(a["one_edit_gross"][1])
    target=Q(t["old_margin"][1])+len(roles)*Q(t["one_edit_gross"][1])
    assert target<0<Q(b["one_edit_margin"][0])
    return dict(head=cohort["head"],caller=cohort["caller_head"],pins=PINS,roles=roles,
                one_gross=a["one_edit_gross"],complete_one_probe=b["one_edit_margin"],
                paid_delta=old["delta_paid_per_edit"],productive_delta=old["delta_productive_per_edit"],
                paid_before=110519,productive=22461,rank_surplus=1424,
                whole_gross_upper=str(whole),fixed_target_complete_upper=str(target),
                event_cap=76466,case_cap=len(roles),runner_seconds_cap=25)


def span(frame):
    out={0}
    for v in frame:
        assert v not in out
        out.update(v^w for w in tuple(out))
    return out


def components(graph,blockers):
    seen=set()
    out=[]
    for r in sorted(graph):
        if r in seen:
            continue
        todo=[r]
        group=set()
        while todo:
            j=todo.pop()
            if j in group:
                continue
            group.add(j)
            todo.extend(graph[j]-group)
        seen.update(group)
        why=sorted([*item] for j in group for item in blockers[j])
        out.append(dict(roles=sorted(group),first_exterior=why[0] if why else None,
                        exterior_event_count=len(why)))
    return out


def audit(word,quote):
    deadline=monotonic()+23
    roles=quote["roles"]
    n=word["public"]
    tape=word["program"]
    assert len(tape)==quote["event_cap"]
    literal = [r for r in range(n) if (word["initial"][r],word["final"][r])==(3,127)]
    assert sorted(roles+[319])==literal and 319 not in roles
    excluded_anchor = next((t,e) for t,e in reversed(list(enumerate(tape)))
                           if e[0]=="MOVE" and e[1]==319)
    assert excluded_anchor[1]==["MOVE",319,1089,127,False]
    a,b,c=[span(word["frames"][i]) for i in (3,207,127)]
    assert a<b<c and [len(s) for s in (a,b,c)]==[1,256,512]
    last={}
    for t,e in enumerate(tape):
        if e[0]=="MOVE" and e[1] in roles:
            last[e[1]]=(t,e)
    anchors={r:t for r,(t,e) in last.items() if e==["MOVE",r,207,127,False]}
    state=word["initial"][:]+[None]*word["owned_fields"]
    graph={r:set() for r in anchors}
    blockers=defaultdict(list)
    edges=[]
    lowered=set()
    unary=[]
    for t,(op,r,*a) in enumerate(tape):
        if t%128==0 and monotonic()>=deadline:
            return dict(unresolved=sorted(anchors),first_unvisited_event=t)
        old=state[r]
        if op=="MOVE":
            assert old==a[0] and a[2]==(r>=n) and r not in lowered
            state[r]=a[1]
            if anchors.get(r)==t:
                lowered.add(r)
        elif op=="INIT":
            assert r>=n and old is None
            state[r]=a[0]
        elif op=="CLEAR":
            assert r>=n and old==a[0]
            state[r]=None
        else:
            assert op in {"ADD","COPY","SCALE"} and old==a[-1]
            if op=="SCALE":
                if r in lowered:
                    assert old==127 and Q(a[0])
                    unary.append([t,r,a[0]])
                continue
            s=a[0]
            assert r!=s and state[s]==old
            if r in lowered or s in lowered:
                assert old==127
                if r in lowered and s in lowered:
                    assert op=="ADD"
                    graph[r].add(s)
                    graph[s].add(r)
                    edges.append([t,r,s,a[1]])
                else:
                    inside,outside=(r,s) if r in lowered else (s,r)
                    blockers[inside].append([t,inside,outside,op,a[1]])
    assert lowered==set(anchors) and state==word["final"]+[None]*word["owned_fields"]
    groups=components(graph,blockers)
    assert sorted(x for g in groups for x in g["roles"])==sorted(anchors)
    return dict(anchors=anchors,edges=edges,unary=unary,groups=groups,excluded_anchor=excluded_anchor,
                survivors=[g["roles"] for g in groups if g["first_exterior"] is None],
                unresolved=[],first_unvisited_event=None)


def controls():
    graph={1:{2},2:{1},3:set()}
    blocked=defaultdict(list,{2:[[9,2,9,"ADD","1"]]})
    out=components(graph,blocked)
    assert out[0]["roles"]==[1,2] and out[0]["first_exterior"]==[9,2,9,"ADD","1"]
    assert out[1]["roles"]==[3] and out[1]["first_exterior"] is None
    return ["exterior edge propagates to the full component","isolated free component"]


def main():
    assert __debug__
    quote=price()
    if sys.argv[1:]==["--price-only"]:
        print(dumps(quote,indent=2,sort_keys=True))
        return
    assert not sys.argv[1:]
    data=decompress(read("inputs/7334-WORD.json.gz"))
    assert sha256(data).hexdigest()=="9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
    result=audit(loads(data,object_pairs_hook=unique),quote)
    print(dumps(dict(head=quote["head"],caller=quote["caller"],pins=PINS,controls=controls(),**result),
                indent=2,sort_keys=True))
    if result["unresolved"]:
        raise SystemExit(2)


if __name__=="__main__":
    main()
