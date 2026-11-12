"""Directed price for fusing two paid Type A QUERYs into one rank-two job."""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations
from json import dumps, loads
from pathlib import Path
from runpy import run_path

ROOT=Path(__file__).resolve().parent
HEAD='aaeec8c0acf01e99a5f331ef363a698d9c084ace'
CALLER='07a76c5e2738882c0cb322278e56f6cae3c9885d'
PINS={
    'inputs/QUERY-CENSUS.json':'ae9ae5116091dc73d10a5dad34a38eab7581ae26654ef30af8be0ffb1acbea5c',
    'inputs/7334-READBACK.json':'337668788fb39ec9575887f9c5faf438a880471f78d936357dabf7deeac5de82',
    'inputs/7334-ADMITTED.json':'c95300e9bca27e44a25c82d794f88cbf70757c142806b0e4c590ea29feb81a13',
    'inputs/pricing.py':'f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182',
    'inputs/7113-CALLER.json':'255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc',
}


def unique(pairs):
    result=dict(pairs)
    if len(result)!=len(pairs):
        raise ValueError('Duplicate JSON key')
    return result


def hist(data):
    result=Counter({int(r):n for r,n in data.items()})
    assert len(result)==len(data) and all(r>0 and type(n) is int and n>0 for r,n in result.items())
    return result


def interval(values):
    return list(map(str,values))


