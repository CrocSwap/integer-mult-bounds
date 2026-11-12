"""Verify the distinct transported axes and all disjoint odd-idle schedules."""
from argparse import ArgumentParser
from gzip import decompress
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal

HERE = Path(__file__).resolve().parent
PINS = {
    "inputs/7113-CALLER.json.gz": "7e8038559cd158f6e32ef6d1a3bf15ab6a8ecc2239af32ab1699511ac28e26d9",
    "inputs/PRICE.json": "cca4b82a9b7b1670705373a245282043e32527f453cd24ba4500794857686872",
    "inputs/7295-CERTIFICATE.json": "0587aeb7029b6e066f73701748075f7786056894bf8803690f66cf223bfa6d8c",
    "inputs/7295-PROVENANCE.json": "fe28d47df369365523aaafd4d26e506fe2cdc2905c5962626a618eb612294fb0",
    "inputs/7295-trace_and_price.py": "feebbca6d093d92f4e165b4aa940fb0628e5deaa4635488c9916aafe08aebc76",
}
CAP = 16
SECONDS = 20


def unique(items):
    out = dict(items)
    if len(out) != len(items):
        raise ValueError("duplicate JSON key")
    return out


def read(root, name):
    raw = (root / name).read_bytes()
    if sha256(raw).hexdigest() != PINS[name]:
        raise ValueError(f"changed dependency {name}")
    return raw


def parsed(root, name):
    return json.loads(read(root,name),object_pairs_hook=unique)


def signed_difference(removed, added):
    return {a: -1 for a in removed-added} | {a: 1 for a in added-removed}


def audit(root):
    price = parsed(root,"inputs/PRICE.json")
    cert = parsed(root,"inputs/7295-CERTIFICATE.json")
    prov = parsed(root,"inputs/7295-PROVENANCE.json")
    trace_file = "inputs/7295-trace_and_price.py"
    read(root,trace_file)
    raw = decompress(read(root,"inputs/7113-CALLER.json.gz"))
    assert price["caller"] == prov["inputs/CALLER.json.gz"]["commit"]
    assert price["caller_sha256"] == prov["inputs/CALLER.json.gz"]["sha256"] == sha256(raw).hexdigest()
    caller = json.loads(raw,object_pairs_hook=unique)
    events = caller["events"]
    ty = caller["types"]["B"]
    assert len(ty["ports"]) == price["ports"] == 8 and caller["stages"] == price["copies"] == 17
    assert ty["roles"] == 36
    contacts = run_path(str(root/trace_file))["backward"](caller)
    broad = [c for c in contacts if c["op"] == "IDLE_ODD"]
    assert len(contacts) == 94 and len(broad) == 4
    assert {c["call"] for c in cert["charges"]} == {c["clock"] for c in broad}
    assert all((c["kind"],c["rank"],c["ports"],c["window"]) == ("B",9,8,[0,len(events)]) for c in broad)
    assert len({c["role"] for c in broad}) == 4
    clock_to_role = {c["clock"]: c["role"]-ty["offset"] for c in broad}
    clock_to_stage = {c["clock"]: c["selected_stages"][0] for c in broad}
    assert all(len(c["selected_stages"]) == 1 and c["role"] == c["slot"] for c in broad)
    assert {str(c["clock"]):[clock_to_role[c["clock"]],c["selected_stages"]] for c in broad} == price["odd_jobs"]

    choices = {stage:[t for t,s in sorted(clock_to_stage.items()) if s==stage] for stage in (8,9)}
    pairs = list(product(choices[8],choices[9]))
    assert list(map(list,pairs)) == price["pairs"]
    schedules = []
    for size in (1,2):
        for edges in combinations(pairs,size):
            if len(set().union(*map(set,edges))) != 2*size:
                continue
            for retained in product(*edges):
                removed, added = {8:set(),9:set()}, {8:set(),9:set()}
                for edge,keep in zip(edges,retained,strict=True):
                    drop, = set(edge)-{keep}
                    stage = clock_to_stage[drop]
                    removed[stage].add(clock_to_role[drop])
                    added[stage].add(clock_to_role[keep])
                assert all(not (removed[s]&added[s]) and len(removed[s])==len(added[s]) for s in (8,9))
                defects = {s:signed_difference(removed[s],added[s]) for s in (8,9)}
                witnesses = {s:[min(x),min(x),str(x[min(x)])] for s,x in defects.items() if x}
                assert witnesses
                schedules.append(dict(pairs=edges,kept=retained,decision="derivative excluded",
                                      witnesses=witnesses,removed={s:sorted(r) for s,r in removed.items()},
                                      added={s:sorted(r) for s,r in added.items()}))
    assert len(schedules) == CAP
    assert sum(len(s["pairs"]) == 1 for s in schedules) == 8
    assert not signed_difference({2},{2})
    assert signed_difference({2,4},{1,4}) == {2:-1,1:1}
    return dict(head=price["head"],caller=price["caller"],events=len(events),pins=PINS,caps=[4,CAP,SECONDS],
                contact_windows=broad,projectors={t:[[r,r,"1"]] for t,r in clock_to_role.items()},
                schedules=schedules,unresolved=0)


def stop(*_):
    raise TimeoutError("20-second hard cap")


def main():
    assert __debug__
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--root",type=Path,default=HERE)
    args = parser.parse_args()
    signal(SIGALRM,stop)
    alarm(SECONDS)
    try:
        print(json.dumps(audit(args.root),indent=2,sort_keys=True))
    finally:
        alarm(0)


if __name__ == "__main__":
    main()
