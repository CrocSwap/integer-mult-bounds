"""Direct exact rational row and column test of Type B singleton squares."""
from argparse import ArgumentParser
from collections import Counter, defaultdict
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
from time import monotonic

HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CALLER_HEAD = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
CAP, SECONDS = 9, 20
PINS = {
    "price": "57687d0cdb758cacaff681497c6d4834ec071749156c05b1d74d326cda9c958d",
    "caller": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "admission": "c95300e9bca27e44a25c82d794f88cbf70757c142806b0e4c590ea29feb81a13",
}


def unique(pairs):
    result = dict(pairs)
    if len(result) != len(pairs):
        raise ValueError("duplicate JSON key")
    return result


def read(path, name):
    raw = path.read_bytes()
    if sha256(raw).hexdigest() != PINS[name]:
        raise ValueError("changed dependency: " + name)
    return json.loads(raw, object_pairs_hook=unique)


def event_action(event, offset, size):
    """Decompose one q=+1, unit-body Type B event into invertible gates."""
    family, name, *args = event
    if family == "A":
        return ()
    if family == "J":
        left, right, first, second = args[1]
        return (("add", left-offset, right-offset, Q(first)),
                ("add", right-offset, left-offset, Q(second)))
    assert family == "B"
    role, *rest = args
    d = role-offset
    assert 0 <= d < size
    if name == "ADD":
        source, scale = rest
        return (("add", d, source-offset, Q(scale)),)
    if name == "QUERY":
        source, power = rest
        assert power in (-1,1)
        return (("add", d, source-offset, Q(1)),)
    if name == "SWAP":
        source, = rest
        return (("swap", d, source-offset, Q(1)),)
    if name == "SCALE":
        scale, = rest
        return (("scale", d, d, Q(scale)),)
    assert name in ("IDLE_ODD", "IDLE_ONE", "LAMBDA")
    return ()


def valid_gate(gate, n):
    kind, d, s, scale = gate
    assert 0 <= d < n and 0 <= s < n
    if kind == "scale":
        assert d == s and scale
    else:
        assert d != s and kind in ("add", "swap")
    return gate


def add_to(vector, coordinate, value):
    new = vector.get(coordinate,Q(0)) + value
    if new:
        vector[coordinate] = new
    else:
        vector.pop(coordinate,None)


def action(vector, gates, adjoint=False):
    order = reversed(gates) if adjoint else gates
    for kind, dest, source, factor in order:
        if kind == "add":
            if adjoint:
                dest, source = source, dest
            if source in vector:
                add_to(vector,dest,factor*vector[source])
        elif kind == "scale":
            if dest in vector:
                vector[dest] *= factor
        else:
            before = vector.pop(dest,None)
            after = vector.pop(source,None)
            if before is not None:
                vector[source] = before
            if after is not None:
                vector[dest] = after
    return vector


def off_axis(gates, role):
    column = action({role:Q(1)},gates)
    row = action({role:Q(1)},gates,adjoint=True)
    diagonal = column.pop(role,Q(0))
    assert row.pop(role,Q(0)) == diagonal
    if not column and not row:
        assert diagonal
    return diagonal, column, row


def controls():
    keep = (("scale",0,0,Q(-3,2)),("add",1,2,Q(4)))
    assert off_axis(keep,0) == (Q(-3,2),{},{})
    column = (("add",2,0,Q(-2)),)
    assert off_axis(column,0) == (Q(1),{2:Q(-2)},{})
    row = (("add",0,2,Q(3,7)),)
    assert off_axis(row,0) == (Q(1),{},{2:Q(3,7)})
    swap = (("swap",0,2,Q(1)),)
    assert off_axis(swap,0) == (Q(0),{2:Q(1)},{2:Q(1)})
    assert off_axis(swap+swap,0) == (Q(1),{},{})
    return ["commuting diagonal and spectator shear", "outgoing exact column shear",
            "incoming fractional row shear", "crossed swap and its cancellation"]


def keys_from(events, offset):
    singleton = defaultdict(list)
    count = 0
    for clock, event in enumerate(events):
        if event[:2] != ["B", "IDLE_ONE"]:
            continue
        _, _, raw_role, mask = event
        count += 1
        if len(mask) == 1:
            singleton[raw_role-offset,mask[0]].append(clock)
    assert count == 60
    keys = [dict(earlier=a,later=b,role=role,stage=stage)
            for (role,stage), clocks in singleton.items() for a,b in combinations(clocks,2)]
    return sorted(keys,key=lambda key:(key["later"]-key["earlier"],key["earlier"]))


def normalized(vector):
    return [[role,str(value)] for role,value in sorted(vector.items())]


def run(price_path, caller_path, admission_path):
    started = monotonic()
    diagnostics = controls()
    price, admission = read(price_path,"price"), read(admission_path,"admission")
    assert price["head"] == admission["head"] == HEAD and admission["exit"] == 0
    assert price["caller_head"] == admission["caller"] == CALLER_HEAD
    assert price["source_sha256"]["inputs/7113-CALLER.json"] == admission["caller_sha256"] == PINS["caller"]
    assert price["limits"]["projector_keys"] == CAP and price["limits"]["projector_seconds"] == SECONDS
    caller = read(caller_path,"caller")
    events = caller["events"]
    port = caller["types"]["B"]
    n, off = port["roles"], port["offset"]
    assert (caller["stages"],n,off,len(port["ports"]),len(events)) == (17,36,36,8,4783)
    keys = keys_from(events,off)
    assert keys == price["cases"] and len(keys) == CAP and all(k["role"] == 0 for k in keys)
    by_clock = [tuple(valid_gate(gate,n) for gate in event_action(event,off,n)) for event in events]
    whole = tuple(gate for interval in by_clock for gate in interval)
    for role in range(n):
        assert action({role:Q(1)},whole) == {role:Q(1)}

    outcomes = []
    for key in keys:
        if monotonic() - started >= SECONDS-2:
            break
        a,b,r = (key[k] for k in ("earlier","later","role"))
        gates = tuple(gate for interval in by_clock[a+1:b] for gate in interval)
        diagonal,column,row = off_axis(gates,r)
        outcomes.append(dict(key=key, literal_interior_events=b-a-1, specialized_gate_count=len(gates),
            diagonal=str(diagonal), column_off_axis=normalized(column), row_off_axis=normalized(row),
            status="excluded" if column or row else "provisional unit-body commute"))
    unvisited = keys[len(outcomes):]
    return dict(head=HEAD,caller_head=CALLER_HEAD,pins=PINS,phase="q=+1, all body variables one",
                unit_body_only=True, old_arbitrary_input_endpoint_columns=n, controls=diagnostics,
                case_cap=CAP,runner_cap_seconds=SECONDS,status="CAPPED" if unvisited else "EXHAUSTED",
                results=outcomes,counts=Counter(x["status"] for x in outcomes),unvisited=unvisited,
                survivors=[x["key"] for x in outcomes if x["status"] != "excluded"])


def main():
    p = ArgumentParser(description=__doc__)
    for name in PINS:
        p.add_argument("--"+name,type=Path)
    p.add_argument("--controls-only",action="store_true")
    args = p.parse_args()
    assert __debug__
    if args.controls_only:
        result = controls()
    else:
        if not all(getattr(args,name) for name in PINS):
            p.error("pass explicit price, caller and admission paths")
        result = run(args.price,args.caller,args.admission)
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__ == "__main__":
    main()
