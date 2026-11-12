"""Reverse chart/incident audit for the two frozen R121 exchange triads."""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction
from functools import cache
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from signal import SIGALRM, alarm, signal
from time import monotonic

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    "plan/PRICE.json": "1d9f68e5cd370846b55f36e522d0b2b2468430179ef9337ec2cf3848c1628894",
    "inputs/7334-WORD.json.gz": "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
}
PEERS = {319:35, 1081:807}
MATRICES = {319:[[0,1],[1,1]],1081:[[-1,1],[1,0]]}
EVENTS = 76466


def read(root,name):
    data = (root/name).read_bytes()
    if sha256(data).hexdigest() != PINS[name]:
        raise ValueError("changed dependency "+name)
    return data


def reduce(v,basis):
    while v and v.bit_length() in basis:
        v ^= basis[v.bit_length()]
    return v


def basis(vectors):
    rows = {}
    for v in vectors:
        q = reduce(v,rows)
        if q:
            rows[q.bit_length()] = q
    return rows


def operator(triad,roles):
    rows = [[Fraction(i==j) for j in range(2)] for i in range(2)]
    for _,(op,d,*a) in triad:
        i = roles.index(d)
        q = Fraction(a[-2])
        if op == "SCALE":
            rows[i] = [q*x for x in rows[i]]
        else:
            assert op == "ADD"
            j = roles.index(a[0])
            rows[i] = [x+q*y for x,y in zip(rows[i],rows[j],strict=True)]
    return rows


def reverse(word,deadline,progress):
    tape,n,m = (word[k] for k in ("program","public","owned_fields"))
    assert (len(tape),n,m)==(EVENTS,1501,68)
    current = word["final"]+[None]*m
    contact = {r:[] for r in (*PEERS,*PEERS.values())}
    copy_guard = set()
    for t in range(EVENTS-1,-1,-1):
        progress["last_unvisited"]=t
        if t%128==0 and monotonic()>=deadline:
            raise TimeoutError("reverse walk cap")
        op,d,*a = tape[t]
        assert 0<=d<len(current) and (d not in copy_guard or op=="INIT")
        after = current[d]
        touched = [d]
        if op=="MOVE":
            old,new,owned=a
            assert after==new and owned==(d>=n)
            current[d]=old
        elif op=="INIT":
            assert d>=n and after==a[0]
            current[d]=None
            copy_guard.discard(d)
        elif op=="CLEAR":
            assert d>=n and after is None
            current[d]=a[0]
        else:
            assert op in ("ADD","COPY","SCALE") and after==a[-1] and Fraction(a[-2])
            if op!="SCALE":
                s=a[0]
                assert s!=d and current[s]==after
                touched.append(s)
            if op=="COPY":
                assert d>=n
                copy_guard.add(d)
        for r in touched:
            if r in contact:
                contact[r].append([t,tape[t],current[r],after if r==d else current[r]])
        progress["events"]+=1
    assert not copy_guard and current==word["initial"]+[None]*m
    progress["last_unvisited"]=None
    return {r:v[::-1] for r,v in contact.items()}


