"""Independently apply unique #7542 edit anchors to #7481 and replay normalized endpoints."""
import argparse
from collections import Counter
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal
from time import perf_counter
from types import ModuleType

HERE = Path(__file__).resolve().parent
BASE_PINS = {
    "data/base-7334-word.json.gz": "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
    "data/edits.json": "04404c0456d3d211beaae5464dedd50d3ae0bbb92bdccbc9b1777055409d1546",
    "data/word.json.gz": "6f320348a954223177c3a63b1292fdba1fc2905d4668888732c9302393bd628d",
}
INCUMBENT_PINS = {
    "inputs/7481-WORD.json.gz": "acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9",
    "inputs/7113-CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
}
ENGINE_PINS = {
    "retained_independent.py": "21f46a8340331abb1486b50bd4e04453f1968b0a5950d86ff7780dd368590874",
    "audit_native.py": "c7d81ad6620de5e46abf97259f62da0138b58a02759c3189e57b8ab176db6bd5",
}
CAP = 120


def emit(**result):
    print(dumps(result, sort_keys=True), flush=True)


def unique(pairs):
    result = dict(pairs)
    assert len(result) == len(pairs), "duplicate JSON keys"
    return result


def authenticate(root, pins):
    data = {p: (root/p).read_bytes() for p in pins}
    assert {p:sha256(x).hexdigest() for p,x in data.items()} == pins
    return data


def canonical(word):
    return dumps(word,sort_keys=True,separators=(",",":")).encode()


def header(word):
    return {k:v for k,v in word.items() if k != "program"}


def splice(base, incumbent, edits):
    old_program, source = base["program"], incumbent["program"]
    assert len(old_program) == edits["base_events"]
    remove = {i:ev for i,ev in edits["delete"]}
    before = {i:events for i,events in edits["insert_before"]}
    assert len(remove)==len(edits["delete"])==11 and len(before)==len(edits["insert_before"])==9
    assert all(old_program[i]==event for i,event in remove.items())
    anchors = sorted(remove.keys() | before.keys())
    mapped = {}
    for i in anchors:
        event = old_program[i]
        assert old_program.count(event)==source.count(event)==1
        mapped[i] = source.index(event)
    assert list(mapped.values()) == sorted(mapped.values())
    working = [(i,event) for i,event in enumerate(source)]
    retire = {mapped[i] for i in remove}
    insert = {mapped[i]:events for i,events in before.items()}
    result = []
    for clock,event in working:
        result.extend(((clock, index), e) for index,e in enumerate(insert.get(clock,())))
        if clock not in retire:
            result.append((clock,event))
    result.extend(((len(source), i),e) for i,e in enumerate(edits["append"]))
    assert [clock for clock,_ in result if type(clock) is int] == [i for i in range(len(source)) if i not in retire]
    return result, mapped


def diff(before,after):
    change=Counter(after)
    change.subtract(before)
    return {k:v for k,v in sorted(change.items()) if v}


def grid_forward(engine_raw, incumbent, composed, tagged):
    raw = engine_raw.decode()
    for old,new in (("2**24","2**25"),
                    ("25 - (abs(value) & -abs(value)).bit_length()", "26 - (abs(value) & -abs(value)).bit_length()")):
        assert raw.count(old)==1
        raw=raw.replace(old,new)
    namespace=ModuleType("composed_grid")
    namespace.__file__=str(HERE/"audit_native.py")
    exec(compile(raw,namespace.__file__,"exec"),namespace.__dict__)
    old_state,old = namespace.replay(incumbent,list(enumerate(incumbent["program"])),set())
    new_state,new = namespace.replay(composed,tagged,set())
    assert all(before == after for i,(before,after) in enumerate(zip(old_state,new_state,strict=True)) if i != 2)
    old_clear,new_clear=old_state[2],new_state[2]
    assert old_clear.keys()==new_clear.keys()
    changed=[i for i in old_clear if old_clear[i] != new_clear[i]]
    assert changed == [42558] and incumbent["program"][42558] == ["CLEAR",1557,595]
    earlier,later = dict(old_clear[42558]),dict(new_clear[42558])
    delta = {r:later.get(r,0)-earlier.get(r,0) for r in earlier.keys()|later.keys()
             if later.get(r,0)!=earlier.get(r,0)}
    assert delta == {902:-56623104000,985:-56623104000}
    assert len(old_state[0])==1569 and len(old_clear)==74 and len(old_state[3])==1
    for k in ("owned_peak","owned_lifetimes","owned_rise_mass","odd_grid_lcm","dyadic_height",
              "maximum_scaled_mass","odd_divisions"):
        assert old[k]==new[k]
    return {"all_rows":len(old_state[0]),"owned_clear_rows":len(old_state[2]),"copy_guards":len(old_state[3]),
            "owned_move_ledger":len(old_state[5]),"native_grid":new,
            "changed_dirty_clear":{"old_clock":42558,"role":1557,"chart":595,
                                   "delta_scaled":delta,"scale":"1125*2^25"},
            "adapted_audit_sha256":sha256(raw.encode()).hexdigest()}


