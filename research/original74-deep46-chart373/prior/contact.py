# SPDX-License-Identifier: Apache-2.0
"""Build one contact on the original-74 #7645 word after checking its first exterior reads."""
import argparse
from collections import Counter
from fractions import Fraction
import gzip
import hashlib
import json
from pathlib import Path
import runpy

HERE = Path(__file__).resolve().parent
BASE = "6c52b2fba7c20343a50cb92ed4b997aa9921c78f212ac6428d13fff2bcd014cf"
WORD44 = "86bc8a1d1276c5b8d80a19704f90279e85b24b9490a02b9afa67c1a5b119c114"
PEER_PATCH = "64f096802f328cac7e51c655c2c5a1aa6c011dd33ea278c53a05caaa598594df"
CHECKER = "b657117ba89a85b0cf2459236e0f117cff1c4c46b208449b2484c415e3136a3d"
SLICE = "607d34d1692261270f721a2de81a866eb679444504c1c96eb87a788f561a615a"
SIGNED = "da2adf53f209c6c0cdc91757f814812fb309600596cdc999ea306e8e876652e1"
CALLER = "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc"
CONTACT = [41078, 41079, 41080, 41171, 42115]
OLD = [["MOVE",134,3,618,False],["MOVE",329,373,618,False],["ADD",134,329,"-1/2",618],
       ["MOVE",329,618,733,False],["MOVE",134,618,913,False]]
NEW = [["MOVE",134,3,373,False],None,["ADD",134,329,"-1/2",373],
       ["MOVE",329,373,733,False],["MOVE",134,373,913,False]]
GRID = 1125 << 25


def check(cond, message):
    if not cond:
        raise ValueError(message)


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",",":")).encode()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def pinned(path, digest):
    data = path.read_bytes()
    check(sha(data) == digest, f"wrong pinned input {path}")
    return data


def prepare_base(source):
    # Clear1nsight #7645 applies DreamingOfClouds #7611's deeper role-46 route
    # to ToikY #7644. The full reconstructed word must equal the public digest.
    raw = gzip.decompress((source/"data/word.json.gz").read_bytes())
    check(sha(raw) == WORD44, "wrong original-74 #7644 word")
    original = json.loads(raw)
    patch = json.loads(pinned(source/"data/peer7611.json", PEER_PATCH))
    insert = dict(patch["insert_before"])
    entrance = [e for e in insert[0] if e[1] not in (185,196)]
    add = {43543:insert[43525],45392:insert[45372],47973:insert[47953]}
    remove = {43543,43544,45387,45388,45390,47973}
    tape = entrance[:]
    for clock,event in enumerate(original["program"]):
        tape.extend(add.get(clock,()))
        if clock not in remove:
            tape.append(event)
    w = dict(original,program=tape)
    check(sha(canonical(w)) == BASE, "wrong published #7645 word")
    return w


def span(frame):
    points = {0}
    for v in frame:
        check(0 < v < 512 and v not in points, "invalid chart basis")
        points |= {x ^ v for x in points}
    return points


def roles(e):
    return e[1:3] if e[0] in ("ADD","COPY") else e[1:2]