def gates(word,price,contact,out,deadline):
    frames,tape = word["frames"],word["program"]
    ranked = cache(lambda label:basis(frames[label]))
    quote = {(row["side"],*row["peer_old"]):row for row in price["profiles"]}
    assert len(quote)==90
    for group in price["stock"]:
        l,r,h=group["key"]
        a,b,c=group["charts"]
        p=PEERS[h]
        triad=group["contacts"]
        assert all(tape[t]==e for t,e in triad) and operator(triad,[h,p])==MATRICES[h]
        lo,hi=triad[0][0],triad[-1][0]
        rails={}
        for role in (h,p):
            contacts=contact[role]
            before=next(row for row in reversed(contacts) if row[0]<lo)
            after=next(row for row in contacts if row[0]>hi)
            inside=[row for row in contacts if lo<=row[0]<=hi]
            assert [x[:2] for x in inside]==[x for x in triad if
                x[1][1]==role or x[1][0]=="ADD" and x[1][2]==role]
            assert all(x[2:]==[b,b] for x in inside)
            rails[role]=[before,inside,after]
        h_before,_,h_after=rails[h]
        p_before,_,p_after=rails[p]
        assert h_before==[l,["MOVE",h,a,b,False],a,b]
        assert h_after==[r,["MOVE",h,b,c,False],b,c]
        assert p_before[-1]==p_after[-2]==b
        left,right=p_before[-2],p_after[-1]
        assert (a,b,c,left,right)==(3,32,355,32,350)
        assert not frames[a] and ranked(left)==ranked(b)
        assert len(ranked(b))==1 and len(ranked(c))==len(ranked(right))==2
        for label in (c,right):
            assert all(not reduce(x,ranked(label)) for x in frames[b])
        union_rank=len(basis(frames[c]+frames[right]))
        assert union_rank==3
        meet_rank=len(ranked(c))+len(ranked(right))-union_rank
        assert meet_rank==len(ranked(b))==1
        p_q=[len(ranked(b))-len(ranked(left)),len(ranked(right))-len(ranked(b))]
        assert p_q==[0,1]
        for side,d,shift in (("A",a,-1),("C",c,1)):
            if monotonic()>=deadline:
                raise TimeoutError("four-route gate cap")
            legs=[]
            for role,when,src,dst in ((h,"entrance",a,d),(h,"exit",d,c),(p,"entrance",left,d),(p,"exit",d,right)):
                rem=next(([v,reduce(v,ranked(dst))] for v in frames[src] if reduce(v,ranked(dst))),None)
                n=len(ranked(dst))-len(ranked(src))
                valid=rem is None and (n>0 or src==dst)
                legs.append(dict(role=role,direction=when,source=src,destination=dst,rank=n,witness=rem,valid=valid))
            ranks=[x["rank"] for x in legs]
            assert ranks==[1+shift,1-shift,p_q[0]+shift,p_q[1]-shift]
            q=quote.get((side,*p_q))
            if q:
                paid=Counter(r for r in ranks if r>0)
                paid.subtract(r for r in [1,1,*p_q] if r>0)
                assert {str(k):17*v for k,v in paid.items() if v}==q["paid_delta"]
            failed=[[x["role"],x["direction"],x["source"],x["destination"]] for x in legs if not x["valid"]]
            assert len(failed)==1
            out.append(dict(key=group["key"],peer=p,side=side,chart=d,rails=rails,matrix=MATRICES[h],
                peer_outer=[left,right],peer_old_ranks=p_q,paid_old=[1,1,*p_q],paid_new_relaxed=ranks,
                legs=legs,failed_legs=failed,price=q,status="nesting exclusion",
                unique_common_span=dict(lower_join_basis=frames[b],upper_meet_basis=frames[b],
                    upper_union_rank=union_rank,intersection_rank=meet_rank,
                    ranks_unchanged=[1,1,*p_q],upper_bases={c:frames[c],right:frames[right]})))


def controls():
    assert len(basis([1,2,3])) == 2 and reduce(2,basis([1])) == 2
    old,new=(1,1,0,1),(2,0,1,0)
    assert sum(old)==sum(new) and sum(map(bool,old))==sum(map(bool,new))+1
    toy=[[0,["ADD",1,0,"1",4]],[1,["SCALE",0,"-1",4]],[2,["ADD",0,1,"1",4]]]
    assert operator(toy,[0,1])==[[0,1],[1,1]]
    toy[0][1][3]="-1"
    assert operator(toy,[0,1])!=[[0,1],[1,1]]
    return ["GF(2) rank and outside generator","charged compensating rank-one leg","wrong scalar sign"]


def main():
    parser=ArgumentParser()
    parser.add_argument("--root",type=Path,default=ROOT)
    parser.add_argument("--controls-only",action="store_true")
    args=parser.parse_args()
    assert __debug__
    checks=controls()
    price=loads(read(args.root,"plan/PRICE.json"))
    assert price["word_sha256"]==PINS["inputs/7334-WORD.json.gz"]
    assert price["runner_limits"]=={"coframes":4,"literal_events":EVENTS,"physical_prototypes":1,"prototype_seconds":120,"seconds":20,"windows":2}
    assert [row["key"][2] for row in price["stock"]]==list(PEERS)
    if args.controls_only:
        print(dumps({"controls":checks}))
        return 0

    def stop(*_):
        raise TimeoutError("hard 20-second cap")

    signal(SIGALRM,stop)
    alarm(20)
    deadline=monotonic()+18
    progress={"events":0,"last_unvisited":EVENTS-1}
    out,timeout=[],None
    try:
        payload=decompress(read(args.root,"inputs/7334-WORD.json.gz"))
        assert sha256(payload).hexdigest()=="9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
        word=loads(payload)
        contact=reverse(word,deadline,progress)
        gates(word,price,contact,out,deadline)
    except TimeoutError as exc:
        timeout=str(exc)
    finally:
        alarm(0)
    completed={(x["key"][2],x["chart"]) for x in out}
    print(dumps(dict(head=price["head"],caller=price["caller_head"],pins=PINS,progress=progress,
        controls=checks,limits=price["runner_limits"],rows=out,counts=Counter(r["status"] for r in out),
        unvisited=[(h,d) for h in PEERS for d in (3,355) if (h,d) not in completed],timeout=timeout),
        indent=2,sort_keys=True))
    return 2 if timeout else 0


if __name__=="__main__":
    raise SystemExit(main())
