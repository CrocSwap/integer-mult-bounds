"""Two exact moment engines, strict outer assembly, and the fixed-family ceiling.

Reuses the signed prices and all-replica supporting inequality of PR795/890/942.
The changed inventory is recounted from the frozen seven-slot supplier plan.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
from common import P,ROOT,read,dump,load,sha

def price(out):
    d=load(ROOT/'research/complex-t37-owners/independent/all_t_bound.py','retained_all_t_bound')
    for path,pin in d.PINS.items():assert sha(ROOT/path)==pin,'Retained arithmetic pin'
    plan=read(P/'data/SUPPLIER-PLAN.json');claim=read(P/'CLAIM.json')
    provider=plan['provider_registry']['gauge44'];inventory=Counter(provider['widths'])
    local={int(r):n for r,n in provider['actual_paid_profile'].items()}
    assert {str(r):n for r,n in inventory.items()}==claim['width_inventory']
    assert {str(r):n for r,n in local.items()}==claim['local_profile']
    mass=sum(c*n for c,(n,_)in d.CAPACITIES.items())-9*sum(r*n for r,n in inventory.items())
    signed=sum(n*p for n,p in d.CAPACITIES.values())+9*sum(inventory[r]*p for r,p in zip(d.WIDTHS,d.PRICES))
    credit=48*signed+13*mass;assert(mass,signed,credit)==(14778,-3568,20850)
    upper,patterns=d.dual_tables();idle={int(r):n for r,n in claim['idle'].items()}
    assert sum(r*n for r,n in idle.items())==37*mass
    assert sum(upper[r]*n for r,n in idle.items())==37*signed
    assert Q(credit,925)==Q(834,37)
    profile=Counter({r:333*n for r,n in local.items()});profile.update(idle)
    assert {str(r):n for r,n in profile.items()}==claim['complex_profile']
    assert 73*33152-sum(r*n for r,n in profile.items())==11840
    M=d.load(d.ENGINE+'moment.py','t37_slots_mercator')
    B=d.load(d.ENGINE+'base_two_moment.py','t37_slots_atanh')
    A=d.load(d.ENGINE+'outer.py','t37_slots_outer')
    O=d.load('research/complex-t21-owners/vendor/pr870/independent/price_profile_t16.py','t37_slots_outer_driver')
    root=M.certify(profile,73,33152);lo,hi=Q(root['lower']),Q(root['upper'])
    assert lo==Q(claim['complex_lower'])
    signs={}
    for name,z in [('lower',lo),('upper',hi)]:
        first=M.moment(profile,73,33152,z);second=B.moment(73,33152,list(profile.items()),z)
        assert(first[1]<1 and second[1]<1)if name=='lower'else(first[0]>1 and second[0]>1)
        signs[name]={'point':str(z),'mercator':[str(v-1)for v in first],'atanh':[str(v-1)for v in second]}
    supporting={kind:d.ratio_certificate(engine,kind,upper,hi)for kind,engine in [('mercator',M),('atanh',B)]}
    bit=Q(claim['bit_lower'])
    assert bit==Q(read(ROOT/'research/complex-t21-owners/data/CLAIM.json')['bit_lower'])
    outer=[O.outer47(bit,z,A)for z in (lo,hi)]
    assert outer[0]['kappa']==outer[1]['kappa']==claim['kappa']
    result=dict(status='PASS_TWO_ENGINE_MOMENTS_OUTER47_AND_FIXED_FAMILY_ALL_T_CEILING',
      kappa=claim['kappa'],kappa_decimal=claim['kappa_decimal'],profile=claim['complex_profile'],
      root=root,signs=signs,outer=outer,patterns=patterns,signed_per_replica=signed,
      idle_mass_per_replica=mass,rank_one_credit_per_replica=credit,supporting_inequalities=supporting,
      scope='Attained outer-grid ceiling for this fixed local paid profile, whole-helper inventory, source capacity stock and retained bit supplier. It is not a ceiling for other constructions.')
    dump(out,result);return result

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    assert not a.out.exists() and not a.out.resolve().is_relative_to(ROOT);a.out.parent.mkdir(parents=True,exist_ok=True)
    r=price(a.out);print(r['status'],r['kappa_decimal'])
