"""Rational native caller parameter selection; Apache-2.0.
Dugongue with substantial OpenAI Codex assistance.
Checks exponent arithmetic, not the retained operator identities.
"""
from fractions import Fraction as F
import json

C=F(3,32)

def choose(provider, target):
    provider, target=F(provider), F(target)
    if not 0 < target < min(provider,C):
        raise ValueError('need 0 < target < min(provider,3/32)')
    q=(target+min(provider,C))/2
    stop=(provider-q)/(2*provider)
    delta=min(F(1,100),(q-target)/(4*(q+1)),(C-q)/16)
    epsilon=1-delta
    beta=1-3*delta
    spare=delta/10
    layout=delta/100
    xi=epsilon*(1+q)-C+layout
    savings={
        'main':epsilon*q,
        'standalone_routing':F(1),
        'fused_gaussian':1-epsilon+q*beta,
        'standalone_addressing':F(1),
        'group_scans':1-epsilon+beta,
        'boundary':C+xi-epsilon,
        'sparse_visits':F(1,2)+xi-epsilon,
        'record_products':epsilon,
        'core_face_recovery':1-(epsilon+beta+48-128+2),
    }
    guards={
        'stopped_provider':provider*(1-stop)-q,
        'stop_positive':stop,
        'stop_below_one':1-stop,
        'epsilon_below_one':1-epsilon,
        'beta_positive':beta,
        'beta_below_epsilon':epsilon-beta,
        'cap_above_band':xi-F(1,2),
        'cap_below_dimension':epsilon-xi,
        'global_gamma':1-epsilon-spare,
        'group_chirp':1-(beta+2*xi-2+spare),
        'group_key':1-(beta+1-epsilon),
        'membership':1-(beta+2*(1-epsilon)),
        'spare_positive':spare,
        'strassen_integer_certificate':F(2**45-7**16),
    }
    guards.update({k+'_excess':v-target for k,v in savings.items()})
    failed=[k for k,v in guards.items() if v<=0]
    if failed:
        raise ValueError('strict guard failure: '+','.join(failed))
    return {'provider':str(provider),'target':str(target),'q':str(q),
            'stop':str(stop),'delta':str(delta),'epsilon':str(epsilon),
            'beta':str(beta),'spare':str(spare),'layout':str(layout),'xi':str(xi),
            'savings':{k:str(v) for k,v in savings.items()},
            'guards':{k:str(v) for k,v in guards.items()},
            'minimum_excess':str(min(v-target for v in savings.values()))}

def check():
    # Illustrations are arithmetic only: supplying q_C is a separate obligation.
    cases=[('0.0030201656','0.0030201655'),
           ('0.00302157','0.003021569'),
           ('0.0156','0.0155'),
           (F(3,32),F(3,32)-F(1,10**9)),
           (F(1,4),F(9,100)),
           (F(1,10**50),F(1,2*10**50))]
    results=[choose(a,b) for a,b in cases]
    for a in range(1,31):
        provider=F(a,320)
        for j in range(1,20):
            choose(provider,min(provider,C)*F(j,20))
    bad=[(0,F(1,100)),(F(1,100),0),
         (F(1,100),F(1,100)),(F(1,4),C),
         (F(1,4),C+F(1,10**9))]
    for a,b in bad:
        try:choose(a,b)
        except ValueError:pass
        else:raise AssertionError('bad parameter accepted')
    return {'status':'PASS','illustrative_cases':results,
            'additional_rational_cases':570,'rejecting_controls':len(bad),
            'scope':'Exact universal parameter formulas instantiated on rational cases; operator identity and provider realization remain separate proof inputs.'}

if __name__=='__main__':
    print(json.dumps(check(),indent=2))
