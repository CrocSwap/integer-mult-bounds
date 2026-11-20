# SPDX-License-Identifier: Apache-2.0
"""Build the 134/329 contact on the original-74 #7657 courier word after checking its first exterior reads."""
import argparse
from collections import Counter
from fractions import Fraction
import gzip
import hashlib
import json
from pathlib import Path
import runpy

HERE = Path(__file__).resolve().parent
BASE = "450c7e544efb5258c4b8b4858b49cbd7482d14f206cdda1a71833fc73343ac66"
CHECKER = "b657117ba89a85b0cf2459236e0f117cff1c4c46b208449b2484c415e3136a3d"
SLICE = "607d34d1692261270f721a2de81a866eb679444504c1c96eb87a788f561a615a"
SIGNED = "26133145bd84e35e48cd83a99e13990532381065fd2e5ad5ba4bdbf3ea5bf9bc"
FINAL = "3e084eb8dd8e8080c9fac85833de042061dedda44f96ab199717b72ab491e688"
CALLER = "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc"
CONTACT = [41078, 41079, 41080, 41171, 42116]
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
    check(tape[45737] == ["MOVE",226,719,127,False], "missing #7657 courier")
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
    check(outside[134]["first_scalar"] == 43553 and outside[329]["first_scalar"] == 41172, "wrong first exterior reads")
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
    ap.add_argument("--base7657", type=Path, required=True)
    ap.add_argument("--evidence7657", type=Path, required=True)
    ap.add_argument("--out", type=Path, default=HERE)
    args = ap.parse_args()
    source = args.source7644
    pinned(args.slice, SLICE)
    checker = source/"independent.py"
    pinned(checker, CHECKER)
    caller = json.loads(pinned(source/"data/caller.json",CALLER))
    check(caller["stages"] == 17, "wrong caller multiplicity")
    signed = json.loads(pinned(args.evidence7657/"SIGNED-RESULT.json", SIGNED))
    final = json.loads(pinned(args.evidence7657/"FINAL.json", FINAL))
    check(final["candidate_canonical_sha256"] == BASE and final["paid_calls"] == 110281 and final["productive_calls"] == 22461, "wrong #7657 final")
    check(signed["price"]["new_native"] == BASE and signed["caller_sha256"] == CALLER,"wrong #7657 signed bill")
    base_bytes = gzip.decompress(args.base7657.read_bytes())
    check(sha(base_bytes) == BASE, "wrong #7657 input word")
    w = json.loads(base_bytes)
    local = check_contact(w,runpy.run_path(str(args.slice)))
    old,new = (Counter(v) for v in local["ranks"])
    delta = {r:17*(new[r]-old[r]) for r in sorted(old.keys()|new.keys()) if new[r]!=old[r]}
    check(delta == {1:-34,2:34,3:-17,4:-17,5:17}, "full signed delta")
    before = signed["price"]["after"]
    paid = Counter({int(k):v for k,v in before["P"].items()})
    targets = {int(k):v for k,v in before["T"].items()}
    paid.update(delta)
    check(before["S"] == 1424 and before["empty_root_credits"] == 0 and sum(paid.values()) == 110264 and sum(targets.values()) == 22461, "signed total")
    hist = {r:targets.get(r,0)-paid[r] for r in targets.keys()|paid.keys()}
    engine = runpy.run_path(str(checker))
    lo,hi = engine["crossing"](hist)
    peer_upper = Fraction(final["raw_crossing"][1])
    base_hist = {r:targets.get(r,0)-int(before["P"].get(str(r),0)) for r in targets.keys()|paid.keys()}
    base_lo, base_hi = engine["crossing"](base_hist)
    check(Fraction(final["raw_crossing"][0]) <= base_lo < base_hi <= peer_upper, "peer crossing receipt")
    check(lo > peer_upper,"composed invoice fails current original-74 target")
    edits = dict(zip(CONTACT,NEW))
    candidate = dict(w,program=[edits.get(i,e) for i,e in enumerate(w["program"]) if edits.get(i,e) is not None])
    check(len(candidate["program"]) == len(w["program"])-1,"candidate event count")
    raw = canonical(candidate)
    receipt = dict(status="PASS_LOCAL_CONTACT_AND_PROJECTED_COMPLETE_INVOICE",base=BASE,candidate=sha(raw),
                   base_events=len(w["program"]),candidate_events=len(candidate["program"]),
                   old={i:e for i,e in zip(CONTACT,OLD)},new=edits,local=local,
                   signed_caller_sha256=CALLER,signed_7657_sha256=SIGNED,final_7657_sha256=FINAL,paid_delta=delta,productive_delta={},
                   paid=dict(paid),targets=targets,surplus=before["S"],empty_root_credits=before["empty_root_credits"],
                   ordinary_routing_delta=-17000,projected_ordinary_upper=final["ordinary_bound"]-17000,
                   peer_lower=str(base_lo),peer_upper=str(base_hi),projected_gain_over_peer_upper=str(lo-peer_upper),
                   projected_directed_crossing=[str(lo),str(hi)],peer7657_test_upper=str(peer_upper),
                   remaining=["full paired strict observations and 74 ordered erased values","physical forward and adjoint all columns and absolute phase","complete direct signed caller, ordinary, precision, tape and outer checks","independent verification"])
    args.out.mkdir(parents=True,exist_ok=True)
    for name,data in [("candidate.json.gz",raw),("base7657.json.gz",base_bytes)]:
        (args.out/name).write_bytes(gzip.compress(data,compresslevel=9,mtime=0))
    (args.out/"GATE.json").write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    print(receipt["status"],receipt["candidate"],[str(lo),str(hi)],flush=True)


if __name__ == "__main__":
    main()
