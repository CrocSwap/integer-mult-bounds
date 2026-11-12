"""Reverse exact endpoint and post-MOVE audit for six public helpers."""
from fractions import Fraction
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from signal import SIGALRM, alarm, signal
from time import monotonic

ROOT = Path(__file__).resolve().parent
PINS = {
    "inputs/PRICE.json": "66d7496dfebb3373aae7c702641877134f1caf48e0dca7bfc13f33a15999d489",
    "inputs/LEAD.json": "d8f2d00bae5781188ec420c8756a727ab6b760129053e3a2b68ede1ccf64ff57",
    "inputs/R92-PRICE.json": "05d7a5ebdd2eeedd6c8f534e8e2eeac22484daf9f387f4a6b88cc9eed22a6b8f",
    "inputs/7334-WORD.json.gz": "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
}
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CALLER = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
PAYLOAD = "9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"


def unique(items):
    result = dict(items)
    if len(result) != len(items):
        raise ValueError("duplicate JSON key")
    return result


def checked(path, zipped=False):
    raw = (ROOT / path).read_bytes()
    if sha256(raw).hexdigest() != PINS[path]:
        raise ValueError(f"changed dependency {path}")
    if zipped:
        raw = decompress(raw)
        assert sha256(raw).hexdigest() == PAYLOAD
    return loads(raw, object_pairs_hook=unique)


def span(frame):
    out = {0}
    for axis in frame:
        assert axis not in out
        out |= {u^axis for u in out}
    return out


def stop(*_):
    raise TimeoutError("20-second reverse census cap")


def walk(word, anchors, old_chart, end_chart, deadline):
    program = word["program"]
    n, owned = word["public"], word["owned_fields"]
    state = word["final"][:] + [None]*owned
    tails = {r:[] for r in anchors}
    open_owners, lifetimes, owner_contacts = {}, {}, []
    last_moves = {}
    for t in range(len(program)-1,-1,-1):
        if t % 128 == 0 and monotonic() >= deadline:
            stop()
        event = program[t]
        op,d,*args = event
        src = args[0] if op in ("ADD","COPY") else None
        touched = (d,src) if src is not None else (d,)
        for r in touched:
            if r not in anchors or r in last_moves:
                continue
            if op == "MOVE":
                assert t == anchors[r] and event == ["MOVE",r,old_chart,end_chart,False]
                last_moves[r] = event
                continue
            assert t > anchors[r] and state[r] == end_chart
            if op == "SCALE":
                assert args[-1] == end_chart and Fraction(args[0])
            else:
                assert op in ("ADD","COPY") and args[-1] == end_chart and Fraction(args[-2])
                other = src if d == r else d
                assert state[other] == end_chart
                if other >= n:
                    assert other in open_owners
                    owner_contacts.append((r,t,other,open_owners[other]))
            tails[r].append([t,"source" if r == src else "destination",event])
        if op == "MOVE":
            before,after,flag = args
            assert state[d] == after and flag == (d>=n)
            state[d] = before
        elif op == "INIT":
            assert d>=n and state[d] == args[0] and d in open_owners
            lifetimes[d,open_owners.pop(d)] = t
            state[d] = None
        elif op == "CLEAR":
            assert d>=n and state[d] is None and d not in open_owners
            open_owners[d] = t
            state[d] = args[0]
        else:
            assert op in ("ADD","COPY","SCALE") and state[d] == args[-1]
            if src is not None:
                assert state[src] == args[-1] and src != d
            if op == "COPY":
                assert d>=n
    assert not open_owners and state == word["initial"] + [None]*owned
    assert set(last_moves) == set(anchors)
    result = {}
    for r,contacts in sorted(tails.items()):
        contacts = contacts[::-1]
        binary = [x for x in contacts if x[2][0] in ("ADD","COPY")]
        result[r] = {
            "terminal_clock": anchors[r], "post_terminal_contacts": contacts,
            "binary_contacts": len(binary), "first_binary_contact": binary[0] if binary else None,
            "status": "fixed_other_field_wrong_chart" if binary else "literal_suffix_survivor",
        }
    owner_details = [[r,t,o,lifetimes[o,clear],clear] for r,t,o,clear in sorted(owner_contacts)]
    assert all(birth<t<clear for _,t,_,birth,clear in owner_details)
    return result,owner_details


