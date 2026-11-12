"""Price one exact Type-A rank-seventeen 8+9 output split."""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from json import dumps,loads
from pathlib import Path
from runpy import run_path
R=Path(__file__).resolve().parent/'inputs'
PINS={'R92-PRICE.json':'05d7a5ebdd2eeedd6c8f534e8e2eeac22484daf9f387f4a6b88cc9eed22a6b8f','pricing.py':'f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182','CALLER.json':'255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc'}
raw={p:(R/p).read_bytes() for p in PINS}
assert all(sha256(v).hexdigest()==PINS[p] for p,v in raw.items())
b,c=(loads(raw[p]) for p in ('R92-PRICE.json','CALLER.json'))
assert b['head']=='aaeec8c0acf01e99a5f331ef363a698d9c084ace' and b['caller_head']=='07a76c5e2738882c0cb322278e56f6cae3c9885d'
a=c['types']['A'];assert len(a['ports'])==96 and len(c['events'])==4783
roots=[i for i,x in enumerate(a['diagonal']) if x[:2]==[-1,0] and sum(x[2:])==2]
assert roots==[7,10,25,28] and c['events'][1742]==['A','IDLE_ONE',10,[9]] and c['events'][3377][:3]==['J',10,[10,0,18,28]]
p,t=(Counter({int(k):v for k,v in b[x].items()}) for x in ('old_paid','old_targets'))
s=t.copy();s.subtract(p);d={8:96,9:96,17:-96};cost=run_path(str(R/'pricing.py'))['cost']
def quote(k):
    g=cost(d,k);o=cost(s,k)
    return dict(gross=list(map(str,g)),one_complete=list(map(str,(o[0]+g[0],o[1]+g[1]))),
                four_compatible_gross_upper=str(4*g[1]),four_complete_upper=str(o[1]+4*g[1]),
                four_with_extra_rank1_per_port_upper=str(o[1]+4*g[1]-96))
print(dumps(dict(head=b['head'],caller=b['caller_head'],pins=PINS,roles=roots,chosen=10,cuts=[1743,1744],paid=110519,productive=22557,rank_surplus=1424,
delta=d,quotes={k:quote(Q(b[k])) for k in ('old_crossing_upper','probe','moonshot')},
ordinary_reservation={'scalar_macros':32*96+2*96,'ordinary_map_slots':2*96,'source_units':32*96*340+2*96*(1000+64)}),indent=2,sort_keys=True))
