"""Reverse contact reconciliation and exhaustive GF(2) rank geometry for R88."""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction
from functools import cache
from gzip import decompress
from hashlib import sha256
from itertools import pairwise
from json import dumps, loads
from pathlib import Path
from signal import SIGALRM, alarm, signal
from time import monotonic

HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
OLD_HEAD = "ed090b57ed88f8859e5ff4643645099e6ba856ea"
PINS = {
    "price": "005efb8329d38638800d82e5273580b1bb529ac490d9923ba1a92e112d31c8b1",
    "word": "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
    "legacy": "2c523ce6fdd6092d758fedc3602a0bcedb692b9766f1e41f903351ba4dee1756",
}
CURRENT_PAYLOAD = "9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"


def unique(pairs):
    result = dict(pairs)
    if len(result) != len(pairs):
        raise ValueError("Duplicate JSON key")
    return result


def checked(path, key):
    raw = path.read_bytes()
    if sha256(raw).hexdigest() != PINS[key]:
        raise ValueError(f"Changed input {key}")
    if key != "price":
        raw = decompress(raw)
    if key == "word":
        assert sha256(raw).hexdigest() == CURRENT_PAYLOAD
    return loads(raw, object_pairs_hook=unique)


def span(basis):
    result = {0}
    for v in basis:
        assert isinstance(v,int) and 0 < v < 512 and v not in result
        result.update(v^x for x in tuple(result))
    return result


def basis_for(space):
    result = []
    obtained = {0}
    for v in sorted(space):
        if v not in obtained:
            result.append(v)
            obtained.update(v^x for x in tuple(obtained))
    assert obtained == space
    return result


def dimension(space):
    size = len(space)
    assert size > 0 and size & (size-1) == 0
    return size.bit_length()-1


def reach_interval(lo1, lo2, hi1, hi2, old_mid, target):
    low = {a^b for a in lo1 for b in lo2}
    high = hi1 & hi2
    assert low <= old_mid <= high
    dim_lo,dim_hi = dimension(low),dimension(high)
    return low,high,{
        "required_rank":target, "low_union_rank":dim_lo, "high_intersection_rank":dim_hi,
        "low_union_basis":basis_for(low), "high_intersection_basis":basis_for(high),
        "low_vector_count":len(low), "high_vector_count":len(high),
        "status":"geometry_survivor" if dim_lo<=target<=dim_hi else
            ("high_intersection_too_small" if target>dim_hi else "low_union_too_large"),
    }


def incidence(event):
    tag = event[0]
    if tag in ("ADD","COPY"):
        assert event[1] != event[2]
        return event[1:3]
    assert tag in ("MOVE","SCALE","INIT","CLEAR")
    return event[1:2]


def contact_index(tape, roles, deadline):
    result = {r:[] for r in roles}
    for clock in range(len(tape)-1,-1,-1):
        if clock%256 == 0 and monotonic()>=deadline:
            raise TimeoutError("backwards literal contact index")
        for role in incidence(tape[clock]):
            if role in result:
                result[role].append(clock)
    return result


def route_contacts(tape, backwards, role, path):
    found = {}
    a,b,c = path
    for after,clock,before in zip(backwards,backwards[1:],backwards[2:]):
        assert before < clock < after
        if tape[before] != ["MOVE",role,a,b,False] or tape[after] != ["MOVE",role,b,c,False]:
            continue
        event = tape[clock]
        if event[0] == "ADD" and event[-1] == b:
            found[clock]=(before,after)
    return found


def signed_add(event):
    op,dst,src,k,chart = event
    assert op=="ADD" and dst!=src
    coef = Fraction(k)
    assert coef
    return dst,src,coef,chart


def order_signature(clock, roles, legs):
    positions = [(clock,"ADD")]
    positions += [(t,f"{r}:{s}") for r,(i,j) in zip(roles,legs,strict=True) for t,s in ((i,"in"),(j,"out"))]
    assert len({x[0] for x in positions})==5
    return [k for _,k in sorted(positions)]


