"""Independently enumerate the literal one-ADD windows and reverse-scan blockers."""
import argparse
from collections import Counter, defaultdict
from fractions import Fraction
import gzip
from hashlib import sha256
from itertools import pairwise
import json
from pathlib import Path
import signal

HEAD = "ed090b57ed88f8859e5ff4643645099e6ba856ea"
PINS = {
    "WORD.json.gz": "2c523ce6fdd6092d758fedc3602a0bcedb692b9766f1e41f903351ba4dee1756",
    "PRICE.json": "8904cdfebbf5f4c9612ece9c106d2d8f98c81ebb76a54fce6a3608f47da4b85e",
    "SUPPORT.json": "5004e8ec6096597f4ed54d27afd069799410363c891d8e1be36fbc0ba7527bf8",
}


def unique(pairs):
    obj = dict(pairs)
    assert len(obj) == len(pairs)
    return obj


def read(path, key):
    data = path.read_bytes()
    if sha256(data).hexdigest() != PINS[key]:
        raise ValueError("changed dependency " + key)
    if key.endswith(".gz"):
        data = gzip.decompress(data)
    return json.loads(data, object_pairs_hook=unique)


def touch(event):
    return event[1:3] if event[0] in ("ADD","COPY") else event[1:2]


def literal_windows(word):
    tape = word["program"]
    n = word["public"]
    paths = defaultdict(list)
    physical = word["initial"] + [None]*word["owned_fields"]
    spans = []
    for axes in word["frames"]:
        row = {0}
        for axis in axes:
            assert axis not in row
            row |= {axis ^ x for x in row}
        spans.append(row)
    for i,e in enumerate(tape):
        op,r,*args = e
        if op == "MOVE":
            a,b,owned = args
            assert owned == (r>=n) and physical[r] == a
            assert spans[a]<spans[b] or (owned and spans[b]<spans[a])
            physical[r] = b
        elif op == "INIT":
            assert physical[r] is None and r>=n
            physical[r] = args[0]
        elif op == "CLEAR":
            assert physical[r] == args[0] and r>=n
            physical[r] = None
        else:
            assert op in ("ADD","COPY","SCALE")
            assert all(physical[j]==e[-1] for j in touch(e))
        for role in touch(e):
            if role < n:
                paths[role].append(i)
    assert physical == word["final"] + [None]*word["owned_fields"]
    stock = []
    windows = 0
    for role, chain in paths.items():
        moves = [i for i,t in enumerate(chain) if tape[t][0]=="MOVE"]
        for left,right in pairwise(moves):
            windows += 1
            if right-left != 2:
                continue
            t, add, u = chain[left:right+1]
            if tape[add][0] != "ADD":
                continue
            _,_,a,b,_ = tape[t]
            _,_,bb,c,_ = tape[u]
            _,d,s,q,frame = tape[add]
            assert bb == b == frame and spans[a]<spans[b]<spans[c] and Fraction(q)
            assert d != s and role in (d,s)
            other = s if role == d else d
            stock.append((t,u,role,add,other,a,b,c))
    assert windows == 4732
    return sorted(stock, key=lambda row:row[1])


def classify(tape, windows, public):
    following = {}
    next_at = {}
    for t in range(len(tape)-1,-1,-1):
        e = tape[t]
        for role in touch(e):
            next_at[t,role] = following.get(role)
            following[role] = t
    records = []
    for t,u,r,add,other,a,b,c in windows:
        peer = next_at[add,other]
        event = tape[peer] if peer is not None else None
        status = "other_first_contact_not_required_lift"
        if event == ["MOVE",other,b,c,other>=public]:
            later = max(u,peer)
            if any(v is not None and v<=later for v in (next_at[u,r],next_at[peer,other])):
                status = "post_lift_contact_before_join"
            else:
                status = "support_only"
        if event is None:
            detail = "no_later_contact"
        elif event[0]=="MOVE":
            assert event[1]==other and event[2]==b
            detail = "move_wrong_destination" if event[3]!=c else "move_to_required_destination"
        elif event[0] in ("ADD","COPY"):
            detail = event[0].lower()+("_source_read" if event[2]==other else "_destination")
        else:
            detail = event[0].lower()
        records.append(dict(role=r,moves=[t,u],add_clock=add,add=tape[add],other_role=other,
                            charts=[a,b,c],first_other_contact=peer,blocking_event=event,
                            status=status,first_other_contact_class=detail))
    return records


def controls():
    p = [["MOVE",0,0,1,False],["ADD",0,1,"-3/2",1],["MOVE",1,1,2,False],
         ["SCALE",2,"2",1],["MOVE",0,1,2,False],["ADD",1,0,"1",2]]
    row = (0,4,0,1,1,0,1,2)
    assert classify(p,[row],3)[0]["status"] == "support_only"
    reversed_lifts = p[:2]+[p[4],p[3],p[2],p[5]]
    assert classify(reversed_lifts,[(0,2,0,1,1,0,1,2)],3)[0]["status"] == "support_only"
    p[3] = ["ADD",2,1,"2",2]
    assert classify(p,[row],3)[0]["status"] == "post_lift_contact_before_join"
    p[2] = ["MOVE",1,1,3,False]
    r = classify(p,[row],3)[0]
    assert r["status"] == "other_first_contact_not_required_lift"
    assert r["first_other_contact_class"] == "move_wrong_destination"
    return ["both_lift_orders","post_lift_source_read","wrong_lift_destination"]


def run(word, price, support):
    assert price["head"] == support["head"] == HEAD
    assert support["price_sha256"] == PINS["PRICE.json"]
    assert not support["survivors"] and not support["remaining"]
    windows = literal_windows(word)
    records = classify(word["program"],windows,word["public"])
    assert len(records) == len(price["records"]) == len(support["records"]) == 1922
    for r,p,s in zip(records,price["records"],support["records"],strict=True):
        assert (r["role"],r["moves"],r["charts"],[r["add_clock"]]) == (
            p["role"],p["moves"],p["charts"],p["contacts"])
        assert all(r[k]==s[k] for k in r if k!="first_other_contact_class")
    statuses = Counter(r["status"] for r in records)
    assert statuses == support["counts"] == {"other_first_contact_not_required_lift":1922}
    counts = Counter(r["first_other_contact_class"] for r in records)
    by_opcode = Counter(r["blocking_event"][0] if r["blocking_event"] else "NONE" for r in records)
    return dict(head=HEAD, pins=PINS, total_windows=4732, exact_one_add=1922,
                statuses=statuses, first_blockers=counts, by_opcode=by_opcode,
                controls=controls(), all_cases_match_lead=True, unresolved=0, survivors=0)


if __name__ == "__main__":
    assert __debug__
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("word", type=Path)
    p.add_argument("receipt_root", type=Path)
    a=p.parse_args()
    signal.alarm(24)
    print(json.dumps(run(read(a.word,"WORD.json.gz"),read(a.receipt_root/"PRICE.json","PRICE.json"),
                         read(a.receipt_root/"SUPPORT.json","SUPPORT.json")),indent=2,sort_keys=True))
