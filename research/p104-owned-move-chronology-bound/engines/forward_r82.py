"""Strict one-ADD commutation gate for owned monotone MOVE contractions."""
from collections import Counter
from fractions import Fraction
from gzip import decompress
from hashlib import sha256
import json
from pathlib import Path
import sys
from time import monotonic

HEAD="aaeec8c0acf01e99a5f331ef363a698d9c084ace"
WORD="4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a"
PRICE="82baf8740dfc695d304602d92bd3888961c965f76a5bcb4784cbd4f9726e7ee6"


def checked(path,want,gzip=False):
    data=path.read_bytes()
    if sha256(data).hexdigest()!=want:
        raise ValueError(f"changed input: {path.name}")
    return json.loads(decompress(data) if gzip else data)


def span(frame):
    points={0}
    for b in frame:
        assert b not in points
        points|={p^b for p in points}
    return points


def touched(e):
    return e[1:3] if e[0] in ("ADD","COPY") else e[1:2]


def barrier(e,owner,peer,peer_mutated):
    op=e[0]
    roles=touched(e)
    if owner in roles:
        return None if op=="MOVE" else "owner chronology"
    if peer not in roles or op=="MOVE":
        return None
    if op=="ADD" and e[2]==peer and e[1] not in (owner,peer) and not peer_mutated:
        return None
    return "counterpart chronology"


def snapshot(word,wanted,deadline):
    public=word["public"]
    active=word["initial"]+[None]*word["owned_fields"]
    lifetimes=[-1]*public+[None]*word["owned_fields"]
    data={}
    for t,e in enumerate(word["program"]):
        if (t%128==0 or t in wanted) and monotonic()>=deadline:
            break
        if t in wanted:
            data[t]={r:(active[r],lifetimes[r]) for r in wanted[t]}
        if t==max(wanted):
            break
        op,r,*args=e
        if op=="MOVE":
            assert active[r]==args[0] and args[2]==(r>=public)
            active[r]=args[1]
        elif op=="INIT":
            assert active[r] is None and lifetimes[r] is None and r>=public
            active[r],lifetimes[r]=args[0],t
        elif op=="CLEAR":
            assert active[r]==args[0] and r>=public and lifetimes[r] is not None
            active[r]=lifetimes[r]=None
        else:
            assert op in ("ADD","COPY","SCALE")
            assert all(active[s]==args[-1] for s in touched(e))
    return data


def classify(p,word,states,end,c):
    r,s=p["owner"],p["peer"]
    f,g=p["move_clocks"]
    t,args=p["literal_ADD"]
    a,b,z=p["chart_path"]
    tape=word["program"]
    assert f<t<g and tape[t]==["ADD",*args]
    assert tape[f]==["MOVE",r,a,b,True] and tape[g]==["MOVE",r,b,z,True]
    assert {r,s}==set(args[:2]) and Fraction(args[2]) and args[3]==b
    assert (p["owner_access"]=="source")==(args[1]==r)
    assert [i for i in range(f+1,g) if r in touched(tape[i])]==[t]
    x,y,w=map(lambda j:span(word["frames"][j]),(a,b,z))
    assert x<y<w or w<y<x
    assert abs(len(w).bit_length()-len(x).bit_length())==p["paid_new"]
    required=a if end=="entrance" else z
    obs,peer_life=states[c][s]
    owner_life=states[c][r][1]
    assert states[t][r][0]==states[t][s][0]==b
    blockers=[]
    path=range(c,t) if c<t else range(t+1,c)
    for k in path:
        e=tape[k]
        if why:=barrier(e,r,s,args[0]==s):
            blockers.append([k,e,why])
    failures=[]
    if obs!=required:
        failures.append("counterpart chart")
    if owner_life is None or owner_life!=states[t][r][1] or peer_life is None or peer_life!=states[t][s][1]:
        failures.append("changed lifetime")
    if blockers:
        failures.append("crossed incident barrier")
    return dict(key=[r,f,g,end,c],peer=s,original_add=[t,args],required_chart=required,
                actual_peer_chart=obs,owner_lifetime=owner_life,peer_lifetime=peer_life,
                crossed_incident_barriers=blockers,failures=failures,
                decision="excluded" if failures else "exact normalized survivor")


def controls():
    assert barrier(["ADD",4,2,"1",9],1,2,True)=="counterpart chronology"
    assert barrier(["ADD",4,2,"1",9],1,2,False) is None
    assert barrier(["ADD",2,4,"1",9],1,2,False)=="counterpart chronology"
    assert barrier(["COPY",4,2,"1",9],1,2,False)=="counterpart chronology"
    assert barrier(["CLEAR",2,9],1,2,False)=="counterpart chronology"
    assert barrier(["MOVE",2,9,12,True],1,2,True) is None
    return ["peer read must follow update","read-only peer commutation","peer write barrier",
            "guarded COPY barrier","owned lifetime barrier","coframe MOVE transports only"]


def main():
    root=Path(sys.argv[1])
    quote=checked(root/"price/PRICE.json",PRICE)
    assert quote["head"]==HEAD and quote["word_sha256"]==WORD and quote["typed_end_placements"]==10
    word=checked(root/"inputs/7334-WORD.json.gz",WORD,gzip=True)
    candidates=quote["candidates"]
    assert len(candidates)==5
    work=[]
    wanted={}
    for p in candidates:
        t=p["literal_ADD"][0]
        want={p["owner"],p["peer"]}
        wanted.setdefault(t,set()).update(want)
        for end,(first,last) in sorted(p["cut_windows_pre_event"].items()):
            for c in range(first,last+1):
                wanted.setdefault(c,set()).update(want)
                work.append((p,end,c))
    assert len(work)==51
    cap=monotonic()+18
    states=snapshot(word,wanted,cap)
    checked_rows=[]
    unvisited=[]
    for p,end,c in work:
        if monotonic()>=cap or not {p["literal_ADD"][0],c}<=states.keys():
            unvisited.append([p["owner"],*p["move_clocks"],end,c])
            continue
        checked_rows.append(classify(p,word,states,end,c))
    print(json.dumps(dict(head=HEAD,price_sha256=PRICE,word_sha256=WORD,controls=controls(),
        case_cap=51,placement_cap=10,seconds_cap=18,
        status="CAPPED" if unvisited else "EXHAUSTED",
        counts=Counter(row["decision"] for row in checked_rows),decisions=checked_rows,
        survivors=[row for row in checked_rows if not row["failures"]],unvisited=unvisited),
        indent=2,sort_keys=True))


if __name__=="__main__":
    main()