def check_case(case, old, new, old_ix, new_ix):
    old_tape,new_tape = old["program"],new["program"]
    old_clock,delta = case["key"]
    operands = case["operands"]
    assert delta == case["delta_midpoint_rank"] and delta
    roles = [x["role"] for x in operands]
    paths = [x["charts"] for x in operands]
    old_moves = [x["moves"] for x in operands]
    midpoint = paths[0][1]
    assert paths[1][1]==midpoint and len(roles)==len(set(roles))==2
    old_add = signed_add(old_tape[old_clock])
    assert set(old_add[:2])==set(roles) and old_add[3]==midpoint
    for role,path,quoted in zip(roles,paths,old_moves,strict=True):
        exact = route_contacts(old_tape,old_ix[role],role,path)
        assert list(exact[old_clock]) == quoted
    inherited_order = order_signature(old_clock,roles,old_moves)

    route_a,route_b = [route_contacts(new_tape,new_ix[role],role,path) for role,path in zip(roles,paths,strict=True)]
    common = sorted(route_a.keys() & route_b.keys())
    signed_matches = [t for t in common if signed_add(new_tape[t])==old_add]
    accepted = []
    for t in signed_matches:
        legs = [route_a[t],route_b[t]]
        if order_signature(t,roles,legs)==inherited_order:
            accepted.append((t,legs))
    record = {"key":case["key"], "roles":roles, "legacy_add_clock":old_clock,
              "legacy_move_clocks":old_moves,"legacy_order":inherited_order,
              "literal_add":[old_add[0],old_add[1],str(old_add[2]),old_add[3]],
              "common_chart_shape_clocks":common,"signed_matches":signed_matches,
              "current_match_count":len(accepted),"paid_delta":case["paid_delta"],
              "directed_gross_upper":case["gross_at_incumbent"][1]}
    if not accepted:
        return record | {"status":"inherited_topology_missing"}
    if len(accepted)!=1:
        return record | {"status":"ambiguous_inherited_topology",
                         "current_matching_tuples":[[t,*legs] for t,legs in accepted]}
    clock,legs=accepted[0]
    frames=new["frames"]
    get=cache(lambda j:span(frames[j]))
    low1,mid1,high1=paths[0]
    low2,mid2,high2=paths[1]
    assert get(mid1)==get(mid2)
    fixed=[(get(a),get(b),get(c)) for a,b,c in paths]
    old_ranks=[]
    paid=Counter()
    for (a,b,c), alt in zip(fixed,operands,strict=True):
        assert a<b<c
        p,q=dimension(b)-dimension(a),dimension(c)-dimension(b)
        assert [p,q]==alt["ranks"] and p+delta>0 and q-delta>0
        old_ranks.append([p,q])
        paid[p] -= 17
        paid[q] -= 17
        paid[p+delta] += 17
        paid[q-delta] += 17
    paid={str(r):v for r,v in sorted(paid.items()) if v}
    assert paid==case["paid_delta"] and not case["target_delta"]
    assert Fraction(case["complete_margin_at_probe"][0]) > 0
    rank=dimension(get(midpoint))+delta
    low,high,proof=reach_interval(get(low1),get(low2),get(high1),get(high2),get(midpoint),rank)
    if proof["status"]=="geometry_survivor":
        current_chart=next((i for i,v in enumerate(frames) if len(v)==rank and low<=get(i)<=high),None)
        if current_chart is not None:
            chosen=list(frames[current_chart])
        else:
            chosen=basis_for(low)
            seen=span(chosen)
            for v in sorted(high):
                if len(chosen)==rank:
                    break
                if v not in seen:
                    chosen.append(v)
                    seen.update(v^w for w in tuple(seen))
        assert len(chosen)==rank and low<=span(chosen)<=high
        proof["existing_chart"]=current_chart
        proof["constructive_basis"]=chosen
    return record|{"current_add_clock":clock,"current_move_clocks":legs,
        "old_midpoint_rank":dimension(get(midpoint)),"old_paid_ranks":old_ranks,
        "new_paid_ranks":[[p+delta,q-delta] for p,q in old_ranks],
        "old_chart_paths":paths,**proof}


