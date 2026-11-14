"""Replay both complete native grid trajectories and reconstruct the signed invoice."""
import argparse
from collections import Counter
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from signal import SIGALRM, alarm, signal
from sys import version_info
from time import perf_counter
from types import ModuleType

INPUTS = {
    "COMPOSED-WORD.json.gz": "926bbb01254b96e9f8a67d4b7c616f89105686ef1acd14438ac2aad06ba58a1c",
    "COMPOSED-APPLICATION.json": "d9b5d292abb87c87eb3fd3f53501e14d77629ca4adca77a527ff2cf5b58df514",
    "7113-CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
}
ENGINE = {"engines/audit_native.py":"c7d81ad6620de5e46abf97259f62da0138b58a02759c3189e57b8ab176db6bd5"}
BASE = "2acc6bfd2807239fafdb3f9e09ff8ad34703df958496590ab657ef0b9ac93aef"
NEW = "bdecd5cc1cb9f164dc695ce07a07d5d44e9961996fcdfa4d77b4092fecbda745"
CALLER = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
CANDIDATE_GZIP = "6e03624b173b90356e96f845d05fc93153846b863734dc8163ab6c44c602cd32"
CANDIDATE = ["MOVE",902,618,913,False]
START, CAP = 40950, 120


def emit(**fields):
    print(dumps(fields,sort_keys=True),flush=True)


def digest(value):
    return sha256(dumps(value,sort_keys=True,separators=(",",":")).encode()).hexdigest()


def unique(pairs):
    obj=dict(pairs)
    assert len(obj)==len(pairs),"duplicate JSON keys"
    return obj


def without_zeros(delta):
    return {k:v for k,v in sorted(delta.items()) if v}


def delta(old,new):
    out=Counter(new)
    out.subtract(old)
    return without_zeros(out)


def invoice(word, caller, paid):
    public=word["public"]
    h=word["hosted"]
    hosted=set(word["live"]) | {i+112 for i in word["live"]} | set(h["X2"]) | set(h["Y2"])
    assert len(hosted)==400 and 902 in h["Y2"]
    native_target=Counter()
    for i in range(public):
        if i not in hosted:
            a,b=word["initial"][i],word["final"][i]
            native_target[len(word["frames"][b])-len(word["frames"][a])]+=1
    assert sum(native_target.values())==1101 and all(k>0 for k in native_target)
    pure_paid,pure_target=Counter(),Counter()
    calls=0
    for event in caller["events"]:
        if event[0]=="J":
            calls+=1
            continue
        tag,op,*args=event
        count=len(caller["types"][tag]["ports"])
        if op=="QUERY":
            pure_paid[1]+=count
        elif op in ("IDLE_ONE","IDLE_ODD"):
            _,mask,*tail=args
            assert mask and len(set(mask))==len(mask)
            assert tail==([-1] if op=="IDLE_ODD" else []) and (op!="IDLE_ODD" or len(mask)==1)
            pure_paid[8*len(mask)+(op=="IDLE_ODD")]+=count
        else:
            assert op in ("ADD","SCALE","SWAP","LAMBDA")
    assert calls==caller["stages"]==17
    for kind in caller["types"].values():
        for q,zero,*mask in kind["diagonal"]:
            assert q in (-1,0,1) and not zero and len(mask)==17 and set(mask)<={0,1}
            pure_target[abs(q)+8*sum(mask)]+=len(kind["ports"])
    return {"signed_paid":Counter({r:calls*n for r,n in paid.items()})+pure_paid,
            "signed_productive":Counter({r:calls*n for r,n in native_target.items()})+pure_target,
            "native_productive":native_target,"pure_caller_paid":pure_paid,"pure_caller_productive":pure_target}


