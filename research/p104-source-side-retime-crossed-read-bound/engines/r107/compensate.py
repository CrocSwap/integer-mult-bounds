"""Check the fixed R107 missing cross-term and its 43 late cut alternatives."""
from argparse import ArgumentParser
from collections import Counter, defaultdict
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal
from time import monotonic

ROOT = Path(__file__).resolve().parent
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CALLER = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
PINS = {
    "inputs/PRICE.json": "526dcf4131c5cfd184047413ccd4a19d9602c42e4e1df034061c5bce453ec476",
    "inputs/7334-WORD.json.gz": "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
    "reused/reverse_span.py": "f8b48f2ed99d003e20f5b3fb2270603c4edbc3ce9a01484102816aa2710ce9ff",
}
PAYLOAD = "9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
N = 1501
EVENTS = 76466
SECONDS = 20
SRC, MID, READER = 532, 205, 198
FIRST, OLD, CROSS, LAST = 44611, 44612, 44613, 46018
LATE = range(45976,46019)
A, B, C = 746, 207, 127


def unique(pairs):
    obj = dict(pairs)
    if len(obj) != len(pairs):
        raise ValueError("Duplicate JSON key")
    return obj


def pinned(root,name):
    raw = (root/name).read_bytes()
    if sha256(raw).hexdigest() != PINS[name]:
        raise ValueError("Changed input " + name)
    return raw


def roles(event):
    return event[1:3] if event[0] in ("ADD","COPY") else event[1:2]


def scaled(engine,row,factor):
    return engine["sum_scaled"](({},1),row,(factor.numerator,factor.denominator))


def fixture(engine):
    source = ({1:1},1)
    previous = ({0:1},1)
    changed = engine["sum_scaled"](previous,source,(-1,2))
    recovered = engine["sum_scaled"](changed,source,(1,2))
    target = scaled(engine,source,Q(1,4))
    assert recovered == previous and changed != previous
    assert engine["exact_span"]([(205,recovered)],target)["status"] == "absent_exterior_coordinate"
    assert engine["exact_span"]([(205,recovered),(198,source)],target)["coefficients"] == {198:"1/4"}
    return engine["controls"]()+["counterfactual undo signed ADD","diagonal donor positive fixture"]


def backward(word,price,deadline,progress):
    tape = word["program"]
    assert (word["public"],word["owned_fields"],len(tape)) == (N,68,EVENTS)
    assert price["key"] == [FIRST,LAST,SRC] and price["charts"] == [A,B,C]
    assert price["old_add"] == [OLD,tape[OLD]] == [OLD,["ADD",MID,SRC,"-1/2",B]]
    assert price["crossed"] == [CROSS,tape[CROSS]] == [CROSS,["ADD",READER,MID,"-1/2",B]]
    assert tape[FIRST] == ["MOVE",SRC,A,B,False] and tape[LAST] == ["MOVE",SRC,B,C,False]
    assert [t for t in range(FIRST+1,LAST) if SRC in roles(tape[t])] == [OLD]
    mid_incidents = [[t,tape[t]] for t in range(OLD+1,LAST) if MID in roles(tape[t])]
    assert mid_incidents == [price["crossed"],[45975,["MOVE",MID,B,C,False]],
                             [45976,["ADD",MID,256,"1",C]],[45999,["ADD",MID,315,"1",C]]]
    assert Q(tape[OLD][3])*Q(tape[CROSS][3]) == Q(price["correction"]) == Q(1,4)

    state = word["final"]+[None]*word["owned_fields"]
    copy_needs_init = set()
    bank = None
    late = {}
    reader_events = []
    for t in range(EVENTS-1,-1,-1):
        progress["first_unvisited_event"] = t
        if t%128 == 0 and monotonic()>=deadline:
            raise TimeoutError("reverse chart cap")
        event = tape[t]
        op,d,*args = event
        assert 0 <= d < len(state) and (d not in copy_needs_init or op == "INIT")
        if op == "MOVE":
            a,b,flag = args
            assert state[d] == b and flag == (d>=N)
            state[d] = a
        elif op == "INIT":
            assert d>=N and state[d] == args[0]
            state[d] = None
            copy_needs_init.discard(d)
        elif op == "CLEAR":
            assert d>=N and state[d] is None
            state[d] = args[0]
        else:
            assert op in ("ADD","COPY","SCALE") and state[d] == args[-1]
            assert Q(args[-2])
            if op != "SCALE":
                assert args[0] != d and state[args[0]] == args[-1]
            if op == "COPY":
                assert d>=N
                copy_needs_init.add(d)
        if t == CROSS:
            assert state[SRC] == state[MID] == state[READER] == B
            bank = [r for r,f in enumerate(state) if f == B and r != SRC]
        if t in LATE:
            assert state[MID] == C and state[SRC] == B
            late[t] = state[READER]
        if CROSS<t<=LATE.stop-1 and READER in roles(event):
            reader_events.append([t,event])
        progress["events_checked"] += 1
    assert state == word["initial"]+[None]*word["owned_fields"] and not copy_needs_init
    progress["first_unvisited_event"] = None
    assert bank is not None and len(late)==len(LATE)==43
    return bank, late, list(reversed(reader_events)), mid_incidents