def controls():
    toy={"public":2,"owned_fields":0,"initial":[0,1],"final":[1,1],
         "program":[["MOVE",0,0,1,False],["SCALE",0,"-2",1]]}
    cases,_=walk(toy,{0:0},0,1,float("inf"))
    assert cases[0]["status"] == "literal_suffix_survivor"
    for event,direction in ((["ADD",1,0,"1/2",1],"source"),
                             (["ADD",0,1,"-2",1],"destination")):
        cases,_=walk(toy|{"program":toy["program"]+[event]},{0:0},0,1,float("inf"))
        assert cases[0]["first_binary_contact"] == [2,direction,event]
    owned=toy|{"owned_fields":1,"program":toy["program"]+[
        ["INIT",2,1],["ADD",0,2,"1",1],["CLEAR",2,1]]}
    _, detail=walk(owned,{0:0},0,1,float("inf"))
    assert detail == [[0,3,2,2,4]]
    return ["negative SCALE-only survivor", "signed source/destination ADDs block",
            "owned lifetime bound from reverse CLEAR and INIT"]


def main():
    assert __debug__
    signal(SIGALRM,stop)
    alarm(20)
    deadline=monotonic()+18
    tests=controls()
    price=checked("inputs/PRICE.json")
    lead=checked("inputs/LEAD.json")
    prior=checked("inputs/R92-PRICE.json")
    assert price["head"]==lead["head"]==prior["head"]==HEAD
    assert price["caller_head"]==lead["caller_head"]==prior["caller_head"]==CALLER
    assert lead["price_sha256"]==PINS["inputs/PRICE.json"]
    assert price["old_paid"]==prior["old_paid"] and price["old_targets"]==prior["old_targets"]
    assert price["delta_paid_per_edit"]=={"1":-17} and price["delta_productive_per_edit"]=={"8":17,"9":-17}
    assert price["copies"]==17 and price["paid_count"][:2]==[110519,110502]
    assert (price["productive_count"],price["signed_rank_surplus"])==(22461,1424)
    quotes=price["quotes"]
    assert Fraction(quotes["probe"]["one_edit_margin"][0])>0
    assert Fraction(quotes["old_crossing_upper"]["one_edit_one_additional_raw_paid_rank_one"][1])<0
    anchors={int(r):t for r,t in price["anchors"].items()}
    assert len(anchors)==6 and len(set(anchors.values()))==6 and set(anchors)<=set(prior["endpoint_cohort"])
    word=checked("inputs/7334-WORD.json.gz",zipped=True)
    assert (len(word["program"]),word["public"],word["owned_fields"])==(76466,1501,68)
    a,b,c=(span(word["frames"][label]) for label in (3,207,127))
    assert a<b<c and [len(x) for x in (a,b,c)]==[1,256,512]
    fixed=set(word["live"]) | {112+r for r in word["live"]}
    fixed.update(word["hosted"]["X2"],word["hosted"]["Y2"])
    assert not set(anchors)&fixed
    assert all((word["initial"][r],word["final"][r])==(3,127) for r in anchors)
    result,owner_details=walk(word,anchors,207,127,deadline)
    assert result=={int(k):v for k,v in lead["dispositions"].items()}
    assert not lead["unresolved"] and lead["first_unvisited_event"] is None
    first_at_next=sum(row["first_binary_contact"][0]==row["terminal_clock"]+1 for row in result.values())
    assert first_at_next==5 and all(r["first_binary_contact"] for r in result.values())
    alarm(0)
    print(dumps(dict(head=HEAD,caller_head=CALLER,pins=PINS,controls=tests,case_cap=6,event_cap=76466,
        runner_seconds_cap=20,dispositions=result,owner_contacts=owner_details,first_binary_at_move_plus_one=first_at_next,
        first_binary_remaining=[1081,44624],old_productive_rank=9,new_productive_rank=8,removed_paid_rank=1,
        agrees_full_signed_contact_sequences=True,excluded=6,unresolved=[]),indent=2,sort_keys=True))


if __name__=="__main__":
    main()