def check_contact(w, slice_module):
    tape = w["program"]
    check([tape[i] for i in CONTACT] == OLD, "wrong contact")
    check(tape[47995] == ["MOVE",46,513,127,False], "missing deeper role-46 leg")
    first, _, add, donor_return, recipient_return = CONTACT
    watch = set(CONTACT)
    outside = {}
    for role,end,expected in [(134,recipient_return,[first,add,recipient_return]),
                              (329,donor_return,[first+1,add,donor_return])]:
        touches = [i for i,e in enumerate(tape) if role in roles(e)]
        check([i for i in touches if first <= i <= end] == expected, f"intervening touch on {role}")
        previous = max(i for i in touches if i < first)
        next_event = min(i for i in touches if i > end)
        next_scalar = next(i for i in touches if i > end and tape[i][0] in ("SCALE","ADD","COPY"))
        outside[role] = {"previous":previous,"exit":end,"first_event":next_event,"first_scalar":next_scalar}
        watch.update([next_event,next_scalar])
    spans = {c:span(w["frames"][c]) for c in (3,373,618,733,913)}
    metrics = []
    for events in (OLD,NEW):
        ranks = []
        for e in events:
            if e and e[0] == "MOVE":
                a,b = e[2:4]
                check(e[-1] is False and e[1] < w["public"] and spans[a] < spans[b], "illegal public MOVE")
                ranks.append(len(w["frames"][b])-len(w["frames"][a]))
        metrics.append(ranks)
    check(metrics == [[3,1,1,4],[2,2,5]], "unexpected route ranks")
    # Evaluate only dependencies of the pre-read operands, all public input columns symbolic.
    readings,_ = slice_module["slice_rows"](list(enumerate(tape)),watch,w["public"],w["public"]+w["owned_fields"])
    def row(clock,role):
        return readings[clock][2][roles(tape[clock]).index(role)][1]
    x,y = row(first,134),row(first+1,329)
    check(row(add,134) == x and row(add,329) == y and x and y,"operands unavailable at first ADD")
    receiver = x.copy()
    slice_module["update"](receiver,y,"-1/2",add)
    details = {}
    for r, wanted in ((134,receiver),(329,y)):
        z = outside[r]
        for label in ("exit","first_event","first_scalar"):
            check(row(z[label],r) == wanted,f"value differs before {r} {label}")
        details[r] = dict(z, first_event_opcode=tape[z["first_event"]],first_scalar_opcode=tape[z["first_scalar"]],
                          entry_nonzero_columns=len(x if r == 134 else y),entry_form_sha256=sha(canonical(sorted((x if r==134 else y).items()))),
                          returned_nonzero_columns=len(wanted),returned_form_sha256=sha(canonical(sorted(wanted.items()))))
    # The MOVE-only changed legs carry both arbitrary forms to their identical
    # exterior charts. x+y/2 is a real equal-price faulty replacement.
    check(receiver != x and any(y.values()), "half-ADD sign control has no distinguishing input")
    return {"external_reads":details,"grid":GRID,"ranks":metrics,
            "equal_invoice_wrong_sign_first_column":min(y),"wrong_sign_difference_in_grid_units":y[min(y)]}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source7644", type=Path, required=True)
    ap.add_argument("--slice", type=Path, required=True)
    ap.add_argument("--signed7645", type=Path, required=True)
    ap.add_argument("--out", type=Path, default=HERE)
    args = ap.parse_args()
    source = args.source7644
    pinned(args.slice, SLICE)
    checker = source/"independent.py"
    pinned(checker, CHECKER)
    caller = json.loads(pinned(source/"data/caller.json",CALLER))
    check(caller["stages"] == 17, "wrong caller multiplicity")
    signed = json.loads(pinned(args.signed7645, SIGNED))
    check(signed["price"]["new_native"] == BASE and signed["caller_sha256"] == CALLER,"wrong #7645 signed bill")
    w = prepare_base(source)
    local = check_contact(w,runpy.run_path(str(args.slice)))
    old,new = (Counter(v) for v in local["ranks"])
    delta = {r:17*(new[r]-old[r]) for r in sorted(old.keys()|new.keys()) if new[r]!=old[r]}
    check(delta == {1:-34,2:34,3:-17,4:-17,5:17}, "full signed delta")
    before = signed["price"]["after"]
    paid = Counter({int(k):v for k,v in before["P"].items()})
    targets = {int(k):v for k,v in before["T"].items()}
    paid.update(delta)
    check(before["S"] == 1424 and before["empty_root_credits"] == 0 and sum(paid.values()) == 110281 and sum(targets.values()) == 22461, "signed total")
    hist = {r:targets.get(r,0)-paid[r] for r in targets.keys()|paid.keys()}
    engine = runpy.run_path(str(checker))
    lo,hi = engine["crossing"](hist)
    peer_upper = Fraction("0.003652423812")  # conservative upper from #7657's published directed interval
    check(lo > peer_upper,"composed invoice fails current original-74 target")
    edits = dict(zip(CONTACT,NEW))
    candidate = dict(w,program=[edits.get(i,e) for i,e in enumerate(w["program"]) if edits.get(i,e) is not None])
    check(len(candidate["program"]) == len(w["program"])-1,"candidate event count")
    raw = canonical(candidate)
    receipt = dict(status="PASS_LOCAL_CONTACT_AND_PROJECTED_COMPLETE_INVOICE",base=BASE,candidate=sha(raw),
                   base_events=len(w["program"]),candidate_events=len(candidate["program"]),
                   old={i:e for i,e in zip(CONTACT,OLD)},new=edits,local=local,
                   signed_caller_sha256=CALLER,signed_7645_sha256=SIGNED,paid_delta=delta,productive_delta={},
                   paid=dict(paid),targets=targets,surplus=before["S"],empty_root_credits=before["empty_root_credits"],
                   ordinary_routing_delta=-17000,projected_ordinary_upper=782628968,
                   projected_directed_crossing=[str(lo),str(hi)],peer7657_test_upper=str(peer_upper),
                   remaining=["full paired strict observations and 74 ordered erased values","physical forward and adjoint all columns and absolute phase","complete direct signed caller, ordinary, precision, tape and outer checks","independent verification"])
    args.out.mkdir(parents=True,exist_ok=True)
    for name,data in [("candidate.json.gz",raw),("base7645.json.gz",canonical(w))]:
        (args.out/name).write_bytes(gzip.compress(data,compresslevel=9,mtime=0))
    (args.out/"GATE.json").write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    print(receipt["status"],receipt["candidate"],[str(lo),str(hi)],flush=True)


if __name__ == "__main__":
    main()