def examine(word,price,live,engine,deadline):
    public = [r for r in live if r<N]
    assert SRC not in public and MID in public and READER in public
    req = defaultdict(list)
    req[OLD].append((SRC,0))
    for i,r in enumerate(public,1):
        req[CROSS].append((r,i))
    traced = engine["transpose_prefix"](word,req,len(public)+1,deadline)
    source = traced[0]
    correction = scaled(engine,source,Q(price["correction"]))
    original = dict(zip(public,traced[1:],strict=True))
    undo = -Q(price["old_add"][1][3])
    adjusted = dict(original)
    adjusted[MID] = engine["sum_scaled"](original[MID],source,(undo.numerator,undo.denominator))
    assert engine["sum_scaled"](adjusted[MID],source,(-undo.numerator,undo.denominator)) == original[MID]
    bank = list(adjusted.items())
    proof = engine["exact_span"](bank,correction)
    if proof["status"] == "absent_exterior_coordinate":
        proof["separating_covector"] = {proof["coordinate"]:"1"}
        proof["separated_target"] = proof["target_coefficient"]
    if proof["status"] != "exact_span":
        probe = {j:Q(v) for j,v in proof["separating_covector"].items()}
        assert all(engine["dot"](row,probe)==0 for _,row in bank)
        assert engine["dot"](correction,probe)==Q(proof["separated_target"])!=0
        proof["probe_original_source"] = str(engine["dot"](source,probe))
    return dict(cut=CROSS,chart=B,public=public,owned_excluded=[r for r in live if r>=N],
        original_source_row=source,target_row=correction,old_205_row=original[MID],
        adjusted_public_rows=adjusted,proof=proof)


def main():
    assert __debug__
    p = ArgumentParser(description=__doc__)
    p.add_argument("--root",type=Path,default=ROOT)
    p.add_argument("--controls-only",action="store_true")
    args = p.parse_args()
    source = "reused/reverse_span.py"
    pinned(ROOT,source)
    engine = run_path(str(ROOT/source))
    checks = fixture(engine)
    if args.controls_only:
        print(dumps(checks))
        return
    progress = dict(events_checked=0,first_unvisited_event=EVENTS-1,late_checked=0,bank_checked=False)
    result, typed, incidents, mid_incidents, failure = None, [], [], [], None

    def stop(*_):
        raise TimeoutError("Hard 20-second cap")

    signal(SIGALRM,stop)
    alarm(SECONDS)
    deadline = monotonic()+SECONDS-2
    try:
        price = loads(pinned(args.root,"inputs/PRICE.json"),object_pairs_hook=unique)
        assert price["head"] == HEAD and price["caller"] == CALLER
        assert price["word_sha256"] == PINS["inputs/7334-WORD.json.gz"] and price["payload_sha256"] == PAYLOAD
        assert price["limits"]["donor_banks"] == 1 and price["limits"]["typed_late_cuts"] == len(LATE)
        assert price["limits"]["seconds"] == SECONDS and price["cuts"] == [LATE.start,LATE.stop-1]
        raw = decompress(pinned(args.root,"inputs/7334-WORD.json.gz"))
        assert sha256(raw).hexdigest() == PAYLOAD
        word = loads(raw,object_pairs_hook=unique)
        live, charts, incidents, mid_incidents = backward(word,price,deadline,progress)
        for cut in LATE:
            first_read = next(([t,event] for t,event in incidents if t<cut and
                             event[0] in ("ADD","COPY") and event[2]==READER),None)
            status = ("different chart" if charts[cut]!=C else "reader was read" if first_read else "eligible")
            typed.append(dict(cut=cut,reader_chart=charts[cut],required_chart=C,
                              first_crossed_read=first_read,status=status))
            progress["late_checked"] += 1
        result = examine(word,price,live,engine,deadline)
        progress["bank_checked"] = True
    except TimeoutError as exc:
        failure = str(exc)
    finally:
        alarm(0)
    print(dumps(dict(head=HEAD,caller=CALLER,pins=PINS,cap_seconds=SECONDS,checks=checks,
        bank=result,typed_late_cuts=typed,reader_incidents=incidents,mid_recipient_incidents=mid_incidents,
        progress=progress,timeout=failure,
        late_counts=dict(Counter(row["status"] for row in typed))),indent=2,sort_keys=True))
    if failure:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
