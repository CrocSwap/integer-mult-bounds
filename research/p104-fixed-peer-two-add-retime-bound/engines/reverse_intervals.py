"""Verify four frozen C-side two-ADD retiming windows by reverse intervals."""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
from json import dumps,loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM,alarm,signal
from time import monotonic
import sys

ROOT=Path(__file__).resolve().parent
HEAD="aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CALLER="07a76c5e2738882c0cb322278e56f6cae3c9885d"
WORD="4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a"
PAYLOAD="9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
PINS={
    "inputs/PRICE.json":"8226a2b9c9240455d6fcdaf3a38929e3336e89f35aed3f15b81564f07ed8387f",
    "inputs/7334-WORD.json.gz":WORD,
    "inputs/reverse_routes.py":"a81a41c1cd33de0a612b568cbf470003d933a344396bc6dc53b85a91888dfe27",
}
EVENTS,WINDOWS,CUTS,SECONDS=76466,4,4124,20


def unique(items):
    value=dict(items)
    if len(value)!=len(items):
        raise ValueError("duplicate JSON key")
    return value


def authenticate(root):
    raw={}
    for name,digest in PINS.items():
        data=(root/name).read_bytes()
        if sha256(data).hexdigest()!=digest:
            raise ValueError(f"changed dependency: {name}")
        raw[name]=data
    return raw


def frame_span(vectors):
    span={0}
    for vector in vectors:
        assert type(vector) is int and 0<vector<512 and vector not in span
        span|={v^vector for v in span}
    return span


def chart_intervals(role,contacts,initial,final,frames,size):
    current,upper=final,size
    intervals=[]
    for clock,event in reversed(contacts):
        if event[0]!="MOVE":
            continue
        op,r,old,new,owned=event
        assert r==role and not owned and current==new
        assert frame_span(frames[old])<frame_span(frames[new])
        intervals.append([clock+1,upper,current])
        current,upper=old,clock
    assert current==initial
    intervals.append([0,upper,initial])
    intervals.reverse()
    assert intervals[0][0]==0 and intervals[-1][1]==size
    assert all(a[1]+1==b[0] for a,b in zip(intervals,intervals[1:]))
    return intervals


def partition(intervals,lo,hi,target,first_block):
    clip=[]
    for f,g,c in intervals:
        left,right=max(lo,f),min(hi,g)
        if left>right:
            continue
        if first_block is None or right<=first_block:
            clip.append([left,right,c,c==target,True])
        elif first_block<left:
            clip.append([left,right,c,c==target,False])
        else:
            clip.extend([[left,first_block,c,c==target,True],[first_block+1,right,c,c==target,False]])
    assert sum(r-l+1 for l,r,_,_,_ in clip)==hi-lo+1
    return clip


def pair_matrix(contacts,mover,peer):
    matrix=[[Q(1),Q(0)],[Q(0),Q(1)]]
    roles={mover:0,peer:1}
    for _,event in contacts:
        op,d,s,q,_=event
        assert op=="ADD" and set(roles)=={d,s}
        i,j=roles[d],roles[s]
        matrix[i]=[a+Q(q)*b for a,b in zip(matrix[i],matrix[j],strict=True)]
    return matrix,matrix[0][0]*matrix[1][1]-matrix[0][1]*matrix[1][0]


def controls():
    rows=partition([[0,3,6],[4,8,7]],1,7,7,5)
    assert rows==[[1,3,6,False,True],[4,5,7,True,True],[6,7,7,True,False]]
    assert partition([[0,5,6]],4,5,7,4)==[[4,4,6,False,True],[5,5,6,False,False]]
    a,b=pair_matrix([[2,["ADD",8,9,"-1",4]],[3,["ADD",9,8,"1/2",4]]],8,9)
    assert a==[[1,-1],[Q(1,2),Q(1,2)]] and b==1
    return ["pre-event chart and forbidden-contact boundaries","exact signed two-ADD determinant"]


