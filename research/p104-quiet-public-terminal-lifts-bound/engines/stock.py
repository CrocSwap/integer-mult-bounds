"""Check the non-H9 terminal stock from authenticated source metadata only."""
import ast
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PINS = {
    "inputs/7334-CHANGED.json":"f4d3f6ca2d87f8cd68c01ac9f77b69bd5a796f92bd567cea8afe3ac7c72e8e4b",
    "inputs/7334-construct.py":"ecb39578063d7f09153a85370a3b9bb7cbf8b36ff9891033a1cce7a2fe7f7fda",
    "inputs/R92-PRICE.json":"05d7a5ebdd2eeedd6c8f534e8e2eeac22484daf9f387f4a6b88cc9eed22a6b8f",
    "inputs/R62-REVERSE.json":"0c1f8d6e8fab92c967a6e01e71cccfafb9607475a617bd17df989cb750d08aa9",
    "inputs/R144-H9.json":"bf315824cb853346b0771b52fd590f1f77ed146c148c0f3903750171b295730d",
    "inputs/R62-COMPARE.json":"c17fcdc3c833f15e989333f85b04e8900dfca455251776b60d1ed59250eaaea4",
}


def unique(items):
    obj=dict(items)
    if len(obj)!=len(items):
        raise ValueError("duplicate JSON key")
    return obj


def read(name):
    data=(ROOT/name).read_bytes()
    if sha256(data).hexdigest()!=PINS[name]:
        raise ValueError("changed dependency "+name)
    return json.loads(data,object_pairs_hook=unique) if name.endswith(".json") else data


def main():
    assert __debug__
    changed,source,price,old,h9_checked,compare=map(read,PINS)
    assert price["head"]=="aaeec8c0acf01e99a5f331ef363a698d9c084ace"
    assert old["caller_head"]==price["caller_head"]=="07a76c5e2738882c0cb322278e56f6cae3c9885d"
    assert old["head"]==compare["head"]=="9d0119eb12fbd9fa534b48cd37b68e7099757b91"
    assert old["complete"] and old["visited_helpers"]==compare["matched_helpers"]==1101
    assert old["visited_events"]==76461 and not old["remaining_roles"] and not compare["unresolved"]
    assert not compare["proper_last_moves_any_positive_rank"]
    constants={a.targets[0].id:ast.literal_eval(a.value) for a in ast.parse(source).body
               if isinstance(a,ast.Assign) and isinstance(a.targets[0],ast.Name)
               and a.targets[0].id in ("BLOCK","CLOCK")}
    assert list(constants["BLOCK"])==changed["body_clocks"]
    last_change=max(*constants["BLOCK"],constants["CLOCK"])
    affected=set(changed["roles"])
    assert len(affected)==14
    cases=[r for r in old["rows"] if r["old_productive_rank"]<9]
    assert len(cases)==485 and all(1<=r["old_productive_rank"]<=8 for r in cases)
    assert len({r["role"] for r in cases})==485
    unchanged,whole_lift,replayed=[],[],[]
    for r in cases:
        h,t,e=r["role"],r["last_clock"],r["last_event"]
        assert t is not None and e is not None
        if h in affected:
            assert t>last_change and e[0]=="ADD" and h in e[1:3] and e[-1]==r["final"]
            replayed.append([h,t,e])
        elif e[0]=="MOVE":
            assert e==["MOVE",h,r["initial"],r["final"],False]
            whole_lift.append([h,t,e])
        else:
            assert e[0] in ("ADD","COPY","SCALE") and e[-1]==r["final"]
            unchanged.append(h)
    assert len(unchanged)==472 and len(whole_lift)==8
    assert [r[0] for r in replayed]==[652,654,1303,1305,1467]
    h9={r["role"]:r for r in old["rows"] if r["old_productive_rank"]==9}
    assert len(h9)==616 and all((r["initial"],r["final"])==(3,127) for r in h9.values())
    assert h9_checked["head"]==price["head"] and not h9_checked["quiet_tails"] and not h9_checked["unresolved"]
    assert set(h9_checked["scope"])==set(price["endpoint_cohort"])==set(h9)-{319}
    assert len(h9_checked["scope"])==615
    protected=h9[319]
    assert 319 in affected and protected["last_clock"]==61388>last_change
    assert protected["last_event"]==["ADD",319,347,"-1",127]
    result=dict(all_productive_helpers=1101,H9_checked=615,protected_H9=[319,61388,protected["last_event"]],
        head=price["head"],caller=price["caller_head"],pins=PINS,
        non_H9_helpers=len(cases),unchanged_final_scalar=unchanged,unchanged_full_exit=whole_lift,
        changed_retained_final_scalar=replayed,constructor_last_changed_scalar=last_change,
        ideal_compatible_upper="0",eligible=[],unresolved=[])
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