def main():
    assert __debug__
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("benchmark_root", type=Path)
    parser.add_argument("peer_package", type=Path)
    parser.add_argument("--write-word", type=Path)
    args=parser.parse_args()
    started=perf_counter()
    stages=[]

    def cap(_sig,_frame):
        emit(status="INDEPENDENT_CAP",completed=stages,seconds=perf_counter()-started,cap_seconds=CAP)
        raise SystemExit(124)

    signal(SIGALRM,cap)
    alarm(CAP)
    left=authenticate(args.benchmark_root,INCUMBENT_PINS)
    right=authenticate(args.peer_package,BASE_PINS)
    engines=authenticate(HERE,ENGINE_PINS)
    base=loads(decompress(right["data/base-7334-word.json.gz"]),object_pairs_hook=unique)
    incumbent=loads(decompress(left["inputs/7481-WORD.json.gz"]),object_pairs_hook=unique)
    peer=loads(decompress(right["data/word.json.gz"]),object_pairs_hook=unique)
    caller=loads(left["inputs/7113-CALLER.json"],object_pairs_hook=unique)
    edits=loads(right["data/edits.json"],object_pairs_hook=unique)
    assert len(base["program"])==76466 and len(incumbent["program"])==76475
    assert header(base)==header(incumbent)==header(peer)
    assert caller["stages"]==sum(e[0]=="J" for e in caller["events"])==17
    peer_tagged,_=splice(base,base,edits)
    assert [e for _,e in peer_tagged]==peer["program"]
    tagged,mapping=splice(base,incumbent,edits)
    composed=dict(incumbent,program=[e for _,e in tagged])
    assert len(composed["program"])==len(incumbent["program"])+sum(len(v) for _,v in edits["insert_before"])+len(edits["append"])-len(edits["delete"])
    assert all(e[0] in ("MOVE","ADD") and e[1]<base["public"] for _,e in edits["delete"])
    assert all(e[0] in ("MOVE","ADD") and e[1]<base["public"] for _,es in edits["insert_before"] for e in es)
    stages.append("all unique splice anchors and both unchanged headers")
    native=run_path(str(HERE/"retained_independent.py"))["native"]
    baseline_n,peer_n,incumbent_n,composed_n=map(native,(base,peer,incumbent,composed))
    assert all(not n["bad_inputs"] for n in (baseline_n,peer_n,incumbent_n,composed_n))
    for field in ("public","helpers"):
        assert baseline_n[field]==peer_n[field]==incumbent_n[field]==composed_n[field]
    for field in ("owned_peak","lifetimes","rises"):
        assert baseline_n[field]==peer_n[field]
        assert incumbent_n[field]==composed_n[field]
    peer_delta=diff(baseline_n["paid"],peer_n["paid"])
    assert diff(incumbent_n["paid"],composed_n["paid"])==peer_delta
    stages.append("four complete normalized native adjoints and exact paid profile")
    grid=grid_forward(engines["audit_native.py"],incumbent,composed,tagged)
    stages.append("all 1569 normalized forward endpoints, COPY/owner MOVE/lifetimes, one exact dirty CLEAR difference")
    encoded=canonical(composed)
    if args.write_word:
        args.write_word.write_bytes(encoded)
    emit(status="PASS_INDEPENDENT_COMPOSED_NATIVE_ADJOINT_AND_FORWARD",completed=stages,
         composed_canonical_sha256=sha256(encoded).hexdigest(), composed_events=len(composed["program"]),
         anchor_mapping=mapping,native_paid_delta=peer_delta,signed_paid_delta={k:17*v for k,v in peer_delta.items()},
         before_paid=incumbent_n["paid"],after_paid=composed_n["paid"],productive=incumbent_n["helpers"],
         old_and_new_owned_peak=composed_n["owned_peak"],signed_caller=INCUMBENT_PINS["inputs/7113-CALLER.json"],
         forward=grid,pins={"peer":BASE_PINS,"benchmark":INCUMBENT_PINS,"engines":ENGINE_PINS},
         seconds=perf_counter()-started,cap_seconds=CAP)
    alarm(0)


if __name__=="__main__":
    main()