def check_windows(word,price,contacts,deadline,state,rows):
    tape,frames,n=word["program"],word["frames"],word["public"]
    for case in price["cases"]:
        if monotonic()>=deadline:
            raise TimeoutError("frozen window cap")
        first,last,mover=case["key"]
        a,b,c=case["charts"]
        peer=case["peer"]
        pair=[tuple(r) for r in case["original_pair"]]
        t0,t1=(t for t,_ in pair)
        lo,hi=case["late_pre_event_cuts"]
        assert first+1==t0 and t0+1==t1 and (lo,hi)==(t1+1,last)
        assert 0<=mover<n and 0<=peer<n and mover!=peer
        assert (len(frames[b])-len(frames[a]),len(frames[c])-len(frames[b]))==(1,1)
        assert frame_span(frames[a])<frame_span(frames[b])<frame_span(frames[c])
        frozen=[(first,["MOVE",mover,a,b,False]),*pair,(last,["MOVE",mover,b,c,False])]
        assert [r for r in contacts[mover] if first<=r[0]<=last]==frozen
        assert [r for r in contacts[peer] if t0<=r[0]<=t1]==pair
        assert all(e[-1]==b and tape[t]==e for t,e in pair)
        matrix,det=pair_matrix(pair,mover,peer)
        assert [[str(v) for v in row] for row in matrix]==case["normalized_matrix"]
        assert str(det)==case["determinant"]=="1"
        trajectory=chart_intervals(peer,contacts[peer],word["initial"][peer],word["final"][peer],frames,EVENTS)
        assert any(l<=t0<=t1<=h and z==b for l,h,z in trajectory)
        after_pair={t:e for role in (mover,peer) for t,e in contacts[role] if lo<=t<hi and e[0]!="MOVE"}
        first_block=min(after_pair,default=None)
        intervals=partition(trajectory,lo,hi,c,first_block)
        counts=Counter()
        for left,right,chart,in_c,clean in intervals:
            assert left<=right and (chart==c)==in_c
            counts["C clean" if clean and in_c else "C blocked" if in_c else "other clean" if clean else "other blocked"]+=right-left+1
        typed=sum(counts.values())
        assert typed==case["per_endpoint_typed_count"]
        assert state["typed_cuts"]+typed<=CUTS
        state["typed_cuts"]+=typed
        row=dict(key=case["key"],peer=peer,old_chart=b,target_chart=c,window=[lo,hi],
            original_pair=pair,mover_contacts=frozen,peer_chart_path=trajectory,
            first_scalar_or_lifetime_contact=None if first_block is None else [first_block,after_pair[first_block]],
            intervals=intervals,counts=counts,chart_C_cut_count=counts["C clean"]+counts["C blocked"],
            corridor_blocked_cut_count=counts["C blocked"]+counts["other blocked"],
            survivors=[[l,h] for l,h,_,in_c,clean in intervals if in_c and clean])
        rows.append(row)


def main():
    p=ArgumentParser(description=__doc__)
    p.add_argument("--root",type=Path,default=ROOT)
    p.add_argument("--controls-only",action="store_true")
    args=p.parse_args()
    assert __debug__ and sys.version_info[:2]==(3,12)
    checks=controls()
    if args.controls_only:
        print(dumps(checks))
        return
    def stop(*_):
        raise TimeoutError("hard 20-second runner cap")
    signal(SIGALRM,stop)
    alarm(SECONDS)
    deadline=monotonic()+18
    rows,cases=[],[]
    progress=dict(events_replayed=0,first_unvisited_event=EVENTS-1,typed_cuts=0)
    timeout=None
    try:
        raw=authenticate(args.root)
        price=loads(raw["inputs/PRICE.json"],object_pairs_hook=unique)
        assert price["head"]==HEAD and price["caller"]==CALLER and price["word_sha256"]==WORD
        lim=price["caps"]
        assert (lim["windows"],lim["late_cuts"],lim["runner_seconds"])==(WINDOWS,CUTS,SECONDS)
        cases=price["cases"]
        assert len(cases)==WINDOWS and len({role for c in cases for role in (c["peer"],c["key"][2])})==8
        assert len({t for c in cases for t in c["key"][:2]})==8
        word_raw=decompress(raw["inputs/7334-WORD.json.gz"])
        assert sha256(word_raw).hexdigest()==price["payload_sha256"]==PAYLOAD
        word=loads(word_raw,object_pairs_hook=unique)
        engine=run_path(str(args.root/"inputs/reverse_routes.py"))
        targets={r for c in cases for r in (c["peer"],c["key"][2])}
        contacts=engine["walk"](word,targets,deadline,progress)
        check_windows(word,price,contacts,deadline,progress,rows)
    except TimeoutError as exc:
        timeout=str(exc)
    finally:
        alarm(0)
    complete=timeout is None
    if complete:
        assert len(rows)==WINDOWS and progress["events_replayed"]==EVENTS and progress["typed_cuts"]==CUTS
    counts=Counter()
    for row in rows:
        counts.update(row["counts"])
    print(dumps(dict(head=HEAD,caller=CALLER,pins=PINS,controls=checks,complete=complete,timeout=timeout,
        caps=dict(events=EVENTS,cuts=CUTS,windows=WINDOWS,seconds=SECONDS),progress=progress,rows=rows,counts=counts,
        unvisited=[r["key"] for r in cases[len(rows):]]),indent=2,sort_keys=True))
    if not complete:
        raise SystemExit(2)


if __name__=="__main__":
    main()
