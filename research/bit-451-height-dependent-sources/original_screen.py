#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""The single frozen 18th-power source/height partition. CPython 3.12."""
from argparse import ArgumentParser
from datetime import datetime, timezone
from decimal import Decimal, localcontext
from fractions import Fraction as F
from hashlib import sha256
from math import comb, lcm
from pathlib import Path
import json
import signal
import time

PINS = {
    'round321/benchmark/producer/BIT-451.json':'538b785f93517b41229186e9070281d240f5d506f80a7e1ed705dd91c68f8749',
    'round336/independent/receipt.json':'69c8f917d6b2676897639eef67e8f15aae1c23a6bfb608dcd38aed236f299818',
    'round339/independent/receipt.json':'41a80ef6b08339dd146791d5a22a7472de8a8ab651b35f25a0282a4ee751295e',
    'round341/independent/receipt-with-minimum.json':'42aede07a16e538f97e43341a605e7a432fc0e600504cb1a381e1476abaa30fd',
}
P, V, h, B, shift = 18, 451, 1804, F(5,2), 32


class Rejected(Exception):
    """Exact failure of a frozen sufficient condition."""


def utc():
    return datetime.now(timezone.utc).isoformat(timespec='milliseconds')


def require(condition, message):
    if not condition:
        raise Rejected(message)


def down(x):
    return F((x*10**25).__floor__(),10**25)


def up(x):
    return F((x*10**25).__ceil__(),10**25)


def power_lower(a,b,e):
    with localcontext() as ctx:
        ctx.prec=80
        lower=F(Decimal(a).ln().next_minus())-F(Decimal(b).ln().next_plus())
        z=e*lower
        v=(Decimal(z.numerator)/Decimal(z.denominator)).next_minus()
        return down(F(v.exp().next_minus()))


