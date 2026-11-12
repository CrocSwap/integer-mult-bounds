"""Directed fixed-price stock for reusing one Type A QUERY result."""
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
    old_cross,old_bit=(cost(old,k) for k in (crossing,bit))
    assert old_cross[1]<0 and old_bit[1]<0
    stock={}
    for uses in (1,2,3):
        removed=ports*uses
        new=paid.copy(); new[1]-=removed
        signed=targets.copy(); signed.subtract(new)
        rank_mass=sum(r*n for r,n in signed.items())
        assert rank_mass==1424+removed and sum(new.values())==110519-removed
        new_cross,new_bit=(cost(signed,k) for k in (crossing,bit))
        assert new_cross==tuple(x+removed for x in old_cross)
        assert new_bit==tuple(x+removed for x in old_bit)
        assert new_cross[0]>0 and new_bit[0]>0
        stock[str(uses)]={'paid_delta':{'1':-removed},'target_delta':{},'paid':dict(new),
                         'paid_positions':sum(new.values()),'productive_fields':22461,
                         'rank_surplus':rank_mass,'empty_root_credits':0,
                         'exact_credit':str(removed),'complete_margin_at_old_crossing':interval(new_cross),
                         'complete_margin_at_retained_bit_premise':interval(new_bit)}
    doc={'head':HEAD,'claim':str(claim),'caller_head':CALLER,'caller_sha256':admission['caller_sha256'],
         'input_sha256':PINS,'old_crossing_upper':str(crossing),'retained_bit_premise':str(bit),
         'old_paid':dict(paid),'targets':dict(targets),'old_rank_surplus':1424,'type_a_ports':ports,
         'old_complete_margin_at_crossing':interval(old_cross),'old_complete_margin_at_bit':interval(old_bit),
         'queries':queries,'eligible_pairs_before_support':[list(pair) for pair in combinations(clocks,2)],
         'first_build_use_cap':1,'support_pair_cap':6,'whole_stock_reuse_cap':3,
         'whole_optimistic_stock_upper':'288','by_number_of_reused_queries':stock,
         'scope':'Directed fixed-price stock only, granting source equality, legal owned cache and all added ordinary costs free. Caller bytes hashed and not decoded.'}
    print(dumps(doc,indent=2,sort_keys=True))


if __name__=='__main__':
    main()
