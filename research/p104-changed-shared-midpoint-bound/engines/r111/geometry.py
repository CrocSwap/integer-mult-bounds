"""Test literal closure and exact chart dimensions of one priced component."""
from collections import defaultdict
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
import json
from pathlib import Path
from signal import SIGALRM, alarm, signal
from time import monotonic

ROOT=Path(__file__).resolve().parents[1]
PINS={
    "lead/PRICE.json":"96802c4ee39368c0e0b7d5b245372a979f68047ecbb0ae3517ced7e38dbf9a9a",
    "inputs/7334-WORD.json.gz":"4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
}


def checked(path):
    raw=(ROOT/path).read_bytes()
    if sha256(raw).hexdigest()!=PINS[path]:
        raise ValueError(f"changed dependency {path}")
    return raw


def span(vectors):
    out={0}
    for v in vectors:
        assert 0<v<512 and v not in out
        out|={x^v for x in out}
    return out


def extend(initial,allowed,rank):
    out=list(initial)
    have=span(out)
    for v in sorted(allowed):
        if len(out)==rank:
            break
        if v not in have:
            out.append(v)
            have|={x^v for x in have}
    assert len(out)==rank and have<=allowed
    return out


def basis(wanted):
    return extend([],wanted,len(wanted).bit_length()-1)


def touches(e):
    op,d,*a=e
    return (d,a[0]) if op in ("ADD","COPY") else (d,)


def stop(*_):
    raise TimeoutError("R111 component cap")


def main():
    assert __debug__
    assert span([1,4])=={0,1,4,5} and extend([1],set(range(8)),2)==[1,2]
    signal(SIGALRM,stop)
    alarm(20)
    deadline=monotonic()+18
    p=json.loads(checked("lead/PRICE.json"))
    raw=decompress(checked("inputs/7334-WORD.json.gz"))
    assert sha256(raw).hexdigest()==p["payload_sha256"]
    w=json.loads(raw)
    tape=w["program"]
    assert (len(tape),w["public"])==(76466,1501)
    roles={r[0] for r in p["fields"]}
    log=defaultdict(list)
    for t,e in enumerate(tape):
        if t%128==0 and monotonic()>=deadline:
            raise TimeoutError("contact index")
        for r in touches(e):
            if r in roles:
                log[r].append([t,e])
    fields=[]
    ranks=[]
    for r,a,b,c,f,g in p["fields"]:
        assert tape[f]==["MOVE",r,a,b,False] and tape[g]==["MOVE",r,b,c,False]
        middle=[x for x in log[r] if f<x[0]<g]
        expected=[x for x in p["add_events"] if r in touches(x[1])]
        assert all(tape[t]==e and e[-1]==b and Q(e[3]) for t,e in expected)
        rs=[len(w["frames"][b])-len(w["frames"][a]),len(w["frames"][c])-len(w["frames"][b])]
        assert all(z>0 for z in rs)
        fields.append(dict(role=r,route=[a,b,c],clocks=[f,g],ranks=rs,middle=middle,closed=middle==expected))
        ranks.append(rs)
    assert ranks[0]==ranks[2]==[3,2]
    positive=[v for v in p["positive_relaxed_variants"] if v["old_peer_ranks"]==ranks[1]]
    assert len(positive)<=p["limits"]["actual_offsets"]
    active=all(r["closed"] for r in fields)
    geometry=[]
    if active and positive:
        spans=list(map(span,w["frames"]))
        low={u^v for u in spans[744] for v in spans[263]}
        high=spans[207]&spans[916]
        assert low<=spans[746]<=high and len(spans[746])==64
        for v in positive:
            rank=v["rank"]
            possible=len(low)<=2**rank<=len(high)
            existing=[i for i,s in enumerate(spans) if len(s)==2**rank and low<=s<=high] if possible else []
            new_basis=w["frames"][existing[0]] if existing else extend(basis(low),high,rank) if possible else None
            geometry.append(v|dict(status="geometry survivor" if possible else
                "low union too large" if 2**rank<len(low) else "high intersection too small",
                low_union_basis=basis(low),high_intersection_basis=basis(high),existing_charts=existing,witness_basis=new_basis))
    alarm(0)
    print(json.dumps(dict(head=p["head"],pins=PINS,fields=fields,closed=active,actual_positive_offsets=len(positive),
        results=geometry,controls=["GF(2) span","nested rank extension","exact literal closed component"],
        events=len(tape),limits=p["limits"]),indent=2,sort_keys=True))


if __name__=="__main__":
    main()