def price(bit, old):
    H=bit['uniform']['H']
    delta=F(bit['separation']['trial'])
    J=((H+h)**P//h**P).bit_length()
    base_ok=(1+F((134**V).bit_length()-1,h))**P>F(bit['uniform']['ambient_power'][1])
    carrier=(h**P << (J-1)) <= (h+H)**P < (h**P << J)
    tail=F(J,H)*(H+h)>2*P
    full=delta-F(J,H)-F(1,H*2**44)
    rho=F(bit['cover_and_stock']['rho'])
    value=F(bit['cover_and_stock']['seed'])
    stages=[]
    for _ in range(7):
        bound=full-rho*(full-value)
        new=F((bound*10**24).__floor__()-1,10**24)
        require(value<new<bound<full<rho<1-bound,'interior stage')
        stages.append([str(new),str(bound-new)])
        value=new
    cap=F((value*10**17).__floor__(),10**17)
    tick=F(1,10**14)
    claim=(cap//tick-8)*tick
    tested=claim+7*tick
    old_ceiling=F(bit['raw_crossing'][1])-F(old['uniform_loss'])-7*tick
    old_claim=F(old['candidate_grid_claim'])
    return dict(p=P,h=h,J=J,base=base_ok,carrier=carrier,tail=tail,covered=str(full),stages=stages,
                cap=str(cap),tested=str(tested),claim=str(claim),old_ceiling=str(old_ceiling),
                change=str(claim-old_claim),separation=str(claim-old_ceiling),
                passed=base_ok and carrier and tail and cap>tested>claim>old_ceiling>old_claim)


def heights(mu):
    common=lcm(*(m.denominator for m in mu))
    coeff=[[comb(i,j)*6**j*int(mu[j]*common) for j in range(i+1)] for i in range(P+1)]
    v=[7**j for j in range(P+1)]
    for g in range(shift+P+1):
        v=[sum(a*v[i-j] for j,a in enumerate(row)) for i,row in enumerate(coeff)]
        yield F(v[-1],6**P*common**(g+1))


def differences(seq):
    result=[]
    while seq:
        result.append(seq[0]);seq=[b-a for a,b in zip(seq,seq[1:])]
    return result


def newton(numer,offset,extra):
    ns=differences(numer[offset:offset+P+1])
    ds=differences([(F(319,100)+F(23,20)*(g+extra))**P for g in range(offset,offset+P+1)])
    require(all(n>=0 and d>0 for n,d in zip(ns,ds)),'nonnegative Newton certificate')
    return [a/b for a,b in zip(ns,ds)]


def discover(data, root, mark):
    files=[]
    for name,sha in PINS.items():
        raw=(root/name).read_bytes()
        if sha256(raw).hexdigest()!=sha:
            raise ValueError(name)
        files.append(json.loads(raw))
    bit,grid,paid,old=files
    require(old['p']==19 and old['uniform_J']==747 and F(old['candidate_grid_claim'])==F('0.00387992804544'),
            'frozen complete comparator')
    check=price(bit,old);data['price']=check
    eta=F(bit['uniform']['eta'][0]);delta=F(bit['separation']['trial'])
    mu=list(map(F,paid['moments'][:P+1]))
    require(len(mu)==19 and mu[0]==1 and mu[1]==F(749,1000),'R339 paid enclosure')
    limit=(mu[1]/F(23,20))**P
    data['terminal']={'ratio':str(limit),'capacity':str(B*eta)}
    require(check['passed'] and limit<B*eta,'full price or terminal asymptote')
    mark('complete price and terminal limit')
    eps=F(paid['epsilon_upper'])
    d=min(F(grid['mean_lower'])-F(3,5),F(9,10)-F(grid['mean_upper']))
    require(d>0 and 11**3>=4**5 and 11**9<=9**10,'unchanged rank band')
    fraction=(1-F(grid['tensor_variance_upper'])/d**2)/(1+eps)
    small=power_lower(16,9,V*delta)
    band=1+fraction*(power_lower(4,1,V*delta)-1)
    data['nonroot']={'band_distance':str(d),'completed_fraction_lower':str(fraction),
                     'partial_group_lower':str(small),'admitted_band_group_lower':str(down(band))}
    require(fraction>0 and min(small,band)>B,'nonroot multiplier')
    mark('both nonroot branches')
    sep=bit['separation'];raw=sep['three_engine_intervals']['source_1']
    alpha,lam=F(raw['alpha'][0]),F(raw['lambda'][1])
    w=F(sep['target_tilt'])
    require(w==F(17,50) and 0<lam<alpha and alpha**V>F(1,2),'Chernoff endpoints')
    decay=up((lam/alpha)**V)
    pref=2**(1+(4*V*w).__ceil__()) # alpha^(-451)<2, k0^w <= 2^ceil(4*451*w).
    require(0<decay<1,'uniform geometric tail')
    b=min(F(old['source_lower']['root']),B)
    root_low=down(b*power_lower(16,1,V*delta/8))
    require(root_low>B,'small x root bound')
    # The unrounded majorant decays. Each recursively rounded value separately
    # bounds it, and a rounded u_32 may be reused for all G>=32.
    us=[F(pref)]
    for _ in range(shift):
        us.append(up(us[-1]*decay))
    caps=[eta*max(b,B-(B-b)*u) for u in us]
    data['root']={'prior_b':str(b),'small_x_lower':str(root_low),'decay_upper':str(decay),
                  'prefactor_upper':str(pref),'tail_root_fraction_upper':str(us[-1]),
                  'tail_capacity_lower':str(caps[-1])}
    mark('source bands and bounded root mass')
    cs=list(heights(mu))
    low=newton(cs,0,0)
    data['small_x']={'newton_ratios':list(map(str,low)),'capacity':str(B*eta)}
    require(low[-1]==limit and max(low)<B*eta,'small x Newton inequality')
    mark('all 19 small-x coefficients')
    rows=[]
    data['large_x_prefix']=rows
    for g in range(shift):
        ratio=cs[g]/(F(319,100)+F(23,20)*(g+F(7,8)))**P
        rows.append({'G':g,'root_fraction_upper':str(us[g]),'ratio':str(ratio),'capacity':str(caps[g])})
        require(ratio<caps[g],f'large x at explicit height {g}')
    mark('all 32 large-x heights')
    high=newton(cs,shift,F(7,8))
    data['large_x_tail']={'newton_ratios':list(map(str,high)),'capacity':str(caps[-1])}
    require(high[-1]==limit and max(high)<caps[-1],'large x shifted Newton inequality')
    mark('all 19 large-x tail coefficients')


def main():
    cli=ArgumentParser(description=__doc__)
    cli.add_argument('--campaign-root',type=Path,required=True);cli.add_argument('--out',type=Path,required=True)
    args=cli.parse_args()
    begin=time.monotonic()
    report={'case':{'p':P,'h':h,'B':str(B),'x_split':'7/8','height_cut':shift},
            'pins':PINS,'events':[],'discovery_budget_seconds':45,'total_budget_seconds':60}
    def mark(name):
        report['events'].append({'utc':utc(),'stage':name,'elapsed':time.monotonic()-begin})
    def timeout(signum,frame):
        raise TimeoutError()
    signal.signal(signal.SIGALRM,timeout);signal.alarm(45)
    mark('single discovery start')
    try:
        discover(report,args.campaign_root,mark)
        report['decision']='ADVANCE_ONE_SIGNED_REPLAY'
    except Rejected as e:
        report['decision']='RETIRE_FROZEN_CERTIFICATE';report['failed_gate']=str(e)
    except TimeoutError:
        report['decision']='CAPPED_UNRESOLVED'
    except (OSError,ValueError) as e:
        report['decision']='INPUT_OR_ARITHMETIC_ERROR';report['error']=str(e)
    finally:
        signal.alarm(0)
    mark('discovery closed')
    args.out.write_text(json.dumps(report,indent=2)+'\n')
    print(report['decision'],report.get('failed_gate',''),report['events'][-1]['elapsed'])


if __name__=='__main__':
    main()
