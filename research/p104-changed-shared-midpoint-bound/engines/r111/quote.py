"""Price one frozen three-helper chart-746 coframe component."""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
from runpy import run_path

ROOT=Path(__file__).resolve().parents[1]
PINS={
    "inputs/R108-ROUTES.json":"7787cbedb364a51ae1c3712086bbc3f70da35ba018037429ad7794d52c8edb93",
    "inputs/R100-PRICE.json":"7109125bbf60e3015c8c0ac7b10b24b7de61f358c1508d06604ebccd89ef6343",
    "inputs/R92-PRICE.json":"05d7a5ebdd2eeedd6c8f534e8e2eeac22484daf9f387f4a6b88cc9eed22a6b8f",
    "inputs/pricing.py":"f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
}


def main():
    docs={}
    for path,pin in PINS.items():
        raw=(ROOT/path).read_bytes()
        if sha256(raw).hexdigest()!=pin:
            raise ValueError(f"changed dependency {path}")
        if path.endswith(".json"):
            docs[path]=json.loads(raw)
    routes,prior,readback=docs.values()
    assert routes["head"]==prior["head"]==readback["head"] and routes["topology_counts"]=={"no four-MOVE topology":10}
    pair=[next(r for r in routes["results"] if r["clock"]==t) for t in (40834,41179)]
    x,y=pair
    assert (x["mover"],x["peer"],y["mover"],y["peer"])==(1250,452,532,452)
    assert x["peer_neighbour_clocks"]==[40832,41179] and y["peer_neighbour_clocks"]==[40834,41180]
    assert x["peer_neighbour_events"]==[["MOVE",452,263,746,False],y["add"]]
    assert y["peer_neighbour_events"]==[x["add"],["MOVE",452,746,916,False]]
    assert x["anchor_move_clocks"]==[40833,44593] and y["anchor_move_clocks"]==[41178,44611]
    fields=[[1250,744,746,207,40833,44593],[452,263,746,916,40832,41180],[532,744,746,207,41178,44611]]
    old=Counter({int(k):v for k,v in readback["old_targets"].items()})
    old.subtract({int(k):v for k,v in readback["old_paid"].items()})
    assert sum(k*v for k,v in old.items())==1424
    at,probe,target=[Q(prior[k]) for k in ("old_crossing_upper","probe","fixed_target")]
    cost=run_path(str(ROOT/"inputs/pricing.py"))["cost"]
    variants=[]
    for p in range(1,7):
        for q in range(1,4):
            for d in range(1-min(p,3),min(q,2)):
                if not d:
                    continue
                before=[3,2,p,q,3,2]
                after=[3+d,2-d,p+d,q-d,3+d,2-d]
                delta=Counter(after)
                delta.subtract(before)
                d_paid={k:17*v for k,v in delta.items() if v}
                assert sum(d_paid.values())==sum(k*v for k,v in d_paid.items())==0
                credit={k:-v for k,v in d_paid.items()}
                new=old.copy()
                new.update(credit)
                net=cost(credit,at)
                whole=cost(new,probe)
                if whole[0]>0:
                    variants.append(dict(old_peer_ranks=[p,q],offset=d,rank=6+d,paid_delta=d_paid,
                        net=list(map(str,net)),full_probe=list(map(str,whole)),
                        target_net=list(map(str,cost(credit,target))),
                        extra_rank_one_upper=str(cost(new,at)[1]-1)))
    assert variants and all(Q(v["extra_rank_one_upper"])<0 for v in variants)
    result=dict(head=routes["head"],caller=routes["caller"],pins=PINS,fields=fields,
        add_events=[[r["clock"],r["add"]] for r in pair],word_sha256=prior["word_sha256"],payload_sha256=prior["word_payload_sha256"],
        old_chart=746,old_chart_rank=6,old_paid=110519,new_paid=110519,productive=22461,surplus=1424,
        positive_relaxed_variants=variants,one_upper=str(max(Q(v["net"][1]) for v in variants)),
        complete_target_upper=str(cost(old,target)[1]+max(Q(v["target_net"][1]) for v in variants)),
        limits={"components":1,"events":76466,"actual_offsets":3,"seconds":20,"prototype_seconds":120,"prototype_cases":1})
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=="__main__":
    assert __debug__
    main()
