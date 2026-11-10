"""Independently recount the dispatch-weighted profile and certify its price."""
from collections import Counter
from fractions import Fraction as Q
from common import P,ROOT,read,dump,load,sha

def price(providers,out):
    d=ROOT/'research/complex-k492-owner-repair/vendor/multicold/engines'
    M=load(d/'moment.py','mixed_mercator');B=load(d/'base_two_moment.py','mixed_atanh')
    A=load(d/'outer.py','mixed_outer')
    O=load(ROOT/'research/complex-t21-owners/vendor/pr870/independent/price_profile_t16.py','mixed_outer_driver')
    mix=read(P/'data/MIX.json');claim=read(P/'CLAIM.json');profile=Counter()
    counts=Counter(pid for pid,s,r in mix)
    assert counts==claim['provider_calls']=={'demote3':125,'demote4':208}
    for pid,count in counts.items():
        word=read(providers[pid]/'CANONICAL-WORD.json.gz')
        profile.update({int(r):count*n for r,n in word['local_profile'].items()})
    profile.update({int(r):n for r,n in claim['idle'].items()})
    assert {str(r):n for r,n in profile.items()}==claim['complex_profile']
    assert 73*33152-sum(r*n for r,n in profile.items())==11840
    root=M.certify(profile,73,33152);lo,hi=Q(root['lower']),Q(root['upper'])
    assert lo==Q(claim['complex_lower'])
    signs={}
    for name,z in [('lower',lo),('upper',hi)]:
        first=M.moment(profile,73,33152,z);second=B.moment(73,33152,list(profile.items()),z)
        assert(first[1]<1 and second[1]<1)if name=='lower'else(first[0]>1 and second[0]>1)
        signs[name]={'point':str(z),'mercator':[str(v-1)for v in first],'atanh':[str(v-1)for v in second]}
    outer=[O.outer47(Q(claim['bit_lower']),z,A)for z in (lo,hi)]
    assert outer[0]['kappa']==outer[1]['kappa']==claim['kappa']
    result=dict(status='PASS_TWO_ENGINE_MIXED_PROFILE_AND_OUTER47',kappa=claim['kappa'],kappa_decimal=claim['kappa_decimal'],
      root=root,signs=signs,outer=outer,profile=dict(sorted(profile.items())),provider_call_counts=dict(counts),
      scope='Arithmetic for the nominated mixed profile; geometry and full invoice require separate admission. No optimality claim.')
    dump(out,result);return result