def main():
    assert __debug__ and version_info[:2]==(3,12)
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_root",type=Path)
    parser.add_argument("candidate",type=Path)
    args=parser.parse_args()
    t=perf_counter()
    stages=[]

    def timeout(_signum,_frame):
        emit(status="INDEPENDENT_CAP",cap_seconds=CAP,completed=stages,seconds=perf_counter()-t)
        raise SystemExit(124)

    signal(SIGALRM,timeout)
    alarm(CAP)
    sources={p:(args.input_root/p).read_bytes() for p in INPUTS}
    assert {p:sha256(raw).hexdigest() for p,raw in sources.items()}==INPUTS
    base=decompress(sources["COMPOSED-WORD.json.gz"])
    packed=args.candidate.read_bytes()
    assert sha256(packed).hexdigest()==CANDIDATE_GZIP
    candidate=decompress(packed)
    assert sha256(base).hexdigest()==BASE and sha256(candidate).hexdigest()==NEW
    base,new=(loads(x,object_pairs_hook=unique) for x in (base,candidate))
    app=loads(sources["COMPOSED-APPLICATION.json"],object_pairs_hook=unique)
    caller=loads(sources["7113-CALLER.json"],object_pairs_hook=unique)
    assert app["status"]=="PASS_COMPOSED_7481_7542_FINAL_APPLICATION"
    assert app["candidate_canonical_sha256"]==BASE and app["caller_sha256"]==INPUTS["7113-CALLER.json"]
    tape=base["program"]
    assert tape[START:START+3]==[["MOVE",902,618,789,False],["MOVE",902,789,913,False],["ADD",985,902,"-1",913]]
    tagged=[(i,CANDIDATE if i==START else e) for i,e in enumerate(tape) if i!=START+1]
    assert new==dict(base,program=[e for _,e in tagged])
    here=Path(__file__).resolve().parent
    path=here/next(iter(ENGINE))
    source=path.read_bytes()
    assert sha256(source).hexdigest()==next(iter(ENGINE.values()))
    source=source.decode()
    patches=(("2**24","2**25"),("25 - (abs(value) & -abs(value)).bit_length()",
                               "26 - (abs(value) & -abs(value)).bit_length()"))
    for old,edited in patches:
        assert source.count(old)==1
        source=source.replace(old,edited)
    mod=ModuleType("role902_grid")
    mod.__file__=str(path)
    exec(compile(source,str(path),"exec"),mod.__dict__)
    stages.append("authenticate and reconstruct exact literal edit")
    a,old_grid=mod.replay(base,list(enumerate(tape)),{38436,40952})
    stages.append("whole comparator integer-grid trajectory")
    b,new_grid=mod.replay(new,tagged,{38436,40952})
    stages.append("whole candidate integer-grid trajectory")
    assert a==b,"exact numerical or ownership ledger mismatch"
    rows,versions,clear,copy,lifetimes,owned_moves=b
    assert len(rows)==1569 and len(versions)==2 and len(clear)==len(lifetimes)==74 and len(copy)==1 and len(owned_moves)==47
    grid_unit=1125*2**25
    h=new["hosted"]
    target=[{i:grid_unit} if i<new["public"] else {} for i in range(len(rows))]
    for j,x in enumerate(new["live"]):
        y=x+112
        if j in h["Dports"]:
            target[y][x]=grid_unit
        else:
            target[x][y]=-grid_unit
            target[y]={x:grid_unit//2,y:grid_unit//2}
    for x,y in zip(h["X2"],h["Y2"],strict=True):
        target[x][y]=-grid_unit
    assert rows==target
    assert delta(old_grid["opcodes"],new_grid["opcodes"])=={"MOVE":-1}
    assert delta(old_grid["paid"],new_grid["paid"])=={2:-2,4:1}
    assert all(v==new_grid[k] for k,v in old_grid.items() if k not in ("opcodes","paid"))
    assert new_grid["owned_rise_mass"]==56 and new_grid["owned_peak"]==50
    assert new_grid["odd_grid_lcm"]==1125 and new_grid["dyadic_height"]==25
    assert new_grid["maximum_scaled_mass"]=="841374570120675/8192"
    stages.append("all 1569 endpoint rows and exact numeric and ownership ledger equality")
    before,after=(invoice(w,caller,g["paid"]) for w,g in ((base,old_grid),(new,new_grid)))
    assert sum(before["signed_paid"].values())==app["paid_calls"]==110485
    assert sum(before["signed_productive"].values())==app["productive_calls"]==22461
    assert sum(after["signed_paid"].values())==110468 and before["signed_productive"]==after["signed_productive"]
    paid=delta(before["signed_paid"],after["signed_paid"])
    assert paid=={2:-34,4:17}
    def mass_surplus(book):
        target, paid = book["signed_productive"], book["signed_paid"]
        return sum(r*(target[r]-paid[r]) for r in target.keys()|paid.keys())

    surplus=mass_surplus(after)
    assert surplus==mass_surplus(before)==1424
    stages.append("independent signed paid and productive profile reconstruction")
    alarm(0)
    emit(status="PASS_ROLE902_INDEPENDENT_WHOLE_GRID_INVOICE",cases_completed=1,unresolved=[],completed=stages,
         caller_head=CALLER,old_canonical_sha256=BASE,candidate_canonical_sha256=NEW,candidate_compressed_sha256=CANDIDATE_GZIP,
         input_pins=INPUTS,engine_pins=ENGINE,adapted_engine_sha256=sha256(source.encode()).hexdigest(),
         forward_rows=len(rows),endpoint_sha256=digest(rows),source_versions_sha256=digest(versions),
         exact_owned_clear_rows=len(clear),owned_clear_sha256=digest(clear),copy_guards=len(copy),copy_sha256=digest(copy),
         owned_lifetimes=len(lifetimes),owned_lifetimes_sha256=digest(lifetimes),owned_move_records=len(owned_moves),owned_moves_sha256=digest(owned_moves),
         before_grid=old_grid,after_grid=new_grid,signed_profile=after,signed_paid_delta=paid,signed_productive_delta={},
         signed_rank_mass_surplus=surplus,cap_seconds=CAP,seconds=perf_counter()-t)


if __name__=="__main__":
    main()
