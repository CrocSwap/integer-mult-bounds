"""Full predecode price for one charged paid subdivision and productive 4+5."""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path

ROOT=Path(__file__).resolve().parent
HEAD="aaeec8c0acf01e99a5f331ef363a698d9c084ace"
WORD="4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a"
PINS={
    "inputs/ADMITTED.json":"c95300e9bca27e44a25c82d794f88cbf70757c142806b0e4c590ea29feb81a13",
    "inputs/RANK-STOCK.json":"4a7841699dd17688f6aada5c902a2a91e94558b2b1b4460c46b0e55aa95b3f9f",
    "inputs/READBACK.json":"337668788fb39ec9575887f9c5faf438a880471f78d936357dabf7deeac5de82",
    "inputs/R86-PRICE.json":"b4bf8e00a8289f03b1da731fb3ab563a771d88d875e0da73acf70954df2f2c56",
    "inputs/pricing.py":"f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
}


def unique(pairs):
    values=dict(pairs)
    if len(values)!=len(pairs):
        raise ValueError("Duplicate JSON key")
    return values


def hist(values):
    return Counter({int(r):n for r,n in values.items()})


def interval(values):
    return list(map(str,values))


def main():
    documents={}
    for rel,pin in PINS.items():
        raw=(ROOT/rel).read_bytes()
        if sha256(raw).hexdigest()!=pin:
            raise ValueError(f"Changed input {rel}")
        if rel.endswith(".json"):
            documents[Path(rel).name]=loads(raw,object_pairs_hook=unique)
    admitted,stock,base,prior=(documents[k] for k in ("ADMITTED.json","RANK-STOCK.json","READBACK.json","R86-PRICE.json"))
    assert all(v["head"]==HEAD for v in (admitted,stock,base,prior))
    assert admitted["status"]=="independently_reproduced_comparable" and admitted["exit"]==0 and len(admitted["stages"])==4
    assert admitted["inputs"]["WORD.json.gz"]==prior["word_sha256"]==WORD
    assert admitted["caller"]==base["caller_head"]==prior["caller_head"]
    assert set(admitted["assumptions"])==set(base["assumptions"])
    paid,targets,public=hist(base["paid"]),hist(base["targets"]),hist(stock["public_paid_histogram"])
    assert paid==hist(stock["old_complete_paid"])==hist(prior["old_paid"])
    assert targets==hist(stock["complete_targets"])==hist(prior["old_targets"])
    assert sum(paid.values())==110519 and sum(targets.values())==22461 and base["copies"]==17
    assert not base["empty_root_credits"] and max(public)==8 and all(public[r]>0 for r in range(1,9))
    cohort=prior["endpoint_cohort"]
    assert len(cohort)==len(set(cohort))==615
    old=targets.copy()
    old.subtract(paid)
    assert sum(r*v for r,v in old.items())==1424
    at=Q(prior["old_crossing_upper"])
    probe=at+Q(1,10**9)
    bit=Q(prior["retained_bit_premise"])
    target=Q(prior["moonshot"])
    assert at==Q(admitted["crossing"][1])==Q(stock["crossing_upper"]) and at<probe<bit<target
    cost=run_path(str(ROOT/"inputs/pricing.py"))["cost"]
    delta_t={4:17,5:17,9:-17}
    new_targets=targets.copy()
    new_targets.update(delta_t)
    assert sum(new_targets.values())==22478
    choices=[]
    for cut_rank in (4,5):
        for left in range(1,cut_rank+1):
            for right in range(1,10-cut_rank):
                direct=left+right
                if not public[direct]:
                    continue
                delta_p=Counter()
                delta_p[left]+=17
                delta_p[right]+=17
                delta_p[direct]-=17
                new_paid=paid.copy()
                new_paid.update(delta_p)
                assert sum(new_paid.values())==110536 and min(new_paid.values())>0
                signed=new_targets.copy()
                signed.subtract(new_paid)
                assert sum(r*n for r,n in signed.items())==1424
                change=Counter(delta_t)
                change.subtract(delta_p)
                add_child=cost(signed,at)[1]-1
                assert cost(signed,probe)[0]>0 and add_child<0
                choices.append(dict(key=[cut_rank,left,right],endpoint_chart_ranks=[cut_rank-left,cut_rank+right],
                    direct_rank=direct,native_public_rank_stock=public[direct],paid_delta=dict(delta_p),target_delta=delta_t,
                    net_incumbent=interval(cost(change,at)),full_incumbent=interval(cost(signed,at)),
                    full_probe=interval(cost(signed,probe)),net_at_bit=interval(cost(change,bit)),
                    net_at_moonshot=interval(cost(change,target)),full_at_moonshot=interval(cost(signed,target)),
                    full_margin_with_one_extra_raw_rank_one_upper=str(add_child)))
    assert len(choices)==38 and len({tuple(sorted(c["key"][1:])) for c in choices})==13
    best={key:max(Q(c[key][1]) for c in choices) for key in ("net_incumbent","net_at_moonshot")}
    for key in best:
        assert {c["direct_rank"] for c in choices if Q(c[key][1])==best[key]}=={2}
    assert public[2]>=len(cohort)
    max_stock=len(cohort)
    base_moon=cost(old,target)
    stock_moon=base_moon[1]+max_stock*best["net_at_moonshot"]
    minimum=(-base_moon[1])//best["net_at_moonshot"]+1
    print(dumps(dict(head=HEAD,kappa=admitted["kappa"],caller_head=admitted["caller"],word_sha256=WORD,
        input_sha256=PINS,old_crossing_upper=str(at),probe=str(probe),retained_bit_premise=str(bit),moonshot=str(target),
        old_paid=paid,old_targets=targets,new_targets=new_targets,public_paid_stock=public,endpoint_cohort=cohort,
        full_paid_positions_before=110519,full_paid_positions_after=110536,productive_positions_before=22461,
        productive_positions_after=22478,rank_surplus=1424,empty_root_credits=0,quotes=choices,
        one_edit_best_net={k:str(v) for k,v in best.items()},
        one_edit_worst_incumbent_lower=str(min(Q(c["full_incumbent"][0]) for c in choices)),
        one_edit_extra_rank_one_at_incumbent_net_upper=str(best["net_incumbent"]-1),
        one_edit_extra_rank_one_uniform_credit_through_bit_upper=str(Q(prior["one_split_uniform_credit_through_bit_upper"])-1),
        optimistic_distinct_compatible_stock_cap=max_stock,
        whole_compatible_incumbent_net_upper=str(max_stock*best["net_incumbent"]),
        whole_compatible_moonshot_net_upper=str(max_stock*best["net_at_moonshot"]),
        moonshot_complete_margin_upper=str(stock_moon),moonshot_necessary_distinct_splits=int(minimum),
        scope="Predecode price for one existing native public ascending MOVE subdivided at absolute chart rank four/five, with one rank-nine 4+5 productive split. All actual geometry, compatibility and ancillary costs unresolved; one split per distinct cohort helper and no repeated MOVE credits."),
        indent=2,sort_keys=True))


if __name__=="__main__":
    assert __debug__
    main()
