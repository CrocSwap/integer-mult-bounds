"""Exact complete signed-invoice comparison, not a paid-count shortcut."""
from collections import Counter
from fractions import Fraction as Q

def verify(new,old):
    def hist(record,key):return Counter({int(k):v for k,v in record[key].items()})
    T,P=hist(new,'targets'),hist(new,'paid');t,p=hist(old,'targets'),hist(old,'paid')
    delta=Counter(T);delta.subtract(P);delta.subtract(t);delta.update(p)
    delta={r:n for r,n in delta.items()if n}
    expected={1:104,16:104,17:-104,41:208,40:-208,57:-208,56:208}
    if delta!=expected:raise ValueError('Complete signed invoice differs from proved concave gain')
    if sum(r*n for r,n in delta.items())!=0:raise ValueError('Rank mass changed')
    bracket=old['raw_root_interval'];upper=Q(bracket[1])
    if not upper<Q(new['kappa']):raise ValueError('No strict source crossing separation')
    return {'previous_claim':'0.00329760','new_claim':new['kappa'],
            'gain':str(Q(new['kappa'])-Q('.00329760')),
            'signed_histogram_delta':{str(k):v for k,v in sorted(delta.items())},
            'strict_gain_for_all_powers':'104*(H1+H16-H17)+208*((H41-H40)-(H57-H56)) > 0 for H(r)=r^t, 0<t<1',
            'proof':'Strict subadditivity supplies the first positive summand; decreasing concave increments supply the second.',
            'source_crossing_upper':str(upper),'rank_mass_delta':0,
            'literal_retirement_operations':1,'interpretation':'Second-retirement-equivalent signed gain; not two literal retirements.'}