def controls():
    low1,low2=span([1]),span([2])
    mid=span([1,2])
    hi=span([1,2,4,8])
    success=reach_interval(low1,low2,hi,span([1,2,4,16]),mid,3)[2]
    assert success["status"]=="geometry_survivor" and success["high_intersection_rank"]==3
    bad=reach_interval(low1,low2,hi,span([1,2,16,32]),mid,3)[2]
    assert bad["status"]=="high_intersection_too_small" and bad["high_intersection_rank"]==2
    assert reach_interval(low1,low2,hi,hi,mid,1)[2]["status"]=="low_union_too_large"

    tape=[["MOVE",0,1,2,False],["ADD",0,1,"-3/2",2],["MOVE",0,2,3,False]]
    ix=contact_index(tape,{0},float("inf"))
    assert route_contacts(tape,ix[0],0,[1,2,3])=={1:(0,2)}
    tape.insert(2,["ADD",2,0,"1",2])
    ix=contact_index(tape,{0},float("inf"))
    assert not route_contacts(tape,ix[0],0,[1,2,3])
    return ["strict_rank_extension","saturated_high_intersection","low_union_bound","source_read_blocks_adjacency"]


def main():
    parser=ArgumentParser(description=__doc__)
    for name in PINS:
        parser.add_argument("--"+name,type=Path)
    parser.add_argument("--controls-only",action="store_true")
    args=parser.parse_args()
    if not __debug__:
        raise RuntimeError("Run with assertions")
    if args.controls_only:
        print(dumps(controls()))
        return
    if not all(getattr(args,name) for name in PINS):
        parser.error("Require all three pinned input paths")

    def stop(*_):
        raise TimeoutError("hard 20-second runner cap")

    tests,keys,decisions=[],[],[]
    timed_out=None
    signal(SIGALRM,stop)
    alarm(20)
    deadline=monotonic()+18
    try:
        tests=controls()
        price=checked(args.price,"price")
        assert price["head"]==HEAD and price["predecessor_head"]==OLD_HEAD and price["word_sha256"]==PINS["word"]
        cases=price["alternatives"]
        keys=[r["key"] for r in cases]
        assert len(keys)==len(set(map(tuple,keys)))==9 and not price["price_unresolved"]
        old=checked(args.legacy,"legacy")
        word=checked(args.word,"word")
        assert (word["public"],word["owned_fields"],len(word["program"]))==(1501,68,76466)
        used_charts={j for row in cases for operand in row["operands"] for j in operand["charts"]}
        assert all(old["frames"][j]==word["frames"][j] for j in used_charts)
        roles={x["role"] for row in cases for x in row["operands"]}
        assert not roles&set(price["protected_roles"])
        for exact in (old,word):
            main=set(exact["live"])|{r+112 for r in exact["live"]}|set(exact["hosted"]["X2"])|set(exact["hosted"]["Y2"])
            assert len(main)==400 and not roles&main and all(0<=r<exact["public"] for r in roles)
            assert all(set(span(exact["frames"][exact["initial"][r]])) <
                       set(span(exact["frames"][exact["final"][r]])) for r in roles)
        old_ix=contact_index(old["program"],roles,deadline)
        new_ix=contact_index(word["program"],roles,deadline)
        for case in cases:
            if monotonic()>=deadline:
                raise TimeoutError("nine-key geometry")
            decisions.append(check_case(case,old,word,old_ix,new_ix))
    except TimeoutError as exc:
        timed_out=str(exc)
    finally:
        alarm(0)
    pending=keys[len(decisions):]
    unresolved=pending+[r["key"] for r in decisions if r["status"]=="ambiguous_inherited_topology"]
    print(dumps(dict(head=HEAD,predecessor_head=OLD_HEAD,input_sha256=PINS,case_cap=9,runner_cap_seconds=20,
        controls=tests,decisions=decisions,unvisited=pending,unresolved=unresolved,
        status_counts=dict(Counter(r["status"] for r in decisions)),
        survivors=[r["key"] for r in decisions if r["status"]=="geometry_survivor"],
        scope="Only nine inherited profitable shapes. No search for new current-word contacts.",timeout=timed_out),
        indent=2,sort_keys=True))
    if timed_out:
        raise SystemExit(2)


if __name__=="__main__":
    main()
