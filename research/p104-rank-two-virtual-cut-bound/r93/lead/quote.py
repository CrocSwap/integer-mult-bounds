"""Freeze the 95 exact R92 mover/cut keys and their singleton price."""
from collections import defaultdict
from fractions import Fraction
from hashlib import sha256
from json import dumps, loads
from pathlib import Path

ROOT=Path(__file__).resolve().parent
PINS={
    "inputs/R92-PRICE.json":"05d7a5ebdd2eeedd6c8f534e8e2eeac22484daf9f387f4a6b88cc9eed22a6b8f",
    "inputs/GEOMETRY.json":"e9f93f3271855012b2de705c70f186f78c31a369d28110e92c5f2ffadae209b3",
    "inputs/GUARDS.json":"c23e9c74b3479e4af6c452eeb73e000878148ec385560a0642433a1c5bac4a07",
}


def unique(pairs):
    d=dict(pairs)
    if len(d)!=len(pairs):
        raise ValueError("Duplicate JSON key")
    return d


def main():
    docs=[]
    for rel,pin in PINS.items():
        raw=(ROOT/rel).read_bytes()
        if sha256(raw).hexdigest()!=pin:
            raise ValueError(f"Changed input {rel}")
        docs.append(loads(raw,object_pairs_hook=unique))
    base,geom,guards=docs
    assert base["head"]==geom["head"]==guards["head"]=="aaeec8c0acf01e99a5f331ef363a698d9c084ace"
    assert geom["price_sha256"]==PINS["inputs/R92-PRICE.json"] and guards["geometry_sha256"]==PINS["inputs/GEOMETRY.json"]
    assert base["word_sha256"]==geom["word_sha256"]==guards["word_sha256"]
    assert geom["events_replayed"]==76466 and not geom["geometry_timeout"]
    assert not geom["eligible"] and not geom["selected"] and not geom["unvisited_support_keys"]
    assert geom["counts"]=={"cohort_rank_two_crossings":95,"no_existing_chart":254,
                            "rank_two_public_moves":844,"unoccupied_or_guarded":31}
    assert guards["counts"]=={"empty_chart":31} and len(guards["cases"])==31
    cases=defaultdict(list)
    for r in geom["raw_placements"]:
        key=(r["move_clock"],r["mover"],r["rank"])
        cases[key].append(dict(quotient_representative=r["quotient_representative"],
                               existing_empty_charts=[lab["chart"] for lab in r["labels"]]))
    assert len(cases)==len({clock for clock,_,_ in cases})==95
    assert all(len(s)==3 for s in cases.values())
    assert sum(len(s["existing_empty_charts"]) for choices in cases.values() for s in choices)==31
    movers=sorted({r for _,r,_ in cases})
    assert set(movers)<=set(base["endpoint_cohort"])
    assert len(movers)<=95
    prices=[c for c in base["quotes"] if c["key"] in ([4,1,1],[5,1,1])]
    assert len(prices)==2 and prices[0]["net_incumbent"]==prices[1]["net_incumbent"]
    assert prices[0]["net_at_moonshot"]==prices[1]["net_at_moonshot"]
    chosen=prices[0]
    assert chosen["paid_delta"]=={"1":34,"2":-17} and chosen["target_delta"]=={"4":17,"5":17,"9":-17}
    credit=Fraction(chosen["net_incumbent"][1])
    moon_credit=Fraction(chosen["net_at_moonshot"][1])
    old_moon_upper=Fraction(chosen["full_at_moonshot"][1])-Fraction(chosen["net_at_moonshot"][0])
    stock_moon=old_moon_upper+len(movers)*moon_credit
    assert stock_moon<0
    print(dumps(dict(head=base["head"],kappa=base["kappa"],caller_head=base["caller_head"],
        word_sha256=base["word_sha256"],input_sha256=PINS,endpoint_cohort=base["endpoint_cohort"],
        case_cap=95,runner_seconds_cap=20,exact_case_cap=4,exact_seconds_cap=35,
        candidate_clock_count=95,distinct_mover_roles=movers,midpoint_subspaces=285,
        existing_empty_labels=31,one_edit=chosen,whole_gross_upper_at_incumbent=str(len(movers)*credit),
        whole_complete_margin_at_moonshot_upper=str(stock_moon),
        keys=[dict(key=list(key),midpoints=options) for key,options in sorted(cases.items())],
        scope="Singleton virtual bank, one existing rank-two public MOVE of each frozen R92 crossing. No other cochart role or new geometry keys."),
        indent=2,sort_keys=True))


if __name__=="__main__":
    assert __debug__
    main()
