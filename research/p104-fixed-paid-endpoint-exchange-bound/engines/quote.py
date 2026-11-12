"""Predecode directed quote for one fixed-paid endpoint swap with role 1481."""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from json import dumps,loads
from pathlib import Path
from runpy import run_path

ROOT=Path(__file__).resolve().parent
PINS={
    'inputs/R92-PRICE.json':'05d7a5ebdd2eeedd6c8f534e8e2eeac22484daf9f387f4a6b88cc9eed22a6b8f',
    'inputs/R115-PRICE.json':'c04adfb199f6dbc25806d6062562c7d707b8fda8ad73f3ed818901248d25ffbf',
    'inputs/pricing.py':'f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182',
}

def unique(items):
    obj=dict(items)
    if len(obj)!=len(items):
        raise ValueError('duplicate key')
    return obj

def main():
    assert __debug__
    raw={}
    for path,digest in PINS.items():
        data=(ROOT/path).read_bytes()
        assert sha256(data).hexdigest()==digest,('changed input',path)
        raw[path]=data
    base,roles=(loads(raw[f'inputs/R{x}-PRICE.json'],object_pairs_hook=unique) for x in (92,115))
    assert base['head']==roles['head']=='aaeec8c0acf01e99a5f331ef363a698d9c084ace'
    assert base['caller_head']==roles['caller']=='07a76c5e2738882c0cb322278e56f6cae3c9885d'
    assert base['word_sha256']==roles['word_sha256']
    old=[g for g in roles['groups'] if g['roles']==[1481]]
    assert old==[{'endpoints':[745,245],'roles':[1481]}]
    cohort=base['endpoint_cohort']
    assert len(set(cohort))==615 and 1481 not in cohort
    p,t=(Counter({int(r):n for r,n in base[k].items()}) for k in ('old_paid','old_targets'))
    old_profile=t.copy()
    old_profile.subtract(p)
    delta={5:-17,6:17,8:17,9:-17}
    changed=old_profile.copy()
    changed.update(delta)
    assert (sum(p.values()),sum(t.values()),sum(r*n for r,n in old_profile.items()))==(110519,22461,1424)
    assert sum(delta.values())==sum(r*n for r,n in delta.items())==0
    cost=run_path(str(ROOT/'inputs/pricing.py'))['cost']
    quotes={}
    for label in ('old_crossing_upper','probe','moonshot'):
        k=Q(base[label])
        old_v,gain,new=(cost(x,k) for x in (old_profile,delta,changed))
        quotes[label]={'kappa':str(k),'old_margin':list(map(str,old_v)),'whole_one_gross':list(map(str,gain)),
                       'complete_one_margin':list(map(str,new)),
                       'complete_one_margin_with_extra_rank_one':list(map(str,(new[0]-1,new[1]-1)))}
    assert Q(quotes['probe']['complete_one_margin'][0])>0
    assert Q(quotes['old_crossing_upper']['complete_one_margin_with_extra_rank_one'][1])<0
    assert Q(quotes['moonshot']['complete_one_margin'][1])<0
    print(dumps({'head':base['head'],'caller':base['caller_head'],'pins':PINS,'word_sha256':base['word_sha256'],
                 'quote':quotes,'old_paid':p,'old_targets':t,'productive_delta':delta,'paid_delta':{},
                 'one_fixed_helper':1481,'old_endpoints':[[745,245],[3,127]],'new_endpoints':[[745,127],[3,245]],
                 'old_rank_pair':[5,9],'new_rank_pair':[6,8],'other_role_cohort':cohort,
                 'potential_unordered_pairs':615,'whole_compatible_pair_cap':1,'native_copies':17,
                 'expected_chart_dimensions':{'3':0,'745':3,'245':8,'127':9}},indent=2,sort_keys=True))

if __name__=='__main__':
    main()
