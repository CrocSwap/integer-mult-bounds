"""Recount #7161 and reprice its helper-only partition relaxation."""
from collections import Counter
from fractions import Fraction as Q
from functools import cache
import gzip
from hashlib import sha256
import json
from pathlib import Path
import sys

PINS = {
    "native/WORD.json.gz": "c1caec11ca3ee264ef03018dd91037eac10c3e28950c4c525ee1b4bf5ee210e2",
    "native/RESULT.json": "59080d75e7281b1a8c1353930917fd15869ad747ff4200948898f78f11c14089",
    "caller/CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
}
TARGET = Q("0.0040075385047236")
GRID = 10**25


def authenticated(root, name):
    blob = (root / name).read_bytes()
    if sha256(blob).hexdigest() != PINS[name]:
        raise ValueError(f"SHA-256 mismatch: {name}")
    return json.loads(gzip.decompress(blob) if name.endswith(".gz") else blob)


def span(basis):
    out = {0}
    for b in basis:
        if b in out:
            raise ValueError("dependent frame")
        out |= {x ^ b for x in out}
    return out


def invoice(w, c, result):
    ranks = list(map(len, w["frames"]))
    spaces = list(map(span, w["frames"]))
    main_roles = [*w["live"], *(112+j for j in w["live"]), *w["hosted"]["X2"], *w["hosted"]["Y2"]]
    assert len(set(main_roles)) == len(main_roles) == 400
    assert w["public"] == len(w["initial"]) == len(w["final"]) == 1499
    assert len(w["live"]) == len(w["ports"]) == 104
    assert sorted(p for d in c["types"].values() for p in d["ports"]) == list(range(104))
    assert sorted(w["hosted"]["Dports"]) == sorted(c["types"]["A"]["ports"])

    origins = {}
    visits = {}
    for role,(a,b) in enumerate(zip(w["initial"], w["final"], strict=True)):
        if role not in main_roles:
            assert spaces[a] < spaces[b]
            origins[role] = (a,b,ranks[b]-ranks[a])
            visits[role] = {a}

    paid_native = Counter()
    for op,role,*rest in w["program"]:
        if op == "MOVE":
            a,b,owned = rest
            assert owned == (role >= w["public"])
            assert spaces[a] < spaces[b] or (owned and spaces[b] < spaces[a])
            paid_native[abs(ranks[b]-ranks[a])] += 1
            if role in visits:
                visits[role].add(b)

    native_stages = [e[1] for e in c["events"] if e[0]=="J"]
    assert native_stages == list(range(1,c["stages"]+1))
    copies = len(native_stages)
    helper_hist = Counter(r for a,b,r in origins.values())
    targets = Counter({r:copies*n for r,n in helper_hist.items()})
    paid = Counter({r:copies*n for r,n in paid_native.items()})
    fixed_main = Counter()
    for spec in c["types"].values():
        ports = len(spec["ports"])
        assert len(spec["diagonal"]) == spec["roles"]
        for sign,head,*body in spec["diagonal"]:
            assert sign == -1 and head == 0 and len(body) == copies and set(body)<={0,1}
            fixed_main[1+8*sum(body)] += ports
    targets.update(fixed_main)
    for event in c["events"]:
        if event[0]=="J":
            continue
        kind,op,_,*args=event
        ports=len(c["types"][kind]["ports"])
        if op=="QUERY":
            paid[1] += ports
        elif op in ("IDLE_ONE","IDLE_ODD"):
            paid[8*len(args[0])+(op=="IDLE_ODD")] += ports

    frozen = result["price"]["after"]
    observed = result["checks"]["ODD-PHYSICAL-BINDING.json"]["occurrence_and_geometry"]
    for key,hist in (("P",paid),("T",targets)):
        assert {str(r):n for r,n in hist.items()} == frozen[key]
        assert frozen[key] == observed["paid" if key=="P" else "targets"]
    assert result["caller_sha256"] == PINS["caller/CALLER.json"]
    assert observed["fresh_helpers"] == copies*len(origins)
    assert sum(r*(targets[r]-paid[r]) for r in targets.keys()|paid.keys()) == frozen["S"] == 1424
    return targets, paid, fixed_main, paid_native, copies, origins, visits, ranks, spaces