def main():
    assert __debug__
    raw={}
    for rel,pin in PINS.items():
        value=(ROOT/rel).read_bytes()
        if sha256(value).hexdigest()!=pin:
            raise ValueError(f'Changed dependency {rel}')
        raw[rel]=value
    read=lambda key:loads(raw[key],object_pairs_hook=unique)
    census=read('inputs/QUERY-CENSUS.json')
    base=read('inputs/7334-READBACK.json')
    admission=read('inputs/7334-ADMITTED.json')
    assert base['head']==admission['head']==HEAD and admission['exit']==0
    assert admission['status']=='independently_reproduced_comparable' and len(admission['stages'])==4
    assert base['caller_head']==admission['caller']==CALLER
    assert census['caller_sha256']==admission['caller_sha256']==PINS['inputs/7113-CALLER.json']
    assert set(base['assumptions'])==set(admission['assumptions'])=={
        'native_all_columns','owned_erasure','compiler','precision_tape','analytic_recovery'}
    queries=census['query_events']
    clocks=sorted(map(int,queries))
    assert clocks==[1516,1580,1659,1721]
    assert all(q=={'destination':0,'q_power':-1,'relative_defect_rank':1,'source':1} for q in queries.values())
    ports=len(set(census['ports']))
    assert ports==len(census['ports'])==96 and len(clocks)==4
    paid,targets=(hist(base[k]) for k in ('paid','targets'))
    assert (sum(paid.values()),sum(targets.values()),paid[1])==(110519,22461,68384)
    old=targets.copy(); old.subtract(paid)
    assert sum(r*n for r,n in old.items())==base['rank_surplus']==1424 and not base['empty_root_credits']
    crossing=Q(base['new_raw_interval'][1]); bit=Q(base['bit_premise']); claim=Q(base['claim'])
    assert claim==Q(admission['kappa'])<crossing<bit<Q(base['bit_admitted'])
    cost=run_path(str(ROOT/'inputs/pricing.py'))['cost']
    target=Q('0.0040075385047236')
    probe=crossing+Q(1,10**9)
    assert crossing<probe<bit<target
    old_cross,old_probe,old_bit,old_target=(cost(old,k) for k in (crossing,probe,bit,target))
    assert all(value[1]<0 for value in (old_cross,old_probe,old_bit,old_target))

    pairs=list(combinations(clocks,2))
    matchings=[(left,right) for left,right in combinations(pairs,2) if not set(left).intersection(right)]
    assert len(pairs)==6 and len(matchings)==3
    assert all(set(left+right)==set(clocks) for left,right in matchings)
    stock={}
    for fusions in (1,2):
        delta=Counter({1:-2*ports*fusions,2:ports*fusions})
        new=paid.copy()
        new.update(delta)
        assert min(new.values())>0
        assert sum(delta.values())==-ports*fusions and sum(r*n for r,n in delta.items())==0
        assert sum(new.values())==110519-ports*fusions
        signed=targets.copy()
        signed.subtract(new)
        assert sum(r*n for r,n in signed.items())==1424
        credit=Counter({rank:-change for rank,change in delta.items()})
        assert sum(r*n for r,n in credit.items())==0
        raw_credit=cost(credit,crossing)
        new_cross,new_probe,new_bit,new_target=(cost(signed,k) for k in (crossing,probe,bit,target))
        with_extra=signed.copy()
        with_extra[1]-=1
        extra=cost(with_extra,crossing)
        assert extra==tuple(x-1 for x in new_cross)
        assert 0<raw_credit[0]<=raw_credit[1]<1
        assert 0<new_cross[0] and 0<new_probe[0]
        assert extra[1]<0 and new_bit[1]<0 and new_target[1]<0
        stock[str(fusions)]={
            'paid_delta':dict(delta),'target_delta':{},'paid':dict(new),
            'paid_positions':sum(new.values()),'productive_fields':sum(targets.values()),
            'rank_surplus':1424,'empty_root_credits':0,
            'gross_credit_at_comparator':interval(raw_credit),
            'complete_margin_at_old_crossing':interval(new_cross),
            'complete_margin_at_price_only_probe':interval(new_probe),
            'complete_margin_at_retained_bit_premise':interval(new_bit),
            'complete_margin_at_fixed_moonshot':interval(new_target),
            'complete_margin_with_one_extra_rank_one_at_old_crossing':interval(extra),
        }
    assert all(Q(x)==2*Q(y) for x,y in zip(stock['2']['gross_credit_at_comparator'],
                                           stock['1']['gross_credit_at_comparator'],strict=True))
    doc={
        'head':HEAD,'claim':str(claim),'caller_head':CALLER,'caller_sha256':admission['caller_sha256'],
        'input_sha256':PINS,'old_crossing_upper':str(crossing),'retained_bit_premise':str(bit),
        'old_paid':dict(paid),'targets':dict(targets),'old_rank_surplus':1424,'type_a_ports':ports,
        'old_complete_margin_at_crossing':interval(old_cross),'old_complete_margin_at_bit':interval(old_bit),
        'price_only_probe':str(probe),'old_complete_margin_at_price_only_probe':interval(old_probe),
        'fixed_moonshot':str(target),'old_complete_margin_at_fixed_moonshot':interval(old_target),
        'queries':queries,'eligible_pairs_before_support':[list(pair) for pair in pairs],
        'host_clock_policy':'before the earlier phase-even ADD at its original QUERY clock',
        'all_two_disjoint_matchings':[[list(left),list(right)] for left,right in matchings],
        'first_build_fusion_cap':1,'support_pair_cap':6,'support_runner_seconds':20,
        'formal_case_cap':1,'formal_runner_seconds':90,'max_disjoint_fusions':2,
        'one_edit_optimistic_upper':stock['1']['gross_credit_at_comparator'][1],
        'two_disjoint_optimistic_upper':stock['2']['gross_credit_at_comparator'][1],
        'by_number_of_fused_pairs':stock,
        'necessary_support':[
            'At q=+1 and body one the compensator is identity.',
            'At q=-1 and body one the phase defect has rank at most two and square zero for two independent commuting transvection axes.',
            'The physical provider still needs exact all-phase Laurent action, unchanged field volume, arbitrary-input forward and adjoint, legal ownership/restoration and all caller, precision and tape costs.',
        ],
        'scope':'Price only. All J providers fixed. Grants one same-volume rank-two compensation before the first phase-even ADD and all ancillary costs free. Caller bytes hashed and not decoded. No literal support or candidate.',
    }
    print(dumps(doc,indent=2,sort_keys=True))


if __name__=='__main__':
    main()