def round_q(x, upper):
    y=x*GRID
    n,d=y.numerator,y.denominator
    return Q(-((-n)//d) if upper else n//d,GRID)


def round_iv(lo,hi):
    return round_q(lo,False), round_q(hi,True)


@cache
def log_reduced(x):
    z=(x-1)/(x+1)
    lo=2*sum(z**(2*j+1)/(2*j+1) for j in range(31))
    return round_iv(lo,lo+2*z**63/(63*(1-z*z)))


@cache
def log_rank(r):
    e=r.bit_length()-1
    lo,hi=log_reduced(Q(r,1<<e))
    l2,h2=log_reduced(Q(2))
    return lo+e*l2,hi+e*h2


def exp_minus(x):
    assert 0<=x<1
    t=s=Q(1)
    for i in range(1,19):
        t=-t*x/i
        s+=t
    return s-t,s


@cache
def power(r,k):
    lo,hi=log_rank(r)
    return round_iv(r*exp_minus(k*hi)[0],r*exp_minus(k*lo)[1])


def dot(hist, evaluate):
    lo=hi=Q(0)
    for r,n in hist.items():
        a,b=evaluate(r)
        if n<0:
            a,b=b,a
        lo+=n*a
        hi+=n*b
    return lo,hi


def moment(signed,k=TARGET):
    return dot(signed,lambda r:power(r,k))


def crossing(signed):
    left,right=Q(0),Q(1,50)
    # Piecewise derivative enclosures cover the entire first-root domain.
    edges=[Q(i,500) for i in range(11)]
    derivative_upper=[]
    for lo,hi in zip(edges,edges[1:]):
        def derivative(r):
            ll,lh=log_rank(r)
            return -lh*power(r,lo)[1],-ll*power(r,hi)[0]
        derivative_upper.append(dot(signed,derivative)[1])
    assert max(derivative_upper)<0
    assert moment(signed,left)[0]>0>moment(signed,right)[1]
    while right-left>Q(1,10**13):
        k=(left+right)/2
        lo,hi=moment(signed,k)
        if lo>0:
            left=k
        elif hi<0:
            right=k
        else:
            raise ValueError("undecided bisection")
    scale=10**13
    l,r=(left*scale,right*scale)
    a,b=Q(l.numerator//l.denominator,scale),Q(-((-r.numerator)//r.denominator),scale)
    assert moment(signed,a)[0]>0>moment(signed,b)[1]
    return {"first_crossing_bracket": list(map(str,(a,b))),
            "largest_derivative_upper_on_0_to_0.02": str(round_q(max(derivative_upper),True))}


def partition(rank,pieces):
    n=min(rank,pieces)
    q,r=divmod(rank,n)
    return [q+1]*r+[q]*(n-r)


def exchange(rank, parts, copies=1):
    delta=Counter({rank:-copies})
    delta.update({r:copies*n for r,n in Counter(parts).items()})
    return delta


def with_splits(signed, profile, copies):
    out=signed.copy()
    for (rank,parts),count in profile.items():
        out.update(exchange(rank,parts,copies*count))
    return out


def integer_room(interval):
    lo,hi=interval
    assert lo>0 and lo.numerator//lo.denominator==hi.numerator//hi.denominator
    return lo.numerator//lo.denominator


def solve(root):
    w,result,c=(authenticated(root,p) for p in PINS)
    T,P,main,native,stages,origins,visits,ranks,spaces=invoice(w,c,result)
    H=Counter(r for a,b,r in origins.values())
    assert set(H)==set(range(1,10))
    signed=T.copy()
    signed.subtract(P)
    base=moment(signed)
    gains={r:moment(exchange(r,partition(r,2),stages)) for r in range(2,10)}
    assert all(gains[r][1]<gains[r+1][0] for r in range(2,9))
    balanced_profile=lambda m: Counter({(r,tuple(partition(r,m))):n for r,n in H.items() if r>1})
    maximums={}
    for pieces in (1,2,9):
        case=with_splits(signed,balanced_profile(pieces),stages)
        maximums[pieces]={**crossing(case),"target_margin":list(map(str,moment(case)))}
    minimum=next(n for n in range(1,H[9]+1) if base[0]+n*gains[9][0]>0)
    prev=moment(with_splits(signed,{(9,(4,5)):minimum-1},stages))
    first=moment(with_splits(signed,{(9,(4,5)):minimum},stages))
    assert prev[1]<0<first[0]
    funded_thresholds={}
    for extras in range(7):
        for count in range(minimum,H[9]+1):
            case=with_splits(signed,{(9,(4,5)):count},stages)
            case[1]-=extras*stages
            value=moment(case)
            if value[0]>0:
                case[4]-=stages
                case[5]-=stages
                case[9]+=stages
                assert moment(case)[1]<0
                funded_thresholds[extras]=count
                break
    assert len(funded_thresholds)==7

    def split_room(profile):
        full=moment(with_splits(signed,profile,stages))
        return {"target_margin":list(map(str,full)),
                "whole_caller_extra_rank_one_limit":integer_room(full),
                "per_native_extra_rank_one_limit":integer_room(tuple(x/stages for x in full))}

    groups=Counter((a,b) for a,b,r in origins.values() if r==9)
    assert groups=={(3,127):616}
    by_id={}
    direct=Counter()
    balanced_nines=[]
    for i,(a,b,r) in origins.items():
        cuts=sorted({ranks[f]-ranks[a] for f in visits[i] if spaces[a]<spaces[f]<spaces[b]})
        by_id[i]={"entrance":a,"exit":b,"rank":r,"literal_legal_interior_cut_ranks":cuts}
        if cuts:
            lo=max(min(u,r-u) for u in cuts)
            direct[r,(lo,r-lo)]+=1
        if r==9 and any(u in (4,5) for u in cuts):
            balanced_nines.append(i)
    cap9=moment(with_splits(signed,{(9,(4,5)):len(balanced_nines)},stages))
    assert cap9[1]<0 and len(balanced_nines)<minimum
    cap_all=moment(with_splits(signed,direct,stages))
    return {
        "input_sha256":PINS,"target_kappa":str(TARGET),"native_copies":stages,
        "helper_origins":by_id,"native_paid":native,"helper_histogram":H,
        "fixed_main_targets":main,"complete_T":T,"complete_P":P,
        "piece_cap_ladder":maximums,
        "binary_exchange_at_target":{r:list(map(str,v)) for r,v in gains.items()},
        "minimum_zero_paid_binary_splits":minimum,"one_less_margin":list(map(str,prev)),
        "first_positive_margin":list(map(str,first)),
        "binary_rank9_only_headroom":split_room({(9,(4,5)):H[9]}),
        "binary_all_helper_headroom":split_room(balanced_profile(2)),
        "minimum_rank9_splits_for_extra_rank_one_native_jobs":funded_thresholds,
        "literal_owner_rank9_balanced_eligible":balanced_nines,
        "literal_owner_rank9_balanced_only_optimistic_margin":list(map(str,cap9)),
        "literal_owner_best_binary_profile":{
            f"{r}->{a}+{b}":n for (r,(a,b)),n in direct.items()},
        "literal_owner_all_ranks_optimistic_margin":list(map(str,cap_all)),
        "scope":"Frozen main and original paid profiles except explicitly added rank-one jobs. Balanced arithmetic is an optimistic relaxation. Literal-owner ceiling requires the same original owner to visit a strict intermediate frame, with no virtual rebase or paid itinerary changes.",
    }


if __name__=="__main__":
    assert __debug__, "run without -O"
    print(json.dumps(solve(Path(sys.argv[1])),sort_keys=True,indent=2))
